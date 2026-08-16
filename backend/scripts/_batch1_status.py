import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from app.config import load_settings
from app.db import query

s = load_settings()
batch1 = [
    "MongoDB", "SpaceX", "Lucid Motors", "TCS", "Snowflake", "Perplexity",
    "Cognition", "Mistral AI", "Sophos", "Red Hat", "Mastercard",
    "Bank of America", "Palo Alto Networks", "American Express",
]
rows = query(
    s,
    "select company_name, ats_type, board_identifier, active, last_checked_at, last_error "
    "from sources where company_name = any(%s) order by company_name",
    (batch1,),
)
for r in rows:
    checked = (r["last_checked_at"] or "").__str__()[:19]
    print(
        f"{r['company_name']:20s} {r['ats_type']:10s} active={r['active']} "
        f"checked={checked} err={(r['last_error'] or '')[:40]}"
    )