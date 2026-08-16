import sys

sys.path.insert(0, "/app")

from app.config import load_settings
from app.db import get_supabase

s = get_supabase(load_settings())
# find Siemens source id
srcs = s.table("sources").select("id,company_name").ilike("company_name", "%Siemens%").execute()
print("siemens sources:", srcs.data)
for x in (srcs.data or []):
    r = s.table("jobs").select("external_job_id,location").eq("source_id", x["id"]).limit(5).execute()
    for j in (r.data or []):
        print(f"   {j['external_job_id']}: {j.get('location')!r}")