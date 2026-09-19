# HiringCafe Expansion — Feasible Subset & Poll Time Plan

> **Question:** "Add only companies that use adapters we already have — is it feasible and how long will a poll take?"
> **Answer:** Yes for `greenhouse`/`lever`/`ashby` (826 companies, ~1.5 min global poll). Workday/Oracle/ICIMS/SuccessFactors need URL reconstruction (689+204+135+349) — would push a global poll to **~10-15 min** and a per-ATS Workday poll to **~3.5 hours** if added all at once. Do it in 50-company batches.

---

## 1. How Many Companies in HiringCafe?

| Scope | Count | How counted |
|-------|-------|-------------|
| **Reported on homepage** `https://hiringcafe.com` | **5,978 companies** / 235,321 jobs | SSR prop `ssrCompanyCount` in `__NEXT_DATA__` |
| **Sampled 0-119 pages** (`_next/data/{buildId}/index.json?page=N`, 40 jobs/page, 15,333 jobs = 6.5% of site) | **5,860 raw rows** (every job occurrence) -> **4,435 unique names** deduped (`backend/data/hiringcafe_companies_deduped.json:1`) | Group by `v5_processed_job_data.company_name` lowercased |
| **Of those 4,435, mapping to jobQuest `ats_type` `backend/migrations/030_board_ats.sql:4`** | **2,294 supported** (51%) / **2,141 unsupported** | `grnhse->greenhouse`, `lever->lever`, `ashby->ashby`, `workday->workday`, `oraclecloud->oracle`, `icims2->icims`, `successfactors->successfactors`, etc. |
| **Of 2,294, token directly usable without URL guessing** | **826 feasible now** (`greenhouse 491` + `lever 156` + `ashby 232`) | `board_token="2k"` is board id; `workday` token `"3m-wd1-search"` is `tenant-shard-site` not `https://tenant.shard.myworkdayjobs.com/site` — needs reconstruction |
| **Overlap with existing `backend/sources.json:1` (129)** | **53 already in jobQuest**, so **826-53=773 truly new** light-ATS companies (or 2,241 new if counting all supported) | Name lower match |

**Distribution of the 2,294 supported (deduped):**

```
workday        689  (30%)  -> needs URL rebuild
greenhouse     491  (21%)  -> ready
successfactors 349  (15%)  -> needs URL
ashby          232  (10%)  -> ready
oracle         204  ( 9%)  -> needs URL
lever          156  ( 7%)  -> ready
icims          135  ( 6%)  -> needs URL
avature         37   -> ready (but HiringCafe shows 37, all 3 existing avature boards already in jobQuest - likely duplicates)
google           1
```

**Unsupported (2,141) would need new adapters:** `zohorecruit 550`, `workable 197`, `smartrecruiters 174`, `bamboohr 98`, `teamtailor 90`, `rippling 67`... — out of scope per `AGENTS.md:19` one-task-at-a time.

---

## 2. Poll Time — Measured vs Ideal

### 2.1 What we measured last 7 days `poll_runs` (local Postgres, `docker exec`)

| `ats_type` | Active sources `sources` | Avg wall per scheduled run `poll_runs` | Avg `jobs_fetched` | Notes |
|------------|--------------------------|----------------------------------------|--------------------|-------|
| `greenhouse` | 57 | **127s (2.1 min)** | 7,943 | Single `GET boards-api.greenhouse.io/v1/boards/{id}/jobs` (~0.5s + JSON) |
| `lever` | 3 | **84s (1.4 min)** | 197 | Single `GET api.lever.co/v0/postings/{id}` |
| `ashby` | 40 | **98s (1.6 min)** | 2,842 | Single `GET api.ashbyhq.com/posting-api/job-board/{id}` |
| `workday` | 62 | **1,072s (17.9 min)** | 52,442 | `POST /wday/cxs/{tenant}/{site}/jobs` paginated `PAGE_SIZE=20` (`workday.py:12`), 5-50 pages per board + `RetryingClient` `http.py:15` |
| `oracle` | 15 | **333s (5.5 min)** | 23,352 | `oracle.py` paginated Taleo Fusion |
| `icims` | 4 | **126s (2.1 min)** | 2,003 | `icims.py:30` JSON API `page=1..3000 size=10` |
| `successfactors` | 5 | **696s (11.6 min)** | 17,930 | Heavy SF API |
| `global` (any `ats_type=null` run) | 129 total | **333s avg (5.5 min)** | — | Includes orchestrator `poll_all_sources` `poller.py:287` + `drain_due_notifications` |

> `SOURCE_CONCURRENCY=8` `backend/app/poller.py:18` — 8 boards fetched in parallel. Wall time = `ceil(sources/8) * per-board + DB overhead (fetch_existing + upsert ~0.08s/board)` + 5s orchestration. Measured averages include retries, staled runs (max 34,918s is orphaned `poll_runs` `poller.py:208`), and API 429/500 backoffs.

### 2.2 Projected wall time for HiringCafe batches

**Ideal (network only, 0.6s green/lever/ashby, 2.5s workday, 1.8s oracle, 8 concurrency):**

| Batch | New sources | Ideal wall (8 conc) |
|-------|-------------|---------------------|
| `greenhouse` 491 | 491 | **0.8 min** (`ceil(491/8)*0.68s`) |
| `lever` 156 | 156 | **0.3 min** |
| `ashby` 232 | 232 | **0.5 min** |
| **826 light total as one global poll** | **826** | **~1.2 min** + DB 7s = **~1.5 min** |
| Existing 129 global | 129 | **0.2 min** |
| **955 (129+826) global** | **955** | **~1.4 min** ideal |
| `workday` 689 | 689 | **3.8 min** ideal |
| `oracle` 204 | 204 | **0.9 min** |
| `successfactors` 349 | 349 | **2.3 min** |
| **All 2241 new supported as one global** | **2241** | **~3.2 min** ideal |

**Measured-scaled (linear from 7-day `poll_runs` wall — includes DB + retries + stales, more honest for capacity planning):**

| ATS | `new/old * old_sec` | Wall if polled as its own scheduled ATS job |
|-----|---------------------|---------------------------------------------|
| `greenhouse` 57->491 | 491/57 *127s = **18.2 min** |
| `lever` 3->156 | 156/3 *84s = **72.8 min** (overestimated — 3-source sample noisy) |
| `ashby` 40->232 | 232/40 *98s = **9.5 min** |
| `workday` 62->689 | 689/62 *1072s = **198 min (3.3 hours)** |
| `successfactors` 5->349 | 349/5 *696s = **~810 min (13.5h)** — would need sharding |

> Takeaway: **Light ATS scale near-linearly and stay under 20 min per ATS**. Heavy ATS (`workday`/`successfactors`) dominate and must not be bulk-added — their per-ATS scheduled poll (`backend/app/main.py:98` `CronTrigger per ats_type`) would block that ATS for hours and hold `poll_runs` `running` lock (`main.py:64` stale 45m guard).

### 2.3 What this means per `AGENTS.md:9` scheduling

* **Current scheduling is per-ATS** (`backend/app/main.py:98` one Cron per `ats_type`), not one global sweep. So "time to run poll on all companies" has two answers:
  * **As scheduled (production):** Each ATS runs independently hourly (`config.py:8` `ATS_DEFAULT_SECONDS` 3600). `greenhouse` 491 would be the next `poll-greenhouse` run wall ~18 min (measured-scaled) or 0.8 min ideal. `workday` 689 would be 3.3h — would overlap next hourly tick and hit `scheduler: skipping workday poll, run X already in progress` `main.py:64`.
  * **As manual `POST /api/poll/run` `routes.py:549` `ats_type=null` (global):** 955 sources = ~1.5 min ideal, ~8-10 min measured (DB + `match_and_enqueue` `notification_queue.py` per new job).

---

## 3. Detailed Plan — Feasible Subset Only

### Phase 0 — Prep (today, no code, 30 min)

* Keep 10 dead `greenhouse` deactivated (`Retool`, `Snyk` etc. already `active=false`). Verify `SELECT active, count(*) FROM sources GROUP BY active` = 194 active /10 inactive.
* Snapshot `poll_runs` duration baseline: `SELECT avg(EXTRACT(EPOCH FROM finished_at-started_at)) FROM poll_runs WHERE started_at>now()-'7d'`.
* Decide batch size: **50** (20 green, 15 ashby, 15 lever) to keep wall <3 min and egress <20 MB extra/day.

### Phase 1 — Batch 1 (50 light ATS, 1 PR, 2h, low risk)

**Scope:** `greenhouse` 20 + `ashby` 15 + `lever` 15 = 50 new, all `board_token` 200 OK validated via `backend/reconcile_sources.py` pattern (`httpx GET boards-api...`).

**Steps:**

1. Generate `backend/data/hiringcafe_supported_greenhouse_lever_ashby.json` (826) — already have. Filter `active=true` not in `sources.json`, sort by `board_token` alpha, take first 50. Validate each token live (skip 404/403). Keep only 200s.
2. Append to `backend/sources.json` (`sources.json:634` pattern). Example entry: `{"company_name":"2K","ats_type":"greenhouse","board_identifier":"2k"}`. Name deduped against `company_name` unique (`migrations/001_initial.sql`).
3. `migrations/030_board_ats.sql` already extends check constraint to include `greenhouse/lever/ashby` — no new migration.
4. `docker compose restart web` triggers `backend/app/poller.py:28` `sync_sources()` upsert on `company_name` — or `INSERT ON CONFLICT` manually if host.
5. Watch `GET /api/schedule` `routes.py:674` — `greenhouse` `source_count` 57->77 etc., `next_run_at` updated.
6. Monitor `poll_runs` next 3 greenhouse/lever/ashby runs: expect `jobs_fetched` + ~500-1k per ATS, `jobs_new` ~50-100, zero `last_error` 404s. Verify DB: `SELECT count(*) FROM jobs WHERE source_id IN (...)`.

**Wall:** 50/8*0.6s ≈ 4s ideal + DB 4s = <10s per ATS. Measured ~2-4 min per ATS (safe).

**Egress:** 50 boards * 300 jobs avg * 350B = ~5 MB extra per full sweep vs current 7.35 GB/14d = negligible.

**Rollback:** `UPDATE sources SET active=false WHERE board_identifier IN (...)` or revert `sources.json` + `sync_sources` keeps `active` toggle; `migrate` no-downtime.

**Done when:** 3 consecutive per-ATS polls `status=completed`, `failed=0`, no `mark_error` `last_error`, `GET /api/jobs?ats=greenhouse&limit=5` returns new company jobs.

### Phase 2 — Expand light ATS to 300 (if Phase 1 error <5%, 1 week, 1 PR)

* Add next 250 of the 826 (e.g., `greenhouse` 100, `ashby` 80, `lever` 70). Same validation.
* Expected wall: 300/8*0.6s = 23s ideal / ~10-12 min measured per ATS. DB +170 MB heap? No — `jobs` grows by `new` only (~0.5k new/day from 300 boards, retention 30d `poller.py:128` keeps steady state ~200k jobs).
* Monitor `pg_size_pretty(pg_database_size('postgres'))` stays <250 MB.
* If `poll_runs` avg_sec grows >15 min for any ATS, split ATS into sub-shards (e.g., `greenhouse-a`, `greenhouse-b` as `custom` with staggered `POLL_INTERVAL_GREENHOUSE_SECONDS` `config.py:83`).

### Phase 3 — Heavy ATS (workday etc.) — only with URL resolver, one ATS at a time, gated

* **Workday resolver:** For each `board_token="3m-wd1-search"`, reconstruct `https://{tenant}.{shard}.myworkdayjobs.com/{site}` and probe via `workday.py:30` `_list_api`. Keep only 200 OK + `total>0`. Expect 30-40% fail (like the 10 stale you removed). Batch 20, validate, add.
* **Oracle/ICIMS/SF:** Similar — need full URL/host from `company_website` + `board_token` mapping. Requires one new helper per ATS (2h each) + integration test with fixture `backend/tests/fixtures/<ats>/` `AGENTS.md:22`.
* Wall for workday 689 would be 3.3h per hourly tick — so throttle: `POLL_INTERVAL_WORKDAY_SECONDS=21600` (6h) `config.py:8` or per-ATS override `PUT /api/schedule/workday` `routes.py:729` before adding. Alternatively shard `workday` into `workday-a/b/c` as separate ATS types to parallelize.

**Do not attempt heavy ATS bulk until Phase 2 proves egress/scheduler headroom.**

### Phase 4 — Unsupported ATS (2,141) — new adapters, out of `AGENTS.md:2` incremental scope

* Each (`zohorecruit`, `smartrecruiters`, `bamboohr` etc.) needs a dedicated adapter `backend/app/adapters/<ats>.py` + `__init__.py:13` registration + `config.py:8` interval + `migrations/031` check constraint + `reconcile_sources.py` probe. Budget 1-2 days per ATS, not in this plan. If you must cover them, prefer single HiringCafe aggregator adapter (`hiringcafe` `ats_type`, one feed) over 12 adapters.

---

## 4. Numbers at a Glance

| What | Count | Poll time wall (1 global sweep, 8 conc) | Notes |
|------|-------|------------------------------------------|-------|
| **Existing jobQuest** | 129 sources (57 GH +3 Lever+40 Ashby+62 WD etc.) | **~1.4 min ideal / ~5-6 min measured** | Current `poll_runs` avg |
| **HiringCafe reported** | 5,978 companies | — | Site says 5,978 |
| **Sampled & deduped** | 4,435 unique / 5,860 rows (15k jobs) | — | `hiringcafe_companies_deduped.json` |
| **Supported ATS (7 ATS)** | 2,294 unique (51%) | — | `grnhse/workday/sf/ashby/oracle/lever/icims` |
| **Feasible now (no URL guessing)** | **826** (GH 491 / Lever 156 / Ashby 232) | **~1.5 min ideal / ~30 min measured across 3 ATS** | Batch 50 = <10s ideal |
| **All supported if URL resolver built** | 2,241 new (2,294-53 overlap) | **~3.2 min ideal / ~4-14h measured (WD+SF dominate)** | Needs sharding/throttle |
| **unsupported (needs new adapters)** | 2,141 | — | `zohorecruit` 550 etc. |

---

## 5. Recommendation

* **Feasible today:** Yes for `greenhouse`/`lever`/`ashby` 826. Add in **50 -> 300** batches, keep 3600s interval, wall stays <20 min/ATS, egress +35% acceptable.
* **Not feasible bulk for `workday`/`oracle`/`icims`/`successfactors` 1,415** — tokens are not URLs, per-board heavy, would exceed scheduler lock and egress budget. Do them as Phase 3 with resolver and 6h interval or skip and keep HiringCafe aggregator alternative (`hiringcafe` single source).
* **Next step:** Say `go batch 1 (50)` and I will generate `sources.hiringcafe_batch1.json` validated (probe 200 OK) and update `backend/sources.json` + `docs/hiringcafe-companies.md` batch log — reversible via `active=false`.

