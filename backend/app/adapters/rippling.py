"""Rippling ATS adapter (embedded Next.js data, paged).

Board_identifier is the board slug (e.g. ``aerospike-inc``).
Fetches ``https://ats.rippling.com/{slug}/jobs`` and parses the embedded
``__NEXT_DATA__`` payload: ``dehydratedState.queries[]`` holds the
``job-posts`` query with ``{items, page, pageSize, totalItems, totalPages}``.
Further pages are fetched via ``?page=N`` (server-rendered per page); a page
that only repeats known ids terminates the loop::

    {"id": "<uuid>", "name": "Title", "url": "https://ats.rippling.com/...",
     "department": {"name": "Engineering"},
     "locations": [{"city": ..., "state": ..., "country": ...,
                    "countryCode": "US", "workplaceType": "ON_SITE"}]}
"""

import json
import re

from app.adapters.base import JobSourceAdapter
from app.adapters.http import RetryingClient
from app.models import NormalizedJob


def _extract_next_data(text: str) -> dict | None:
    match = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', text, re.DOTALL
    )
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None


def _job_posts_page(data: dict | None) -> tuple[list[dict], int, int]:
    """Return (items, page, totalPages) from the embedded job-posts query."""
    if not data:
        return [], 0, 1
    try:
        queries = data["props"]["pageProps"]["dehydratedState"]["queries"]
    except (KeyError, TypeError):
        return [], 0, 1
    for query in queries:
        try:
            key = json.dumps(query.get("queryKey") or [])
        except (TypeError, ValueError):
            continue
        if "job-posts" not in key:
            continue
        payload = (query.get("state") or {}).get("data") or {}
        items = payload.get("items") or []
        try:
            page = int(payload.get("page") or 0)
        except (TypeError, ValueError):
            page = 0
        try:
            total_pages = int(payload.get("totalPages") or 1)
        except (TypeError, ValueError):
            total_pages = 1
        return items, page, max(total_pages, 1)
    return [], 0, 1


class RipplingAdapter(JobSourceAdapter):
    ats_type = "rippling"

    async def fetch_jobs(self, board_identifier: str, client=None) -> list[NormalizedJob]:
        slug = (board_identifier or "").strip().strip("/")
        base = slug if "://" in slug else f"https://ats.rippling.com/{slug}"
        url = f"{base.rstrip('/')}/jobs"
        if client is not None:
            return await self._fetch_all(client, url)
        async with RetryingClient(timeout=30.0) as _client:
            return await self._fetch_all(_client, url)

    async def _fetch_all(self, client, url: str) -> list[NormalizedJob]:
        jobs: list[NormalizedJob] = []
        seen: set[str] = set()
        page = 0
        while True:
            target = url if page == 0 else f"{url}?page={page}"
            response = await client.get(target)
            response.raise_for_status()
            items, _, total_pages = _job_posts_page(_extract_next_data(response.text))
            if not items:
                break
            fresh = False
            for item in items:
                job = self._normalize(item)
                if job is None or job.external_job_id in seen:
                    continue
                seen.add(job.external_job_id)
                jobs.append(job)
                fresh = True
            if not fresh or page + 1 >= total_pages:
                break
            page += 1
        return jobs

    @staticmethod
    def _normalize(item: dict) -> NormalizedJob | None:
        job_id = item.get("id")
        title = (item.get("name") or "").strip()
        if not job_id or not title:
            return None
        locs = []
        countries: list[str] = []
        remote = False
        for loc in item.get("locations") or []:
            city = (loc.get("city") or "").strip()
            state = (loc.get("state") or "").strip()
            country = (loc.get("country") or "").strip()
            label = ", ".join(p for p in (city, state, country) if p)
            if label:
                locs.append(label)
            cc = (loc.get("countryCode") or "").strip().upper()
            if len(cc) == 2 and cc not in countries:
                countries.append(cc)
            if (loc.get("workplaceType") or "").upper() == "REMOTE":
                remote = True
        location = "; ".join(locs) or None
        if location is None and remote:
            location = "Remote"
        return NormalizedJob(
            external_job_id=str(job_id),
            title=title,
            location=location,
            url=item.get("url"),
            description="",
            raw_payload=item,
            posted_at=None,
            countries=countries,
            is_remote=remote,
        )
