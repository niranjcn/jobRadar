import os

from dotenv import load_dotenv

REQUIRED_ENV = ("SUPABASE_URL", "SUPABASE_KEY", "DATABASE_URL")
DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000001"

ATS_DEFAULT_SECONDS = {
    "greenhouse": 3600,
    "lever": 3600,
    "ashby": 3600,
    "workday": 1800,
    "oracle": 3600,
    "icims": 3600,
    "successfactors": 3600,
    "phenom": 3600,
    "avature": 21600,
    "google": 3600,
    "amazon": 3600,
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


def _parse_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _load_ats_intervals() -> dict[str, int]:
    default = int(os.environ.get("POLL_INTERVAL_SECONDS", "3600"))
    intervals: dict[str, int] = {}
    for ats, seconds in ATS_DEFAULT_SECONDS.items():
        intervals[ats] = int(os.environ.get(f"POLL_INTERVAL_{ats.upper()}_SECONDS", str(seconds)))
    intervals["custom"] = default
    return intervals


def load_settings() -> Settings:
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
    )
