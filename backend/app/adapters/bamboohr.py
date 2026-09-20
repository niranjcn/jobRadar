"""BambooHR adapter (public JSON list, single request).

Board_identifier is the company subdomain (e.g. ``reach52``).
Fetches ``https://{subdomain}.bamboohr.com/careers/list`` which returns::

    {"meta": {"totalCount": N}, "result": [{"id": "83",
      "jobOpeningName": "Title", "departmentLabel": ...,
      "employmentStatusLabel": "Full-Time",
      "location": {"city": ..., "state": ...}, "isRemote": ...}]}
"""

from app.adapters.base import JobSourceAdapter
from app.adapters.http import RetryingClient
from app.models import NormalizedJob


class BamboohrAdapter(JobSourceAdapter):
    ats_type = "bamboohr"

    async def fetch_jobs(self, board_identifier: str, client=None) -> list[NormalizedJob]:
        sub = (board_identifier or "").strip().rstrip("/")
        if "://" in sub:
            base = sub.rstrip("/")
        else:
            base = f"https://{sub}.bamboohr.com"
        url = f"{base}/careers/list"
        if client is not None:
            response = await client.get(url)
            response.raise_for_status()
            payload = response.json()
        else:
            async with RetryingClient(timeout=30.0) as _client:
                response = await _client.get(url)
                response.raise_for_status()
                payload = response.json()
        jobs: list[NormalizedJob] = []
        for entry in payload.get("result", []) or []:
            job = self._normalize(base, entry)
            if job is not None:
                jobs.append(job)
        return jobs

    @staticmethod
    def _normalize(base: str, entry: dict) -> NormalizedJob | None:
        job_id = entry.get("id")
        if job_id is None or str(job_id).strip() == "":
            return None
        title = (entry.get("jobOpeningName") or "").strip()
        if not title:
            return None
        loc = entry.get("location") or {}
        location = ", ".join(
            p.strip() for p in (loc.get("city") or "", loc.get("state") or "") if p.strip()
        )
        location = location or None
        remote = bool(entry.get("isRemote"))
        if location is None and remote:
            location = "Remote"
        return NormalizedJob(
            external_job_id=str(job_id),
            title=title,
            location=location,
            url=f"{base}/careers/{job_id}",
            description="",
            raw_payload=entry,
            posted_at=None,
            countries=[],
            is_remote=remote,
        )
