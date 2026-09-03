"""Adapter for We Work Remotely — RSS board for remote programming/design/etc.

Feeds: https://weworkremotely.com/categories/remote-programming-jobs.rss  (25 items)
        https://weworkremotely.com/remote-jobs.rss  (all categories, ~100+ items)
Board identifier is the category slug — "programming" (default, 25 jobs) or "all".

RSS items: title, link (job url), guid (stable id), pubDate, description (HTML),
           dc:creator (company). No structured location; treat as Remote.

We use xml.etree (std lib) to avoid extra deps; feed is small and stable.
"""

import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

from app.adapters.base import JobSourceAdapter
from app.adapters.http import RetryingClient
from app.models import NormalizedJob

FEED_BASE = "https://weworkremotely.com"
# Category feeds — only these are stable; "all" uses the aggregate feed.
FEED_MAP = {
    "all": f"{FEED_BASE}/remote-jobs.rss",
    "programming": f"{FEED_BASE}/categories/remote-programming-jobs.rss",
    "design": f"{FEED_BASE}/categories/remote-design-jobs.rss",
    "devops": f"{FEED_BASE}/categories/remote-devops-sysadmin-jobs.rss",
}


class WeworkremotelyAdapter(JobSourceAdapter):
    ats_type = "weworkremotely"

    async def fetch_jobs(self, board_identifier: str, client=None) -> list[NormalizedJob]:
        token = (board_identifier or "").strip().lower()
        # Default to programming — matches sources.json and keeps payload small (~166kB vs 847kB all).
        if token in ("weworkremotely", "programming", ""):
            token = "programming"
        url = FEED_MAP.get(token, FEED_MAP["programming"])

        if client is not None:
            response = await client.get(url)
            response.raise_for_status()
            xml_text = response.text
        else:
            async with RetryingClient(timeout=30.0) as _client:
                response = await _client.get(url)
                response.raise_for_status()
                xml_text = response.text

        return self._parse_rss(xml_text)

    @staticmethod
    def _parse_rss(xml_text: str) -> list[NormalizedJob]:
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError:
            return []

        # Handle default namespace-less RSS 2.0: channel -> item
        channel = root.find("channel")
        if channel is None:
            # Some feeds have root as channel directly
            channel = root
        items = channel.findall("item") if channel is not None else []

        jobs: list[NormalizedJob] = []
        for item in items:
            title_el = item.find("title")
            link_el = item.find("link")
            guid_el = item.find("guid")
            pub_el = item.find("pubDate")
            desc_el = item.find("description")

            title = (title_el.text or "").strip() if title_el is not None else ""
            link = (link_el.text or "").strip() if link_el is not None else ""
            guid = (guid_el.text or "").strip() if guid_el is not None else link

            # guid is like https://weworkremotely.com/remote-jobs/toptal-... — stable.
            # Use last path segment as external_job_id for deduplication stability.
            external_id = guid.rstrip("/").split("/")[-1] if guid else link
            # Normalize id: lowercase, truncate to 200 chars
            external_id = external_id.strip().lower()[:200] or link[:200]

            if not title or not external_id:
                continue

            # pubDate: "Wed, 12 Aug 2026 18:38:32 +0000" -> ISO
            posted_at = None
            if pub_el is not None and pub_el.text:
                try:
                    posted_at = parsedate_to_datetime(pub_el.text.strip()).isoformat()
                except Exception:
                    posted_at = None

            description = (desc_el.text or "") if desc_el is not None else ""
            # Title on WWR includes company prefix "Toptal: Python ..." — keep as-is;
            # matcher.py will still hit keywords; company extractor can split on ":" later.
            # Location: not in feed; treat as Remote so matcher remote logic applies.
            location = "Remote"

            jobs.append(
                NormalizedJob(
                    external_job_id=external_id,
                    title=title,
                    location=location,
                    url=link or None,
                    description=description,
                    raw_payload={
                        "title": title,
                        "link": link,
                        "guid": guid,
                        "pubDate": pub_el.text if pub_el is not None else None,
                    },
                    posted_at=posted_at,
                )
            )
        return jobs
