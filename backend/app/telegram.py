import asyncio
import json
from datetime import datetime, timezone
from typing import Any

import httpx
from supabase import Client

from app.config import DEFAULT_USER_ID
from app.messages import build_text_sections, build_text_summary

TELEGRAM_API = "https://api.telegram.org/bot"
MAX_MESSAGE_LENGTH = 4000
IN_BATCH = 200
GET_UPDATES_TIMEOUT = 30

START_MESSAGE = (
    "👋 Welcome to jobRadar!\n\n"
    "I keep an eye on company career pages — across 10 different "
    "applicant-tracking systems — and ping you the moment a new role appears.\n\n"
    "🔍 What I do:\n"
    "• Monitor 100+ companies' job boards\n"
    "• Filter postings against your preferences (role, location, skills)\n"
    "• Deduplicate results, so each job only reaches you once\n\n"
    "📬 What you'll get:\n"
    "• 🚨 New job alerts as they're posted\n"
    "• 🎯 Preference matches, called out separately\n"
    "• 📍 Location and a direct Apply link in every alert\n\n"
    "No repeats, no spam — just new roles that fit.\n\n"
    "Adjust your preferences anytime in the dashboard and I'll adapt.\n\n"
    "First alerts are on the way. 📡"
)


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


def _fetch_sent_job_ids(supabase: Client) -> set[str]:
    response = (
        supabase.table("notifications_sent")
        .select("job_id")
        .eq("user_id", DEFAULT_USER_ID)
        .eq("channel", "telegram")
        .execute()
    )
    return {row["job_id"] for row in response.data or []}


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


def _get_updates(bot_token: str, offset: int | None) -> httpx.Response:
    payload: dict[str, Any] = {
        "timeout": GET_UPDATES_TIMEOUT,
        "allowed_updates": ["message"],
    }
    if offset is not None:
        payload["offset"] = offset
    return _post(bot_token, "getUpdates", payload)


def handle_start_commands(bot_token: str, updates: list[dict[str, Any]]) -> int:
    """Reply with the welcome message to every /start message in a batch.

    Returns the number of chats greeted. Non-/start messages are ignored.
    """
    greeted = 0
    for update in updates:
        message = update.get("message") or {}
        text = message.get("text") or ""
        if not text.startswith("/start"):
            continue
        chat_id = (message.get("chat") or {}).get("id")
        if chat_id is None:
            continue
        _send_message(bot_token, str(chat_id), START_MESSAGE)
        greeted += 1
    return greeted


async def telegram_command_loop(*, bot_token: str) -> None:
    """Long-poll Telegram for /start commands and reply with the welcome message.

    Runs for the lifetime of the process while Telegram is enabled. Uses
    ``getUpdates`` long polling (no webhook), so it works behind docker-compose
    and Render without a public tunnel. If a webhook is ever configured on the
    bot, ``getUpdates`` fails with HTTP 409 and this loop stops with a clear log.
    """
    offset: int | None = None
    while True:
        try:
            response = await asyncio.to_thread(_get_updates, bot_token, offset)
            if response.status_code == 409:
                print(
                    "telegram: /start loop stopped — bot has a webhook configured "
                    "(getUpdates HTTP 409)"
                )
                return
            if response.status_code >= 400:
                print(f"telegram: getUpdates failed {response.status_code}: {response.text[:200]}")
                await asyncio.sleep(60)
                continue
            updates = response.json().get("result") or []
            if updates:
                offset = updates[-1]["update_id"] + 1
                greeted = await asyncio.to_thread(handle_start_commands, bot_token, updates)
                if greeted:
                    print(f"telegram: welcomed {greeted} chat(s)")
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            print(f"telegram: /start poll error — {exc}")
            await asyncio.sleep(60)


def _mark_sent(supabase: Client, user_id: str, job_ids: list[str]) -> None:
    if not job_ids:
        return
    sent_at = datetime.now(timezone.utc).isoformat()
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
) -> tuple[int, int]:
    if not enabled:
        return 0, 0

    jobs = _fetch_new_jobs(supabase, candidates)

    companies = _fetch_companies(supabase, list({job["source_id"] for job in jobs}))

    if scope == "matched":
        matched_response = (
            supabase.table("job_matches")
            .select("job_id")
            .eq("user_id", DEFAULT_USER_ID)
            .execute()
        )
        matched_ids = {row["job_id"] for row in matched_response.data or []}
        job_ids = [job["id"] for job in jobs if job["id"] in matched_ids]
    else:
        job_ids = [job["id"] for job in jobs]

    already_sent = _fetch_sent_job_ids(supabase)
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
