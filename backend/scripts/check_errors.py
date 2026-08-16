from app.config import load_settings
from app.db import query

s = load_settings()
rows = query(
    s,
    "select company_name, ats_type, last_error from sources where last_error is not null order by company_name",
)
for r in rows:
    print(f'{r["company_name"]} [{r["ats_type"]}]: {r["last_error"][:200]}')