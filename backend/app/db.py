import uuid
from typing import Any

import psycopg_pool
from supabase import Client, create_client

from app.config import Settings

_pool: psycopg_pool.ConnectionPool | None = None
_apool: psycopg_pool.AsyncConnectionPool | None = None
_apool_loop: Any = None


def json_safe(row: dict[str, Any]) -> dict[str, Any]:
    """Convert DB-native types that don't survive JSON encoding (uuid.UUID)
    into strings. Pooled-SQL rows feed both SQL re-params (accept either) and
    Supabase REST payloads (require JSON-safe values)."""
    out = {}
    for key, value in row.items():
        if isinstance(value, uuid.UUID):
            value = str(value)
        out[key] = value
    return out


def get_pool(settings: Settings) -> psycopg_pool.ConnectionPool:
    global _pool
    if _pool is None:
        _pool = psycopg_pool.ConnectionPool(
            settings.database_url,
            min_size=1,
            max_size=20,
            open=False,
        )
        _pool.open(wait=True, timeout=30)
    return _pool


def get_supabase(settings: Settings) -> Client:
    # Local PostgREST (docker `postgrest` service) serves at http://postgrest:3000/
    # while supabase-py expects /rest/v1 – patch the client to use the root when
    # SUPABASE_URL points at our local postgrest / proxy.
    if "postgrest" in settings.supabase_url or "supabase-proxy" in settings.supabase_url:
        client = create_client(settings.supabase_url, settings.supabase_key)
        base = settings.supabase_url.rstrip("/")
        # supabase-py builds rest_url as supabase_url + "/rest/v1" – override to base
        client.rest_url = base  # type: ignore[attr-defined]
        try:
            from postgrest import SyncClient

            client._postgrest = SyncClient(  # type: ignore[attr-defined]
                base_url=base,
                headers=client.options.headers,  # type: ignore[attr-defined]
                timeout=client.options.postgrest_client_timeout,  # type: ignore[attr-defined]
            )
        except Exception:
            pass
        return client
    return create_client(settings.supabase_url, settings.supabase_key)


def query(settings: Settings, sql: str, params: tuple = ()) -> list[dict[str, Any]]:
    """Run a SQL query against Postgres and return rows as dicts.
    Statements without a result set (insert/update/delete) return []."""
    with get_pool(settings).connection(timeout=20) as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        if cur.description is None:
            conn.commit()
            return []
        columns = [col.name for col in cur.description]
        return [json_safe(dict(zip(columns, row))) for row in cur.fetchall()]


async def open_async_pool(settings: Settings) -> None:
    """Open the shared async connection pool (Tier 3 / Step C).

    The pool is bound to the running event loop, and each pipeline run executes
    on a fresh loop (`run_pipeline_in_thread`), so the pool is keyed off the
    loop: a stale pool from a previous (now closed) loop is discarded and
    reopened. API route handlers are sync (FastAPI threadpool) and keep using
    `query()`.
    """
    import asyncio

    global _apool, _apool_loop
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if _apool is not None and _apool_loop is loop:
        return
    await close_async_pool()
    pool = psycopg_pool.AsyncConnectionPool(
        settings.database_url,
        min_size=1,
        max_size=20,
        open=False,
    )
    await pool.open(wait=True, timeout=30)
    _apool = pool
    _apool_loop = loop


async def close_async_pool() -> None:
    """Close the shared async pool; safe to call when already closed."""
    global _apool, _apool_loop
    if _apool is not None:
        try:
            await _apool.close()
        except Exception:
            pass
        _apool = None
        _apool_loop = None


async def query_async(settings: Settings, sql: str, params: tuple = ()) -> list[dict[str, Any]]:
    """Async mirror of `query()` for event-loop hot paths (poller lookups).

    Uses the shared pool when open; otherwise falls back to a short-lived pool
    so ad-hoc async callers (single-source runs, scripts, tests) work without
    lifecycle management.
    """
    if _apool is not None:
        return await _run_async(_apool, sql, params)
    async with psycopg_pool.AsyncConnectionPool(
        settings.database_url, min_size=1, max_size=2
    ) as tmp:
        return await _run_async(tmp, sql, params)


async def _run_async(pool, sql: str, params: tuple) -> list[dict[str, Any]]:
    async with pool.connection(timeout=20) as conn, conn.cursor() as cur:
        await cur.execute(sql, params)
        if cur.description is None:
            await conn.commit()
            return []
        columns = [col.name for col in cur.description]
        return [json_safe(dict(zip(columns, row))) for row in await cur.fetchall()]
