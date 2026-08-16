"""Insert SAP SuccessFactors batch sources (companies verified against SF).

Board identifiers verified live:
- Wipro:    https://careers.wipro.com                (Recruiting API v1)
- HCLTech:  https://careers.hcltech.com              (Recruiting API v1)
- SAP:      https://jobs.sap.com/search-jobs/Results?k=&l=&p=1        (j2w HTML)
- Capgemini: https://careers.capgemini.com/search-jobs/Results?k=&l=&p=1  (j2w HTML)

Lam Research (careers.lamresearch.com) is a JS-heavy SPA on SuccessFactors
with bot protection; not added yet — needs separate investigation.
Upsert on company_name (matches the POST /api/sources behavior).
"""

from app.config import load_settings
from app.db import get_supabase

SOURCES = [
    ("Wipro", "successfactors", "https://careers.wipro.com"),
    ("HCLTech", "successfactors", "https://careers.hcltech.com"),
    ("SAP", "successfactors", "https://jobs.sap.com/search-jobs/Results?k=&l=&p=1"),
    ("Capgemini", "successfactors", "https://careers.capgemini.com/search-jobs/Results?k=&l=&p=1"),
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
