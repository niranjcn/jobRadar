import asyncio
import sys

sys.path.insert(0, "/app")

from app.adapters import adapter_for
from app.config import load_settings
from app.db import get_supabase
from app.poller import poll_source


async def poll_one(company):
    settings = load_settings()
    supabase = get_supabase(settings)
    rows = supabase.table("sources").select("*").eq("company_name", company).execute()
    source = rows.data[0]
    adapter = adapter_for(source["ats_type"])
    result = await poll_source(supabase, source, adapter)
    print(f"{company}: fetched={result['fetched']} new={result['new']} first_check={result['first_check']}")


async def main():
    for company in ["Perplexity AI", "Cognition AI", "Redis", "SpaceX"]:
        try:
            await poll_one(company)
        except Exception as e:
            print(f"{company}: FAILED {type(e).__name__}: {e}")


asyncio.run(main())