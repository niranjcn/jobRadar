import asyncio
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from supabase import Client

from app.adapters import adapter_for
from app.config import load_settings
from app.db import get_supabase, query
from app.geo import map_location
from app.matcher import load_notification_settings, sync_preferences
from app.models import NormalizedJob
from app.notification_queue import drain_due_notifications, load_audience, match_and_enqueue
from app.settings_store import load_location_mapping

SOURCE_CONCURRENCY = 8
MAX_POSTING_AGE_DAYS = 90
SOURCES_FILE = Path(__file__).resolve().parent.parent / "sources.json"


def load_source_config() -> list[dict[str, Any]]:
    with open(SOURCES_FILE, encoding="utf-8") as f:
        return json.load(f)


def sync_sources(supabase: Client) -> None:
    for entry in load_source_config():
        supabase.table("sources").upsert(
            [
                {
                    "company_name": entry["company_name"],
                    "ats_type": entry["ats_type"],
                    "board_identifier": entry["board_identifier"],
                    "active": entry.get("active", True),
                }
            ],
            on_conflict="company_name",
        ).execute()


def fetch_sources(supabase: Client) -> list[dict[str, Any]]:
    response = supabase.table("sources").select("*").eq("active", True).execute()
    return response.data


def source_status(source: dict[str, Any], interval: int, now: datetime) -> tuple[str, str | None]:
    """Return (status, reason) for a source row using the same rules as GET /sources."""
    last = source.get("last_checked_at")
    last_error = source.get("last_error")
    if last is None:
        return "never", "never checked yet"
    if isinstance(last, str):
        try:
            last = datetime.fromisoformat(last)
        except ValueError:
            return "stale", "last_checked_at unparseable"
    if now - last > timedelta(seconds=interval * 2):
        if last_error:
            return "stale", f"last check failed: {last_error}"
        return (
            "stale",
            (
                f"last successful check was {(now - last).total_seconds() // 60:.0f}m ago "
                f"(expected every {interval // 3600}h)"
            ),
        )
    if last_error:
        return "stale", f"recovered but last run reported: {last_error}"
    return "healthy", None


def unhealthy_sources(supabase: Client, intervals: dict[str, int]) -> list[dict[str, Any]]:
    """Active sources whose status is not healthy (stale/never), with reason."""
    now = datetime.now(UTC)
    result = []
    for source in fetch_sources(supabase):
        interval = intervals.get(source["ats_type"], 3600)
        status, reason = source_status(source, interval, now)
        if status == "healthy":
            continue
        result.append(
            {
                "id": source["id"],
                "company_name": source["company_name"],
                "ats_type": source["ats_type"],
                "status": status,
                "reason": reason,
            }
        )
    return result


def fetch_existing_job_ids(supabase: Client, source_id: str) -> set[str]:
    """External job IDs already stored for a source.

    Uses a single pooled SQL query instead of paginating 1000-row REST pages
    (a 20k-job source used to cost 20 sequential HTTP round-trips per poll).
    """
    rows = query(
        load_settings(),
        "select external_job_id from jobs where source_id = %s",
        (source_id,),
    )
    return {row["external_job_id"] for row in rows}


def upsert_jobs(supabase: Client, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    supabase.table("jobs").upsert(rows, on_conflict="source_id,external_job_id").execute()


def mark_checked(supabase: Client, source_id: str) -> None:
    supabase.table("sources").update(
        {"last_checked_at": datetime.now(UTC).isoformat(), "last_error": None}
    ).eq("id", source_id).execute()


def mark_error(supabase: Client, source: dict[str, Any], exc: Exception) -> None:
    message = str(exc).strip().replace("\n", " ")[:500] or exc.__class__.__name__
    supabase.table("sources").update(
        {"last_checked_at": datetime.now(UTC).isoformat(), "last_error": message}
    ).eq("id", source["id"]).execute()


def prune_old_jobs(supabase: Client, retention_days: int) -> int:
    cutoff = datetime.now(UTC) - timedelta(days=retention_days)
    response = supabase.table("jobs").delete().lt("first_seen_at", cutoff.isoformat()).execute()
    deleted = len(response.data or [])
    if deleted:
        print(f"retention: deleted {deleted} job(s) older than {retention_days} day(s)")
    return deleted


def _is_within_age(job: NormalizedJob, max_age_days: int) -> bool:
    if max_age_days <= 0 or not job.posted_at:
        return True
    try:
        posted = datetime.fromisoformat(job.posted_at)
        if posted.tzinfo is None:
            posted = posted.replace(tzinfo=UTC)
    except (ValueError, TypeError):
        return True
    cutoff = datetime.now(UTC) - timedelta(days=max_age_days)
    return posted >= cutoff


def dedupe_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Drop rows that share an external_job_id (Oracle Fusion pagination can overlap)."""
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for row in rows:
        key = row["external_job_id"]
        if key in seen:
            continue
        seen.add(key)
        result.append(row)
    return result


async def run_pipeline_in_thread(coro) -> Any:
    """Run a blocking-heavy async pipeline in a dedicated worker thread.

    The ingestion pipeline interleaves async adapter calls with synchronous
    Supabase REST / psycopg calls. Running it directly on the main event loop
    would stall the Telegram bot long-poll and every API request for the whole
    poll. Running the coroutine in a worker thread (with its own event loop)
    keeps the main loop responsive.
    """
    return await asyncio.to_thread(asyncio.run, coro)


async def poll_source(
    supabase: Client,
    source: dict[str, Any],
    adapter,
    max_posting_age_days: int = MAX_POSTING_AGE_DAYS,
) -> dict[str, Any]:
    jobs = await adapter.fetch_jobs(source["board_identifier"])
    first_check = source.get("last_checked_at") is None
    geo_settings = load_location_mapping(supabase)
    for job in jobs:
        if job.location:
            mapped = map_location(job.location, geo_settings)
            job.countries = mapped["countries"]
            job.is_remote = mapped["is_remote"]
    jobs = [j for j in jobs if _is_within_age(j, max_posting_age_days)]
    rows = dedupe_rows([job.to_row(source_id=source["id"]) for job in jobs])
    existing = fetch_existing_job_ids(supabase, source["id"])
    new_rows = [row for row in rows if row["external_job_id"] not in existing]
    for row in rows:
        if row["external_job_id"] in existing:
            row.pop("description", None)
    upsert_jobs(supabase, rows)
    mark_checked(supabase, source["id"])
    return {
        "company": source["company_name"],
        "source_id": source["id"],
        "fetched": len(jobs),
        "new": len(new_rows),
        "first_check": first_check,
        "new_ids": [row["external_job_id"] for row in new_rows],
    }


def clear_orphaned_runs(supabase: Client, stale_minutes: int = 10) -> int:
    """Mark stuck/running poll runs as failed at startup.

    uvicorn --reload restarts the process on code changes, killing in-flight
    polls but leaving their 'running' rows behind. Those orphaned rows then
    block the per-ATS scheduler lock (a reload during a batch meant every ATS
    was skipped for hours). Any 'running' row still present after startup is
    from a dead process, so clear it immediately.
    """
    stale_ids = (
        supabase.table("poll_runs")
        .select("id")
        .eq("status", "running")
        .lt("started_at", (datetime.now(UTC) - timedelta(minutes=stale_minutes)).isoformat())
        .execute()
    )
    rows = stale_ids.data or []
    for row in rows:
        supabase.table("poll_runs").update(
            {
                "status": "failed",
                "finished_at": datetime.now(UTC).isoformat(),
                "error": "orphaned: process restarted before the run completed (cleared at startup)",
            }
        ).eq("id", row["id"]).execute()
    if rows:
        print(f"scheduler: cleared {len(rows)} orphaned running poll run(s) at startup")
    return len(rows)


def create_poll_run(
    supabase: Client, *, triggered_by: str = "scheduled", ats_type: str | None = None
) -> str:
    response = (
        supabase.table("poll_runs")
        .insert(
            {
                "triggered_by": triggered_by,
                "ats_type": ats_type,
                "status": "running",
                "started_at": datetime.now(UTC).isoformat(),
            }
        )
        .execute()
    )
    return response.data[0]["id"]


def finish_poll_run(
    supabase: Client,
    run_id: str,
    *,
    status: str,
    jobs_fetched: int = 0,
    jobs_new: int = 0,
    matches_considered: int = 0,
    matches_new: int = 0,
    telegram_sent: int = 0,
    email_sent: int = 0,
    sources: list[dict[str, Any]] | None = None,
    error: str | None = None,
) -> None:
    update: dict[str, Any] = {
        "status": status,
        "finished_at": datetime.now(UTC).isoformat(),
        "jobs_fetched": jobs_fetched,
        "jobs_new": jobs_new,
        "matches_considered": matches_considered,
        "matches_new": matches_new,
        "telegram_sent": telegram_sent,
        "email_sent": email_sent,
    }
    if sources is not None:
        update["sources"] = sources
    if error is not None:
        update["error"] = error
    supabase.table("poll_runs").update(update).eq("id", run_id).execute()


async def poll_all_sources(
    ats_type: str | None = None,
    *,
    run_id: str | None = None,
    triggered_by: str = "scheduled",
    source_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Run the full ingestion pipeline and return a per-run status summary.

    Every invocation (scheduled cron or manual button) records a poll_runs row
    so the UI can show new jobs, new matches, and per-channel alert sends.
    """
    settings = load_settings()
    supabase = get_supabase(settings)

    if run_id is None:
        run_id = create_poll_run(supabase, triggered_by=triggered_by, ats_type=ats_type)

    try:
        sync_sources(supabase)
        prune_old_jobs(supabase, settings.job_retention_days)
        sources = fetch_sources(supabase)
        if source_ids is not None:
            sources = [source for source in sources if source["id"] in set(source_ids)]
        if ats_type:
            sources = [source for source in sources if source["ats_type"] == ats_type]
        if not sources:
            print(f"poller: no active {ats_type or ''} sources to poll".strip())
            finish_poll_run(supabase, run_id, status="completed")
            return {"run_id": run_id, "status": "completed", "jobs_new": 0, "matches_new": 0}

        # Preferences must exist before the audience snapshot so a fresh
        # deployment matches on its very first poll.
        sync_preferences(supabase, settings.preferences)
        notify_settings = load_notification_settings(supabase)
        notify_first_check = notify_settings.get("notify_first_check", True)
        geo_settings = load_location_mapping(supabase)
        company_by_source = {source["id"]: source["company_name"] for source in sources}
        audience = load_audience(settings)

        tally = {"considered": 0, "matched": 0, "enqueued": 0}
        source_results: list[dict[str, Any]] = []
        semaphore = asyncio.Semaphore(SOURCE_CONCURRENCY)
        total_fetched = 0
        total_new = 0

        # Hybrid immediate per-company (Option C, user request: "after you check
        # a company immediately sent me the match (else its taking alot of time)").
        # Buffer per-source matches and flush every 5 companies or 30s, so admin
        # gets low-latency alerts without 200 separate messages. Final
        # numbers-only drain + failure report still happen after all 200.
        immediate_buffer: list[dict[str, Any]] = []
        immediate_lock = asyncio.Lock()
        last_immediate_flush = datetime.now(UTC)

        async def flush_immediate(force: bool = False) -> None:
            nonlocal immediate_buffer, last_immediate_flush
            async with immediate_lock:
                if not immediate_buffer:
                    return
                now = datetime.now(UTC)
                if (
                    not force
                    and len(immediate_buffer) < 5
                    and (now - last_immediate_flush).total_seconds() < 30
                ):
                    return
                # Copy and clear under lock, then send outside lock
                to_send = list(immediate_buffer)
                immediate_buffer = []
                last_immediate_flush = now
            # Send outside lock to avoid blocking _poll
            try:
                from app.telegram.notifications import (
                    MAX_MESSAGE_LENGTH,
                    _chunk_sections,
                    _send_message,
                )

                lines = [f"🔔 New matches — {now:%H:%M UTC} ({len(to_send)} companies)"]
                for entry in to_send:
                    lines.append(
                        f"• {entry['company']} ({entry['ats_type']}): {entry['matched']} new"
                    )
                text = "\n".join(lines)
                for chunk in _chunk_sections([text], MAX_MESSAGE_LENGTH):
                    _send_message(settings.telegram_bot_token, settings.telegram_chat_id, chunk)
                print(f"immediate: sent {len(to_send)} companies with new matches")
            except Exception as exc:
                print(f"immediate: FAILED - {exc}")

        async def _poll(source: dict[str, Any]) -> None:
            nonlocal total_fetched, total_new
            async with semaphore:
                entry: dict[str, Any] = {
                    "company": source["company_name"],
                    "ats_type": source["ats_type"],
                    "status": "ok",
                }
                try:
                    adapter = adapter_for(source["ats_type"])
                    result = await poll_source(
                        supabase, source, adapter, settings.max_posting_age_days
                    )
                    entry["fetched"] = result["fetched"]
                    entry["new"] = result["new"]
                    entry["first_check"] = result["first_check"]
                    total_fetched += result["fetched"]
                    total_new += result["new"]
                    print(f"{result['company']}: fetched {result['fetched']}, new {result['new']}")
                    # Match + enqueue IMMEDIATELY for this source — a slow board
                    # elsewhere no longer delays these alerts (per-source pipeline).
                    suppress = result["first_check"] and not notify_first_check
                    new_ids = [] if suppress else list(result["new_ids"])
                    if new_ids:
                        outcome = match_and_enqueue(
                            supabase,
                            settings,
                            company_by_source=company_by_source,
                            audience=audience,
                            geo_settings=geo_settings,
                            source_id=result["source_id"],
                            external_ids=new_ids,
                        )
                        tally["considered"] += outcome["considered"]
                        tally["matched"] += outcome["matched"]
                        tally["enqueued"] += outcome["enqueued"]
                        # Hybrid immediate per-company (Option C): if this company
                        # produced new matches, buffer it for near-real-time admin
                        # alert. Flush is debounced (5 companies or 30s).
                        if (
                            outcome["matched"] > 0
                            and settings.telegram_enabled
                            and settings.telegram_bot_token
                            and settings.telegram_chat_id
                        ):
                            async with immediate_lock:
                                immediate_buffer.append(
                                    {
                                        "company": source["company_name"],
                                        "ats_type": source["ats_type"],
                                        "matched": outcome["matched"],
                                    }
                                )
                            # Try debounced flush (may send if threshold reached)
                            await flush_immediate()
                except Exception as exc:
                    entry["status"] = "error"
                    entry["error"] = str(exc)[:300]
                    print(f"{source['company_name']}: FAILED - {exc}")
                    try:
                        mark_error(supabase, source, exc)
                    except Exception as mark_err:
                        print(f"{source['company_name']}: could not record error - {mark_err}")
                source_results.append(entry)

        await asyncio.gather(*(_poll(source) for source in sources))

        # Ensure any remaining immediate per-company alerts are flushed before
        # the final batch drain and failure report (user: matching first, then
        # issue report after all 200).
        await flush_immediate(force=True)

        print(
            f"matching: considered={tally['considered']}, "
            f"matched={tally['matched']}, enqueued={tally['enqueued']}"
        )

        # Flush everything already due right now — accounts with delay 0 get
        # their alerts here. Delayed accounts are released by the scheduler's
        # drain ticker when scheduled_for passes.
        drained = drain_due_notifications(settings, supabase)
        telegram_sent = drained["sent_telegram"]
        email_sent = drained["sent_email"]

        # Failure report: after all checks, summarize which sites failed (if any).
        # Separate from job-match alerts (which only fire when pending > 0).
        try:
            failed = [s for s in source_results if s.get("status") == "error"]
            if (
                failed
                and settings.telegram_enabled
                and settings.telegram_bot_token
                and settings.telegram_chat_id
            ):
                # Reuse the same helper as the legacy poller (main branch).
                # Import locally to avoid circular import at module load.
                try:
                    from app.telegram.notifications import send_poll_failure_report
                except ImportError:
                    send_poll_failure_report = None  # type: ignore
                if send_poll_failure_report is not None:
                    send_poll_failure_report(
                        bot_token=settings.telegram_bot_token,
                        chat_id=settings.telegram_chat_id,
                        sources=source_results,
                        run_id=run_id,
                    )
                    print(f"failure-report: sent for {len(failed)} failed source(s)")
                else:
                    # Fallback: numbers-only (no per-site list) as requested
                    import json

                    import httpx

                    text = f"⚠️ Poll completed — {datetime.now(UTC):%Y-%m-%d %H:%M UTC}\n{len(source_results)} checked, {len(source_results) - len(failed)} ok, {len(failed)} failed (run {run_id[:8]}…)"
                    with httpx.Client(timeout=30) as client:
                        client.post(
                            f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage",
                            content=json.dumps(
                                {"chat_id": settings.telegram_chat_id, "text": text}
                            ),
                            headers={"Content-Type": "application/json"},
                        )
                    print(f"failure-report: sent (fallback) for {len(failed)} failed source(s)")
        except Exception as exc:
            print(f"failure-report: FAILED - {exc}")

        finish_poll_run(
            supabase,
            run_id,
            status="completed",
            jobs_fetched=total_fetched,
            jobs_new=total_new,
            matches_considered=tally["considered"],
            matches_new=tally["matched"],
            telegram_sent=telegram_sent,
            email_sent=email_sent,
            sources=source_results,
        )
        return {
            "run_id": run_id,
            "status": "completed",
            "jobs_fetched": total_fetched,
            "jobs_new": total_new,
            "matches_new": tally["matched"],
            "telegram_sent": telegram_sent,
            "email_sent": email_sent,
            "sources": source_results,
        }
    except Exception as exc:
        print(f"poll run {run_id} FAILED: {exc}")
        try:
            finish_poll_run(supabase, run_id, status="failed", error=str(exc)[:500])
        except Exception:
            pass
        return {"run_id": run_id, "status": "failed", "error": str(exc)[:500]}
