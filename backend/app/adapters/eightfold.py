"""Eightfold.ai adapter (positions JSON embedded in the careers page).

Board_identifier is the tenant slug (e.g. ``albemarle``).
Fetches ``https://{slug}.eightfold.ai/careers`` and extracts the embedded
``"positions": [...]`` array via bracket matching::

    {"id": 1099555988595, "posting_name": "Title",
     "location": "Bengaluru, Karnataka, India",
     "locations": [...], "department": ...,
     "t_create": 1788134400, "ats_job_id": "REQ-31366",
     "work_location_option": "onsite",
     "canonicalPositionUrl": "https://{slug}.eightfold.ai/careers/job/<id>"}
"""

import html as html_module
import json
from datetime import UTC, datetime

from app.adapters.base import JobSourceAdapter
from app.adapters.http import RetryingClient
from app.models import NormalizedJob


def _extract_positions(text: str) -> list[dict] | None:
    """Bracket-match the embedded ``"positions": [...]`` array (None if absent)."""
    anchor = text.find('"positions"')
    if anchor == -1:
        return None
    start = text.find("[", anchor)
    if start == -1:
        return None
    depth = 0
    in_string = False
    escaped = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                try:
                    parsed = json.loads(text[start : i + 1])
                except json.JSONDecodeError:
                    return None
                return parsed if isinstance(parsed, list) else None
    return None


class EightfoldAdapter(JobSourceAdapter):
    ats_type = "eightfold"

    async def fetch_jobs(self, board_identifier: str, client=None) -> list[NormalizedJob]:
        token = (board_identifier or "").strip().rstrip("/")
        base = token if "://" in token else f"https://{token}.eightfold.ai"
        url = f"{base.rstrip('/')}/careers"
        if client is not None:
            text, final_base = await self._fetch_page(client, url, base)
        else:
            async with RetryingClient(timeout=30.0) as _client:
                text, final_base = await self._fetch_page(_client, url, base)
        jobs: list[NormalizedJob] = []
        for position in _extract_positions(text) or []:
            job = self._normalize(final_base, position)
            if job is not None:
                jobs.append(job)
        return jobs

    @staticmethod
    async def _fetch_page(client, url: str, base: str) -> tuple[str, str]:
        """GET with manual redirect follow (boards move to custom domains, e.g.
        career.mlp.com) and HTML-unescape: bot renders escape the embedded JSON
        (&#34;positions&#34;), so unescape before bracket matching."""
        response = await client.get(url)
        hops = 0
        while response.is_redirect and hops < 3:
            location = response.headers.get("location")
            if not location:
                break
            response = await client.get(location)
            hops += 1
        response.raise_for_status()
        text = html_module.unescape(response.text)
        if hops:
            final = str(response.url).rstrip("/")
            base = final.removesuffix("/careers")
        return text, base

    @staticmethod
    def _normalize(base: str, position: dict) -> NormalizedJob | None:
        job_id = position.get("id")
        title = (position.get("posting_name") or position.get("name") or "").strip()
        if job_id is None or str(job_id).strip() == "" or not title:
            return None
        locs = [str(loc).strip() for loc in (position.get("locations") or []) if str(loc).strip()]
        location = "; ".join(locs) or (position.get("location") or "").strip() or None
        posted_at = None
        created = position.get("t_create")
        try:
            posted_at = (
                datetime.fromtimestamp(int(created), tz=UTC).isoformat() if created else None
            )
        except (TypeError, ValueError, OverflowError, OSError):
            posted_at = None
        remote = (position.get("work_location_option") or "").lower() == "remote"
        if location is None and remote:
            location = "Remote"
        return NormalizedJob(
            external_job_id=str(job_id),
            title=title,
            location=location,
            url=position.get("canonicalPositionUrl") or f"{base}/careers/job/{job_id}",
            description="",
            raw_payload={},
            posted_at=posted_at,
            countries=[],
            is_remote=remote,
        )
