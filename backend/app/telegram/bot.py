"""Telegram command bot: command menu + long-polling command dispatcher.

Mirrors the dashboard feature surface as bot commands. The bot only responds
to the configured TELEGRAM_CHAT_ID (single-user, like the rest of the system).
It uses getUpdates long polling, so no public URL or webhook is required.
"""

import asyncio
import json
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
from supabase import Client

from app.config import DEFAULT_USER_ID, Settings
from app.db import get_supabase, query
from app.poller import source_status
from app.schedule_store import (
    effective_intervals,
    last_checked_by_ats,
    load_interval_overrides,
    next_run_at,
    source_count_by_ats,
)

TELEGRAM_API = "https://api.telegram.org/bot"
MAX_MESSAGE_LENGTH = 4000
POLL_TIMEOUT = 30

COMMANDS: list[dict[str, str]] = [
    {"command": "start", "description": "Welcome and quick overview"},
    {"command": "help", "description": "List all commands"},
    {"command": "stats", "description": "Dashboard stats"},
    {"command": "jobs", "description": "Recent jobs (optional search term)"},
    {"command": "newjobs", "description": "Jobs found in last 7 days"},
    {"command": "matches", "description": "Your matching jobs"},
    {"command": "newmatches", "description": "New matches in last 7 days"},
    {"command": "companies", "description": "Monitored companies"},
    {"command": "sources", "description": "Source health"},
    {"command": "schedule", "description": "Polling schedule"},
    {"command": "runs", "description": "Recent poll runs"},
    {"command": "notifications", "description": "Recent alerts sent"},
    {"command": "preferences", "description": "Your preferences"},
]

# Inline menu (read-only commands only). Two columns per row keeps the
# keyboard compact on phones. Callback data is "menu:<command>".
MENU_BUTTONS: list[tuple[str, str]] = [
    ("stats", "📊 Stats"),
    ("jobs", "📦 Jobs"),
    ("newjobs", "🆕 New jobs"),
    ("matches", "🎯 Matches"),
    ("newmatches", "✨ New matches"),
    ("companies", "🏢 Companies"),
    ("sources", "🩺 Sources"),
    ("schedule", "🕐 Schedule"),
    ("runs", "▶️ Runs"),
    ("notifications", "🔔 Alerts"),
    ("preferences", "⚙️ Preferences"),
    ("help", "❓ Help"),
]

MENU_COMMANDS = {command for command, _ in MENU_BUTTONS}

STATUS_EMOJI = {"healthy": "\U0001f7e2", "stale": "\U0001f7e1", "never": "\u26aa"}


# ---------- parsing / auth ----------


def parse_command(text: str) -> tuple[str, str]:
    """Return (command, args) from a message like '/jobs python'.

    Handles Telegram's optional '@BotName' suffix on the command.
    """
    if not text or not text.startswith("/"):
        return "", ""
    first, _, rest = text.partition(" ")
    command = first.lstrip("/").lower()
    if "@" in command:
        command = command.split("@")[0]
    return command, rest.strip()


def authorized(chat_id: Any, settings: Settings) -> bool:
    return str(chat_id) == str(settings.telegram_chat_id)


# ---------- API helpers ----------


def _post(token: str, method: str, payload: dict[str, Any]) -> httpx.Response:
    with httpx.Client(timeout=30.0) as client:
        return client.post(
            f"{TELEGRAM_API}{token}/{method}",
            content=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )


async def _post_async(
    client: httpx.AsyncClient, token: str, method: str, payload: dict[str, Any]
) -> httpx.Response:
    return await client.post(
        f"{TELEGRAM_API}{token}/{method}",
        content=json.dumps(payload),
        headers={"Content-Type": "application/json"},
    )


def register_command_menu(token: str) -> bool:
    """Register the bot command menu (setMyCommands). Call once at startup."""
    response = _post(token, "setMyCommands", {"commands": COMMANDS})
    if response.status_code >= 400:
        print(f"telegram setMyCommands failed: {response.status_code} {response.text[:200]}")
        return False
    return True


def _chunk_text(text: str, max_len: int = MAX_MESSAGE_LENGTH) -> list[str]:
    if len(text) <= max_len:
        return [text]
    paragraphs = text.split("\n\n")
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for paragraph in paragraphs:
        size = len(paragraph) + 2
        if current and current_len + size > max_len:
            chunks.append("\n\n".join(current))
            current = [paragraph]
            current_len = len(paragraph)
        else:
            current.append(paragraph)
            current_len += size
    if current:
        chunks.append("\n\n".join(current))
    return chunks


def _menu_markup() -> dict[str, Any]:
    """Inline keyboard for the main menu (read-only command buttons)."""
    pairs = [MENU_BUTTONS[i : i + 2] for i in range(0, len(MENU_BUTTONS), 2)]
    return {
        "inline_keyboard": [
            [{"text": label, "callback_data": f"menu:{command}"} for command, label in row]
            for row in pairs
        ]
    }


async def _send_message(
    client: httpx.AsyncClient,
    token: str,
    chat_id: Any,
    text: str,
    reply_markup: dict[str, Any] | None = None,
) -> None:
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    for chunk in _chunk_text(text):
        response = await _post_async(client, token, "sendMessage", {**payload, "text": chunk})
        if response.status_code >= 400:
            raise RuntimeError(f"telegram API {response.status_code}: {response.text[:200]}")


# ---------- message formatting ----------


def format_job_block(job: dict[str, Any]) -> str:
    lines = [job.get("title") or "Untitled"]
    meta = f"\U0001f3e2 {job.get('company_name') or 'Unknown'}"
    if job.get("location"):
        meta += f" \u00b7 \U0001f4cd {job['location']}"
    if job.get("match_score") is not None:
        meta += f" \u00b7 \U0001f3af {job['match_score']}%"
    lines.append(meta)
    url = job.get("url")
    if url:
        lines.append(f"\U0001f517 {url}")
    return "\n".join(lines)


def _fmt_interval(seconds: int) -> str:
    if seconds % 3600 == 0:
        return f"{seconds // 3600}h"
    return f"{seconds // 60}m"


def _fmt_dt(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M")
    return str(value)[:16].replace("T", " ")


def _build_reply(blocks: list[str]) -> str:
    return "\n\n".join(blocks)


# ---------- queries ----------


def _list_jobs(
    settings: Settings,
    *,
    q: str = "",
    since_days: int | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    since_cond = " and j.first_seen_at >= %s::timestamptz" if since_days else ""
    params: list[Any] = [DEFAULT_USER_ID, q, q, q]
    if since_days:
        params.append((datetime.now(UTC) - timedelta(days=since_days)).isoformat())
    params.append(limit)
    return query(
        settings,
        f"""
        select j.id, j.title, j.location, j.url, j.first_seen_at,
               s.company_name, s.ats_type, m.match_score
        from jobs j
        join sources s on s.id = j.source_id
        left join job_matches m on m.job_id = j.id and m.user_id = %s
        where (%s = '' or (lower(j.title) ilike lower('%%' || %s || '%%')
               or lower(s.company_name) ilike lower('%%' || %s || '%%')))
        {since_cond}
        order by j.first_seen_at desc
        limit %s
        """,
        tuple(params),
    )


def _list_matches(
    settings: Settings,
    *,
    company: str = "",
    since_days: int | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    since_cond = " and m.created_at >= now() - interval '7 days'" if since_days else ""
    params: list[Any] = [DEFAULT_USER_ID, company, company]
    params.append(limit)
    return query(
        settings,
        f"""
        select j.id, j.title, j.location, j.url, j.first_seen_at,
               s.company_name, s.ats_type, m.match_score
        from job_matches m
        join jobs j on j.id = m.job_id
        join sources s on s.id = j.source_id
        where m.user_id = %s
          and (%s = '' or lower(s.company_name) ilike lower('%%' || %s || '%%'))
        {since_cond}
        order by m.match_score desc, j.first_seen_at desc
        limit %s
        """,
        tuple(params),
    )


# ---------- command handlers ----------


def _cmd_start(settings: Settings, supabase: Client, args: str) -> str:
    row = query(
        settings,
        """
        select
          (select count(*)::int from jobs) as jobs_total,
          (select count(*)::int from sources where active) as companies,
          (select count(*)::int from job_matches where user_id = %s) as matches
        """,
        (DEFAULT_USER_ID,),
    )[0]
    return (
        "👋 Welcome to JobRadar!\n\n"
        "I monitor company career pages and alert you about new jobs.\n\n"
        f"📦 {row['jobs_total']} jobs tracked\n"
        f"🏢 {row['companies']} companies monitored\n"
        f"🎯 {row['matches']} matches\n\n"
        "Try /help to see everything I can do."
    )


def _cmd_help(settings: Settings, supabase: Client, args: str) -> str:
    lines = ["🤖 JobRadar commands", ""]
    lines.extend(f"/{c['command']} — {c['description']}" for c in COMMANDS)
    return "\n".join(lines)


def _cmd_stats(settings: Settings, supabase: Client, args: str) -> str:
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
        (since, DEFAULT_USER_ID, DEFAULT_USER_ID),
    )[0]
    return _build_reply(
        [
            "📊 Dashboard stats",
            (
                f"New jobs (7d): {row['jobs_7d']}\n"
                f"Matches: {row['matches']}\n"
                f"Companies monitored: {row['companies']}\n"
                f"Avg match: {row['avg_score']}%\n"
                f"Total jobs: {row['jobs_total']}"
            ),
        ]
    )


def _cmd_jobs(settings: Settings, supabase: Client, args: str) -> str:
    rows = _list_jobs(settings, q=args, limit=10)
    if not rows:
        return "No jobs found." if args else "No jobs tracked yet."
    header = f"📦 {len(rows)} job(s)"
    if args:
        header += f" matching '{args}'"
    return _build_reply([header, *[format_job_block(j) for j in rows]])


def _cmd_newjobs(settings: Settings, supabase: Client, args: str) -> str:
    rows = _list_jobs(settings, since_days=7, limit=10)
    if not rows:
        return "No new jobs in the last 7 days."
    return _build_reply(["📦 New jobs (7d)", *[format_job_block(j) for j in rows]])


def _cmd_matches(settings: Settings, supabase: Client, args: str) -> str:
    rows = _list_matches(settings, company=args, limit=10)
    if not rows:
        return "No matches found." if args else "No matching jobs yet."
    header = f"🎯 {len(rows)} match(es)"
    if args:
        header += f" for '{args}'"
    return _build_reply([header, *[format_job_block(j) for j in rows]])


def _cmd_newmatches(settings: Settings, supabase: Client, args: str) -> str:
    rows = _list_matches(settings, since_days=7, limit=10)
    if not rows:
        return "No new matches in the last 7 days."
    return _build_reply(["🎯 New matches (7d)", *[format_job_block(j) for j in rows]])


def _cmd_companies(settings: Settings, supabase: Client, args: str) -> str:
    rows = query(
        settings,
        """
        select s.company_name, s.ats_type, s.active, count(j.id)::int as job_count
        from sources s
        left join jobs j on j.source_id = s.id
        group by s.id
        order by s.company_name
        """,
    )
    lines = [f"🏢 Companies ({len(rows)})", ""]
    for r in rows:
        suffix = "" if r["active"] else " (inactive)"
        lines.append(f"• {r['company_name']} ({r['ats_type']}) — {r['job_count']} jobs{suffix}")
    return "\n".join(lines)


def _cmd_sources(settings: Settings, supabase: Client, args: str) -> str:
    rows = supabase.table("sources").select("*").eq("active", True).execute().data or []
    intervals = settings.ats_intervals
    now = datetime.now(UTC)
    lines = [f"🩺 Source health ({len(rows)})", ""]
    for src in rows:
        interval = intervals.get(src["ats_type"], 3600)
        status, reason = source_status(src, interval, now)
        lines.append(f"{STATUS_EMOJI.get(status, '\u26aa')} {src['company_name']} — {status}")
        if reason:
            lines.append(f"   {reason}")
    return "\n".join(lines)


def _cmd_schedule(settings: Settings, supabase: Client, args: str) -> str:
    overrides = load_interval_overrides(supabase)
    intervals = effective_intervals(settings.ats_intervals, overrides)
    last_checked = last_checked_by_ats(settings)
    counts = source_count_by_ats(settings)
    lines = ["🕐 Polling schedule", ""]
    for ats, interval in intervals.items():
        suffix = " (overridden)" if ats in overrides else ""
        nxt = next_run_at(interval, last_checked.get(ats))
        nxt_txt = f"next ~{_fmt_dt(nxt)}" if nxt else "next unknown"
        lines.append(
            f"• {ats}{suffix}: every {_fmt_interval(interval)} — "
            f"{counts.get(ats, 0)} source(s), {nxt_txt}"
        )
    return "\n".join(lines)


def _cmd_runs(settings: Settings, supabase: Client, args: str) -> str:
    rows = query(
        settings,
        """
        select id, triggered_by, ats_type, status, started_at, finished_at,
               jobs_fetched, jobs_new, matches_new, telegram_sent, email_sent, error
        from poll_runs
        order by started_at desc
        limit 5
        """,
    )
    if not rows:
        return "No poll runs recorded yet."
    lines = ["▶️ Recent poll runs", ""]
    for r in rows:
        marker = {"completed": "✅", "failed": "❌", "running": "⏳"}.get(r["status"], "•")
        scope = r["ats_type"] or "all"
        error = f" — {r['error']}" if r.get("error") else ""
        lines.append(
            f"{marker} {_fmt_dt(r['started_at'])} {r['triggered_by']} ({scope}) — "
            f"{r['status']}{error}"
        )
        lines.append(
            f"   fetched {r['jobs_fetched']} · new {r['jobs_new']} · "
            f"matches {r['matches_new']} · tg {r['telegram_sent']} · email {r['email_sent']}"
        )
    return "\n".join(lines)


def _cmd_notifications(settings: Settings, supabase: Client, args: str) -> str:
    rows = query(
        settings,
        """
        select n.channel, n.sent_at, j.title, s.company_name
        from notifications_sent n
        left join jobs j on j.id = n.job_id
        left join sources s on s.id = j.source_id
        where n.user_id = %s
        order by n.sent_at desc
        limit 10
        """,
        (DEFAULT_USER_ID,),
    )
    if not rows:
        return "No alerts sent yet."
    lines = ["🔔 Recent alerts", ""]
    for r in rows:
        title = r["title"] or "?"
        company = r["company_name"] or "?"
        channel = "Telegram" if r["channel"] == "telegram" else "Email"
        lines.append(f"• {_fmt_dt(r['sent_at'])} · {channel} — {title} · {company}")
    return "\n".join(lines)


def _cmd_preferences(settings: Settings, supabase: Client, args: str) -> str:
    rows = query(
        settings,
        """
        select roles, keywords, locations, seniority, excluded_companies,
               excluded_roles, notify_telegram, notify_email, alert_frequency,
               telegram_scope, email_scope, notify_first_check
        from preferences where user_id = %s
        """,
        (DEFAULT_USER_ID,),
    )
    env = settings.preferences
    if not rows:
        prefs = {
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
        }
    else:
        row = rows[0]
        prefs = {
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
        }

    def _fmt_list(values: list[str]) -> str:
        return ", ".join(values) if values else "—"

    notify = []
    if prefs["notify_telegram"]:
        notify.append(f"Telegram ({prefs['telegram_scope']})")
    if prefs["notify_email"]:
        notify.append(f"Email ({prefs['email_scope']})")
    return _build_reply(
        [
            "⚙️ Preferences",
            (
                f"Roles: {_fmt_list(prefs['roles'])}\n"
                f"Skills: {_fmt_list(prefs['keywords'])}\n"
                f"Locations: {_fmt_list(prefs['locations'])}\n"
                f"Seniority: {_fmt_list(prefs['seniority'])}\n"
                f"Excluded roles: {_fmt_list(prefs['excluded_roles'])}\n"
                f"Excluded companies: {_fmt_list(prefs['excluded_companies'])}\n"
                f"Alerts: {', '.join(notify) if notify else '—'} · {prefs['alert_frequency']}"
            ),
        ]
    )


HANDLERS: dict[str, Any] = {
    "start": _cmd_start,
    "help": _cmd_help,
    "stats": _cmd_stats,
    "jobs": _cmd_jobs,
    "newjobs": _cmd_newjobs,
    "matches": _cmd_matches,
    "newmatches": _cmd_newmatches,
    "companies": _cmd_companies,
    "sources": _cmd_sources,
    "schedule": _cmd_schedule,
    "runs": _cmd_runs,
    "notifications": _cmd_notifications,
    "preferences": _cmd_preferences,
}


def dispatch_command(settings: Settings, supabase: Client, command: str, args: str) -> str:
    handler = HANDLERS.get(command)
    if handler is None:
        return "Unknown command. Try /help."
    try:
        return handler(settings, supabase, args)
    except Exception as exc:
        print(f"telegram command '{command}' failed: {exc}")
        return f"Error running /{command}: {exc}"


# ---------- long polling ----------


async def _answer_callback(client: httpx.AsyncClient, token: str, callback_id: str) -> None:
    response = await _post_async(
        client, token, "answerCallbackQuery", {"callback_query_id": callback_id}
    )
    if response.status_code >= 400:
        print(f"telegram answerCallbackQuery {response.status_code}: {response.text[:200]}")


async def _handle_callback(
    settings: Settings, update: dict[str, Any], client: httpx.AsyncClient
) -> None:
    """Handle an inline-menu callback (read-only commands only).

    The menu never exposes mutating actions, so a callback is safe to answer
    as-is. Chat authorization still applies exactly like a typed command.
    """
    callback = update.get("callback_query") or {}
    data = callback.get("data") or ""
    callback_id = callback.get("id") or ""
    chat_id = (callback.get("message") or {}).get("chat", {}).get("id")
    token = settings.telegram_bot_token
    if not data.startswith("menu:") or not callback_id or not chat_id:
        return
    command = data.split(":", 1)[1]
    if command not in MENU_COMMANDS:
        return
    await _answer_callback(client, token, callback_id)
    if not authorized(chat_id, settings):
        await _send_message(client, token, chat_id, "Not authorized.")
        return
    supabase = get_supabase(settings)
    reply = dispatch_command(settings, supabase, command, "")
    if reply:
        await _send_message(client, token, chat_id, reply, reply_markup=_menu_markup())


async def handle_update(
    settings: Settings, update: dict[str, Any], client: httpx.AsyncClient
) -> None:
    if "callback_query" in update:
        await _handle_callback(settings, update, client)
        return
    message = update.get("message") or {}
    text = (message.get("text") or "").strip()
    chat_id = (message.get("chat") or {}).get("id")
    if not text or not chat_id:
        return
    if not text.startswith("/"):
        return
    token = settings.telegram_bot_token
    if not authorized(chat_id, settings):
        await _send_message(client, token, chat_id, "Not authorized.")
        return
    command, args = parse_command(text)
    supabase = get_supabase(settings)
    reply = dispatch_command(settings, supabase, command, args)
    if reply:
        await _send_message(client, token, chat_id, reply, reply_markup=_menu_markup())


async def run_bot(settings: Settings) -> None:
    """Long-poll getUpdates forever, dispatching commands as they arrive."""
    token = settings.telegram_bot_token
    offset = 0
    async with httpx.AsyncClient(timeout=POLL_TIMEOUT + 20) as client:
        while True:
            try:
                response = await _post_async(
                    client,
                    token,
                    "getUpdates",
                    {
                        "offset": offset,
                        "timeout": POLL_TIMEOUT,
                        "allowed_updates": ["message", "callback_query"],
                    },
                )
                if response.status_code >= 400:
                    raise RuntimeError(f"getUpdates {response.status_code}: {response.text[:200]}")
                for update in response.json().get("result", []):
                    offset = update["update_id"] + 1
                    await handle_update(settings, update, client)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                print(f"telegram bot poll error: {exc}")
                await asyncio.sleep(5)
