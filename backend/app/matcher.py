import json
import re
from datetime import UTC, datetime
from functools import lru_cache
from typing import Any

from supabase import Client

from app.config import DEFAULT_USER_ID
from app.db import get_pool
from app.geo import country_stored_variants, location_matches_preference, map_location
from app.settings_store import load_location_mapping

REMOTE_PREF_WORDS = ("remote", "work from home", "wfh", "anywhere", "worldwide", "global")

IN_BATCH = 200


@lru_cache(maxsize=1024)
def _term_pattern(term_low: str) -> re.Pattern[str] | None:
    """Compiled whole-word pattern for a lowercased preference term.

    None for empty terms (they must never match). Cached because each poll
    evaluates thousands of titles against the same few terms.
    """
    if not term_low:
        return None
    return re.compile(r"(?<![a-z0-9])" + re.escape(term_low) + r"(?![a-z0-9])")


def term_matches_text(term_low: str, text_low: str) -> bool:
    """Whole-word/phrase hit: 'ai' matches 'AI Engineer' and 'AI/ML', but
    not 'retailer', 'training', or 'fair'. Multi-word terms ('machine
    learning') match as a phrase; symbols ('c++', '.net') match on
    non-alphanumeric boundaries."""
    pattern = _term_pattern(term_low)
    return pattern is not None and pattern.search(text_low) is not None


def fetch_sources(supabase: Client) -> list[dict[str, Any]]:
    # 60: explicit columns for determinism
    response = supabase.table("sources").select("id, company_name").eq("active", True).execute()
    return response.data


_MATCH_KEYS = (
    "roles",
    "keywords",
    "locations",
    "seniority",
    "excluded_companies",
    "excluded_roles",
)


def preference_signature(preferences: dict[str, Any]) -> tuple:
    """Hashable evaluation-identity for a preference set.

    Exact raw lists (order- and duplicate-sensitive): matched_on reasons embed
    the user's own strings in list order, so only byte-identical preference
    lists may share one evaluation. None and [] are equivalent (every access
    goes through `or []`).
    """
    return tuple(tuple(preferences.get(key) or []) for key in _MATCH_KEYS)


def normalize_job_for_matching(job: dict[str, Any]) -> dict[str, Any]:
    """Job-side one-time view for matching.

    Lowercased text plus resolved countries, computed once per job per run
    instead of once per (job, user). Pure derivation — the same values the
    per-pair path recomputed every time.
    """
    title = job.get("title") or ""
    title_l = title.lower()
    company = job.get("company_name") or ""
    return {
        "id": job.get("id"),
        "title_l": title_l,
        # Keyword matching is title-only by product decision (descriptions are
        # not stored); legacy dicts carrying a description key behave the same.
        "text_l": title_l,
        "location_l": (job.get("location") or "").lower(),
        "company": company,
        "company_l": company.lower(),
        "countries": country_stored_variants([c for c in (job.get("countries") or []) if c]),
        "is_remote": bool(job.get("is_remote")),
    }


def lowered_term_lists(preferences: dict[str, Any]) -> dict[str, list[str]]:
    """Lowercased copies of the six matching lists, computed once per user-group
    per run. Reasons still use the original strings (see _match_core)."""
    return {key: [term.lower() for term in (preferences.get(key) or [])] for key in _MATCH_KEYS}


def _score_from_hits(
    roles: list,
    roles_hit: list,
    keywords: list,
    keywords_hit: list,
    locations: list,
    locations_hit: list,
    seniority: list,
    seniority_hit: list,
) -> int:
    """Deterministic 0-100 score: share of active preference categories hit."""
    categories = 0
    hits = 0
    if roles:
        categories += 1
        if roles_hit:
            hits += 1
    if keywords:
        categories += 1
        if keywords_hit:
            hits += 1
    if locations:
        categories += 1
        if locations_hit:
            hits += 1
    if seniority:
        categories += 1
        if seniority_hit:
            hits += 1
    if categories == 0:
        return 100
    return round((hits / categories) * 100)


def _match_core(
    norm: dict[str, Any],
    preferences: dict[str, Any],
    lowered: dict[str, list[str]],
    geo_settings: dict[str, Any] | None,
) -> tuple[bool, list[str], int]:
    """Shared heart of matching and scoring over normalized inputs.

    Returns (is_match, reasons, score). Reasons assemble in canonical
    role/keyword/seniority/location order with the user's original strings —
    byte-identical to the legacy per-pair path regardless of evaluation order.
    The location hard filter runs before the content scans (same outcome, skips
    expensive scans on mismatches); the score ignores exclusions, also as before.
    """
    roles = preferences.get("roles") or []
    keywords = preferences.get("keywords") or []
    locations = preferences.get("locations") or []
    seniority = preferences.get("seniority") or []

    if norm["company_l"] in lowered["excluded_companies"]:
        excluded_hit = True
    else:
        excluded_hit = any(
            term_matches_text(term, norm["title_l"]) for term in lowered["excluded_roles"]
        )

    roles_hit = [
        orig
        for orig, low in zip(roles, lowered["roles"])
        if term_matches_text(low, norm["title_l"])
    ]
    keywords_hit = [
        orig
        for orig, low in zip(keywords, lowered["keywords"])
        if term_matches_text(low, norm["text_l"])
    ]
    seniority_hit = [
        orig
        for orig, low in zip(seniority, lowered["seniority"])
        if term_matches_text(low, norm["title_l"]) or low == "any"
    ]

    # Location is a hard filter: when any location preference is set, the job
    # must actually match it (raw text or mapped country/remote fallback).
    locations_hit: list[str] = []
    if locations:
        locations_hit = [
            orig
            for orig, low in zip(locations, lowered["locations"])
            if term_matches_text(low, norm["location_l"])
            or (low == "remote" and term_matches_text("remote", norm["location_l"]))
        ]
        # country-aware: also accept a job whose mapped countries cover a
        # preference that resolves to a country (India, Dubai -> AE, BLR -> IN).
        if norm["countries"]:
            locations_hit = list(locations_hit) or [
                loc
                for loc in locations
                if location_matches_preference(
                    norm["countries"], norm["is_remote"], loc, geo_settings
                )
            ]

    score = _score_from_hits(
        roles,
        roles_hit,
        keywords,
        keywords_hit,
        locations,
        locations_hit,
        seniority,
        seniority_hit,
    )

    if excluded_hit:
        return False, [], score

    reasons: list[str] = []
    if roles_hit:
        reasons.append("role:" + ",".join(roles_hit))
    if keywords_hit:
        reasons.append("keyword:" + ",".join(keywords_hit))
    if seniority_hit:
        reasons.append("seniority:" + ",".join(seniority_hit))

    if locations:
        if not locations_hit:
            return False, [], score
        reasons.append("location:" + ",".join(locations_hit))

    # Content is OR: the job must hit at least one role / keyword / seniority
    # term when any of those categories are configured.
    content_configured = bool(roles or keywords or seniority)
    content_hit = bool(roles_hit or keywords_hit or seniority_hit)
    if content_configured and not content_hit:
        return False, [], score
    return True, reasons, score


def evaluate_normalized_jobs(
    norm_jobs: list[dict[str, Any]],
    preferences: dict[str, Any],
    lowered: dict[str, list[str]],
    geo_settings: dict[str, Any] | None,
) -> tuple[list[dict[str, Any]], set[str]]:
    """Evaluate pre-normalized jobs for one preference set.

    Returns (templates, matched_ids): templates carry matched_on + match_score
    without user_id so one evaluation fans out to every group member.
    """
    templates: list[dict[str, Any]] = []
    matched: set[str] = set()
    for norm in norm_jobs:
        is_match, reasons, score = _match_core(norm, preferences, lowered, geo_settings)
        if not is_match:
            continue
        matched.add(norm["id"])
        templates.append({"job_id": norm["id"], "matched_on": reasons, "match_score": score})
    return templates, matched


def job_matches_preferences(
    job: dict[str, Any], preferences: dict[str, Any], geo_settings: dict[str, Any] | None = None
) -> tuple[bool, list[str]]:
    norm = normalize_job_for_matching(job)
    is_match, reasons, _ = _match_core(
        norm, preferences, lowered_term_lists(preferences), geo_settings
    )
    return is_match, reasons


def compute_match_score(
    job: dict[str, Any], preferences: dict[str, Any], geo_settings: dict[str, Any] | None = None
) -> int:
    """Deterministic 0-100 score: share of active preference categories hit."""
    norm = normalize_job_for_matching(job)
    _, _, score = _match_core(norm, preferences, lowered_term_lists(preferences), geo_settings)
    return score


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
    response = (
        supabase.table("preferences")
        .select(
            "roles, keywords, locations, seniority, excluded_companies, excluded_roles, notify_telegram, notify_email, alert_frequency, telegram_scope, email_scope, notify_first_check"
        )
        .eq("user_id", user_id)
        .execute()
    )
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
                .select("id, source_id, title, location, countries, is_remote")
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
