import os
import time
from collections.abc import Callable
from pathlib import Path

import psycopg

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"

# Postgres refuses connections while replaying WAL after an unclean shutdown
# (SQLSTATE 57P03 "the database system is not yet accepting connections").
# A busy local stack can spend minutes in recovery, so startup waits it out
# instead of crashing and leaving the reloader with no server child.
CONNECT_WAIT_SECONDS = 300.0
CONNECT_RETRY_INITIAL_DELAY = 1.0
CONNECT_RETRY_MAX_DELAY = 10.0


def connect_with_retry(
    database_url: str,
    wait_seconds: float | None = None,
    sleep: Callable[[float], None] = time.sleep,
) -> psycopg.Connection:
    """Connect to Postgres, retrying while it is still starting/recovering."""
    if wait_seconds is None:
        wait_seconds = float(os.environ.get("MIGRATION_CONNECT_WAIT_SECONDS", CONNECT_WAIT_SECONDS))
    deadline = time.monotonic() + wait_seconds
    delay = CONNECT_RETRY_INITIAL_DELAY
    while True:
        try:
            return psycopg.connect(database_url)
        except psycopg.OperationalError as exc:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise
            wait = min(delay, remaining)
            print(f"migrations: database not ready, retrying in {wait:.0f}s ({exc})")
            sleep(wait)
            delay = min(delay * 2, CONNECT_RETRY_MAX_DELAY)


def run_migrations(database_url: str) -> None:
    applied_any = False
    with connect_with_retry(database_url) as conn:
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
