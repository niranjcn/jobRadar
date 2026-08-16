from datetime import datetime, timezone

from app.config import load_settings
from app.db import get_supabase

s = load_settings()
supabase = get_supabase(s)

resp = supabase.table("poll_runs").select("id, ats_type").eq("status", "running").execute()
for row in resp.data or []:
    supabase.table("poll_runs").update(
        {
            "status": "failed",
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "error": "stale: killed by reload",
        }
    ).eq("id", row["id"]).execute()
    print(f"marked failed: {row['ats_type']} {row['id']}")

# also clear stale last_checked run-blocking? not needed