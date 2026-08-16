from app.adapters.base import JobSourceAdapter
from app.adapters.http import RetryingClient
from app.models import NormalizedJob

BOARDS_API_BASE = "https://boards-api.greenhouse.io/v1/boards"


class GreenhouseAdapter(JobSourceAdapter):
    ats_type = "greenhouse"

    async def fetch_jobs(self, board_identifier: str) -> list[NormalizedJob]:
        url = f"{BOARDS_API_BASE}/{board_identifier}/jobs"
        async with RetryingClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            payload = response.json()
        return [self._normalize(job) for job in payload.get("jobs", [])]

    @staticmethod
    def _normalize(job: dict) -> NormalizedJob:
        location = (job.get("location") or {}).get("name")
        return NormalizedJob(
            external_job_id=str(job.get("id")),
            title=job.get("title") or "",
            location=location,
            url=job.get("absolute_url"),
            raw_payload=job,
            posted_at=job.get("first_published"),
        )

    async def fetch_job_detail(self, board_identifier: str, external_job_id: str) -> dict | None:
        url = f"{BOARDS_API_BASE}/{board_identifier}/jobs/{external_job_id}"
        async with RetryingClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
        return response.json()
