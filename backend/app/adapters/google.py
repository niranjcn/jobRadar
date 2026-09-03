"""Google careers adapter (SSR embedded JSON parsing).

Google does not expose a public jobs API (the legacy /api/v3/search endpoint
returns 404). The careers site server-renders search results at:

    https://www.google.com/about/careers/applications/jobs/results?q=...&page=N

Each page embeds the job list in a script tag:

    AF_initDataCallback({key: 'ds:1', hash: '...', data: [[[job...], null, total, per_page]]});

`data[0]` is the job list (None when a filter matches nothing), `data[2]` the
total count and `data[3]` the page size (20). Pagination is via `page`.

Each job is a fixed-position array:
    [0]  id
    [1]  title
    [2]  signin/apply URL (contains a jobId token, not a stable link)
    [3]  [null, description HTML]
    [4]  [null, qualifications HTML]
    [7]  company name
    [9]  locations: [display, [aliases], city, zip, region, country_code][]
    [12] [posted_epoch_seconds, ...]
    [19] [null, minimum qualifications HTML]

The canonical job URL is {results_root}/{id}. The board_identifier is the
search query term; an empty string fetches all jobs.
"""

import json
import re
from datetime import UTC, datetime

from app.adapters.base import JobSourceAdapter
from app.adapters.http import RetryingClient
from app.models import NormalizedJob

RESULTS_URL = "https://www.google.com/about/careers/applications/jobs/results"
PAGE_SIZE = 20
MAX_PAGES = 100


class GoogleAdapter(JobSourceAdapter):
    ats_type = "google"

    async def fetch_jobs(self, board_identifier: str, client=None) -> list[NormalizedJob]:
        jobs: list[NormalizedJob] = []
        async with RetryingClient(timeout=30.0) as client:
            page = 1
            while page <= MAX_PAGES:
                params = {"page": page}
                if board_identifier:
                    params["q"] = board_identifier
                response = await client.get(RESULTS_URL, params=params)
                response.raise_for_status()
                data = _extract_ds1_data(response.text)
                if data is None:
                    break
                entries = data[0] or []
                jobs.extend(self._normalize(entry) for entry in entries)
                total = int(data[2] or 0)
                returned = int(data[3] or 0)
                if not entries or len(entries) < returned or (total and page * PAGE_SIZE >= total):
                    break
                page += 1
        return jobs

    @staticmethod
    def _normalize(job: list) -> NormalizedJob:
        job_id = str(job[0] or "").strip()
        title = str(job[1] or "").strip()
        description = _description(job)
        locations = _locations(job)
        countries = [code for _, code in locations if code]
        location = _display(job)
        return NormalizedJob(
            external_job_id=job_id,
            title=title,
            location=location,
            url=f"{RESULTS_URL}/{job_id}" if job_id else None,
            raw_payload=_to_payload(job),
            description=description,
            posted_at=_parse_posted(job),
            countries=countries,
            is_remote=any(
                word in (location or "").lower() for word in ("remote", "virtual", "anywhere")
            ),
        )


def _extract_ds1_data(text: str) -> list | None:
    match = re.search(r"AF_initDataCallback\(\{key: 'ds:1'", text)
    if not match:
        return None
    start = text.find("data:", match.start())
    if start == -1:
        return None
    start += len("data:")
    end = _matching_bracket(text, start, "[", "]")
    if end is None:
        return None
    try:
        return json.loads(text[start:end])
    except ValueError:
        return None


def _matching_bracket(s: str, start: int, open_ch: str, close_ch: str) -> int | None:
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(s)):
        ch = s[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        elif ch == '"':
            in_str = True
        elif ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                return i + 1
    return None


def _description(job: list) -> str:
    parts = []
    for idx in (3, 4, 19):
        block = job[idx] if idx < len(job) else None
        value = block[1] if isinstance(block, list) and len(block) > 1 else None
        if value and str(value).strip():
            parts.append(str(value))
    return "\n\n".join(parts)


def _locations(job: list) -> list[tuple[str, str]]:
    raw = job[9] if len(job) > 9 else None
    if not isinstance(raw, list):
        return []
    result: list[tuple[str, str]] = []
    for entry in raw:
        if not isinstance(entry, list) or not entry:
            continue
        display = str(entry[0] or "").strip()
        code = str(entry[5] or "").strip() if len(entry) > 5 else ""
        if display:
            result.append((display, code.upper() or None))
    return result


def _display(job: list) -> str | None:
    seen: list[str] = []
    for display, _ in _locations(job):
        if display and display not in seen:
            seen.append(display)
    return ", ".join(seen) if seen else None


def _parse_posted(job: list) -> str | None:
    raw = job[12] if len(job) > 12 else None
    if not isinstance(raw, list) or not raw:
        return None
    ts = raw[0]
    if isinstance(ts, (int, float)):
        return datetime.fromtimestamp(ts, tz=UTC).isoformat()
    return None


def _to_payload(job: list) -> dict:
    keys = [
        "id",
        "title",
        "apply_url",
        "description",
        "qualifications",
        "company_path",
        None,
        "company",
        "locale",
        "locations",
        "summary",
        "category_ids",
        "posted",
        "created",
        "expires",
        "apply_targets",
        None,
        None,
        "notifications",
        "min_qualifications",
        "type",
    ]
    payload: dict = {}
    for idx, key in enumerate(keys):
        if key and idx < len(job):
            payload[key] = job[idx]
    return payload
