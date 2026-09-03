"""Adapter for Remotive — remote job board with public JSON API.

API: https://remotive.com/api/remote-jobs
     Public, no auth. Returns ~19-500 jobs per call (search-filtered).
     Also supports ?search=<keyword> and ?category=<slug> but we fetch all
     and let the poller's matcher filter. Board identifier is the search/category
     token — default "all" fetches unfiltered.

See docs/board-adapters-plan.md Phase A.
"""

from datetime import UTC

from app.adapters.base import JobSourceAdapter
from app.adapters.http import RetryingClient
from app.models import NormalizedJob

API_BASE = "https://remotive.com/api/remote-jobs"


class RemotiveAdapter(JobSourceAdapter):
    ats_type = "remotive"

    async def fetch_jobs(self, board_identifier: str, client=None) -> list[NormalizedJob]:
        # board_identifier: "all" (default, in sources.json) or a search/category slug.
        # "all" -> unfiltered feed (~19 jobs currently, paginated by Remotive API limit).
        url = API_BASE
        params: dict[str, str] = {}
        # Keep identifier semantics: "remotive" or "all" means full feed.
        # Any other non-empty token is treated as ?search=<token> so we can add
        # category-specific rows later without code change (e.g., "python", "software-development").
        token = (board_identifier or "").strip().lower()
        if token and token not in ("all", "remotive"):
            params["search"] = token

        if client is not None:
            response = await client.get(url, params=params or None)
            response.raise_for_status()
            payload = response.json()
        else:
            async with RetryingClient(timeout=30.0) as _client:
                response = await _client.get(url, params=params or None)
                response.raise_for_status()
                payload = response.json()

        jobs = payload.get("jobs", []) or []
        return [self._normalize(job) for job in jobs if job.get("id")]

    @staticmethod
    def _normalize(job: dict) -> NormalizedJob:
        # Use Remotive's publication_date as posted_at; fall back to None so
        # poller.py:_is_within_age keeps it (missing date = not filtered).
        posted = job.get("publication_date")
        # Ensure ISO; Remotive is like "2026-08-27T14:36:09"
        if posted and "T" in posted and not posted.endswith("Z"):
            # Attach UTC if naive
            try:
                from datetime import datetime

                dt = datetime.fromisoformat(posted)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=UTC)
                posted = dt.isoformat()
            except Exception:
                pass

        return NormalizedJob(
            external_job_id=str(job.get("id")),
            title=(job.get("title") or "").strip(),
            location=job.get("candidate_required_location")
            or job.get("candidate_required_location")
            or "Remote",
            url=job.get("url"),
            description=job.get("description") or "",
            raw_payload=job,
            posted_at=posted,
        )
