import json
from datetime import UTC, datetime
from typing import Any

import httpx
from supabase import Client

from app.config import DEFAULT_USER_ID
from app.telegram.messages import build_text_sections, build_text_summary

TELEGRAM_API = "https://api.telegram.org/bot"
MAX_MESSAGE_LENGTH = 4000
IN_BATCH = 200


def _fetch_new_jobs(supabase: Client, candidates: list[tuple[str, str]]) -> list[dict[str, Any]]:
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
    response = supabase.table("sources").select("id, company_name").in_("id", source_ids).execute()
    return {src["id"]: src["company_name"] for src in response.data or []}


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
            .eq("channel", "telegram")
            .in_("job_id", batch)
            .execute()
        )
        sent.update(row["job_id"] for row in response.data or [])
    return sent


def _fetch_matched_job_ids(supabase: Client, job_ids: list[str]) -> set[str]:
    if not job_ids:
        return set()
    matched: set[str] = set()
    for start in range(0, len(job_ids), IN_BATCH):
        batch = job_ids[start : start + IN_BATCH]
        response = (
            supabase.table("job_matches")
            .select("job_id")
            .eq("user_id", DEFAULT_USER_ID)
            .in_("job_id", batch)
            .execute()
        )
        matched.update(row["job_id"] for row in response.data or [])
    return matched


def _chunk_sections(sections: list[str], max_len: int = MAX_MESSAGE_LENGTH) -> list[str]:
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for section in sections:
        section_len = len(section) + 1
        if current and current_len + section_len > max_len:
            chunks.append("\n\n".join(current))
            current = [section]
            current_len = section_len
        else:
            current.append(section)
            current_len += section_len
    if current:
        chunks.append("\n\n".join(current))
    return chunks


def _post(bot_token: str, method: str, payload: dict[str, Any]) -> httpx.Response:
    with httpx.Client(timeout=30.0) as client:
        return client.post(
            f"{TELEGRAM_API}{bot_token}/{method}",
            content=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )


def _send_message(bot_token: str, chat_id: str, text: str) -> None:
    response = _post(bot_token, "sendMessage", {"chat_id": chat_id, "text": text})
    if response.status_code >= 400:
        raise RuntimeError(f"telegram API {response.status_code}: {response.text[:200]}")


def _mark_sent(supabase: Client, user_id: str, job_ids: list[str]) -> None:
    if not job_ids:
        return
    sent_at = datetime.now(UTC).isoformat()
    supabase.table("notifications_sent").upsert(
        [
            {"user_id": user_id, "job_id": job_id, "channel": "telegram", "sent_at": sent_at}
            for job_id in job_ids
        ],
        on_conflict="job_id,channel",
    ).execute()


def send_telegram_notifications(
    supabase: Client,
    *,
    enabled: bool,
    bot_token: str,
    chat_id: str,
    candidates: list[tuple[str, str]],
    scope: str = "all",
    jobs: list[dict[str, Any]] | None = None,
) -> tuple[int, int]:
    if not enabled:
        return 0, 0

    if jobs is None:
        jobs = _fetch_new_jobs(supabase, candidates)

    companies = _fetch_companies(supabase, list({job["source_id"] for job in jobs}))

    job_ids = [job["id"] for job in jobs]
    if scope == "matched":
        matched_ids = _fetch_matched_job_ids(supabase, job_ids)
        job_ids = [job_id for job_id in job_ids if job_id in matched_ids]

    already_sent = _fetch_sent_job_ids(supabase, job_ids)
    pending_ids = [job_id for job_id in job_ids if job_id not in already_sent]
    pending_by_id = {job["id"]: job for job in jobs}
    pending = [pending_by_id[job_id] for job_id in pending_ids if job_id in pending_by_id]

    for job in pending:
        job["company"] = companies.get(job.get("source_id"), "")

    sections = [build_text_summary(len(jobs), len(pending))]
    if pending:
        sections += build_text_sections(pending)[1:]
    chunks = _chunk_sections(sections)

    for chunk in chunks:
        _send_message(bot_token, chat_id, chunk)

    _mark_sent(supabase, DEFAULT_USER_ID, pending_ids)
    return len(pending), len(jobs)
