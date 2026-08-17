import asyncio
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from supabase import Client

from app.adapters import adapter_for
from app.config import load_settings
from app.db import get_supabase, query
from app.geo import map_job_locations, map_location
from app.matcher import load_notification_settings, match_all, sync_preferences
from app.models import NormalizedJob, strip_html
from app.notify import send_email_notifications
from app.settings_store import load_location_mapping
from app.telegram import send_telegram_notifications

DETAIL_CONCURRENCY = 15
SOURCE_CONCURRENCY = 8
IN_BATCH = 200
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


def clear_descriptions(supabase: Client, candidates: list[tuple[str, str]]) -> int:
    """Null out the description of newly-seen jobs once their alert is sent.

    Descriptions are only needed transiently (keyword matching + first alert).
    After both notification channels have run, reclaim the space.
    """
    if not candidates:
        return 0
    by_source: dict[str, list[str]] = {}
    for source_id, external_job_id in candidates:
        by_source.setdefault(source_id, []).append(external_job_id)
    cleared = 0
    for source_id, external_ids in by_source.items():
        for start in range(0, len(external_ids), IN_BATCH):
            batch = external_ids[start : start + IN_BATCH]
            response = (
                supabase.table("jobs")
                .update({"description": None})
                .eq("source_id", source_id)
                .in_("external_job_id", batch)
                .execute()
            )
            cleared += len(response.data or [])
    return cleared


def _detail_location_hints(detail: dict) -> tuple[str | None, list[str]]:
    """Pull the best location + office/alternate location strings from a detail payload."""
    location_name: str | None = None
    offices: list[str] = []

    loc = detail.get("location")
    if isinstance(loc, dict) and loc.get("name"):
        location_name = loc["name"]
    elif isinstance(loc, str) and loc:
        location_name = loc

    for office in detail.get("offices") or []:
        name = office.get("name")
        if name:
            offices.append(name)

    for key in ("additionalLocations", "secondaryLocations", "locations"):
        for item in detail.get(key) or []:
            if isinstance(item, str) and item:
                offices.append(item)
            elif isinstance(item, dict):
                name = item.get("location") or item.get("name")
                if name:
                    offices.append(name)

    categories = detail.get("categories") or {}
    if isinstance(categories, dict):
        all_locations = categories.get("allLocations") or []
        if isinstance(all_locations, list):
            offices.extend(loc for loc in all_locations if loc)
        elif isinstance(all_locations, str) and all_locations:
            offices.append(all_locations)
    return location_name, offices


def update_job_detail(
    supabase: Client, source_id: str, external_job_id: str, description: str, detail: dict
) -> None:
    location_name, offices = _detail_location_hints(detail)
    mapped = map_job_locations(location_name, offices, load_location_mapping(supabase))
    update: dict[str, Any] = {
        "description": strip_html(description),
        "countries": mapped["countries"],
        "is_remote": mapped["is_remote"],
    }
    if location_name:
        current = (
            supabase.table("jobs")
            .select("location")
            .eq("source_id", source_id)
            .eq("external_job_id", external_job_id)
            .execute()
        )
        if not (current.data and current.data[0].get("location")):
            update["location"] = location_name
    supabase.table("jobs").update(update).eq("source_id", source_id).eq(
        "external_job_id", external_job_id
    ).execute()


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


async def enrich_jobs(
    supabase: Client, source: dict[str, Any], adapter, external_ids: list[str]
) -> None:
    if not external_ids:
        return
    semaphore = asyncio.Semaphore(DETAIL_CONCURRENCY)

    async def fetch_and_store(job_id: str) -> None:
        async with semaphore:
            detail = await adapter.fetch_job_detail(source["board_identifier"], job_id)
            if not detail:
                return
            update_job_detail(
                supabase, source["id"], job_id, adapter.extract_description(detail), detail
            )

    results = await asyncio.gather(
        *(fetch_and_store(job_id) for job_id in external_ids), return_exceptions=True
    )
    for result in results:
        if isinstance(result, Exception):
            print(f"{source['company_name']}: detail enrichment failed - {result}")


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


def fetch_candidate_jobs(
    supabase: Client, candidates: list[tuple[str, str]]
) -> list[dict[str, Any]]:
    """Fetch the newly-discovered candidate job rows once so the Telegram and
    email notification paths share a single lookup instead of each refetching
    the same candidates."""
    if not candidates:
        return []
    by_source: dict[str, list[str]] = {}
    for source_id, external_job_id in candidates:
        by_source.setdefault(source_id, []).append(external_job_id)
    jobs: list[dict[str, Any]] = []
    for source_id, external_ids in by_source.items():
        for start in range(0, len(external_ids), IN_BATCH):
            batch = external_ids[start : start + IN_BATCH]
            response = (
                supabase.table("jobs")
                .select("id, source_id, title, location, url")
                .eq("source_id", source_id)
                .in_("external_job_id", batch)
                .execute()
            )
            jobs.extend(response.data or [])
    return jobs


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
    if not first_check:
        await enrich_jobs(supabase, source, adapter, [row["external_job_id"] for row in new_rows])
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

        candidates: list[tuple[str, str]] = []
        source_results: list[dict[str, Any]] = []
        semaphore = asyncio.Semaphore(SOURCE_CONCURRENCY)
        total_fetched = 0
        total_new = 0
        notify_settings = load_notification_settings(supabase)
        notify_first_check = notify_settings.get("notify_first_check", True)

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
                    if not result["first_check"] or notify_first_check:
                        candidates.extend(
                            (result["source_id"], job_id) for job_id in result["new_ids"]
                        )
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

        sync_preferences(supabase, settings.preferences)
        match_result = match_all(supabase, candidates=candidates)
        matches_new = match_result.get("matched", 0)
        print(
            f"matching: result={match_result.get('result')}, "
            f"considered={match_result.get('considered')}, "
            f"matched={matches_new}"
        )

        notify_settings = load_notification_settings(supabase)
        telegram_ui = notify_settings.get("notify_telegram", True)
        email_ui = notify_settings.get("notify_email", True)
        telegram_scope = notify_settings.get("telegram_scope", "all")
        email_scope = notify_settings.get("email_scope", "matched")

        candidate_jobs = fetch_candidate_jobs(supabase, candidates)

        telegram_sent = 0
        try:
            sent, candidate = send_telegram_notifications(
                supabase,
                enabled=settings.telegram_enabled and telegram_ui,
                bot_token=settings.telegram_bot_token,
                chat_id=settings.telegram_chat_id,
                candidates=candidates,
                jobs=candidate_jobs,
                scope=telegram_scope,
            )
            telegram_sent = sent
            print(f"notify-tg: sent={sent} candidates={candidate}")
        except Exception as exc:
            print(f"notify-tg: FAILED - {exc}")

        email_sent = 0
        try:
            sent, candidate = send_email_notifications(
                supabase,
                enabled=settings.notify_enabled and email_ui,
                api_key=settings.resend_api_key,
                to_addresses=settings.notify_to,
                candidates=candidates,
                jobs=candidate_jobs,
                scope=email_scope,
            )
            email_sent = sent
            print(f"notify: sent={sent} candidates={candidate}")
        except Exception as exc:
            print(f"notify: FAILED - {exc}")

        cleared = clear_descriptions(supabase, candidates)
        print(f"descriptions: cleared {cleared} new-job description(s) after notify")

        finish_poll_run(
            supabase,
            run_id,
            status="completed",
            jobs_fetched=total_fetched,
            jobs_new=total_new,
            matches_considered=match_result.get("considered", 0),
            matches_new=matches_new,
            telegram_sent=telegram_sent,
            email_sent=email_sent,
            sources=source_results,
        )
        return {
            "run_id": run_id,
            "status": "completed",
            "jobs_fetched": total_fetched,
            "jobs_new": total_new,
            "matches_new": matches_new,
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
