"""Jobvite adapter (server-rendered HTML, single page).

Board_identifier is the company slug (e.g. ``alivecor``).
Fetches ``https://jobs.jobvite.com/{slug}`` whose ``table.jv-job-list`` rows
hold ``<a href="/{slug}/job/{id}">Title</a>`` plus a location cell::

    <td class="jv-job-list-name"><a href="/alivecor/job/oHjKAfw4">Dev/SysOps Engineer</a></td>
    <td class="jv-job-list-location">Mountain View, California</td>
"""

import html as html_module
import re

from app.adapters.base import JobSourceAdapter
from app.adapters.http import RetryingClient
from app.models import NormalizedJob


def _clean(text: str | None) -> str:
    return html_module.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text or ""))).strip()


class JobviteAdapter(JobSourceAdapter):
    ats_type = "jobvite"

    async def fetch_jobs(self, board_identifier: str, client=None) -> list[NormalizedJob]:
        slug = (board_identifier or "").strip().strip("/")
        url = f"https://jobs.jobvite.com/{slug}"
        if client is not None:
            response = await client.get(url)
            response.raise_for_status()
            text = response.text
        else:
            async with RetryingClient(timeout=30.0) as _client:
                response = await _client.get(url)
                response.raise_for_status()
                text = response.text
        return self._parse_page(text, slug)

    @staticmethod
    def _parse_page(text: str, slug: str) -> list[NormalizedJob]:
        jobs: list[NormalizedJob] = []
        for row in re.findall(r"<tr>(.*?)</tr>", text, re.DOTALL):
            job = JobviteAdapter._normalize(row, slug)
            if job is not None:
                jobs.append(job)
        return jobs

    @staticmethod
    def _normalize(row: str, slug: str) -> NormalizedJob | None:
        link = re.search(r'<a href="/[^"]*/job/([^"/]+)">(.*?)</a>', row, re.DOTALL)
        if not link:
            return None
        job_id, title = link.group(1).strip(), _clean(link.group(2))
        if not job_id or not title:
            return None
        loc = re.search(r'<td class="jv-job-list-location">(.*?)</td>', row, re.DOTALL)
        location = _clean(loc.group(1)) if loc else ""
        if not location or "locations" in location.lower():
            location = None
        return NormalizedJob(
            external_job_id=job_id,
            title=title,
            location=location,
            url=f"https://jobs.jobvite.com/{slug}/job/{job_id}",
            description="",
            raw_payload={},
            posted_at=None,
        )
