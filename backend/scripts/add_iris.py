"""Insert Iris Software (J2W custom) source. Run from backend/ with PYTHONPATH set."""

from app.config import load_settings
from app.db import get_supabase

COMPANY = "Iris Software"
ATS_TYPE = "custom"
BOARD = "https://careers.irissoftware.com"

settings = load_settings()
supabase = get_supabase(settings)
response = (
    supabase.table("sources")
    .upsert(
        [
            {
                "company_name": COMPANY,
                "ats_type": ATS_TYPE,
                "board_identifier": BOARD,
                "active": True,
            }
        ],
        on_conflict="company_name",
    )
    .execute()
)
row = response.data[0]
print(f"Iris Software source id: {row['id']}")
