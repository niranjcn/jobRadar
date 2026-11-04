import json
from datetime import UTC, datetime
from typing import Any

import httpx
from supabase import Client

from app.config import DEFAULT_USER_ID
from app.telegram.messages import build_html

RESEND_API_URL = "https://api.resend.com/emails"
TEST_MODE_FROM = "JobQuest <onboarding@resend.dev>"
IN_BATCH = 200


def _fetch_candidate_jobs(
    supabase: Client, candidates: list[tuple[str, str]]
) -> list[dict[str, Any]]:
    """Jobs that are candidates (newly discovered this run), by job id."""
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


def _fetch_companies(supabase: Client, source_ids: list[str]) -> dict[str, str]:
    if not source_ids:
        return {}
    companies: dict[str, str] = {}
    for start in range(0, len(source_ids), IN_BATCH):
        batch = source_ids[start : start + IN_BATCH]
        response = supabase.table("sources").select("id, company_name").in_("id", batch).execute()
        companies.update({src["id"]: src["company_name"] for src in response.data or []})
    return companies


def _fetch_sent_job_ids(supabase: Client, job_ids: list[str]) -> set[str]:
    if not job_ids:
        return set()
    sent: set[str] = set()
    for start in range(0, len(job_ids), IN_BATCH):
        batch = job_ids[start : start + IN_BATCH]
        response = (
            supabase.table("notifications_sent")
            .select("job_id")
            .eq("user_id", DEFAULT_USER_ID)
            .eq("channel", "email")
            .in_("job_id", batch)
            .execute()
        )
        sent.update(row["job_id"] for row in response.data or [])
    return sent


def _fetch_matched(supabase: Client, job_ids: list[str]) -> dict[str, list[str]]:
    if not job_ids:
        return {}
    matched_by_id: dict[str, list[str]] = {}
    for start in range(0, len(job_ids), IN_BATCH):
        batch = job_ids[start : start + IN_BATCH]
        response = (
            supabase.table("job_matches")
            .select("job_id, matched_on")
            .eq("user_id", DEFAULT_USER_ID)
            .in_("job_id", batch)
            .execute()
        )
        matched_by_id.update(
            {row["job_id"]: row.get("matched_on") or [] for row in response.data or []}
        )
    return matched_by_id


def _send_email(
    api_key: str,
    to_addresses: list[str],
    subject: str,
    html: str,
    idempotency_key: str | None = None,
    extra_headers: dict[str, str] | None = None,
) -> None:
    """Send via Resend. idempotency_key (when given) makes crash-retries safe:
    Resend dedups redeliveries of the same logical send server-side.

    extra_headers sets recipient-visible headers such as List-Unsubscribe
    (CAN-SPAM: every marketing email must offer a working opt-out).
    """
    with httpx.Client(timeout=30.0) as client:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        payload: dict[str, Any] = {
            "from": TEST_MODE_FROM,
            "to": to_addresses,
            "subject": subject,
            "html": html,
        }
        if extra_headers:
            payload["headers"] = extra_headers
        response = client.post(
            RESEND_API_URL,
            headers=headers,
            content=json.dumps(payload),
        )
        if response.status_code >= 400:
            raise RuntimeError(f"resend API {response.status_code}: {response.text[:200]}")


def _mark_sent(supabase: Client, user_id: str, job_ids: list[str]) -> None:
    if not job_ids:
        return
    sent_at = datetime.now(UTC).isoformat()
    supabase.table("notifications_sent").upsert(
        [
            {"user_id": user_id, "job_id": job_id, "channel": "email", "sent_at": sent_at}
            for job_id in job_ids
        ],
        on_conflict="user_id,job_id,channel",
    ).execute()


def send_email_notifications(
    supabase: Client,
    *,
    enabled: bool,
    api_key: str,
    to_addresses: list[str],
    candidates: list[tuple[str, str]],
    scope: str = "matched",
    jobs: list[dict[str, Any]] | None = None,
    app_base_url: str = "",
    postal_address: str = "",
) -> tuple[int, int]:
    if not enabled:
        return 0, 0

    if jobs is None:
        jobs = _fetch_candidate_jobs(supabase, candidates)
    companies = _fetch_companies(supabase, list({job["source_id"] for job in jobs}))

    job_ids = [job["id"] for job in jobs]
    matched_by_id = _fetch_matched(supabase, job_ids)

    if scope == "matched":
        pending = [job for job in jobs if job["id"] in matched_by_id]
    else:
        pending = jobs

    pending_ids = [job["id"] for job in pending]
    already_sent = _fetch_sent_job_ids(supabase, pending_ids)
    pending = [job for job in pending if job["id"] not in already_sent]

    new_matches = [
        {
            "job_id": job["id"],
            "title": job.get("title") or "",
            "company": companies.get(job.get("source_id"), ""),
            "location": job.get("location") or "",
            "url": job.get("url") or "",
            "matched_on": matched_by_id.get(job["id"], []),
        }
        for job in pending
    ]

    # Only send email when there is at least one new matched job.
    if not new_matches:
        return 0, 0

    # CAN-SPAM: working unsubscribe mechanism + physical postal address on
    # every send. The manage URL lands on preferences (one click to disable
    # email alerts via the notify_email toggle); the same URL feeds the
    # List-Unsubscribe header so inboxes render a native unsubscribe button.
    manage_url = f"{app_base_url}/preferences" if app_base_url else ""
    list_unsub = f"<{manage_url}>" if manage_url else ""
    _send_email(
        api_key=api_key,
        to_addresses=to_addresses,
        subject=(
            f"📡 JobQuest: {len(jobs)} new job(s), "
            f"{len(new_matches)} new matching job(s) — {datetime.now(UTC):%b %d}"
        ),
        html=build_html(
            new_matches,
            new_jobs=len(jobs),
            new_matches=len(new_matches),
            unsubscribe_url=manage_url or None,
            postal_address=postal_address or None,
        ),
        extra_headers={"List-Unsubscribe": list_unsub} if list_unsub else None,
    )
    sent = [match["job_id"] for match in new_matches]
    _mark_sent(supabase, DEFAULT_USER_ID, sent)
    return len(sent), len(new_matches)
