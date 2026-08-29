"""User accounts: owner bootstrap, registration, lookups.

The historical sentinel id (DEFAULT_USER_ID) is seeded as the owner/admin
account so every existing user_id reference keeps working unchanged.
"""

from datetime import UTC, datetime
from typing import Any

from supabase import Client

from app.config import DEFAULT_USER_ID, Settings
from app.db import query

OWNER_DISPLAY_NAME = "owner"


def ensure_owner(settings: Settings) -> dict[str, Any]:
    """Seed the owner row (idempotent) and stamp env identities when missing."""
    query(
        settings,
        """
        insert into users (id, role, status, access_locked, is_owner, display_name)
        values (%s, 'admin', 'approved', false, true, %s)
        on conflict (id) do nothing
        """,
        (DEFAULT_USER_ID, OWNER_DISPLAY_NAME),
    )
    if settings.telegram_chat_id:
        try:
            chat_id = int(settings.telegram_chat_id)
            # For private chats chat_id == user_id, so stamp both columns when empty.
            query(
                settings,
                """
                update users set
                    telegram_chat_id = coalesce(telegram_chat_id, %s),
                    telegram_user_id = coalesce(telegram_user_id, %s),
                    updated_at = now()
                where id = %s and (telegram_chat_id is null or telegram_user_id is null)
                """,
                (chat_id, chat_id, DEFAULT_USER_ID),
            )
        except ValueError:
            pass
    if settings.notify_to:
        query(
            settings,
            "update users set email = %s, updated_at = now() where id = %s and email is null",
            (settings.notify_to[0], DEFAULT_USER_ID),
        )
    rows = fetch_user(settings, DEFAULT_USER_ID)
    if not rows:
        raise RuntimeError("owner user row missing after ensure_owner")
    return rows[0]


def fetch_user(settings: Settings, user_id: str) -> list[dict[str, Any]]:
    return query(
        settings,
        "select id, email, telegram_chat_id, telegram_user_id, telegram_username, "
        "display_name, role, status, capabilities, alert_delay_minutes, access_locked, "
        "is_owner, password_hash, last_login_at, created_at from users where id = %s::uuid",
        (user_id,),
    )


def fetch_user_by_email(settings: Settings, email: str) -> list[dict[str, Any]]:
    return query(
        settings,
        "select id, email, telegram_chat_id, display_name, role, status, capabilities, "
        "alert_delay_minutes, access_locked, is_owner, password_hash "
        "from users where lower(email) = lower(%s)",
        (email,),
    )


def fetch_user_by_telegram(settings: Settings, telegram_user_id: int) -> list[dict[str, Any]]:
    return query(
        settings,
        "select id, email, telegram_chat_id, telegram_user_id, telegram_username, telegram_photo_url, "
        "display_name, role, status, capabilities, "
        "alert_delay_minutes, access_locked, is_owner from users where telegram_user_id = %s",
        (telegram_user_id,),
    )


def fetch_user_by_telegram_any(settings: Settings, telegram_id: int) -> list[dict[str, Any]]:
    """Lookup by either telegram_user_id or telegram_chat_id (covers legacy owner rows where only chat_id was stamped)."""
    return query(
        settings,
        "select id, email, telegram_chat_id, telegram_user_id, telegram_username, telegram_photo_url, "
        "display_name, role, status, capabilities, alert_delay_minutes, access_locked, is_owner "
        "from users where telegram_user_id = %s or telegram_chat_id = %s limit 1",
        (telegram_id, telegram_id),
    )


def fetch_user_by_telegram_chat(settings: Settings, telegram_chat_id: int) -> list[dict[str, Any]]:
    return query(
        settings,
        "select id, email, telegram_chat_id, telegram_user_id, telegram_username, telegram_photo_url, "
        "display_name, role, status, capabilities, "
        "alert_delay_minutes, access_locked, is_owner from users where telegram_chat_id = %s",
        (telegram_chat_id,),
    )


def _tg_display_name(tg: dict[str, Any]) -> str:
    first = (tg.get("first_name") or "").strip()
    last = (tg.get("last_name") or "").strip()
    full = f"{first} {last}".strip()
    if full:
        return full
    if tg.get("username"):
        return str(tg["username"])
    if tg.get("id"):
        return f"tg_{tg['id']}"
    return "telegram_user"


def create_user_from_telegram(
    settings: Settings,
    supabase: Client,
    tg: dict[str, Any],
) -> dict[str, Any]:
    """Create a new account from a verified Telegram identity.

    Telegram-only accounts have email=None; the onboarding flow will prompt
    for it later. They start as approved but access_locked (same gate as
    email registration) so billing still applies.
    """
    tg_id = int(tg["id"])
    # Conflict check: telegram_user_id is unique
    existing = fetch_user_by_telegram(settings, tg_id)
    if existing:
        raise ValueError("this Telegram account is already linked to another profile")
    payload: dict[str, Any] = {
        "telegram_user_id": tg_id,
        "telegram_chat_id": int(tg.get("chat_id") or tg_id),
        "telegram_username": tg.get("username"),
        "telegram_photo_url": tg.get("photo_url"),
        "display_name": _tg_display_name(tg),
        "role": "user",
        "status": "approved",
        "access_locked": True,
        "capabilities": ["dashboard", "preferences", "telegram_alerts"],
    }
    # Keep email null for now — onboarding may fill it
    response = supabase.table("users").insert(payload).execute()
    if not response.data:
        raise RuntimeError("failed to create telegram user")
    row = response.data[0]
    seed_preferences(supabase, row["id"], settings.preferences)
    return row


def link_telegram_to_user(
    settings: Settings,
    user_id: str,
    tg: dict[str, Any],
) -> dict[str, Any]:
    """Link a verified Telegram identity to an existing user. Raises if already taken."""
    tg_id = int(tg["id"])
    chat_id = int(tg.get("chat_id") or tg_id)
    # If someone else already owns this telegram_user_id, refuse
    owner = fetch_user_by_telegram(settings, tg_id)
    if owner and str(owner[0]["id"]) != str(user_id):
        raise ValueError("this Telegram account is already linked to another profile")
    # Also guard chat_id uniqueness across other users
    chat_owner = fetch_user_by_telegram_chat(settings, chat_id)
    if chat_owner and str(chat_owner[0]["id"]) != str(user_id):
        raise ValueError("this Telegram chat is already linked to another profile")
    rows = query(
        settings,
        """
        update users
        set telegram_user_id = %s,
            telegram_chat_id = %s,
            telegram_username = %s,
            telegram_photo_url = coalesce(%s, telegram_photo_url),
            -- Fill display_name only if currently empty/owner-like
            display_name = case when display_name in ('', 'owner') then %s else display_name end,
            updated_at = now()
        where id = %s::uuid
        returning id, email, telegram_chat_id, telegram_user_id, telegram_username, telegram_photo_url,
                  display_name, role, status, capabilities, alert_delay_minutes, access_locked, is_owner
        """,
        (tg_id, chat_id, tg.get("username"), tg.get("photo_url"), _tg_display_name(tg), user_id),
    )
    if not rows:
        raise LookupError("user not found")
    return rows[0]


def update_user_profile(
    settings: Settings, user_id: str, display_name: str | None = None, email: str | None = None
) -> dict[str, Any]:
    """Update display_name/email for the onboarding completion step."""
    fields: dict[str, Any] = {}
    if display_name is not None:
        fields["display_name"] = display_name.strip()
    if email is not None:
        email = email.strip().lower()
        if email == "":
            email = None
        elif "@" not in email:
            raise ValueError("a valid email is required")
        else:
            # Ensure no one else owns this email
            existing = fetch_user_by_email(settings, email)
            if existing and str(existing[0]["id"]) != str(user_id):
                raise ValueError("an account with this email already exists")
            fields["email"] = email
    if not fields:
        raise ValueError("nothing to update")
    sets = ", ".join(f"{k} = %s" for k in fields)
    params = [*fields.values(), user_id]
    rows = query(
        settings,
        f"update users set {sets}, updated_at = now() where id = %s::uuid returning id, email, telegram_chat_id, telegram_user_id, telegram_username, display_name, role, status, capabilities, alert_delay_minutes, access_locked, is_owner",
        tuple(params),
    )
    if not rows:
        raise LookupError("user not found")
    return rows[0]


def touch_login(settings: Settings, user_id: str) -> None:
    query(
        settings,
        "update users set last_login_at = now(), updated_at = now() where id = %s::uuid",
        (user_id,),
    )


def seed_preferences(supabase: Client, user_id: str, preferences: dict[str, Any]) -> None:
    """Create a per-user preferences row from the env defaults (same shape and
    semantics as matcher.sync_preferences, but for any user). Never overwrites
    an existing row."""
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


def create_registered_user(
    settings: Settings,
    supabase: Client,
    *,
    email: str,
    display_name: str = "",
    password: str | None = None,
) -> dict[str, Any]:
    """Register a new account. Requires admin approval before login is allowed."""
    email = (email or "").strip().lower()
    if not email or "@" not in email:
        raise ValueError("a valid email is required")
    if not password:
        raise ValueError("password is required")
    from app.auth import hash_password, validate_password_strength

    problems = validate_password_strength(password)
    if problems:
        raise ValueError(problems[0])
    existing = fetch_user_by_email(settings, email)
    if existing:
        raise ValueError("an account with this email already exists")
    payload: dict[str, Any] = {
        "email": email,
        "display_name": display_name.strip() or email.split("@")[0],
        "role": "user",
        "status": "pending",
        "access_locked": True,
        "password_hash": hash_password(password),
    }
    response = supabase.table("users").insert(payload).execute()
    row = response.data[0]
    seed_preferences(supabase, row["id"], settings.preferences)
    return row


def set_password(settings: Settings, user_id: str, new_hash: str) -> None:
    query(
        settings,
        "update users set password_hash = %s, updated_at = now() where id = %s::uuid",
        (new_hash, user_id),
    )


def admin_update_user(settings: Settings, user_id: str, update: dict[str, Any]) -> dict[str, Any]:
    allowed = {"role", "status", "capabilities", "alert_delay_minutes", "access_locked"}
    payload = {k: v for k, v in update.items() if k in allowed}
    if not payload:
        raise ValueError("nothing to update")
    sets = ", ".join(f"{k} = %s" for k in payload)
    params = [*payload.values(), user_id]
    rows = query(
        settings,
        f"update users set {sets}, updated_at = now() where id = %s::uuid "
        "returning id, email, role, status, capabilities, alert_delay_minutes, access_locked",
        tuple(params),
    )
    if not rows:
        raise LookupError("user not found")
    return rows[0]
