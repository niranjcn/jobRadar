"""Phenom CareerConnect adapter (SSR HTML parsing).

Phenom sites render the job list into a script tag during server-side
rendering. For a careers root like https://careers.opentext.com, the
search-results page embeds a `phApp.ddo` object:

    var phApp = phApp || {...};
    phApp.ddo = { ... "eagerLoadRefineSearch": {
        "status": 200, "hits": 10, "totalHits": N,
        "data": { "jobs": [ {...}, ... ] }
    } ... };

Jobs are paginated server-side via ?from=N (page size 10). Each job object
contains reqId, title, city, country, postedDate, jobSeqNo, category, and
multi_location.

The job detail URL is {root}/{locale}/job/{reqId}.

Only the SSR-embedded data is used; the Phenom search-widget API
(POST {root}/widgets with ddoKey) requires a session token and is not used.
"""

import asyncio
import json
import re
from datetime import datetime

import httpx

from app.adapters.base import JobSourceAdapter
from app.models import NormalizedJob

PHENOM_PAGE_SIZE = 10
MAX_PAGES = 200
MAX_RETRIES = 4
LOCALE = "us/en"


class PhenomAdapter(JobSourceAdapter):
    ats_type = "phenom"

    async def fetch_jobs(self, board_identifier: str, client=None) -> list[NormalizedJob]:
        root = board_identifier.rstrip("/")
        base_url = f"{root}/{LOCALE}/search-results"
        jobs: list[NormalizedJob] = []

        async def _run(client) -> None:
            nonlocal jobs
            total = None
            from_offset = 0
            empty_streak = 0
            while from_offset // PHENOM_PAGE_SIZE < MAX_PAGES:
                page_jobs, total_hits = await self._fetch_page(client, base_url, from_offset)
                total = total_hits if total_hits is not None else total
                for job_data in page_jobs:
                    job = self._normalize(job_data, root)
                    if job.external_job_id:
                        jobs.append(job)
                if not page_jobs:
                    empty_streak += 1
                    if empty_streak >= MAX_RETRIES or total is None:
                        break
                    await asyncio.sleep(empty_streak)
                    continue
                empty_streak = 0
                from_offset += len(page_jobs)
                if total is not None and from_offset >= total:
                    break

        if client is not None:
            await _run(client)
        else:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as _client:
                await _run(_client)
        return jobs

    async def _fetch_page(
        self, client: httpx.AsyncClient, base_url: str, from_offset: int
    ) -> tuple[list[dict], int | None]:
        last_exc: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                response = await client.get(base_url, params={"from": from_offset})
                if response.status_code == 429:
                    raise httpx.HTTPStatusError(
                        "rate limited", request=response.request, response=response
                    )
                response.raise_for_status()
                return self._parse_page(response.text)
            except (httpx.HTTPError, ValueError) as exc:
                last_exc = exc
                await asyncio.sleep(2**attempt)
        raise last_exc or RuntimeError("failed to fetch page")

    @staticmethod
    def _parse_page(text: str) -> tuple[list[dict], int | None]:
        match = re.search(r"phApp\.ddo\s*=\s*(\{)", text)
        if not match:
            return [], None
        raw = _extract_json_object(text, match.start(1))
        if raw is None:
            return [], None
        ddo = json.loads(raw)
        refine = ddo.get("eagerLoadRefineSearch") or {}
        jobs = (refine.get("data") or {}).get("jobs") or []
        total = refine.get("totalHits")
        return jobs, int(total) if isinstance(total, int) else None

    @staticmethod
    def _normalize(job: dict, root: str) -> NormalizedJob:
        job_id = str(job.get("reqId") or job.get("jobId") or "").strip()
        title = str(job.get("title") or "").strip()
        locations = list(job.get("multi_location") or []) or []
        if not locations:
            locations = [job.get("cityStateCountry") or job.get("location") or ""]
        location = _first(locations)
        countries = []
        country = job.get("country")
        if country:
            countries.append(str(country))
        is_remote = bool(location and re.search(r"\b(virtual|remote)\b", location, re.IGNORECASE))
        return NormalizedJob(
            external_job_id=job_id,
            title=title,
            location=location,
            url=f"{root}/{LOCALE}/job/{job_id}" if root and job_id else None,
            raw_payload=job,
            posted_at=_parse_posted(job.get("postedDate")),
            countries=countries,
            is_remote=is_remote,
        )


def _extract_json_object(s: str, start: int) -> str | None:
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(s)):
        c = s[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return s[start : i + 1]
    return None


def _first(value) -> str | None:
    if isinstance(value, str):
        value = [value]
    for item in value or []:
        item = str(item).strip()
        if item:
            return item
    return None


def _parse_posted(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f%z").date().isoformat()
    except ValueError:
        pass
    try:
        return datetime.fromisoformat(value).date().isoformat()
    except ValueError:
        return None
