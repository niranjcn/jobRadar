import asyncio
import sys

sys.path.insert(0, "/app")

from app.adapters import adapter_for
from app.config import load_settings
from app.db import get_supabase
from app.poller import poll_source, create_poll_run, finish_poll_run


async def main():
    settings = load_settings()
    supabase = get_supabase(settings)
    rows = supabase.table("sources").select("*").eq("company_name", "Iris Software").execute()
    source = rows.data[0]
    print("source:", source["company_name"], source["ats_type"], source["board_identifier"])
    adapter = adapter_for(source["ats_type"])
    run_id = create_poll_run(supabase, triggered_by="manual", ats_type="custom")
    result = {}
    try:
        result = await poll_source(supabase, source, adapter)
        print("RESULT:", result)
    finally:
        finish_poll_run(
            supabase,
            run_id,
            status="completed",
            jobs_fetched=result.get("fetched", 0),
            jobs_new=result.get("new", 0),
        )


asyncio.run(main())