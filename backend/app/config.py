import os

from dotenv import load_dotenv

REQUIRED_ENV = ("SUPABASE_URL", "SUPABASE_KEY", "DATABASE_URL")
DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000001"

ATS_DEFAULT_SECONDS = {
    "greenhouse": 3600,
    "lever": 3600,
    "ashby": 3600,
    "workday": 3600,
    "oracle": 3600,
    "icims": 3600,
    "successfactors": 7200,
    "phenom": 3600,
    "avature": 21600,
    "emirates": 3600,
    "google": 3600,
    "amazon": 3600,
    "remotive": 3600,
    "weworkremotely": 3600,
}

# Per-ATS concurrency for Tier 1: light boards handle 16 parallel. Heavy boards
# run 10-way: rate limits are per-host (each company is a different tenant
# host) and the retrying client backs off on 429, so cross-board concurrency is
# safe. Tune per ATS without code changes via POLL_CONCURRENCY_{ATS} env vars.
# Workday bumped to 20 for 200+ boards (271): 10-way would be ~78 min wall at
# 62→271 scale (>1h interval would skip). 20-way halves to ~39 min, fits 60m
# interval without sharding. Per-host limits still safe (each tenant distinct).
ATS_CONCURRENCY = {
    "greenhouse": 16,
    "lever": 16,
    "ashby": 16,
    "remotive": 16,
    "weworkremotely": 16,
    "workday": 20,
    "oracle": 10,
    "successfactors": 10,
    "phenom": 8,
    "avature": 10,
    "custom": 8,
    "emirates": 8,
    "icims": 8,
    "google": 8,
    "amazon": 8,
}


class Settings:
    def __init__(
        self,
        supabase_url: str,
        supabase_key: str,
        database_url: str,
        poll_interval_seconds: int,
        preferences: dict[str, list[str]],
        notify_enabled: bool,
        resend_api_key: str,
        notify_to: list[str],
        job_retention_days: int,
        max_posting_age_days: int,
        telegram_enabled: bool,
        telegram_bot_token: str,
        telegram_chat_id: str,
        telegram_mini_app_url: str,
        ats_intervals: dict[str, int],
        ats_concurrency: dict[str, int] | None = None,
        secret_key: str = "",
        require_auth: bool = False,
        session_ttl_hours: int = 168,
        session_cookie_secure: bool = False,
        billing_provider: str = "manual",
        notify_drain_seconds: int = 30,
        telegram_bot_username: str = "",
        admin_chat_id: str = "",
        razorpay_key_id: str = "",
        razorpay_key_secret: str = "",
        razorpay_webhook_secret: str = "",
        razorpay_plan_id: str = "",
    ) -> None:
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.database_url = database_url
        self.poll_interval_seconds = poll_interval_seconds
        self.preferences = preferences
        self.notify_enabled = notify_enabled
        self.resend_api_key = resend_api_key
        self.notify_to = notify_to
        self.job_retention_days = job_retention_days
        self.max_posting_age_days = max_posting_age_days
        self.telegram_enabled = telegram_enabled
        self.telegram_bot_token = telegram_bot_token
        self.telegram_chat_id = telegram_chat_id
        self.telegram_mini_app_url = telegram_mini_app_url
        self.ats_intervals = ats_intervals
        self.ats_concurrency = ats_concurrency or dict(ATS_CONCURRENCY)
        self.secret_key = secret_key
        self.require_auth = require_auth
        self.session_ttl_hours = session_ttl_hours
        self.session_cookie_secure = session_cookie_secure
        self.billing_provider = billing_provider
        self.notify_drain_seconds = notify_drain_seconds
        self.telegram_bot_username = telegram_bot_username
        self.admin_chat_id = admin_chat_id or telegram_chat_id
        self.razorpay_key_id = razorpay_key_id
        self.razorpay_key_secret = razorpay_key_secret
        self.razorpay_webhook_secret = razorpay_webhook_secret
        self.razorpay_plan_id = razorpay_plan_id


def _parse_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _load_ats_intervals() -> dict[str, int]:
    default = int(os.environ.get("POLL_INTERVAL_SECONDS", "3600"))
    intervals: dict[str, int] = {}
    for ats, seconds in ATS_DEFAULT_SECONDS.items():
        intervals[ats] = int(os.environ.get(f"POLL_INTERVAL_{ats.upper()}_SECONDS", str(seconds)))
    intervals["custom"] = default
    return intervals


def _load_ats_concurrency() -> dict[str, int]:
    """Per-ATS fetch concurrency, overridable via POLL_CONCURRENCY_{ATS} env vars."""
    concurrency: dict[str, int] = {}
    for ats, slots in ATS_CONCURRENCY.items():
        try:
            concurrency[ats] = max(
                1, int(os.environ.get(f"POLL_CONCURRENCY_{ats.upper()}", str(slots)))
            )
        except ValueError:
            concurrency[ats] = slots
    return concurrency


def _build_settings() -> Settings:
    load_dotenv()
    missing = [name for name in REQUIRED_ENV if name not in os.environ]
    if missing:
        raise RuntimeError(f"missing required env vars: {', '.join(missing)} (see .env.example)")
    return Settings(
        supabase_url=os.environ["SUPABASE_URL"],
        supabase_key=os.environ["SUPABASE_KEY"],
        database_url=os.environ["DATABASE_URL"],
        poll_interval_seconds=int(os.environ.get("POLL_INTERVAL_SECONDS", "3600")),
        preferences={
            "roles": _parse_list(os.environ.get("PREF_ROLES", "")),
            "keywords": _parse_list(os.environ.get("PREF_KEYWORDS", "")),
            "locations": _parse_list(os.environ.get("PREF_LOCATIONS", "")),
            "seniority": _parse_list(os.environ.get("PREF_SENIORITY", "")),
            "excluded_companies": _parse_list(os.environ.get("PREF_EXCLUDED_COMPANIES", "")),
            "excluded_roles": _parse_list(os.environ.get("PREF_EXCLUDED_ROLES", "")),
        },
        notify_enabled=os.environ.get("NOTIFY_ENABLED", "").lower() in ("1", "true", "yes"),
        resend_api_key=os.environ.get("RESEND_API_KEY", ""),
        notify_to=_parse_list(os.environ.get("NOTIFY_TO", "")),
        job_retention_days=int(os.environ.get("JOB_RETENTION_DAYS", "30")),
        max_posting_age_days=int(os.environ.get("MAX_POSTING_AGE_DAYS", "90")),
        telegram_enabled=os.environ.get("TELEGRAM_ENABLED", "").lower() in ("1", "true", "yes"),
        telegram_bot_token=os.environ.get("TELEGRAM_BOT_TOKEN", ""),
        telegram_chat_id=os.environ.get("TELEGRAM_CHAT_ID", ""),
        telegram_mini_app_url=os.environ.get("TELEGRAM_MINI_APP_URL", ""),
        ats_intervals=_load_ats_intervals(),
        ats_concurrency=_load_ats_concurrency(),
        secret_key=os.environ.get("SECRET_KEY", ""),
        require_auth=os.environ.get("JOBQUEST_REQUIRE_AUTH", "").lower() in ("1", "true", "yes"),
        session_ttl_hours=int(os.environ.get("SESSION_TTL_HOURS", "168")),
        session_cookie_secure=os.environ.get("SESSION_COOKIE_SECURE", "").lower()
        in ("1", "true", "yes"),
        billing_provider=os.environ.get("BILLING_PROVIDER", "manual"),
        notify_drain_seconds=int(os.environ.get("NOTIFY_DRAIN_SECONDS", "30")),
        telegram_bot_username=os.environ.get("TELEGRAM_BOT_USERNAME", "").lstrip("@"),
        admin_chat_id=os.environ.get("ADMIN_CHAT_ID", "").strip(),
        razorpay_key_id=os.environ.get("RAZORPAY_KEY_ID", "").strip(),
        razorpay_key_secret=os.environ.get("RAZORPAY_KEY_SECRET", "").strip(),
        razorpay_webhook_secret=os.environ.get("RAZORPAY_WEBHOOK_SECRET", "").strip(),
        razorpay_plan_id=os.environ.get("RAZORPAY_PLAN_ID", "").strip(),
    )


_settings_cache: Settings | None = None


def load_settings() -> Settings:
    """Load settings from the environment (memoized per process).

    Env parsing + `.env` file I/O used to run on every call (~50 call sites,
    several per request and one per source per poll). The environment is static
    for the life of a process, so the first build is cached and reused.
    Call `reset_settings_cache()` in tests or after changing the environment.
    """
    global _settings_cache
    if _settings_cache is None:
        _settings_cache = _build_settings()
    return _settings_cache


def reset_settings_cache() -> None:
    """Drop the memoized settings so the next `load_settings()` rebuilds."""
    global _settings_cache
    _settings_cache = None
