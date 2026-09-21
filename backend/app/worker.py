"""Standalone worker: scheduler + Telegram bot, no HTTP API.

Run alongside the API so a 9-minute Workday poll never blocks GET /health
or POST /poll/run. The advisory locks make a second scheduler harmless —
a crashed worker releases its locks on disconnect, and two workers simply
skip each other's ticks.

Usage:
  python -m app.worker          # local
  docker compose up worker      # compose (see docker-compose.yml)
"""

import asyncio
import os
import signal

from app.config import load_settings
from app.db import get_supabase
from app.main import _build_scheduler
from app.migrate import run_migrations
from app.poller import clear_orphaned_runs
from app.telegram.bot import register_command_menu, run_bot
from app.users import ensure_owner


async def main() -> None:
    settings = load_settings()
    run_migrations(settings.database_url)

    # Same orphan cleanup as the API lifespan, with the same PostgREST retry.
    supabase = get_supabase(settings)
    for attempt in range(6):
        try:
            clear_orphaned_runs(supabase)
            break
        except Exception as exc:
            is_last = attempt == 5
            print(f"worker: orphan cleanup failed (attempt {attempt + 1}/6) - {exc}")
            if is_last:
                break
            await asyncio.sleep(2 * (attempt + 1))

    try:
        await asyncio.to_thread(ensure_owner, settings)
    except Exception as exc:
        print(f"worker: owner bootstrap failed: {exc}")

    # Scheduler (IntervalTrigger per ATS, same code as the API would use).
    scheduler = None
    if os.environ.get("JOBQUEST_DISABLE_SCHEDULER", "").lower() not in ("1", "true", "yes"):
        scheduler = _build_scheduler()
        scheduler.start()
        print(f"worker: scheduler started with {len(scheduler.get_jobs())} jobs")
    else:
        print("worker: scheduler disabled via JOBQUEST_DISABLE_SCHEDULER")

    # Telegram bot (same gating as the API).
    bot_task = None
    if (
        settings.telegram_enabled
        and settings.telegram_bot_token
        and settings.telegram_chat_id
        and os.environ.get("JOBQUEST_DISABLE_BOT", "").lower() not in ("1", "true", "yes")
    ):
        try:
            await asyncio.to_thread(register_command_menu, settings.telegram_bot_token)
            bot_task = asyncio.create_task(run_bot(settings))
            print("worker: telegram bot polling started")
        except Exception as exc:
            print(f"worker: telegram bot startup failed: {exc}")
    else:
        print("worker: telegram bot disabled (not configured or JOBQUEST_DISABLE_BOT)")

    # Wait until terminated.
    stop = asyncio.Event()

    def _handle_stop(*_args):
        stop.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _handle_stop)
        except (NotImplementedError, ValueError):
            # Windows or already-registered signal.
            pass

    await stop.wait()

    if bot_task:
        bot_task.cancel()
        try:
            await bot_task
        except asyncio.CancelledError:
            pass
    if scheduler:
        scheduler.shutdown(wait=False)
        print("worker: scheduler shut down")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
