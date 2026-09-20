"""SmartRecruiters ATS adapter.

Board_identifier is the company slug (e.g. ``abbvie``).
Uses the public postings endpoint (no auth):
  GET https://api.smartrecruiters.com/v1/companies/{slug}/postings?limit=100&offset=N
which returns ``{"totalFound": N, "content": [...]}``.
"""

from app.adapters.base import JobSourceAdapter
from app.adapters.http import RetryingClient
from app.models import NormalizedJob

POSTINGS_API_BASE = "https://api.smartrecruiters.com/v1/companies"
PAGE_SIZE = 100


class SmartRecruitersAdapter(JobSourceAdapter):
    ats_type = "smartrecruiters"

    async def fetch_jobs(self, board_identifier: str, client=None) -> list[NormalizedJob]:
        slug = (board_identifier or "").strip()
        if client is not None:
            return await self._fetch_all(client, slug)
        async with RetryingClient(timeout=30.0) as _client:
            return await self._fetch_all(_client, slug)

    async def _fetch_all(self, client, slug: str) -> list[NormalizedJob]:
        jobs: list[NormalizedJob] = []
        offset = 0
        total: int | None = None
        while True:
            response = await client.get(
                f"{POSTINGS_API_BASE}/{slug}/postings",
                params={"limit": PAGE_SIZE, "offset": offset},
            )
            response.raise_for_status()
            payload = response.json()
            if total is None:
                try:
                    total = int(payload.get("totalFound") or 0)
                except (TypeError, ValueError):
                    total = 0
            content = payload.get("content") or []
            if not content:
                break
            for posting in content:
                job = self._normalize(slug, posting)
                if job is not None:
                    jobs.append(job)
            offset += len(content)
            if total is not None and offset >= total:
                break
        return jobs

    @staticmethod
    def _normalize(slug: str, posting: dict) -> NormalizedJob | None:
        job_id = posting.get("id")
        if job_id is None or str(job_id).strip() == "":
            return None
        company = posting.get("company") or {}
        identifier = company.get("identifier") or slug
        loc = posting.get("location") or {}
        remote = bool(loc.get("remote"))
        location = (loc.get("fullLocation") or "").strip() or ", ".join(
            p.strip()
            for p in (loc.get("city") or "", loc.get("region") or "", loc.get("country") or "")
            if p.strip()
        )
        location = location or None
        if location is None and remote:
            location = "Remote"
        cc = (loc.get("country") or "").strip().upper()
        return NormalizedJob(
            external_job_id=str(job_id),
            title=(posting.get("name") or "").strip(),
            location=location,
            url=f"https://jobs.smartrecruiters.com/{identifier}/{job_id}",
            description="",
            raw_payload=posting,
            posted_at=posting.get("releasedDate"),
            countries=[cc] if len(cc) == 2 else [],
            is_remote=remote,
        )
