from typing import Any

import psycopg_pool
from supabase import Client, create_client

from app.config import Settings

_pool: psycopg_pool.ConnectionPool | None = None


def get_pool(settings: Settings) -> psycopg_pool.ConnectionPool:
    global _pool
    if _pool is None:
        _pool = psycopg_pool.ConnectionPool(
            settings.database_url,
            min_size=1,
            max_size=10,
            open=False,
        )
        _pool.open(wait=True, timeout=30)
    return _pool


def get_supabase(settings: Settings) -> Client:
    return create_client(settings.supabase_url, settings.supabase_key)


def query(settings: Settings, sql: str, params: tuple = ()) -> list[dict[str, Any]]:
    """Run a read-only SQL query against Postgres and return rows as dicts."""
    with get_pool(settings).connection(timeout=20) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            columns = [col.name for col in cur.description] if cur.description else []
            return [dict(zip(columns, row)) for row in cur.fetchall()]
