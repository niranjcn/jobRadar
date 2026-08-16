"""Insert iCIMS batch sources (companies verified against the iCIMS API).

Board identifiers verified live:
- AMD:    https://careers.amd.com          (Jibe JSON /api/jobs)
- Rivian: https://careers.rivian.com      (Jibe JSON /api/jobs)
- Arm:    https://careers.arm.com/search-jobs?k=&l=&p=1  (TalentBrew HTML)

Microsoft careers (jobs.careers.microsoft.com) is bot-protected and is not
added yet — it needs a separate investigation.
Upsert on company_name (matches the POST /api/sources behavior).
"""

from app.config import load_settings
from app.db import get_supabase

SOURCES = [
    ("AMD", "icims", "https://careers.amd.com"),
    ("Rivian", "icims", "https://careers.rivian.com"),
    ("Arm", "icims", "https://careers.arm.com/search-jobs?k=&l=&p=1"),
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