"""Insert the HPE Workday source.

HPE's careers site (careers.hpe.com) is a Phenom front-end, but the actual job
data lives on Workday (hpe.wd5.myworkdayjobs.com/Jobsathpe). The existing
Workday adapter fetches all ~1057 jobs from that board, so HPE is added as a
workday source with the Workday board URL as board_identifier.

Upsert on company_name (matches the POST /api/sources behavior).
"""

from app.config import load_settings
from app.db import get_supabase

SOURCES = [
    ("HPE", "workday", "https://hpe.wd5.myworkdayjobs.com/Jobsathpe"),
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
