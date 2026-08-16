"""Fast validation of every source in sources.json.

List-only, bounded to the first page / a few pages so the whole registry can be
checked in seconds instead of running the full poll (which backfills thousands
of descriptions). Reports per-source: OK(count) / EMPTY / FAILED(reason).

Greenhouse/Lever/Ashby: full list in one call, count = len(jobs).
Workday: reads the CXS total + first page only.
Oracle (Taleo): first page only.
"""

import asyncio
import json
from pathlib import Path

import httpx

from app.adapters import adapter_for
from app.adapters.workday import WorkdayAdapter

SOURCES_FILE = Path(__file__).resolve().parent / "sources.json"


async def probe(source: dict) -> str:
    ats = source["ats_type"]
    bid = source["board_identifier"]
    try:
        if ats in ("greenhouse", "lever", "ashby"):
            adapter = adapter_for(ats)
            jobs = await asyncio.wait_for(adapter.fetch_jobs(bid), timeout=60.0)
            return f"OK {len(jobs)}"
        elif ats == "workday":
            adapter = WorkdayAdapter()
            tenant, shard, site = adapter._parse_board(bid)
            api = f"https://{tenant}.{shard}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs"
            async with httpx.AsyncClient(timeout=25.0) as client:
                r = await client.post(api, json={"limit": 20, "offset": 0, "searchText": ""})
                if r.status_code == 200:
                    data = r.json()
                    total = data.get("total")
                    return f"OK total={total}"
                return f"HTTP {r.status_code} site={site!r}"
        elif ats == "oracle":
            base = bid.rstrip("/")
            async with httpx.AsyncClient(timeout=25.0, follow_redirects=True) as client:
                page = await client.get(f"{base}/jobsearch.ftl")
                if page.status_code != 200:
                    return f"HTTP {page.status_code}"
                import re

                m = re.search(r"portalNo:\s*'(\d+)'", page.text)
                if not m:
                    return "no portalNo found"
                host = bid.split("/careersection")[0].rstrip("/")
                r = await client.post(
                    f"{host}/careersection/rest/jobboard/searchjobs?portal={m.group(1)}",
                    json={
                        "multilineEnabled": False,
                        "sortingSelection": {
                            "sortBySelectionParam": "1",
                            "ascendingSortingOrder": "false",
                        },
                        "fieldData": {
                            "fields": {"KEYWORD": "", "LOCATION": "", "CATEGORY": ""},
                            "valid": True,
                        },
                        "pageNo": 1,
                    },
                    headers={
                        "Content-Type": "application/json",
                        "X-Requested-With": "XMLHttpRequest",
                    },
                )
                if r.status_code != 200:
                    return f"HTTP {r.status_code}"
                return f"OK {len(r.json().get('requisitionList') or [])} (first page)"
        return "UNKNOWN ATS"
    except Exception as exc:
        return f"EXC {str(exc)[:90]}"


async def main() -> None:
    sources = json.loads(SOURCES_FILE.read_text(encoding="utf-8"))
    ok = empty = failed = 0
    for src in sources:
        label = src["company_name"]
        result = await probe(src)
        tag = result.split(" ")[0]
        if tag == "OK":
            ok += 1
        elif "EMPTY" in result or "total=0" in result:
            empty += 1
        else:
            failed += 1
        print(f"{label:<20} {src['ats_type']:<10} {result}")
    print(f"\nstored={len(sources)} ok={ok} empty={empty} failed={failed}")


if __name__ == "__main__":
    asyncio.run(main())
