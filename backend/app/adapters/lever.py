import asyncio

import httpx

from app.adapters.base import JobSourceAdapter
from app.models import NormalizedJob

POSTINGS_API_BASE = "https://api.lever.co/v0/postings"
MAX_RETRIES = 4
RETRY_BACKOFF_SECONDS = 2.0


class LeverAdapter(JobSourceAdapter):
    ats_type = "lever"

    async def fetch_jobs(self, board_identifier: str) -> list[NormalizedJob]:
        url = f"{POSTINGS_API_BASE}/{board_identifier}?mode=json"
        last_error: Exception | None = None
        async with httpx.AsyncClient(timeout=30.0) as client:
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    response = await client.get(url)
                    if response.status_code == 200:
                        payload = response.json()
                        return [self._normalize(job) for job in payload]
                    if response.status_code not in (404, 429, 500, 502, 503):
                        response.raise_for_status()
                    last_error = httpx.HTTPStatusError(
                        f"lever returned {response.status_code}", request=response.request, response=response
                    )
                except httpx.TransportError as exc:
                    last_error = exc
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(RETRY_BACKOFF_SECONDS * attempt)
        raise last_error or RuntimeError("lever fetch failed with no error")

    @staticmethod
    def _normalize(posting: dict) -> NormalizedJob:
        categories = posting.get("categories") or {}
        locations = categories.get("allLocations") or []
        location = next((loc for loc in locations if loc), None) or categories.get("location")
        created_ms = posting.get("createdAt")
        if created_ms:
            from datetime import datetime, timezone
            posted_at = datetime.fromtimestamp(created_ms / 1000, tz=timezone.utc).isoformat()
        else:
            posted_at = None
        return NormalizedJob(
            external_job_id=posting.get("id") or "",
            title=posting.get("text") or "",
            location=location,
            url=posting.get("hostedUrl") or posting.get("applyUrl"),
            description=posting.get("description") or "",
            raw_payload=posting,
            posted_at=posted_at,
        )