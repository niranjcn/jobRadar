"""Auth endpoints: email/password registration & login with admin approval."""

from datetime import UTC, datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel

from app.auth import (
    UserCtx,
    clear_session_cookie,
    get_current_user,
    is_valid_email,
    log_auth_event,
    rate_limit,
    sanitize_display_name,
    set_session_cookie,
    validate_password_strength,
)
from app.config import load_settings
from app.db import get_supabase, query
from app.users import (
    create_registered_user,
    fetch_user,
    fetch_user_by_email,
    touch_login,
    update_user_profile,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _me_payload(ctx: UserCtx) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "id": ctx.id,
        "email": ctx.email,
        "display_name": getattr(ctx, "display_name", "") or "",
        "role": ctx.role,
        "status": ctx.status,
        "capabilities": ctx.capabilities,
        "alert_delay_minutes": ctx.alert_delay_minutes,
        "access_locked": ctx.access_locked,
        "is_owner": ctx.is_owner,
        "telegram_chat_id": ctx.telegram_chat_id,
        "telegram_linked": ctx.telegram_chat_id is not None,
        "anonymous": ctx.anonymous,
    }
    if not ctx.anonymous:
        settings = load_settings()
        from app.users import fetch_user

        rows = fetch_user(settings, ctx.id)
        payload["has_password"] = bool(rows[0].get("password_hash") if rows else None)
        payload["telegram_chat_id"] = (
            rows[0].get("telegram_chat_id") if rows else ctx.telegram_chat_id
        )
        payload["telegram_linked"] = payload["telegram_chat_id"] is not None
        payload["needs_onboarding"] = not bool(rows[0].get("email") if rows else True)
        from app.access import active_subscription

        sub = active_subscription(settings, ctx.id)
        payload["subscription"] = sub
    return payload


class RegisterBody(BaseModel):
    email: str
    display_name: str = ""
    password: str
    accept_terms: bool = False


@router.post("/register", status_code=201)
def register(body: RegisterBody, request: Request, response: Response) -> dict:
    settings = load_settings()
    ip = request.client.host if request.client else "unknown"
    ua = request.headers.get("user-agent", "")[:256]
    if not rate_limit(f"register:{ip}", max_events=5, window_seconds=3600):
        raise HTTPException(status_code=429, detail="too many registrations, try again later (1h)")
    email = (body.email or "").strip().lower()
    if not is_valid_email(email):
        raise HTTPException(status_code=422, detail="enter a valid email address")
    # DPDP Act 2023: explicit, unticked consent — server-enforced, never implied.
    if not body.accept_terms:
        raise HTTPException(
            status_code=422, detail="you must accept the Terms of Service and Privacy Policy"
        )
    # display_name: MNC - 2-50 chars, filtered
    try:
        display_name = (
            sanitize_display_name(body.display_name)
            if body.display_name.strip()
            else email.split("@")[0]
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    if not body.password:
        raise HTTPException(status_code=422, detail="password is required")
    problems = validate_password_strength(body.password, email=email, display_name=display_name)
    if problems:
        raise HTTPException(status_code=422, detail=problems[0])
    supabase = get_supabase(settings)
    try:
        row = create_registered_user(
            settings,
            supabase,
            email=email,
            display_name=display_name,
            password=body.password,
        )
    except ValueError as exc:
        # Use generic timing to reduce enumeration, but still 409 for UX (admin needs to know duplicate)
        log_auth_event(
            settings, email=email, user_id=None, event_type="register", ip=ip, user_agent=ua
        )
        raise HTTPException(status_code=409, detail=str(exc))
    log_auth_event(
        settings, email=email, user_id=str(row["id"]), event_type="register", ip=ip, user_agent=ua
    )
    # Pending accounts get a session but product access is blocked until admin approves
    set_session_cookie(response, settings, row["id"])
    payload = _me_payload(_ctx_of(row))
    return {
        "ok": True,
        "status": row.get("status"),
        "access_locked": row.get("access_locked"),
        "user_id": row["id"],
        **payload,
    }


def _ctx_of(row: dict[str, Any]) -> UserCtx:
    return UserCtx(
        id=str(row["id"]),
        email=row.get("email"),
        display_name=row.get("display_name") or "",
        role=row.get("role") or "user",
        status=row.get("status") or "pending",
        capabilities=row.get("capabilities") or [],
        alert_delay_minutes=int(row.get("alert_delay_minutes") or 0),
        access_locked=bool(row.get("access_locked")),
        is_owner=bool(row.get("is_owner")),
        telegram_chat_id=row.get("telegram_chat_id"),
    )


class PasswordLoginBody(BaseModel):
    email: str
    password: str


@router.post("/login-password")
def login_password(body: PasswordLoginBody, request: Request, response: Response) -> dict:
    settings = load_settings()
    ip = request.client.host if request.client else "unknown"
    ua = request.headers.get("user-agent", "")[:256]
    email_norm = (body.email or "").strip().lower()
    if not is_valid_email(email_norm):
        raise HTTPException(status_code=422, detail="enter a valid email address")
    # Coarse per-IP bucket first: bounds total PBKDF2 CPU per IP even when the
    # attacker rotates emails (each rotation would otherwise get a fresh bucket).
    if not rate_limit(f"pwd-ip:{ip}", max_events=30, window_seconds=300):
        raise HTTPException(status_code=429, detail="too many attempts, try again shortly (5 min)")
    if not rate_limit(f"pwd:{ip}:{email_norm}", max_events=10, window_seconds=300):
        raise HTTPException(status_code=429, detail="too many attempts, try again shortly (5 min)")
    rows = fetch_user_by_email(settings, email_norm)
    invalid = HTTPException(status_code=401, detail="invalid email or password")
    if not rows:
        from app.auth import hash_password

        hash_password(body.password)
        log_auth_event(
            settings,
            email=email_norm,
            user_id=None,
            event_type="login_failure",
            ip=ip,
            user_agent=ua,
        )
        raise invalid
    user = rows[0]
    # lockout check (MNC: 5 failures → 15 min lock, exponential)
    lockout_until = user.get("lockout_until")
    if lockout_until:
        from datetime import UTC, datetime

        try:
            lu = lockout_until if isinstance(lockout_until, str) else str(lockout_until)
            lu_dt = datetime.fromisoformat(lu) if isinstance(lu, str) else lockout_until
            if lu_dt and lu_dt.tzinfo is None:
                lu_dt = lu_dt.replace(tzinfo=UTC)
            if lu_dt and lu_dt > datetime.now(UTC):
                log_auth_event(
                    settings,
                    email=email_norm,
                    user_id=str(user["id"]),
                    event_type="lockout",
                    ip=ip,
                    user_agent=ua,
                )
                raise HTTPException(
                    status_code=423,
                    detail="account temporarily locked — too many failed attempts, try again in 15 minutes",
                )
        except HTTPException:
            raise
        except Exception:
            pass
    from app.auth import hash_password, needs_rehash, verify_password

    if not verify_password(user.get("password_hash"), body.password):
        # increment failure, lock if needed
        try:
            fails = int(user.get("failed_login_attempts") or 0) + 1
            # lock after 5 fails within window
            if fails >= 5:
                query(
                    settings,
                    "update users set failed_login_attempts=%s, last_failed_at=now(), lockout_until=now() + interval '15 minutes', updated_at=now() where id=%s::uuid",
                    (fails, user["id"]),
                )
            else:
                query(
                    settings,
                    "update users set failed_login_attempts=%s, last_failed_at=now(), updated_at=now() where id=%s::uuid",
                    (fails, user["id"]),
                )
        except Exception:
            pass
        log_auth_event(
            settings,
            email=email_norm,
            user_id=str(user["id"]),
            event_type="login_failure",
            ip=ip,
            user_agent=ua,
        )
        raise invalid
    # success: check status before clearing lockout
    if user.get("status") == "disabled":
        raise HTTPException(status_code=403, detail="account disabled")
    if user.get("status") == "pending":
        raise HTTPException(status_code=403, detail="account pending admin approval")
    # rehash if old iterations
    if needs_rehash(user.get("password_hash")):
        try:
            new_hash = hash_password(body.password)
            query(
                settings,
                "update users set password_hash=%s, password_changed_at=now(), updated_at=now() where id=%s::uuid",
                (new_hash, user["id"]),
            )
        except Exception:
            pass
    # clear lockout on success
    try:
        query(
            settings,
            "update users set failed_login_attempts=0, lockout_until=null, last_failed_at=null, updated_at=now() where id=%s::uuid",
            (user["id"],),
        )
    except Exception:
        pass
    touch_login(settings, user["id"])
    log_auth_event(
        settings,
        email=email_norm,
        user_id=str(user["id"]),
        event_type="login_success",
        ip=ip,
        user_agent=ua,
    )
    set_session_cookie(response, settings, str(user["id"]))
    return {"ok": True, **_me_payload(_ctx_of(user))}


class ProfileUpdateBody(BaseModel):
    display_name: str | None = None
    email: str | None = None


@router.put("/profile")
@router.post("/profile")
def update_profile(
    body: ProfileUpdateBody, ctx: Annotated[UserCtx, Depends(get_current_user)]
) -> dict:
    if ctx.anonymous:
        raise HTTPException(status_code=401, detail="log in first")
    settings = load_settings()
    try:
        row = update_user_profile(
            settings, ctx.id, display_name=body.display_name, email=body.email
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return {"ok": True, **_me_payload(_ctx_of(row))}


class SetPasswordBody(BaseModel):
    new_password: str
    current_password: str = ""


@router.post("/password")
def set_password_route(
    body: SetPasswordBody, ctx: Annotated[UserCtx, Depends(get_current_user)], request: Request
) -> dict:
    if ctx.anonymous:
        raise HTTPException(status_code=401, detail="register or log in first")
    settings = load_settings()
    ip = request.client.host if request.client else "unknown"
    ua = request.headers.get("user-agent", "")[:256]
    if not rate_limit(f"setpwd:{ip}:{ctx.id}", max_events=5, window_seconds=300):
        raise HTTPException(status_code=429, detail="too many attempts, try again shortly")
    # fetch email for strength check (no email fragment in password)
    rows = fetch_user(settings, ctx.id)
    email_for_check = rows[0].get("email") if rows else None
    problems = validate_password_strength(
        body.new_password, email=email_for_check, display_name=ctx.display_name
    )
    if problems:
        raise HTTPException(status_code=422, detail=problems[0])
    rows = fetch_user(settings, ctx.id)
    if not rows:
        raise HTTPException(status_code=404, detail="account not found")
    existing_hash = rows[0].get("password_hash")
    if existing_hash:
        from app.auth import verify_password

        if not verify_password(existing_hash, body.current_password or ""):
            raise HTTPException(status_code=403, detail="current password is incorrect")
    from app.auth import hash_password
    from app.users import set_password

    set_password(settings, str(ctx.id), hash_password(body.new_password))
    query(
        settings,
        "update users set password_changed_at=now(), failed_login_attempts=0, lockout_until=null, updated_at=now() where id=%s::uuid",
        (ctx.id,),
    )
    log_auth_event(
        settings,
        email=email_for_check,
        user_id=str(ctx.id),
        event_type="password_change",
        ip=ip,
        user_agent=ua,
    )
    return {"ok": True, "message": "password saved — you can now log in with email + password"}


@router.get("/me/export")
def export_me(ctx: Annotated[UserCtx, Depends(get_current_user)]) -> dict:
    """DPDP/GDPR data-portability export: everything stored about this account.

    Never includes password_hash. Matches/matches-history are 24h-bounded by
    retention, so the dump stays small.
    """
    if ctx.anonymous:
        raise HTTPException(status_code=401, detail="log in first")
    settings = load_settings()
    rows = fetch_user(settings, ctx.id)
    if not rows:
        raise HTTPException(status_code=404, detail="account not found")
    user = dict(rows[0])
    user.pop("password_hash", None)
    for k, v in list(user.items()):
        if isinstance(v, datetime):
            user[k] = v.isoformat()
    prefs = query(settings, "select * from preferences where user_id = %s::uuid", (ctx.id,))
    subs = query(
        settings,
        "select plan_code, status, provider, current_period_start, current_period_end, "
        "created_at from subscriptions where user_id = %s::uuid order by created_at desc",
        (ctx.id,),
    )
    sent = query(
        settings,
        "select job_id, channel, sent_at from notifications_sent "
        "where user_id = %s::uuid order by sent_at desc",
        (ctx.id,),
    )
    matches = query(
        settings,
        "select job_id, matched_on, match_score, created_at from job_matches "
        "where user_id = %s::uuid order by created_at desc",
        (ctx.id,),
    )
    coupons = query(
        settings,
        "select code, grants_role, grant_duration_days, claimed_at from coupon_codes "
        "where claimed_by = %s::uuid",
        (ctx.id,),
    )
    events = query(
        settings,
        "select event_type, ip, created_at from auth_events "
        "where user_id = %s::uuid order by created_at desc limit 200",
        (ctx.id,),
    )

    def _iso_list(items: list[dict]) -> list[dict]:
        out = []
        for item in items:
            row = dict(item)
            for k, v in list(row.items()):
                if isinstance(v, datetime):
                    row[k] = v.isoformat()
            out.append(row)
        return out

    return {
        "exported_at": datetime.now(UTC).isoformat(),
        "user": user,
        "preferences": _iso_list(prefs),
        "subscriptions": _iso_list(subs),
        "notifications_sent": _iso_list(sent),
        "job_matches": _iso_list(matches),
        "coupons_claimed": _iso_list(coupons),
        "auth_events": _iso_list(events),
    }


class DeleteAccountBody(BaseModel):
    password: str = ""


@router.delete("/me")
def delete_me(
    body: DeleteAccountBody,
    request: Request,
    response: Response,
    ctx: Annotated[UserCtx, Depends(get_current_user)],
) -> dict:
    """DPDP/GDPR erasure: delete this account and everything FK-cascaded to it.

    - Owner account can never be deleted.
    - Accounts with a password must confirm it (prevents session/CSRF abuse).
    - Shared preference_presets the user created are reassigned to the owner
      (their FK is NO ACTION); coupons stay single-use via claimed_at even when
      claimed_by is nulled by SET NULL; auth_events keep an anonymized row.
    """
    if ctx.anonymous:
        raise HTTPException(status_code=401, detail="log in first")
    from app.config import DEFAULT_USER_ID

    if str(ctx.id).lower() == DEFAULT_USER_ID.lower():
        raise HTTPException(status_code=403, detail="the owner account cannot be deleted")
    settings = load_settings()
    rows = fetch_user(settings, ctx.id)
    if not rows:
        raise HTTPException(status_code=404, detail="account not found")
    existing_hash = rows[0].get("password_hash")
    if existing_hash:
        from app.auth import verify_password

        if not verify_password(existing_hash, body.password or ""):
            raise HTTPException(status_code=403, detail="current password is incorrect")
    ip = request.client.host if request.client else "unknown"
    ua = request.headers.get("user-agent", "")[:256]
    # Keep shared presets alive under the owner instead of violating NO ACTION.
    query(
        settings,
        "update preference_presets set created_by = %s::uuid, updated_at = now() "
        "where created_by = %s::uuid",
        (DEFAULT_USER_ID, ctx.id),
    )
    deleted = query(settings, "delete from users where id = %s::uuid returning id", (ctx.id,))
    if not deleted:
        raise HTTPException(status_code=404, detail="account not found")
    log_auth_event(
        settings, email=None, user_id=None, event_type="account_delete", ip=ip, user_agent=ua
    )
    clear_session_cookie(response, settings)
    return {"ok": True}


@router.post("/logout")
def logout(
    request: Request, response: Response, ctx: Annotated[UserCtx, Depends(get_current_user)]
) -> dict:
    settings = load_settings()
    ip = request.client.host if request.client else "unknown"
    ua = request.headers.get("user-agent", "")[:256]
    if not ctx.anonymous:
        log_auth_event(
            settings, email=ctx.email, user_id=ctx.id, event_type="logout", ip=ip, user_agent=ua
        )
    clear_session_cookie(response, settings)
    return {"ok": True}


class TelegramChatIdBody(BaseModel):
    telegram_chat_id: str


@router.put("/telegram-chat-id")
@router.post("/telegram-chat-id")
def set_telegram_chat_id(
    body: TelegramChatIdBody, ctx: Annotated[UserCtx, Depends(get_current_user)]
) -> dict:
    if ctx.anonymous:
        raise HTTPException(status_code=401, detail="log in first")
    raw = (body.telegram_chat_id or "").strip()
    if not raw:
        # clear
        query(
            load_settings(),
            "update users set telegram_chat_id=null, updated_at=now() where id=%s::uuid",
            (ctx.id,),
        )
        return {"ok": True, "telegram_chat_id": None}
    try:
        # allow -100... for channels, normal ids are positive ints
        chat_id = int(raw)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="telegram chat ID must be a number (e.g. 1415590254 or -1001234567890 for channels)",
        )
    if chat_id == 0 or abs(chat_id) < 1000:
        raise HTTPException(status_code=422, detail="invalid telegram chat ID")
    query(
        load_settings(),
        "update users set telegram_chat_id=%s, updated_at=now() where id=%s::uuid",
        (chat_id, ctx.id),
    )
    return {"ok": True, "telegram_chat_id": chat_id}


@router.get("/me")
def me(ctx: Annotated[UserCtx, Depends(get_current_user)]) -> dict:
    return _me_payload(ctx)
