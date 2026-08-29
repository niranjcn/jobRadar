"""Admin API: user management, roles, per-user delays, capabilities, coupons,
presets, subscription grants, and system rollups. Every route requires the
admin capability (compat mode: anonymous = owner = admin, unchanged)."""

from datetime import UTC, datetime, timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.access import mint_coupon, provision_subscription
from app.auth import UserCtx, get_current_admin
from app.config import DEFAULT_USER_ID, load_settings
from app.db import get_supabase, query
from app.entitlements import effective_capabilities
from app.presets import (
    apply_preset_to_user,
    create_preset,
    delete_preset,
    get_preset,
    list_presets,
    preset_fields,
    snapshot_user_preferences,
    update_preset,
)
from app.users import admin_update_user

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(get_current_admin)])


def _supabase():
    return get_supabase(load_settings())


# ---------- users ----------


@router.get("/users")
def list_users(
    query_text: str = "",
    role: str = "",
    status: str = "",
    limit: int = 100,
    offset: int = 0,
) -> dict:
    settings = load_settings()
    where = ["true"]
    params: list[Any] = []
    if query_text:
        where.append("(u.email ilike %s or u.display_name ilike %s)")
        params += [f"%{query_text}%", f"%{query_text}%"]
    if role:
        where.append("u.role = %s")
        params.append(role)
    if status:
        where.append("u.status = %s")
        params.append(status)
    params += [limit, offset]
    rows = query(
        settings,
        f"""
        select u.id, u.email, u.display_name, u.role, u.status, u.access_locked,
               u.alert_delay_minutes, u.capabilities, u.is_owner,
               u.created_at, u.last_login_at,
               s.plan_code as sub_plan, s.provider as sub_provider,
               s.current_period_end as sub_period_end
        from users u
        left join subscriptions s on s.user_id = u.id and s.status = 'active'
        where {" and ".join(where)}
        order by u.created_at desc
        limit %s offset %s
        """,
        tuple(params),
    )
    for row in rows:
        for key in ("created_at", "last_login_at", "sub_period_end"):
            if row.get(key):
                row[key] = row[key].isoformat() if isinstance(row[key], datetime) else str(row[key])
    total = query(settings, "select count(*)::int as c from users u")[0]["c"]
    return {"users": rows, "total": total}


@router.get("/users/{user_id}")
def user_detail(user_id: str) -> dict:
    settings = load_settings()
    rows = query(
        settings,
        """
        select id, email, display_name, telegram_chat_id, role, status, capabilities,
               alert_delay_minutes, access_locked, is_owner, created_at, last_login_at
        from users where id = %s::uuid
        """,
        (user_id,),
    )
    if not rows:
        raise HTTPException(status_code=404, detail="user not found")
    row = rows[0]
    subs = query(
        settings,
        "select plan_code, status, provider, current_period_end, created_at "
        "from subscriptions where user_id = %s::uuid order by created_at desc limit 5",
        (user_id,),
    )
    counts = query(
        settings,
        """
        select
          (select count(*)::int from job_matches where user_id = %s::uuid) as matches,
          (select count(*)::int from notifications_sent where user_id = %s::uuid) as alerts_sent,
          (select count(*)::int from notification_queue
             where user_id = %s::uuid and status = 'pending') as alerts_pending
        """,
        (user_id, user_id, user_id),
    )[0]
    for entry in subs + [row]:
        for key in ("current_period_end", "created_at", "last_login_at"):
            if isinstance(entry.get(key), datetime):
                entry[key] = entry[key].isoformat()
    return {**row, "subscriptions": subs, "counts": counts}


class RoleBody(BaseModel):
    role: str


@router.put("/users/{user_id}/role")
def set_role(
    user_id: str,
    body: RoleBody,
    admin: Annotated[UserCtx, Depends(get_current_admin)],
) -> dict:
    if body.role not in ("user", "privileged", "admin"):
        raise HTTPException(status_code=422, detail="role must be user|privileged|admin")
    _guard_owner(user_id)
    return _update(user_id, {"role": body.role})


def _guard_owner(user_id: str) -> None:
    if user_id.lower() == DEFAULT_USER_ID.lower():
        raise HTTPException(status_code=403, detail="the owner account cannot be modified")


def _update(user_id: str, payload: dict[str, Any]) -> dict:
    try:
        return admin_update_user(load_settings(), user_id, payload)
    except LookupError:
        raise HTTPException(status_code=404, detail="user not found")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


class DelayBody(BaseModel):
    alert_delay_minutes: int


@router.put("/users/{user_id}/delay")
def set_delay(user_id: str, body: DelayBody) -> dict:
    if body.alert_delay_minutes < 0 or body.alert_delay_minutes > 60 * 24 * 7:
        raise HTTPException(status_code=422, detail="delay must be 0..10080 minutes")
    return _update(user_id, {"alert_delay_minutes": body.alert_delay_minutes})


class CapabilitiesBody(BaseModel):
    add: list[str] = []
    remove: list[str] = []


@router.post("/users/{user_id}/capabilities")
def set_capabilities(user_id: str, body: CapabilitiesBody) -> dict:
    settings = load_settings()
    rows = query(
        settings,
        "select id, role, capabilities from users where id = %s::uuid",
        (user_id,),
    )
    if not rows:
        raise HTTPException(status_code=404, detail="user not found")
    current = effective_capabilities(rows[0])
    known = {"dashboard", "preferences", "telegram_alerts", "email_alerts", "fast_alerts", "admin"}
    unknown = (set(body.add) | set(body.remove)) - known
    if unknown:
        raise HTTPException(status_code=422, detail=f"unknown capabilities: {sorted(unknown)}")
    merged = sorted((current - set(body.remove)) | set(body.add))
    return _update(user_id, {"capabilities": merged})


@router.post("/users/{user_id}/approve")
def approve_user(user_id: str) -> dict:
    _guard_owner(user_id)
    return _update(user_id, {"status": "approved"})


@router.post("/users/{user_id}/disable")
def disable_user(user_id: str) -> dict:
    _guard_owner(user_id)
    return _update(user_id, {"status": "disabled", "access_locked": True})


@router.post("/users/{user_id}/enable")
def enable_user(user_id: str) -> dict:
    return _update(user_id, {"status": "approved"})


@router.post("/users/{user_id}/lock")
def lock_user(user_id: str) -> dict:
    _guard_owner(user_id)
    return _update(user_id, {"access_locked": True})


@router.post("/users/{user_id}/unlock")
def unlock_user(user_id: str) -> dict:
    return _update(user_id, {"access_locked": False, "status": "approved"})


class CompBody(BaseModel):
    plan_code: str = "standard"
    duration_days: int | None = None


@router.put("/users/{user_id}/subscription")
def comp_subscription(user_id: str, body: CompBody) -> dict:
    settings = load_settings()
    exists = query(settings, "select 1 as ok from users where id = %s::uuid", (user_id,))
    if not exists:
        raise HTTPException(status_code=404, detail="user not found")
    period_end = None
    if body.duration_days:
        period_end = (datetime.now(UTC) + timedelta(days=body.duration_days)).isoformat()
    sub = provision_subscription(
        settings,
        user_id=user_id,
        plan_code=body.plan_code,
        provider="manual",
        period_end=period_end,
    )
    query(
        settings,
        "update users set access_locked = false, updated_at = now() where id = %s::uuid",
        (user_id,),
    )
    return {"ok": True, "subscription": sub}


class ApplyPresetBody(BaseModel):
    preset_id: str


@router.post("/users/{user_id}/apply-preset")
def apply_preset(user_id: str, body: ApplyPresetBody) -> dict:
    settings = load_settings()
    supabase = _supabase()
    try:
        result = apply_preset_to_user(settings, supabase, preset_id=body.preset_id, user_id=user_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="preset not found")
    recompute_error = None
    try:
        from app.matcher import recompute_matches

        recompute_matches(supabase, user_id=user_id)
    except Exception as exc:
        recompute_error = str(exc)[:200]
    return {"ok": True, **result, "recompute_error": recompute_error}


# ---------- coupons ----------


class CouponMintBody(BaseModel):
    grants_role: str
    duration_days: int | None = None
    note: str | None = None


@router.post("/coupons", status_code=201)
def create_coupon(
    body: CouponMintBody, admin: Annotated[UserCtx, Depends(get_current_admin)]
) -> dict:
    settings = load_settings()
    try:
        coupon = mint_coupon(
            settings,
            created_by=admin.id,
            grants_role=body.grants_role,
            duration_days=body.duration_days,
            note=body.note,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    coupon["created_at"] = (
        coupon["created_at"].isoformat()
        if isinstance(coupon["created_at"], datetime)
        else coupon["created_at"]
    )
    coupon["expires_at"] = (
        coupon["expires_at"].isoformat()
        if isinstance(coupon["expires_at"], datetime)
        else coupon["expires_at"]
    )
    return coupon


@router.get("/coupons")
def list_coupons(state: str = "", limit: int = 50) -> dict:
    settings = load_settings()
    where = {
        "open": "where claimed_by is null and expires_at > now()",
        "claimed": "where claimed_by is not null",
        "expired": "where claimed_by is null and expires_at <= now()",
    }.get(state, "")
    rows = query(
        settings,
        f"""
        select c.id, c.code, c.grants_role, c.duration_days, c.note,
               c.created_at, c.expires_at, c.claimed_at,
               u.email as claimed_by_email, cu.email as created_by_email
        from coupon_codes c
        left join users u on u.id = c.claimed_by
        left join users cu on cu.id = c.created_by
        {where}
        order by c.created_at desc
        limit %s
        """,
        (limit,),
    )
    for row in rows:
        for key in ("created_at", "expires_at", "claimed_at"):
            if isinstance(row.get(key), datetime):
                row[key] = row[key].isoformat()
    return {"coupons": rows}


@router.delete("/coupons/{coupon_id}")
def void_coupon(coupon_id: str) -> dict:
    settings = load_settings()
    rows = query(
        settings,
        "delete from coupon_codes where id = %s::uuid and claimed_by is null returning id",
        (coupon_id,),
    )
    if not rows:
        raise HTTPException(status_code=404, detail="coupon not found or already claimed")
    return {"ok": True}


# ---------- presets ----------


def _serialize_preset(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    for key in ("created_at", "updated_at"):
        if isinstance(out.get(key), datetime):
            out[key] = out[key].isoformat()
    return out


@router.get("/presets")
def presets(include_admin_only: bool = True) -> dict:
    return {"presets": list_presets(load_settings(), include_admin_only=include_admin_only)}


class PresetCreateBody(BaseModel):
    name: str
    description: str = ""
    is_admin_only: bool = False
    roles: list[str] = []
    keywords: list[str] = []
    locations: list[str] = []
    seniority: list[str] = []
    excluded_companies: list[str] = []
    excluded_roles: list[str] = []


@router.post("/presets", status_code=201)
def create_preset_route(
    body: PresetCreateBody, admin: Annotated[UserCtx, Depends(get_current_admin)]
) -> dict:
    fields = preset_fields(body.model_dump())
    try:
        row = create_preset(
            load_settings(),
            created_by=admin.id,
            name=body.name.strip(),
            description=body.description,
            fields=fields,
            is_admin_only=body.is_admin_only,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return row


class SnapshotBody(BaseModel):
    source_user_id: str
    name: str
    description: str = ""
    is_admin_only: bool = True


@router.post("/presets/snapshot", status_code=201)
def snapshot_preset(body: SnapshotBody) -> dict:
    try:
        return snapshot_user_preferences(
            load_settings(),
            _supabase(),
            source_user_id=body.source_user_id,
            name=body.name.strip(),
            description=body.description,
            is_admin_only=body.is_admin_only,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


class PresetUpdateBody(BaseModel):
    name: str | None = None
    description: str | None = None
    is_admin_only: bool | None = None
    roles: list[str] | None = None
    keywords: list[str] | None = None
    locations: list[str] | None = None
    seniority: list[str] | None = None
    excluded_companies: list[str] | None = None
    excluded_roles: list[str] | None = None


@router.patch("/presets/{preset_id}")
def patch_preset(preset_id: str, body: PresetUpdateBody) -> dict:
    update = {k: v for k, v in body.model_dump().items() if v is not None}
    try:
        update_preset(load_settings(), preset_id, update)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    row = get_preset(load_settings(), preset_id)
    if not row:
        raise HTTPException(status_code=404, detail="preset not found")
    return _serialize_preset(row)


@router.delete("/presets/{preset_id}")
def remove_preset(preset_id: str) -> dict:
    row = get_preset(load_settings(), preset_id)
    if not row:
        raise HTTPException(status_code=404, detail="preset not found")
    if row["name"] == "Admin Preference":
        raise HTTPException(status_code=403, detail="the Admin Preference preset cannot be deleted")
    delete_preset(load_settings(), preset_id)
    return {"ok": True}


# ---------- subscriptions / billing events / stats ----------


@router.get("/subscriptions")
def subscriptions(status: str = "") -> dict:
    settings = load_settings()
    where = "" if not status else "where s.status = %(status)s"
    rows = query(
        settings,
        f"""
        select s.id, s.plan_code, s.status, s.provider,
               s.current_period_start, s.current_period_end, s.created_at,
               u.email, u.display_name, u.role
        from subscriptions s join users u on u.id = s.user_id
        {where}
        order by s.created_at desc
        limit 200
        """,
        {"status": status} if status else {},
    )
    for row in rows:
        for key in ("current_period_start", "current_period_end", "created_at"):
            if isinstance(row.get(key), datetime):
                row[key] = row[key].isoformat()
    return {"subscriptions": rows}


@router.get("/billing-events")
def billing_events(limit: int = 50) -> dict:
    settings = load_settings()
    rows = query(
        settings,
        "select provider, provider_event_id, event_type, status, error, received_at "
        "from billing_events order by received_at desc limit %s",
        (limit,),
    )
    return {"events": rows}


@router.get("/stats")
def admin_stats() -> dict:
    settings = load_settings()
    row = query(
        settings,
        """
        select
          (select count(*)::int from users) as users_total,
          (select count(*)::int from users where role = 'privileged') as privileged,
          (select count(*)::int from users where access_locked) as locked,
          (select count(*)::int from users where status = 'disabled') as disabled,
          (select count(*)::int from subscriptions where status = 'active') as active_subs,
          (select count(*)::int from coupon_codes where claimed_by is null and expires_at > now()) as coupons_open,
          (select coalesce(sum(price_cents),0)::int from subscriptions s
             join plans p on p.code = s.plan_code
            where s.status = 'active' and p.interval = 'month') as mrr_cents,
          (select count(*)::int from notifications_sent where sent_at >= now() - interval '7 days') as alerts_7d
        """,
    )[0]
    return row
