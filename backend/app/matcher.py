import json
from datetime import UTC, datetime
from typing import Any

from supabase import Client

from app.config import DEFAULT_USER_ID
from app.db import get_pool
from app.geo import country_stored_variants, location_matches_preference, map_location
from app.settings_store import load_location_mapping

REMOTE_PREF_WORDS = ("remote", "work from home", "wfh", "anywhere", "worldwide", "global")

IN_BATCH = 200


def fetch_sources(supabase: Client) -> list[dict[str, Any]]:
    response = supabase.table("sources").select("*").eq("active", True).execute()
    return response.data


def _needles(match_in: str, needles: list[str]) -> list[str]:
    lowered = match_in.lower()
    return [n for n in needles if n.lower() in lowered]


def job_matches_preferences(
    job: dict[str, Any], preferences: dict[str, Any], geo_settings: dict[str, Any] | None = None
) -> tuple[bool, list[str]]:
    title = (job.get("title") or "").lower()
    description = (job.get("description") or "").lower()
    location = (job.get("location") or "").lower()
    company = job.get("company_name") or ""

    job_countries = country_stored_variants([c for c in (job.get("countries") or []) if c])
    job_is_remote = bool(job.get("is_remote"))

    roles = preferences.get("roles") or []
    keywords = preferences.get("keywords") or []
    locations = preferences.get("locations") or []
    seniority = preferences.get("seniority") or []
    excluded = preferences.get("excluded_companies") or []
    excluded_roles = preferences.get("excluded_roles") or []

    if company.lower() in [e.lower() for e in excluded]:
        return False, []

    if any(er.lower() in title for er in excluded_roles):
        return False, []

    reasons: list[str] = []

    roles_hit = _needles(title, roles)
    keywords_hit = _needles(f"{title} {description}", keywords)
    if roles_hit:
        reasons.append("role:" + ",".join(roles_hit))
    if keywords_hit:
        reasons.append("keyword:" + ",".join(keywords_hit))

    seniority_hit = [s for s in seniority if s.lower() in title or s.lower() == "any"]
    if seniority_hit:
        reasons.append("seniority:" + ",".join(seniority_hit))

    # Location is a hard filter: when any location preference is set, the job
    # must actually match it (raw text or mapped country/remote fallback).
    if locations:
        locations_hit = [
            loc
            for loc in locations
            if loc.lower() in location or (loc.lower() == "remote" and "remote" in location)
        ]
        # country-aware: also accept a job whose mapped countries cover a
        # preference that resolves to a country (India, Dubai -> AE, BLR -> IN).
        if job_countries:
            locations_hit = list(locations_hit) or [
                loc
                for loc in locations
                if location_matches_preference(job_countries, job_is_remote, loc, geo_settings)
            ]
        if not locations_hit:
            return False, []
        reasons.append("location:" + ",".join(locations_hit))

    # Content is OR: the job must hit at least one role / keyword / seniority
    # term when any of those categories are configured.
    content_configured = bool(roles or keywords or seniority)
    content_hit = bool(roles_hit or keywords_hit or seniority_hit)
    if content_configured and not content_hit:
        return False, []
    return True, reasons


def compute_match_score(
    job: dict[str, Any], preferences: dict[str, Any], geo_settings: dict[str, Any] | None = None
) -> int:
    """Deterministic 0-100 score: share of active preference categories hit."""
    title = (job.get("title") or "").lower()
    description = (job.get("description") or "").lower()
    location = (job.get("location") or "").lower()

    job_countries = country_stored_variants([c for c in (job.get("countries") or []) if c])
    job_is_remote = bool(job.get("is_remote"))

    categories = 0
    hits = 0

    roles = preferences.get("roles") or []
    keywords = preferences.get("keywords") or []
    locations = preferences.get("locations") or []
    seniority = preferences.get("seniority") or []

    if roles:
        categories += 1
        if _needles(title, roles):
            hits += 1

    if keywords:
        categories += 1
        if _needles(f"{title} {description}", keywords):
            hits += 1

    if locations:
        categories += 1
        if any(
            loc.lower() in location or (loc.lower() == "remote" and "remote" in location)
            for loc in locations
        ) or (
            job_countries
            and any(
                location_matches_preference(job_countries, job_is_remote, loc, geo_settings)
                for loc in locations
            )
        ):
            hits += 1

    if seniority:
        categories += 1
        if _needles(title, seniority):
            hits += 1

    if categories == 0:
        return 100
    return round((hits / categories) * 100)


def sync_preferences(
    supabase: Client, preferences: dict[str, Any], user_id: str = DEFAULT_USER_ID
) -> None:
    """Seed env preferences into the DB, but only if no row exists yet.

    Once a preferences row is saved (via the API/UI), it becomes the single
    source of truth — later polls must NOT overwrite user edits with env
    defaults.
    """
    existing = supabase.table("preferences").select("user_id").eq("user_id", user_id).execute()
    if existing.data:
        return
    fields = {
        "keywords": preferences.get("keywords", []),
        "roles": preferences.get("roles", []),
        "locations": preferences.get("locations", []),
        "seniority": preferences.get("seniority", []),
        "excluded_companies": preferences.get("excluded_companies", []),
        "excluded_roles": preferences.get("excluded_roles", []),
    }
    if not any(fields.values()):
        return
    supabase.table("preferences").upsert(
        [
            {
                "user_id": user_id,
                **fields,
                "updated_at": datetime.now(UTC).isoformat(),
            }
        ],
        on_conflict="user_id",
    ).execute()


def load_preferences(supabase: Client, user_id: str = DEFAULT_USER_ID) -> dict[str, Any]:
    response = supabase.table("preferences").select("*").eq("user_id", user_id).execute()
    if not response.data:
        return {}
    row = response.data[0]
    return {
        "roles": row.get("roles") or [],
        "keywords": row.get("keywords") or [],
        "locations": row.get("locations") or [],
        "seniority": row.get("seniority") or [],
        "excluded_companies": row.get("excluded_companies") or [],
        "excluded_roles": row.get("excluded_roles") or [],
        "notify_telegram": row.get("notify_telegram", True),
        "notify_email": row.get("notify_email", True),
        "alert_frequency": row.get("alert_frequency", "immediate"),
        "telegram_scope": row.get("telegram_scope", "matched"),
        "email_scope": row.get("email_scope", "matched"),
        "notify_first_check": row.get("notify_first_check", True),
    }


def load_notification_settings(supabase: Client, user_id: str = DEFAULT_USER_ID) -> dict[str, Any]:
    prefs = load_preferences(supabase, user_id)
    return {
        "notify_telegram": prefs.get("notify_telegram", True),
        "notify_email": prefs.get("notify_email", True),
        "alert_frequency": prefs.get("alert_frequency", "immediate"),
        "telegram_scope": prefs.get("telegram_scope", "matched"),
        "email_scope": prefs.get("email_scope", "matched"),
        "notify_first_check": prefs.get("notify_first_check", True),
    }


def match_all(
    supabase: Client,
    candidates: list[tuple[str, str]] | None = None,
    user_id: str = DEFAULT_USER_ID,
) -> dict[str, Any]:
    preferences = load_preferences(supabase, user_id)
    if not preferences:
        return {"result": "no preferences row yet", "matched": 0}

    if not candidates:
        return {"result": "no new jobs since last poll", "considered": 0, "matched": 0}

    sources = fetch_sources(supabase)
    company_by_source_id = {source["id"]: source["company_name"] for source in sources}
    if not company_by_source_id:
        return {"result": "no active sources", "matched": 0}

    by_source: dict[str, list[str]] = {}
    for source_id, external_job_id in candidates:
        by_source.setdefault(source_id, []).append(external_job_id)

    jobs: list[dict[str, Any]] = []
    for source_id, external_ids in by_source.items():
        for start in range(0, len(external_ids), IN_BATCH):
            batch = external_ids[start : start + IN_BATCH]
            response = (
                supabase.table("jobs")
                .select("id, source_id, title, location, description, countries, is_remote")
                .eq("source_id", source_id)
                .in_("external_job_id", batch)
                .execute()
            )
            jobs.extend(response.data or [])

    geo_settings = load_location_mapping(supabase)
    rows: list[dict[str, Any]] = []
    matched = 0
    for job in jobs:
        job["company_name"] = company_by_source_id.get(job.get("source_id"), "")
        is_match, reasons = job_matches_preferences(job, preferences, geo_settings)
        if is_match:
            matched += 1
            rows.append(
                {
                    "user_id": user_id,
                    "job_id": job["id"],
                    "matched_on": reasons,
                    "match_score": compute_match_score(job, preferences, geo_settings),
                }
            )

    if rows:
        supabase.table("job_matches").upsert(rows, on_conflict="user_id,job_id").execute()

    return {"result": "ok", "considered": len(jobs), "matched": matched}


def recompute_matches(
    supabase: Client,
    settings: Any | None = None,
    user_id: str = DEFAULT_USER_ID,
) -> dict[str, Any]:
    """Rebuild job_matches from scratch for the CURRENT preferences.

    The match itself runs inside Postgres (recompute_job_matches) because a
    full re-match over every stored job cannot be done in Python: reading ~50k
    job rows over the slow pooler link costs ~7ms per row (minutes total).
    Location preferences are pre-resolved to country codes here via geo.py and
    passed in as JSON, so the SQL stays a faithful mirror of
    job_matches_preferences / compute_match_score.

    Call this after saving preferences so the /matches page reflects the new
    filters immediately instead of only applying to jobs scraped later.
    """
    from app.config import load_settings

    settings = settings or load_settings()
    preferences = load_preferences(supabase, user_id)
    if not preferences:
        return {"result": "no preferences row yet", "matched": 0}

    geo = load_location_mapping(supabase)
    locations = preferences.get("locations") or []
    pref_locations = []
    for loc in locations:
        p = loc.strip().lower()
        if p in REMOTE_PREF_WORDS:
            pref_locations.append({"raw": loc, "remote": True, "codes": []})
        else:
            mapped = map_location(loc, geo)
            pref_locations.append(
                {"raw": loc, "remote": False, "codes": mapped.get("countries") or []}
            )

    with get_pool(settings).connection(timeout=60) as conn, conn.cursor() as cur:
        cur.execute(
            "select recompute_job_matches(%s, %s, %s, %s::jsonb, %s, %s, %s)",
            (
                user_id,
                preferences.get("roles") or [],
                preferences.get("keywords") or [],
                json.dumps(pref_locations),
                preferences.get("seniority") or [],
                preferences.get("excluded_companies") or [],
                preferences.get("excluded_roles") or [],
            ),
        )
        result = cur.fetchone()[0]

    return {
        "result": result.get("result"),
        "considered": result.get("considered"),
        "matched": result.get("matched"),
    }
