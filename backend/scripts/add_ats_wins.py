"""Insert standard-ATS sources discovered via board-slug probing. Run from backend/."""

from app.config import load_settings
from app.db import get_supabase

SOURCES = [
    {"company_name": "Perplexity AI", "ats_type": "ashby", "board_identifier": "perplexity"},
    {"company_name": "Cognition AI", "ats_type": "ashby", "board_identifier": "cognition"},
    {"company_name": "Redis", "ats_type": "ashby", "board_identifier": "redis"},
    {"company_name": "SpaceX", "ats_type": "greenhouse", "board_identifier": "spacex"},
]

settings = load_settings()
supabase = get_supabase(settings)
for s in SOURCES:
    response = (
        supabase.table("sources")
        .upsert(
            [
                {
                    "company_name": s["company_name"],
                    "ats_type": s["ats_type"],
                    "board_identifier": s["board_identifier"],
                    "active": True,
                }
            ],
            on_conflict="company_name",
        )
        .execute()
    )
    print(f"{s['company_name']} source id: {response.data[0]['id']}")