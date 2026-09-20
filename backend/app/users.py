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
            query(
                settings,
                """
                update users set
                    telegram_chat_id = coalesce(telegram_chat_id, %s),
                    updated_at = now()
                where id = %s and telegram_chat_id is null
                """,
                (chat_id, DEFAULT_USER_ID),
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
        "select id, email, telegram_chat_id, "
        "display_name, role, status, capabilities, alert_delay_minutes, access_locked, "
        "is_owner, password_hash, last_login_at, created_at from users where id = %s::uuid",
        (user_id,),
    )


def fetch_user_by_email(settings: Settings, email: str) -> list[dict[str, Any]]:
    return query(
        settings,
        "select id, email, telegram_chat_id, display_name, role, status, capabilities, "
        "alert_delay_minutes, access_locked, is_owner, password_hash, "
        "failed_login_attempts, lockout_until, last_failed_at "
        "from users where lower(email) = lower(%s)",
        (email,),
    )


def fetch_user_by_telegram_chat(settings: Settings, telegram_chat_id: int) -> list[dict[str, Any]]:
    return query(
        settings,
        "select id, email, telegram_chat_id, "
        "display_name, role, status, capabilities, "
        "alert_delay_minutes, access_locked, is_owner from users where telegram_chat_id = %s",
        (telegram_chat_id,),
    )


def update_user_profile(
    settings: Settings, user_id: str, display_name: str | None = None, email: str | None = None
) -> dict[str, Any]:
    """Update display_name/email for the onboarding completion step."""
    from app.auth import is_valid_email, sanitize_display_name

    fields: dict[str, Any] = {}
    if display_name is not None:
        # Use MNC sanitizer
        fields["display_name"] = sanitize_display_name(display_name)
    if email is not None:
        email = email.strip().lower()
        if email == "":
            email = None
        elif not is_valid_email(email):
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
        f"update users set {sets}, updated_at = now() where id = %s::uuid returning id, email, telegram_chat_id, display_name, role, status, capabilities, alert_delay_minutes, access_locked, is_owner",
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
    """Register a new account. MNC flow: approved immediately but locked until payment/coupon."""
    from app.auth import (
        hash_password,
        is_valid_email,
        sanitize_display_name,
        validate_password_strength,
    )

    email = (email or "").strip().lower()
    if not is_valid_email(email):
        raise ValueError("a valid email is required")
    # sanitize display_name via MNC rules
    if display_name and display_name.strip():
        display_name = sanitize_display_name(display_name)
    else:
        display_name = email.split("@")[0]
    if not password:
        raise ValueError("password is required")
    problems = validate_password_strength(password, email=email, display_name=display_name)
    if problems:
        raise ValueError(problems[0])
    existing = fetch_user_by_email(settings, email)
    if existing:
        raise ValueError("an account with this email already exists")
    payload: dict[str, Any] = {
        "email": email,
        "display_name": display_name.strip() or email.split("@")[0],
        "role": "user",
        "status": "approved",
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
