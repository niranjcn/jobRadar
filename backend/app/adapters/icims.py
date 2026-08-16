"""iCIMS adapter.

Supports two board_identifier formats:

1. Jibe/iCIMS JSON API (AMD, Rivian):
   board_identifier is the careers-site root, e.g. https://careers.amd.com
   Jobs are fetched from {root}/api/jobs?page=N&size=10 (page size is capped
   at 10 by the API, totalCount tells us when to stop).

2. Server-rendered TalentBrew search (Arm):
   board_identifier is the search-jobs URL,
   e.g. https://careers.arm.com/search-jobs?k=&l=&p={page}
   Job cards are parsed from the HTML (data-job-id, .location, .category).
"""

import html
import re

from app.adapters.base import JobSourceAdapter
from app.adapters.http import RetryingClient
from app.models import NormalizedJob

PAGE_SIZE = 10
JSON_API_MAX_PAGES = 3000


class IcimsAdapter(JobSourceAdapter):
    ats_type = "icims"

    async def fetch_jobs(self, board_identifier: str) -> list[NormalizedJob]:
        if board_identifier.startswith("http") and "/search-jobs" in board_identifier:
            return await self._fetch_html_jobs(board_identifier)
        if board_identifier.startswith("http") and "/api/jobs" in board_identifier:
            return await self._fetch_json_jobs(board_identifier)
        if board_identifier.startswith("http"):
            return await self._fetch_json_jobs(f"{board_identifier.rstrip('/')}/api/jobs")
        return await self._fetch_json_jobs(f"https://{board_identifier}/api/jobs")

    async def _fetch_json_jobs(self, api_url: str) -> list[NormalizedJob]:
        jobs: list[NormalizedJob] = []
        async with RetryingClient(timeout=30.0) as client:
            page = 1
            while page <= JSON_API_MAX_PAGES:
                response = await client.get(
                    api_url,
                    params={"page": page, "size": PAGE_SIZE},
                    headers={"Accept": "application/json"},
                )
                response.raise_for_status()
                payload = response.json()
                entries = payload.get("jobs") or []
                jobs.extend(self._normalize_json(entry) for entry in entries)
                total = int(payload.get("totalCount") or 0)
                if page * PAGE_SIZE >= total or len(entries) == 0:
                    break
                page += 1
        return jobs

    @staticmethod
    def _normalize_json(entry: dict) -> NormalizedJob:
        data = entry.get("data") or {}
        location = data.get("short_location") or data.get("full_location") or data.get("location_name")
        return NormalizedJob(
            external_job_id=str(data.get("req_id") or data.get("slug") or ""),
            title=data.get("title") or "",
            location=location,
            url=data.get("apply_url") or data.get("url"),
            raw_payload=data,
            posted_at=(data.get("posted_date") or data.get("create_date")) or None,
        )

    async def _fetch_html_jobs(self, search_url: str) -> list[NormalizedJob]:
        jobs: list[NormalizedJob] = []
        seen: set[str] = set()
        async with RetryingClient(timeout=30.0, follow_redirects=True) as client:
            page = 1
            while page <= JSON_API_MAX_PAGES:
                url = re.sub(r"p=\d+", f"p={page}", search_url) if "p=" in search_url else search_url
                response = await client.get(url)
                response.raise_for_status()
                text = response.text
                # Parse only the main results list (the page also renders
                # recommended/recently-viewed sections that repeat the same jobs).
                results_m = re.search(
                    r'<ul class="list-reset" id="search-results-jobs".*?</ul>', text, re.DOTALL
                )
                results_block = results_m.group(0) if results_m else text
                cards = re.findall(r'<li class="job-card.*?</li>', results_block, re.DOTALL)
                if not cards:
                    break
                page_jobs = [self._normalize_html(card, search_url) for card in cards]
                for job in page_jobs:
                    if job.external_job_id and job.external_job_id not in seen:
                        seen.add(job.external_job_id)
                        jobs.append(job)
                if "p=" not in search_url:
                    break
                next_links = [int(n) for n in re.findall(r"/search-jobs&amp;p=(\d+)", text)]
                if not next_links or max(next_links) <= page:
                    break
                page += 1
        return jobs

    @staticmethod
    def _normalize_html(card: str, search_url: str) -> NormalizedJob:
        title_m = re.search(r'data-job-id="(\d+)"[^>]*>(.*?)</a>', card, re.DOTALL)
        href_m = re.search(r'href="(/job/[^"]+)"', card)
        location_m = re.search(r'<span class="location">(.*?)</span>', card, re.DOTALL)
        title = title_m.group(2) if title_m else ""
        title = html.unescape(re.sub(r"\s+", " ", title).strip())
        base = re.match(r"https?://[^/]+", search_url)
        root = base.group(0) if base else "https://careers.arm.com"
        return NormalizedJob(
            external_job_id=title_m.group(1) if title_m else "",
            title=title,
            location=location_m.group(1).strip() if location_m else None,
            url=f"{root}{href_m.group(1)}" if href_m else None,
            raw_payload={"card": card},
        )
