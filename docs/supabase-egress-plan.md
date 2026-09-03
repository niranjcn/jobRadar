# Supabase Egress Optimization Plan — Zero-Risk, No Breaking Changes

> **Status:** Draft — ready for review, no code changes required to start
> **Goal:** Cut Supabase egress from **7.35 GB / 14 days (~538 MB/day)** to **< 500 MB / month** without changing any API contracts, frontend behavior, or job coverage.
> **Constraint:** Every phase must be independently reversible, independently testable, and must not break existing features. If a phase fails, roll back one env var / one file and the system returns to current behavior.

---

## Table of Contents

1. [Context — What We Verified](#1-context--what-we-verified)
2. [Why Egress Was 7.35 GB (Simple Explanation)](#2-why-egress-was-735-gb-simple-explanation)
3. [Guiding Principles (No Side Effects)](#3-guiding-principles-no-side-effects)
4. [What "Efficient" Means Here](#4-what-efficient-means-here)
5. [Phased Plan — Overview](#5-phased-plan--overview)
6. [Phase 0 — Measure & Baseline (Start Here, No Code)](#6-phase-0--measure--baseline-start-here-no-code)
7. [Phase 1 — Stop the Active Bleed (Config Only, 5 Minutes)](#7-phase-1--stop-the-active-bleed-config-only-5-minutes)
8. [Phase 2 — Shrink Every Database Round-Trip (Low Risk)](#8-phase-2--shrink-every-database-round-trip-low-risk)
9. [Phase 3 — Poll Less, But Smarter (Scheduling)](#9-phase-3--poll-less-but-smarter-scheduling)
10. [Phase 4 — Cache What Repeats (In-Memory, No New Infra)](#10-phase-4--cache-what-repeats-in-memory-no-new-infra)
11. [Phase 5 — Ship Less Data Per Request (Projection & Pagination)](#11-phase-5--ship-less-data-per-request-projection--pagination)
12. [Phase 6 — Retain Less, Prune More (Storage vs Egress Tradeoff)](#12-phase-6--retain-less-prune-more-storage-vs-egress-tradeoff)
13. [Phase 7 — Make Supabase Itself Quieter (Dashboard Toggles)](#13-phase-7--make-supabase-itself-quieter-dashboard-toggles)
14. [Phase 8 — Observe & Alert (So It Never Surprises You Again)](#14-phase-8--observe--alert-so-it-never-surprises-you-again)
15. [Phase 9 — Long-Term Architecture (No Action Now, Just Decision Frame)](#15-phase-9--long-term-architecture-no-action-now-just-decision-frame)
16. [Risk Matrix & Rollback Cheat-Sheet](#16-risk-matrix--rollback-cheat-sheet)
17. [Timeline & Effort](#17-timeline--effort)
18. [Definition of Done](#18-definition-of-done)
19. [Appendix A — How Supabase Bills Egress (Plain English)](#19-appendix-a--how-supabase-bills-egress-plain-english)
20. [Appendix B — Verification Queries You Can Run Today](#20-appendix-b--verification-queries-you-can-run-today)
21. [Appendix C — Checklist Before Merging Each Phase](#21-appendix-c--checklist-before-merging-each-phase)

---

## 1. Context — What We Verified

| Area | Evidence | Reading |
|------|----------|---------|
| **Local DB size** | `docker exec jobradar-postgres psql -U postgres -c "SELECT pg_size_pretty(pg_database_size('postgres'))"` | **129 MB** total, `jobs` table **111 MB** (69 MB heap + 39 MB indexes) for **185,211 rows**, avg **314 bytes**/row |
| **Descriptions** | `backend/migrations/011_clear_descriptions.sql:6`, `backend/app/models.py:38` | Only **864 rows** have a description, total **276 kB**. 99.5% are `NULL` — already optimized. |
| **`poll_runs` last 14d** | `SELECT count(*) FROM poll_runs WHERE started_at > now()-'14d'` | **2,752 runs**, **36,528,356 jobs_fetched** — avg **197 runs/day** |
| **Egress reported** | Supabase dashboard (user) | **7.35 GB / 14 days = ~538 MB/day** — billed as **Database + REST** egress |
| **Current env** | `backend/.env:4` | `SUPABASE_URL=http://postgrest:3000`, `DATABASE_URL=postgresql://postgres:postgres@postgres:5432/postgres` — **local Docker, not Supabase** (migrated 2026-08-28) |
| **Render** | `render.yaml:8-12` | `SUPABASE_URL`, `SUPABASE_KEY`, `DATABASE_URL` are `sync: false` — requires manual change on Render dashboard. Still points at old Supabase if not updated. |
| **Frontend -> Supabase direct?** | `frontend/lib/api.ts:8`, `frontend/next.config.mjs:14` | **Never.** Frontend only calls `http://localhost:8000/api/*` via FastAPI. No `supabase-js` import in `frontend/`. |
| **Realtime** | `SELECT * FROM pg_publication` | Publication `supabase_realtime` exists but **0 tables** subscribed — negligible. |
| **Old hot path** | `git show 8c70efc:backend/app/poller.py:95` vs `37538fb` | Before 2026-08-17, `fetch_existing_job_ids` paginated 1000-row REST pages (~20 round-trips for a 20k-job board). Fixed to single `query()` in `backend/app/poller.py:101`. |

**Conclusion:** Egress was not frontend abuse, not images, not storage. It was the **backend worker + FastAPI** repeatedly reading the `jobs` table from Supabase over the internet — every poll re-sent overlapping data.

---

## 2. Why Egress Was 7.35 GB (Simple Explanation)

Think of Supabase as a library. Your database is a **129 MB book** on the shelf. Egress is the number of **photocopies the librarian hands out**. Reading the whole book **122 times** = 7.35 GB of copies, even though the book itself is small.

```
Book size:                       129 MB (what is stored)
Full scan cost (185k rows * ~350B JSON):  ~61.8 MB per scan (what is sent)
Scans needed for 7.35 GB:        7,526 MB / 61.8 MB = ~122 scans in 14 days = 8.7/day
Actual poller did:               ~197 small scans/day (per-source, overlapping) => math fits
```

**Four contributors, in order:**

1. **Per-source dedup reads** (`backend/app/poller.py:101` `SELECT external_job_id FROM jobs WHERE source_id = %s`) — ~202 sources x ~35 kB/response x ~6 sweeps/day = **~42 MB/day** via REST (pre-fix) or **~25 MB/day** via pooler (post-fix). Small per call, huge in aggregate.
2. **Direct Postgres pooler reads** — Supabase counts **both** REST and `DATABASE_URL` (`backend/app/db.py:24` `psycopg_pool`) as egress. FastAPI endpoints (`backend/app/api/routes.py:256` `/jobs`) and matching (`backend/app/poller.py:327` `match_and_enqueue`) all went over the pooler while hosted on Render/laptop -> Supabase.
3. **High poll frequency** — 13 ATS crons (`backend/app/main.py:96`), Workday every **1800s**, others 3600s, plus 12h integrity sweep. Effective **~197 poll_runs/day**, each fetching 0-116k jobs.
4. **Historical bloat** — `raw_payload JSONB` (dropped in `008`) + full descriptions (nulled in `011`). Now fixed, but contributed to earlier scans.

> None of this is a bug in your code logic — it is **expected** when the compute and the database are on different clouds without caching/projection.

---

## 3. Guiding Principles (No Side Effects)

1. **No API contract changes** — `GET /api/jobs`, `/api/sources`, `/api/poll/runs` keep the same request/response shapes. Frontend needs zero changes.
2. **Config before code** — Phases 0-1 require only dashboard/env edits. Code phases are behind defaults that preserve current behavior unless an env var is set.
3. **One phase = one PR = one rollback lever** — Each phase ships alone, passes `ruff` + `pytest`, and can be reverted by reverting one commit or flipping one env var.
4. **Measure first, optimize second** — Every phase carries a before/after egress number so we prove impact.
5. **Adapter isolation stays** (`AGENTS.md:5`) — Adapters only fetch external career sites. They never touch egress logic.
6. **No new infra until proven** — No Redis/Kafka/K8s (`AGENTS.md:2`). In-memory + SQL is enough to reach <500 MB/month.

---

## 4. What "Efficient" Means Here

| Kind of efficiency | What we improve | Example |
|--------------------|-----------------|---------|
| **Bytes per query** | Send fewer columns, fewer rows | `SELECT id, title` instead of `SELECT *`; `LIMIT 50` already exists in `routes.py:264` |
| **Queries per poll** | Remove duplicates, batch | Fetch candidate jobs once and reuse for Telegram + email (`poller.py:357` already does `match_and_enqueue` per-source) |
| **Polls per day** | Poll when it matters | Slow boards (e.g., `Snyk 404`, `Rippling 404` in logs) need retries, but not every 30 min |
| **Distance** | Don't cross the internet | Local Postgres (`docker-compose.yml:2`) already does this for dev. Same idea for prod. |
| **Repeat work** | Cache | `load_location_mapping` per poll run, not per job |

Goal is **not** "fetch fewer jobs from Greenhouse/Lever" — that would hurt coverage. Goal is "touch Supabase fewer times and with smaller payloads for the same coverage".

---

## 5. Phased Plan — Overview

```
Phase 0  Measure & baseline          [dashboard, 30 min, no code]
Phase 1  Stop active bleed (Render)  [config, 5 min, no code]
Phase 2  Shrink DB round-trips        [code, 1 file, low risk]  -40% egress
Phase 3  Poll less but smarter        [config + 1 file]         -50% egress
Phase 4  In-memory cache              [code, 2 files]           -10% egress
Phase 5  Projection / pagination      [code, 2 files]           -15% egress
Phase 6  Retention / prune            [sql + config]            -5% egress, keeps DB small
Phase 7  Supabase quiet mode          [dashboard toggles]       -5% egress
Phase 8  Observe & alert              [code + dashboard]        prevents relapse
Phase 9  Long-term choice             [decision doc]            no action now
```

Each phase states **risk, rollback, verification, and expected egress saving**. Phases 0-3 alone bring you from **7.35 GB/14d to ~2 GB/14d**. Adding 4-7 reaches **<1 GB/month**.

---

## 6. Phase 0 — Measure & Baseline (Start Here, No Code)

**Why:** You cannot optimize what you do not measure. Supabase's 7.35 GB number is a trailing 14-day total — we need the breakdown by product.

**What to do:**

1. Open Supabase Dashboard -> Project -> **Reports** -> **Network Egress** (or Billing -> Usage).
2. Record three numbers for the last 14 days:
   * **Database Egress** (pooler/direct)
   * **REST Egress** (`/rest/v1/`)
   * **Auth / Realtime / Storage Egress**
3. Take a screenshot and note the date. This is your baseline.
4. Locally, run the queries in **Appendix B** and record: `jobs` count/size, `poll_runs` count/day, avg `sources` JSON size.

**Files:** none.

**Risk:** none.

**Rollback:** N/A.

**Verification:** Dashboard numbers exist and match the 7.35 GB total (±0.5 GB). If Database >> REST, Cause B is confirmed; if REST >> Database, Cause A is dominant.

**Egress saving:** 0 — but unlocks correct prioritization for all later phases.

---

## 7. Phase 1 — Stop the Active Bleed (Config Only, 5 Minutes)

**Why:** Your laptop (`backend/.env`) already points to local Postgres, so local egress is 0. But `render.yaml:8-12` is `sync: false` — **Render's live deployment may still point at Supabase** and keep adding egress even now.

**What to do (choose one, no code):**

* **Option 1A — Recommended:** Render Dashboard -> Service `jobradar` -> Environment -> update:
  * `SUPABASE_URL` -> `http://postgrest:3000` **or** leave Supabase but set `JOBRADAR_DISABLE_SCHEDULER=1` on Supabase-hosted service while you validate local.
  * Better: if you intend to move off Supabase entirely, set `DATABASE_URL` to your self-hosted Postgres (Neon, Fly Postgres, or keep Render's Postgres addon) and rotate `SUPABASE_KEY`. This instantly stops new egress.
* **Option 1B — Pause to prove:** Render -> Suspend service for 24h. Check Supabase egress the next day — if it flatlines to near 0, Render was the source.
* **Option 1C — Keep Supabase but throttle:** If you must stay on Supabase for now, set `POLL_INTERVAL_SECONDS=21600` (6h) on Render only. This cuts poll volume by 6x without code.

**Files:** `render.yaml` (only doc update), Render dashboard (real change).

**Risk:** **Low.** Config-only. Scheduler disable is respected in `backend/app/main.py:217` (`JOBRADAR_DISABLE_SCHEDULER`) and `backend/app/db.py:41` handles both local and Supabase URLs.

**Rollback:** Revert env var in Render dashboard -> Redeploy -> previous behavior returns in <2 min.

**Verification:**
* `docker logs jobradar-web` should show `scheduler disabled via JOBRADAR_DISABLE_SCHEDULER` if you chose disable.
* Supabase egress 24h later should drop to <50 MB/day (only health checks).

**Egress saving:** **100% of ongoing Render-driven egress** — typically **60-80% of total** when local dev is already off Supabase. If Render drives 300 MB/day, this phase alone saves **~4.2 GB / 14 days**.

---

## 8. Phase 2 — Shrink Every Database Round-Trip (Low Risk)

**Why:** Even after `37538fb`, some paths still fetch **more than needed**: e.g., `/api/jobs/filters` scans all sources + all countries, and `notification_queue` drains unscoped.

**What to change (single PR, two files):**

* **2a. Scope `notification_queue` drain** — `backend/app/notification_queue.py` currently does `SELECT *`. Change to `WHERE status='pending' AND scheduled_for <= now()` with `LIMIT 400` (already has `DRAIN_BATCH=400`) and project only `id, user_id, job_id, channel`. This is a `SELECT` projection change, not logic change.
* **2b. Tighten `fetch_existing_job_ids` cache** — `backend/app/poller.py:95` already uses SQL, but it runs **once per source per poll**. For sources with 0 new jobs, the same set is re-fetched each interval. Add an **in-poll-run LRU** (dict `source_id -> set[ids]` valid for the current `poll_all_sources` call only) so a repeated fetch within one sweep is free. Lifetime = one poll run, not cross-run, so correctness is trivial.
* **2c. Replace `supabase.table(...).upsert` hot path with SQL `INSERT ... ON CONFLICT`** for `jobs` upsert — Supabase REST JSON encoding is ~1.3x larger than Postgres binary. Keep REST for rare paths (`sources` upsert) for now.

**Files:** `backend/app/poller.py:95`, `backend/app/notification_queue.py`, `backend/app/db.py:60` (add `execute()` helper that ignores result sets).

**Risk:** **Low-Med.** Queries are strictly narrower. `ON CONFLICT` already has `UNIQUE(source_id, external_job_id)` in `migrations/001_initial.sql:22`.

**Rollback:** Revert one commit; previous REST path still exists in git history.

**Verification:**
* `pytest backend/tests/` — existing 98 unit tests still pass.
* `docker exec jobradar-postgres psql -c "EXPLAIN SELECT external_job_id FROM jobs WHERE source_id = '...'"` shows `Index Scan using jobs_source_id_idx` (already indexed).
* Supabase egress 24h delta before/after (check Reports).

**Egress saving:** **~30-40%** of Database egress. Fewer bytes per query + fewer queries per sweep.

---

## 9. Phase 3 — Poll Less, But Smarter (Scheduling)

**Why:** 197 poll runs/day is higher than the 13 ATS crons imply. Reason: overlapping retries, `poll-all-integrity` 12h sweep, manual triggers (`backend/app/api/routes.py:549` `/poll/run`), plus unhealthy re-runs (`routes.py:601`). Polling a healthy board every 30 min that rarely changes (e.g., `Retool 404` or `Snyk 404` in logs) wastes egress.

**What to change (config + one file):**

* **3a. Make intervals data-driven, not fixed.** `backend/app/config.py:8` `ATS_DEFAULT_SECONDS` + `backend/app/schedule_store.py` already supports per-ATS overrides. Change defaults:
  * `workday: 1800 -> 3600` (30m -> 1h) for large boards that rarely change
  * `greenhouse/lever/ashby: 3600 -> 5400` (1h -> 1.5h) for healthy boards; keep **30m only** for boards with recent `jobs_new > 0`
  * `avature: 21600` stays (already 6h)
  * Add **backoff**: if a source's last 3 polls had `fetched==0` or `status==error` (e.g., 404 boards like `rippling`, `snyk`), double its interval up to 12h. `backend/app/poller.py:333` `_poll` already records `fetched`/`error`, so this reads `sources.last_error`.

* **3b. Jitter & coalesce.** `backend/app/main.py:98` already uses `CronTrigger`. Add ±10% jitter and `coalesce=True` (already set at `main.py:105`) so 13 ATS jobs do not all fire at `00:00`.

* **3c. Skip empty sweeps.** Before a scheduled run, `backend/app/main.py:64` already checks `status='running'` locks. Extend to: if no source in that ATS has `last_checked_at < now() - interval`, skip the run (avoid duplicate sweep when manual trigger already covered it).

**Files:** `backend/app/config.py:8`, `backend/app/main.py:91`, `backend/app/schedule_store.py`, `backend/.env.example` (document `POLL_INTERVAL_*`).

**Risk:** **Low.** Intervals only via env/DB overrides, live-editable on `/schedule` page (`frontend/app/(app)/schedule/page.tsx`). No ingestion logic changes.

**Rollback:** `PUT /api/schedule/{ats}` reset (`routes.py:754` `delete_schedule`) or revert `ATS_DEFAULT_SECONDS`.

**Verification:**
* `GET /api/schedule` shows new `interval_seconds` and `next_run_at`.
* `SELECT ats_type, count(*) FROM poll_runs WHERE started_at > now()-'24h' GROUP BY ats_type` count drops by ~50% while `jobs_new` stays similar (same new jobs, fewer empty polls).

**Egress saving:** **40-60%** of current poll-driven egress. Halving poll frequency halves the per-source dedup reads.

---

## 10. Phase 4 — Cache What Repeats (In-Memory, No New Infra)

**Why:** The same small tables are read **hundreds of times per day**: `sources` list (202 rows), `app_settings` location mapping, `preferences`, `poll_schedule` intervals.

**What to change:**

* **4a. Cache `load_settings()`** — `backend/app/config.py:88` calls `load_dotenv()` on every request. Memoize with TTL 60s (invalidate on env change). One function, no API change.
* **4b. Cache `load_location_mapping` per poll run** — Pass `geo_settings` object through `poll_source` (`backend/app/poller.py:183` already loads it once per run and reuses). Ensure `map_location` hits cache, not DB.
* **4c. Cache `/geo/countries` index** (`backend/app/geo.py:load_geo_index`) in memory; it is a static file.

**Files:** `backend/app/config.py:88`, `backend/app/poller.py:183`, `backend/app/geo.py`.

**Risk:** **Very low.** In-memory only, TTL < 2 min, so preference changes appear quickly anyway (schedule page triggers immediate re-read).

**Rollback:** Remove decorator, revert.

**Verification:** Add `LOG` line on cache miss; miss rate should be <5%.

**Egress saving:** **~5-10%** alone, but combines with Phase 3 to reduce DB round-trips further.

---

## 11. Phase 5 — Ship Less Data Per Request (Projection & Pagination)

**Why:** Even with smaller scans, any `SELECT *` still ships `url` (18 MB total), `location`, etc. API list endpoints already paginate (`routes.py:264` `limit=50`), but some helper queries are broad.

**What to change:**

* **5a. Audit and project.** Every `supabase.table(...).select("*")` and `query("SELECT *")` becomes explicit columns. Example: `backend/app/api/routes.py:256` `/jobs` already projects `id, source_id, external_job_id, title, location, url, first_seen_at, countries, is_remote` — **not** `description`. Keep that. Change `fetch_sources` (`backend/app/poller.py:43` `select("*")` -> `select("id, company_name, ats_type, board_identifier, active, last_checked_at, last_error")`).
* **5b. Compress `poll_runs.sources` JSONB.** Currently avg **2,459 bytes** per run (`2448 bytes` measured), max 37 kB. Store per-ATS summary instead of per-company when >100 companies: `{ats_type, companies_total, healthy, fetched_total}` plus error list only. Frontend `frontend/app/(app)/runs/page.tsx:62` already shows per-source lines, so keep per-source **only for non-healthy** runs; for healthy sweeps store aggregates. This cuts `poll_runs` egress ~60%.
* **5c. Enable HTTP compression.** FastAPI `GZipMiddleware` (add in `backend/app/main.py:252`) + Postgres `pg_total_relation_size` is already small. PostgREST already gzips. Ensure `Accept-Encoding: gzip` is set by `@/lib/api.ts`.

**Files:** `backend/app/poller.py:43`, `backend/app/api/routes.py`, `backend/app/main.py:259` (middleware), `backend/migrations/` (for `poll_runs` JSONB doc).

**Risk:** **Low.** Projection is strictly fewer columns; compression is transparent. Frontend already handles `description: null` (`routes.py:200`).

**Rollback:** Revert select lists; decompress is no-op.

**Verification:**
* `SELECT pg_column_size(row) FROM (SELECT * FROM jobs LIMIT 1)` vs projected size delta.
* `GET /api/jobs?limit=50` response `content-encoding: gzip` and body is parseable.

**Egress saving:** **10-20%** on REST paths.

---

## 12. Phase 6 — Retain Less, Prune More (Storage vs Egress Tradeoff)

**Why:** More rows = larger scans = more egress, even with small rows. You already have `JOB_RETENTION_DAYS=30` (`backend/app/poller.py:307` `prune_old_jobs`) and `MAX_POSTING_AGE_DAYS=90`. Current 185k rows = 129 MB; each +30 days adds ~50k rows.

**What to change:**

* Keep `JOB_RETENTION_DAYS=30` (already aggressive). **Do not lower further** unless storage pressure — 30 days already prunes well (`poller.py:129` deletes cascades to `job_matches`, `notifications_sent`).
* **Add prune for `poll_runs`** (no retention today): `DELETE FROM poll_runs WHERE started_at < now() - interval '30 days'` as a daily cron next to `prune_old_jobs`. At 197 runs/day * 30 days = ~6k rows, keeps `poll_runs` at ~6.5 MB * (30/14) instead of growing forever (currently 3,162 rows).
* **No change** to `jobs` retention without product decision — fewer days = fewer searchable jobs on `/jobs` page.

**Files:** `backend/app/poller.py:128` (add `prune_poll_runs`), `backend/.env.example` (document `POLL_RUNS_RETENTION_DAYS`).

**Risk:** **Low.** Purely deletions of derived/logs data; `jobs` still 30d. `poll_runs` is append-only log, not needed for correctness.

**Rollback:** Stop calling the prune function.

**Verification:** `SELECT count(*) FROM poll_runs` drops, `GET /api/poll/runs?limit=10` still returns recent runs.

**Egress saving:** **5% indirect** — smaller scans over time.

---

## 13. Phase 7 — Make Supabase Itself Quieter (Dashboard Toggles)

**Why:** Supabase has services you pay egress for but do not use: Realtime WAL shipping, Vault, GraphQL, unused auth flows.

**What to toggle (dashboard only, no code):**

* **Realtime:** Project -> Database -> Publications -> ensure no tables are added to `supabase_realtime` (currently 0). Keep it that way.
* **GraphQL:** Project -> API -> GraphQL -> **Disable** if not used (no frontend uses it).
* **Auth:** Project -> Authentication -> keep **email** only; disable OAuth providers you do not use (reduces `auth` egress + email sends).
* **Backups/PITR:** Keep daily backups, but note that dashboard-initiated restores/exports also count as egress (rare).
* **Connection pooling:** Keep **Transaction mode** (pooler), not `Session` — already via `DATABASE_URL` pooler host. Transaction mode multiplexes and compresses.

**Files:** none (dashboard).

**Risk:** none.

**Rollback:** Re-enable toggle.

**Verification:** Supabase Reports -> **Realtime** egress near 0 confirms.

**Egress saving:** **0-5%**, but removes surprise line items.

---

## 14. Phase 8 — Observe & Alert (So It Never Surprises You Again)

**Why:** The 7.35 GB bill surprised you. Make future egress visible in your own dashboard before Supabase bills you.

**What to change (small):**

* **8a. Log egress proxy metric.** In `backend/app/db.py:60` `query()`, add a debug counter: `bytes_out = sum(len(str(row)))` per query + `backend/app/api/routes.py` response size via middleware. Log as `egress_estimate_bytes`. Not exact, but trends well, stays local, costs 0 egress itself.
* **8b. Add `/api/admin/egress` endpoint** (admin-only, reusing `get_current_admin` from `routes.py:402`) returning: `jobs_total`, `jobs_bytes`, `poll_runs_last_24h`, `estimated_egress_last_24h`. Frontend admin page (`frontend/app/admin/page.tsx`) shows it.
* **8c. Supabase alert.** Supabase Dashboard -> Billing -> Usage Alerts -> set alert at **3 GB** (60% of 5 GB free tier). You already have Telegram (`TELEGRAM_ENABLED`) — forward the Supabase webhook to Telegram via `backend/app/notify.py`.
* **8d. Weekly check.** Add to `CHANGELOG.md` process: every Monday, paste Supabase Reports egress screenshot into `docs/supabase-egress-plan.md` history table below.

**History table to fill:**

| Week | Database | REST | Realtime | Total | `jobs` count | `poll_runs`/day | Notes |
|------|----------|------|----------|-------|--------------|-----------------|-------|
| 2026-W35 | ? | ? | ~0 | **7.35 GB / 14d** | 185k | 197 | Baseline (this plan) |
| 2026-W36 |  |  |  |  |  |  | After Phase 1 |
| 2026-W37 |  |  |  |  |  |  | After Phase 3 |

**Files:** `backend/app/db.py:60`, `backend/app/api/admin_routes.py`, `frontend/app/admin/page.tsx`, docs.

**Risk:** **Very low.** Read-only, admin-gated.

**Rollback:** Remove endpoint.

**Verification:** `GET /api/admin/egress` returns numbers; Supabase alert fires in test.

**Egress saving:** 0 directly, but **prevents the next 7 GB bill**.

---

## 15. Phase 9 — Long-Term Architecture (No Action Now, Just Decision Frame)

Pick **one** when you outgrow the current local+Render split:

| Option | When | Egress | Complexity |
|--------|------|--------|------------|
| **A. Stay on Supabase, but co-locate compute** | You like Supabase auth/storage | **Low** if backend runs in same region (e.g., Fly `iad` + Supabase `us-east-1`). Egress within-region is cheaper/free on many providers. | Low |
| **B. Self-host Postgres** (current local is a prototype) | You own 185k+ rows, want predictable cost | **~0 Supabase egress**, pay only VPS egress (Hetzner/Fly/Neon). You already have `docker-compose.yml:2` postgres. | Medium (backups, PITR) |
| **C. Hybrid: Supabase for Auth only, Postgres elsewhere** | Need RLS/multi-tenant but not DB egress | Auth egress is tiny; DB egress moves off Supabase. | Medium |

**Recommendation for now:** Do **Phases 0-8** first. Phase 9 is only if Phase 3+4+5 do not bring you under 1 GB/month. The current `docker-compose.yml` postgres is production-capable for your scale (129 MB DB, 200 sources).

---

## 16. Risk Matrix & Rollback Cheat-Sheet

| Phase | Risk | Blast radius | Rollback |
|-------|------|--------------|----------|
| 0 Measure | None | None | N/A |
| 1 Render env | Low | Render only | Change env back, redeploy (<2 min) |
| 2 Query shrink | Low | Backend reads | `git revert <commit>` |
| 3 Poll intervals | Low | Scheduler only | `PUT /api/schedule/{ats}` reset or `git revert` |
| 4 Cache | Very low | In-memory | Remove decorator |
| 5 Projection | Low | API responses | Revert `select()` lists |
| 6 Retention | Low | Old data lifetime | Stop cron |
| 7 Dashboard toggles | None | Supabase services | Toggle back |
| 8 Observability | Very low | Logs + admin page | Remove endpoint |
| 9 Architecture | N/A (decision only) | — | — |

**Global rollback lever:** `backend/.env.supabase.bak` is kept per `backend/.env:2` comment. To fully return to pre-local state: `copy .env.supabase.bak to .env && docker compose down/up`.

---

## 17. Timeline & Effort

```
Week 1  Phase 0 + 1   (today, 1 hour total) -> egress flatlines
Week 2  Phase 2 + 3   (one PR each, 2-3h each) -> -60% egress, verify via dashboard
Week 3  Phase 4 + 5   (one PR, 2h) -> -15% more
Week 4  Phase 6 + 7 + 8 (polish, 2h) -> steady state + alerts

Total: ~8 hours engineering, 3 PRs, 0 infra spend.
```

Each PR follows `AGENTS.md:23` — small, focused, `ruff` + `pytest` green, reviewer required.

---

## 18. Definition of Done

Per `AGENTS.md:25`, a phase is done when:

- [ ] Code/Config implemented and reviewed
- [ ] Tests added (fixture-based, no live Supabase) and `pytest` green
- [ ] `ruff check` + `ruff format` clean
- [ ] Supabase dashboard egress for the next 7 days is lower than baseline (screenshot attached to PR)
- [ ] Rollback tested once (flip env var / revert commit and confirm recovery)
- [ ] `docs/supabase-egress-plan.md` history table updated
- [ ] No secrets committed (`.env` stays gitignored per `AGENTS.md:18`)

---

## 19. Appendix A — How Supabase Bills Egress (Plain English)

Supabase egress = every byte that **leaves** Supabase's network:

* **Database egress** — responses to `DATABASE_URL` (pooler) queries. `backend/app/db.py:24` `psycopg_pool` counts here.
* **REST egress** — responses to `supabase.table(...).execute()` (`backend/app/db.py:37` `get_supabase()`). Even `SELECT external_job_id` (tiny) counts.
* **Auth / Realtime / Storage egress** — you use Auth lightly (3 users) and Realtime not at all (0 tables) and Storage not at all, so these are near 0.
* **Free tier:** 5 GB/month. Your 7.35 GB / 14 days = **~15 GB/month** pace, hence the overage notice. After local migration + Phase 1, you should be **<1 GB/month**.

---

## 20. Appendix B — Verification Queries You Can Run Today

```sql
-- Local DB size (run on local: docker exec jobradar-postgres psql -U postgres)
SELECT pg_size_pretty(pg_database_size('postgres')) AS db_size;
-- 129 MB expected

-- Jobs breakdown
SELECT count(*) AS total_jobs,
       pg_size_pretty(sum(pg_column_size(description))::bigint) AS desc_bytes,
       count(*) FILTER (WHERE length(description) > 100) AS jobs_with_desc
FROM jobs;
-- 185k, 276 kB, ~132 expected

-- Poll runs last 14 days
SELECT date_trunc('day', started_at) AS day, count(*) AS runs, sum(jobs_fetched) AS fetched
FROM poll_runs GROUP BY 1 ORDER BY 1 DESC LIMIT 14;
-- ~197/day expected before Phase 3

-- Avg JSON per poll run
SELECT pg_size_pretty(avg(octet_length(sources::text))::bigint) AS avg_run_json
FROM poll_runs;
-- ~2.4 kB expected
```

---

## 21. Appendix C — Checklist Before Merging Each Phase

```text
[ ] git fetch origin && git rebase origin/main
[ ] ruff check backend/ && ruff format backend/ --check
[ ] pytest backend/tests/ -q
[ ] .env.example updated if new env var introduced
[ ] No SUPABASE_KEY / DATABASE_URL / TELEGRAM_BOT_TOKEN in diff
[ ] Supabase dashboard egress screenshot before/after attached to PR
[ ] Rollback step tested locally (flip env / revert commit)
[ ] AGENTS.md:5 — adapters unchanged and isolated
```

---

> **Next step:** Review this plan, then run **Phase 0 + 1** (30 min, no deploy freeze). Paste your Supabase Reports breakdown here and we will confirm whether Database or REST is dominant before coding Phase 2. If you want, I can ship Phases 2-3 as separate PRs after your approval.
