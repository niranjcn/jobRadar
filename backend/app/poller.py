import asyncio
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import httpx
from supabase import Client

from app.adapters import adapter_for
from app.adapters.http import RetryingClient
from app.config import load_settings
from app.db import close_async_pool, get_supabase, open_async_pool, query_async
from app.geo import map_location
from app.matcher import load_notification_settings, sync_preferences
from app.models import NormalizedJob
from app.notification_queue import drain_due_notifications, load_audience, match_and_enqueue
from app.settings_store import load_location_mapping

SOURCE_CONCURRENCY = 8  # fallback when ats_type not in ATS_CONCURRENCY
MAX_POSTING_AGE_DAYS = 90
SOURCES_FILE = Path(__file__).resolve().parent.parent / "sources.json"

# Backoff for recently 404'd boards — skip re-poll for 12h to save egress and avoid hammering dead boards.
NOT_FOUND_BACKOFF_SECONDS = 12 * 3600

# Quiet-board backoff: a healthy board with this many consecutive no-new runs is
# polled every QUIET_SKIP_MULTIPLE-th interval on scheduled per-ATS runs (it
# only delays discovery, never misses: any new job resets the counter, manual
# and global runs always poll everything).
QUIET_RUNS_THRESHOLD = 5
QUIET_SKIP_MULTIPLE = 3


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
                    "domain": (entry.get("domain") or "").strip().lower() or None,
                    "active": entry.get("active", True),
                }
            ],
            on_conflict="company_name",
        ).execute()


def fetch_sources(supabase: Client) -> list[dict[str, Any]]:
    response = supabase.table("sources").select("*").eq("active", True).execute()
    return response.data


def stale_after_seconds(source: dict[str, Any], interval: int) -> int:
    """How long without a check before a source counts as stale.

    Quiet boards (QUIET_RUNS_THRESHOLD+ consecutive no-new runs) are only
    polled every QUIET_SKIP_MULTIPLE-th interval by design, so judging them
    by the normal 2x-interval bar would flag healthy-but-quiet boards as
    stale forever. They get 2x their own (slower) cadence instead. Boards
    whose last check errored keep the strict bar — errors deserve attention.
    """
    quiet = int(source.get("quiet_runs") or 0) >= QUIET_RUNS_THRESHOLD
    if quiet and not source.get("last_error"):
        return interval * QUIET_SKIP_MULTIPLE * 2
    return interval * 2


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
    if now - last > timedelta(seconds=stale_after_seconds(source, interval)):
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


async def fetch_existing_job_ids(supabase: Client, source_id: str) -> set[str]:
    """External job IDs already stored for a source.

    Uses a single pooled async SQL query instead of paginating 1000-row REST pages
    (a 20k-job source used to cost 20 sequential HTTP round-trips per poll).
    """
    rows = await query_async(
        load_settings(),
        "select external_job_id from jobs where source_id = %s",
        (source_id,),
    )
    return {row["external_job_id"] for row in rows}


async def fetch_existing_job_ids_batch(
    supabase: Client, source_ids: list[str]
) -> dict[str, set[str]]:
    """Batch version: one async query for many sources (Tier 2).

    One `SELECT ... WHERE source_id = ANY(...)` replaces N per-source queries (200 queries -> 1).
    Returns dict source_id -> set[external_job_id]. Missing sources get empty set.
    """
    if not source_ids:
        return {}
    rows = await query_async(
        load_settings(),
        "select source_id, external_job_id from jobs where source_id = any(%s::uuid[])",
        (source_ids,),
    )
    out: dict[str, set[str]] = {sid: set() for sid in source_ids}
    for row in rows:
        sid = str(row["source_id"])
        # query returns uuid objects that become strings via json_safe, but be safe
        if sid not in out:
            out[sid] = set()
        out[sid].add(row["external_job_id"])
    return out


def upsert_jobs(supabase: Client, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    supabase.table("jobs").upsert(rows, on_conflict="source_id,external_job_id").execute()


def mark_checked(supabase: Client, source_id: str, quiet_runs: int = 0) -> None:
    supabase.table("sources").update(
        {
            "last_checked_at": datetime.now(UTC).isoformat(),
            "last_error": None,
            "quiet_runs": quiet_runs,
        }
    ).eq("id", source_id).execute()


def next_quiet_runs(source: dict[str, Any], first_check: bool, new_count: int) -> int:
    """Consecutive no-new counter for quiet-board backoff.

    Resets on first checks and on any new job; otherwise increments. Error runs
    never reach here (mark_error path), so failures don't count as quiet.
    """
    if first_check or new_count > 0:
        return 0
    return int(source.get("quiet_runs") or 0) + 1


def quiet_due(
    source: dict[str, Any],
    interval: int,
    now: datetime,
    *,
    triggered_by: str,
    ats_type: str | None,
) -> tuple[bool, str | None]:
    """Whether a source is due on this run (quiet-board backoff).

    Returns (True, None) when due, (False, reason) when skipped. Only scheduled
    per-ATS runs skip; manual and global (ats_type=None) runs always poll
    everything, so nothing is ever missed — quiet boards just check less often.
    """
    if triggered_by != "scheduled" or not ats_type:
        return True, None
    quiet = int(source.get("quiet_runs") or 0)
    if quiet < QUIET_RUNS_THRESHOLD:
        return True, None
    last = source.get("last_checked_at")
    if last is None:
        return True, None
    if isinstance(last, str):
        try:
            last = datetime.fromisoformat(last)
        except ValueError:
            return True, None
    if (now - last).total_seconds() < interval * QUIET_SKIP_MULTIPLE:
        return False, (
            f"quiet board: {quiet} consecutive no-new runs, "
            f"checking every {QUIET_SKIP_MULTIPLE}rd interval"
        )
    return True, None


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
    *,
    client=None,
    existing_ids: set[str] | None = None,
    geo_settings: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Poll one source. Tier 2: if `client` (shared RetryingClient) is given, reuse it to keep TCP alive.
    If `existing_ids` is given, skip the per-source SELECT and use the batch result.
    If `geo_settings` is given, reuse it instead of re-reading the location
    mapping from the DB (one fewer query per source per poll)."""
    jobs = await adapter.fetch_jobs(source["board_identifier"], client=client)
    first_check = source.get("last_checked_at") is None
    if geo_settings is None:
        geo_settings = load_location_mapping(supabase)
    for job in jobs:
        if job.location:
            mapped = map_location(job.location, geo_settings)
            job.countries = mapped["countries"]
            job.is_remote = mapped["is_remote"]
    jobs = [j for j in jobs if _is_within_age(j, max_posting_age_days)]
    rows = dedupe_rows([job.to_row(source_id=source["id"]) for job in jobs])
    existing = (
        existing_ids
        if existing_ids is not None
        else await fetch_existing_job_ids(supabase, source["id"])
    )
    new_rows = [row for row in rows if row["external_job_id"] not in existing]
    for row in rows:
        if row["external_job_id"] in existing:
            row.pop("description", None)
    upsert_jobs(supabase, rows)
    mark_checked(supabase, source["id"], next_quiet_runs(source, first_check, len(new_rows)))
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
        # Tier 3 / Step C: open the shared async pool for this run's event loop.
        # Always closed in the finally below, on every exit path.
        await open_async_pool(settings)
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
        # Tier 1: per-ATS concurrency from settings (env-overridable via
        # POLL_CONCURRENCY_{ATS}; heavy boards run 10-way since rate limits are
        # per-host and the client backs off on 429). For a mixed global poll
        # (ats_type=None), use semaphores per ATS so a heavy ATS never starves light ones.
        _ATS_CC = dict(getattr(settings, "ats_concurrency", None) or {})
        if not _ATS_CC:
            try:
                from app.config import ATS_CONCURRENCY as _ATS_DEFAULTS

                _ATS_CC = dict(_ATS_DEFAULTS)
            except Exception:
                _ATS_CC = {}
        # One semaphore per ATS type; fallback to SOURCE_CONCURRENCY for unknown types.
        _sems: dict[str, asyncio.Semaphore] = {}

        def _sem_for(ats: str) -> asyncio.Semaphore:
            if ats not in _sems:
                _sems[ats] = asyncio.Semaphore(int(_ATS_CC.get(ats, SOURCE_CONCURRENCY)))
            return _sems[ats]

        # Tier 1: skip recently 404'd boards for 12h to save egress and avoid hammering dead boards.
        # This is the "404 backoff" — a board that returned 404 and was checked <12h ago is skipped.
        # It stays `active=true` so it can recover without manual re-activation, but we don't waste time on it every hour.
        _now = datetime.now(UTC)
        _filtered_sources: list[dict[str, Any]] = []
        _skipped: list[dict[str, Any]] = []
        for _s in sources:
            _err = _s.get("last_error") or ""
            _last = _s.get("last_checked_at")
            if _last is None:
                _filtered_sources.append(_s)
                continue
            if isinstance(_last, str):
                try:
                    _last = datetime.fromisoformat(_last)
                except ValueError:
                    _filtered_sources.append(_s)
                    continue
            if "404" in _err and (_now - _last).total_seconds() < NOT_FOUND_BACKOFF_SECONDS:
                _skipped.append(
                    {
                        "company": _s["company_name"],
                        "ats_type": _s["ats_type"],
                        "status": "skipped",
                        "reason": "404 backoff 12h",
                    }
                )
            else:
                _filtered_sources.append(_s)
        if _skipped:
            print(f"poll: skipping {_skipped.__len__()} recently 404'd boards for 12h backoff")
            # Record skipped as source_results so the timing page shows them as skipped, not missing.
            source_results.extend(_skipped)
        sources = _filtered_sources

        # Quiet-board backoff: healthy boards with 5+ consecutive no-new runs are
        # polled every 3rd interval on scheduled per-ATS runs. Manual and global
        # runs always poll everything (see quiet_due).
        _quiet_skipped: list[dict[str, Any]] = []
        if triggered_by == "scheduled" and ats_type:
            _interval = settings.ats_intervals.get(ats_type, 3600)
            _still_due: list[dict[str, Any]] = []
            for _s in sources:
                _due, _reason = quiet_due(
                    _s, _interval, _now, triggered_by=triggered_by, ats_type=ats_type
                )
                if _due:
                    _still_due.append(_s)
                else:
                    _quiet_skipped.append(
                        {
                            "company": _s["company_name"],
                            "ats_type": _s["ats_type"],
                            "status": "skipped",
                            "reason": _reason,
                        }
                    )
            if _quiet_skipped:
                print(f"poll: skipping {_quiet_skipped.__len__()} quiet boards for this run")
                source_results.extend(_quiet_skipped)
            sources = _still_due

        # Tier 2: batch existing_ids after 404 filtering — one async query for
        # all remaining sources.
        _existing_map: dict[str, set[str]] = {}
        if sources:
            try:
                _existing_map = await fetch_existing_job_ids_batch(
                    supabase, [s["id"] for s in sources]
                )
            except Exception as e:
                print(f"batch existing_ids failed, falling back to per-source: {e}")
                _existing_map = {}

        total_fetched = 0
        total_new = 0

        # Tier 2: one shared HTTP client for this poll — reuses TCP/TLS across all boards.
        # Limits sized for 10-way per-ATS concurrency with overlapping ATS runs.
        async with RetryingClient(
            timeout=30.0, limits=httpx.Limits(max_keepalive_connections=50, max_connections=100)
        ) as _shared_client:

            async def _poll(source: dict[str, Any]) -> None:
                nonlocal total_fetched, total_new
                ats = source.get("ats_type") or "custom"
                sem = _sem_for(ats)
                async with sem:
                    entry: dict[str, Any] = {
                        "company": source["company_name"],
                        "ats_type": ats,
                        "status": "ok",
                    }
                    t0 = asyncio.get_event_loop().time()
                    try:
                        adapter = adapter_for(ats)
                        result = await poll_source(
                            supabase,
                            source,
                            adapter,
                            settings.max_posting_age_days,
                            client=_shared_client,
                            existing_ids=_existing_map.get(source["id"]),
                            geo_settings=geo_settings,
                        )
                        entry["fetched"] = result["fetched"]
                        entry["new"] = result["new"]
                        entry["first_check"] = result["first_check"]
                        total_fetched += result["fetched"]
                        total_new += result["new"]
                        print(
                            f"{result['company']}: fetched {result['fetched']}, new {result['new']}"
                        )
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
                    except Exception as exc:
                        entry["status"] = "error"
                        entry["error"] = str(exc)[:300]
                        print(f"{source['company_name']}: FAILED - {exc}")
                        try:
                            mark_error(supabase, source, exc)
                        except Exception as mark_err:
                            print(f"{source['company_name']}: could not record error - {mark_err}")
                    finally:
                        # Duration per source in milliseconds — used by /poll/timings page.
                        entry["duration_ms"] = int((asyncio.get_event_loop().time() - t0) * 1000)
                    source_results.append(entry)

            await asyncio.gather(*(_poll(source) for source in sources))

        print(
            f"matching: considered={tally['considered']}, "
            f"matched={tally['matched']}, enqueued={tally['enqueued']}"
        )

        # Batch drain after all 200 are checked — matching is sent first,
        # numbers-only, and only when there are new matches (early-return
        # when pending==0 in notification_queue). No failure report, as
        # requested: only new matching job alerts like before.
        drained = drain_due_notifications(settings, supabase)
        telegram_sent = drained["sent_telegram"]
        email_sent = drained["sent_email"]

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
    finally:
        try:
            await close_async_pool()
        except Exception as exc:
            print(f"poll run {run_id}: async pool close failed: {exc}")
