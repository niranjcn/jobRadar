"""Shared structured message builders for Telegram + email notifications.

Both channels render the same company-grouped structure:

    🚨 10 jobs found

    Adobe — 3 new roles
    Google — 2 new roles

    Software Engineer

    🏢 Adobe

    📍 Bengaluru, India

    Apply

    https://careers.adobe.com/

Jobs are grouped by company so each company's new roles appear together.
"""

from html import escape
from typing import Any


def group_by_company(jobs: list[dict[str, Any]]) -> list[tuple[str, list[dict[str, Any]]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for job in jobs:
        company = job.get("company") or "Unknown"
        grouped.setdefault(company, []).append(job)
    return list(grouped.items())


def _job_lines(job: dict[str, Any], company: str) -> list[str]:
    lines = [job.get("title") or "", "", f"\U0001f3e2 {company}"]
    if job.get("location"):
        lines += ["", f"\U0001f4cd {job['location']}"]
    url = job.get("url")
    lines += ["", "Apply"]
    if url:
        lines += ["", url]
    return lines


def build_text_summary(new_jobs: int, new_matches: int) -> str:
    """Single-line run summary used as the header for Telegram/email.

    Emitted even when nothing was found, so the user gets a status update
    after every poll run.
    """
    return (
        f"\U0001f4e2 New job(s) found: {new_jobs} \u2014 New matching job(s) found: {new_matches}"
    )


def build_text(jobs: list[dict[str, Any]]) -> str:
    """Full plain-text message (header + company summary + per-job blocks)."""
    if not jobs:
        return ""
    groups = group_by_company(jobs)
    lines = [f"\U0001f4e2 {len(jobs)} jobs found", ""]
    for company, group in groups:
        lines.append(f"{company} — {len(group)} new role(s)")
    for company, group in groups:
        for job in group:
            lines.append("")
            lines.extend(_job_lines(job, company))
    return "\n".join(lines).rstrip()


def build_text_sections(jobs: list[dict[str, Any]]) -> list[str]:
    """Split the message into independent sections for chunking.

    Each section is either the header, a company summary line, or a single job
    block. Chunking between sections never splits a job block mid-way.
    """
    if not jobs:
        return []
    groups = group_by_company(jobs)
    sections = [f"\U0001f4e2 {len(jobs)} jobs found"]
    for company, group in groups:
        sections.append(f"{company} — {len(group)} new role(s)")
    for company, group in groups:
        for job in group:
            sections.append("\n".join(_job_lines(job, company)))
    return sections


def build_html(
    jobs: list[dict[str, Any]],
    *,
    new_jobs: int | None = None,
    new_matches: int | None = None,
    unsubscribe_url: str | None = None,
    postal_address: str | None = None,
) -> str:
    """HTML rendering of the same structure for email.

    When ``new_jobs`` is provided the header becomes a run summary line
    ("New job(s) found: X — New matching job(s) found: Y") which is emitted
    even when no jobs matched, so the recipient always gets a status update
    after a poll. Individual matched jobs still render in the grouped
    structure below it.

    CAN-SPAM: every marketing email must carry a working unsubscribe link
    and the sender's physical postal address. Pass ``unsubscribe_url`` (the
    preferences/manage page) and ``postal_address``; both render in a footer
    on every send. Placeholders render visibly so a missing configuration
    is obvious instead of silently non-compliant.
    """
    groups = group_by_company(jobs)

    if new_jobs is not None:
        matches = len(jobs) if new_matches is None else new_matches
        parts = [
            (
                f"<h2>\U0001f4e2 New job(s) found: {new_jobs} \u2014 "
                f"New matching job(s) found: {matches}</h2>"
            )
        ]
    else:
        if not jobs:
            return ""
        parts = [f"<h2>\U0001f4e2 {len(jobs)} jobs found</h2>"]

    if groups:
        summary = "<br>".join(
            f"<strong>{escape(company)}</strong> — {len(group)} new role(s)"
            for company, group in groups
        )
        parts.append(f"<p>{summary}</p>")
        for company, group in groups:
            for job in group:
                title = escape(job.get("title") or "")
                location = escape(job.get("location") or "")
                url = job.get("url")
                parts.append(f"<h3>{title}</h3>")
                meta = f"\U0001f3e2 {escape(company)}"
                if location:
                    meta += f"<br>\U0001f4cd {location}"
                parts.append(f"<p>{meta}</p>")
                if url:
                    parts.append(f'<p><a href="{escape(url)}">Apply</a></p>')
    footer_lines = []
    if unsubscribe_url:
        footer_lines.append(
            f"You received this because job alerts are enabled. "
            f'<a href="{escape(unsubscribe_url)}">Unsubscribe or manage email alerts</a>.'
        )
    else:
        footer_lines.append(
            "You received this because job alerts are enabled. "
            "Manage email alerts in JobQuest preferences. [UNSUBSCRIBE_URL]"
        )
    footer_lines.append(escape(postal_address) if postal_address else "[POSTAL_ADDRESS]")
    parts.append('<hr><p style="font-size:12px;color:#666">' + "<br>".join(footer_lines) + "</p>")
    return "<html><body>" + "\n".join(parts) + "</body></html>"
