import asyncio
import os
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.access import sweep_expired_subscriptions
from app.api.access_routes import router as access_router
from app.api.admin_routes import router as admin_router
from app.api.auth_routes import router as auth_router
from app.api.miniapp import router as miniapp_router
from app.api.public_routes import router as public_router
from app.api.routes import router
from app.config import load_settings
from app.db import get_supabase, query
from app.migrate import run_migrations
from app.notification_queue import drain_due_notifications
from app.poller import clear_orphaned_runs, poll_all_sources, run_pipeline_in_thread
from app.schedule_store import effective_intervals, load_interval_overrides
from app.telegram.bot import register_command_menu, run_bot
from app.users import ensure_owner


def _supabase():
    return get_supabase(load_settings())


def _interval_seconds_to_cron(seconds: int) -> str:
    if seconds >= 3600 and seconds % 3600 == 0:
        return f"0 */{seconds // 3600} * * *"
    if seconds % 60 == 0:
        return f"*/{seconds // 60} * * * *"
    return "* * * * *"


async def _run_safe(ats_type: str | None = None) -> None:
    try:
        settings = load_settings()
        # Auto-clear stale running rows (a killed/crashed process leaves a
        # 'running' row behind that would otherwise block future polls).
        # The threshold is 45m: the longest healthy batch run is ~40m.
        stale_ids = query(
            settings,
            """
            select id from poll_runs
            where status = 'running'
              and started_at < now() - interval '45 minutes'
            """,
        )
        for row in stale_ids:
            print(f"scheduler: marking stale run {row['id']} failed (no completion in 45m)")
            _supabase().table("poll_runs").update(
                {
                    "status": "failed",
                    "finished_at": datetime.now(UTC).isoformat(),
                    "error": "stale: run did not complete (marked failed)",
                }
            ).eq("id", row["id"]).execute()

        if ats_type is None:
            # Integrity sweep: skip only if a full sweep is already running.
            running = query(
                settings,
                "select id from poll_runs where status = 'running' and ats_type is null limit 1",
            )
        else:
            # Per-ATS lock: only skip if the SAME ats_type has a live run, so a
            # long/hung poll of one ATS never blocks every other ATS from polling.
            running = query(
                settings,
                "select id from poll_runs where status = 'running' and ats_type = %s limit 1",
                (ats_type,),
            )
        if running:
            print(
                f"scheduler: skipping {ats_type or 'all'} poll, run {running[0]['id']} already in progress"
            )
            return
        await run_pipeline_in_thread(poll_all_sources(ats_type=ats_type))
    except Exception as exc:
        print(f"poll run failed ({ats_type or 'all'}): {exc}")


_scheduler: AsyncIOScheduler | None = None


def _build_scheduler() -> AsyncIOScheduler:
    global _scheduler
    settings = load_settings()
    supabase = get_supabase(settings)
    intervals = effective_intervals(settings.ats_intervals, load_interval_overrides(supabase))
    _scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
    for ats, seconds in intervals.items():
        # Tier 1: jitter ±120s so 14 ATS jobs don't all fire at :00 and hit DB at same instant.
        _trigger = CronTrigger.from_crontab(_interval_seconds_to_cron(seconds))
        _trigger.jitter = 120
        _scheduler.add_job(
            _run_safe,
            _trigger,
            args=[ats],
            id=f"poll-{ats}",
            name=f"poll {ats}",
            max_instances=1,
            coalesce=True,
            misfire_grace_time=3600,
        )

    _scheduler.add_job(
        _run_safe,
        IntervalTrigger(seconds=43200),
        args=[None],
        id="poll-all-integrity",
        name="poll all (integrity sweep, 12h)",
        max_instances=1,
        coalesce=True,
        misfire_grace_time=3600,
    )
    _scheduler.add_job(
        _drain_notifications_safe,
        IntervalTrigger(seconds=max(10, settings.notify_drain_seconds)),
        id="notify-drain",
        name="drain notification queue",
        max_instances=1,
        coalesce=True,
        misfire_grace_time=60,
    )
    _scheduler.add_job(
        _sweep_subscriptions_safe,
        CronTrigger(hour=3, minute=17),
        id="subscription-sweep",
        name="expire subscriptions / relock users",
        max_instances=1,
        coalesce=True,
        misfire_grace_time=3600,
    )
    return _scheduler


async def _drain_notifications_safe() -> None:
    try:
        settings = load_settings()
        result = await asyncio.to_thread(drain_due_notifications, settings, get_supabase(settings))
        if result["sent_telegram"] or result["sent_email"] or result["failed"]:
            print(f"notify-drain: {result}")
    except Exception as exc:
        print(f"notify-drain failed: {exc}")


async def _sweep_subscriptions_safe() -> None:
    try:
        locked = await asyncio.to_thread(sweep_expired_subscriptions, load_settings())
        if locked:
            print(f"subscription sweep: expired plans, relocked {locked} account(s)")
    except Exception as exc:
        print(f"subscription sweep failed: {exc}")


def scheduler_next_run(ats_type: str) -> str | None:
    """Return the live APScheduler next-run time for an ATS poll job (UTC ISO).

    This is the ground truth the running scheduler will actually fire, unlike a
    best-effort estimate. Returns None when the scheduler is disabled or the
    job is not registered.
    """
    scheduler = _scheduler
    if scheduler is None:
        return None
    job = scheduler.get_job(f"poll-{ats_type}")
    if job is None:
        return None
    return job.next_run_time.isoformat() if job.next_run_time else None


def reschedule_ats(ats_type: str, interval_seconds: int) -> bool:
    """Reschedule a running poll job for an ATS (applied immediately, no restart)."""
    scheduler = _scheduler
    if scheduler is None:
        return False
    job = scheduler.get_job(f"poll-{ats_type}")
    if job is None:
        return False
    job.reschedule(CronTrigger.from_crontab(_interval_seconds_to_cron(interval_seconds)))
    return True


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = load_settings()
    run_migrations(settings.database_url)

    # Seed the owner account (the historical sentinel user) so every existing
    # reference keeps working; also stamps env telegram/email identities.
    try:
        await asyncio.to_thread(ensure_owner, settings)
    except Exception as exc:
        print(f"owner bootstrap failed: {exc}")

    # A reload (uvicorn --reload restarts on any code change) kills in-flight
    # polls but leaves their 'running' rows behind, which would block the
    # per-ATS scheduler lock. Clear orphaned rows before starting fresh.
    # Retry briefly while postgrest is still in crash-recovery (see logs:
    # "Could not query the database for the schema cache. Retrying." 503).
    _supa = get_supabase(settings)
    for _attempt in range(6):
        try:
            clear_orphaned_runs(_supa)
            break
        except Exception as exc:
            is_last = _attempt == 5
            print(f"scheduler: startup orphan cleanup failed (attempt {_attempt + 1}/6) - {exc}")
            if is_last:
                break
            await asyncio.sleep(2 * (_attempt + 1))

    scheduler = None
    if os.environ.get("JOBRADAR_DISABLE_SCHEDULER", "").lower() not in ("1", "true", "yes"):
        scheduler = _build_scheduler()
        scheduler.start()
        app.state.poll_scheduler = scheduler
    else:
        print("scheduler disabled via JOBRADAR_DISABLE_SCHEDULER")

    # Telegram command bot: register the command menu and long-poll for commands.
    # Runs in the same event loop as the scheduler and is gated by the same
    # env toggles so tests never hit the Telegram API.
    bot_task = None
    if settings.telegram_enabled and settings.telegram_bot_token and settings.telegram_chat_id:
        if os.environ.get("JOBRADAR_DISABLE_BOT", "").lower() not in ("1", "true", "yes"):
            try:
                # setMyCommands is a best-effort one-shot; run it in a thread so
                # a slow/unreachable Telegram API never blocks startup.
                await asyncio.to_thread(register_command_menu, settings.telegram_bot_token)
                bot_task = asyncio.create_task(run_bot(settings))
                app.state.telegram_bot_task = bot_task
                print("telegram bot: command menu registered, polling started")
            except Exception as exc:
                print(f"telegram bot startup failed: {exc}")
        else:
            print("telegram bot disabled via JOBRADAR_DISABLE_BOT")
    else:
        print("telegram bot disabled (telegram not configured)")

    yield
    if bot_task:
        bot_task.cancel()
    if scheduler:
        scheduler.shutdown(wait=False)


app = FastAPI(title="jobRadar", lifespan=lifespan)

app.include_router(router)
app.include_router(public_router)
app.include_router(auth_router)
app.include_router(access_router)
app.include_router(admin_router)
app.include_router(miniapp_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        *[
            origin.strip()
            for origin in os.environ.get("CORS_ORIGINS", "").split(",")
            if origin.strip()
        ],
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
