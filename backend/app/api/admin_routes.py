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
    grant_duration_days: int | None = None


@router.put("/users/{user_id}/subscription")
def comp_subscription(user_id: str, body: CompBody) -> dict:
    settings = load_settings()
    exists = query(settings, "select 1 as ok from users where id = %s::uuid", (user_id,))
    if not exists:
        raise HTTPException(status_code=404, detail="user not found")
    period_end = None
    if body.grant_duration_days:
        period_end = (datetime.now(UTC) + timedelta(days=body.grant_duration_days)).isoformat()
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
    grant_duration_days: int | None = None
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
            grant_duration_days=body.grant_duration_days,
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
    # claimed_at is the canonical "used" marker (claimed_by can be nulled by
    # ON DELETE SET NULL when a claimant is purged — see 037).
    where = {
        "open": "where claimed_at is null and expires_at > now()",
        "claimed": "where claimed_at is not null",
        "expired": "where claimed_at is null and expires_at <= now()",
    }.get(state, "")
    rows = query(
        settings,
        f"""
        select c.id, c.code, c.grants_role, c.grant_duration_days, c.note,
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
        "delete from coupon_codes where id = %s::uuid and claimed_at is null returning id",
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


@router.get("/egress")
def egress_overview(days: int = 30) -> dict:
    """Database egress / storage monitor for admin.

    Returns everything needed to watch egress pressure at a glance:
    total DB size, per-table breakdown (data/index/toast/rows), daily
    ingest & estimated bytes, top egress contributors (sources), recent
    poll footprints, bloat/vacuum hints, retention reclaim estimate,
    and actionable warnings. All queries are best-effort — a failing
    subsystem returns zeros rather than breaking the whole page.
    """
    settings = load_settings()
    days = max(7, min(days, 90))
    now_iso = datetime.now(UTC).isoformat()

    # --- database size ---
    db_size_bytes = 0
    try:
        r = query(settings, "select pg_database_size(current_database())::bigint as sz")
        db_size_bytes = int(r[0]["sz"]) if r else 0
    except Exception:
        db_size_bytes = 0

    # --- per-table breakdown ---
    tables: list[dict[str, Any]] = []
    try:
        rows = query(
            settings,
            """
            select c.relname as name,
                   pg_total_relation_size(c.oid)::bigint        as total_bytes,
                   pg_relation_size(c.oid)::bigint              as table_bytes,
                   pg_indexes_size(c.oid)::bigint               as index_bytes,
                   coalesce(s.n_live_tup, 0)::bigint            as live_rows,
                   coalesce(s.n_dead_tup, 0)::bigint            as dead_rows,
                   s.last_vacuum, s.last_autovacuum
            from pg_class c
            join pg_namespace nsp on nsp.oid = c.relnamespace
            left join pg_stat_user_tables s
              on s.relname = c.relname and s.schemaname = nsp.nspname
            where c.relkind = 'r' and nsp.nspname = 'public'
            order by pg_total_relation_size(c.oid) desc
            """,
        )
        for row in rows:
            total = int(row.get("total_bytes") or 0)
            tbl = int(row.get("table_bytes") or 0)
            idx = int(row.get("index_bytes") or 0)
            toast = max(0, total - tbl - idx)
            live = int(row.get("live_rows") or 0)
            avg_row = int(total / live) if live else 0
            # isoformat datetimes if present
            for k in ("last_vacuum", "last_autovacuum"):
                v = row.get(k)
                if isinstance(v, datetime):
                    row[k] = v.isoformat()
                elif v is not None:
                    row[k] = str(v)
            tables.append(
                {
                    "name": row["name"],
                    "total_bytes": total,
                    "table_bytes": tbl,
                    "index_bytes": idx,
                    "toast_bytes": toast,
                    "live_rows": live,
                    "dead_rows": int(row.get("dead_rows") or 0),
                    "avg_row_bytes": avg_row,
                    "last_vacuum": row.get("last_vacuum"),
                    "last_autovacuum": row.get("last_autovacuum"),
                }
            )
    except Exception as exc:
        print(f"egress: table breakdown failed: {exc}")

    # convenience: jobs table stats for avg row math
    jobs_table = next((t for t in tables if t["name"] == "jobs"), None)
    avg_job_bytes = (
        int(jobs_table["avg_row_bytes"]) if jobs_table and jobs_table["live_rows"] else 512
    )

    # --- totals / counts ---
    totals: dict[str, Any] = {}
    try:
        r = query(
            settings,
            """
            select
              (select count(*)::int from jobs) as jobs_total,
              (select count(*)::int from sources) as sources_total,
              (select count(*)::int from sources where active) as active_sources,
              (select count(*)::int from jobs where first_seen_at >= now() - interval '24 hours') as jobs_24h,
              (select count(*)::int from jobs where first_seen_at >= now() - interval '7 days') as jobs_7d,
              (select count(*)::int from jobs where first_seen_at >= now() - interval '30 days') as jobs_30d,
              (select count(*)::int from notifications_sent) as notif_total,
              (select count(*)::int from notification_queue) as queue_total,
              (select count(*)::int from poll_runs where started_at >= now() - interval '24 hours') as runs_24h
            """,
        )[0]
        totals = dict(r)
        totals["avg_job_bytes"] = avg_job_bytes
        totals["db_size_bytes"] = db_size_bytes
        # estimated bytes
        totals["bytes_24h_est"] = totals.get("jobs_24h", 0) * avg_job_bytes
        totals["bytes_7d_est"] = totals.get("jobs_7d", 0) * avg_job_bytes
        totals["bytes_30d_est"] = totals.get("jobs_30d", 0) * avg_job_bytes
        # 30d daily avg -> monthly projection
        daily_avg_jobs = (
            (totals.get("jobs_30d", 0) / 30)
            if totals.get("jobs_30d")
            else (totals.get("jobs_7d", 0) / 7 if totals.get("jobs_7d") else 0)
        )
        totals["proj_monthly_jobs"] = int(daily_avg_jobs * 30)
        totals["proj_monthly_bytes"] = int(daily_avg_jobs * 30 * avg_job_bytes)
    except Exception as exc:
        print(f"egress: totals failed: {exc}")
        totals = {
            "jobs_total": 0,
            "sources_total": 0,
            "active_sources": 0,
            "jobs_24h": 0,
            "jobs_7d": 0,
            "jobs_30d": 0,
            "avg_job_bytes": avg_job_bytes,
            "db_size_bytes": db_size_bytes,
            "bytes_24h_est": 0,
            "bytes_7d_est": 0,
            "bytes_30d_est": 0,
            "proj_monthly_jobs": 0,
            "proj_monthly_bytes": 0,
        }

    # --- daily ingest trend (egress proxy) ---
    daily: list[dict[str, Any]] = []
    try:
        rows = query(
            settings,
            """
            select to_char(day, 'YYYY-MM-DD') as date,
                   (select count(*)::int from jobs where date_trunc('day', first_seen_at) = day) as jobs,
                   (select count(*)::int from job_matches where date_trunc('day', created_at) = day) as matches,
                   (select count(*)::int from notifications_sent where date_trunc('day', sent_at) = day) as alerts
            from generate_series(
                date_trunc('day', now()) - (%s || ' days')::interval,
                date_trunc('day', now()), '1 day') as day
            order by 1
            """,
            (days - 1,),
        )
        for r in rows:
            j = int(r.get("jobs") or 0)
            daily.append(
                {
                    "date": r["date"],
                    "jobs": j,
                    "matches": int(r.get("matches") or 0),
                    "alerts": int(r.get("alerts") or 0),
                    "bytes_est": j * avg_job_bytes,
                }
            )
    except Exception as exc:
        print(f"egress: daily failed: {exc}")

    # --- top egress contributors (sources by job volume) ---
    top_sources: list[dict[str, Any]] = []
    try:
        rows = query(
            settings,
            """
            select s.company_name, s.ats_type, count(j.id)::int as job_count
            from sources s left join jobs j on j.source_id = s.id
            group by s.company_name, s.ats_type
            having count(j.id) > 0
            order by job_count desc
            limit 15
            """,
        )
        total_jobs = sum(int(r["job_count"]) for r in rows) or 1
        for r in rows:
            jc = int(r["job_count"])
            top_sources.append(
                {
                    "company": r["company_name"],
                    "ats_type": r["ats_type"],
                    "job_count": jc,
                    "bytes_est": jc * avg_job_bytes,
                    "share_pct": round((jc / total_jobs) * 100, 1),
                }
            )
    except Exception as exc:
        print(f"egress: top sources failed: {exc}")

    # --- recent poll runs (egress footprint per run) ---
    recent_runs: list[dict[str, Any]] = []
    try:
        rows = query(
            settings,
            """
            select id, triggered_by, ats_type, status, started_at, finished_at,
                   jobs_fetched, jobs_new, sources, error,
                   extract(epoch from (finished_at - started_at))*1000 as dur_ms
            from poll_runs
            order by started_at desc
            limit 12
            """,
        )
        for r in rows:
            for k in ("started_at", "finished_at"):
                if isinstance(r.get(k), datetime):
                    r[k] = r[k].isoformat()
                elif r.get(k) is not None:
                    r[k] = str(r[k])
            fetched = int(r.get("jobs_fetched") or 0)
            new = int(r.get("jobs_new") or 0)
            recent_runs.append(
                {
                    "id": str(r.get("id")),
                    "triggered_by": r.get("triggered_by"),
                    "ats_type": r.get("ats_type"),
                    "status": r.get("status"),
                    "started_at": r.get("started_at"),
                    "finished_at": r.get("finished_at"),
                    "jobs_fetched": fetched,
                    "jobs_new": new,
                    "bytes_est": new * avg_job_bytes,
                    "duration_ms": int(r.get("dur_ms") or 0) if r.get("dur_ms") else None,
                    "sources_count": len(r.get("sources") or [])
                    if isinstance(r.get("sources"), list)
                    else None,
                    "error": r.get("error"),
                }
            )
    except Exception as exc:
        print(f"egress: recent runs failed: {exc}")

    # --- cache / connection health (best-effort) ---
    cache: dict[str, Any] = {}
    try:
        r = query(
            settings,
            """
            select
              sum(blks_hit)::bigint as hits,
              sum(blks_read)::bigint as reads
            from pg_stat_database where datname = current_database()
            """,
        )[0]
        hits = int(r.get("hits") or 0)
        reads = int(r.get("reads") or 0)
        total = hits + reads
        cache = {
            "blks_hit": hits,
            "blks_read": reads,
            "hit_ratio": round((hits / total) * 100, 1) if total else None,
        }
    except Exception:
        cache = {}

    # --- retention reclaim estimate ---
    retention: dict[str, Any] = {}
    try:
        ret_days = int(settings.job_retention_days or 30)
        r = query(
            settings,
            "select count(*)::int as cnt from jobs where first_seen_at < now() - (%s || ' days')::interval",
            (ret_days,),
        )[0]
        cnt = int(r.get("cnt") or 0)
        retention = {
            "retention_days": ret_days,
            "reclaimable_jobs": cnt,
            "reclaimable_bytes_est": cnt * avg_job_bytes,
        }
    except Exception:
        retention = {"retention_days": 30, "reclaimable_jobs": 0, "reclaimable_bytes_est": 0}

    # --- warnings ---
    warnings: list[dict[str, Any]] = []
    # Supabase tiers: free 500 MB, pro 8 GB (reference only)
    FREE_LIMIT = 500 * 1024 * 1024
    PRO_LIMIT = 8 * 1024 * 1024 * 1024
    free_pct = (db_size_bytes / FREE_LIMIT * 100) if FREE_LIMIT else 0
    pro_pct = (db_size_bytes / PRO_LIMIT * 100) if PRO_LIMIT else 0
    if db_size_bytes and free_pct >= 90:
        warnings.append(
            {
                "level": "critical",
                "title": "Database near free-tier limit",
                "detail": f"{free_pct:.1f}% of 500 MB used. Upgrade to Pro (8 GB) or reduce retention before writes fail.",
            }
        )
    elif free_pct >= 70:
        warnings.append(
            {
                "level": "warn",
                "title": "Database over 70% of free tier",
                "detail": f"{free_pct:.1f}% of 500 MB. At current ingest (~{totals.get('proj_monthly_bytes', 0) // (1024 * 1024)} MB/mo) you have limited headroom.",
            }
        )
    # bloat
    high_bloat = [t for t in tables if t["dead_rows"] > max(5000, t["live_rows"] * 0.15)]
    if high_bloat:
        names = ", ".join(t["name"] for t in high_bloat[:3])
        warnings.append(
            {
                "level": "warn",
                "title": "Tables with dead tuples",
                "detail": f"{len(high_bloat)} table(s) have high dead rows (e.g. {names}). Consider VACUUM or schedule autovacuum tuning.",
            }
        )
    # growth velocity
    proj = totals.get("proj_monthly_bytes", 0)
    if proj and db_size_bytes and (db_size_bytes + proj) > FREE_LIMIT * 0.95 and free_pct < 90:
        warnings.append(
            {
                "level": "warn",
                "title": "Projected to hit limit this month",
                "detail": f"At ~{proj // 1024} KB/mo, DB would reach {(db_size_bytes + proj) / FREE_LIMIT * 100:.1f}% of 500 MB in 30 days.",
            }
        )
    # retention
    if retention.get("reclaimable_jobs", 0) > 5000:
        warnings.append(
            {
                "level": "info",
                "title": "Retention cleanup available",
                "detail": f"{retention['reclaimable_jobs']} jobs older than {retention['retention_days']}d (~{retention['reclaimable_bytes_est'] // 1024} KB) would be removed by the retention job.",
            }
        )
    # jobs dominating
    if jobs_table and db_size_bytes and (jobs_table["total_bytes"] / db_size_bytes) > 0.65:
        warnings.append(
            {
                "level": "info",
                "title": "Jobs table dominates storage",
                "detail": f"Jobs is {(jobs_table['total_bytes'] / db_size_bytes * 100):.1f}% of DB. Descriptions are already stripped; further savings need lower retention or fewer sources.",
            }
        )
    # cache hit
    if cache.get("hit_ratio") is not None and cache["hit_ratio"] < 85:
        warnings.append(
            {
                "level": "info",
                "title": "Low cache hit ratio",
                "detail": f"Buffer hit ratio {cache['hit_ratio']}% (<85%). Queries are hitting disk — consider indexes or larger cache.",
            }
        )

    return {
        "generated_at": now_iso,
        "days": days,
        "database": {
            "size_bytes": db_size_bytes,
            "free_limit_bytes": FREE_LIMIT,
            "pro_limit_bytes": PRO_LIMIT,
            "free_pct": round(free_pct, 1),
            "pro_pct": round(pro_pct, 3),
        },
        "tables": tables,
        "totals": totals,
        "daily": daily,
        "top_sources": top_sources,
        "recent_runs": recent_runs,
        "cache": cache,
        "retention": retention,
        "warnings": warnings,
    }


@router.get("/schema")
def admin_schema() -> dict:
    """Live DB schema + analysis for the visual schema page.

    Returns tables with columns, PK/FK, indexes, sizes, row counts and a pre-computed
    issues list (missing FKs, inconsistent deletes, naming, etc.) so the frontend
    is a pure renderer and never fails to show something.
    """
    settings = load_settings()
    # --- tables ---
    tables = query(
        settings,
        "select table_name from information_schema.tables where table_schema='public' and table_type='BASE TABLE' order by table_name",
    )
    table_names = [r["table_name"] for r in tables]
    # columns (only base tables — avoid views like v_job_source)
    cols = query(
        settings,
        "select table_name, column_name, data_type, udt_name, is_nullable, column_default from information_schema.columns where table_schema='public' and table_name = any(%s) order by table_name, ordinal_position",
        (table_names,),
    )
    cols_by_table: dict[str, list[dict[str, Any]]] = {t: [] for t in table_names}
    for c in cols:
        if c["table_name"] in cols_by_table:
            cols_by_table[c["table_name"]].append(c)
    # constraints
    fks = query(
        settings,
        """
        select tc.table_name, tc.constraint_name, kcu.column_name, ccu.table_name as foreign_table, ccu.column_name as foreign_column, rc.delete_rule
        from information_schema.table_constraints tc
        join information_schema.key_column_usage kcu on tc.constraint_name=kcu.constraint_name and tc.table_schema=kcu.table_schema
        left join information_schema.constraint_column_usage ccu on ccu.constraint_name=tc.constraint_name and ccu.table_schema=tc.table_schema
        left join information_schema.referential_constraints rc on rc.constraint_name=tc.constraint_name and rc.constraint_schema=tc.table_schema
        where tc.table_schema='public' and tc.constraint_type='FOREIGN KEY'
        order by tc.table_name
    """,
    )
    fks_by_table: dict[str, list[dict[str, Any]]] = {t: [] for t in table_names}
    for fk in fks:
        if fk["table_name"] in fks_by_table:
            fks_by_table[fk["table_name"]].append(fk)
    # pks
    pks = query(
        settings,
        """
        select tc.table_name, kcu.column_name
        from information_schema.table_constraints tc
        join information_schema.key_column_usage kcu on tc.constraint_name=kcu.constraint_name
        where tc.table_schema='public' and tc.constraint_type='PRIMARY KEY'
    """,
    )
    pks_by_table: dict[str, set[str]] = {t: set() for t in table_names}
    for pk in pks:
        if pk["table_name"] in pks_by_table:
            pks_by_table[pk["table_name"]].add(pk["column_name"])
    # uniques
    uniques = query(
        settings,
        """
        select tc.table_name, tc.constraint_name, kcu.column_name
        from information_schema.table_constraints tc
        join information_schema.key_column_usage kcu on tc.constraint_name=kcu.constraint_name
        where tc.table_schema='public' and tc.constraint_type='UNIQUE'
        order by tc.table_name
    """,
    )
    uniques_by_table: dict[str, list[str]] = {t: [] for t in table_names}
    for u in uniques:
        if u["table_name"] in uniques_by_table:
            uniques_by_table[u["table_name"]].append(u["column_name"])
    # indexes
    idxs = query(
        settings,
        "select tablename as table_name, indexname, indexdef from pg_indexes where schemaname='public' order by tablename",
    )
    idx_by_table: dict[str, list[dict[str, Any]]] = {t: [] for t in table_names}
    for idx in idxs:
        if idx["table_name"] in idx_by_table:
            idx_by_table[idx["table_name"]].append(idx)
    # sizes + row counts (best-effort, never fail page)
    sizes: dict[str, dict[str, Any]] = {}
    for t in table_names:
        try:
            r = query(
                settings,
                "select pg_total_relation_size(%s::regclass)::bigint as total_bytes, pg_relation_size(%s::regclass)::bigint as data_bytes",
                (f"public.{t}", f"public.{t}"),
            )
            total = int(r[0]["total_bytes"]) if r else 0
            data = int(r[0]["data_bytes"]) if r else 0
            # estimated rows via n_live_tup, plus exact count for small tables (<100k est)
            est = query(
                settings,
                "select coalesce(n_live_tup,0)::bigint as est from pg_stat_user_tables where relname=%s",
                (t,),
            )
            est_rows = int(est[0]["est"]) if est and est[0]["est"] is not None else 0
            exact = None
            if est_rows < 100000:
                try:
                    c = query(settings, f"select count(*)::int as c from {t} limit 100000")
                    # Use count(*) without limit for exact when small
                    c2 = query(settings, f"select count(*)::bigint as c from public.{t}")
                    exact = int(c2[0]["c"]) if c2 else None
                except Exception:
                    exact = None
            sizes[t] = {
                "total_bytes": total,
                "data_bytes": data,
                "est_rows": est_rows,
                "exact_rows": exact,
            }
        except Exception:
            sizes[t] = {"total_bytes": 0, "data_bytes": 0, "est_rows": 0, "exact_rows": None}
    # --- analysis (MNC checklist) ---
    issues: list[dict[str, Any]] = []
    # 1. Missing FKs that logically should exist
    has_job_fk = any(fk["column_name"] == "job_id" for fk in fks_by_table.get("job_matches", []))
    if not has_job_fk:
        issues.append(
            {
                "level": "high",
                "table": "job_matches",
                "title": "Missing FK job_matches.job_id → jobs.id",
                "detail": "Orphan job_matches can survive job deletion (jobs ON DELETE CASCADE does not clean them). Add FK with ON DELETE CASCADE.",
            }
        )
    has_nq_job_fk = any(
        fk["column_name"] == "job_id" for fk in fks_by_table.get("notification_queue", [])
    )
    if not has_nq_job_fk:
        issues.append(
            {
                "level": "high",
                "table": "notification_queue",
                "title": "Missing FK notification_queue.job_id → jobs.id",
                "detail": "Queue rows can orphan when jobs are pruned (retention). Add FK ON DELETE CASCADE like jobs_source_id_fkey.",
            }
        )
    # 2. FK delete rule inconsistency
    for tbl in ("preferences", "subscriptions", "coupon_codes"):
        for fk in fks_by_table.get(tbl, []):
            if fk["delete_rule"] == "NO ACTION":
                issues.append(
                    {
                        "level": "medium",
                        "table": tbl,
                        "title": f"FK {fk['constraint_name']} NO ACTION",
                        "detail": f"{fk['column_name']} → {fk['foreign_table']}.{fk['foreign_column']} is NO ACTION; deleting a user leaves orphan {tbl}. Prefer ON DELETE CASCADE (or SET NULL where nullable like coupon_codes.claimed_by).",
                    }
                )
    # 3. Missing FK indexes (Postgres does not auto-index FK columns)
    # Check: job_matches.job_id already has index, notification_queue job_id has no index
    nq_indexes = [idx["indexdef"] for idx in idx_by_table.get("notification_queue", [])]
    if not any("job_id" in d for d in nq_indexes):
        issues.append(
            {
                "level": "medium",
                "table": "notification_queue",
                "title": "No index on notification_queue.job_id",
                "detail": "FK without index → slow deletes and JOINs on jobs prune. Add btree(job_id).",
            }
        )
    # 4. Naming / standard
    for t in table_names:
        if any(
            c["column_name"].endswith("_at") and c["data_type"] != "timestamp with time zone"
            for c in cols_by_table[t]
        ):
            issues.append(
                {
                    "level": "low",
                    "table": t,
                    "title": "Timestamp without timestamptz",
                    "detail": f"{t} has _at column not timestamptz — use timestamptz for UTC.",
                }
            )
    # 5. Users email nullable + unique allows multiple NULLs — intentional for telegram-only accounts, but note
    issues.append(
        {
            "level": "info",
            "table": "users",
            "title": "users.email nullable + unique (intentional)",
            "detail": "Allows telegram-only accounts (email NULL). Postgres unique allows many NULLs — correct for this design, not a bug.",
        }
    )
    # 6. Text vs varchar, no length checks
    for t in table_names:
        for c in cols_by_table[t]:
            if c["data_type"] == "text" and c["column_name"] in ("email", "display_name", "code"):
                pass  # intentional, validated in app layer
    # 7. Row count vs size sanity
    # 8. Missing updated_at trigger (app sets updated_at manually in queries — okay but note)
    issues.append(
        {
            "level": "info",
            "table": "app_settings",
            "title": "No updated_at trigger",
            "detail": "updated_at is set by app code (query ... updated_at=now()), not a DB trigger — works but manual.",
        }
    )
    # Build payload
    payload_tables = []
    for t in table_names:
        payload_tables.append(
            {
                "name": t,
                "columns": cols_by_table[t],
                "pks": sorted(pks_by_table[t]),
                "fks": fks_by_table[t],
                "uniques": uniques_by_table[t],
                "indexes": idx_by_table[t],
                "size": sizes[t],
            }
        )
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "tables": payload_tables,
        "issues": issues,
        "counts": {
            "tables": len(table_names),
            "total_bytes": sum(s["total_bytes"] for s in sizes.values()),
        },
    }


@router.get("/db-observability")
def db_observability() -> dict:
    """pg_stat observability for 56/57: table scans, index usage, bloat.

    Returns pg_stat_user_tables (seq_scan/idx_scan/n_tup_*/n_dead_tup) and
    pg_stat_user_indexes (idx_scan) for the hot tables plus a country sanity
    check (64) and index bloat hints. All queries best-effort — a failing
    stat table never breaks the page.
    """
    settings = load_settings()
    tables: list[dict[str, Any]] = []
    indexes: list[dict[str, Any]] = []
    country_sanity: list[dict[str, Any]] = []
    try:
        tables = query(
            settings,
            """
            select relname,
                   seq_scan, seq_tup_read, idx_scan,
                   n_tup_ins, n_tup_upd, n_tup_del, n_tup_hot_upd,
                   n_live_tup, n_dead_tup, vacuum_count, autovacuum_count,
                   last_vacuum, last_autovacuum, last_analyze, last_autoanalyze,
                   pg_size_pretty(pg_total_relation_size(relid)) as total_size,
                   pg_total_relation_size(relid)::bigint as total_bytes
            from pg_stat_user_tables
            where schemaname = 'public'
            order by pg_total_relation_size(relid) desc
            """,
        )
        for r in tables:
            for k in ("last_vacuum", "last_autovacuum", "last_analyze", "last_autoanalyze"):
                v = r.get(k)
                if isinstance(v, datetime):
                    r[k] = v.isoformat()
                elif v is not None:
                    r[k] = str(v)
    except Exception as exc:
        print(f"db-observability: tables failed: {exc}")
    try:
        indexes = query(
            settings,
            """
            select schemaname, relname as table_name, indexrelname,
                   pg_size_pretty(pg_relation_size(indexrelid)) as size,
                   pg_relation_size(indexrelid)::bigint as bytes,
                   idx_scan, idx_tup_read, idx_tup_fetch
            from pg_stat_user_indexes
            where schemaname = 'public'
            order by pg_relation_size(indexrelid) desc
            """,
        )
    except Exception as exc:
        print(f"db-observability: indexes failed: {exc}")
    try:
        country_sanity = query(
            settings,
            """
            select distinct unnest(countries) as code,
                   count(*)::int as jobs
            from jobs
            where countries is not null and array_length(countries,1) > 0
            group by 1
            order by 1
            """,
        )
    except Exception as exc:
        print(f"db-observability: country sanity failed: {exc}")
    # Highlight unused indexes (>5 MB and idx_scan=0)
    unused = [
        ix
        for ix in indexes
        if int(ix.get("idx_scan") or 0) == 0 and int(ix.get("bytes") or 0) > 5 * 1024 * 1024
    ]
    # Highlight bloat candidates (dead >15% of live or >5k dead)
    bloat = [
        t
        for t in tables
        if int(t.get("n_dead_tup") or 0) > max(5000, int(t.get("n_live_tup") or 0) * 0.15)
    ]
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "tables": tables,
        "indexes": indexes,
        "country_sanity": country_sanity,
        "hints": {
            "unused_indexes": unused,
            "bloat_candidates": bloat,
        },
    }


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
          (select count(*)::int from coupon_codes where claimed_at is null and expires_at > now()) as coupons_open,
          (select coalesce(sum(price_minor_units),0)::int from subscriptions s
             join plans p on p.code = s.plan_code
            where s.status = 'active' and p.interval = 'month') as mrr_cents,
          (select count(*)::int from notifications_sent where sent_at >= now() - interval '7 days') as alerts_7d
        """,
    )[0]
    return row
