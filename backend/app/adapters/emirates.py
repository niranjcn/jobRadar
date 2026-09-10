"""Emirates Group Careers adapter (public JSON API).

The Emirates Group runs its own careers site at
https://www.emiratesgroupcareers.com with a public JSON API used by the
/search-and-apply/ React frontend:

    GET {root}/api/v1/jobs-unique-props
        -> brands, jobcategories, locations (filter metadata)

    GET {root}/api/v1/jobs?title=&brand=&category=&location=&jobcategory=&showAll=false
        -> {"status": "success", "data": [ {...}, ... ]} (full listing, no pagination)

    GET {root}/api/v1/jobs/{reqid}
        -> {"status": "success", "data": {...}} (single job detail)

Each job carries a stable `reqid` (the Avature req id behind the scenes),
`title`, `brand` (Emirates, dnata, Emirates Engineering, ...), `category`
(the job family, e.g. "Information Technology"), `city`/`state`/`country` /
`location`, `postingdate` (epoch milliseconds), `jobdescription` (HTML) and
`redirectionurl` (the Avature apply link).

The public job page is {root}/search-and-apply/{reqid}.

The board_identifier is the site root, e.g.
https://www.emiratesgroupcareers.com
"""

import re
from datetime import UTC, datetime

from app.adapters.base import JobSourceAdapter
from app.adapters.http import RetryingClient
from app.models import NormalizedJob

JOBS_PATH = "/api/v1/jobs"
DEFAULT_ROOT = "https://www.emiratesgroupcareers.com"


def _root(board_identifier: str) -> str:
    root = (board_identifier or "").strip().rstrip("/")
    if not root:
        return DEFAULT_ROOT
    # Accept a full /api/... URL or a /search-and-apply/... URL as the board
    # identifier; trim back to the site root.
    for marker in ("/api/v1/jobs", "/search-and-apply"):
        if marker in root:
            root = root.split(marker, maxsplit=1)[0].rstrip("/")
    return root or DEFAULT_ROOT


class EmiratesAdapter(JobSourceAdapter):
    ats_type = "emirates"

    async def fetch_jobs(self, board_identifier: str, client=None) -> list[NormalizedJob]:
        root = _root(board_identifier)
        url = f"{root}{JOBS_PATH}"
        params = {
            "title": "",
            "brand": "",
            "category": "",
            "location": "",
            "jobcategory": "",
            "showAll": "false",
        }

        async def _fetch(client) -> list[dict]:
            response = await client.get(url, params=params)
            response.raise_for_status()
            payload = response.json()
            data = payload.get("data") if isinstance(payload, dict) else None
            return data if isinstance(data, list) else []

        if client is not None:
            entries = await _fetch(client)
        else:
            async with RetryingClient(timeout=30.0) as _client:
                entries = await _fetch(_client)
        jobs = [self._normalize(entry, root) for entry in entries]
        return [job for job in jobs if job.external_job_id]

    async def fetch_job_detail(self, board_identifier: str, external_job_id: str) -> dict | None:
        root = _root(board_identifier)
        url = f"{root}{JOBS_PATH}/{external_job_id}"
        try:
            async with RetryingClient(timeout=30.0) as client:
                response = await client.get(url)
                if response.status_code != 200:
                    return None
                payload = response.json()
        except Exception:
            return None
        data = payload.get("data") if isinstance(payload, dict) else None
        if not isinstance(data, dict):
            return None
        return {"content": data.get("jobdescription") or "", "raw": data}

    def extract_description(self, detail: dict) -> str:
        return detail.get("content") or ""

    @staticmethod
    def _normalize(job: dict, root: str) -> NormalizedJob:
        job_id = str(job.get("reqid") or job.get("reqno") or "").strip()
        title = str(job.get("title") or "").strip()
        location = _location(job)
        country = str(job.get("country") or "").strip()
        countries = [country] if country else []
        is_remote = bool(
            location and re.search(r"\b(virtual|remote|work from home)\b", location, re.IGNORECASE)
        )
        return NormalizedJob(
            external_job_id=job_id,
            title=title,
            location=location,
            url=f"{root}/search-and-apply/{job_id}" if root and job_id else None,
            raw_payload={
                "brand": job.get("brand"),
                "category": job.get("category"),
                "city": job.get("city"),
                "state": job.get("state"),
                "country": job.get("country"),
                "system": job.get("system"),
                "redirectionurl": job.get("redirectionurl"),
            },
            description=job.get("jobdescription") or "",
            posted_at=_parse_posted(job.get("postingdate")),
            countries=countries,
            is_remote=is_remote,
        )


def _location(job: dict) -> str | None:
    direct = str(job.get("location") or "").strip()
    if direct:
        return direct
    parts = [
        str(job.get("city") or "").strip(),
        str(job.get("state") or "").strip(),
        str(job.get("country") or "").strip(),
    ]
    # Avoid "Dubai, Dubai, United Arab Emirates" style duplication.
    seen: list[str] = []
    for part in parts:
        if part and part.lower() not in {s.lower() for s in seen}:
            seen.append(part)
    return ", ".join(seen) if seen else None


def _parse_posted(value) -> str | None:
    if value is None:
        return None
    try:
        millis = int(value)
    except (TypeError, ValueError):
        return None
    try:
        return datetime.fromtimestamp(millis / 1000, tz=UTC).date().isoformat()
    except (OverflowError, OSError, ValueError):
        return None
