import time
from pathlib import Path

import psycopg

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"


def run_migrations(database_url: str) -> None:
    applied_any = False
    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "create table if not exists schema_migrations "
                "(version text primary key, applied_at timestamptz not null default now())"
            )
        with conn.cursor() as cur:
            cur.execute("select version from schema_migrations")
            applied = {row[0] for row in cur.fetchall()}
        for sql_file in sorted(MIGRATIONS_DIR.glob("*.sql")):
            if sql_file.name in applied:
                continue
            applied_any = True
            with conn.cursor() as cur:
                cur.execute(sql_file.read_text(encoding="utf-8"))
                cur.execute("insert into schema_migrations (version) values (%s)", (sql_file.name,))
        with conn.cursor() as cur:
            cur.execute("notify pgrst, 'reload schema'")
        conn.commit()
    if applied_any:
        time.sleep(1.5)
