import re
from urllib.parse import urlparse

from app.adapters.base import JobSourceAdapter
from app.adapters.http import RetryingClient
from app.models import NormalizedJob

PAGE_SIZE = 20


def _strip_html(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text or "")).strip()


class WorkdayAdapter(JobSourceAdapter):
    ats_type = "workday"

    def _parse_board(self, board_identifier: str) -> tuple[str, str, str]:
        parsed = urlparse(board_identifier)
        host = parsed.hostname or ""
        parts = host.split(".")
        tenant, shard = parts[0], parts[1]
        path_segments = [s for s in (parsed.path or "/").strip("/").split("/")]
        while path_segments and re.match(r"^[a-z]{2}(-[A-Z]{2})?$", path_segments[0]):
            path_segments.pop(0)
        site = path_segments[0] if path_segments else "External"
        return tenant, shard, site

    def _list_api(self, board_identifier: str) -> str:
        tenant, shard, site = self._parse_board(board_identifier)
        return f"https://{tenant}.{shard}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs"

    def _detail_api(self, board_identifier: str, external_path: str) -> str:
        tenant, shard, site = self._parse_board(board_identifier)
        return f"https://{tenant}.{shard}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/{external_path.lstrip('/')}"

    async def fetch_jobs(self, board_identifier: str) -> list[NormalizedJob]:
        url = self._list_api(board_identifier)
        jobs: list[NormalizedJob] = []
        first = True
        total = 0
        async with RetryingClient(timeout=30.0) as client:
            for offset in range(0, 1_000_000, PAGE_SIZE):
                response = await client.post(
                    url, json={"limit": PAGE_SIZE, "offset": offset, "searchText": ""}
                )
                if response.status_code == 400:
                    break
                response.raise_for_status()
                payload = response.json()
                if first:
                    total = payload.get("total") or 0
                    first = False
                postings = payload.get("jobPostings") or []
                if not postings:
                    break
                for p in postings:
                    if not p.get("externalPath"):
                        continue
                    jobs.append(self._normalize(board_identifier, p))
                if len(jobs) >= total:
                    break
        seen: set[str] = set()
        unique: list[NormalizedJob] = []
        for job in jobs:
            if job.external_job_id in seen:
                continue
            seen.add(job.external_job_id)
            unique.append(job)
        return unique

    @staticmethod
    def _normalize(board_identifier: str, posting: dict) -> NormalizedJob:
        external_path = posting.get("externalPath") or ""
        return NormalizedJob(
            external_job_id=external_path,
            title=posting.get("title") or "",
            location=posting.get("locationsText") or None,
            url=f"{board_identifier}{external_path}",
            raw_payload=posting,
        )

    async def fetch_job_detail(self, board_identifier: str, external_job_id: str) -> dict | None:
        url = self._detail_api(board_identifier, external_job_id)
        async with RetryingClient(timeout=30.0) as client:
            response = await client.get(url)
            if response.status_code != 200:
                return None
            payload = response.json()
        return payload.get("jobPostingInfo") or payload

    def extract_description(self, detail: dict) -> str:
        return _strip_html(detail.get("jobDescription") or "")