"""Access endpoints: public pricing, coupon redemption, checkout stubs + Razorpay autopay."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from app.access import CouponError, create_razorpay_subscription, handle_razorpay_webhook, redeem_coupon, start_checkout, verify_razorpay_signature
from app.auth import UserCtx, get_current_user, require_product_access
from app.config import load_settings
from app.db import get_supabase, query

router = APIRouter(prefix="/api", tags=["access"])


@router.get("/presets")
def user_presets(ctx: Annotated[UserCtx, Depends(require_product_access)]) -> dict:
    """Quick-start preference presets visible to signed-in users.
    Admin-only presets (e.g. 'Admin Preference') are excluded."""
    from app.presets import list_presets

    return {"presets": list_presets(load_settings(), include_admin_only=False)}


@router.get("/plans")
def plans() -> dict:
    settings = load_settings()
    rows = query(
        settings,
        "select code, name, price_cents, currency, interval from plans "
        "where is_active order by sort_order",
    )
    return {"plans": rows}


class RedeemBody(BaseModel):
    code: str


@router.post("/coupons/redeem")
def redeem(body: RedeemBody, ctx: Annotated[UserCtx, Depends(get_current_user)]) -> dict:
    if ctx.anonymous:
        raise HTTPException(status_code=401, detail="register or log in first")
    settings = load_settings()
    supabase = get_supabase(settings)
    try:
        result = redeem_coupon(settings, supabase, ctx.id, body.code)
    except CouponError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.reason)
    # Make the newly unlocked account's matches appear immediately.
    try:
        from app.matcher import recompute_matches

        recompute_matches(supabase, user_id=ctx.id)
    except Exception as exc:
        print(f"redeem: recompute failed for {ctx.id}: {exc}")
    return {"ok": True, **result}


class CheckoutBody(BaseModel):
    plan_code: str = "standard"


@router.post("/billing/checkout")
def checkout(body: CheckoutBody, ctx: Annotated[UserCtx, Depends(get_current_user)]) -> dict:
    if ctx.anonymous:
        raise HTTPException(status_code=401, detail="register or log in first")
    settings = load_settings()
    return start_checkout(settings, ctx.id)


@router.get("/billing/portal")
def portal(ctx: Annotated[UserCtx, Depends(get_current_user)]) -> dict:
    if ctx.anonymous:
        raise HTTPException(status_code=401, detail="register or log in first")
    settings = load_settings()
    if settings.billing_provider == "manual":
        raise HTTPException(status_code=404, detail="no billing portal (manual payments)")
    return {"url": None, "provider": settings.billing_provider}


class RazorpayVerifyBody(BaseModel):
    razorpay_payment_id: str
    razorpay_signature: str
    razorpay_subscription_id: str | None = None
    razorpay_order_id: str | None = None


@router.post("/billing/razorpay/create-subscription")
def razorpay_create_subscription(ctx: Annotated[UserCtx, Depends(get_current_user)]) -> dict:
    if ctx.anonymous:
        raise HTTPException(status_code=401, detail="register or log in first")
    settings = load_settings()
    if settings.billing_provider != "razorpay":
        raise HTTPException(status_code=400, detail="Razorpay not enabled — set BILLING_PROVIDER=razorpay")
    try:
        sub = create_razorpay_subscription(settings, ctx.id)
        # also return key for frontend
        return {"ok": True, "key_id": settings.razorpay_key_id, **sub}
    except CouponError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.reason)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)[:200])


@router.post("/billing/razorpay/verify")
def razorpay_verify(body: RazorpayVerifyBody, ctx: Annotated[UserCtx, Depends(get_current_user)]) -> dict:
    if ctx.anonymous:
        raise HTTPException(status_code=401, detail="register or log in first")
    settings = load_settings()
    if not verify_razorpay_signature(settings, body.model_dump()):
        raise HTTPException(status_code=400, detail="payment verification failed — signature mismatch")
    # verified -> provision 30 days (autopay or one-time). Razorpay will send subscription.charged webhook for renewals
    from datetime import UTC, datetime, timedelta

    from app.access import provision_subscription
    from app.db import query as db_query

    period_end = (datetime.now(UTC) + timedelta(days=30)).isoformat()
    provider_sub_id = body.razorpay_subscription_id or body.razorpay_order_id or body.razorpay_payment_id
    provision_subscription(settings, user_id=ctx.id, plan_code="standard", provider="razorpay", period_end=period_end, provider_subscription_id=provider_sub_id)
    db_query(settings, "update users set access_locked=false, updated_at=now() where id=%s::uuid", (ctx.id,))
    try:
        from app.matcher import recompute_matches

        supabase = get_supabase(settings)
        recompute_matches(supabase, user_id=ctx.id)
    except Exception:
        pass
    return {"ok": True, "subscription_id": provider_sub_id, "period_end": period_end}


@router.post("/billing/razorpay/cancel")
def razorpay_cancel(ctx: Annotated[UserCtx, Depends(get_current_user)]) -> dict:
    if ctx.anonymous:
        raise HTTPException(status_code=401, detail="register or log in first")
    settings = load_settings()
    # Razorpay cancel is via dashboard or API; we just mark cancel_at_period_end
    from app.db import query as db_query

    rows = db_query(settings, "update subscriptions set cancel_at_period_end=true, updated_at=now() where user_id=%s::uuid and status='active' and provider='razorpay' returning id", (ctx.id,))
    if not rows:
        raise HTTPException(status_code=404, detail="no active Razorpay subscription to cancel")
    return {"ok": True, "message": "autopay cancelled — access remains until period end, then revoked"}


@router.post("/webhooks/razorpay")
async def razorpay_webhook(request: Request) -> dict:
    settings = load_settings()
    raw = await request.body()
    sig = request.headers.get("X-Razorpay-Signature") or request.headers.get("x-razorpay-signature")
    supabase = get_supabase(settings)
    try:
        result = handle_razorpay_webhook(settings, supabase, raw, sig)
        return result
    except CouponError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.reason)
