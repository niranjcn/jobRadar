from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from supabase import Client

from app.config import load_settings
from app.db import query

IST = ZoneInfo("Asia/Kolkata")


def load_interval_overrides(supabase: Client) -> dict[str, int]:
    rows = query(
        load_settings(),
        "select ats_type, interval_seconds from poll_schedule",
    )
    return {row["ats_type"]: row["interval_seconds"] for row in rows}


def effective_intervals(env_intervals: dict[str, int], overrides: dict[str, int]) -> dict[str, int]:
    merged = dict(env_intervals)
    merged.update(overrides)
    return merged


def last_checked_by_ats(settings=None) -> dict[str, str | None]:
    settings = settings or load_settings()
    rows = query(
        settings,
        """
        select ats_type, max(last_checked_at) as last_checked_at
        from sources
        where last_checked_at is not null
        group by ats_type
        """,
    )
    result: dict[str, str | None] = {}
    for row in rows:
        last = row["last_checked_at"]
        result[row["ats_type"]] = last.isoformat() if last else None
    return result


def source_count_by_ats(settings=None) -> dict[str, int]:
    settings = settings or load_settings()
    rows = query(
        settings,
        """
        select ats_type, count(*)::int as n
        from sources
        where active
        group by ats_type
        """,
    )
    return {row["ats_type"]: row["n"] for row in rows}


def set_interval_override(supabase: Client, ats_type: str, interval_seconds: int) -> None:
    supabase.table("poll_schedule").upsert(
        {
            "ats_type": ats_type,
            "interval_seconds": int(interval_seconds),
            "updated_at": datetime.now(UTC).isoformat(),
        },
        on_conflict="ats_type",
    ).execute()


def next_run_at(interval_seconds: int, last_checked_at: str | None) -> str | None:
    """Estimate when the next poll for this ATS will run, in IST.

    Scheduler now uses IntervalTrigger (every `interval_seconds` wall-clock,
    not cron-aligned), so the estimate is max(now, last_checked_at) + interval.
    Jitter ±120s is ignored for the estimate — ground truth is
    `scheduler_next_run()` from the live APScheduler.
    """
    if interval_seconds <= 0:
        return None
    now = datetime.now(IST)
    base = now
    if last_checked_at is not None:
        try:
            last = datetime.fromisoformat(last_checked_at)
            if last.tzinfo is None:
                last = last.replace(tzinfo=UTC)
            last = last.astimezone(IST)
            base = max(base, last)
        except (ValueError, TypeError):
            return None
    nxt = base + timedelta_seconds(interval_seconds)
    return nxt.isoformat()


def timedelta_seconds(seconds: int):
    from datetime import timedelta

    return timedelta(seconds=seconds)
