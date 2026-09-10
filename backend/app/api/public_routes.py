"""Public (unauthenticated) jobs API for the public browse page.

The authenticated /api/jobs endpoints attach per-user match info and require
a session. The public browse page needs the same job catalog without any
login, so these endpoints return the same job shape with match fields left
empty. No user data is exposed.
"""

from typing import Any

from fastapi import APIRouter, HTTPException

from app.config import load_settings
from app.db import query

router = APIRouter(prefix="/api/public", tags=["public"])

MAX_LIMIT = 100


def _settings() -> Any:
    return load_settings()


@router.get("/jobs/filters")
def public_job_filters() -> dict:
    """Distinct companies, countries, and ats types — same data as /api/jobs/filters."""
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
def public_list_jobs(
    q: str = "",
    ats: str = "",
    company: str = "",
    country: str = "",
    since: str = "",
    remote_only: bool = False,
    mode: str = "",
    limit: int = 50,
    offset: int = 0,
) -> dict:
    """Public job listing with every available filter. No auth required.

    mode narrows by work mode: remote (flagged remote), hybrid (mentions
    hybrid in title/location — heuristic, sources expose no hybrid flag),
    onsite (everything else).
    """
    settings = _settings()
    limit = max(1, min(limit, MAX_LIMIT))
    offset = max(0, offset)

    since_cond = "" if not since else " and j.first_seen_at >= %s::timestamptz"
    remote_cond = " and j.is_remote = true" if remote_only else ""
    mode = (mode or "").strip().lower()
    if mode == "remote":
        mode_cond = " and j.is_remote = true"
    elif mode == "hybrid":
        mode_cond = (
            " and j.is_remote = false"
            " and (lower(j.title) like '%%hybrid%%' or lower(j.location) like '%%hybrid%%')"
        )
    elif mode == "onsite":
        mode_cond = (
            " and j.is_remote = false"
            " and lower(coalesce(j.title, '')) not like '%%hybrid%%'"
            " and lower(coalesce(j.location, '')) not like '%%hybrid%%'"
        )
    else:
        mode_cond = ""
    sql = f"""
        select j.id, j.source_id, j.external_job_id, j.title, j.location, j.url,
               j.first_seen_at, j.countries, j.is_remote,
               s.company_name, s.ats_type, s.domain
        from jobs j join sources s on s.id = j.source_id
        where (%s = '' or s.company_name ilike '%%' || %s || '%%')
          and (%s = '' or s.ats_type = %s)
          and (%s = '' or lower(j.title) ilike lower('%%' || %s || '%%'))
          and (%s = '' or %s = any(j.countries))
          {since_cond}{remote_cond}{mode_cond}
        order by j.first_seen_at desc
        limit %s offset %s
    """
    params: list[Any] = [company, company, ats, ats, q, q, country.upper(), country.upper()]
    if since:
        params.append(since)
    params += [limit, offset]
    rows = query(settings, sql, params)

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
            "match_score": None,
            "matched_on": [],
        }
        for row in rows
    ]

    total_sql = (
        "select count(*)::int as c from jobs j join sources s on s.id = j.source_id "
        "where (%s = '' or s.company_name ilike '%%' || %s || '%%') and (%s = '' or s.ats_type = %s) "
        "and (%s = '' or lower(j.title) ilike lower('%%' || %s || '%%')) "
        "and (%s = '' or %s = any(j.countries))"
        + (" and j.first_seen_at >= %s::timestamptz" if since else "")
        + (" and j.is_remote = true" if remote_only else "")
        + mode_cond
    )
    total_params: list[Any] = [company, company, ats, ats, q, q, country.upper(), country.upper()]
    if since:
        total_params.append(since)
    total = query(settings, total_sql, total_params)[0]["c"]

    return {"jobs": jobs, "total": total, "limit": limit, "offset": offset}


@router.get("/jobs/{job_id}")
def public_get_job(job_id: str) -> dict:
    """Public single-job detail. No auth required."""
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
        "match_score": None,
        "matched_on": [],
    }


@router.get("/companies")
def public_companies() -> dict:
    """Companies with domains + job counts for the public browse page (logo strip, stats)."""
    settings = _settings()
    rows = query(
        settings,
        """
        select s.company_name, s.domain, s.ats_type,
               count(j.id)::int as job_count,
               max(j.first_seen_at) as latest_job_at
        from sources s left join jobs j on j.source_id = s.id
        where s.active
        group by s.id
        having count(j.id) > 0
        order by count(j.id) desc, s.company_name
        """,
    )
    return {
        "companies": [
            {
                "company_name": row["company_name"],
                "domain": row.get("domain"),
                "ats_type": row["ats_type"],
                "job_count": row["job_count"],
                "latest_job_at": row["latest_job_at"].isoformat()
                if row["latest_job_at"]
                else None,
            }
            for row in rows
        ]
    }
