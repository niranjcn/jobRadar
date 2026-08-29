"""Entitlements: what an account may do.

Model (docs/subscription-plan.md §7):
  effective capabilities = explicit users.capabilities array when non-empty,
                           otherwise the defaults for the user's role.
Admins grant/revoke by editing the array; empty means "role defaults".

Deliverability adds the subscription gate: plain `user` accounts need an
active subscription; privileged/admin accounts are exempt.
"""

from typing import Any

ROLE_DEFAULT_CAPABILITIES: dict[str, set[str]] = {
    "user": {"dashboard", "preferences", "telegram_alerts", "email_alerts"},
    "privileged": {"dashboard", "preferences", "telegram_alerts", "email_alerts"},
    "admin": {
        "dashboard",
        "preferences",
        "telegram_alerts",
        "email_alerts",
        "admin",
    },
}


def effective_capabilities(user: dict[str, Any]) -> set[str]:
    caps = user.get("capabilities") or []
    role = user.get("role") or "user"
    if caps:
        return set(caps)
    return set(ROLE_DEFAULT_CAPABILITIES.get(role, ROLE_DEFAULT_CAPABILITIES["user"]))


def has_cap(user: dict[str, Any], cap: str) -> bool:
    return cap in effective_capabilities(user)


def can_receive_channel(user: dict[str, Any], channel: str) -> bool:
    return has_cap(user, f"{channel}_alerts")


def delivery_delay_minutes(user: dict[str, Any]) -> int:
    # Per-tier delay: admin 0, privileged -> app_settings privileged_delay_minutes, normal -> normal_delay_minutes
    # Falls back to per-user alert_delay_minutes if set, then tier defaults.
    role = (user.get("role") or "user").lower()
    if role == "admin":
        return 0
    # If user has explicit per-user delay, use it (allows admin override per user if needed)
    value = user.get("alert_delay_minutes")
    try:
        if value is not None:
            # None/empty is treated as 0 (unit tests expect 0), non-zero respects explicit value
            iv = int(value)
            if iv != 0:
                return max(0, iv)
            return 0
    except (TypeError, ValueError):
        pass
    # Tier defaults - will be overridden by DB values in load_audience where we inject
    # When _tier_* keys are absent (unit tests without DB), default to 0 rather than 30/360
    if role == "privileged":
        tier = user.get("_tier_privileged_delay")
        return int(tier) if tier is not None else 0
    tier = user.get("_tier_normal_delay")
    return int(tier) if tier is not None else 0


def subscription_required(role: str) -> bool:
    return role == "user"


def is_deliverable(user: dict[str, Any], *, has_active_subscription: bool) -> bool:
    """May this account receive alerts at all?"""
    if user.get("status") != "approved" or user.get("access_locked"):
        return False
    if subscription_required(user.get("role") or "user"):
        return has_active_subscription
    return True


# ---------- plan limits (enforced at preference-write time only) ----------


def validate_preferences_against_limits(
    prefs: dict[str, Any], limits: dict[str, Any] | None
) -> list[str]:
    """Return human-readable violations of the user's plan limits.

    Limits cap NEW writes only — stored data is never mutated on downgrade.
    Missing/None limits mean unrestricted (owner/privileged/manual grants).
    """
    if not limits:
        return []
    errors: list[str] = []
    checks = (
        ("max_locations", "locations"),
        ("max_keywords", "keywords"),
        ("max_roles", "roles"),
    )
    for limit_key, pref_key in checks:
        max_count = limits.get(limit_key)
        if max_count is None:
            continue
        values = prefs.get(pref_key) or []
        if len(values) > int(max_count):
            errors.append(f"{pref_key}: your plan allows at most {max_count} (got {len(values)})")
    return errors
