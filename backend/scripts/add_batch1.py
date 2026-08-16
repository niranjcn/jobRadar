"""Insert batch-1 sources (companies that reuse existing adapters).

Board identifiers below were verified live against each ATS's public API.
Upsert on company_name (matches the POST /api/sources behavior).
"""

from app.config import load_settings
from app.db import get_supabase

SOURCES = [
    # Greenhouse (boards-api verified)
    ("MongoDB", "greenhouse", "mongodb"),
    ("SpaceX", "greenhouse", "spacex"),
    ("Lucid Motors", "greenhouse", "lucidmotors"),
    ("TCS", "greenhouse", "tcs"),
    # Ashby (posting-api verified)
    ("Snowflake", "ashby", "snowflake"),
    ("Perplexity", "ashby", "perplexity"),
    ("Cognition", "ashby", "cognition"),
    ("Mistral AI", "ashby", "mistral.ai"),
    # Lever (api verified)
    ("Sophos", "lever", "sophos"),
    # Workday (cxs API verified)
    ("Red Hat", "workday", "https://redhat.wd5.myworkdayjobs.com/en-US/jobs"),
    ("Mastercard", "workday", "https://mastercard.wd1.myworkdayjobs.com/CorporateCareers"),
    ("Bank of America", "workday", "https://ghr.wd1.myworkdayjobs.com/en-US/lateral-us"),
    ("Palo Alto Networks", "workday", "https://paloaltonetworks.wd5.myworkdayjobs.com/en-US/panwexternalcareers"),
    # Oracle Fusion (vanity domain verified)
    ("American Express", "oracle", "https://careers.americanexpress.com/en/sites/CX_1"),
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