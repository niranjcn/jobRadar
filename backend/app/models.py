from dataclasses import dataclass
import re
from typing import Any


def strip_html(text: str | None) -> str:
    """Turn scraped HTML into a single-line plain-text string.

    Descriptions are the largest remaining column; stripping tags cuts storage
    significantly and avoids rendering untrusted scraped HTML in the UI.
    """
    if not text:
        return ""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text)).strip()


@dataclass
class NormalizedJob:
    external_job_id: str
    title: str
    location: str | None
    url: str | None
    raw_payload: dict[str, Any]
    description: str = ""
    posted_at: str | None = None
    countries: list[str] | None = None
    is_remote: bool = False

    def to_row(self, source_id: str) -> dict[str, Any]:
        # raw_payload is intentionally not persisted: it is the largest column
        # and duplicates the fields below (title/location/description/url).
        return {
            "source_id": source_id,
            "external_job_id": self.external_job_id,
            "title": self.title,
            "location": self.location,
            "url": self.url,
            "description": strip_html(self.description),
            "countries": self.countries or [],
            "is_remote": self.is_remote,
        }
