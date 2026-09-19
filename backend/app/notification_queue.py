"""Notification queue: enqueue-at-match-time + drain worker.

Ingestion no longer waits for every source before matching/notifying. Each
per-source task calls match_and_enqueue() immediately after its upsert;
drain_due_notifications() releases rows whose scheduled_for has passed
(scheduled_for = enqueue time + users.alert_delay_minutes).
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

from supabase import Client

from app.config import Settings
from app.db import query
from app.entitlements import (
    can_receive_channel,
    delivery_delay_minutes,
    is_deliverable,
)
from app.matcher import compute_match_score, job_matches_preferences
from app.notify import _send_email
from app.telegram.messages import build_html, build_text_sections, build_text_summary
from app.telegram.notifications import MAX_MESSAGE_LENGTH, _chunk_sections, _send_message

IN_BATCH = 200
DRAIN_BATCH = 400
MAX_ATTEMPTS = 3


@dataclass
class AudienceUser:
    """One recipient with everything needed to match + schedule alerts."""

    id: str
    role: str
    status: str
    access_locked: bool
    alert_delay_minutes: int
    telegram_chat_id: int | None
    email: str | None
    capabilities: list[str]
    prefs: dict[str, Any] = field(default_factory=dict)

    @property
    def has_active_subscription(self) -> bool:
        return self.role in ("admin", "privileged") or bool(self.prefs.get("_has_active_sub"))

    def deliverable(self) -> bool:
        return is_deliverable(
            {"status": self.status, "access_locked": self.access_locked, "role": self.role},
            has_active_subscription=self.has_active_subscription,
        )


def _load_tier_delays(settings: Settings) -> tuple[int, int]:
    """Return (privileged_delay, normal_delay) minutes from app_settings, with defaults."""
    try:
        rows = query(
            settings,
            "select key, value from app_settings where key in ('privileged_delay_minutes','normal_delay_minutes')",
        )
        m = {r["key"]: r["value"] for r in rows}

        # value may be int or jsonb int
        def _as_int(v, default):
            if v is None:
                return default
            if isinstance(v, int):
                return v
            try:
                return int(v)
            except Exception:
                try:
                    return int(str(v).strip('"'))
                except Exception:
                    return default

        return _as_int(m.get("privileged_delay_minutes"), 30), _as_int(
            m.get("normal_delay_minutes"), 360
        )
    except Exception:
        return 30, 360


def load_audience(settings: Settings) -> list[AudienceUser]:
    """Every account that may receive alerts right now, with preferences."""
    priv_delay, normal_delay = _load_tier_delays(settings)
    rows = query(
        settings,
        """
        select u.id, u.role, u.status, u.access_locked, u.alert_delay_minutes,
               u.telegram_chat_id, u.email, u.capabilities,
               p.roles, p.keywords, p.locations, p.seniority,
               p.excluded_companies, p.excluded_roles,
               p.notify_telegram, p.notify_email,
               p.telegram_scope, p.email_scope,
               (s.id is not null) as has_active_sub
        from users u
        left join preferences p on p.user_id = u.id
        left join subscriptions s on s.user_id = u.id and s.status = 'active'
        where u.status = 'approved'
          and not u.access_locked
        """,
    )
    audience: list[AudienceUser] = []
    for row in rows:
        # Inject tier delays so delivery_delay_minutes can use them
        row["_tier_privileged_delay"] = priv_delay
        row["_tier_normal_delay"] = normal_delay
        audience.append(
            AudienceUser(
                id=str(row["id"]),
                role=row.get("role") or "user",
                status=row.get("status") or "approved",
                access_locked=bool(row.get("access_locked")),
                alert_delay_minutes=delivery_delay_minutes(row),
                telegram_chat_id=row.get("telegram_chat_id"),
                email=row.get("email"),
                capabilities=row.get("capabilities") or [],
                prefs={
                    "roles": row.get("roles") or [],
                    "keywords": row.get("keywords") or [],
                    "locations": row.get("locations") or [],
                    "seniority": row.get("seniority") or [],
                    "excluded_companies": row.get("excluded_companies") or [],
                    "excluded_roles": row.get("excluded_roles") or [],
                    "notify_telegram": row.get("notify_telegram", True),
                    "notify_email": row.get("notify_email", True),
                    "telegram_scope": row.get("telegram_scope", "matched"),
                    "email_scope": row.get("email_scope", "matched"),
                    "_has_active_sub": bool(row.get("has_active_sub")),
                },
            )
        )
    return audience


def evaluate_jobs_for_user(
    jobs: list[dict[str, Any]], user: AudienceUser, geo_settings: dict[str, Any] | None
) -> tuple[list[dict[str, Any]], set[str]]:
    """Match one user against fetched job rows. Pure given inputs.

    Returns (job_matches upsert rows, matched job-id set).
    """
    match_rows: list[dict[str, Any]] = []
    matched_ids: set[str] = set()
    for job in jobs:
        is_match, reasons = job_matches_preferences(job, user.prefs, geo_settings)
        if not is_match:
            continue
        matched_ids.add(job["id"])
        match_rows.append(
            {
                "user_id": user.id,
                "job_id": job["id"],
                "matched_on": reasons,
                "match_score": compute_match_score(job, user.prefs, geo_settings),
            }
        )
    return match_rows, matched_ids


def build_queue_rows(
    *,
    now: datetime,
    candidate_job_ids: list[str],
    user: AudienceUser,
    matched_ids: set[str],
    channels: list[str],
) -> list[dict[str, Any]]:
    """Rows to enqueue for one user. Scope flags decide matched-only vs all."""
    scheduled_for = now + timedelta(minutes=user.alert_delay_minutes)
    rows: list[dict[str, Any]] = []
    for channel in channels:
        scope = user.prefs.get(f"{channel}_scope", "matched")
        ids = matched_ids if scope == "matched" else candidate_job_ids
        for job_id in ids:
            rows.append(
                {
                    "user_id": user.id,
                    "job_id": job_id,
                    "channel": channel,
                    "scheduled_for": scheduled_for.isoformat(),
                }
            )
    return rows


def _channels_for(user: AudienceUser) -> list[str]:
    channels: list[str] = []
    if (
        user.telegram_chat_id
        and user.prefs.get("notify_telegram", True)
        and can_receive_channel({"capabilities": user.capabilities, "role": user.role}, "telegram")
    ):
        channels.append("telegram")
    if (
        user.email
        and user.prefs.get("notify_email", True)
        and can_receive_channel({"capabilities": user.capabilities, "role": user.role}, "email")
    ):
        channels.append("email")
    return channels


def _batched(rows: list[dict[str, Any]], size: int = IN_BATCH):
    for start in range(0, len(rows), size):
        yield rows[start : start + size]


def match_and_enqueue(
    supabase: Client,
    settings: Settings,
    *,
    company_by_source: dict[str, str],
    audience: list[AudienceUser],
    geo_settings: dict[str, Any] | None,
    source_id: str,
    external_ids: list[str],
    now: datetime | None = None,
) -> dict[str, int]:
    """Per-source pipeline step: refetch the freshly-inserted rows, match every
    eligible user in memory, persist job_matches, enqueue alerts."""
    now = now or datetime.now(UTC)
    considered = 0
    matched_new = 0
    enqueued = 0

    if not external_ids or not audience:
        return {"considered": 0, "matched": 0, "enqueued": 0}

    deliverable = [u for u in audience if u.deliverable()]
    if not deliverable:
        return {"considered": 0, "matched": 0, "enqueued": 0}

    jobs: list[dict[str, Any]] = []
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
    for job in jobs:
        job["company_name"] = company_by_source.get(job.get("source_id"), "")
    considered = len(jobs)

    all_match_rows: list[dict[str, Any]] = []
    matched_by_user: dict[str, set[str]] = {}
    candidate_ids = [job["id"] for job in jobs]
    for user in deliverable:
        match_rows, matched_ids = evaluate_jobs_for_user(jobs, user, geo_settings)
        matched_by_user[user.id] = matched_ids
        all_match_rows.extend(match_rows)

    if all_match_rows:
        matched_new = len(all_match_rows)
        for chunk in _batched(all_match_rows):
            supabase.table("job_matches").upsert(chunk, on_conflict="user_id,job_id").execute()

    queue_rows: list[dict[str, Any]] = []
    for user in deliverable:
        queue_rows.extend(
            build_queue_rows(
                now=now,
                candidate_job_ids=candidate_ids,
                user=user,
                matched_ids=matched_by_user.get(user.id, set()),
                channels=_channels_for(user),
            )
        )
    if queue_rows:
        for chunk in _batched(queue_rows):
            response = (
                supabase.table("notification_queue")
                .upsert(chunk, on_conflict="user_id,job_id,channel", ignore_duplicates=True)
                .execute()
            )
        enqueued = len(queue_rows)

    return {"considered": considered, "matched": matched_new, "enqueued": enqueued}


# ---------- drain ----------


def retry_decision(attempts_after_increment: int) -> str:
    """'pending' while retries remain, then 'failed'. Pure."""
    return "failed" if attempts_after_increment >= MAX_ATTEMPTS else "pending"


def drain_due_notifications(
    settings: Settings, supabase: Client, *, limit: int = DRAIN_BATCH, now: datetime | None = None
) -> dict[str, int]:
    """Send every due queue row. Groups by (user, channel) so each person gets
    one consolidated message per channel per drain tick."""
    now = now or datetime.now(UTC)
    # Exclude rows whose user has no destination for that channel – they would
    # otherwise occupy the LIMIT window forever and starve deliverable users
    # (e.g., a user without telegram_chat_id whose telegram rows stay pending).
    # Those rows are canceled below on first sight; filtering here makes the fix
    # effective immediately without needing 14 drain ticks to clear 5530 rows.
    due = query(
        settings,
        """
        select q.id, q.user_id, q.job_id, q.channel, q.attempts,
               u.role, u.status, u.access_locked, u.capabilities,
               u.alert_delay_minutes, u.telegram_chat_id, u.email
        from notification_queue q
        join users u on u.id = q.user_id
        where q.status = 'pending'
          and q.scheduled_for <= %s
          and (
                (q.channel = 'telegram' and u.telegram_chat_id is not null)
             or (q.channel = 'email' and u.email is not null and u.email <> '')
          )
        order by
          case when u.role = 'admin' then 0
               when u.role = 'privileged' then 1
               else 2 end,
          q.scheduled_for
        limit %s
        """,
        (now.isoformat(), limit),
    )
    # Opportunistic cleanup: pending rows for users missing a destination are
    # stale (future enqueues require a destination – see _channels_for). Cancel
    # them so they never accumulate and never block the due-window. This is
    # best-effort and ignores errors so it never breaks the drain.
    try:
        _cancel_undeliverable_pending(settings, supabase)
    except Exception:
        pass
    if not due:
        return {"sent_telegram": 0, "sent_email": 0, "failed": 0}

    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in due:
        groups.setdefault((row["user_id"], row["channel"]), []).append(row)

    sent = {"telegram": 0, "email": 0}
    failed = 0

    for (user_id, channel), rows in groups.items():
        head = rows[0]
        if head.get("status") == "disabled" or head.get("access_locked"):
            # Locked/disabled accounts: leave rows pending (resumes if unlocked).
            continue
        user_caps = head.get("capabilities") or []
        if not can_receive_channel({"capabilities": user_caps, "role": head.get("role")}, channel):
            _mark_rows(supabase, [r["id"] for r in rows], status="canceled")
            continue

        destination: str | None = None
        globally_enabled = True
        if channel == "telegram":
            destination = str(head["telegram_chat_id"]) if head.get("telegram_chat_id") else None
            globally_enabled = settings.telegram_enabled
        elif channel == "email":
            destination = head.get("email")
            globally_enabled = settings.notify_enabled
        if not globally_enabled:
            # Channel disabled globally: stay pending (admin may re-enable).
            continue
        if not destination:
            # No destination for this channel (e.g., telegram without chat_id).
            # Future enqueues require a destination – cancel stale rows so they
            # never block the LIMIT window for deliverable users.
            _mark_rows(supabase, [r["id"] for r in rows], status="canceled")
            continue

        job_ids = [r["job_id"] for r in rows]
        items = _load_job_items(settings, job_ids, user_id)
        try:
            if channel == "telegram":
                sections = [build_text_summary(len(items), len(items))]
                if items:
                    sections += build_text_sections(items)[1:]
                for chunk in _chunk_sections(sections, MAX_MESSAGE_LENGTH):
                    _send_message(settings.telegram_bot_token, destination, chunk)
                sent["telegram"] += len(rows)
            else:
                html = build_html(items, new_jobs=len(items), new_matches=len(items))
                subject = (
                    f"📡 JobQuest: {len(items)} new matching job(s) — {datetime.now(UTC):%b %d}"
                )
                _send_email(settings.resend_api_key, [destination], subject, html)
                sent["email"] += len(rows)
        except Exception as exc:
            failed += _record_failure(settings, supabase, rows, exc)
            continue
        _mark_rows(supabase, [r["id"] for r in rows], status="sent")
        _record_ledger(supabase, rows)

    return {
        "sent_telegram": sent["telegram"],
        "sent_email": sent["email"],
        "failed": failed,
    }


def _load_job_items(settings: Settings, job_ids: list[str], user_id: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for start in range(0, len(job_ids), IN_BATCH):
        batch = job_ids[start : start + IN_BATCH]
        items.extend(
            query(
                settings,
                """
                select j.id, j.title, j.location, j.url,
                       coalesce(m.matched_on, '{}') as matched_on,
                       s.company_name as company
                from jobs j
                join sources s on s.id = j.source_id
                left join job_matches m
                       on m.job_id = j.id and m.user_id = %s::uuid
                where j.id = any(%s::uuid[])
                """,
                (user_id, batch),
            )
        )
    return items


def _cancel_undeliverable_pending(settings: Settings, supabase: Client) -> int:
    """Cancel pending queue rows where the user has no destination for that channel.

    These rows were enqueued before _channels_for required a destination and would
    otherwise sit pending forever, occupying the drain LIMIT and starving the
    admin (who does have a telegram_chat_id). Best-effort: returns canceled count.
    """
    canceled = 0
    # Telegram without chat_id
    try:
        rows = query(
            settings,
            """
            select q.id from notification_queue q
            join users u on u.id = q.user_id
            where q.status = 'pending' and q.channel = 'telegram'
              and u.telegram_chat_id is null
            limit 1000
            """,
        )
        ids = [r["id"] for r in rows]
        if ids:
            _mark_rows(supabase, ids, status="canceled")
            canceled += len(ids)
    except Exception:
        pass
    # Email without address
    try:
        rows = query(
            settings,
            """
            select q.id from notification_queue q
            join users u on u.id = q.user_id
            where q.status = 'pending' and q.channel = 'email'
              and (u.email is null or u.email = '')
            limit 1000
            """,
        )
        ids = [r["id"] for r in rows]
        if ids:
            _mark_rows(supabase, ids, status="canceled")
            canceled += len(ids)
    except Exception:
        pass
    return canceled


def _mark_rows(supabase: Client, row_ids: list[str], *, status: str) -> None:
    update: dict[str, Any] = {"status": status}
    if status == "sent":
        update["sent_at"] = datetime.now(UTC).isoformat()
    for start in range(0, len(row_ids), IN_BATCH):
        supabase.table("notification_queue").update(update).in_(
            "id", row_ids[start : start + IN_BATCH]
        ).execute()


def _record_failure(
    settings: Settings, supabase: Client, rows: list[dict[str, Any]], exc: Exception
) -> int:
    message = str(exc)[:300]
    failed = 0
    for row in rows:
        attempts = int(row.get("attempts") or 0) + 1
        status = retry_decision(attempts)
        if status == "failed":
            failed += 1
        supabase.table("notification_queue").update(
            {"attempts": attempts, "status": status, "last_error": message}
        ).eq("id", row["id"]).execute()
    return failed


def _record_ledger(supabase: Client, rows: list[dict[str, Any]]) -> None:
    sent_at = datetime.now(UTC).isoformat()
    ledger = [
        {
            "user_id": r["user_id"],
            "job_id": r["job_id"],
            "channel": r["channel"],
            "sent_at": sent_at,
        }
        for r in rows
    ]
    for chunk in _batched(ledger):
        supabase.table("notifications_sent").upsert(
            chunk, on_conflict="user_id,job_id,channel"
        ).execute()
