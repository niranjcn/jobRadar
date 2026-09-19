"""Access control: coupon minting/redemption, subscription provisioning,
expiry sweeps, and the manual payment-provider backend.

Coupon guarantees (docs/subscription-plan.md §6/§11):
  * 12-hour validity — stamped server-side AND enforced by a DB constraint
  * single claim     — atomic conditional UPDATE, race-proof
  * claimed_at is the canonical "used" marker (not claimed_by): both FKs are
    ON DELETE SET NULL (037), so a claimant/creator purge nulls the attribution
    without resurrecting the code — every "unused" guard checks claimed_at.
"""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from supabase import Client

from app.config import Settings
from app.db import query

COUPON_TTL_HOURS = 12
CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"  # no lookalikes (0/O, 1/I/L)
CODE_GROUP_LENGTH = 4

PLAN_STANDARD = "standard"


class CouponError(Exception):
    def __init__(self, reason: str, status_code: int = 400) -> None:
        super().__init__(reason)
        self.reason = reason
        self.status_code = status_code


@dataclass
class CouponGrant:
    code_id: str
    grants_role: str
    duration_days: int | None


# ---------- pure helpers (unit-tested offline) ----------


def generate_coupon_code(random_hex: str) -> str:
    """Deterministic formatter for testability: 'JR-XXXX-XXXX' from hex input."""
    chars = []
    for i in range(CODE_GROUP_LENGTH * 2):
        byte = int(random_hex[i % len(random_hex)], 16)
        chars.append(CODE_ALPHABET[(byte + i * 7) % len(CODE_ALPHABET)])
    joined = "".join(chars)
    return f"JR-{joined[:CODE_GROUP_LENGTH]}-{joined[CODE_GROUP_LENGTH:]}"


def coupon_state(code_row: dict[str, Any], now: datetime) -> str:
    """open | claimed | expired — pure state classifier.

    claimed_at is canonical: after ON DELETE SET NULL (037) a claimed row can
    have claimed_by NULL (claimant purged) while claimed_at stays set.
    claimed_by is kept as a fallback so old row dicts still classify.
    """
    if code_row.get("claimed_at") or code_row.get("claimed_by"):
        return "claimed"
    expires_at = code_row.get("expires_at")
    if isinstance(expires_at, datetime):
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        if expires_at <= now:
            return "expired"
    elif isinstance(expires_at, str):
        try:
            if datetime.fromisoformat(expires_at) <= now:
                return "expired"
        except ValueError:
            pass
    return "open"


# ---------- DB operations ----------


def mint_coupon(
    settings: Settings,
    *,
    created_by: str,
    grants_role: str,
    duration_days: int | None = None,
    note: str | None = None,
) -> dict[str, Any]:
    import secrets as _secrets

    if grants_role not in ("user", "privileged"):
        raise ValueError("grants_role must be 'user' or 'privileged'")
    if duration_days is not None:
        try:
            duration_days = int(duration_days)
        except (TypeError, ValueError):
            raise ValueError("duration must be 1-12 months (30-365 days)")
        if duration_days < 30 or duration_days > 365:
            raise ValueError("coupon duration must be 1-12 months (30-365 days)")
        # normalize to months: 30,60,90,120,150,180,210,240,270,300,330,365
        # keep as-is for flexibility but enforce bounds
    raw = _secrets.token_hex(16)
    code = generate_coupon_code(raw)
    expires_at = datetime.now(UTC) + timedelta(hours=COUPON_TTL_HOURS)
    rows = query(
        settings,
        """
        insert into coupon_codes (code, grants_role, duration_days, note, created_by, expires_at)
        values (%s, %s, %s, %s, %s::uuid, %s)
        returning id, code, grants_role, duration_days, note, created_at, expires_at
        """,
        (code, grants_role, duration_days, note, created_by, expires_at.isoformat()),
    )
    return rows[0]


def redeem_coupon(settings: Settings, supabase: Client, user_id: str, code: str) -> dict[str, Any]:
    """Atomically claim the coupon and unlock the account. Raises CouponError."""
    code = (code or "").strip().upper()
    claimed = query(
        settings,
        """
        update coupon_codes
           set claimed_by = %s::uuid, claimed_at = now()
         where code = %s
           and claimed_by is null
           and claimed_at is null
           and expires_at > now()
        returning id, grants_role, duration_days
        """,
        (user_id, code),
    )
    if not claimed:
        raise CouponError("this code is invalid, expired, or already used")
    grant = claimed[0]
    grants_role = grant["grants_role"]
    period_end: str | None = None
    if grant["duration_days"]:
        period_end = (datetime.now(UTC) + timedelta(days=int(grant["duration_days"]))).isoformat()

    query(
        settings,
        "update users set role = %s, access_locked = false, updated_at = now() where id = %s::uuid",
        (grants_role, user_id),
    )
    provision_subscription(
        settings,
        user_id=user_id,
        plan_code=PLAN_STANDARD,
        provider="coupon",
        period_end=period_end,
    )
    # Make sure matching works immediately for the newly unlocked account.
    from app.users import seed_preferences

    seed_preferences(supabase, user_id, load_settings_prefs())
    return {"role": grants_role, "duration_days": grant["duration_days"]}


def load_settings_prefs() -> dict[str, list[str]]:
    from app.config import load_settings

    return load_settings().preferences


def provision_subscription(
    settings: Settings,
    *,
    user_id: str,
    plan_code: str = PLAN_STANDARD,
    provider: str = "manual",
    period_end: str | None = None,
    provider_subscription_id: str | None = None,
) -> dict[str, Any]:
    """Insert (or replace) the single live subscription row for a user."""
    query(
        settings,
        """
        update subscriptions
           set status = 'canceled', updated_at = now()
         where user_id = %s::uuid and status in ('active', 'past_due')
        """,
        (user_id,),
    )
    rows = query(
        settings,
        """
        insert into subscriptions (
            user_id, plan_code, status, provider, provider_subscription_id,
            current_period_start, current_period_end
        )
        values (%s::uuid, %s, 'active', %s, %s, now(), %s)
        returning id, plan_code, status, provider, current_period_end
        """,
        (user_id, plan_code, provider, provider_subscription_id, period_end),
    )
    return rows[0]


def active_subscription(settings: Settings, user_id: str) -> dict[str, Any] | None:
    rows = query(
        settings,
        """
        select s.plan_code, s.status, s.provider, s.current_period_end,
               p.limits as plan_limits
          from subscriptions s
          join plans p on p.code = s.plan_code
         where s.user_id = %s::uuid and s.status = 'active'
         limit 1
        """,
        (user_id,),
    )
    return rows[0] if rows else None


def has_active_subscription(settings: Settings, user_id: str) -> bool:
    return active_subscription(settings, user_id) is not None


def sweep_expired_subscriptions(settings: Settings) -> int:
    """Expire past-period subscriptions and re-lock plain users who lost access.

    Privileged/admin accounts and coupons without expiry are unaffected.
    Returns the number of users locked.
    """
    query(
        settings,
        """
        update subscriptions
           set status = 'expired', updated_at = now()
         where status in ('active', 'past_due')
           and current_period_end is not null
           and current_period_end < now()
        """,
    )
    locked = query(
        settings,
        """
        update users u
           set access_locked = true, updated_at = now()
         where u.role = 'user'
           and not u.access_locked
           and u.is_owner = false
           and not exists (
               select 1 from subscriptions s
                where s.user_id = u.id and s.status = 'active'
           )
        returning u.id
        """,
    )
    return len(locked)


def _razorpay_client(settings: Settings):
    if not settings.razorpay_key_id or not settings.razorpay_key_secret:
        return None
    try:
        import razorpay

        return razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))
    except Exception:
        return None


def _get_or_create_razorpay_plan(settings: Settings, client) -> str | None:
    # Reuse env plan_id if set and valid
    if settings.razorpay_plan_id:
        try:
            client.plan.fetch(settings.razorpay_plan_id)
            return settings.razorpay_plan_id
        except Exception:
            pass
    # Create fresh monthly plan from DB plan
    try:
        rows = query(settings, "select price_cents, currency, name from plans where code='standard' and is_active limit 1")
        plan = rows[0] if rows else {"price_cents": 900, "currency": "INR", "name": "Standard"}
        amount = int(plan["price_cents"])
        # Razorpay expects amount in paise for INR (₹9 = 900 paise). Our DB stores cents/paise already (900 = ₹9)
        # Ensure at least 100 paise (₹1) minimum
        if amount < 100:
            amount = 100
        currency = "INR"
        resp = client.plan.create(
            {
                "period": "monthly",
                "interval": 1,
                "item": {"name": plan.get("name", "Standard"), "amount": amount, "currency": currency, "description": "JobQuest monthly autopay"},
            }
        )
        return resp.get("id")
    except Exception as exc:
        print(f"razorpay plan create failed: {exc}")
        return None


def _create_razorpay_order(settings: Settings, client, user_id: str) -> dict[str, Any]:
    """Fallback one-time order when subscriptions not enabled (autopay disabled in dashboard)."""
    rows = query(settings, "select price_cents, currency from plans where code='standard' and is_active limit 1")
    plan = rows[0] if rows else {"price_cents": 50000, "currency": "INR"}
    amount = int(plan["price_cents"])
    if amount < 100:
        amount = 100
    # Razorpay order amount is in paise
    try:
        order = client.order.create({"amount": amount, "currency": "INR", "receipt": f"jq_{user_id[:8]}_{int(datetime.now(UTC).timestamp())}", "notes": {"user_id": user_id, "plan_code": PLAN_STANDARD}})
        return {"order_id": order.get("id"), "amount": amount, "currency": "INR"}
    except Exception as exc:
        raise CouponError(f"Razorpay order failed: {exc}", status_code=500)


def create_razorpay_subscription(settings: Settings, user_id: str) -> dict[str, Any]:
    """Create a Razorpay subscription for autopay. Falls back to order if subscriptions disabled."""
    client = _razorpay_client(settings)
    if client is None:
        raise CouponError("Razorpay not configured — set RAZORPAY_KEY_ID/SECRET", status_code=500)
    # fetch user
    rows = query(settings, "select email, display_name from users where id=%s::uuid", (user_id,))
    if not rows:
        raise CouponError("user not found", status_code=404)
    email = rows[0].get("email") or ""
    name = rows[0].get("display_name") or email.split("@")[0]
    # create customer
    try:
        customer = client.customer.create({"name": name, "email": email, "notes": {"user_id": user_id}})
        customer_id = customer.get("id")
    except Exception as exc:
        print(f"razorpay customer create failed: {exc}")
        customer_id = None
    plan_id = _get_or_create_razorpay_plan(settings, client)
    if plan_id:
        # try subscription (autopay)
        try:
            sub = client.subscription.create(
                {
                    "plan_id": plan_id,
                    "customer_id": customer_id,
                    "quantity": 1,
                    "total_count": 12,
                    "customer_notify": 1,
                    "notes": {"user_id": user_id, "plan_code": PLAN_STANDARD},
                }
            )
            return {
                "subscription_id": sub.get("id"),
                "plan_id": plan_id,
                "customer_id": customer_id,
                "amount": 0,
                "is_subscription": True,
            }
        except Exception as exc:
            print(f"razorpay subscription failed (fallback to order): {exc}")
    # fallback to one-time order (autopay not enabled in Razorpay dashboard)
    order = _create_razorpay_order(settings, client, user_id)
    return {
        "order_id": order["order_id"],
        "plan_id": None,
        "customer_id": customer_id,
        "amount": order["amount"],
        "is_subscription": False,
        "subscription_id": None,
    }


def verify_razorpay_signature(settings: Settings, payload: dict[str, Any]) -> bool:
    client = _razorpay_client(settings)
    if client is None:
        return False
    # support both order and subscription verification
    # Order: razorpay_order_id + razorpay_payment_id
    # Subscription: razorpay_subscription_id + razorpay_payment_id
    try:
        data: dict[str, Any] = {}
        if payload.get("razorpay_order_id"):
            data = {
                "razorpay_order_id": payload.get("razorpay_order_id"),
                "razorpay_payment_id": payload.get("razorpay_payment_id"),
                "razorpay_signature": payload.get("razorpay_signature"),
            }
        else:
            data = {
                "razorpay_subscription_id": payload.get("razorpay_subscription_id"),
                "razorpay_payment_id": payload.get("razorpay_payment_id"),
                "razorpay_signature": payload.get("razorpay_signature"),
            }
        if not data.get("razorpay_signature") or not data.get("razorpay_payment_id"):
            return False
        # need at least one of order/subscription id
        if not (data.get("razorpay_order_id") or data.get("razorpay_subscription_id")):
            return False
        client.utility.verify_payment_signature(data)
        return True
    except Exception:
        # fallback manual HMAC
        try:
            import hmac, hashlib

            if payload.get("razorpay_order_id"):
                msg = f"{payload.get('razorpay_order_id')}|{payload.get('razorpay_payment_id')}"
            else:
                msg = f"{payload.get('razorpay_subscription_id')}|{payload.get('razorpay_payment_id')}"
                msg2 = f"{payload.get('razorpay_payment_id')}|{payload.get('razorpay_subscription_id')}"
                expected2 = hmac.new(settings.razorpay_key_secret.encode(), msg2.encode(), hashlib.sha256).hexdigest()
                if hmac.compare_digest(expected2, payload.get("razorpay_signature") or ""):
                    return True
            expected = hmac.new(settings.razorpay_key_secret.encode(), msg.encode(), hashlib.sha256).hexdigest()
            return hmac.compare_digest(expected, payload.get("razorpay_signature") or "")
        except Exception:
            return False


def handle_razorpay_webhook(settings: Settings, supabase: Client, raw_body: bytes, signature: str | None) -> dict[str, Any]:
    """Verify webhook signature, persist billing_event, and provision/cancel subscription."""
    # verify if secret is set
    if settings.razorpay_webhook_secret and signature:
        try:
            import razorpay

            client = _razorpay_client(settings)
            if client:
                client.utility.verify_webhook_signature(raw_body.decode(), signature, settings.razorpay_webhook_secret)
        except Exception as exc:
            raise CouponError(f"webhook signature invalid: {exc}", status_code=400)
    try:
        import json

        event = json.loads(raw_body.decode())
    except Exception:
        raise CouponError("invalid webhook payload", status_code=400)
    provider_event_id = str(event.get("event") or "") + ":" + str(event.get("payload", {}).get("payment", {}).get("entity", {}).get("id") or event.get("payload", {}).get("subscription", {}).get("entity", {}).get("id") or "")
    event_type = str(event.get("event") or "unknown")
    # persist raw event idempotently
    try:
        query(
            settings,
            "insert into billing_events (provider, provider_event_id, event_type, payload, status) values (%s,%s,%s,%s::jsonb,'received') on conflict (provider, provider_event_id) do nothing",
            ("razorpay", provider_event_id or f"evt_{datetime.now(UTC).isoformat()}", event_type, json.dumps(event)),
        )
    except Exception:
        pass
    # handle subscription charged / payment captured -> activate
    payload = event.get("payload", {})
    sub_entity = payload.get("subscription", {}).get("entity") or {}
    pay_entity = payload.get("payment", {}).get("entity") or {}
    # Try to find user_id from notes
    user_id = None
    if sub_entity.get("notes", {}).get("user_id"):
        user_id = str(sub_entity["notes"]["user_id"])
    elif pay_entity.get("notes", {}).get("user_id"):
        user_id = str(pay_entity["notes"]["user_id"])
    # For subscription events, provision 30 days on charged
    if event_type in ("subscription.charged", "invoice.paid", "payment.captured") and user_id:
        period_end = (datetime.now(UTC) + timedelta(days=30)).isoformat()
        # subscription.charged is autopay success
        sub_id = sub_entity.get("id") or pay_entity.get("subscription_id") or pay_entity.get("id")
        provision_subscription(settings, user_id=user_id, plan_code=PLAN_STANDARD, provider="razorpay", period_end=period_end, provider_subscription_id=str(sub_id) if sub_id else None)
        try:
            query(settings, "update users set access_locked=false, updated_at=now() where id=%s::uuid", (user_id,))
            from app.users import seed_preferences

            seed_preferences(supabase, user_id, load_settings_prefs())
        except Exception:
            pass
        return {"ok": True, "event": event_type, "user_id": user_id}
    if event_type in ("subscription.cancelled", "subscription.completed") and user_id:
        # Mark cancel_at_period_end — keep access until period_end, then sweep will revoke
        try:
            query(settings, "update subscriptions set cancel_at_period_end=true, updated_at=now() where user_id=%s::uuid and status='active' and provider='razorpay'", (user_id,))
        except Exception:
            pass
        return {"ok": True, "event": event_type, "user_id": user_id}
    return {"ok": True, "event": event_type}


def start_checkout(settings: Settings, user_id: str) -> dict[str, Any]:
    """Return checkout instructions for the configured provider.

    The 'manual' backend ships first: the admin confirms payment and unlocks
    from /admin. Real PSPs plug in behind the same interface later.
    """
    provider = settings.billing_provider
    if provider == "manual":
        return {
            "provider": "manual",
            "instructions": (
                "Send your payment to the admin, then share your account email. "
                "The admin will unlock your account from the admin panel."
            ),
        }
    if provider == "razorpay":
        client = _razorpay_client(settings)
        if client is None:
            try:
                rows = query(settings, "select price_cents, currency from plans where code='standard' and is_active limit 1")
                price = rows[0] if rows else {"price_cents": 900, "currency": "INR"}
                amt = f"{price['currency']} {(price['price_cents']/100):.2f}"
            except Exception:
                amt = "plan price"
            return {
                "provider": "razorpay",
                "instructions": (
                    f"Razorpay monthly — {amt}/month. Complete payment via Razorpay Checkout. "
                    "Once paid, admin/webhook will mark your subscription active and matches/telegram will unlock. "
                    "If Razorpay keys are not configured, contact admin for manual unlock."
                ),
                "order_id": None,
                "amount": price.get("price_cents") if 'price' in locals() and isinstance(price, dict) else 900,
            }
        # create subscription for autopay
        try:
            sub = create_razorpay_subscription(settings, user_id)
            rows = query(settings, "select price_cents, currency from plans where code='standard' and is_active limit 1")
            price = rows[0] if rows else {"price_cents": 900, "currency": "INR"}
            return {
                "provider": "razorpay",
                "subscription_id": sub["subscription_id"],
                "plan_id": sub["plan_id"],
                "customer_id": sub["customer_id"],
                "key_id": settings.razorpay_key_id,
                "amount": price["price_cents"],
                "currency": price.get("currency", "INR"),
                "instructions": "Razorpay autopay — subscription created, complete authentication to activate monthly billing. Access unlocks only after successful payment.",
            }
        except CouponError as exc:
            return {"provider": "razorpay", "instructions": str(exc), "error": True}
        except Exception as exc:
            return {"provider": "razorpay", "instructions": f"Razorpay error: {exc}", "error": True}
    # Real providers are wired in Phase 7; until then behave like manual.
    return {
        "provider": provider,
        "instructions": "online payments are not enabled yet — contact the admin",
    }
