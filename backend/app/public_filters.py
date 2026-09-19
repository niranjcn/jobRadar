"""Keyword filters for the public jobs API (landing page).

Our pipeline stores no salary / experience / employment-type columns, so
these filters match keyword groups against the combined
title + location + description text. Explicitly heuristic: unknown keys are
ignored and an empty selection means "no filter". Everything here is pure
(no DB) and covered by offline unit tests.
"""

TEXT_SQL = (
    "(coalesce(j.title, '') || ' ' || coalesce(j.location, '') "
    "|| ' ' || coalesce(j.description, ''))"
)


def escape_like(value: str) -> str:
    """Escape LIKE wildcards so user input matches literally."""
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def split_csv(raw: str | None) -> list[str]:
    """Split a comma-separated query param, dropping empties/duplicates."""
    if not raw:
        return []
    seen: list[str] = []
    for part in raw.split(","):
        value = part.strip()
        if value and value.lower() not in {s.lower() for s in seen}:
            seen.append(value)
    return seen


FILTER_KEYWORDS: dict[str, dict[str, list[str]]] = {
    "types": {
        "full-time": ["full time", "full-time", "fulltime", "fte"],
        "part-time": ["part time", "part-time"],
        "internship": ["intern", "internship"],
        "contract": ["contract", "contractor", "contractual"],
        "freelance": ["freelance", "freelancer"],
    },
    "exp": {
        "fresher": [
            "fresher",
            "fresher",
            "intern",
            "trainee",
            "entry level",
            "entry-level",
            "junior",
            "graduate",
            "new grad",
        ],
        "1-3": ["1-3", "1 – 3", "1–3", "0-2", "0 – 2", "0–2", "1+", "2+", "1-2"],
        "3-5": ["3-5", "3 – 5", "3–5", "2-5", "3+", "4+"],
        "5+": [
            "5+",
            "8+",
            "10+",
            "senior",
            "sr.",
            "lead",
            "principal",
            "staff",
            "architect",
            "manager",
            "director",
            "head of",
        ],
    },
    "cats": {
        "software": ["software", "backend", "frontend", "full stack", "sde", "developer", "mobile"],
        "data": ["data", "analyst", "analytics", "machine learning", "scientist", "tableau"],
        "design": ["design", "designer", "ui", "ux", "figma"],
        "devops": ["devops", "sre", "site reliability", "platform", "kubernetes", "cloud"],
        "product": ["product manager", "product owner", "program manager", "scrum"],
        "marketing": ["marketing", "seo", "content", "brand", "growth", "social media"],
        "sales": ["sales", "account executive", "business development"],
        "security": ["security", "cyber", "soc", "penetration", "infosec"],
        "qa": ["qa", "quality assurance", "tester", "testing"],
        "support": ["support", "customer success", "helpdesk"],
        "hr": ["hr", "human resources", "recruiter", "talent"],
        "finance": ["finance", "accounting", "accountant", "audit"],
    },
}

# LPA mentions like "12 LPA" or "12.5lpa" inside the posting text.
SALARY_PATTERN = "(?i)(\\d+(?:\\.\\d+)?)\\s*lpa"
SALARY_SQL = f"(substring({TEXT_SQL} from '{SALARY_PATTERN}')::numeric)"


def keyword_group_condition(group: str, selected: list[str]) -> tuple[str, list[str]]:
    """OR-condition for one keyword group. Unknown keys are ignored."""
    mapping = FILTER_KEYWORDS.get(group, {})
    keywords: list[str] = []
    for key in selected:
        keywords.extend(mapping.get(key.strip().lower(), []))
    unique = list(dict.fromkeys(keywords))
    if not unique:
        return "", []
    cond = " or ".join(f"{TEXT_SQL} ilike %s escape '\\'" for _ in unique)
    return f"({cond})", ["%" + escape_like(k) + "%" for k in unique]


def csv_ilike_condition(column_sql: str, values: list[str]) -> tuple[str, list[str]]:
    """OR-condition matching any of the values as a literal substring."""
    if not values:
        return "", []
    cond = " or ".join(f"{column_sql} ilike %s escape '\\'" for _ in values)
    return f"({cond})", ["%" + escape_like(v) + "%" for v in values]


def parse_lpa(raw: str | None) -> float | None:
    """Lenient LPA bound parser; invalid/non-positive input means no bound."""
    try:
        value = float(str(raw or "").strip())
    except (ValueError, TypeError):
        return None
    return value if value > 0 else None


def salary_condition(min_raw: str | None, max_raw: str | None) -> tuple[str, list[float]]:
    """Bounds over the first LPA mention in the posting text.

    Postings without a detectable LPA figure never match an active bound —
    salary coverage is limited until ingest extracts structured pay data.
    """
    conds: list[str] = []
    params: list[float] = []
    low = parse_lpa(min_raw)
    high = parse_lpa(max_raw)
    if low is not None:
        conds.append(f"{SALARY_SQL} >= %s")
        params.append(low)
    if high is not None:
        conds.append(f"{SALARY_SQL} <= %s")
        params.append(high)
    if not conds:
        return "", []
    return "(" + " and ".join(conds) + ")", params
