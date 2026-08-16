"""Insert the OpenText (Phenom) and Siemens (Avature) sources.

Board identifiers:
- OpenText: careers root https://careers.opentext.com (Phenom SSR search-results)
- Siemens: https://jobs.siemens.com/en_US/externaljobs (Avature SearchJobs SSR)

Upsert on company_name (matches the POST /api/sources behavior).
"""

from app.config import load_settings
from app.db import get_supabase

SOURCES = [
    ("OpenText", "phenom", "https://careers.opentext.com"),
    ("Siemens", "avature", "https://jobs.siemens.com/en_US/externaljobs"),
]


def main() -> None:
    s = load_settings()
    supabase = get_supabase(s)
    for name, ats, board in SOURCES:
        response = (
            supabase.table("sources")
            .upsert(
                {
                    "company_name": name,
                    "ats_type": ats,
                    "board_identifier": board,
                    "active": True,
                },
                on_conflict="company_name",
            )
            .execute()
        )
        row = response.data[0]
        print(f"ok: {name} | {ats} | {row['id']} | active={row['active']}")


if __name__ == "__main__":
    main()
