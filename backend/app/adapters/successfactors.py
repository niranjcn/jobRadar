"""SAP SuccessFactors adapter.

Supports two board_identifier formats:

1. Recruiting API (Wipro, HCLTech):
   board_identifier is the careers-site root, e.g. https://careers.wipro.com
   Jobs are fetched via POST {root}/services/recruiting/v1/jobs with
   {"keywords": "", "locale": "en_US", "location": "", "pageNumber": N,
   "sortBy": "recent"}. The API returns 10 jobs per page; totalJobs tells us
   when to stop. Transient rate-limits (empty/HTML pages mid-pagination) are
   retried with backoff instead of aborting the whole source early.
"""

import asyncio
import html
import re
from datetime import datetime

import httpx

from app.adapters.base import JobSourceAdapter
from app.models import NormalizedJob

API_PAGE_SIZE = 10
MAX_PAGES = 2000
MAX_RETRIES = 4
LOCALE = "en_US"


class SuccessFactorsAdapter(JobSourceAdapter):
    ats_type = "successfactors"

    async def fetch_jobs(self, board_identifier: str) -> list[NormalizedJob]:
        if "/search-jobs" in board_identifier:
            return await self._fetch_html_jobs(board_identifier)
        if "/services/recruiting/v1/jobs" in board_identifier:
            return await self._fetch_api_jobs(board_identifier)
        return await self._fetch_api_jobs(f"{board_identifier.rstrip('/')}/services/recruiting/v1/jobs")

    async def _fetch_api_jobs(self, api_url: str) -> list[NormalizedJob]:
        jobs: list[NormalizedJob] = []
        root = api_url.split("/services/")[0]
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            page_number = 0
            empty_streak = 0
            while page_number < MAX_PAGES:
                payload = await self._fetch_api_page(client, api_url, root, page_number)
                entries = payload.get("jobSearchResult") or []
                for entry in entries:
                    job = self._normalize_api(entry.get("response") or {}, root)
                    if job.external_job_id:
                        jobs.append(job)
                total = int(payload.get("totalJobs") or 0)
                if (page_number + 1) * API_PAGE_SIZE >= total:
                    break
                if len(entries) == 0:
                    # Empty page before total reached: transient rate-limit.
                    empty_streak += 1
                    if empty_streak >= MAX_RETRIES:
                        break
                    await asyncio.sleep(empty_streak)
                    continue
                empty_streak = 0
                page_number += 1
        return jobs

    async def _fetch_api_page(self, client: httpx.AsyncClient, api_url: str, root: str, page_number: int) -> dict:
        last_exc: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                response = await client.post(
                    api_url,
                    json={
                        "keywords": "",
                        "locale": LOCALE,
                        "location": "",
                        "pageNumber": page_number,
                        "sortBy": "recent",
                    },
                    headers={"Content-Type": "application/json", "Origin": root},
                )
                if response.status_code == 429:
                    raise httpx.HTTPStatusError(
                        "rate limited", request=response.request, response=response
                    )
                response.raise_for_status()
                return response.json()
            except (httpx.HTTPError, ValueError) as exc:
                last_exc = exc
                await asyncio.sleep(2**attempt)
        raise last_exc or RuntimeError("failed to fetch page")

    @staticmethod
    def _normalize_api(resp: dict, root: str) -> NormalizedJob:
        job_id = str(resp.get("id") or "")
        url_title = resp.get("urlTitle") or resp.get("unifiedUrlTitle") or ""
        countries = [
            c
            for c in list(resp.get("jobLocationCountry") or []) + list(resp.get("custCountryRegion") or [])
            if c
        ]
        location = _first(
            resp.get("jobLocationShort")
            or resp.get("sfstd_jobLocation_obj")
            or resp.get("custprimecity")
        )
        if location:
            location = re.sub(r"<[^>]+>", " ", location)
            location = re.sub(r"\s+", " ", location).strip()
        return NormalizedJob(
            external_job_id=job_id,
            title=resp.get("unifiedStandardTitle") or resp.get("title") or "",
            location=location,
            url=f"{root}/job/{url_title}/{job_id}/" if url_title and job_id else None,
            raw_payload=resp,
            posted_at=_parse_start(resp.get("unifiedStandardStart")),
            countries=countries,
        )

    async def _fetch_html_jobs(self, search_url: str) -> list[NormalizedJob]:
        jobs: list[NormalizedJob] = []
        base = re.match(r"https?://[^/]+", search_url)
        root = base.group(0) if base else ""
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            url = search_url
            current = 0
            visited: set[int] = set()
            while True:
                text = await self._fetch_html_page(client, url)
                table = re.search(r'<table id="searchresults".*?</table>', text, re.DOTALL)
                block = table.group(0) if table else text
                rows = re.findall(r'<tr class="data-row">(.*?)</tr>', block, re.DOTALL)
                if not rows:
                    break
                jobs.extend(self._normalize_html(row, root) for row in rows)
                next_hrefs = sorted(
                    {
                        href
                        for href in re.findall(r'href="(\?[^"]*startrow=\d+[^"]*)"', html.unescape(text))
                    },
                    key=lambda h: int(re.search(r"startrow=(\d+)", h).group(1)),
                )
                next_startrow = None
                for href in next_hrefs:
                    startrow = int(re.search(r"startrow=(\d+)", href).group(1))
                    if startrow > current and startrow not in visited:
                        next_startrow = startrow
                        next_url = f"{root}/search-jobs/Results{href}"
                        break
                if next_startrow is None:
                    break
                visited.add(next_startrow)
                current = next_startrow
                url = next_url
        return jobs

    async def _fetch_html_page(self, client: httpx.AsyncClient, url: str) -> str:
        last_exc: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                response = await client.get(url)
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
    def _normalize_html(row: str, root: str) -> NormalizedJob:
        title_m = re.search(r'class="jobTitle-link"[^>]*>(.*?)</a>', row, re.DOTALL)
        href_m = re.search(r'href="(/job/[^"]+)"', row)
        loc_m = re.search(r'class="jobLocation"[^>]*>\s*(.*?)</', row, re.DOTALL)
        date_m = re.search(r'class="jobDate"[^>]*>\s*(.*?)</', row, re.DOTALL)
        title = html.unescape(re.sub(r"\s+", " ", title_m.group(1)).strip()) if title_m else ""
        href = href_m.group(1) if href_m else ""
        job_id = href.rstrip("/").rsplit("/", 1)[-1] if href else ""
        location = html.unescape(re.sub(r"\s+", " ", loc_m.group(1)).strip()) if loc_m else None
        return NormalizedJob(
            external_job_id=job_id,
            title=title,
            location=location,
            url=f"{root}{href}" if root and href else None,
            raw_payload={"row": row},
            posted_at=_parse_j2w_date(date_m.group(1).strip() if date_m else None),
        )


def _first(values) -> str | None:
    if isinstance(values, str):
        values = [values]
    for value in values or []:
        value = str(value).strip()
        if value:
            return value
    return None


def _parse_start(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%m/%d/%y").date().isoformat()
    except ValueError:
        return None


def _parse_j2w_date(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%b %d, %Y").date().isoformat()
    except ValueError:
        return None
