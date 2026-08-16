from app.adapters.base import JobSourceAdapter
from app.adapters.http import RetryingClient
from app.models import NormalizedJob

POSTINGS_API_BASE = "https://api.ashbyhq.com/posting-api/job-board"


class AshbyAdapter(JobSourceAdapter):
    ats_type = "ashby"

    async def fetch_jobs(self, board_identifier: str) -> list[NormalizedJob]:
        url = f"{POSTINGS_API_BASE}/{board_identifier}"
        async with RetryingClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            payload = response.json()
        return [self._normalize(job) for job in payload.get("jobs", [])]

    @staticmethod
    def _normalize(job: dict) -> NormalizedJob:
        secondary = [s.get("location") for s in (job.get("secondaryLocations") or [])]
        locations = [loc for loc in [job.get("location"), *secondary] if loc]
        return NormalizedJob(
            external_job_id=job.get("id") or "",
            title=(job.get("title") or "").strip(),
            location=", ".join(locations) or None,
            url=job.get("jobUrl") or job.get("applyUrl"),
            description=job.get("descriptionPlain") or "",
            raw_payload=job,
            posted_at=job.get("publishedAt"),
        )