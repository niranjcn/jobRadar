"""Operational self-checks: stall detection for the poll scheduler.

A crashed scheduler restarts the container; a *stalled* one (deadlocked
thread, swallowed exception) just stops producing completed runs while
/health keeps returning ok. This query is the tripwire: zero completed runs
in the window means page the owner, not the logs.
"""

from app.config import Settings
from app.db import query

# Interval is 60m + jitter, so one missed tick + margin. Must stay above the
# longest healthy per-ATS interval or every quiet board pages you nightly.
STALL_WINDOW_MINUTES = 70


def check_poll_stall(settings: Settings) -> dict:
    """Return {ok, completed}: True when at least one run finished in-window."""
    rows = query(
        settings,
        "select count(*)::int as c from poll_runs "
        "where status = 'completed' and finished_at > now() - (%s || ' minutes')::interval",
        (STALL_WINDOW_MINUTES,),
    )
    completed = int(rows[0]["c"]) if rows else 0
    return {"ok": completed > 0, "completed": completed}
