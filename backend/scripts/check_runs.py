from datetime import datetime, timezone

from app.config import load_settings
from app.db import query

s = load_settings()
rows = query(
    s,
    "select id, triggered_by, ats_type, status, started_at, finished_at, jobs_fetched, jobs_new, error "
    "from poll_runs order by started_at desc limit 12",
)
print(f"now={datetime.now(timezone.utc).isoformat()}")
for r in rows:
    sa = r["started_at"]
    age = ""
    if sa:
        age = f" {int((datetime.now(timezone.utc) - sa).total_seconds() / 60)}m ago"
    print(
        f"{r['status']:10s} {r['ats_type'] or 'all':10s} triggered_by={r['triggered_by']:9s} "
        f"started={r['started_at']}{age} fetched={r['jobs_fetched']} new={r['jobs_new']} err={r['error'] or ''}"
    )