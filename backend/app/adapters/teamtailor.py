"""Teamtailor adapter (public RSS feed, single request).

Board_identifier is the portal subdomain (e.g. ``adform``).
Fetches ``https://{subdomain}.teamtailor.com/jobs.rss`` whose items carry
``title`` / ``link`` (``{id}-{slug}``) / ``pubDate`` / ``guid`` (stable UUID) /
``remoteStatus`` plus ``tt:location`` (city/country) and ``tt:department``.
"""

import re
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

from app.adapters.base import JobSourceAdapter
from app.adapters.http import RetryingClient
from app.models import NormalizedJob

_TT_NS = "{https://teamtailor.com/locations}"


def _text(parent, tag: str) -> str:
    el = parent.find(tag)
    return (el.text or "").strip() if el is not None and el.text else ""


class TeamtailorAdapter(JobSourceAdapter):
    ats_type = "teamtailor"

    async def fetch_jobs(self, board_identifier: str, client=None) -> list[NormalizedJob]:
        token = (board_identifier or "").strip().rstrip("/")
        if "://" in token:
            base = token.rstrip("/")
        else:
            base = f"https://{token}.teamtailor.com"
        url = f"{base}/jobs.rss"
        if client is not None:
            response = await client.get(url)
            response.raise_for_status()
            text = response.text
        else:
            async with RetryingClient(timeout=30.0) as _client:
                response = await _client.get(url)
                response.raise_for_status()
                text = response.text
        return self._parse_feed(text)

    @staticmethod
    def _parse_feed(text: str) -> list[NormalizedJob]:
        try:
            channel = ET.fromstring(text).find("channel")
        except ET.ParseError:
            return []
        if channel is None:
            return []
        jobs: list[NormalizedJob] = []
        for item in channel.findall("item"):
            job = TeamtailorAdapter._normalize(item)
            if job is not None:
                jobs.append(job)
        return jobs

    @staticmethod
    def _normalize(item) -> NormalizedJob | None:
        guid = _text(item, "guid")
        title = _text(item, "title")
        if not guid or not title:
            return None
        link = _text(item, "link") or None
        posted_at = None
        raw_date = _text(item, "pubDate")
        if raw_date:
            try:
                posted_at = parsedate_to_datetime(raw_date).isoformat()
            except (TypeError, ValueError):
                posted_at = None
        locs = []
        for loc in item.findall(f"{_TT_NS}locations/{_TT_NS}location"):
            city = ""
            country = ""
            for child in loc:
                tag = re.sub(r"^\{.*\}", "", child.tag)
                if tag == "city":
                    city = (child.text or "").strip()
                elif tag == "country":
                    country = (child.text or "").strip()
            label = ", ".join(p for p in (city, country) if p)
            if label:
                locs.append(label)
        location = "; ".join(locs) or None
        remote = _text(item, "remoteStatus").lower() == "remote"
        if location is None and remote:
            location = "Remote"
        return NormalizedJob(
            external_job_id=guid,
            title=title,
            location=location,
            url=link,
            description="",
            raw_payload={},
            posted_at=posted_at,
            countries=[],
            is_remote=remote,
        )
