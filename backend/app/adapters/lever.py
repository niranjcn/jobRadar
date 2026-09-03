import asyncio
from datetime import UTC

import httpx

from app.adapters.base import JobSourceAdapter
from app.models import NormalizedJob

POSTINGS_API_BASE = "https://api.lever.co/v0/postings"
MAX_RETRIES = 4
RETRY_BACKOFF_SECONDS = 2.0


class LeverAdapter(JobSourceAdapter):
    ats_type = "lever"

    async def fetch_jobs(self, board_identifier: str, client=None) -> list[NormalizedJob]:
        url = f"{POSTINGS_API_BASE}/{board_identifier}?mode=json"
        last_error: Exception | None = None
        # Tier 2: reuse shared client if given (keeps connection alive); otherwise create one.
        _client = client
        _needs_close = False
        if _client is None:
            _client = httpx.AsyncClient(timeout=30.0)
            _needs_close = True
            await _client.__aenter__()
        try:
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    response = await _client.get(url)
                    if response.status_code == 200:
                        payload = response.json()
                        return [self._normalize(job) for job in payload]
                    if response.status_code not in (404, 429, 500, 502, 503):
                        response.raise_for_status()
                    last_error = httpx.HTTPStatusError(
                        f"lever returned {response.status_code}",
                        request=response.request,
                        response=response,
                    )
                except httpx.TransportError as exc:
                    last_error = exc
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(RETRY_BACKOFF_SECONDS * attempt)
            raise last_error or RuntimeError("lever fetch failed with no error")
        finally:
            if _needs_close:
                await _client.__aexit__(None, None, None)

    @staticmethod
    def _normalize(posting: dict) -> NormalizedJob:
        categories = posting.get("categories") or {}
        locations = categories.get("allLocations") or []
        location = next((loc for loc in locations if loc), None) or categories.get("location")
        created_ms = posting.get("createdAt")
        if created_ms:
            from datetime import datetime

            posted_at = datetime.fromtimestamp(created_ms / 1000, tz=UTC).isoformat()
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
