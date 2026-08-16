"""Custom career page adapter (SSR HTML parsing).

Used for companies that do not use a standard ATS. The first supported
platform is the J2W ("jobs2web") site builder, e.g.
careers.irissoftware.com. It renders job search results server-side at
/tile-search-results, paginated by startrow:

    /tile-search-results?q=&startrow=0
    /tile-search-results?q=&startrow=25
    ...

The page reports the total result count via aria-rowcount on the job list.
Each job is a <li class="job-tile"> row containing:

    <li class="job-tile job-id-{id} ..." data-url="/job/{slug}/{id}/">
        <a class="jobTitle-link" href="/job/{slug}/{id}/">Title</a>
        <div ...section-location-value">Noida, UP, India</div>
        <div ...section-date-value">14 Aug 2026</div>
        <div ...section-customfield1-value">34361</div>

The stable external id is the numeric id in the /job/{slug}/{id}/ URL.

Job detail pages (/job/{slug}/{id}/) add the full description and confirm
location/date; the board_identifier is the careers site root.
"""

import asyncio
import html as html_module
import re
from datetime import UTC, datetime

import httpx

from app.adapters.base import JobSourceAdapter
from app.models import NormalizedJob

PAGE_SIZE = 25
MAX_PAGES = 400
MAX_RETRIES = 4
PAGE_DELAY_SECONDS = 0.4


class CustomAdapter(JobSourceAdapter):
    ats_type = "custom"

    async def fetch_jobs(self, board_identifier: str) -> list[NormalizedJob]:
        base = board_identifier.rstrip("/")
        jobs: list[NormalizedJob] = []
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            total: int | None = None
            offset = 0
            for page in range(MAX_PAGES):
                text = await self._fetch_page(client, base, offset)
                tiles = re.findall(r'<li[^>]*class="[^"]*job-tile[^"]*".*?</li>', text, re.DOTALL)
                for tile in tiles:
                    job = self._normalize(tile, base)
                    if job.external_job_id:
                        jobs.append(job)
                if total is None:
                    m = re.search(r'aria-rowcount="(\d+)"', text)
                    if m:
                        total = int(m.group(1))
                if not tiles:
                    break
                page_size = len(tiles)
                offset += page_size
                if total is not None and offset >= total:
                    break
                if page_size < PAGE_SIZE:
                    break
                await asyncio.sleep(PAGE_DELAY_SECONDS)
        return jobs

    async def _fetch_page(self, client: httpx.AsyncClient, base: str, offset: int) -> str:
        url = f"{base}/tile-search-results"
        last_exc: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                response = await client.get(url, params={"q": "", "startrow": offset})
                if response.status_code == 429:
                    raise httpx.HTTPStatusError(
                        "rate limited", request=response.request, response=response
                    )
                response.raise_for_status()
                return response.text
            except (httpx.HTTPError, ValueError) as exc:
                last_exc = exc
                await asyncio.sleep(2**attempt)
        raise last_exc or RuntimeError("failed to fetch page")

    @staticmethod
    def _normalize(tile: str, base: str | None = None) -> NormalizedJob:
        url = _clean(re.search(r'data-url="([^"]*)"', tile))
        title = _clean(
            re.search(r'class="jobTitle-link[^"]*"[^>]*>\s*(.*?)\s*</a>', tile, re.DOTALL)
        )
        location = _clean(re.search(r'section-location-value"\s*>([^<]+?)\s*<', tile))
        posted = _clean(re.search(r'section-date-value"\s*>([^<]+?)\s*<', tile))
        job_id = _extract_job_id(url)
        if url and base and url.startswith("/"):
            url = f"{base.rstrip('/')}{url}"
        return NormalizedJob(
            external_job_id=job_id,
            title=title or "",
            location=location,
            url=url,
            raw_payload={
                "requisition": _clean(
                    re.search(r'section-customfield1-value"\s*>([^<]+?)\s*<', tile)
                )
            },
            posted_at=_parse_posted(posted),
        )

    async def fetch_job_detail(self, board_identifier: str, external_job_id: str) -> dict | None:
        # J2W detail URLs are /job/{slug}/{id}/ where the slug is only known from
        # the list row. The list tiles already carry title/location/date, so
        # enrichment adds nothing the list does not provide; skip it.
        return None

    def extract_description(self, detail: dict) -> str:
        return detail.get("content") or ""


def _parse_posted(posted: str | None) -> str | None:
    """Parse a J2W posted date '14 Aug 2026' into ISO UTC."""
    if not posted:
        return None
    try:
        parsed = datetime.strptime(posted, "%d %b %Y")
    except ValueError:
        return None
    return parsed.replace(tzinfo=UTC).isoformat()


def _clean(match) -> str | None:
    if not match:
        return None
    value = html_module.unescape(re.sub(r"\s+", " ", match.group(1))).strip()
    return value or None


def _extract_job_id(url: str | None) -> str:
    """Extract the numeric job id from /job/{slug}/{id}/ URLs."""
    if not url:
        return ""
    path = url.split("?", 1)[0]
    match = re.search(r"/job/[^/]+/(\d+)/?$", path)
    return match.group(1) if match else ""
