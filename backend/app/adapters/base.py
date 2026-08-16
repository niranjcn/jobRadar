from abc import ABC, abstractmethod

from app.models import NormalizedJob


class JobSourceAdapter(ABC):
    ats_type: str = ""

    @abstractmethod
    async def fetch_jobs(self, board_identifier: str) -> list[NormalizedJob]:
        raise NotImplementedError

    async def fetch_job_detail(self, board_identifier: str, external_job_id: str) -> dict | None:
        return None

    def extract_description(self, detail: dict) -> str:
        return detail.get("content") or detail.get("description") or ""
