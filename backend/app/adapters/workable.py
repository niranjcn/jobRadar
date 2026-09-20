"""Workable ATS adapter.

Board_identifier is the account subdomain (e.g. ``accellor``).
Uses the public read-only accounts endpoint (no auth):
  GET https://www.workable.com/api/accounts/{subdomain}
which returns the full public job list in a single response.
"""

from app.adapters.base import JobSourceAdapter
from app.adapters.http import RetryingClient
from app.models import NormalizedJob

PUBLIC_API_BASE = "https://www.workable.com/api/accounts"


class WorkableAdapter(JobSourceAdapter):
    ats_type = "workable"

    async def fetch_jobs(self, board_identifier: str, client=None) -> list[NormalizedJob]:
        url = f"{PUBLIC_API_BASE}/{board_identifier}"
        if client is not None:
            payload = await self._fetch_payload(client, url)
        else:
            async with RetryingClient(timeout=30.0) as _client:
                payload = await self._fetch_payload(_client, url)
        jobs: list[NormalizedJob] = []
        for job in payload.get("jobs", []) or []:
            jobs.extend(self._normalize(job))
        return jobs

    @staticmethod
    async def _fetch_payload(client, url: str) -> dict:
        """GET with manual redirect follow: many boards 302 to the widget API
        (apply.workable.com/api/v1/widget/accounts/...) which returns the
        identical shape. httpx does not follow redirects by default."""
        response = await client.get(url)
        hops = 0
        while response.is_redirect and hops < 3:
            location = response.headers.get("location")
            if not location:
                break
            response = await client.get(location)
            hops += 1
        response.raise_for_status()
        return response.json()

    @staticmethod
    def _normalize(job: dict) -> list[NormalizedJob]:
        """One row per location entry: the API repeats a shortcode per location."""
        shortcode = (job.get("shortcode") or "").strip()
        if not shortcode:
            return []
        title = (job.get("title") or "").strip()
        url = job.get("url") or f"https://apply.workable.com/j/{shortcode}"
        posted_at = job.get("published_on") or job.get("created_at")
        remote = bool(job.get("telecommuting"))
        entries = job.get("locations") or [{}]
        out: list[NormalizedJob] = []
        for loc in entries:
            cc = ((loc.get("countryCode") or "").strip() or "").upper()
            city = (loc.get("city") or "").strip()
            region = (loc.get("region") or "").strip()
            country = (loc.get("country") or "").strip()
            location = ", ".join(p for p in (city, region, country) if p) or None
            if location is None and remote:
                location = "Remote"
            ext = shortcode if not (cc or city) else f"{shortcode}:{cc}:{city}"
            out.append(
                NormalizedJob(
                    external_job_id=ext,
                    title=title,
                    location=location,
                    url=url,
                    description="",
                    raw_payload=job,
                    posted_at=posted_at,
                    countries=[cc] if cc else [],
                    is_remote=remote,
                )
            )
        return out
