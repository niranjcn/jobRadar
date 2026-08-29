"""Access endpoints: public pricing, coupon redemption, checkout stubs."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.access import CouponError, redeem_coupon, start_checkout
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
