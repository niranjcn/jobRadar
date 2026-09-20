"""Breezy HR adapter (server-rendered HTML, single page).

Board_identifier is the portal subdomain (e.g. ``accrete-ai``).
Fetches ``https://{subdomain}.breezy.hr/`` which lists every opening as
``<li class="position transition">`` cards with ``/p/{id}-{slug}`` links::

    <a href="/p/2bb71f1b4ae7-ai-engineer-..." title="Apply"><h2>Title</h2>
    <ul class="meta"><li class="location">...<span>Alexandria, VA</span>
"""

import html as html_module
import re

from app.adapters.base import JobSourceAdapter
from app.adapters.http import RetryingClient
from app.models import NormalizedJob


def _clean(text: str | None) -> str:
    return html_module.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text or ""))).strip()


class BreezyAdapter(JobSourceAdapter):
    ats_type = "breezy"

    async def fetch_jobs(self, board_identifier: str, client=None) -> list[NormalizedJob]:
        url = (
            f"https://{board_identifier}/"
            if "://" in board_identifier
            else f"https://{board_identifier}.breezy.hr/"
        )
        if client is not None:
            response = await client.get(url)
            response.raise_for_status()
            text = response.text
        else:
            async with RetryingClient(timeout=30.0) as _client:
                response = await _client.get(url)
                response.raise_for_status()
                text = response.text
        root = (
            f"https://{board_identifier}.breezy.hr"
            if "://" not in board_identifier
            else board_identifier.rstrip("/")
        )
        return self._parse_page(text, root)

    @staticmethod
    def _parse_page(text: str, root: str) -> list[NormalizedJob]:
        jobs: list[NormalizedJob] = []
        for chunk in re.split(r'<li class="position transition">', text)[1:]:
            job = BreezyAdapter._normalize(chunk, root)
            if job is not None:
                jobs.append(job)
        return jobs

    @staticmethod
    def _normalize(chunk: str, root: str) -> NormalizedJob | None:
        link = re.search(
            r'<a href="(/p/([0-9a-f]+)-[^"]*)"[^>]*>\s*<h2>(.*?)</h2>', chunk, re.DOTALL
        )
        if not link:
            return None
        path, job_id, title = link.group(1), link.group(2), _clean(link.group(3))
        if not job_id or not title:
            return None
        loc = re.search(r'<li class="location">.*?<span>(.*?)</span>', chunk, re.DOTALL)
        location = _clean(loc.group(1)) if loc else None
        return NormalizedJob(
            external_job_id=job_id,
            title=title,
            location=location or None,
            url=root + path,
            description="",
            raw_payload={},
            posted_at=None,
        )
