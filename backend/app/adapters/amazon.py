"""Amazon jobs adapter (public JSON search endpoint).

Amazon exposes its global job board through a public JSON search endpoint:

    GET https://www.amazon.jobs/en/search.json
        ?base_query=&offset=0&result_limit=100&sort=recent

The response contains a `hits` total and a `jobs` array. Each job carries a
stable numeric `id_icims` (used in the apply URL path), `title`, location
strings, `job_path`, `posted_date`, `description` and qualification blocks.

The `normalized_country_code[]` param filters by ISO3 country (e.g. IND).
The board_identifier is that country code; an empty string fetches all
countries. Offset pagination walks until `hits` is reached or a page comes
back short.
"""

from datetime import UTC, datetime

from app.adapters.base import JobSourceAdapter
from app.adapters.http import RetryingClient
from app.models import NormalizedJob

SEARCH_URL = "https://www.amazon.jobs/en/search.json"
PAGE_SIZE = 100
MAX_OFFSET = 100_000


class AmazonAdapter(JobSourceAdapter):
    ats_type = "amazon"

    async def fetch_jobs(self, board_identifier: str) -> list[NormalizedJob]:
        jobs: list[NormalizedJob] = []
        async with RetryingClient(timeout=30.0) as client:
            offset = 0
            while offset <= MAX_OFFSET:
                params: dict[str, str | int] = {
                    "base_query": "",
                    "offset": offset,
                    "result_limit": PAGE_SIZE,
                    "sort": "recent",
                }
                if board_identifier:
                    params["normalized_country_code[]"] = board_identifier
                response = await client.get(SEARCH_URL, params=params)
                response.raise_for_status()
                payload = response.json()
                entries = payload.get("jobs") or []
                jobs.extend(self._normalize(entry) for entry in entries)
                total = int(payload.get("hits") or 0)
                offset += PAGE_SIZE
                if len(entries) < PAGE_SIZE or (total and offset >= total):
                    break
        return jobs

    @staticmethod
    def _normalize(job: dict) -> NormalizedJob:
        job_id = str(job.get("id_icims") or job.get("id") or "").strip()
        location = job.get("normalized_location") or job.get("location")
        raw_locations = []
        for raw in job.get("locations") or []:
            if isinstance(raw, str):
                try:
                    raw_locations.append(_parse_location_json(raw))
                except ValueError:
                    continue
            elif isinstance(raw, dict):
                raw_locations.append(raw)
        countries = _country_codes(raw_locations)
        is_remote = _is_remote(location, raw_locations)
        return NormalizedJob(
            external_job_id=job_id,
            title=job.get("title") or "",
            location=location,
            url=_job_url(job),
            raw_payload=job,
            description=_description(job),
            posted_at=_parse_posted(job.get("posted_date")),
            countries=countries,
            is_remote=is_remote,
        )


def _job_url(job: dict) -> str | None:
    path = job.get("job_path")
    if not path:
        return None
    return f"https://www.amazon.jobs{path}"


def _description(job: dict) -> str:
    parts = [
        job.get("description") or "",
        job.get("basic_qualifications") or "",
        job.get("preferred_qualifications") or "",
    ]
    return "\n\n".join(part.strip() for part in parts if part and part.strip())


def _parse_posted(value: str | None) -> str | None:
    if not value:
        return None
    try:
        parsed = datetime.strptime(value, "%B %d, %Y")
    except ValueError:
        return None
    return parsed.replace(tzinfo=UTC).isoformat()


def _parse_location_json(raw: str) -> dict:
    import json

    return json.loads(raw)


def _country_codes(raw_locations: list[dict]) -> list[str]:
    codes: list[str] = []
    for entry in raw_locations:
        code = entry.get("countryIso2a") or entry.get("normalizedCountryCode")
        if code and code not in codes:
            codes.append(code)
    return codes


def _is_remote(location: str | None, raw_locations: list[dict]) -> bool:
    if location and any(word in location.lower() for word in ("virtual", "remote")):
        return True
    return any((entry.get("type") or "").upper() == "VIRTUAL" for entry in raw_locations)
