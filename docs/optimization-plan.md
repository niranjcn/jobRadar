# Backend Optimization Plan

> Status: Steps A & B implemented (see §5). File is a working plan, not tracked in git.

## 0. Current state (verified)

- **Unit tests:** 98/98 pass (`tests/test_unit.py`)
- **API tests:** 18/19 pass — the 1 failure is the known flaky live-Supabase timeout (`test_location_mapping_roundtrip`, passes in isolation)
- **Lint/format:** clean with pinned `ruff==0.16.3`
- **App import:** `from app.main import app` OK, 30 routes registered

The backend is functionally healthy. This plan targets **load/efficiency**, not correctness.

## 1. Bottleneck analysis (by order of impact)

### 1.1 Synchroneous Supabase REST inside async code (biggest issue)

`poller.py` / `matcher.py` / `notify.py` / `telegram/notifications.py` run **sync Supabase REST** calls
(`supabase.table(...).execute()`) inside `async def` functions. Under FastAPI's single event loop:

- A poll of N sources holds the loop for the **entire run** (each source = list + detail-enrich + upsert).
- The Telegram bot long-poll task shares the same loop → **bot replies stall during a poll**.
- API requests queue behind the poll.

Concretely: `poll_all_sources` → `poll_source` → `enrich_jobs` all do blocking I/O per job. With
`DETAIL_CONCURRENCY=15` those are concurrent, but each is still a blocking sync call, so they don't
block each other but **do block the loop** (they just serialize CPU/IO chunks).

**Fix:** run the heavy pipeline off the event loop.

- Wrap the whole `poll_all_sources` (and `recompute_matches`, `send_*_notifications`) body in
  `asyncio.to_thread(...)` / a `ThreadPoolExecutor`, OR
- Switch the pool-backed `query()` path (already psycopg + connection pool) to `async` via
  `psycopg_pool` async pool + `asyncpg`/psycopg async cursors, and use it for the hot loops.

Cheapest correct first step: **`asyncio.to_thread` around the pipeline** so the loop stays responsive
to the bot + API. Longer term: async psycopg.

### 1.2 `fetch_existing_job_ids` paginates 1000-row REST pages

`_fetch_external_job_ids` (`poller.py`) walks `range(0, 1_000_000, PAGE_SIZE)` over REST — a source
with 20k jobs = **20 sequential REST round-trips** per poll. This runs once per source per poll.

**Fix:** one pooled SQL query: `select external_job_id from jobs where source_id = %s` via `query()`
(already exists in `db.py`). Turns 20 REST calls into 1 DB round-trip.

### 1.3 Notification paths refetch + duplicate work

- `telegram/notifications.py` and `notify.py` each:
  - fetch candidate jobs (REST, batched)
  - fetch **all** `notifications_sent` job ids for dedup (`_fetch_sent_job_ids`) — this set grows
    forever; at 100k sent rows it's a large REST fetch **every poll run**.
  - fetch all `job_matches` for the user (REST, unbounded) even when the candidate set is tiny.
- Fixes:
  - Dedup in SQL: `select job_id from notifications_sent where user_id=%s and channel=%s and job_id = any(%s::uuid[])`.
  - Match-scope in SQL: only pull matches for candidate job ids, not the whole table.
  - Reuse one fetched "candidate jobs" list across telegram + email (currently fetched twice).

### 1.4 `query()` connection pool is sync psycopg

`get_pool` is `psycopg_pool.ConnectionPool(min_size=1, max_size=10)` — good for the read paths, but
it's synchronous inside the same blocking problem as 1.1. Read-only API queries are fast, but the
poller's detail-enrich writes (`update_job_detail` REST per job) are the true hotspot.

### 1.5 Description retention vs. re-fetch

`clear_descriptions` nulls descriptions after notify (good). But `match_all` runs **before** clear on
candidates only — fine. `recompute_matches` runs over all jobs in SQL (already DB-side). No change
needed here, just noting it's already efficient.

### 1.6 `load_settings()` called per request / per query helper

`load_dotenv()` + env parsing happens on every `load_settings()` — called in most route handlers and
by `query()` helpers indirectly. Minor, but a module-level cached settings object (invalidated on a
config touch) removes repeated env file I/O. Keep `load_settings()` but memoize.

## 2. Recommended plan (incremental, each step independently testable)

### Step A — Keep the event loop responsive (high impact, low risk)
- Wrap `poll_all_sources`, `recompute_matches`, `send_telegram_notifications`,
  `send_email_notifications` entry points in `asyncio.to_thread`.
- Add a test asserting a poll starts without blocking a concurrent bot command (unit-level: verify
  `to_thread` wiring with a fake pollable source).

### Step B — Collapse REST fan-out into pooled SQL (high impact, low risk)
- `_fetch_external_job_ids` → single `query()` select.
- `match_all` job lookup → one `query()` with `external_job_id = any(...)`.
- `notifications_sent` dedup + `job_matches` scope → parameterized `any(...)` selects.
- Keep `upsert`/`update` via REST (Supabase upsert semantics) or move to psycopg; decide per call.

### Step C — Async DB access (medium impact, higher risk)
- Add `psycopg_pool.AsyncConnectionPool` + async `query_async()`; use in poller/enrich/notify hot
  paths; keep sync `query()` for simple API reads initially.

### Step D — Caching (low impact, easy)
- Memoize `load_settings()` (invalidate when `.env`/env changes, or TTL).
- Cache `load_location_mapping` / preferences within a single poll run (pass through instead of
  re-reading per source — `poll_source` already receives settings; thread one `geo_settings` object).

### Step E — API/query tuning (low impact, easy)
- `/jobs` and `/matches/jobs` already use `query()`; add missing indexes if profiles show scans:
  - `jobs(source_id, external_job_id)` (already unique)
  - `job_matches(user_id, job_id)` (already unique)
  - `notifications_sent(job_id, channel)` (already unique via upsert key)
  - Consider `poll_runs(started_at desc)` and `sources(last_checked_at)`.
- Pagination is already bounded (`limit/offset`); no unbounded API scans found.

## 3. Out of scope for now

- Worker process / Celery / Redis (per AGENTS.md — no demonstrated need yet).
- Horizontal scaling / microservices / Kubernetes.
- LLM matching.
- Frontend load work.

## 4. Definition of done

Each step lands with:
- Tests (unit; fixture-based, no live network)
- ruff lint + format clean (pinned 0.16.3)
- Existing 98 unit + 18 API tests still green
- Observable: bot latency during a poll, and reduced REST call counts (logged)

## 5. Implementation log

### Step A — Event loop responsiveness (DONE)

Added `run_pipeline_in_thread(coro)` in `app/poller.py`: runs the blocking-heavy
pipeline coroutine inside `asyncio.to_thread(asyncio.run, ...)` so it executes in
a dedicated worker thread with its own event loop.

Applied at all four async entry points:
- `app/main.py::_run_safe` (scheduler)
- `app/api/routes.py::run_source`, `_run_poll_background`, `_run_unhealthy_background`

The Telegram bot long-poll and API handlers now stay responsive while a poll is
running (previously they were frozen for the whole poll).

### Step B — Collapse REST fan-out into pooled SQL (DONE)

- `fetch_existing_job_ids` in `app/poller.py` now runs one pooled SQL query
  (`select external_job_id from jobs where source_id = %s`) instead of walking
  1000-row REST pages (~20 round-trips per 20k-job source, once per source per
  poll).
- `notifications_sent` dedup + `job_matches` lookups in `app/notify.py` and
  `app/telegram/notifications.py` are now scoped to the candidate job ids
  (`in_("job_id", batch)`) instead of fetching every row ever recorded for the
  user/channel.
- Candidate jobs are fetched once per poll via `fetch_candidate_jobs` in
  `app/poller.py` and passed to both the Telegram and email senders (`jobs=`)
  instead of each path refetching the same candidates.

### Step C — Async DB access (PENDING)

Add `psycopg_pool.AsyncConnectionPool` + async `query_async()`; use in the hot
paths. Step A already removed the event-loop stalls, so this is optional until
profiling shows DB latency itself is a bottleneck.

### Step D — Caching (PENDING)

Memoize `load_settings()` and pass geo/location settings through a poll run
instead of re-reading per source.