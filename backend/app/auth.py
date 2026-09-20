"""Authentication: signed session cookies and the FastAPI dependencies used by every route.

Compat mode: when JOBQUEST_REQUIRE_AUTH is false (default), unauthenticated
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
from datetime import UTC, datetime
from typing import Annotated, Any

from fastapi import Depends, HTTPException, Request

from app.config import Settings, load_settings
from app.db import query

SESSION_COOKIE = "jobquest_session"

PBKDF2_ITERATIONS = 600_000  # OWASP 2023: 600k for SHA256
PBKDF2_MIN_ITERATIONS = 480_000  # accept legacy hashes for verification + upgrade

# Top 20 breached/common passwords (subset of OWASP SecLists 10k) — extend as needed
COMMON_PASSWORDS = {
    "password",
    "123456",
    "123456789",
    "qwerty",
    "password123",
    "admin",
    "welcome",
    "12345678",
    "abc123",
    "letmein",
    "monkey",
    "dragon",
    "12345",
    "password1",
    "1234567",
    "qwerty123",
    "admin123",
    "welcome123",
    "iloveyou",
    "000000",
}


# ---------- passwords (stdlib PBKDF2-HMAC-SHA256; no new dependencies) ----------


def hash_password(password: str, iterations: int = PBKDF2_ITERATIONS) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    return f"pbkdf2_sha256${iterations}${salt.hex()}${digest.hex()}"


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


def needs_rehash(password_hash: str | None) -> bool:
    """True if hash uses old iteration count and should be upgraded on next login."""
    try:
        scheme, iterations, _, _ = (password_hash or "").split("$")
        if scheme != "pbkdf2_sha256":
            return True
        return int(iterations) < PBKDF2_ITERATIONS
    except Exception:
        return True


def validate_password_strength(
    password: str, *, email: str | None = None, display_name: str | None = None
) -> list[str]:
    """MNC/OWASP ASVS 2.1: 12-128 chars, 3/4 categories, not common/breached, not containing user identity."""
    errors: list[str] = []
    pwd = password or ""
    if len(pwd) < 12:
        errors.append("at least 12 characters")
    if len(pwd) > 128:
        errors.append("at most 128 characters")
    has_upper = any(c.isupper() for c in pwd)
    has_lower = any(c.islower() for c in pwd)
    has_digit = any(c.isdigit() for c in pwd)
    has_special = any(c in "!@#$%^&*()-_=+[]{}|;:',.<>?/`~\"\\ " for c in pwd)
    categories = sum([has_upper, has_lower, has_digit, has_special])
    if categories < 3:
        errors.append("at least 3 of: upper, lower, number, special character")
    if pwd.lower() in COMMON_PASSWORDS:
        errors.append("too common — choose a less predictable password")
    # not containing email local-part or display name
    if email:
        local = email.split("@")[0].lower()
        if local and len(local) >= 3 and local in pwd.lower():
            errors.append("must not contain part of your email")
    if display_name:
        for part in display_name.strip().split():
            if len(part) >= 3 and part.lower() in pwd.lower():
                errors.append("must not contain your name")
                break
    if errors:
        return ["password needs " + ", ".join(errors)]
    return []


def password_strength_score(password: str) -> int:
    """0-4 score for UX meter (length + variety). Not a security gate, just guidance."""
    pwd = password or ""
    score = 0
    if len(pwd) >= 12:
        score += 1
    if any(c.isupper() for c in pwd) and any(c.islower() for c in pwd):
        score += 1
    if any(c.isdigit() for c in pwd):
        score += 1
    if any(c in "!@#$%^&*()-_=+[]{}|;:',.<>?/`~" for c in pwd):
        score += 1
    return min(score, 4)


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


# ---------- simple in-memory rate limiter (per process; good enough here) ----------

_rate_buckets: dict[str, list[float]] = {}


def rate_limit(key: str, max_events: int, window_seconds: int) -> bool:
    """True if allowed, False if over the limit for this window."""
    now = time.time()
    # opportunistic cleanup to bound memory
    if len(_rate_buckets) > 2000:
        for k in list(_rate_buckets.keys())[:500]:
            _rate_buckets.pop(k, None)
    bucket = [t for t in _rate_buckets.get(key, []) if now - t < window_seconds]
    if len(bucket) >= max_events:
        _rate_buckets[key] = bucket
        return False
    bucket.append(now)
    _rate_buckets[key] = bucket
    return True


def is_valid_email(email: str) -> bool:
    """RFC 5322-ish + length checks. Rejects control chars, consecutive dots, etc."""
    import re

    email = (email or "").strip()
    if not email or len(email) > 254:
        return False
    if email.count("@") != 1:
        return False
    local, domain = email.split("@", 1)
    if not local or not domain or len(local) > 64 or len(domain) > 253:
        return False
    if ".." in email or email.startswith(".") or email.endswith("."):
        return False
    # local: allow alphanum + ._%+- but not leading/trailing dot; domain: labels 1-63 chars
    pattern = r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$"
    if not re.match(pattern, email):
        return False
    return bool(re.match(r"^[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$", domain))


def sanitize_display_name(name: str) -> str:
    """Trim, collapse spaces, 2-50 chars, allow letters/numbers/space .-'_ . No HTML."""
    import re

    raw = (name or "").strip()
    raw = re.sub(r"\s+", " ", raw)
    if len(raw) < 2:
        raise ValueError("display name must be at least 2 characters")
    if len(raw) > 50:
        raise ValueError("display name must be at most 50 characters")
    if not re.match(r"^[A-Za-z0-9 .'_@\-]+$", raw):
        raise ValueError("display name contains invalid characters")
    # strip any < > to prevent HTML injection even though React escapes
    if "<" in raw or ">" in raw:
        raise ValueError("display name must not contain < or >")
    return raw


def log_auth_event(
    settings: Settings,
    *,
    email: str | None,
    user_id: str | None,
    event_type: str,
    ip: str | None,
    user_agent: str | None = None,
) -> None:
    """Best-effort audit log; never raises."""
    try:
        query(
            settings,
            "insert into auth_events (user_id, email, event_type, ip, user_agent) values (%s::uuid, %s, %s, %s, %s)",
            (
                user_id,
                (email or "")[:254] if email else None,
                event_type,
                (ip or "")[:64],
                (user_agent or "")[:256] if user_agent else None,
            ),
        )
    except Exception:
        pass


# ---------- FastAPI dependencies ----------

_owner_cache: dict[str, UserCtx] = {}
_ephemeral_secret: str | None = None


def session_secret(settings: Settings) -> str:
    """Configured SECRET_KEY, or an ephemeral per-process fallback when auth
    enforcement is off (sessions then die on restart — acceptable for the
    single-owner compat mode; JOBQUEST_REQUIRE_AUTH=true requires a real key)."""
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
    # support both __Host- prefix and legacy name (rolling upgrade)
    token = request.cookies.get(f"__Host-{SESSION_COOKIE}") or request.cookies.get(SESSION_COOKIE)
    if token:
        user_id = verify_session_token(session_secret(settings), token)
        if user_id:
            ctx = load_user_ctx(settings, user_id)
            if ctx is None:
                raise HTTPException(status_code=401, detail="account no longer exists")
            if ctx.status == "disabled":
                raise HTTPException(status_code=403, detail="account disabled")
            # enforce lockout at session resolve as well (in case lock happened after cookie issue)
            try:
                rows = query(
                    settings, "select lockout_until from users where id = %s::uuid", (user_id,)
                )
                if rows and rows[0].get("lockout_until"):
                    lu = rows[0]["lockout_until"]
                    if isinstance(lu, str):
                        lu = datetime.fromisoformat(lu)
                    if lu and lu > datetime.now(UTC):
                        raise HTTPException(
                            status_code=423,
                            detail="account temporarily locked due to repeated failed logins",
                        )
            except HTTPException:
                raise
            except Exception:
                pass
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
    # __Host- prefix requires Secure + Path=/ + no Domain — use only when Secure is on
    cookie_name = f"__Host-{SESSION_COOKIE}" if settings.session_cookie_secure else SESSION_COOKIE
    response.set_cookie(
        cookie_name,
        token,
        httponly=True,
        samesite="lax",
        secure=settings.session_cookie_secure,
        max_age=settings.session_ttl_hours * 3600,
        path="/",
    )
    # keep legacy name for rolling upgrade (read checks both)
    if settings.session_cookie_secure:
        response.set_cookie(
            SESSION_COOKIE,
            token,
            httponly=True,
            samesite="lax",
            secure=True,
            max_age=settings.session_ttl_hours * 3600,
            path="/",
        )


def clear_session_cookie(response: Any, settings: Settings | None = None) -> None:
    # clear both names and __Host- variant
    for name in (SESSION_COOKIE, f"__Host-{SESSION_COOKIE}"):
        response.delete_cookie(name, path="/")


def resolve_delivery_identity(settings: Settings, user_id: str) -> dict[str, Any]:
    rows = query(
        settings,
        "select telegram_chat_id, email from users where id = %s::uuid",
        (user_id,),
    )
    return rows[0] if rows else {}
