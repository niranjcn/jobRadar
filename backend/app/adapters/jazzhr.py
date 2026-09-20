"""JazzHR adapter (server-rendered HTML, single page).

Board_identifier is the portal subdomain (e.g. ``antler``).
Fetches ``https://{subdomain}.applytojob.com/apply/jobs`` whose
``<tr id="row_job_...">`` rows hold the title link, department and location::

    <tr id="row_job_...">
      <td><a class="job_title_link" href="/apply/jobs/details/{id}?&">Title</a>
        <br /><span class="resumator_department">Dept</span></td>
      <td>Location</td></tr>
"""

import html as html_module
import re

from app.adapters.base import JobSourceAdapter
from app.adapters.http import RetryingClient
from app.models import NormalizedJob


def _clean(text: str | None) -> str:
    return html_module.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text or ""))).strip()


class JazzhrAdapter(JobSourceAdapter):
    ats_type = "jazzhr"

    async def fetch_jobs(self, board_identifier: str, client=None) -> list[NormalizedJob]:
        token = (board_identifier or "").strip().rstrip("/")
        if "://" in token:
            base = token.rstrip("/")
        else:
            base = f"https://{token}.applytojob.com"
        url = f"{base}/apply/jobs"
        if client is not None:
            response = await client.get(url)
            response.raise_for_status()
            text = response.text
        else:
            async with RetryingClient(timeout=30.0) as _client:
                response = await _client.get(url)
                response.raise_for_status()
                text = response.text
        return self._parse_page(text, base)

    @staticmethod
    def _parse_page(text: str, base: str) -> list[NormalizedJob]:
        jobs: list[NormalizedJob] = []
        for chunk in re.split(r'<tr id="row_job_', text)[1:]:
            job = JazzhrAdapter._normalize(chunk, base)
            if job is not None:
                jobs.append(job)
        return jobs

    @staticmethod
    def _normalize(chunk: str, base: str) -> NormalizedJob | None:
        link = re.search(
            r'<a class="job_title_link" href="/apply/jobs/details/([^"?&]+)[^"]*">(.*?)</a>',
            chunk,
            re.DOTALL,
        )
        if not link:
            return None
        job_id, title = link.group(1).strip(), _clean(link.group(2))
        if not job_id or not title:
            return None
        tds = re.findall(r"<td>(.*?)</td>", chunk, re.DOTALL)
        location = _clean(tds[-1]) if tds else ""
        return NormalizedJob(
            external_job_id=job_id,
            title=title,
            location=location or None,
            url=f"{base}/apply/jobs/details/{job_id}",
            description="",
            raw_payload={},
            posted_at=None,
        )
