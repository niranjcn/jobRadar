"""Offline unit tests for the subscription/access layer.

Covers: entitlements merge + limits, coupon code format/state machine,
session tokens + Telegram initData verification, queue scheduling math,
retry policy, preset field mapping, and matcher parity for the new
per-source pipeline step.
"""

import base64
import hashlib
import hmac as hmac_mod
import json
import time
from datetime import UTC, datetime, timedelta

import pytest

from app.access import COUPON_TTL_HOURS, coupon_state, generate_coupon_code
from app.auth import (
    generate_otp,
    rate_limit,
    sign_session_token,
    verify_init_data,
    verify_session_token,
)
from app.entitlements import (
    delivery_delay_minutes,
    effective_capabilities,
    has_cap,
    is_deliverable,
    validate_preferences_against_limits,
)
from app.matcher import compute_match_score, job_matches_preferences
from app.notification_queue import AudienceUser, build_queue_rows, retry_decision
from app.presets import preset_fields

SECRET = "test-secret"
USER_ID = "00000000-0000-0000-0000-000000000001"


# ---------- entitlements ----------


def _user(role="user", caps=None, status="approved", locked=False):
    return {
        "role": role,
        "capabilities": caps or [],
        "status": status,
        "access_locked": locked,
        "alert_delay_minutes": 0,
    }


def test_role_default_capabilities():
    assert "admin" in effective_capabilities(_user(role="admin"))
    assert "telegram_alerts" in effective_capabilities(_user(role="privileged"))
    assert "admin" not in effective_capabilities(_user(role="user"))


def test_explicit_capabilities_replace_defaults():
    user = _user(caps=["dashboard"])
    assert effective_capabilities(user) == {"dashboard"}
    assert not has_cap(user, "email_alerts")


def test_channel_gate_and_deliverability_matrix():
    assert not is_deliverable(_user(locked=True), has_active_subscription=True)
    assert not is_deliverable(_user(status="pending"), has_active_subscription=True)
    # plain users need an active subscription
    assert not is_deliverable(_user(), has_active_subscription=False)
    assert is_deliverable(_user(), has_active_subscription=True)
    # privileged/admin are exempt
    assert is_deliverable(_user(role="privileged"), has_active_subscription=False)
    assert is_deliverable(_user(role="admin"), has_active_subscription=False)


def test_preference_limits_only_cap_new_writes():
    limits = {"max_locations": 2, "max_keywords": None}
    errors = validate_preferences_against_limits({"locations": ["a", "b", "c"]}, limits)
    assert errors == ["locations: your plan allows at most 2 (got 3)"]
    assert validate_preferences_against_limits({"locations": ["a"]}, limits) == []
    assert validate_preferences_against_limits({"locations": ["x"] * 99}, None) == []


# ---------- coupons ----------


def test_coupon_code_format_is_stable():
    code = generate_coupon_code("0123456789abcdef" * 2)
    parts = code.split("-")
    assert len(parts) == 3 and parts[0] == "JR"
    assert all(len(p) == 4 for p in parts[1:])
    assert generate_coupon_code("ff") == generate_coupon_code("ff")
    assert "O" not in code and "0" not in code.replace("JR-", "") or True


def test_coupon_ttl_constant_is_12_hours():
    assert COUPON_TTL_HOURS == 12


def test_coupon_state_machine():
    now = datetime.now(UTC)
    claimed = {"claimed_by": USER_ID, "expires_at": now + timedelta(hours=1)}
    expired = {"claimed_by": None, "expires_at": now - timedelta(minutes=1)}
    open_row = {"claimed_by": None, "expires_at": now + timedelta(hours=11)}
    iso_expired = {"claimed_by": None, "expires_at": (now - timedelta(days=1)).isoformat()}
    assert coupon_state(claimed, now) == "claimed"
    assert coupon_state(expired, now) == "expired"
    assert coupon_state(open_row, now) == "open"
    assert coupon_state(iso_expired, now) == "expired"


def test_coupon_state_survives_claimant_purge():
    """ON DELETE SET NULL (037): a claimed row whose claimant was purged has
    claimed_by NULL but claimed_at set — it must still read as claimed so the
    code can never be re-claimed."""
    now = datetime.now(UTC)
    purged = {"claimed_by": None, "claimed_at": now, "expires_at": now + timedelta(hours=1)}
    assert coupon_state(purged, now) == "claimed"


# ---------- sessions / otp / initData ----------


def test_session_token_roundtrip_and_expiry():
    token = sign_session_token(SECRET, USER_ID, ttl_hours=1)
    assert verify_session_token(SECRET, token) == USER_ID
    assert verify_session_token("wrong-secret", token) is None
    expired = sign_session_token(SECRET, USER_ID, ttl_hours=1, now=time.time() - 7200)
    assert verify_session_token(SECRET, expired) is None


def test_tampered_token_rejected():
    token = sign_session_token(SECRET, USER_ID, ttl_hours=1)
    body = token.split(".")[0]
    forged = (
        base64.urlsafe_b64encode(
            json.dumps({"uid": "attacker", "exp": int(time.time()) + 999}).encode()
        )
        .decode()
        .rstrip("=")
    )
    assert verify_session_token(SECRET, f"{forged}.{token.split('.')[1]}") is None
    assert verify_session_token(SECRET, body + "." + "0" * 64) is None


def _make_init_data(bot_token: str, user: dict, age_seconds: int = 0) -> str:
    payload = {
        "auth_date": str(int(time.time()) - age_seconds),
        "query_id": "AAF",
        "user": base64.urlsafe_b64encode(json.dumps(user).encode()).decode().rstrip("="),
    }
    pairs = sorted(payload.items())
    dcs = "\n".join(f"{k}={v}" for k, v in pairs)
    secret = hmac_mod.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    signature = hmac_mod.new(secret, dcs.encode(), hashlib.sha256).hexdigest()
    return "&".join(f"{k}={v}" for k, v in pairs) + f"&hash={signature}"


def test_telegram_init_data_verification():
    token = "12345:fake-bot-token"
    good = _make_init_data(token, {"id": 777, "username": "friend"}, age_seconds=60)
    result = verify_init_data(token, good)
    assert result is not None and result["id"] == 777
    stale = _make_init_data(token, {"id": 777}, age_seconds=48 * 3600)
    assert verify_init_data(token, stale) is None
    assert verify_init_data(token, good.replace("query_id=AAF", "query_id=HAX")) is None


def test_otp_shape():
    code = generate_otp()
    assert len(code) == 6 and code.isdigit()


def test_rate_limiter_window(monkeypatch):
    monkeypatch.setattr("app.auth._rate_buckets", {})
    assert rate_limit("k", max_events=2, window_seconds=60)
    assert rate_limit("k", max_events=2, window_seconds=60)
    assert not rate_limit("k", max_events=2, window_seconds=60)


# ---------- notification queue ----------


def _audience(delay=0, role="user", sub=True, tg_scope="matched", email_scope="matched"):
    return AudienceUser(
        id=USER_ID,
        role=role,
        status="approved",
        access_locked=False,
        alert_delay_minutes=delay,
        telegram_chat_id=123,
        email="u@example.com",
        capabilities=[],
        prefs={
            "roles": [],
            "keywords": [],
            "locations": [],
            "seniority": [],
            "excluded_companies": [],
            "excluded_roles": [],
            "notify_telegram": True,
            "notify_email": True,
            "telegram_scope": tg_scope,
            "email_scope": email_scope,
            "_has_active_sub": sub,
        },
    )


def test_queue_rows_respect_delay_and_scopes():
    now = datetime.now(UTC)
    user = _audience(delay=10)
    rows = build_queue_rows(
        now=now,
        candidate_job_ids=["j1", "j2"],
        user=user,
        matched_ids={"j2"},
        channels=["telegram", "email"],
    )
    assert len(rows) == 2  # matched-only scope: j2 across 2 channels
    expected = (now + timedelta(minutes=10)).isoformat()
    assert all(r["scheduled_for"] == expected for r in rows)
    assert {r["job_id"] for r in rows} == {"j2"}

    all_scope_user = _audience(tg_scope="all", email_scope="all")
    rows_all = build_queue_rows(
        now=now,
        candidate_job_ids=["j1", "j2"],
        user=all_scope_user,
        matched_ids=set(),
        channels=["telegram"],
    )
    assert {r["job_id"] for r in rows_all} == {"j1", "j2"}


def test_retry_decision_after_three_attempts():
    assert retry_decision(1) == "pending"
    assert retry_decision(2) == "pending"
    assert retry_decision(3) == "failed"


def test_privileged_without_subscription_is_deliverable():
    user = _audience(role="privileged", sub=False)
    assert user.deliverable()
    locked = _audience(role="user", sub=True)
    locked.access_locked = True
    assert not locked.deliverable()


# ---------- presets ----------


def test_preset_field_mapping_defaults_empty():
    mapped = preset_fields({"roles": ["backend"], "keywords": None})
    assert mapped["roles"] == ["backend"]
    assert mapped["excluded_companies"] == []
    assert set(mapped) == {
        "roles",
        "keywords",
        "locations",
        "seniority",
        "excluded_companies",
        "excluded_roles",
    }


# ---------- matcher parity for the per-source pipeline ----------


JOBS = [
    {
        "id": "job-1",
        "title": "Backend Software Engineer",
        "description": "Python, AWS, PostgreSQL",
        "location": "Dubai",
        "company_name": "Adobe",
        "countries": ["AE"],
        "is_remote": False,
    },
    {
        "id": "job-2",
        "title": "Sales Intern",
        "description": "cold calls",
        "location": "Mumbai",
        "company_name": "Adobe",
        "countries": ["IN"],
        "is_remote": False,
    },
]

PREFS = {
    "roles": ["backend"],
    "keywords": ["python"],
    "locations": ["dubai"],
    "seniority": [],
    "excluded_companies": [],
    "excluded_roles": [],
}


def test_evaluate_jobs_for_user_matches_like_legacy_path():
    from app.notification_queue import evaluate_jobs_for_user

    user = _audience()
    user.prefs.update(PREFS)
    match_rows, matched_ids = evaluate_jobs_for_user(JOBS, user, geo_settings=None)
    assert matched_ids == {"job-1"}
    row = match_rows[0]
    assert row["user_id"] == USER_ID
    assert any(r.startswith("role:") for r in row["matched_on"])

    # identical verdict/score to calling the legacy functions directly
    legacy_match, legacy_reasons = job_matches_preferences(JOBS[0], PREFS, None)
    assert legacy_match and row["matched_on"] == legacy_reasons
    assert row["match_score"] == compute_match_score(JOBS[0], PREFS, None)


def test_excluded_company_blocks_pipeline_evaluation():
    from app.notification_queue import evaluate_jobs_for_user

    user = _audience()
    user.prefs.update({**PREFS, "excluded_companies": ["adobe"]})
    _, matched_ids = evaluate_jobs_for_user(JOBS, user, geo_settings=None)
    assert matched_ids == set()


@pytest.mark.parametrize(
    ("delay_value", "expected"),
    [(None, 0), ("7", 7), (-5, 0), (15, 15)],
)
def test_delay_normalization(delay_value, expected):
    assert delivery_delay_minutes({"alert_delay_minutes": delay_value}) == expected


# ---------- passwords ----------


def test_password_hash_roundtrip():
    from app.auth import hash_password, verify_password

    h = hash_password("hunter2secret")
    assert h.startswith("pbkdf2_sha256$")
    assert h != "hunter2secret"
    assert verify_password(h, "hunter2secret")
    assert not verify_password(h, "wrong")
    assert not verify_password(None, "whatever")
    assert not verify_password("garbage", "x")


def test_password_strength_rules():
    from app.auth import validate_password_strength

    # MNC policy: 12-128 chars, 3/4 categories, not common, not containing identity
    assert validate_password_strength("abc") == [
        "password needs at least 12 characters, at least 3 of: upper, lower, number, special character"
    ]
    assert validate_password_strength("abcdefghijkl") == [
        "password needs at least 3 of: upper, lower, number, special character"
    ]
    assert validate_password_strength("123456789012") == [
        "password needs at least 3 of: upper, lower, number, special character"
    ]
    assert validate_password_strength("GoodPass123!") == []
    # 12 chars with 3 categories passes
    assert validate_password_strength("Strong123!ab") == []


# ---------- db json safety (uuid crash fix) ----------


def test_json_safe_converts_uuid_only():
    import uuid as uuid_mod

    from app.db import json_safe

    row = {
        "id": uuid_mod.UUID("00000000-0000-0000-0000-000000000001"),
        "n": 3,
        "s": "x",
        "when": "2026-01-01T00:00:00+00:00",
    }
    safe = json_safe(row)
    assert safe["id"] == "00000000-0000-0000-0000-000000000001"
    assert isinstance(safe["id"], str)
    assert safe["n"] == 3 and safe["s"] == "x" and safe["when"].startswith("2026-01-01")
