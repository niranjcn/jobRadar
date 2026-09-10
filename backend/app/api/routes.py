"""REST API for the frontend dashboard.

Identity is resolved per request (session cookie). With JOBRADAR_REQUIRE_AUTH
off — the default — anonymous requests act as the owner account, preserving
the original single-user behavior exactly.
"""

from datetime import UTC, datetime, timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.adapters import adapter_for
from app.api.detect import detect_source
from app.auth import UserCtx, get_current_admin, require_product_access
from app.config import load_settings
from app.db import get_supabase, query
from app.geo import load_geo_index, map_location
from app.matcher import recompute_matches
from app.poller import create_poll_run as poller_create_run
from app.poller import (
    poll_all_sources,
    poll_source,
    run_pipeline_in_thread,
    stale_after_seconds,
    unhealthy_sources,
)
from app.schedule_store import (
    effective_intervals,
    last_checked_by_ats,
    load_interval_overrides,
    next_run_at,
    set_interval_override,
    source_count_by_ats,
)
from app.settings_store import load_location_mapping, save_location_mapping

router = APIRouter(prefix="/api")


def _settings() -> Any:
    return load_settings()


def _supabase():
    return get_supabase(_settings())


# ---------- schemas ----------


def _domain_for(domain: str = "", url: str = "") -> str | None:
    """Company domain for logo resolution: explicit value wins, else URL host."""
    if (domain or "").strip():
        return domain.strip().lower()
    try:
        from urllib.parse import urlparse

        host = (urlparse(url or "").hostname or "").strip().lower()
        return host or None
    except Exception:
        return None


class SourceCreate(BaseModel):
    company_name: str
    url: str = ""
    ats_type: str = ""
    board_identifier: str = ""
    domain: str = ""


class SourceUpdate(BaseModel):
    active: bool | None = None
    board_identifier: str | None = None
    domain: str | None = None


class PreferencesUpdate(BaseModel):
    roles: list[str] = []
    keywords: list[str] = []
    locations: list[str] = []
    seniority: list[str] = []
    excluded_companies: list[str] = []
    excluded_roles: list[str] = []
    notify_telegram: bool = True
    notify_email: bool = True
    alert_frequency: str = "immediate"
    telegram_scope: str = "matched"
    email_scope: str = "matched"
    notify_first_check: bool = True


class LocationMappingUpdate(BaseModel):
    enabled: bool | None = None
    remote_to: list[str] | None = None
    custom_aliases: dict[str, str] | None = None


class ScheduleUpdate(BaseModel):
    interval_seconds: int


class LocationPreview(BaseModel):
    location: str


# ---------- helpers ----------


def _company_names(supabase) -> dict[str, str]:
    response = supabase.table("sources").select("id, company_name").execute()
    return {src["id"]: src["company_name"] for src in response.data or []}


# ---------- stats ----------


@router.get("/stats")
def stats(user: Annotated[UserCtx, Depends(require_product_access)]) -> dict:
    settings = _settings()
    since = (datetime.now(UTC) - timedelta(days=7)).isoformat()

    row = query(
        settings,
        """
        select
          (select count(*)::int from jobs) as jobs_total,
          (select count(*)::int from jobs where first_seen_at >= %s) as jobs_7d,
          (select count(*)::int from sources where active) as companies,
          (select count(*)::int from job_matches where user_id = %s) as matches,
          (select coalesce(round(avg(match_score))::int, 0) from job_matches where user_id = %s) as avg_score
        """,
        (since, user.id, user.id),
    )[0]

    return {
        "jobs_total": row["jobs_total"],
        "jobs_new_7d": row["jobs_7d"],
        "companies": row["companies"],
        "matches": row["matches"],
        "avg_match_score": row["avg_score"],
        "sources_active": row["companies"],
    }


@router.get("/matches/summary")
def matches_summary(user: Annotated[UserCtx, Depends(require_product_access)]) -> dict:
    """Match counts per company for the matches page."""
    settings = _settings()
    rows = query(
        settings,
        """
        select s.company_name as company, s.domain, count(*)::int as matches
        from job_matches m
        join jobs j on j.id = m.job_id
        join sources s on s.id = j.source_id
        where m.user_id = %s
        group by s.company_name, s.domain
        order by matches desc, s.company_name
        """,
        (user.id,),
    )
    total = sum(row["matches"] for row in rows)
    return {"total": total, "companies": rows}


@router.get("/matches/jobs")
def matches_jobs(
    user: Annotated[UserCtx, Depends(require_product_access)],
    company: str = "",
    ats: str = "",
    since: str = "",
    limit: int = 100,
    offset: int = 0,
) -> dict:
    """All matched jobs for the user, optionally scoped to one company.

    Mirrors the job shape of /api/jobs so the frontend can render the same
    JobCard. Clicking a company card on the matches page uses this to list
    every matched role for that company (not just the latest N jobs).
    """
    settings = _settings()
    where = "m.user_id = %s"
    params: list[Any] = [user.id]
    if company:
        where += " and s.company_name = %s"
        params.append(company)
    if ats:
        where += " and s.ats_type = %s"
        params.append(ats)
    if since:
        where += " and m.created_at >= %s::timestamptz"
        params.append(since)

    rows = query(
        settings,
        f"""
        select j.id, j.source_id, j.external_job_id, j.title, j.location, j.url,
               j.first_seen_at, j.countries, j.is_remote,
               s.company_name, s.ats_type, s.domain, m.match_score, m.matched_on
        from job_matches m
        join jobs j on j.id = m.job_id
        join sources s on s.id = j.source_id
        where {where}
        order by m.match_score desc, j.first_seen_at desc
        limit %s offset %s
        """,
        (*params, limit, offset),
    )

    jobs = [
        {
            "id": row["id"],
            "source_id": row["source_id"],
            "external_job_id": row["external_job_id"],
            "title": row["title"],
            "location": row["location"],
            "url": row["url"],
            "description": None,
            "first_seen_at": row["first_seen_at"].isoformat() if row["first_seen_at"] else None,
            "company": row["company_name"],
            "ats_type": row["ats_type"],
            "domain": row.get("domain"),
            "countries": row["countries"] or [],
            "is_remote": row["is_remote"] or False,
            "match_score": row["match_score"],
            "matched_on": row["matched_on"] or [],
        }
        for row in rows
    ]

    total = query(
        settings,
        f"select count(*)::int as c from job_matches m join jobs j on j.id = m.job_id "
        f"join sources s on s.id = j.source_id where {where}",
        params,
    )[0]["c"]

    return {"jobs": jobs, "total": total, "limit": limit, "offset": offset}


# ---------- jobs ----------


@router.get("/jobs/filters")
def job_filters() -> dict:
    """Distinct companies, countries, and ats types present in the jobs table, for filters."""
    settings = _settings()
    companies = [
        row["company_name"]
        for row in query(
            settings,
            "select distinct s.company_name from sources s join jobs j on j.source_id = s.id "
            "order by s.company_name",
        )
    ]
    countries = [
        row["country"]
        for row in query(
            settings,
            "select distinct unnest(countries) as country from jobs where countries is not null "
            "order by 1",
        )
    ]
    ats_types = [
        row["ats_type"]
        for row in query(
            settings,
            "select distinct s.ats_type from sources s join jobs j on j.source_id = s.id "
            "order by s.ats_type",
        )
    ]
    return {"companies": companies, "countries": countries, "ats_types": ats_types}


@router.get("/jobs")
def list_jobs(
    user: Annotated[UserCtx, Depends(require_product_access)],
    q: str = "",
    ats: str = "",
    company: str = "",
    country: str = "",
    since: str = "",
    remote_only: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> dict:
    settings = _settings()

    since_cond = "" if not since else " and j.first_seen_at >= %s::timestamptz"
    remote_cond = " and j.is_remote = true" if remote_only else ""
    sql = f"""
        select j.id, j.source_id, j.external_job_id, j.title, j.location, j.url,
               j.first_seen_at, j.countries, j.is_remote,
               s.company_name, s.ats_type, s.domain
        from jobs j join sources s on s.id = j.source_id
        where (%s = '' or s.company_name ilike '%%' || %s || '%%')
          and (%s = '' or s.ats_type = %s)
          and (%s = '' or lower(j.title) ilike lower('%%' || %s || '%%'))
          and (%s = '' or %s = any(j.countries))
          {since_cond}{remote_cond}
        order by j.first_seen_at desc
        limit %s offset %s
    """
    params: list[Any] = [company, company, ats, ats, q, q, country.upper(), country.upper()]
    if since:
        params.append(since)
    params += [limit, offset]
    rows = query(settings, sql, params)

    # attach match info
    job_ids = [row["id"] for row in rows]
    match_by_id: dict[str, Any] = {}
    if job_ids:
        mrows = query(
            settings,
            "select job_id, matched_on, match_score from job_matches where user_id = %s and job_id = any(%s::uuid[])",
            (user.id, job_ids),
        )
        for m in mrows:
            match_by_id[m["job_id"]] = m

    jobs = []
    for row in rows:
        match = match_by_id.get(row["id"])
        jobs.append(
            {
                "id": row["id"],
                "source_id": row["source_id"],
                "external_job_id": row["external_job_id"],
                "title": row["title"],
                "location": row["location"],
                "url": row["url"],
                "description": None,
                "first_seen_at": row["first_seen_at"].isoformat() if row["first_seen_at"] else None,
                "company": row["company_name"],
                "ats_type": row["ats_type"],
                "domain": row.get("domain"),
                "countries": row["countries"] or [],
                "is_remote": row["is_remote"] or False,
                "match_score": match["match_score"] if match else None,
                "matched_on": match["matched_on"] if match else [],
            }
        )

    total_sql = (
        "select count(*)::int as c from jobs j join sources s on s.id = j.source_id "
        "where (%s = '' or s.company_name ilike '%%' || %s || '%%') and (%s = '' or s.ats_type = %s) "
        "and (%s = '' or lower(j.title) ilike lower('%%' || %s || '%%')) "
        "and (%s = '' or %s = any(j.countries))"
        + (" and j.first_seen_at >= %s::timestamptz" if since else "")
        + (" and j.is_remote = true" if remote_only else "")
    )
    total_params: list[Any] = [company, company, ats, ats, q, q, country.upper(), country.upper()]
    if since:
        total_params.append(since)
    total = query(settings, total_sql, total_params)[0]["c"]

    return {"jobs": jobs, "total": total, "limit": limit, "offset": offset}


@router.get("/jobs/{job_id}")
def get_job(job_id: str, user: Annotated[UserCtx, Depends(require_product_access)]) -> dict:
    settings = _settings()
    rows = query(
        settings,
        """
        select j.id, j.source_id, j.external_job_id, j.title, j.location, j.url,
               j.description, j.first_seen_at, j.countries, j.is_remote,
               s.company_name, s.ats_type, s.domain
        from jobs j join sources s on s.id = j.source_id
        where j.id = %s::uuid
        """,
        (job_id,),
    )
    if not rows:
        raise HTTPException(status_code=404, detail="job not found")
    row = rows[0]
    matches = query(
        settings,
        "select matched_on, match_score from job_matches where user_id = %s and job_id = %s::uuid",
        (user.id, job_id),
    )
    match = matches[0] if matches else None
    return {
        "id": row["id"],
        "source_id": row["source_id"],
        "external_job_id": row["external_job_id"],
        "title": row["title"],
        "location": row["location"],
        "url": row["url"],
        "description": row["description"],
        "first_seen_at": row["first_seen_at"].isoformat() if row["first_seen_at"] else None,
        "company": row["company_name"],
        "ats_type": row["ats_type"],
        "domain": row.get("domain"),
        "countries": row["countries"] or [],
        "is_remote": row["is_remote"] or False,
        "match_score": match["match_score"] if match else None,
        "matched_on": match["matched_on"] if match else [],
    }


# ---------- companies / sources ----------


@router.get("/companies")
def companies() -> dict:
    settings = _settings()
    rows = query(
        settings,
        """
        select s.id, s.company_name, s.ats_type, s.domain, s.last_checked_at, s.active,
               count(j.id)::int as job_count
        from sources s left join jobs j on j.source_id = s.id
        group by s.id
        order by s.company_name
        """,
    )
    for row in rows:
        row["last_checked_at"] = (
            row["last_checked_at"].isoformat() if row["last_checked_at"] else None
        )
    return {"companies": rows}


@router.get("/sources")
def sources(admin: Annotated[UserCtx, Depends(get_current_admin)]) -> dict:
    settings = _settings()
    rows = query(
        settings,
        """
        select s.id, s.company_name, s.ats_type, s.domain, s.board_identifier, s.last_checked_at,
               s.last_error, s.active, s.quiet_runs, count(j.id)::int as job_count
        from sources s left join jobs j on j.source_id = s.id
        group by s.id
        order by s.company_name
        """,
    )
    intervals = settings.ats_intervals
    result = []
    for row in rows:
        interval = intervals.get(row["ats_type"], 3600)
        last = row["last_checked_at"]
        last_error = row["last_error"]
        now = datetime.now(UTC)
        reason = None
        if last is None:
            status = "never"
            reason = "never checked yet"
        elif now - last > timedelta(seconds=stale_after_seconds(row, interval)):
            status = "stale"
            if last_error:
                reason = f"last check failed: {last_error}"
            else:
                expected = (
                    f"{interval // 60}m"
                    if interval % 3600 != 0 and interval % 60 == 0
                    else f"{interval // 3600}h"
                )
                reason = (
                    f"last successful check was {(now - last).total_seconds() // 60:.0f}m ago "
                    f"(expected every {expected})"
                )
        elif last_error:
            status = "stale"
            reason = f"recovered but last run reported: {last_error}"
        else:
            status = "healthy"
        row["last_checked_at"] = last.isoformat() if last else None
        row["poll_interval"] = interval
        row["status"] = status
        row["reason"] = reason
        row.pop("last_error", None)
        result.append(row)
    return {"sources": result, "intervals": intervals}


@router.get("/sources/unhealthy")
def sources_unhealthy(admin: Annotated[UserCtx, Depends(get_current_admin)]) -> dict:
    """Active sources whose status is stale/never (not healthy), with reason."""
    settings = _settings()
    supabase = _supabase()
    return {"unhealthy": unhealthy_sources(supabase, settings.ats_intervals)}


@router.post("/sources", status_code=201)
async def create_source(
    payload: SourceCreate, admin: Annotated[UserCtx, Depends(get_current_admin)]
) -> dict:
    supabase = _supabase()
    name = payload.company_name.strip()
    if not name:
        raise HTTPException(status_code=422, detail="company_name is required")

    if payload.ats_type and payload.board_identifier:
        ats, board = payload.ats_type, payload.board_identifier.strip()
    else:
        detected = await detect_source(name, payload.url)
        if not detected:
            raise HTTPException(
                status_code=422,
                detail="could not auto-detect an ATS for this company — provide ats_type and board_identifier manually",
            )
        ats, board = detected["ats_type"], detected["board_identifier"]

    response = (
        supabase.table("sources")
        .upsert(
            {
                "company_name": name,
                "ats_type": ats,
                "board_identifier": board,
                "domain": _domain_for(payload.domain, payload.url),
                "active": True,
            },
            on_conflict="company_name",
        )
        .execute()
    )
    row = response.data[0]
    return {
        "id": row["id"],
        "company_name": row["company_name"],
        "ats_type": row["ats_type"],
        "board_identifier": row["board_identifier"],
        "domain": row.get("domain"),
    }


@router.patch("/sources/{source_id}")
def update_source(
    source_id: str, payload: SourceUpdate, admin: Annotated[UserCtx, Depends(get_current_admin)]
) -> dict:
    supabase = _supabase()
    update: dict[str, Any] = {}
    if payload.active is not None:
        update["active"] = payload.active
    if payload.board_identifier:
        update["board_identifier"] = payload.board_identifier
    if payload.domain is not None:
        update["domain"] = payload.domain.strip().lower() or None
    if not update:
        raise HTTPException(status_code=422, detail="nothing to update")
    response = supabase.table("sources").update(update).eq("id", source_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="source not found")
    return {"ok": True, "source": response.data[0]}


@router.post("/sources/{source_id}/run")
async def run_source(source_id: str, admin: Annotated[UserCtx, Depends(get_current_admin)]) -> dict:
    settings = _settings()
    supabase = _supabase()
    response = supabase.table("sources").select("*").eq("id", source_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="source not found")
    source = response.data[0]
    adapter = adapter_for(source["ats_type"])
    from app.settings_store import load_location_mapping

    result = await run_pipeline_in_thread(
        poll_source(
            supabase,
            source,
            adapter,
            settings.max_posting_age_days,
            geo_settings=load_location_mapping(supabase),
        )
    )
    return {
        "ok": True,
        "company": result["company"],
        "fetched": result["fetched"],
        "new": result["new"],
        "first_check": result["first_check"],
    }


# ---------- poll runs ----------


class PollRunRequest(BaseModel):
    ats_type: str | None = None


@router.post("/poll/run")
async def run_poll(
    admin: Annotated[UserCtx, Depends(get_current_admin)],
    payload: PollRunRequest | None = None,
) -> dict:
    """Trigger a full ingestion pipeline run (manual button).

    Starts the poll in the background so the request returns immediately; the
    run's progress is tracked in poll_runs and surfaced via GET /poll/runs.
    """
    import asyncio

    settings = _settings()
    supabase = _supabase()
    ats_type = (payload.ats_type if payload else None) or None

    running = query(
        settings,
        "select id, started_at from poll_runs where status = 'running' limit 1",
    )
    if running:
        started = running[0]["started_at"]
        age_minutes = (datetime.now(UTC) - started).total_seconds() / 60
        if age_minutes > 45:
            # A crashed/killed run would otherwise block future polls forever.
            supabase.table("poll_runs").update(
                {
                    "status": "failed",
                    "finished_at": datetime.now(UTC).isoformat(),
                    "error": "stale: previous run did not complete (marked failed)",
                }
            ).eq("id", running[0]["id"]).execute()
        else:
            raise HTTPException(
                status_code=409,
                detail=f"a poll run is already in progress (id={running[0]['id']})",
            )

    run_id = poller_create_run(supabase, triggered_by="manual", ats_type=ats_type)
    asyncio.create_task(_run_poll_background(run_id, ats_type))
    return {"run_id": run_id, "status": "running", "ats_type": ats_type}


async def _run_poll_background(run_id: str, ats_type: str | None) -> None:
    try:
        await run_pipeline_in_thread(
            poll_all_sources(ats_type=ats_type, run_id=run_id, triggered_by="manual")
        )
    except Exception as exc:
        print(f"manual poll run {run_id} FAILED: {exc}")


@router.post("/poll/run-unhealthy")
async def run_unhealthy_poll(admin: Annotated[UserCtx, Depends(get_current_admin)]) -> dict:
    """Trigger an ingestion run limited to unhealthy (stale/never) sources."""
    import asyncio

    settings = _settings()
    supabase = _supabase()

    running = query(
        settings,
        "select id, started_at from poll_runs where status = 'running' limit 1",
    )
    if running:
        started = running[0]["started_at"]
        age_minutes = (datetime.now(UTC) - started).total_seconds() / 60
        if age_minutes > 45:
            supabase.table("poll_runs").update(
                {
                    "status": "failed",
                    "finished_at": datetime.now(UTC).isoformat(),
                    "error": "stale: previous run did not complete (marked failed)",
                }
            ).eq("id", running[0]["id"]).execute()
        else:
            raise HTTPException(
                status_code=409,
                detail=f"a poll run is already in progress (id={running[0]['id']})",
            )

    unhealthy = unhealthy_sources(supabase, settings.ats_intervals)
    source_ids = [source["id"] for source in unhealthy]
    if not source_ids:
        return {"run_id": None, "status": "completed", "sources": []}

    run_id = poller_create_run(supabase, triggered_by="manual", ats_type=None)
    asyncio.create_task(_run_unhealthy_background(run_id, source_ids))
    return {"run_id": run_id, "status": "running", "sources": unhealthy}


async def _run_unhealthy_background(run_id: str, source_ids: list[str]) -> None:
    try:
        await run_pipeline_in_thread(
            poll_all_sources(run_id=run_id, triggered_by="manual", source_ids=source_ids)
        )
    except Exception as exc:
        print(f"unhealthy poll run {run_id} FAILED: {exc}")


@router.get("/poll/runs")
def poll_runs(admin: Annotated[UserCtx, Depends(get_current_admin)], limit: int = 20) -> dict:
    """Recent poll runs with per-run summary + per-source breakdown."""
    settings = _settings()
    rows = query(
        settings,
        """
        select id, triggered_by, ats_type, status, started_at, finished_at,
               jobs_fetched, jobs_new, matches_considered, matches_new,
               telegram_sent, email_sent, sources, error
        from poll_runs
        order by started_at desc
        limit %s
        """,
        (limit,),
    )
    for row in rows:
        row["started_at"] = row["started_at"].isoformat() if row["started_at"] else None
        row["finished_at"] = row["finished_at"].isoformat() if row["finished_at"] else None
    return {"runs": rows}


# ---------- schedule ----------


@router.get("/schedule")
def schedule(admin: Annotated[UserCtx, Depends(get_current_admin)]) -> dict:
    """Polling schedule per ATS: effective interval, last check, next run."""
    settings = _settings()
    supabase = _supabase()
    env_intervals = settings.ats_intervals
    overrides = load_interval_overrides(supabase)
    intervals = effective_intervals(env_intervals, overrides)
    last_checked = last_checked_by_ats(settings)
    counts = source_count_by_ats(settings)

    ats_order = [
        "greenhouse",
        "lever",
        "ashby",
        "workday",
        "oracle",
        "icims",
        "successfactors",
        "phenom",
        "avature",
        "emirates",
        "google",
        "amazon",
        "custom",
        "remotive",
        "weworkremotely",
    ]
    entries = []
    for ats in ats_order:
        if ats not in intervals:
            continue
        interval = intervals[ats]
        entries.append(
            {
                "ats_type": ats,
                "interval_seconds": interval,
                "overridden": ats in overrides,
                "env_interval_seconds": env_intervals.get(ats, interval),
                "concurrency": settings.ats_concurrency.get(ats, 8),
                "last_checked_at": last_checked.get(ats),
                "next_run_at": _scheduled_next_run(ats)
                or next_run_at(interval, last_checked.get(ats)),
                "source_count": counts.get(ats, 0),
            }
        )
    return {"schedule": entries}


def _scheduled_next_run(ats_type: str) -> str | None:
    """Prefer the live APScheduler next-run time; fall back to an estimate.

    The scheduler may be disabled or the job not registered, so this must
    never raise — the caller already has a best-effort estimate.
    """
    try:
        from app.main import scheduler_next_run

        return scheduler_next_run(ats_type)
    except Exception:
        return None


@router.put("/schedule/{ats_type}")
def update_schedule(
    ats_type: str, payload: ScheduleUpdate, admin: Annotated[UserCtx, Depends(get_current_admin)]
) -> dict:
    settings = _settings()
    supabase = _supabase()
    if ats_type not in settings.ats_intervals:
        raise HTTPException(status_code=404, detail=f"unknown ats_type: {ats_type}")
    if payload.interval_seconds < 60:
        raise HTTPException(status_code=422, detail="interval must be at least 60 seconds")
    set_interval_override(supabase, ats_type, payload.interval_seconds)
    from app.main import reschedule_ats

    try:
        rescheduled = reschedule_ats(ats_type, payload.interval_seconds)
    except Exception as exc:
        print(f"schedule reschedule {ats_type} FAILED: {exc}")
        rescheduled = False
    return {
        "ok": True,
        "ats_type": ats_type,
        "interval_seconds": payload.interval_seconds,
        "rescheduled": rescheduled,
    }


@router.delete("/schedule/{ats_type}")
def delete_schedule(ats_type: str, admin: Annotated[UserCtx, Depends(get_current_admin)]) -> dict:
    """Revert an override back to the env-default interval."""
    settings = _settings()
    supabase = _supabase()
    if ats_type not in settings.ats_intervals:
        raise HTTPException(status_code=404, detail=f"unknown ats_type: {ats_type}")
    supabase.table("poll_schedule").delete().eq("ats_type", ats_type).execute()
    return {"ok": True, "ats_type": ats_type}


# ---------- preferences ----------


@router.get("/preferences")
def get_preferences(user: Annotated[UserCtx, Depends(require_product_access)]) -> dict:
    settings = _settings()
    rows = query(
        settings,
        """
        select roles, keywords, locations, seniority, excluded_companies,
               excluded_roles, notify_telegram, notify_email, alert_frequency,
               telegram_scope, email_scope, notify_first_check
        from preferences where user_id = %s
        """,
        (user.id,),
    )
    env = settings.preferences
    if not rows:
        # No row yet: expose env defaults so the UI shows what is configured
        # before the first save. Once saved, the DB row is the source of truth.
        return {
            "roles": env.get("roles") or [],
            "keywords": env.get("keywords") or [],
            "locations": env.get("locations") or [],
            "seniority": env.get("seniority") or [],
            "excluded_companies": env.get("excluded_companies") or [],
            "excluded_roles": env.get("excluded_roles") or [],
            "notify_telegram": True,
            "notify_email": True,
            "alert_frequency": "immediate",
            "telegram_scope": "matched",
            "email_scope": "matched",
            "notify_first_check": True,
        }
    row = rows[0]
    # DB row wins completely — including empty lists, so clearing a field in the
    # UI actually sticks and never falls back to env values.
    return {
        "roles": row["roles"] or [],
        "keywords": row["keywords"] or [],
        "locations": row["locations"] or [],
        "seniority": row["seniority"] or [],
        "excluded_companies": row["excluded_companies"] or [],
        "excluded_roles": row["excluded_roles"] or [],
        "notify_telegram": row["notify_telegram"],
        "notify_email": row["notify_email"],
        "alert_frequency": row["alert_frequency"],
        "telegram_scope": row["telegram_scope"],
        "email_scope": row["email_scope"],
        "notify_first_check": row["notify_first_check"],
    }


@router.put("/preferences")
def put_preferences(
    payload: PreferencesUpdate, user: Annotated[UserCtx, Depends(require_product_access)]
) -> dict:
    settings = _settings()
    supabase = _supabase()

    # Plan limits cap new writes only — stored data is never mutated here.
    if user.role == "user":
        from app.access import active_subscription
        from app.entitlements import validate_preferences_against_limits

        sub = active_subscription(settings, user.id)
        violations = validate_preferences_against_limits(
            payload.model_dump(), (sub or {}).get("plan_limits")
        )
        if violations:
            raise HTTPException(status_code=422, detail="; ".join(violations))

    row = {
        "user_id": user.id,
        "roles": payload.roles,
        "keywords": payload.keywords,
        "locations": payload.locations,
        "seniority": payload.seniority,
        "excluded_companies": payload.excluded_companies,
        "excluded_roles": payload.excluded_roles,
        "notify_telegram": payload.notify_telegram,
        "notify_email": payload.notify_email,
        "alert_frequency": payload.alert_frequency,
        "telegram_scope": payload.telegram_scope,
        "email_scope": payload.email_scope,
        "notify_first_check": payload.notify_first_check,
        "updated_at": datetime.now(UTC).isoformat(),
    }
    supabase.table("preferences").upsert(row, on_conflict="user_id").execute()
    try:
        recomputed = recompute_matches(supabase, user_id=user.id)
        return {"ok": True, "preferences": get_preferences(), "recomputed": recomputed}
    except Exception as exc:
        print(f"preferences recompute FAILED: {exc}")
        return {"ok": True, "preferences": get_preferences()}


# ---------- notifications ----------


@router.get("/notifications")
def notifications(
    user: Annotated[UserCtx, Depends(require_product_access)], limit: int = 50
) -> dict:
    settings = _settings()
    rows = query(
        settings,
        """
        select n.id, n.job_id, n.channel, n.sent_at, j.title, s.company_name, s.domain
        from notifications_sent n
        left join jobs j on j.id = n.job_id
        left join sources s on s.id = j.source_id
        where n.user_id = %s
        order by n.sent_at desc
        limit %s
        """,
        (user.id, limit),
    )
    for row in rows:
        row["sent_at"] = row["sent_at"].isoformat() if row["sent_at"] else None
    return {"notifications": rows}


# ---------- location mapping ----------


@router.get("/geo/countries")
def geo_countries() -> dict:
    """Country list for the preferences dropdown (name + ISO2 code)."""
    idx = load_geo_index()
    countries = sorted(
        [{"name": name.title(), "code": code} for name, code in idx["countries"].items()],
        key=lambda c: c["name"],
    )
    return {"countries": countries}


@router.get("/settings/location-mapping")
def get_location_mapping(admin: Annotated[UserCtx, Depends(get_current_admin)]) -> dict:
    supabase = _supabase()
    settings = load_location_mapping(supabase)
    index = load_geo_index()
    return {
        "settings": settings,
        "index_stats": {
            "countries": len(index["countries"]),
            "states": len(index["states"]),
            "cities": len(index["cities"]),
        },
    }


@router.put("/settings/location-mapping")
def put_location_mapping(
    payload: LocationMappingUpdate, admin: Annotated[UserCtx, Depends(get_current_admin)]
) -> dict:
    supabase = _supabase()
    current = load_location_mapping(supabase)
    update = {
        "enabled": payload.enabled if payload.enabled is not None else current.get("enabled", True),
        "remote_to": payload.remote_to
        if payload.remote_to is not None
        else current.get("remote_to", []),
        "custom_aliases": payload.custom_aliases
        if payload.custom_aliases is not None
        else current.get("custom_aliases", {}),
    }
    save_location_mapping(supabase, update)
    try:
        recomputed = recompute_matches(supabase, user_id=admin.id)
        return {"ok": True, "settings": load_location_mapping(supabase), "recomputed": recomputed}
    except Exception as exc:
        print(f"location-mapping recompute FAILED: {exc}")
        return {"ok": True, "settings": load_location_mapping(supabase)}


@router.post("/settings/location-mapping/preview")
def preview_location_mapping(payload: LocationPreview) -> dict:
    supabase = _supabase()
    settings = load_location_mapping(supabase)
    result = map_location(payload.location, settings)
    return {"location": payload.location, **result}
