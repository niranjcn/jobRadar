"""Authentication: signed session cookies, OTP login codes, Telegram
MiniApp initData verification, and the FastAPI dependencies used by every
route.

Compat mode: when JOBRADAR_REQUIRE_AUTH is false (default), unauthenticated
requests resolve to the owner account so the existing single-user frontend
and bot keep working unchanged. Flip the flag to enforce real auth.
"""

import base64
import hashlib
import hmac
import json
import secrets
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Annotated, Any

from fastapi import Depends, HTTPException, Request
from supabase import Client

from app.config import Settings, load_settings
from app.db import query

SESSION_COOKIE = "jobradar_session"
OTP_TTL_MINUTES = 5
OTP_MAX_ATTEMPTS = 5

PBKDF2_ITERATIONS = 480_000


# ---------- passwords (stdlib PBKDF2-HMAC-SHA256; no new dependencies) ----------


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password_hash: str | None, password: str) -> bool:
    """Constant-time verification. Returns False for null/legacy hashes."""
    try:
        scheme, iterations, salt_hex, digest_hex = (password_hash or "").split("$")
        if scheme != "pbkdf2_sha256":
            return False
        expected = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), bytes.fromhex(salt_hex), int(iterations)
        )
        return hmac.compare_digest(expected.hex(), digest_hex)
    except (ValueError, AttributeError):
        return False


def validate_password_strength(password: str) -> list[str]:
    """Human-readable violations; empty list means acceptable."""
    errors: list[str] = []
    if len(password or "") < 8:
        errors.append("at least 8 characters")
    if not any(c.isdigit() for c in password or ""):
        errors.append("at least one number")
    if not any(c.isalpha() for c in password or ""):
        errors.append("at least one letter")
    if errors:
        return ["password needs " + ", ".join(errors)]
    return []


# ---------- request context ----------


@dataclass
class UserCtx:
    id: str
    email: str | None = None
    display_name: str = ""
    role: str = "user"
    status: str = "approved"
    capabilities: list[str] = field(default_factory=list)
    alert_delay_minutes: int = 0
    access_locked: bool = False
    is_owner: bool = False
    telegram_chat_id: int | None = None
    anonymous: bool = False

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"


def _ctx_from_row(row: dict[str, Any], *, anonymous: bool = False) -> UserCtx:
    return UserCtx(
        id=str(row["id"]),
        email=row.get("email"),
        display_name=row.get("display_name") or "",
        role=row.get("role") or "user",
        status=row.get("status") or "approved",
        capabilities=row.get("capabilities") or [],
        alert_delay_minutes=int(row.get("alert_delay_minutes") or 0),
        access_locked=bool(row.get("access_locked")),
        is_owner=bool(row.get("is_owner")),
        telegram_chat_id=row.get("telegram_chat_id"),
        anonymous=anonymous,
    )


# ---------- signed tokens (stdlib only; no new dependencies) ----------


def _b64e(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _b64d(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def sign_session_token(
    secret_key: str, user_id: str, ttl_hours: int, now: float | None = None
) -> str:
    issued = now if now is not None else time.time()
    payload = json.dumps({"uid": user_id, "exp": int(issued + ttl_hours * 3600)})
    body = _b64e(payload.encode())
    sig = hmac.new(secret_key.encode(), body.encode(), hashlib.sha256).hexdigest()
    return f"{body}.{sig}"


def verify_session_token(secret_key: str, token: str, now: float | None = None) -> str | None:
    """Return the user id for a valid, unexpired token; None otherwise."""
    try:
        body, sig = token.split(".", 1)
        expected = hmac.new(secret_key.encode(), body.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return None
        payload = json.loads(_b64d(body))
        exp = float(payload["exp"])
        if now is None:
            now = time.time()
        if exp < now:
            return None
        return str(payload["uid"])
    except Exception:
        return None


# ---------- Telegram Login Widget ----------


def verify_telegram_widget(
    bot_token: str, data: dict[str, Any], max_age_seconds: int = 86400
) -> dict[str, Any] | None:
    """Verify Telegram Login Widget payload per https://core.telegram.org/widgets/login.

    Input `data` is the dict received from the widget's data-onauth callback
    (keys: id, first_name, last_name, username, photo_url, auth_date, hash).
    Returns the normalized user dict on success, None on failure.

    Scheme: secret_key = SHA256(bot_token)
            data_check_string = '\\n'.join(f\"{k}={v}\" for k,v in sorted(data) if k != 'hash')
            hash = HMAC-SHA256(data_check_string, secret_key)
    """
    try:
        if not bot_token or not isinstance(data, dict):
            return None
        provided_hash = str(data.get("hash") or "")
        if not provided_hash:
            return None
        # Build check string from all fields except hash, sorted by key.
        # Telegram spec requires string values; ints must be stringified.
        pairs = [(str(k), str(v)) for k, v in data.items() if k != "hash"]
        pairs.sort(key=lambda kv: kv[0])
        data_check_string = "\n".join(f"{k}={v}" for k, v in pairs)
        secret_key = hashlib.sha256(bot_token.encode()).digest()
        calculated = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(calculated, provided_hash):
            return None
        # Freshness check on auth_date
        try:
            auth_date = int(str(data.get("auth_date") or "0"))
        except ValueError:
            auth_date = 0
        if auth_date and time.time() - auth_date > max_age_seconds:
            return None
        # Normalize: id is required; other fields optional
        tg_id = data.get("id")
        if tg_id is None:
            return None
        try:
            tid = int(tg_id)
        except (TypeError, ValueError):
            return None
        return {
            "id": tid,
            "first_name": str(data.get("first_name") or ""),
            "last_name": str(data.get("last_name") or ""),
            "username": str(data.get("username") or "") or None,
            "photo_url": str(data.get("photo_url") or "") or None,
            "auth_date": auth_date,
        }
    except Exception:
        return None


# ---------- Telegram deep-link nonce (bot login) ----------

TELEGRAM_NONCE_TTL_MINUTES = 5
TELEGRAM_NONCE_BYTES = 24  # 48 hex chars


def create_telegram_login_token(
    settings: Settings, initiated_by_ip: str | None = None
) -> dict[str, Any]:
    """Create a one-time nonce for bot deep-link login. Returns row dict with token + expires_at."""
    token = secrets.token_hex(TELEGRAM_NONCE_BYTES)
    expires_at = (datetime.now(UTC) + timedelta(minutes=TELEGRAM_NONCE_TTL_MINUTES)).isoformat()
    rows = query(
        settings,
        "insert into telegram_login_tokens (token, initiated_by_ip, expires_at) values (%s, %s, %s::timestamptz) returning id, token, expires_at, created_at",
        (token, initiated_by_ip, expires_at),
    )
    if not rows:
        raise RuntimeError("could not create telegram login token")
    return rows[0]


def get_telegram_login_token(settings: Settings, token: str) -> dict[str, Any] | None:
    rows = query(
        settings,
        "select id, token, telegram_user_id, telegram_chat_id, telegram_username, telegram_first_name, telegram_last_name, telegram_photo_url, initiated_by_ip, created_at, expires_at, authenticated_at, consumed_at, consumed_by from telegram_login_tokens where token = %s",
        (token,),
    )
    return rows[0] if rows else None


def authenticate_telegram_login_token(
    settings: Settings,
    token: str,
    tg_identity: dict[str, Any],
) -> bool:
    """Mark a pending nonce as authenticated by the Telegram bot. Idempotent once authenticated."""
    # Only authenticate pending (not yet authenticated, not expired, not consumed)
    rows = query(
        settings,
        """
        update telegram_login_tokens
        set telegram_user_id = %s,
            telegram_chat_id = %s,
            telegram_username = %s,
            telegram_first_name = %s,
            telegram_last_name = %s,
            telegram_photo_url = %s,
            authenticated_at = now()
        where token = %s
          and authenticated_at is null
          and consumed_at is null
          and expires_at > now()
        returning id
        """,
        (
            tg_identity.get("id"),
            tg_identity.get("chat_id") or tg_identity.get("id"),
            tg_identity.get("username"),
            tg_identity.get("first_name"),
            tg_identity.get("last_name"),
            tg_identity.get("photo_url"),
            token,
        ),
    )
    return bool(rows)


def consume_telegram_login_token(
    settings: Settings, token: str, consumed_by: str | None = None
) -> dict[str, Any] | None:
    """Consume an authenticated nonce (single-use). Returns the row if successful."""
    rows = query(
        settings,
        """
        update telegram_login_tokens
        set consumed_at = now(),
            consumed_by = %s::uuid
        where token = %s
          and authenticated_at is not null
          and consumed_at is null
          and expires_at > now()
        returning id, token, telegram_user_id, telegram_chat_id, telegram_username, telegram_first_name, telegram_last_name, telegram_photo_url
        """,
        (consumed_by, token),
    )
    return rows[0] if rows else None


def purge_expired_telegram_login_tokens(settings: Settings) -> int:
    """Delete expired unconsumed tokens older than 1 day (housekeeping). Returns count."""
    rows = query(
        settings,
        "delete from telegram_login_tokens where expires_at < now() - interval '1 day' returning id",
    )
    return len(rows) if rows else 0


# ---------- Telegram MiniApp initData ----------


def verify_init_data(
    bot_token: str, init_data: str, max_age_seconds: int = 86400
) -> dict[str, Any] | None:
    """Verify Telegram WebApp initData per the documented HMAC-SHA256 scheme.
    Returns the parsed data dict (with 'user') on success."""
    try:
        pairs = sorted(pair.split("=", 1) for pair in init_data.split("&"))
        by_key = dict(pairs)
        # The HMAC covers every field EXCEPT the hash itself (Telegram spec).
        data_check_string = "\n".join(f"{k}={v}" for k, v in pairs if k != "hash")
        provided_hash = by_key.get("hash", "")
        secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
        calculated = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        if not provided_hash or not hmac.compare_digest(calculated, provided_hash):
            return None
        auth_date = int(dict(pairs).get("auth_date", "0"))
        if auth_date and time.time() - auth_date > max_age_seconds:
            return None
        return json.loads(_b64d(dict(pairs).get("user", "") or "e30="))
    except Exception:
        return None


# ---------- OTP codes ----------


def generate_otp() -> str:
    return "".join(secrets.choice("0123456789") for _ in range(6))


def issue_login_code(settings: Settings, supabase: Client, user_id: str, channel: str) -> str:
    code = generate_otp()
    expires_at = (datetime.now(UTC) + timedelta(minutes=OTP_TTL_MINUTES)).isoformat()
    # Invalidate any outstanding codes for this user+channel first.
    supabase.table("login_codes").update({"used_at": datetime.now(UTC).isoformat()}).eq(
        "user_id", user_id
    ).eq("channel", channel).is_("used_at", "null").execute()
    supabase.table("login_codes").insert(
        {"user_id": user_id, "channel": channel, "code": code, "expires_at": expires_at}
    ).execute()
    return code


def consume_login_code(
    settings: Settings, supabase: Client, user_id: str, channel: str, code: str
) -> bool:
    rows = (
        supabase.table("login_codes")
        .select("id, code, expires_at, attempts, used_at")
        .eq("user_id", user_id)
        .eq("channel", channel)
        .is_("used_at", "null")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    if not rows.data:
        return False
    row = rows.data[0]
    expires_at = row["expires_at"]
    if isinstance(expires_at, str):
        try:
            expires_at = datetime.fromisoformat(expires_at)
        except ValueError:
            return False
    valid_code = secrets.compare_digest(str(row["code"]), str(code))
    fresh = isinstance(expires_at, datetime) and expires_at > datetime.now(UTC)
    if not (valid_code and fresh and row.get("used_at") is None):
        supabase.table("login_codes").update({"attempts": int(row.get("attempts") or 0) + 1}).eq(
            "id", row["id"]
        ).execute()
        return False
    supabase.table("login_codes").update({"used_at": datetime.now(UTC).isoformat()}).eq(
        "id", row["id"]
    ).execute()
    return True


# ---------- simple in-memory rate limiter (per process; good enough here) ----------

_rate_buckets: dict[str, list[float]] = {}


def rate_limit(key: str, max_events: int, window_seconds: int) -> bool:
    """True if allowed, False if over the limit for this window."""
    now = time.time()
    bucket = [t for t in _rate_buckets.get(key, []) if now - t < window_seconds]
    if len(bucket) >= max_events:
        _rate_buckets[key] = bucket
        return False
    bucket.append(now)
    _rate_buckets[key] = bucket
    return True


# ---------- FastAPI dependencies ----------

_owner_cache: dict[str, UserCtx] = {}
_ephemeral_secret: str | None = None


def session_secret(settings: Settings) -> str:
    """Configured SECRET_KEY, or an ephemeral per-process fallback when auth
    enforcement is off (sessions then die on restart — acceptable for the
    single-owner compat mode; JOBRADAR_REQUIRE_AUTH=true requires a real key)."""
    global _ephemeral_secret
    if settings.secret_key:
        return settings.secret_key
    if settings.require_auth:
        raise HTTPException(status_code=500, detail="SECRET_KEY must be configured")
    if _ephemeral_secret is None:
        import secrets as _secrets

        _ephemeral_secret = _secrets.token_hex(32)
        print("auth: SECRET_KEY not set — using an ephemeral in-process session secret")
    return _ephemeral_secret


def get_settings_dep() -> Settings:
    return load_settings()


def load_user_ctx(settings: Settings, user_id: str) -> UserCtx | None:
    from app.users import fetch_user

    rows = fetch_user(settings, user_id)
    if not rows:
        return None
    return _ctx_from_row(rows[0])


def owner_ctx(settings: Settings) -> UserCtx:
    cached = _owner_cache.get("owner")
    if cached:
        return cached
    from app.users import ensure_owner

    row = ensure_owner(settings)
    ctx = _ctx_from_row(row, anonymous=True)
    _owner_cache["owner"] = ctx
    return ctx


def reset_owner_cache() -> None:
    _owner_cache.pop("owner", None)


def get_current_user(request: Request) -> UserCtx:
    """Resolve the requesting identity.

    require_auth off (default): anonymous requests act as the owner — the
    pre-subscription behavior, byte for byte.
    """
    settings = get_settings_dep()
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        user_id = verify_session_token(session_secret(settings), token)
        if user_id:
            ctx = load_user_ctx(settings, user_id)
            if ctx is None:
                raise HTTPException(status_code=401, detail="account no longer exists")
            if ctx.status == "disabled":
                raise HTTPException(status_code=403, detail="account disabled")
            return ctx
        if settings.require_auth:
            raise HTTPException(status_code=401, detail="invalid or expired session")
    else:
        if settings.require_auth:
            raise HTTPException(status_code=401, detail="authentication required")
    return owner_ctx(settings)


def get_current_admin(user: Annotated[UserCtx, Depends(get_current_user)]) -> UserCtx:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="admin access required")
    return user


def require_product_access(user: Annotated[UserCtx, Depends(get_current_user)]) -> UserCtx:
    """Dependency for subscriber-facing data routes: blocks locked/pending
    accounts once auth enforcement is on. No-op in compat mode."""
    settings = get_settings_dep()
    if not settings.require_auth or user.anonymous:
        return user
    if user.status != "approved" or user.access_locked:
        raise HTTPException(status_code=402, detail="account locked: pay or redeem a coupon")
    return user


def set_session_cookie(response: Any, settings: Settings, user_id: str) -> None:
    token = sign_session_token(session_secret(settings), user_id, settings.session_ttl_hours)
    response.set_cookie(
        SESSION_COOKIE,
        token,
        httponly=True,
        samesite="lax",
        secure=settings.session_cookie_secure,
        max_age=settings.session_ttl_hours * 3600,
    )


def clear_session_cookie(response: Any) -> None:
    response.delete_cookie(SESSION_COOKIE)


def resolve_delivery_identity(settings: Settings, user_id: str) -> dict[str, Any]:
    rows = query(
        settings,
        "select telegram_chat_id, email from users where id = %s::uuid",
        (user_id,),
    )
    return rows[0] if rows else {}
