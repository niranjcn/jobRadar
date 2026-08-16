"""Avature ATS adapter (SSR HTML parsing).

Avature portals (e.g. jobs.siemens.com) render job search results
server-side at /en_US/externaljobs/SearchJobs. The results are paginated via
folderOffset, which must step by the page size (folderRecordsPerPage, capped
at 6 on this portal):

    /en_US/externaljobs/SearchJobs/?folderRecordsPerPage=6&folderOffset=0
    /en_US/externaljobs/SearchJobs/?folderRecordsPerPage=6&folderOffset=6

Each job is an <article> row containing:

    <a class="link" href=".../JobDetail/{id}">Title</a>
    <span class="list-item-jobCity">Pune</span>
    <span class="list-item-jobState">Maharashtra</span>
    <span class="list-item-jobCountry">India</span>
    <span class="list-item-jobId">Job ID: 514376</span>
    <span class="list-item-family">Information Technology</span>

The list rows do not include a posted date. The board_identifier is the
SearchJobs root, e.g. https://jobs.siemens.com/en_US/externaljobs.

The RSS feed (SearchJobs/feed) is not used: it caps at 20 items and is not a
reliable full listing.
"""

import asyncio
import html as html_module
import re
from datetime import UTC, datetime

import httpx

from app.adapters.base import JobSourceAdapter
from app.models import NormalizedJob

MAX_PAGES = 1000
MAX_RETRIES = 4
PAGE_DELAY_SECONDS = 0.4


class AvatureAdapter(JobSourceAdapter):
    ats_type = "avature"

    async def fetch_jobs(self, board_identifier: str) -> list[NormalizedJob]:
        search_url = board_identifier.rstrip("/")
        if not search_url.endswith("/SearchJobs"):
            search_url = f"{search_url}/SearchJobs"
        jobs: list[NormalizedJob] = []
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            offset_param = None
            per_page_param = None
            offset = 0
            empty_streak = 0
            while offset // 6 < MAX_PAGES:
                text = await self._fetch_page(
                    client, search_url, offset, offset_param, per_page_param
                )
                if offset == 0:
                    offset_param, per_page_param = _detect_pagination_params(text)
                rows = re.findall(r"<article.*?</article>", text, re.DOTALL)
                for row in rows:
                    job = self._normalize(row)
                    if job.external_job_id:
                        jobs.append(job)
                if not rows:
                    empty_streak += 1
                    if empty_streak >= MAX_RETRIES:
                        break
                    await asyncio.sleep(empty_streak)
                    continue
                empty_streak = 0
                offset += 6
                if len(rows) < 6:
                    break
                await asyncio.sleep(PAGE_DELAY_SECONDS)
        return jobs

    async def _fetch_page(
        self,
        client: httpx.AsyncClient,
        search_url: str,
        offset: int,
        offset_param: str | None = None,
        per_page_param: str | None = None,
    ) -> str:
        params: dict[str, int] = {
            (offset_param or "folderOffset"): offset,
        }
        if per_page_param:
            params[per_page_param] = 6
        else:
            params["folderRecordsPerPage"] = 6
        last_exc: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                response = await client.get(search_url, params=params)
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
    def _normalize(row: str) -> NormalizedJob:
        link_m = re.search(r'href="([^"]*JobDetail/[^"]*)"[^>]*>\s*(.*?)\s*</a>', row, re.DOTALL)
        city = _clean(re.search(r'class="list-item-jobCity"[^>]*>\s*(.*?)\s*<', row))
        state = _clean(re.search(r'class="list-item-jobState"[^>]*>\s*(.*?)\s*<', row))
        country = _clean(re.search(r'class="list-item-jobCountry"[^>]*>\s*(.*?)\s*<', row))
        family = _clean(re.search(r'class="list-item-family"[^>]*>\s*(.*?)\s*<', row))
        url = link_m.group(1) if link_m else None
        job_id = _extract_job_id(url)
        title = html_module.unescape(re.sub(r"\s+", " ", link_m.group(2))).strip() if link_m else ""
        parts = [part for part in (city, state, country) if part]
        location = ", ".join(parts) if parts else None
        posted = _clean(re.search(r'class="list-item-posted"[^>]*>\s*(.*?)\s*<', row))
        return NormalizedJob(
            external_job_id=job_id,
            title=title,
            location=location,
            url=url,
            raw_payload={"family": family, "city": city, "state": state, "country": country},
            posted_at=_parse_posted(posted),
        )

    async def fetch_job_detail(self, board_identifier: str, external_job_id: str) -> dict | None:
        base = board_identifier.rstrip("/")
        url = f"{base}/JobDetail/{external_job_id}"
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
            except httpx.HTTPError:
                return None
        text = response.text
        return self._parse_detail_html(text)

    @staticmethod
    def _parse_detail_html(text: str) -> dict:
        fields: dict[str, str] = {}
        for match in re.finditer(
            r'content__view__field__label"[^>]*>\s*(.*?)\s*</[^>]+>\s*'
            r'<[^>]+content__view__field__value"[^>]*>(.*?)</',
            text,
            re.DOTALL,
        ):
            label = _clean_string(match.group(1))
            value = _clean_string(match.group(2))
            if label and value:
                fields[label] = value
        description = ""
        desc_label = re.search(r"Job Description and Requirements\s*</[^>]+>", text)
        if desc_label:
            desc_start = desc_label.end()
            actions = text.find('<article class="article article--actions"', desc_start)
            login = text.find("Login?", desc_start)
            ends = [i for i in (actions, login) if i != -1]
            desc_end = min(ends) if ends else desc_start + 20_000
            if desc_end > desc_start:
                description = text[desc_start:desc_end]
        location = None
        city = fields.get("City")
        state = fields.get("State/Province")
        country = fields.get("Country")
        parts = [part for part in (city, state, country) if part]
        if parts:
            location = ", ".join(parts)
        return {
            "location": location,
            "posted": fields.get("Date Posted"),
            "remote": fields.get("Remote Eligible"),
            "category": fields.get("Job Category"),
            "subcategory": fields.get("Job Subcategory"),
            "content": description,
        }

    def extract_description(self, detail: dict) -> str:
        return detail.get("content") or ""


def _parse_posted(posted: str | None) -> str | None:
    """Parse an Avature 'Posted 20-Jul-2026' (or bare '20-Jul-2026') into ISO UTC."""
    if not posted:
        return None
    match = re.search(r"(\d{1,2}-[A-Za-z]{3}-\d{4})", posted)
    if not match:
        return None
    try:
        parsed = datetime.strptime(match.group(1), "%d-%b-%Y")
    except ValueError:
        return None
    return parsed.replace(tzinfo=UTC).isoformat()


def _clean(match) -> str | None:
    if not match:
        return None
    value = html_module.unescape(re.sub(r"\s+", " ", match.group(1))).strip()
    return value or None


def _clean_string(value: str) -> str | None:
    cleaned = html_module.unescape(re.sub(r"\s+", " ", value)).strip()
    return cleaned or None


def _extract_job_id(url: str | None) -> str:
    """Extract the numeric job id from a JobDetail URL.

    Supports both layouts seen in the wild:
      .../JobDetail/514376              (id directly after JobDetail)
      .../JobDetail/slug-title-13924/13924?businessTitle=...   (id in last path segment)
    """
    if not url:
        return ""
    path = url.split("?", 1)[0]
    match = re.search(r"/JobDetail/(?:[^/]+/)?(\d+)$", path)
    return match.group(1) if match else ""


def _detect_pagination_params(text: str) -> tuple[str | None, str | None]:
    """Infer the portal's pagination query-parameter names from the pager links.

    Avature portals differ: Siemens paginates with folderOffset /
    folderRecordsPerPage, Synopsys with jobOffset / jobRecordsPerPage.
    The pager links in the HTML name the real params; plain string presence
    is unreliable because feeds and other chrome also mention them. When no
    pager link is found, fall back to the folder* defaults.
    """
    pager = re.search(r"SearchJobs/\?[^\"']*(?:jobOffset|folderOffset)[^\"']*", text)
    if pager:
        query = pager.group(0)
        has_job = "jobOffset" in query
        has_folder = "folderOffset" in query
        if has_job or has_folder:
            return (
                "jobOffset" if has_job else "folderOffset",
                "jobRecordsPerPage" if "jobRecordsPerPage" in query else "folderRecordsPerPage",
            )
    return (None, None)
