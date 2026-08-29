"""Access control: coupon minting/redemption, subscription provisioning,
expiry sweeps, and the manual payment-provider backend.

Coupon guarantees (docs/subscription-plan.md §6/§11):
  * 12-hour validity — stamped server-side AND enforced by a DB constraint
  * single claim     — atomic conditional UPDATE, race-proof
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
    """open | claimed | expired — pure state classifier."""
    if code_row.get("claimed_by"):
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
    # Real providers are wired in Phase 7; until then behave like manual.
    return {
        "provider": provider,
        "instructions": "online payments are not enabled yet — contact the admin",
    }
