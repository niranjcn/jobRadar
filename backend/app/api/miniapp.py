"""Mini App auth: validates Telegram WebApp initData and returns user."""

import hashlib
import hmac
import json
import time
from typing import Any
from urllib.parse import parse_qsl, unquote

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.config import load_settings
from app.db import query

router = APIRouter(prefix="/api/miniapp", tags=["miniapp"])


def _validate_init_data(init_data: str, bot_token: str) -> dict[str, Any] | None:
    """Validate Telegram Mini App initData per https://core.telegram.org/bots/web_apps#validating-data-received-via-the-mini-app.

    Returns the `user` dict if valid, None otherwise.
    """
    if not init_data or not bot_token:
        return None
    # Parse query string into dict
    try:
        data = dict(parse_qsl(init_data, keep_blank_values=True))
    except Exception:
        return None
    hash_received = data.pop("hash", None)
    if not hash_received:
        return None
    # Build data_check_string: sorted keys joined as key=value with newline
    # Values must be as received (parse_qsl already decodes, but Telegram expects decoded)
    # Re-encode check: use sorted keys
    check_parts = [f"{k}={data[k]}" for k in sorted(data.keys())]
    data_check_string = "\n".join(check_parts)
    # Secret key = HMAC-SHA256(bot_token, key="WebAppData")
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(calculated_hash, hash_received):
        return None
    # Check auth_date freshness (optional, allow 1 day)
    try:
        auth_date = int(data.get("auth_date", "0"))
        if auth_date and abs(time.time() - auth_date) > 86400:
            # Still allow but could warn
            pass
    except Exception:
        pass
    # Extract user
    user_json = data.get("user")
    if not user_json:
        return None
    try:
        user = json.loads(unquote(user_json) if "%" in user_json else user_json)
        # parse_qsl already unquotes, so try direct
        if isinstance(user, str):
            user = json.loads(user)
        return user
    except Exception:
        # Try raw
        try:
            return json.loads(data.get("user", "{}"))
        except Exception:
            return None


class MiniAppAuthBody(BaseModel):
    initData: str


@router.post("/auth")
def miniapp_auth(body: MiniAppAuthBody, request: Request) -> dict[str, Any]:
    settings = load_settings()
    if not settings.telegram_bot_token:
        raise HTTPException(status_code=500, detail="telegram not configured")
    user = _validate_init_data(body.initData, settings.telegram_bot_token)
    if not user or not user.get("id"):
        raise HTTPException(status_code=401, detail="invalid initData")
    chat_id = user.get("id")
    # Also try to get chat_id from initData if present via query param? WebApp user id is the chat id for private chats
    # Ensure user exists (instant active)
    from app.telegram.bot import _ensure_telegram_user

    # Build from_user dict for ensure
    from_user = {
        "id": user.get("id"),
        "username": user.get("username"),
        "first_name": user.get("first_name") or "",
        "last_name": user.get("last_name") or "",
    }
    _ensure_telegram_user(settings, chat_id, from_user)
    # Fetch full user row
    urows = query(
        settings,
        "select id, telegram_chat_id, telegram_username, display_name, role, status from users where telegram_chat_id = %s or telegram_user_id = %s limit 1",
        (int(chat_id), int(chat_id)),
    )
    if not urows:
        raise HTTPException(status_code=500, detail="could not create user")
    u = urows[0]
    admin_id = getattr(settings, "admin_chat_id", "") or settings.telegram_chat_id
    is_admin = admin_id and str(chat_id) == str(admin_id)
    return {
        "ok": True,
        "user": {
            "id": str(u["id"]),
            "chat_id": int(chat_id),
            "username": u.get("telegram_username"),
            "display_name": u.get("display_name"),
            "role": u.get("role"),
            "is_admin": bool(is_admin),
        },
        "is_admin": bool(is_admin),
    }


@router.get("/me")
def miniapp_me(request: Request) -> dict[str, Any]:
    # Alternative: validate via header X-Telegram-Init-Data
    init_data = (
        request.headers.get("X-Telegram-Init-Data") or request.query_params.get("initData") or ""
    )
    settings = load_settings()
    user = _validate_init_data(init_data, settings.telegram_bot_token) if init_data else None
    if not user:
        raise HTTPException(status_code=401, detail="not authenticated via Mini App")
    chat_id = user.get("id")
    rows = query(
        settings,
        "select id, telegram_chat_id, telegram_username, display_name, role, status from users where telegram_chat_id = %s or telegram_user_id = %s limit 1",
        (int(chat_id), int(chat_id)),
    )
    if not rows:
        raise HTTPException(status_code=404, detail="user not found, tap /start first")
    u = rows[0]
    admin_id = getattr(settings, "admin_chat_id", "") or settings.telegram_chat_id
    is_admin = admin_id and str(chat_id) == str(admin_id)
    return {
        "user": {
            "id": str(u["id"]),
            "chat_id": int(chat_id),
            "role": u.get("role"),
            "is_admin": bool(is_admin),
        }
    }


def _get_user_from_init(request: Request) -> tuple[dict[str, Any], dict[str, Any]]:
    """Helper: validate initData from header/body and return (telegram_user, db_user_row)."""
    init_data = (
        request.headers.get("X-Telegram-Init-Data")
        or request.headers.get("x-telegram-init-data")
        or ""
    )
    # Also try JSON body for POST
    if not init_data:
        try:
            request.scope.get("body")  # not reliable, use query param fallback
        except Exception:
            pass
    settings = load_settings()
    # Try header first, then query param
    if not init_data:
        init_data = request.query_params.get("initData") or ""
    user = _validate_init_data(init_data, settings.telegram_bot_token) if init_data else None
    if not user or not user.get("id"):
        raise HTTPException(status_code=401, detail="invalid initData, open via Telegram Mini App")
    chat_id = user.get("id")
    rows = query(
        settings,
        "select id, telegram_chat_id, telegram_user_id, display_name, role, status from users where telegram_chat_id = %s or telegram_user_id = %s limit 1",
        (int(chat_id), int(chat_id)),
    )
    if not rows:
        # Auto-create like /start
        from app.telegram.bot import _ensure_telegram_user

        _ensure_telegram_user(settings, chat_id, user)
        rows = query(
            settings,
            "select id, telegram_chat_id, telegram_user_id, display_name, role, status from users where telegram_chat_id = %s or telegram_user_id = %s limit 1",
            (int(chat_id), int(chat_id)),
        )
        if not rows:
            raise HTTPException(status_code=500, detail="could not create user")
    return user, rows[0]


@router.get("/preferences")
def miniapp_get_preferences(request: Request) -> dict[str, Any]:
    settings = load_settings()
    # Try header
    init_data = (
        request.headers.get("X-Telegram-Init-Data")
        or request.headers.get("x-telegram-init-data")
        or request.query_params.get("initData")
        or ""
    )
    if not init_data:
        raise HTTPException(status_code=401, detail="missing initData")
    _user, db_user = _get_user_from_init(request)
    # Use the helper that also handles header case
    # Re-validate to get db_user
    _, db_user = _get_user_from_init(request)
    user_id = str(db_user["id"])
    rows = query(
        settings,
        "select roles, keywords, locations, seniority, excluded_companies, excluded_roles from preferences where user_id = %s",
        (user_id,),
    )
    if not rows:
        # Return empty (isolated, not inherited)
        return {
            "roles": [],
            "keywords": [],
            "locations": [],
            "seniority": [],
            "excluded_companies": [],
            "excluded_roles": [],
        }
    r = rows[0]
    return {
        "roles": r.get("roles") or [],
        "keywords": r.get("keywords") or [],
        "locations": r.get("locations") or [],
        "seniority": r.get("seniority") or [],
        "excluded_companies": r.get("excluded_companies") or [],
        "excluded_roles": r.get("excluded_roles") or [],
    }


def _require_admin(request: Request) -> tuple[dict[str, Any], dict[str, Any]]:
    """Validate initData and ensure caller is admin. Returns (telegram_user, db_user)."""
    init_data = (
        request.headers.get("X-Telegram-Init-Data")
        or request.headers.get("x-telegram-init-data")
        or request.query_params.get("initData")
        or ""
    )
    # Also try to read from JSON body if header missing (for POST with initData in body, caller should pass header)
    settings = load_settings()
    user = _validate_init_data(init_data, settings.telegram_bot_token) if init_data else None
    if not user or not user.get("id"):
        raise HTTPException(status_code=401, detail="admin initData required")
    chat_id = user.get("id")
    admin_id = getattr(settings, "admin_chat_id", "") or settings.telegram_chat_id
    if not admin_id or str(chat_id) != str(admin_id):
        raise HTTPException(status_code=403, detail="admin only")
    rows = query(
        settings,
        "select id, role from users where telegram_chat_id = %s or telegram_user_id = %s limit 1",
        (int(chat_id), int(chat_id)),
    )
    if not rows:
        raise HTTPException(status_code=403, detail="admin not found")
    return user, rows[0]


class MiniPrefsBody(BaseModel):
    initData: str = ""
    roles: list[str] = []
    keywords: list[str] = []
    locations: list[str] = []
    seniority: list[str] = []
    excluded_companies: list[str] = []
    excluded_roles: list[str] = []


@router.put("/preferences")
@router.post("/preferences")
def miniapp_put_preferences(body: MiniPrefsBody, request: Request) -> dict[str, Any]:
    settings = load_settings()
    # Prefer body.initData, fallback to header
    init_data = (
        body.initData
        or request.headers.get("X-Telegram-Init-Data")
        or request.headers.get("x-telegram-init-data")
        or ""
    )
    if not init_data:
        raise HTTPException(status_code=401, detail="missing initData")
    user = _validate_init_data(init_data, settings.telegram_bot_token)
    if not user or not user.get("id"):
        raise HTTPException(status_code=401, detail="invalid initData")
    chat_id = user.get("id")
    rows = query(
        settings,
        "select id from users where telegram_chat_id = %s or telegram_user_id = %s limit 1",
        (int(chat_id), int(chat_id)),
    )
    if not rows:
        from app.telegram.bot import _ensure_telegram_user

        _ensure_telegram_user(settings, chat_id, user)
        rows = query(
            settings,
            "select id from users where telegram_chat_id = %s or telegram_user_id = %s limit 1",
            (int(chat_id), int(chat_id)),
        )
    user_id = str(rows[0]["id"])
    # Upsert isolated per user
    supabase = __import__("app.db", fromlist=["get_supabase"]).get_supabase(settings)
    supabase.table("preferences").upsert(
        {
            "user_id": user_id,
            "roles": body.roles,
            "keywords": body.keywords,
            "locations": body.locations,
            "seniority": body.seniority,
            "excluded_companies": body.excluded_companies,
            "excluded_roles": body.excluded_roles,
        },
        on_conflict="user_id",
    ).execute()
    return {"ok": True}


@router.get("/admin/users")
def miniapp_admin_users(request: Request) -> dict[str, Any]:
    _require_admin(request)
    settings = load_settings()
    rows = query(
        settings,
        """
        select u.id, u.telegram_chat_id, u.telegram_username, u.display_name, u.role, u.status,
               u.created_at, u.last_login_at,
               p.roles, p.keywords, p.locations
        from users u
        left join preferences p on p.user_id = u.id
        order by u.created_at desc
        limit 100
        """,
    )
    for r in rows:
        for k in ("created_at", "last_login_at"):
            if r.get(k) and hasattr(r[k], "isoformat"):
                r[k] = r[k].isoformat()
    return {"users": rows}


class MiniRoleBody(BaseModel):
    initData: str = ""
    role: str


@router.put("/admin/users/{user_id}/role")
def miniapp_admin_set_role(user_id: str, body: MiniRoleBody, request: Request) -> dict[str, Any]:
    _require_admin(request)
    if body.role not in ("user", "privileged", "admin"):
        raise HTTPException(status_code=422, detail="role must be user|privileged|admin")
    settings = load_settings()
    # Guard owner
    from app.config import DEFAULT_USER_ID

    if user_id.lower() == DEFAULT_USER_ID.lower():
        raise HTTPException(status_code=403, detail="owner cannot be changed")
    from app.users import admin_update_user

    try:
        row = admin_update_user(settings, user_id, {"role": body.role})
    except LookupError:
        raise HTTPException(status_code=404, detail="user not found")
    return {"ok": True, "user": row}


class MiniDelayBody(BaseModel):
    initData: str = ""
    privileged_delay_minutes: int | None = None
    normal_delay_minutes: int | None = None


@router.get("/admin/delays")
def miniapp_admin_get_delays(request: Request) -> dict[str, Any]:
    _require_admin(request)
    settings = load_settings()
    rows = query(
        settings,
        "select key, value from app_settings where key in ('privileged_delay_minutes','normal_delay_minutes')",
    )
    m = {r["key"]: r["value"] for r in rows}

    def _as_int(v, d):
        try:
            return int(v) if isinstance(v, int) else int(str(v).strip('"'))
        except Exception:
            return d

    return {
        "privileged_delay_minutes": _as_int(m.get("privileged_delay_minutes"), 30),
        "normal_delay_minutes": _as_int(m.get("normal_delay_minutes"), 360),
    }


@router.put("/admin/delays")
def miniapp_admin_set_delays(body: MiniDelayBody, request: Request) -> dict[str, Any]:
    # Also allow header initData if body.initData empty
    if not body.initData:
        # Try header
        hdr = (
            request.headers.get("X-Telegram-Init-Data")
            or request.headers.get("x-telegram-init-data")
            or ""
        )
        body.initData = hdr
    _require_admin(request)
    settings = load_settings()
    supabase = __import__("app.db", fromlist=["get_supabase"]).get_supabase(settings)
    from datetime import UTC, datetime

    if body.privileged_delay_minutes is not None:
        if not 0 <= body.privileged_delay_minutes <= 10080:
            raise HTTPException(status_code=422, detail="privileged delay 0..10080")
        supabase.table("app_settings").upsert(
            {
                "key": "privileged_delay_minutes",
                "value": body.privileged_delay_minutes,
                "updated_at": datetime.now(UTC).isoformat(),
            },
            on_conflict="key",
        ).execute()
    if body.normal_delay_minutes is not None:
        if not 0 <= body.normal_delay_minutes <= 10080:
            raise HTTPException(status_code=422, detail="normal delay 0..10080")
        supabase.table("app_settings").upsert(
            {
                "key": "normal_delay_minutes",
                "value": body.normal_delay_minutes,
                "updated_at": datetime.now(UTC).isoformat(),
            },
            on_conflict="key",
        ).execute()
    return {"ok": True}
