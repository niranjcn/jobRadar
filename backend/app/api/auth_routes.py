"""Auth endpoints: email/password registration & login with admin approval."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel

from app.auth import (
    UserCtx,
    clear_session_cookie,
    get_current_user,
    rate_limit,
    set_session_cookie,
    validate_password_strength,
)
from app.config import load_settings
from app.db import get_supabase
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
        "telegram_linked": ctx.telegram_chat_id is not None,
        "anonymous": ctx.anonymous,
    }
    if not ctx.anonymous:
        settings = load_settings()
        from app.users import fetch_user

        rows = fetch_user(settings, ctx.id)
        payload["has_password"] = bool(rows[0].get("password_hash") if rows else None)
        payload["telegram_username"] = rows[0].get("telegram_username") if rows else None
        payload["telegram_photo_url"] = rows[0].get("telegram_photo_url") if rows else None
        payload["needs_onboarding"] = not bool(rows[0].get("email") if rows else True)
        from app.access import active_subscription

        sub = active_subscription(settings, ctx.id)
        payload["subscription"] = sub
    return payload


class RegisterBody(BaseModel):
    email: str
    display_name: str = ""
    password: str


@router.post("/register", status_code=201)
def register(body: RegisterBody, request: Request, response: Response) -> dict:
    settings = load_settings()
    ip = request.client.host if request.client else "unknown"
    if not rate_limit(f"register:{ip}", max_events=5, window_seconds=3600):
        raise HTTPException(status_code=429, detail="too many registrations, try later")
    if not body.password:
        raise HTTPException(status_code=422, detail="password is required")
    problems = validate_password_strength(body.password)
    if problems:
        raise HTTPException(status_code=422, detail=problems[0])
    supabase = get_supabase(settings)
    try:
        row = create_registered_user(
            settings,
            supabase,
            email=body.email,
            display_name=body.display_name,
            password=body.password,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
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
    if not rate_limit(f"pwd:{ip}:{body.email.strip().lower()}", max_events=10, window_seconds=300):
        raise HTTPException(status_code=429, detail="too many attempts, try again shortly")
    rows = fetch_user_by_email(settings, body.email)
    invalid = HTTPException(status_code=401, detail="invalid email or password")
    if not rows:
        from app.auth import hash_password

        hash_password(body.password)
        raise invalid
    user = rows[0]
    from app.auth import verify_password

    if not verify_password(user.get("password_hash"), body.password):
        raise invalid
    if user.get("status") == "disabled":
        raise HTTPException(status_code=403, detail="account disabled")
    if user.get("status") == "pending":
        raise HTTPException(status_code=403, detail="account pending admin approval")
    touch_login(settings, user["id"])
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
    if not rate_limit(f"setpwd:{ip}:{ctx.id}", max_events=5, window_seconds=300):
        raise HTTPException(status_code=429, detail="too many attempts, try again shortly")
    problems = validate_password_strength(body.new_password)
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
    return {"ok": True, "message": "password saved — you can now log in with email + password"}


@router.post("/logout")
def logout(response: Response) -> dict:
    clear_session_cookie(response)
    return {"ok": True}


@router.get("/me")
def me(ctx: Annotated[UserCtx, Depends(get_current_user)]) -> dict:
    return _me_payload(ctx)
