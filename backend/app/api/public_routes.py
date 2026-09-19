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
from app.geo import country_stored_variants
from app.public_filters import (
    TEXT_SQL,
    csv_ilike_condition,
    escape_like,
    keyword_group_condition,
    salary_condition,
    split_csv,
)

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
            "where j.is_active order by s.company_name",
        )
    ]
    countries = [
        row["country"]
        for row in query(
            settings,
            "select distinct unnest(countries) as country from jobs "
            "where is_active and countries is not null order by 1",
        )
    ]
    ats_types = [
        row["ats_type"]
        for row in query(
            settings,
            "select distinct s.ats_type from sources s join jobs j on j.source_id = s.id "
            "where j.is_active order by s.ats_type",
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
    loc: str = "",
    locs: str = "",
    companies: str = "",
    sources: str = "",
    countries: str = "",
    types: str = "",
    exp: str = "",
    skills: str = "",
    cats: str = "",
    min_salary: str = "",
    max_salary: str = "",
    sort: str = "newest",
    limit: int = 50,
    offset: int = 0,
) -> dict:
    """Public job listing with every available filter. No auth required.

    q is a multi-keyword search: comma-separated terms, any term matching
    the company name or the combined title + location + description text
    includes the job (OR/union semantics). loc/locs narrow to location
    substring(s); company/companies to company name(s); sources to ATS
    type(s); country/countries to country code(s). types/exp/skills/cats
    match keyword groups against the posting text (heuristic — see
    app.public_filters). min/max_salary bound the first LPA mention in the
    posting text. sort is 'newest' (default) or 'oldest'. mode narrows by
    work mode: remote (flagged remote), hybrid (mentions hybrid in
    title/location — heuristic, sources expose no hybrid flag), onsite
    (everything else).
    """
    settings = _settings()
    limit = max(1, min(limit, MAX_LIMIT))
    offset = max(0, offset)
    sort = (sort or "newest").strip().lower()
    if sort not in ("newest", "oldest"):
        sort = "newest"
    order_dir = "desc" if sort == "newest" else "asc"

    company_names = split_csv(f"{company},{companies}")
    locations = split_csv(f"{loc},{locs}")
    ats_names = split_csv(f"{ats},{sources}")
    # Stored country values mix ISO codes ("IN") and full names ("India"),
    # so the filter matches every spelling of each selected country.
    country_codes = country_stored_variants(split_csv(f"{country},{countries}"))

    # Public catalog shows open postings only (detail endpoint stays unfiltered).
    where: list[str] = ["j.is_active"]
    params: list[Any] = []
    if company_names:
        cond, cond_params = csv_ilike_condition("s.company_name", company_names)
        where.append(cond)
        params += cond_params
    if ats_names:
        where.append("(" + " or ".join("s.ats_type = %s" for _ in ats_names) + ")")
        params += ats_names
    # Multi-keyword search (union): a job matches when ANY term hits the
    # company name or the posting text. Terms are LIKE-escaped so a typed %
    # or _ matches literally instead of acting as a wildcard.
    terms = [t.strip() for t in q.split(",") if t.strip()]
    if terms:
        groups: list[str] = []
        for term in terms:
            term_like = "%" + escape_like(term) + "%"
            groups.append(
                f"(lower(s.company_name) ilike lower(%s) or lower({TEXT_SQL}) ilike lower(%s))"
            )
            params += [term_like, term_like]
        where.append("(" + " or ".join(groups) + ")")
    if country_codes:
        where.append("(" + " or ".join("%s = any(j.countries)" for _ in country_codes) + ")")
        params += country_codes
    if since:
        where.append("j.first_seen_at >= %s::timestamptz")
        params.append(since)
    if remote_only:
        where.append("j.is_remote = true")
    if locations:
        cond, cond_params = csv_ilike_condition("j.location", locations)
        where.append(cond)
        params += cond_params
    for group, selected in (
        ("types", split_csv(types)),
        ("exp", split_csv(exp)),
        ("cats", split_csv(cats)),
    ):
        cond, cond_params = keyword_group_condition(group, selected)
        if cond:
            where.append(cond)
            params += cond_params
    skill_names = split_csv(skills)
    if skill_names:
        cond, cond_params = csv_ilike_condition(TEXT_SQL, skill_names)
        where.append(cond)
        params += cond_params
    cond, cond_params = salary_condition(min_salary, max_salary)
    if cond:
        where.append(cond)
        params += cond_params
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
    from_clause = "from jobs j join sources s on s.id = j.source_id"
    where_sql = " and ".join(where) if where else "true"
    sql = (
        "select j.id, j.source_id, j.external_job_id, j.title, j.location, j.url,"
        " j.first_seen_at, j.countries, j.is_remote,"
        " s.company_name, s.ats_type, s.domain "
        f"{from_clause} where {where_sql}"
        f"{mode_cond} order by j.first_seen_at {order_dir} limit %s offset %s"
    )
    rows = query(settings, sql, (*params, limit, offset))

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

    # Same WHERE as the listing — one builder, no divergence possible.
    total_sql = f"select count(*)::int as c {from_clause} where {where_sql}" + mode_cond
    total = query(settings, total_sql, params)[0]["c"]

    return {"jobs": jobs, "total": total, "limit": limit, "offset": offset}


@router.get("/jobs/{job_id}")
def public_get_job(job_id: str) -> dict:
    """Public single-job detail. No auth required."""
    settings = _settings()
    rows = query(
        settings,
        """
        select j.id, j.source_id, j.external_job_id, j.title, j.location, j.url,
               j.description, j.first_seen_at, j.countries, j.is_remote, j.is_active,
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
        "is_active": row["is_active"],
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
               count(j.id) filter (where j.is_active)::int as job_count,
               max(j.first_seen_at) filter (where j.is_active) as latest_job_at
         from sources s left join jobs j on j.source_id = s.id
         where s.active
         group by s.id
         having count(j.id) filter (where j.is_active) > 0
         order by count(j.id) filter (where j.is_active) desc, s.company_name
         """,
    )
    return {
        "companies": [
            {
                "company_name": row["company_name"],
                "domain": row.get("domain"),
                "ats_type": row["ats_type"],
                "job_count": row["job_count"],
                "latest_job_at": row["latest_job_at"].isoformat() if row["latest_job_at"] else None,
            }
            for row in rows
        ]
    }


@router.get("/schema")
def public_schema() -> dict:
    """Public DB schema for the standalone visual page — no auth, never fails."""
    from datetime import UTC, datetime

    try:
        from app.api.admin_routes import admin_schema as _admin_schema

        # Reuse admin logic but bypass admin check — same live data
        return _admin_schema()
    except Exception as exc:
        # Fallback minimal shape so page never shows "Failed to fetch"
        return {
            "generated_at": datetime.now(UTC).isoformat(),
            "tables": [],
            "issues": [
                {
                    "level": "info",
                    "table": "_",
                    "title": "Schema fetch fallback",
                    "detail": str(exc)[:300],
                }
            ],
            "counts": {"tables": 0, "total_bytes": 0},
        }
