from abc import ABC, abstractmethod

from app.models import NormalizedJob


class JobSourceAdapter(ABC):
    ats_type: str = ""

    @abstractmethod
    async def fetch_jobs(self, board_identifier: str, client=None) -> list[NormalizedJob]:
        """Fetch jobs for a board. If `client` (httpx.AsyncClient / RetryingClient) is given, reuse it
        to keep the TCP connection open across many boards in one poll (Tier 2)."""
        raise NotImplementedError

    async def fetch_job_detail(self, board_identifier: str, external_job_id: str) -> dict | None:
        return None

    def extract_description(self, detail: dict) -> str:
        return detail.get("content") or detail.get("description") or ""
