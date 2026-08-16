"""Best-effort ATS detection for adding a new source from the UI.

Probes the public APIs of Greenhouse / Lever / Ashby with a candidate slug,
and pattern-matches Workday / Oracle URLs. Returns the first working match.
"""

import re
from urllib.parse import urlparse

import httpx

GREENHOUSE = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
LEVER = "https://api.lever.co/v0/postings/{slug}?mode=json"
ASHBY = "https://api.ashbyhq.com/posting-api/job-board/{slug}"
PROBE_TIMEOUT = 8.0


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def _detect_from_url(url: str) -> dict | None:
    host = urlparse(url).hostname or ""
    if "myworkdayjobs.com" in host:
        return {"ats_type": "workday", "board_identifier": url.rstrip("/")}
    if "taleo.net" in host or "/careersection" in url:
        return {"ats_type": "oracle", "board_identifier": url.rstrip("/")}
    if "oraclecloud.com" in host or "oraclecloud.net" in host or host == "careers.oracle.com":
        return {"ats_type": "oracle", "board_identifier": url.rstrip("/")}
    if ".icims.com" in host:
        return {"ats_type": "icims", "board_identifier": url.rstrip("/")}
    if "successfactors" in host or "/search-jobs" in url:
        return {"ats_type": "successfactors", "board_identifier": url.rstrip("/")}
    if "avature.net" in host or "/externaljobs" in url:
        return {"ats_type": "avature", "board_identifier": url.rstrip("/")}
    return None


async def _probe(client: httpx.AsyncClient, url: str) -> bool:
    try:
        response = await client.get(url)
        return response.status_code == 200
    except httpx.HTTPError:
        return False


async def detect_source(company_name: str, url: str = "") -> dict | None:
    """Return {ats_type, board_identifier} if a source can be identified."""
    if url:
        detected = _detect_from_url(url)
        if detected:
            return detected

    slug = slugify(company_name)
    if not slug:
        return None

    async with httpx.AsyncClient(timeout=PROBE_TIMEOUT) as client:
        if await _probe(client, GREENHOUSE.format(slug=slug)):
            return {"ats_type": "greenhouse", "board_identifier": slug}
        if await _probe(client, LEVER.format(slug=slug)):
            return {"ats_type": "lever", "board_identifier": slug}
        if await _probe(client, ASHBY.format(slug=slug)):
            return {"ats_type": "ashby", "board_identifier": slug}
    return None
