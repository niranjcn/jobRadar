import asyncio
import httpx

from app.adapters.oracle import (
    OracleAdapter,
    FUSION_SEARCH_PATH,
    FUSION_FACETS,
    FUSION_EXPAND,
    FUSION_ACTION,
    FUSION_CONTENT_TYPE,
    TZ_HEADERS,
)


async def main() -> None:
    base = "https://careers.americanexpress.com/en/sites/CX_1"
    adapter = OracleAdapter()
    host, site_number = await adapter._fusion_endpoint(base)
    print("host:", host, "site:", site_number)
    site_root = adapter._fusion_site_root(base)
    print("site_root:", site_root)
    search_url = f"{host}{FUSION_SEARCH_PATH}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            search_url,
            json={
                "siteNumber": site_number,
                "limit": 3,
                "offset": 0,
                "facets": FUSION_FACETS,
                "input": "",
                "expand": FUSION_EXPAND,
                "sortBy": "POSTING_DATES_DESC",
            },
            headers={
                "Content-Type": FUSION_CONTENT_TYPE,
                "Ora-Irc-Rest-Action": FUSION_ACTION,
                **TZ_HEADERS,
            },
        )
        print("status:", response.status_code)
        if response.status_code == 200:
            data = response.json()
            item = (data.get("items") or [{}])[0]
            postings = item.get("requisitionList") or []
            print("total:", item.get("totalJobsCount"))
            for p in postings[:3]:
                j = adapter._normalize_fusion(site_root, site_number, p)
                print("  ", j.title[:60], "|", j.location, "|", j.url)


asyncio.run(main())