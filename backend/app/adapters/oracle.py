import json
import re
from urllib.parse import unquote_plus, urlparse

from app.adapters.base import JobSourceAdapter
from app.adapters.http import RetryingClient
from app.models import NormalizedJob

SEARCH_API_SUFFIX = "/rest/jobboard/searchjobs"
TZ_HEADERS = {"tz": "GMT+05:30", "tzname": "Asia/Kolkata"}
FUSION_SEARCH_PATH = "/hcmRestApi/CandidateExperience/recruitingCEJobSearch/list"
FUSION_ACTION = "ACE_JOBSEARCH_LIST"
FUSION_CONTENT_TYPE = "application/vnd.oracle.adf.action+json"
FUSION_FACETS = "LOCATION;WORKPLACE_TYPE;TITLES;WORKER_TYPE;BUSINESS_UNIT;JOB_FUNCTION"
FUSION_EXPAND = (
    "requisitionList.workLocation,requisitionList.otherWorkLocations,"
    "requisitionList.secondaryLocations,flexFieldsFacet.values,"
    "requisitionList.requisitionFlexFields"
)
FUSION_PAGE_SIZE = 100


def _strip_html(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text or "")).strip()


def _is_fusion(board_identifier: str) -> bool:
    """Oracle Fusion candidate-experience sites.

    Recognized by the standard /hcmUI/CandidateExperience/ path, by
    oraclecloud hosts, or by vanity career-site URLs that serve Fusion
    (e.g. https://careers.oracle.com/ or https://careers.americanexpress.com/en/sites/CX_1).
    """
    if "/hcmUI/CandidateExperience/" in board_identifier:
        return True
    if "/en/sites/" in board_identifier and "/careersection" not in board_identifier:
        return True
    host = urlparse(board_identifier).hostname or ""
    return "oraclecloud.com" in host or "oraclecloud.net" in host or host == "careers.oracle.com"


class OracleAdapter(JobSourceAdapter):
    """Oracle Recruiting Cloud adapter.

    Supports both legacy Taleo career sections (board_identifier must be the
    full careersection base URL, e.g. https://valero.taleo.net/careersection/2)
    and Oracle Fusion candidate-experience sites (board_identifier must be the
    full careers URL, e.g. https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1002).
    """

    ats_type = "oracle"

    def _base(self, board_identifier: str) -> str:
        return board_identifier.rstrip("/")

    def _host(self, board_identifier: str) -> str:
        return board_identifier.split("/careersection")[0].rstrip("/")

    @property
    def _rest_base(self) -> str:
        return "/careersection/rest/jobboard/searchjobs"

    async def fetch_jobs(self, board_identifier: str) -> list[NormalizedJob]:
        if _is_fusion(board_identifier):
            return await self._fetch_fusion_jobs(board_identifier)
        return await self._fetch_taleo_jobs(board_identifier)

    async def _fetch_fusion_jobs(self, board_identifier: str) -> list[NormalizedJob]:
        base = self._base(board_identifier)
        host, site_number = await self._fusion_endpoint(base)
        site_root = self._fusion_site_root(base)
        search_url = f"{host}{FUSION_SEARCH_PATH}"
        jobs: list[NormalizedJob] = []

        async with RetryingClient(timeout=30.0) as client:
            offset = 0
            while True:
                payload = {
                    "siteNumber": site_number,
                    "limit": FUSION_PAGE_SIZE,
                    "offset": offset,
                    "facets": FUSION_FACETS,
                    "input": "",
                    "expand": FUSION_EXPAND,
                    "sortBy": "POSTING_DATES_DESC",
                }
                response = await client.post(
                    search_url,
                    json=payload,
                    headers={
                        "Content-Type": FUSION_CONTENT_TYPE,
                        "Ora-Irc-Rest-Action": FUSION_ACTION,
                        **TZ_HEADERS,
                    },
                )
                if response.status_code != 200:
                    break
                data = response.json()
                item = (data.get("items") or [{}])[0]
                postings = item.get("requisitionList") or []
                jobs.extend(
                    self._normalize_fusion(site_root, site_number, p) for p in postings
                )
                total = item.get("totalJobsCount") or 0
                offset += len(postings)
                if offset >= total or not postings:
                    break
        return jobs

    @staticmethod
    def _fusion_site_root(base: str) -> str:
        """The public site URL prefix used for job links.

        Standard URLs point directly at the site
        (https://host/hcmUI/CandidateExperience/en/sites/CX_1002), so the root
        is that site URL. Vanity domains use either a path-based site that
        already contains /en/sites/ (https://careers.americanexpress.com/en/sites/CX_1)
        or a bare domain (https://careers.oracle.com/) where the site lives at
        /en/sites/jobsearch.
        """
        if "/hcmUI/CandidateExperience/" in base:
            return base.rstrip("/").removesuffix("/jobs")
        if "/en/sites/" in base:
            return base.rstrip("/").removesuffix("/jobs")
        return f"{base.rstrip('/')}/en/sites/jobsearch"

    @staticmethod
    async def _fusion_endpoint(base: str) -> tuple[str, str]:
        """Resolve the API host and site number for a Fusion careers URL.

        Standard URLs embed both (/hcmUI/CandidateExperience/en/sites/CX_1002).
        Vanity domains (e.g. https://careers.oracle.com/) redirect to Fusion, so
        the page is fetched and data-apibaseurl / data-sitenumber are read from
        the <base> tag.
        """
        parsed = urlparse(base)
        if "/hcmUI/CandidateExperience/" in base:
            site = OracleAdapter._fusion_site_number(base)
            return f"{parsed.scheme}://{parsed.hostname}", site
        async with RetryingClient(timeout=20.0, follow_redirects=True) as client:
            response = await client.get(base)
            response.raise_for_status()
            text = response.text
        api_base = re.search(r'data-apibaseurl="([^"]+)"', text)
        site_number = re.search(r'data-sitenumber="([^"]+)"', text)
        if not api_base or not site_number:
            raise RuntimeError(f"oracle fusion: could not resolve API base for {base}")
        return api_base.group(1).rstrip("/"), site_number.group(1)

    @staticmethod
    def _fusion_site_number(base: str) -> str:
        match = re.search(r"/sites/([^/]+)", base)
        if match:
            return match.group(1)
        raise RuntimeError(f"oracle fusion: could not find site number in {base}")

    @staticmethod
    def _normalize_fusion(site_root: str, site_number: str, posting: dict) -> NormalizedJob:
        requisition_id = posting.get("id") or posting.get("requisitionNumber") or ""
        title = posting.get("title") or ""
        location = posting.get("primaryLocation") or ""
        work_locations = posting.get("workLocation") or []
        if not location and work_locations:
            location = work_locations[0].get("townOrCity") or ""
        return NormalizedJob(
            external_job_id=str(requisition_id),
            title=title,
            location=location or None,
            url=f"{site_root}/job/{requisition_id}",
            description=posting.get("shortDescriptionStr") or "",
            posted_at=posting.get("postedDate") or None,
            raw_payload=posting,
        )

    async def _fetch_taleo_jobs(self, board_identifier: str) -> list[NormalizedJob]:
        base = self._base(board_identifier)
        jobs: list[NormalizedJob] = []
        async with RetryingClient(timeout=30.0) as client:
            page = await client.get(f"{base}/jobsearch.ftl", follow_redirects=True)
            page.raise_for_status()
            match = re.search(r"portalNo:\s*'(\d+)'", page.text)
            if not match:
                raise RuntimeError(f"oracle: could not find portalNo for {board_identifier}")
            portal = match.group(1)
            search_url = f"{self._host(board_identifier)}{self._rest_base}?portal={portal}"
            for page_no in range(1, 1_000_000):
                payload = {
                    "multilineEnabled": False,
                    "sortingSelection": {
                        "sortBySelectionParam": "1",
                        "ascendingSortingOrder": "false",
                    },
                    "fieldData": {
                        "fields": {"KEYWORD": "", "LOCATION": "", "CATEGORY": ""},
                        "valid": True,
                    },
                    "pageNo": page_no,
                }
                response = await client.post(
                    search_url,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "X-Requested-With": "XMLHttpRequest",
                        **TZ_HEADERS,
                    },
                )
                if response.status_code != 200:
                    break
                data = response.json()
                postings = data.get("requisitionList") or []
                jobs.extend(self._normalize_taleo(base, p) for p in postings)
                total = (data.get("pagingData") or {}).get("totalCount") or 0
                if len(jobs) >= total:
                    break
        return jobs

    @staticmethod
    def _normalize_taleo(base: str, posting: dict) -> NormalizedJob:
        columns = posting.get("column") or []
        title = columns[0] if len(columns) > 0 else ""
        location = ""
        if len(columns) > 1:
            try:
                locs = json.loads(columns[1])
                location = ", ".join(locs) if isinstance(locs, list) else str(locs)
            except (ValueError, TypeError):
                location = columns[1]
        contest_no = posting.get("contestNo") or posting.get("jobId") or ""
        return NormalizedJob(
            external_job_id=contest_no,
            title=title,
            location=location or None,
            url=f"{base}/jobdetail.ftl?job={contest_no}&lang=en",
            raw_payload=posting,
        )

    async def fetch_job_detail(self, board_identifier: str, external_job_id: str) -> dict | None:
        if _is_fusion(board_identifier):
            return await self._fetch_fusion_job_detail(board_identifier, external_job_id)
        return await self._fetch_taleo_job_detail(board_identifier, external_job_id)

    async def _fetch_fusion_job_detail(self, board_identifier: str, external_job_id: str) -> dict | None:
        base = self._base(board_identifier)
        url = f"{base}/job/{external_job_id}"
        async with RetryingClient(timeout=30.0) as client:
            response = await client.get(url, follow_redirects=True)
            if response.status_code != 200:
                return None
            html_text = response.text
        match = re.search(
            r'<meta name="description" content="([^"]*)"',
            html_text,
            re.IGNORECASE,
        )
        if match:
            return {"description": _strip_html(unquote_plus(match.group(1)))}
        return {"description": ""}

    async def _fetch_taleo_job_detail(self, board_identifier: str, external_job_id: str) -> dict | None:
        base = self._base(board_identifier)
        url = f"{base}/jobdetail.ftl?job={external_job_id}&lang=en"
        async with RetryingClient(timeout=30.0) as client:
            response = await client.get(url, follow_redirects=True)
            if response.status_code != 200:
                return None
            html_text = response.text
        marker = html_text.find("!*!")
        if marker < 0:
            return {"description": ""}
        start = html_text.rfind("<input", 0, marker)
        end = html_text.find(">", marker) + 1
        match = re.search(r'value="(.*?)"\s*/?>\s*$', html_text[start:end], re.S)
        if not match:
            return {"description": ""}
        raw = unquote_plus(match.group(1))
        parts = raw.split("!*!", 1)
        desc_raw = parts[1] if len(parts) > 1 else ""
        return {"description": _strip_html(unquote_plus(desc_raw))}

    def extract_description(self, detail: dict) -> str:
        return detail.get("description") or ""