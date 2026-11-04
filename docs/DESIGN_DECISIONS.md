# JobQuest — Design Decisions & Engineering Tradeoffs

> **Purpose.** This is the engineering companion to the README: the full story behind the
> code, written so a reviewer or interviewer can understand not just *what* was built, but
> *why* — including the options that were rejected, the measurements that changed the
> design, the failures that shaped it, and the debt that remains.
>
> Last verified against the repo: **2026-11-04**, branch
> `feature/lifecycle-ingestion-access`, HEAD `e93a4f1`.
>
> Planning documents in `docs/` are historical records and sometimes describe earlier
> states. When this document and the code disagree, trust the code and
> [CODEBASE_MAP.md](CODEBASE_MAP.md).

---

## Contents

1. [How to read this document](#1-how-to-read-this-document)
2. [The product thesis](#2-the-product-thesis)
3. [Constraints and non-goals](#3-constraints-and-non-goals)
4. [System overview](#4-system-overview)
5. [Decision log](#5-decision-log)
   - [5.1 Runtime and architecture](#51-runtime-and-architecture)
   - [5.2 Source adapters](#52-source-adapters)
   - [5.3 Job model and deduplication](#53-job-model-and-deduplication)
   - [5.4 Ingestion pipeline](#54-ingestion-pipeline)
   - [5.5 Scheduling and concurrency](#55-scheduling-and-concurrency)
   - [5.6 Matching](#56-matching)
   - [5.7 Notifications](#57-notifications)
   - [5.8 Authentication and authorization](#58-authentication-and-authorization)
   - [5.9 Billing and entitlements](#59-billing-and-entitlements)
   - [5.10 Database and migrations](#510-database-and-migrations)
   - [5.11 Frontend](#511-frontend)
   - [5.12 Performance and egress](#512-performance-and-egress)
   - [5.13 Security, privacy, and compliance](#513-security-privacy-and-compliance)
   - [5.14 Deployment and observability](#514-deployment-and-observability)
   - [5.15 Testing and CI](#515-testing-and-ci)
6. [Tradeoff ledger](#6-tradeoff-ledger)
7. [Failure analyses and war stories](#7-failure-analyses-and-war-stories)
8. [Scaling to 10,000 users](#8-scaling-to-10000-users)
9. [Known limitations and debt](#9-known-limitations-and-debt)
10. [What I would do next](#10-what-i-would-do-next)
11. [Interview Q&A](#11-interview-qa)
12. [Numbers appendix](#12-numbers-appendix)
13. [Glossary](#13-glossary)

---

## 1. How to read this document

If you have five minutes:

- **The pitch:** JobQuest is a self-hostable job radar. It polls 2,519 company boards
  across 24 ATS adapters, deduplicates postings in Postgres, matches them deterministically
  against each user's preferences, and delivers alerts through Telegram.
- **The architecture:** a modular monolith — FastAPI + APScheduler + a Postgres queue + a
  Next.js frontend. No Kafka, no Redis, no microservices.
- **The thesis:** the hard part of job search is not ranking; it is **coverage, freshness,
  and noise reduction**. Get ingestion and deduplication right, and matching can stay
  simple and explainable.
- **The honesty:** the system is production-shaped but not fully production-hardened.
  Section 9 lists every known gap, including a live matcher parity bug.

If you are preparing for an interview, read Sections 2, 4, 5, 6, 7, and 11 first. The
remaining sections are reference material.

---

## 2. The product thesis

### 2.1 The problem

A job seeker has three bad options:

1. **Refresh career pages manually.** Accurate and early, but impossible to do at scale.
2. **Use job boards.** Convenient, but postings are syndicated late, duplicated, ranked for
   engagement, and often missing niche or early-career roles.
3. **Use alerts from a handful of companies.** Useful, but limited to companies you already
   know about.

The best moment to apply is usually the first few hours after a posting goes live: fewer
applicants, a fresher requisition, and a higher chance of a human reading the application.
Job boards optimize for inventory, not for that moment.

### 2.2 The bet

If you can poll a large number of company boards cheaply, normalize their postings, and
remove duplicates, then **simple deterministic filters become valuable**. The product does
not need an LLM to know that a "Backend Engineer" role in "Dubai" matching "python" and
"aws" is relevant. It needs to see it early, once, and in a channel the user checks.

### 2.3 Who it serves

| Segment | Need | How JobQuest serves it |
|---|---|---|
| Active job seeker | See new roles within minutes | Per-ATS polling, first-seen timestamps, immediate matching, delayed-but-fast alerts |
| Early-career candidate | Filter out senior/staff roles | Role, keyword, seniority, and excluded-role filters |
| Company-specific tracker | Follow a shortlist | One JSON line per company; no code changes |
| Privacy-conscious user | Avoid resume uploads and trackers | Self-hostable, no resume ingestion, self-hosted fonts, no session replay |
| Operator | Run it as a small paid product | Accounts, subscriptions, coupons, admin console, public browse |
| Engineer | Learn a real pipeline | Readable adapters, measured tradeoffs, offline fixtures |

### 2.4 Product principles

1. **Coverage beats ranking.** A missed posting cannot be ranked.
2. **Freshness beats volume.** A job seen 10 minutes ago is worth more than 10,000 stale rows.
3. **Explainability beats cleverness.** Every match shows why it matched.
4. **One ingest serves everyone.** Jobs are global; only matches and alerts are per-user.
5. **Boring infrastructure until proven otherwise.** Postgres is the queue, the lock, and
   the ledger.
6. **Adapters are replaceable.** The rest of the system should not care where a job came from.

---

## 3. Constraints and non-goals

### 3.1 Constraints

- **Solo developer, small budget.** Infrastructure must fit on one VPS or a free/cheap
  managed tier.
- **Politeness and legality.** Prefer official APIs; no CAPTCHA bypass, no authentication
  bypass, no aggressive scraping.
- **Unreliable sources.** Career pages change, rate-limit, return 403/429/500, and paginate
  inconsistently. Failure isolation is mandatory.
- **No dedicated data team.** The schema and matcher must be understandable by one person.
- **A real product surface.** Public pages, accounts, billing, admin, and legal pages are
  in scope, not just a scraper.
- **Windows development.** The dev environment must work on a Windows host with Docker
  bind mounts; this is why polling flags and a long Postgres start period exist in compose.

### 3.2 Non-goals (for now)

- LLM-based primary matching. AI is a later, optional enhancement.
- Resume parsing, candidate profiles, or recruiter workflows.
- Real-time streaming (Kafka, WebSockets for job flow).
- Multi-region, active-active, or horizontal sharding.
- A native mobile app. Telegram is the mobile notification surface.
- Full resume/application automation. The product links out to the employer.
- Email as a second live channel (see Section 9; the current pipeline is Telegram-only).

---

## 4. System overview

### 4.1 Runtime topology

```text
                       ┌──────────────────────────────┐
                       │        Next.js frontend      │
                       │  public + dashboard + admin   │
                       └──────────────┬───────────────┘
                                      │ REST, cookies
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          FastAPI application                                │
│                                                                             │
│  /api/public      /api/auth      /api        /api/admin      /health        │
│       │               │            │              │                         │
│       └───────────────┴────────────┴──────────────┘                         │
│                                      │                                      │
│  ┌──────────────┬────────────────────┼──────────────────┬────────────────┐  │
│  ▼              ▼                    ▼                  ▼                ▼  │
│ adapters     poller             matcher          notification queue   telegram│
│ (24)         APScheduler        (pure Python)    (Postgres)           bot    │
└───────┬───────────────────────────────────────────────────────────────┬─────┘
        │                                                               │
        ▼                                                               ▼
┌───────────────────────────────┐                     ┌─────────────────────────┐
│ PostgreSQL 15                 │                     │ Telegram Bot API        │
│ sources, jobs, matches,       │                     │ messages, commands,     │
│ queue, users, billing, runs   │                     │ inline, Mini App        │
└───────────────────────────────┘                     └─────────────────────────┘
        ▲
        │ HTTPS
┌───────┴──────────────────────────────────────────────────────────────────────┐
│ 2,519 company boards: Greenhouse, Lever, Ashby, Workday, Oracle, iCIMS,      │
│ SuccessFactors, Phenom, Avature, Workable, SmartRecruiters, BambooHR, ...    │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 One poll, end to end

```text
1. Scheduler fires poll-greenhouse (every hour by default, jitter ±120 s).
2. try_acquire_poll_lock('greenhouse') takes a Postgres advisory lock.
3. sync_sources() upserts sources.json into the sources table.
4. prune_old_jobs() applies retention and cleans old matches/ledger rows.
5. fetch_sources() selects active boards for the ATS.
6. Per-source work runs concurrently under an ATS-specific semaphore:
   a. adapter.fetch_jobs(board_identifier, shared_client)
   b. normalize → NormalizedJob → row
   c. filter stale postings by posted_at (MAX_POSTING_AGE_DAYS)
   d. dedupe within the batch
   e. upsert with ON CONFLICT (source_id, external_job_id)
   f. reactivate / touch / sweep lifecycle
   g. mark source healthy and record quiet_runs
7. New and reactivated job IDs are passed to match_and_enqueue().
8. The queue drain runs after the run, and on its own ~30 s schedule.
9. finish_poll_run() records counts, duration, per-source outcomes, and skips.
10. The advisory lock is released.
```

Three guards make this safe:

- **Advisory lock** — one poll per ATS at a time, across processes.
- **First-check suppression** — a board's first poll is backfill, not news.
- **Notification queue** — ingestion never talks to Telegram directly.

### 4.3 Scale snapshot

Measured at different points during development (these are historical measurements, not
current live counters):

| Metric | Value |
|---|---|
| Configured boards | 2,519 |
| Adapters | 24 |
| Largest ATS families | Workday 618, Greenhouse 513, Ashby 241, Workable 195, SmartRecruiters 171 |
| Jobs stored | ~515,000 in the September 2026 baseline |
| Poll runs | ~301 per 24 h in the September baseline; ~2.4 min average |
| Daily fetched rows | ~36.5 million over a 14-day window |
| Users at the time of the 10k plan | 4 |
| Database size | ~378 MB in the 10k plan; earlier 129 MB snapshot |

These numbers explain the design: at hundreds of thousands of jobs, full-table reads over
a network are expensive, and a naive per-user match table explodes. The architecture is
shaped by those two facts.

---

## 5. Decision log

Each decision follows the same shape:

- **Decision** — what was chosen.
- **Why** — the reasoning and evidence.
- **Alternatives rejected** — what else was considered.
- **Cost accepted** — the price of the choice.

---

### 5.1 Runtime and architecture

#### D1 — Modular monolith, not microservices

**Decision:** one FastAPI codebase, one Postgres database, one scheduler, one Telegram bot,
one frontend. Deploy as one web service, or split API and worker when polling load demands
it.

**Why:**
- The dominant workload is I/O-bound polling, not CPU-bound fan-out.
- One database gives strong consistency for deduplication, locks, and idempotency.
- A solo developer can operate it without a platform team.
- The boundaries are still real: adapters, matcher, queue, and web layer are separate
  modules with explicit interfaces.

**Alternatives rejected:**
- **Microservices per adapter.** Multiplies deploys, networking, and failure modes for no
  current benefit.
- **Kafka/Redis/Celery.** Adds infrastructure before there is a measured need. Postgres
  provides locking, queuing, and idempotency with constraints.
- **Kubernetes.** Operationally unjustified for one or a few processes.

**Cost accepted:** one process can starve another if work is not isolated. Mitigated by
`asyncio.to_thread`, async psycopg pools, a separate worker service in production, and
advisory locks.

#### D2 — FastAPI + Uvicorn

**Decision:** FastAPI for the REST API and OpenAPI docs; Uvicorn as the server.

**Why:**
- Async support for the poller, bot, and outbound HTTP.
- Pydantic request models and automatic `/docs`.
- Dependency injection fits `get_current_user` / `get_current_admin` cleanly.
- Familiar and small enough for a single developer.

**Alternatives rejected:** Django (ORM/admin overhead and sync-first), Flask (less typed
API support), Node/NestJS (would split the stack across two runtimes).

**Cost accepted:** no built-in admin, no ORM, no migration framework — all deliberately
replaced with explicit code and raw SQL.

#### D3 — Jobs are global; matches are per-user

**Decision:** one `jobs` table shared by all users. `job_matches`, `notification_queue`,
`notifications_sent`, and access state are per-user.

**Why:**
- A job posting is identical for every user. Duplicating it per user would multiply storage
  and ingestion cost by the user count.
- One poll serves every account; matching is a read of shared data against user filters.
- The 10k plan explicitly rejects per-user job copies.

**Alternatives rejected:** a per-user job table (storage explosion), a separate
recommendation index per user (complexity without current need).

**Cost accepted:** match computation is a fan-out over users per new job. Mitigated by
loading all eligible preferences once per run, matching per source, and pruning matches
after 24 hours.

#### D4 — Postgres as queue, lock, and ledger

**Decision:** use Postgres for `pg_try_advisory_lock`, `notification_queue`,
`notifications_sent`, and `rate_events`.

**Why:**
- Atomic constraints (`UNIQUE(user_id, job_id, channel)`) make idempotency structural.
- Advisory locks work across processes and release on disconnect.
- The queue volume is modest; it does not justify Redis or a broker.

**Alternatives rejected:** Redis/Celery/RQ (operational cost), in-memory queues (lost on
restart), Kafka (massive overkill).

**Cost accepted:** polling the queue every 30 seconds is less immediate than a push broker.
At the current and near-term scale, 30 seconds is well within the product's "minutes"
latency budget.

---

### 5.2 Source adapters

#### D5 — One adapter interface, one registry

**Decision:**

```python
class JobSourceAdapter(ABC):
    ats_type: str

    async def fetch_jobs(self, board_identifier: str, client=None) -> list[NormalizedJob]:
        ...

    async def fetch_job_detail(self, board_identifier: str, external_job_id: str):
        return None
```

Adapters are resolved by `adapter_for(ats_type)` in `backend/app/adapters/__init__.py`.
A shared retrying `httpx` client (`backend/app/http.py`) keeps connections alive across
boards.

**Why:**
- The pipeline depends only on `NormalizedJob`, never on an ATS SDK.
- Adding a source is a single file plus a registry branch, not a pipeline change.
- The optional `client` parameter lets one poll reuse TCP/TLS connections across hundreds
  of boards.
- `fetch_job_detail` is optional, so simple feeds stay simple.

**Alternatives rejected:**
- A plugin system with dynamic discovery (unnecessary complexity; the registry is explicit).
- A universal scraper (fragile and impossible to test per source).
- Per-adapter HTTP clients (connection churn).

**Cost accepted:** the registry is a long `if` chain. Readable, but it does not scale to
hundreds of adapters; a dict registry would be the next step if needed.

#### D6 — Official API > public JSON > server-rendered HTML > browser automation

**Decision:** follow the extraction ladder from `AGENTS.md`. Playwright is not used.

**Why:**
- APIs are faster, cheaper, and less brittle.
- HTML scraping increases egress, maintenance, and legal risk.
- The board-adapter analysis found that of 25 requested sources, only 3 were cleanly
  feasible; 18 required HTML scraping and were rejected.

**Alternatives rejected:**
- Playwright for JavaScript-heavy boards (heavy, slow, anti-bot conflict, high egress).
- Proxy rotation / anti-bot bypass (explicitly out of bounds).
- One scraper per HTML board (unmaintainable).

**Cost accepted:** some sources remain uncovered. The chosen tradeoff is fewer, reliable
sources over broad, brittle coverage.

#### D7 — Fixtures over live tests

**Decision:** every adapter has saved-response fixtures under
`backend/tests/fixtures/<ats>/`; the default test suite never calls a live career site.

**Why:**
- Live tests are flaky, slow, rate-limited, and occasionally blocked.
- Fixtures make parsing changes reviewable and deterministic.
- CI can run offline on every pull request.

**Alternatives rejected:** a live smoke test per adapter in CI (credentials, flakiness,
politeness), recorded VCR-style HTTP (heavier than plain fixtures).

**Cost accepted:** fixtures can go stale when a source changes shape. The mitigation is a
small number of opt-in live checks and production source-health monitoring.

#### D8 — Deactivate dead boards; never delete them by default

**Decision:** dead boards are set `active=false`, not deleted.

**Why:**
- `jobs` has `ON DELETE CASCADE`; deleting a source destroys its job history.
- Deactivation is reversible and preserves historical postings for debugging.
- `sync_sources()` respects `active=false` and does not resurrect the board.

**Alternatives rejected:** hard delete (irreversible, cascades), removing from
`sources.json` only (does not handle rows already in the DB).

**Cost accepted:** the `sources` table accumulates inactive rows and the UI must explain
them.

#### D8.1 — One source row per aggregator board

**Decision:** an aggregator (Remotive, We Work Remotely) is one `sources` row. The board
brand becomes `sources.company_name`; the per-job company is not promoted to a first-class
column.

**Why:**
- The ATS model is "one source = one company"; an aggregator is "one source = many
  companies" (Remotive can return ~500 jobs from ~400 companies in one call).
- Per-category rows would multiply sources and operator work. One row per board keeps the
  poll simple and the rollback trivial (`active=false`).
- The alternative — one row per company discovered inside an aggregator — would create
  hundreds of synthetic sources and pollute `/api/companies`.

**Alternatives rejected:** per-category rows (more control, more maintenance), per-company
rows (fake sources, broken company counts), separate schema/tables for aggregate feeds.

**Cost accepted:** company filtering on aggregate boards is weaker, and the UI must not
pretend the board name is always the employer. Freelance/gig boards were deferred entirely:
the matcher expects title/location semantics, while gigs carry budget, rate, and skills
semantics that would need a separate data model.

---

### 5.3 Job model and deduplication

#### D9 — Normalize into one shared model

**Decision:** adapters return `NormalizedJob` with a common set of fields; source-specific
data goes into metadata, not new columns.

**Why:**
- The rest of the system must not know whether a job came from Workday or Greenhouse.
- A shared model makes matching, deduplication, and API responses uniform.
- Source-specific columns would leak the source taxonomy into the core schema.

**Cost accepted:** some source-specific fields are lost or flattened. If a field becomes
product-critical (e.g., salary), it should be promoted deliberately.

#### D10 — Deduplicate on `(source_id, external_job_id)`

**Decision:** database-level `UNIQUE(source_id, external_job_id)`; a batch-level dedupe
handles provider pagination overlap before the upsert.

**Why:**
- Most ATSs expose a stable job ID.
- A unique constraint is stronger than an application check and survives concurrency.
- The fallback (company + title + location) is fuzzier and reserved for sources without
  stable IDs.

**Alternatives rejected:**
- Fuzzy title/location matching (false positives; explicitly postponed until deterministic
  methods are exhausted).
- URL-only dedupe (URLs change; some ATSs emit multiple URLs per job).
- Content hashing (descriptions are not stored and change frequently).

**Cost accepted:** a job reposted with a new external ID appears as a new row. The lifecycle
system handles the common inverse case (same ID disappears and returns).

#### D11 — Lifecycle tracking, not just upsert

**Decision:** `jobs.is_active` plus `last_seen_at`:
- reactivate rows that reappear,
- touch `last_seen_at` at most once per 24 h,
- deactivate rows unseen for 72 h,
- retain inactive rows for 7 days, then prune,
- keep active jobs up to the 30-day retention window.

**Why:**
- A job that disappears and returns is a signal (repost), not a duplicate.
- A simple "last seen" flag prevents stale jobs from matching forever.
- Reposts should alert again; unchanged rows should not.

**Alternatives rejected:** hard-delete missing jobs immediately (loses repost detection),
never deactivate (stale matches and alerts), mark inactive on a single miss (flaky polls
would produce false removals).

**Cost accepted:** lifecycle logic adds SQL and state. The 72-hour grace window is a product
judgment, not a mathematical certainty.

#### D12 — Do not store descriptions

**Decision:** `jobs.description` was dropped in migration 043. Detail endpoints return
`description: null`; matching is title/location based by product decision.

**Why:**
- Descriptions averaged ~21 bytes and were mostly empty; the largest outliers were
  expensive to move over the network.
- Keyword matching against descriptions produced noisy matches.
- Dropping the column reduced storage and egress significantly.
- The frontend already falls back when the field is null.

**Alternatives rejected:** storing full descriptions (egress and storage cost), fetching
descriptions on demand (extra HTTP per view, source-specific parsing, latency).

**Cost accepted:** users cannot read the full description in-app; they click through to the
employer. Keyword recall is narrower because matching is title-only.

#### D13 — First poll is backfill, never an alert

**Decision:** suppress notifications for a source's first successful poll.

**Why:**
- A newly added company can have hundreds or thousands of historical jobs.
- Alerting on all of them would flood users and train them to ignore alerts.
- The first poll establishes a baseline; only later postings are "new".

**Alternatives rejected:** alert on everything (bad UX), require a manual "mark baseline"
step (extra operator work), suppress by date (date fields are inconsistent across ATSs).

**Cost accepted:** if a genuinely new job appears between adding a source and its first
poll, it is silently treated as history. Acceptable for correctness of the alert stream.

---

### 5.4 Ingestion pipeline

#### D14 — Per-source isolation and per-source error recording

**Decision:** every source runs inside its own try/except. A failure marks the source with
an error, HTTP status, and error type; the run continues. Errors are never silently dropped.

**Why:**
- External sources fail routinely: 403, 429, 500, timeouts, malformed JSON, HTML changes.
- One broken Workday tenant must not block 500 healthy Greenhouse boards.
- Source health is a product feature: the Runs page and `/api/sources/unhealthy` expose it.

**Alternatives rejected:** fail-fast the whole run (unacceptable coverage loss), retry
forever (hangs the run), ignore errors (silent data loss).

**Cost accepted:** partial runs are normal. The run record must be read carefully; a
"completed" run can still contain per-source failures.

#### D15 — Retries with backoff at the HTTP layer

**Decision:** a shared retrying client with timeouts and backoff; 429 responses are honored.

**Why:**
- Transient network and rate-limit errors are common.
- Centralizing retries avoids duplicating logic in 24 adapters.
- A bounded retry budget prevents infinite loops.

**Alternatives rejected:** per-adapter retry logic (inconsistent), no retries (unnecessary
coverage loss), unbounded retries (run hangs).

**Cost accepted:** retries increase the tail latency of a poll. ATS-level concurrency and
quiet-board backoff keep the total run bounded.

#### D16 — Incremental detail fetching only when needed

**Decision:** list fetches are the default; `fetch_job_detail` is optional and only used by
adapters that need a second request for fields not present in the list response.

**Why:**
- Detail requests multiply egress and latency.
- Descriptions are not stored, so many detail calls would be wasted.
- Adapters that need details can still ask for them without changing the pipeline.

**Alternatives rejected:** fetch every detail for every job (2N requests, huge egress),
never fetch details (some sources would lose location/URL data).

**Cost accepted:** some adapters depend on detail calls and are slower; they are isolated
to the sources that need them.

#### D17 — Deduplicate within a batch before the upsert

**Decision:** `dedupe_rows()` removes duplicate `external_job_id`s inside one fetch result
before hitting the database.

**Why:**
- Some providers' pagination overlaps (notably Oracle Fusion), returning the same job twice.
- `ON CONFLICT` handles cross-run duplicates, but a single `INSERT ... ON CONFLICT` batch
  cannot update the same row twice in one statement.
- Fixing it in memory is cheap and keeps the SQL simple.

**Alternatives rejected:** rely on `ON CONFLICT` alone (Postgres error: cannot affect row a
second time), de-duplicate in SQL with a CTE (more complex, slower).

**Cost accepted:** a small in-memory set per source batch.

---

### 5.5 Scheduling and concurrency

#### D18 — One interval trigger per ATS, not one global poll

**Decision:** APScheduler registers `poll-<ats>` per ATS family, default 3600 s with ±120 s
jitter, plus a 12-hour global integrity sweep.

**Why:**
- ATSs have different costs and freshness expectations. Workday is heavy; Greenhouse is
  light.
- A slow ATS must not delay others.
- Jitter prevents synchronized thundering herds.
- Live interval changes are persisted in `poll_schedule` and reschedule the job.

**Alternatives rejected:** one global poll (head-of-line blocking), external cron per ATS
(more moving parts), fixed identical intervals (ignores per-source cost).

**Cost accepted:** many scheduler jobs and more moving parts. The dashboard exposes the
schedule and next-run times to make it observable.

#### D19 — Advisory locks as the distributed mutex

**Decision:** `pg_try_advisory_lock('poll-{ats}')` (and a global lock for full sweeps).

**Why:**
- Works across the API process, the worker, and a manual `run_poll.py`.
- Releases automatically when a connection closes.
- A second scheduler is harmless: it skips the tick.
- `poll_runs` is history, not the mutex; a crashed run cannot deadlock the system.

**Alternatives rejected:** a `running` row as the lock (stale rows after a crash), Redis
locks (new infrastructure), no lock (overlapping runs and duplicate work).

**Cost accepted:** advisory locks are Postgres-specific and require care with connection
pooling. The lock is acquired on a dedicated connection and released in `finally`.

#### D20 — Worker split in production

**Decision:** production compose runs the API with `JOBQUEST_DISABLE_SCHEDULER=1` and
`JOBQUEST_DISABLE_BOT=1`, and runs a separate `python -m app.worker`.

**Why:**
- A Workday sweep can take ~9 minutes.
- If it runs in the API process, it competes for the event loop and can delay `/health`,
  manual runs, and dashboard requests.
- The worker owns the scheduler and bot; the API owns HTTP.

**Alternatives rejected:** one process (simpler but head-of-line blocking), Celery workers
(new broker and deployment), per-ATS external cron (configuration sprawl).

**Cost accepted:** two processes to deploy and monitor. The advisory locks make a second
scheduler safe if both are accidentally enabled.

#### D21 — Quiet-board backoff

**Decision:** after 5 consecutive polls with zero new jobs, a healthy board is polled every
third interval on scheduled runs. Its quiet-run counter resets on the first check or any
new job. Manual and global runs always poll everything.

**Why:**
- Many boards are healthy but rarely change; polling them every hour is wasted egress.
- Measurement showed ~26% of boards could be skipped per run, with discovery delay bounded
  to about 3 hours.
- Correctness is preserved: a global sweep still covers everything.

**Alternatives rejected:** permanent per-source intervals (manual tuning burden), stop
polling quiet boards (miss postings), no backoff (wasted egress).

**Cost accepted:** a quiet board can take up to ~3 hours to surface a new job. This is
explicitly a product tradeoff, not a bug.

#### D22 — Do not use date-based or ID-based early termination

**Decision:** paginate the full result set even when pages look old or all IDs are known.

**Why:**
- Measurement killed both shortcuts:
  - SuccessFactors page 1 contained a **February 2025** posting among **April 2026** ones.
  - Workday exposes only coarse relative dates ("Posted 3 Days Ago").
- A shadow run showed that ID-based early termination hid **18** new Workday jobs and
  **67** new Avature jobs behind pages full of known IDs.
- Page-size increases were blocked by providers: Workday rejects `limit > 20`,
  SuccessFactors ignores `pageSize` at 10/page, Avature caps at 6 rows.

**Alternatives rejected:** date cutoff, all-known-ID cutoff, larger pages.

**Cost accepted:** more requests and latency. Mitigated with 10-way concurrency for heavy
ATSs, quiet-board backoff, and connection reuse.

---

### 5.6 Matching

#### D23 — Deterministic matching, no LLM

**Decision:** match on roles, keywords, locations, seniority, excluded companies, and
excluded roles. No model call is on the critical path.

**Why:**
- Explainability: every match has `matched_on` reasons and a simple score.
- Testability: pure functions and SQL parity can be unit-tested offline.
- Cost: matching runs on every new job for every user; an LLM would be slow and expensive.
- The product's value is discovery and noise reduction, not semantic ranking.

**Alternatives rejected:** embeddings/vector search (infra, opacity, cold start), LLM
classification (cost, latency, non-determinism), fuzzy string matching (false positives).

**Cost accepted:** limited semantic understanding. "SDE" will not match "Software
Development Engineer" unless the user adds both. This is an acceptable phase-one tradeoff;
AI is explicitly a later enhancement.

#### D24 — Whole-word/phrase matching, not substring

**Decision:** compile a boundary-aware regex per term (`term_matches_text`); SQL has a
matching `term_matches()` function.

**Why:**
- Substring matching produced embarrassing false positives: `ai` matched "said" and
  "maintenance"; `go` matched "ongoing".
- Whole-word matching with phrase support handles `AI/ML`, `C++`, and `full stack`.
- It is deterministic and cheap to test.

**Example:**

| Term | Text | Match |
|---|---|---|
| `ai` | `AI Engineer` | yes |
| `ai` | `AI/ML` | yes |
| `ai` | `said` | no |
| `ai` | `maintenance` | no |
| `full stack` | `Full-Stack Engineer` | yes |

**Alternatives rejected:** plain substring (false positives), tokenization + stemming
(language-specific, more complexity), regex from user input (ReDoS risk; terms are escaped).

**Cost accepted:** some legitimate morphological variants do not match. Users can add
variants; precision is preferred over recall for alerts.

#### D25 — Score = share of active categories hit

**Decision:** the score is `hits / active_categories * 100`; no active categories means
100. Exclusions disqualify a job but do not reduce the score.

**Why:**
- A simple, explainable number is more useful than a proprietary relevance rank.
- Users can reason about why a job scored 75.
- It avoids weighting debates that cannot be validated without click data.

**Alternatives rejected:** weighted scores per category (arbitrary weights), ML ranking
(no training data), percentage of terms matched (penalizes broad preferences).

**Cost accepted:** the score is coarse. A role-and-location match scores the same as a
keyword-and-seniority match.

#### D26 — Hard filters vs soft signals

**Decision:**
- **Hard:** excluded companies, excluded roles, and location when locations are set.
- **Soft:** roles, keywords, and seniority are OR'd together within the job's matching
  evaluation.

**Why:**
- A user who sets a location does not want jobs elsewhere; location must filter, not score.
- A user who lists five roles does not want only jobs matching all five; OR semantics
  reflect intent better.
- Excluded companies/roles are explicit negatives and must always win.

**Alternatives rejected:** everything as a score (irrelevant jobs leak through), AND across
all categories (too few matches).

**Cost accepted:** a job can match a keyword while missing the user's preferred role. The
`matched_on` reasons make this visible.

#### D27 — Geo normalization

**Decision:** normalize locations through a geo index with country aliases and a remote
flag. Preferences store structured locations (raw text, codes, remote).

**Why:**
- Job locations are free text: "Dubai, UAE", "United Arab Emirates", "Remote - EMEA".
- Users think in countries/cities, not exact strings.
- Country codes make cross-source matching stable.

**Alternatives rejected:** exact string match (misses aliases), geocoding API per job
(latency, cost, rate limits), LLM extraction (overkill).

**Cost accepted:** the alias table needs maintenance. Ambiguous locations (e.g., "Georgia")
remain imperfect.

#### D28 — Per-source matching during the poll

**Decision:** match each source's newly upserted jobs immediately after that source is
processed, not after all sources finish.

**Why:**
- The original design waited for `asyncio.gather()` over every source, then matched.
- One slow board therefore delayed every user's alerts by the tail latency of the slowest
  source.
- Moving matching inside the per-source flow makes job → match latency bounded by that
  source's fetch time.

**Alternatives rejected:** a separate match queue with `FOR UPDATE SKIP LOCKED` (deferred
until profiling shows a need; estimated threshold ~1k users × ~2k jobs/run), end-of-run
batch matching (tail latency).

**Cost accepted:** preference loading must be hoisted once per run, and matching code runs
inside the poll's concurrency context. The queue still decouples delivery.

#### D29 — Match retention of 24 hours

**Decision:** `job_matches` is pruned daily; only matches for jobs first seen in the last
24 hours are rebuilt on preference save.

**Why:**
- At 10k users × 500k jobs, an unbounded match table reaches **5 billion rows**.
- The product only needs recent matches for alerts; older jobs remain searchable in `jobs`.
- The notification ledger outlives match pruning, so re-matching cannot cause re-alerts.

**Alternatives rejected:** keep all matches forever (storage explosion), partition by user
(premature complexity), compute matches on read (slow dashboard).

**Cost accepted:** older matches are not available in the matches view. The jobs feed still
contains the postings.

#### D30 — Grouped matching by preference signature

**Decision:** evaluate each distinct preference signature once, then apply the result to
all users sharing it.

**Why:**
- Many users have identical or near-identical preferences (especially default presets).
- Measurement: **150 users × 200 jobs** dropped from **30,000 evaluations** to **1,000**,
  and runtime from **1.335 s** to **0.018 s**.
- It is a pure in-memory optimization; semantics are unchanged.

**Alternatives rejected:** per-user loops (wasted CPU), caching match results by job only
(would require per-user keys anyway).

**Cost accepted:** signatures must be canonicalized carefully (list order, case, empty
values). A mistake could apply one user's recommendations to another, so this is tested.

#### D31 — SQL/Python parity for preference saves

**Decision:** preference saves call a Postgres `recompute_job_matches()` function so the
dashboard is immediately consistent without waiting for a poll.

**Why:**
- Users expect a saved preference to update their matches immediately.
- Doing it in SQL avoids shipping the candidate set to Python.
- Migration 064 added `term_matches()` to mirror Python's whole-word semantics.

**Alternatives rejected:** recompute only on the next poll (stale UI), recompute in Python
(loads jobs into the API), trigger-only recompute (harder to reason about).

**Cost accepted:** two implementations must stay in sync. This is a real maintenance risk
and a **known current bug**: historical `recompute_job_matches` overloads coexist, and the
signature called by `matcher.py` can resolve to the older substring-based version instead
of the whole-word version. See Section 9.

---

### 5.7 Notifications

#### D32 — Queue intents; deliver asynchronously

**Decision:** ingestion writes `notification_queue` rows with `scheduled_for`; a drain
worker sends due rows. Ingestion never sends messages directly.

**Why:**
- Decouples the poll's latency from Telegram's rate limits.
- Makes retries, delays, and idempotency possible.
- A failed send cannot fail ingestion.
- The queue is inspectable in Postgres.

**Alternatives rejected:** send inline during ingestion (head-of-line blocking, no retry
control), a separate message broker (new infrastructure).

**Cost accepted:** delivery is delayed by up to the drain interval (~30 s) plus the user's
alert delay.

#### D33 — Idempotency at the database layer

**Decision:** `UNIQUE(user_id, job_id, channel)` on both the queue and the sent ledger.
Queue inserts use `ON CONFLICT ... DO NOTHING`; sends check the ledger.

**Why:**
- Re-running a poll, a drain, or a match must not double-alert.
- A constraint is stronger than a read-then-write check under concurrency.
- The ledger also supports debugging ("was I sent this?").

**Alternatives rejected:** application-only checks (race conditions), an in-memory sent set
(lost on restart), exactly-once delivery (not achievable with an external API).

**Cost accepted:** delivery is at-least-once. A crash after Telegram accepts a message but
before the ledger commit can produce a duplicate. The window is small and the ledger
prevents the common cases.

#### D34 — Retry then fail permanently

**Decision:** up to 3 attempts; then `failed` with `last_error`.

**Why:**
- Transient Telegram/network errors should recover.
- Infinite retries would poison the queue and hide systemic problems.
- 3 attempts is enough for transient failures without unbounded work.

**Alternatives rejected:** unlimited retries (stuck queue), zero retries (lost alerts).

**Cost accepted:** a persistent Telegram outage can move alerts to `failed`; they are not
automatically replayed later. This is visible in the queue and is a candidate for better
dead-letter handling.

#### D35 — Per-user delay, not per-tier only

**Decision:** each user has `alert_delay_minutes`; `scheduled_for = now + delay`. Tier
defaults live in `app_settings` (privileged/normal default 10 minutes in code).

**Why:**
- Gives users control over alert timing.
- Spreads notification load instead of a thundering herd at poll completion.
- Replaces the earlier rigid tier-only model.

**Alternatives rejected:** immediate sends for everyone (load spikes, notification fatigue),
fixed tiers only (no user control).

**Cost accepted:** changing a delay affects only future intents; already-queued sends keep
their original schedule. This is predictable but can surprise users.

#### D36 — Telegram-only delivery (email is legacy)

**Decision:** the live pipeline enqueues Telegram only. Email code (Resend) exists but is
not part of the active path; email queue rows are canceled at drain.

**Why:**
- The product's mobile-first surface is Telegram, which needs no domain or email
  infrastructure.
- Email deliverability, unsubscribe compliance, SPF/DKIM/DMARC, bounce handling, and
  anti-spam law are a project of their own.
- A half-working email channel is worse than a reliable single channel.

**Alternatives rejected:** ship email early (deliverability and compliance risk), delete the
code entirely (loses groundwork for a future channel).

**Cost accepted:** no email fallback for users who do not use Telegram. The documentation
must be explicit about this; the README and `.env.example` still contain email history and
should be cleaned up.

#### D37 — Telegram pacing

**Decision:** a global token bucket at ~25 messages/sec sustained with burst 30, plus a
0–200 ms jitter. Honor `retry_after` on 429.

**Why:**
- Telegram enforces roughly 30 messages/sec per bot.
- Bursting thousands of alerts at once would trigger 429s and permanent failures after 3
  attempts.
- The 10k plan predicted 1,000–2,000 sends in a single drain tick for a hot posting.

**Alternatives rejected:** unbounded sends (429 flood), one message per job (more messages
than necessary), a separate Telegram worker (premature until multiple app replicas).

**Cost accepted:** a large drain can take minutes. The queue is durable, so slowness is
preferable to loss.

---

### 5.8 Authentication and authorization

#### D38 — Signed session cookies, not server-side sessions

**Decision:** HMAC-SHA256 signed, httpOnly cookies (`jobquest_session`; `__Host-` prefix in
secure mode), default TTL 7 days (168 h).

**Why:**
- Stateless verification avoids a DB lookup on every request.
- httpOnly protects against JavaScript token theft.
- `SameSite`/`Secure` settings work with the frontend's `credentials: include`.
- The design is replaceable by a hosted auth provider later.

**Alternatives rejected:** JWT in localStorage (XSS exposure), server-side session table
(extra query), Supabase Auth (would couple the product to one provider).

**Cost accepted:** revocation requires rotating `SECRET_KEY` or short TTLs; there is no
per-session revocation list. For a small product, this is acceptable.

#### D39 — PBKDF2-SHA256 with 600,000 iterations

**Decision:** stdlib `hashlib.pbkdf2_hmac`, per-password salt, `hmac.compare_digest` for
verification, and rehash on login when iterations are below current policy.

**Why:**
- OWASP 2023 guidance for PBKDF2-HMAC-SHA256 is 600k iterations.
- No new dependency (passlib/argon2 add supply-chain surface).
- The hash format includes the scheme and iteration count, enabling upgrades.

**Alternatives rejected:** bcrypt/argon2 (better memory hardness, but a dependency and
native build), plain SHA-256 (unsafe), MD5 (never).

**Cost accepted:** ~0.5 s of CPU per login. At current scale, that is a feature (brute-force
cost) rather than a bottleneck.

#### D40 — Layered authorization: role + capabilities

**Decision:**
- `role`: `user`, `privileged`, `admin`.
- `capabilities`: explicit overrides (e.g., `telegram_alerts`, `email_alerts`, `dashboard`,
  `preferences`, `admin`).
- Effective permissions = explicit capabilities if non-empty, otherwise role defaults.
- Subscription gate: plain `user` needs an active subscription; privileged/admin bypass.

**Why:**
- "Promote this person" and "revoke one feature" are different operations.
- Capabilities allow fine-grained support without inventing roles for every combination.
- Centralizing the logic in `entitlements.py` avoids scattered checks.

**Alternatives rejected:** roles only (inflexible), per-endpoint ad-hoc checks (inconsistent
and easy to miss), RLS-only (the app uses a service-role key).

**Cost accepted:** two concepts to reason about. The merge rule (`capabilities` override
role defaults) must be documented and tested.

#### D41 — DB-backed rate limiting and lockout

**Decision:** `rate_events` table for shared limits, with an in-memory fallback for tests;
login lockout after repeated failures.

**Why:**
- Per-process dictionaries do not work across API replicas.
- Registration, login, coupon redemption, and other abuse-sensitive paths need shared
  counters.
- The database is already a dependency; no Redis needed.

**Alternatives rejected:** in-memory only (resets on restart, per-replica), Redis (new
infra), no rate limiting (abuse).

**Cost accepted:** a DB write per rate-limited action. Indexed and pruned after 24 hours.

#### D42 — Password login now, Telegram linking alongside

**Decision:** email + password registration/login; Telegram identity is linked separately.
Early OTP tables were dropped in migration 048.

**Why:**
- Passwords are familiar and do not depend on email deliverability.
- Telegram login is valuable for Mini App users but should not be the only path.
- The OTP flow added friction and delivery dependencies; the product pivoted to passwords.

**Alternatives rejected:** OTP-only (email deliverability, friction), Telegram-only (excludes
non-Telegram users), magic links (email dependency).

**Cost accepted:** password reset is not implemented as a route; the login page points
users to support/unlock. This is a known gap.

---

### 5.9 Billing and entitlements

#### D43 — Provider-neutral billing, manual first

**Decision:** `BILLING_PROVIDER` switches between `manual` (default) and `razorpay`;
the schema records provider events generically. Registration alone never grants access:
a plain account must subscribe, redeem a coupon, or receive an admin grant.

**Why:**
- Shipping access control before payment integration is better than blocking the product
  on a payment provider decision.
- Requiring an explicit grant doubles as a spam brake and replaces an approval queue.
- Coupons and manual grants are enough to onboard early users.
- Coupons and manual grants are enough to onboard early users.
- Razorpay is the right first provider for India (UPI, local cards, ~2–3% fees).

**Alternatives rejected:** Stripe (payout friction in India, tax complexity), Paddle/Lemon
Squeezy (merchant-of-record fees ~5%), waiting for the perfect provider.

**Cost accepted:** manual operations do not scale; the Razorpay path must be hardened
before charging strangers at volume.

#### D44 — Single-use, short-lived coupons

**Decision:** admin-generated coupons `JR-XXXX-XXXX`, single-use, expire 12 hours after
creation, atomic claim with a conditional `UPDATE ... WHERE claimed_by IS NULL`.

**Why:**
- Coupons support invite-only onboarding and support cases without a payment provider.
- A short TTL limits sharing and brute force.
- The atomic update makes double redemption structurally impossible.

**Alternatives rejected:** reusable codes (fraud), long-lived codes (leak risk), application
level checks (race conditions).

**Cost accepted:** users must redeem promptly; support may need to mint a new code.

#### D45 — Entitlement resolution in one service

**Decision:** `effective = explicit capabilities when non-empty, otherwise role defaults`,
gated by `subscription_active` for plain users. Privileged/admin are exempt.

**Why:**
- One place to answer "can this user access this?"
- Easy to test and reason about.
- Supports comps, coupons, and manual grants.

**Alternatives rejected:** scattered checks (drift), subscription-only (no admin comps),
role-only (no fine-grained revocation).

**Cost accepted:** cached entitlements can be briefly stale; the cache TTL must be short.

Two related rules prevent data damage:
- Plan limits are validated at preference **write** time; stored preference rows are never
  mutated to fit a plan.
- Applying a preset writes through the normal preference-save path; presets are copies, so
  the "Admin Preference" source row is never overwritten.

**Cost accepted:** validation must stay in sync with every plan definition, and an existing
preference row can exceed a new plan's limits until the user edits it.

---

### 5.10 Database and migrations

#### D46 — Raw SQL migrations, not an ORM

**Decision:** numbered `.sql` files in `backend/migrations/`, tracked in
`schema_migrations`, applied automatically at startup. No Alembic, no ORM.

**Why:**
- The schema uses Postgres-specific features: partial indexes, `pg_try_advisory_lock`,
  `ON CONFLICT`, JSONB, arrays, check constraints, and SQL functions.
- Raw SQL is reviewable and portable to psql.
- Automatic application removes a deployment step.
- The runner retries the initial connection for up to 300 s during WAL recovery.

**Alternatives rejected:** SQLAlchemy + Alembic (abstraction overhead for a Postgres-only
product), Supabase migrations only (vendor lock-in), manual `psql` (human error).

**Cost accepted:** no autogeneration, no rollback framework. Migrations must be written
carefully and tested against a real Postgres.

#### D47 — Dual database access: psycopg for SQL, PostgREST for CRUD

**Decision:**
- `psycopg 3` sync pool for API SQL reads and a loop-keyed async pool for the poller.
- `supabase-py`/PostgREST for simple table reads/writes.

**Why:**
- SQL is the right tool for joins, `ON CONFLICT`, advisory locks, and bulk operations.
- PostgREST/supabase-py made early CRUD fast to write and works with hosted Supabase.
- Keeping both avoids a rewrite while allowing the hot paths to move to SQL.

**Alternatives rejected:** PostgREST-only (poor fit for complex queries and locks),
psycopg-only (a larger rewrite of working CRUD code).

**Cost accepted:** two access paths and two mental models. The hot path (ingestion) is
mostly SQL; the REST path remains for simple table operations.

#### D48 — Constraints over application checks

**Decision:** uniqueness and idempotency live in the database:
- `UNIQUE(source_id, external_job_id)` on jobs,
- primary key `(user_id, job_id)` on matches,
- `UNIQUE(user_id, job_id, channel)` on queue and ledger.

**Why:**
- Concurrency-safe.
- Survives code bugs.
- Makes duplicate prevention a schema property, not a convention.

**Alternatives rejected:** application-only checks (races), soft uniqueness via queries
(slow and fallible).

**Cost accepted:** constraint violations must be handled gracefully (upsert/ignore).

#### D49 — Retention as a first-class design concern

**Decision:** prune aggressively and deliberately:
- jobs by `first_seen_at`: 30 days,
- inactive jobs: 7 days,
- matches: 24 hours,
- sent ledger: 24 hours,
- auth events: 90 days,
- rate events: 24 hours.

**Why:**
- Unbounded `job_matches` at 10k users × 500k jobs would reach 5 billion rows.
- The product needs recent alerts, not a permanent archive.
- Pruning the sent ledger after the idempotency window keeps "why didn't I get this
  alert?" debuggable while bounding growth.

**Alternatives rejected:** keep everything (cost), partition tables (operational
complexity), prune jobs to 7 days (too little searchable history).

**Cost accepted:** old matches disappear from the dashboard. Jobs remain until retention
expires.

---

### 5.11 Frontend

#### D50 — Next.js App Router, no extra data library

**Decision:** Next 15.1.6, React 19, TypeScript 5.7, Tailwind 3.4. All server calls go
through `lib/api.ts`; pages use `useState`/`useEffect`; auth is the only global context.

**Why:**
- The app is mostly CRUD screens with simple local state.
- React Query/SWR/Redux would add concepts without a current need.
- A single API client centralizes `credentials: "include"`, error handling, and base URL.

**Alternatives rejected:** Next server components for authenticated data (session cookies
and client gates made this awkward), React Query (cache invalidation complexity), Redux
(overkill).

**Cost accepted:** repeated loading/error boilerplate and no shared cache. The dashboard's
`useOverviewData` does a `Promise.all`; some pages refetch on mount.

#### D51 — Client gates are UX, not security

**Decision:** `AuthGate`, `PaywallGate`, and `AdminGuard` run in the browser. There is no
Next.js middleware. The backend enforces every protected route.

**Why:**
- The API is the trust boundary; duplicating authorization in middleware would drift.
- Client gates prevent confusing navigation and improve UX.
- The backend already has `get_current_user`, `get_current_admin`, and entitlement checks.

**Alternatives rejected:** middleware-only protection (false sense of security; API still
needs checks), server-side route protection (would require a session-aware Next backend and
duplicate logic).

**Cost accepted:** a determined user can load a dashboard shell, but API calls fail. This
is the correct security model, but it must be stated clearly to avoid misunderstanding.

#### D52 — localStorage for saved/hidden/applied jobs

**Decision:** store job IDs in `jobquest:saved-jobs:v1`, `jobquest:hidden-jobs:v1`, and
`jobquest:applied-jobs:v1`, capped at 500 entries.

**Why:**
- These are personal UI preferences, not shared business data.
- They work for anonymous public browsers.
- No account or API round-trip is needed for a bookmark.

**Alternatives rejected:** database persistence (adds user rows for lightweight actions),
cookies (size limits), IndexedDB (overkill).

**Cost accepted:** state is per-browser, lost on cache clear, and not synced across devices.

#### D53 — Two visual systems, deliberately scoped

**Decision:** browse and editorial pages use a "Warm Editorial" system; the dashboard,
pricing, legal shell, and admin surfaces use a dark "Ink" glass system. Auth pages have
their own green split layout; the landing page has a separate navy/blue design.

**Why:**
- The public site should feel editorial and approachable; the dashboard should feel like a
  dense instrument panel.
- Scoping styles prevents the two systems from fighting.
- The design direction was tested through a 15-way exploration before adoption.

**Alternatives rejected:** one global system (harder to optimize both marketing and data
density), a third-party component kit (would flatten the identity).

**Cost accepted:** real inconsistency. Tokens are not applied globally; `html/body` are
hardcoded dark, and several routes override backgrounds. This is listed as debt, not a
feature.

#### D54 — Self-hosted fonts and legal guards

**Decision:** Fraunces, Inter, IBM Plex Mono, and JetBrains Mono via `next/font` (self-hosted
at build time). A frontend test bans CDN font links and session-replay/keystroke trackers.

**Why:**
- Avoid leaking visitor IPs to Google Fonts.
- Avoid third-party scripts that capture sensitive form input.
- Make privacy a testable property, not a promise.

**Alternatives rejected:** Google Fonts CDN (privacy), no test (guards rot), system fonts
(less identity).

**Cost accepted:** larger build output and a test that must be maintained. Company logos
still use Google's favicon service, a known third-party request.

---

### 5.12 Performance and egress

#### D55 — Keep the event loop free

**Decision:** wrap heavy synchronous pipeline work in `asyncio.to_thread`; use a loop-keyed
async psycopg pool.

**Why:**
- The original poller called synchronous Supabase REST inside `async def`.
- That held the FastAPI event loop for the entire run, stalling the Telegram bot and API.
- `to_thread` isolates the blocking work; async SQL removes the worst fan-out.

**Alternatives rejected:** leave it synchronous (API freezes), move everything to a separate
process immediately (the worker split came later), rewrite all adapters async (they already
were).

**Cost accepted:** thread-pool complexity and a loop-keyed pool lifecycle. The pool must be
discarded if bound to a dead event loop.

#### D56 — Collapse REST fan-out into SQL

**Decision:**
- `fetch_existing_job_ids` is one `SELECT external_job_id ... WHERE source_id = %s`.
- Notification/match lookups are scoped to candidate IDs.
- Candidate jobs are fetched once and shared by senders.

**Why:**
- A 20k-job source previously made 20 sequential REST round-trips just to check existing IDs.
- At 100k sent rows, an unbounded REST fetch ran on every poll.
- PostgREST JSON is ~1.3× larger than Postgres binary and counts as Supabase egress.

**Alternatives rejected:** paginate REST more aggressively (still N round-trips), keep
unbounded reads (growing cost), move everything to SQL at once (rewrite risk).

**Cost accepted:** two query paths and some duplication between PostgreSQL and PostgREST
calls.

#### D57 — Projections, LIMITs, and GZip

**Decision:** select only needed columns; cap public results; drain the queue with
`status='pending' AND scheduled_for <= now() LIMIT 400`; compress large responses.

**Why:**
- `SELECT *` was a major egress contributor.
- The queue scan was reading more than it needed.
- `poll_runs.sources` JSONB averaged ~2.4 kB and could reach 37 kB; compression and
  summarization cut egress ~60%.

**Alternatives rejected:** cache everything in Redis (new infra), reduce job coverage
(product damage), store less history (debugging loss).

**Cost accepted:** more explicit SQL and a summarized run payload that may lose per-source
detail for very large runs.

#### D58 — Poll less only where it is safe

**Decision:** quiet-board backoff; no date/ID early termination; per-ATS intervals.

**Why:** correctness measurements (see D22) showed that early termination loses jobs.
Backoff is safe because global sweeps still cover everything.

**Alternatives rejected:** date cutoff (misses old-but-new postings), ID cutoff (hides jobs
behind known pages), lower coverage (product damage).

**Cost accepted:** quiet boards surface new jobs with up to ~3 hours of delay.

#### D59 — The Supabase egress turnaround

**Decision:** measure first, then apply reversible phases: config, scoped queries, SQL
upserts, poll tuning, caching, projections, retention, provider quiet mode, monitoring.

**Why:**
- Egress reached **7.35 GB over 14 days (~538 MB/day)** against a 5 GB/month free tier.
- The root cause was not images or the frontend; it was the backend repeatedly reading
  `jobs` over the internet (the frontend never talks to Supabase directly).
- The plan targeted **<500 MB/month** without changing API contracts or coverage.

**Alternatives rejected:** migrate off Supabase immediately (premature), reduce features
(product damage), add Redis (not the bottleneck).

**Cost accepted:** multiple phases and two access paths. The long-term architecture choice
(co-locate compute, self-host Postgres, or hybrid) is deliberately deferred.

---

### 5.13 Security, privacy, and compliance

#### D60 — Service-role key stays server-side

**Decision:** the Supabase service-role key and `DATABASE_URL` are backend-only environment
variables. The frontend only calls FastAPI.

**Why:**
- The service-role key bypasses RLS; leaking it compromises the whole database.
- The frontend bundle is public; any key in it is effectively public.
- Keeping all business logic server-side also prevents bypassing entitlements.

**Alternatives rejected:** direct Supabase access from the browser (RLS complexity and
leak risk), anon key for all operations (RLS work not yet done).

**Cost accepted:** every read goes through the API. That is the intended architecture.

#### D61 — No RLS, explicit server-side authorization

**Decision:** authorization is enforced in FastAPI/SQL; Postgres RLS is not enabled.

**Why:**
- The app uses a service-role connection; RLS would not apply without re-architecting
  access.
- All authorization is centralized and testable in one place.
- RLS is a later option if multi-tenant direct database access is introduced.

**Alternatives rejected:** add RLS now (large policy surface, no current benefit), allow
client SQL (unacceptable).

**Cost accepted:** a missing dependency check is a real vulnerability; the code review and
tests must cover route protection. The `JOBQUEST_REQUIRE_AUTH=false` compatibility mode is
dangerous if exposed.

#### D62 — Age gate and legal pages

**Decision:** registration requires an 18+ date of birth; legal pages exist for terms,
privacy, refunds, DMCA, and contact.

**Why:**
- Consent and age requirements matter for a public product.
- Payment providers and app stores expect these pages.
- The privacy page is explicit that no registered entity exists yet.

**Alternatives rejected:** launch without legal pages (compliance risk), collect full KYC
(overkill for a ₹49 subscription).

**Cost accepted:** placeholders remain for entity name, address, contact, and grievance
officer. These must be filled before a real commercial launch.

#### D63 — Privacy by default

**Decision:** no resume upload, no third-party analytics, self-hosted fonts, no session
replay, minimal public data, and explicit account export/delete.

**Why:**
- Job search data is sensitive.
- The product does not need behavioral tracking to work.
- A small data footprint reduces breach impact.

**Alternatives rejected:** add analytics (not needed), session replay (banned by a test),
third-party auth (data sharing).

**Cost accepted:** less product analytics. The tradeoff is intentional.

---

### 5.14 Deployment and observability

#### D64 — Docker Compose for dev, split services for prod

**Decision:** `docker-compose.yml` runs Postgres, PostgREST, API with reload, and the
frontend dev server. `docker-compose.prod.yml` runs a built API and a separate worker.

**Why:**
- Local parity with production.
- Bind-mounted hot reload for development; immutable images for production.
- Worker isolation protects the API from long polls.

**Alternatives rejected:** a single all-in-one image (harder to scale roles), Kubernetes
(premature), local-only Postgres (no cloud deployment path).

**Cost accepted:** Compose-specific quirks: Windows polling flags, anonymous volumes for
`node_modules`, and a 300 s Postgres start period.

#### D65 — Render as the single-service blueprint

**Decision:** `render.yaml` deploys the backend as one Docker web service with the scheduler
and bot in-process.

**Why:**
- Simple and cheap for an early product.
- The advisory locks make this safe.
- The worker split is available for heavier deployments via Compose.

**Alternatives rejected:** separate Render worker service (more cost and configuration),
external cron (more moving parts).

**Cost accepted:** a long poll can compete with API requests on the single service. The
worker split is the upgrade path.

#### D66 — Stall detection, source health, no full observability stack

**Decision:** record `poll_runs`, per-source health, and durations; run a stall watcher
every 10 minutes and page the owner through Telegram after 70 minutes without a completed
poll.

**Why:**
- The most important failure is "the poller silently stopped".
- The database already holds the timing truth.
- Sentry/Prometheus/Grafana were deliberately deferred.

**Alternatives rejected:** add a full observability stack early (cost, setup, noise), rely
on logs alone (silent failure).

**Cost accepted:** no error tracker, no metrics, no uptime probe. This is a known gap and
the next operational investment.

---

### 5.15 Testing and CI

#### D67 — Offline-first backend tests

**Decision:** adapter tests use saved fixtures; matcher, queue, billing, and entitlement
tests are pure unit tests; the API suite is live and opt-in.

**Why:**
- The default suite must run offline and deterministically.
- Live career sites are flaky and rate-limited.
- The live API suite validates SQL and migrations against a real database when credentials
  are available.

**Alternatives rejected:** live-only tests (flaky CI), mock everything (misses SQL drift).

**Cost accepted:** fixtures can go stale, and the live API suite does not run by default in
CI. Migration and SQL parity bugs can slip through.

#### D68 — CI gates on lint, format, and tests

**Decision:** GitHub Actions runs Ruff check, Ruff format check, offline pytest, and Vitest
on push to `main` and every PR. API tests are gated by a repository variable and secrets.

**Why:**
- Formatting and lint drift are cheap to prevent.
- The offline suite catches most regressions without credentials.
- The live suite is available when secrets are configured.

**Alternatives rejected:** no CI (quality drift), live tests always (flaky, secret-dependent).

**Cost accepted:** model behavior and SQL parity are only partially covered.

---

## 6. Tradeoff ledger

| # | Decision | Alternative rejected | Why chosen | Cost accepted |
|---|---|---|---|---|
| 1 | Modular monolith | Microservices | Operability, consistency, single developer | One process can starve another |
| 2 | Postgres queue | Redis/Celery/Kafka | Constraints, locks, zero new infra | ~30 s delivery granularity |
| 3 | Global jobs | Per-user copies | One ingest serves all users | Matching fan-out |
| 4 | Adapter registry | Universal scraper | Testability, isolation | Long if-chain |
| 5 | Official APIs first | Playwright everywhere | Reliability, politeness, low egress | Less coverage |
| 6 | Stable-ID dedupe | Fuzzy matching | Deterministic, correct | Reposts with new IDs duplicate |
| 7 | Lifecycle tracking | Delete missing jobs | Repost detection, reversibility | Extra SQL/state |
| 8 | Drop descriptions | Store full text | Egress/storage; title-only matching | No in-app descriptions |
| 9 | First poll backfill | Alert on everything | Prevents floods | A new job between add and first poll is silent |
| 10 | Per-ATS scheduling | One global poll | Isolation, freshness tuning | More scheduler jobs |
| 11 | Advisory locks | Running-row lock | Crash-safe, cross-process | Postgres-specific |
| 12 | Worker split | One process | Protects API latency | Two services |
| 13 | Quiet-board backoff | Poll everything always | Saves egress | Up to ~3 h discovery delay |
| 14 | No early pagination stop | Date/ID cutoff | Measured job loss | More requests |
| 15 | Deterministic matcher | LLM/embeddings | Explainability, cost, testability | No semantic matching |
| 16 | Whole-word matching | Substring | Precision | Misses morphology |
| 17 | Category-share score | Weighted/ML score | Simple, explainable | Coarse ranking |
| 18 | Per-source matching | End-of-run batch | Bounds latency by source | More concurrent work |
| 19 | 24 h match retention | Keep all matches | Bounds 5B-row explosion | Older matches unavailable |
| 20 | Grouped matching | Per-user loops | 30k → 1k evaluations | Signature canonicalization risk |
| 21 | Postgres recompute | Next-poll only | Immediate UI consistency | Python/SQL parity risk |
| 22 | Queue-driven alerts | Inline sends | Retries, delays, idempotency | Up to ~30 s + user delay |
| 23 | DB idempotency | App-only checks | Concurrency-safe | At-least-once duplicate window |
| 24 | Telegram-only | Email now | Reliability, compliance simplicity | No email fallback |
| 25 | Telegram pacing | Burst sends | Avoids 429 flood | Large drains take minutes |
| 26 | Signed cookies | Session table/JWT-localStorage | Stateless, httpOnly | No per-session revocation |
| 27 | PBKDF2 600k | bcrypt/argon2 | Stdlib, no dependency | ~0.5 s CPU/login |
| 28 | Role + capabilities | Roles only | Fine-grained revocation | Two concepts |
| 29 | DB rate limiting | In-memory/Redis | Shared across replicas | DB write per action |
| 30 | Manual billing first | Wait for PSP | Unblocks product | Operational burden |
| 31 | 12 h single-use coupons | Reusable codes | Abuse resistance | Support friction |
| 32 | Raw SQL migrations | ORM/Alembic | Postgres-specific features | No autogeneration/rollback |
| 33 | Dual DB access | One access path | Avoids rewrite; SQL for hot paths | Two mental models |
| 34 | Constraints over checks | App checks | Correctness under concurrency | Error handling |
| 35 | Aggressive retention | Keep everything | Bounded storage | History loss |
| 36 | App Router + no data lib | React Query/Redux | Simplicity | Boilerplate, no shared cache |
| 37 | Client gates + API checks | Middleware-only | Single trust boundary | Shell can load for unauthorized users |
| 38 | localStorage job state | DB persistence | Anonymous-friendly, cheap | No cross-device sync |
| 39 | Two visual systems | One global system | Marketing vs density | Inconsistency debt |
| 40 | Self-hosted fonts | Google Fonts CDN | Privacy | Larger bundle |
| 41 | `to_thread` + async pools | Sync-only | Keeps event loop free | Lifecycle complexity |
| 42 | SQL fan-out reduction | REST pagination | Egress/latency | Two query paths |
| 43 | Projections/GZip | `SELECT *` | Egress | More explicit SQL |
| 44 | No RLS | RLS policies | Current architecture simplicity | Route-check discipline |
| 45 | 18+ and legal pages | Launch without | Compliance | Placeholders remain |
| 46 | Render single service | Worker split now | Cost/simplicity | Long polls share the process |
| 47 | Stall detection only | Sentry/Grafana | Minimal ops | No error tracking/metrics |
| 48 | Fixtures offline | Live tests | Deterministic CI | Fixture staleness |
| 49 | CI unit gates | Live tests always | No secrets/flakiness | SQL/parity bugs can slip |

---

## 7. Failure analyses and war stories

### 7.1 The pagination early-stop that hid new jobs

**Symptom:** The poller wanted to stop paginating once it reached jobs older than the last
seen date, or once a page contained only known IDs. It looked like an easy 50%+ reduction
in requests.

**Investigation:** A shadow run compared "stop early" vs "paginate fully":
- SuccessFactors page 1 contained a **February 2025** posting among **April 2026** jobs.
- Workday only exposes relative dates ("Posted 3 Days Ago"), not exact timestamps.
- ID-based stopping hid **18** new Workday jobs and **67** new Avature jobs behind pages
  full of known IDs.

**Decision:** reject early termination entirely; accept the request cost. The savings came
from concurrency and quiet-board backoff instead.

**Lesson:** "New to us" is not the same as "new in the source's ordering". Source ordering
is not chronological, and known IDs do not imply a known tail.

### 7.2 The Supabase egress bill

**Symptom:** 7.35 GB of egress in 14 days (~538 MB/day) on a 5 GB/month free tier.

**Investigation:** It was not the frontend, images, or storage. The backend was repeatedly
reading the `jobs` table over the internet:
- per-source dedupe reads (~202 sources × ~35 kB),
- unbounded `notifications_sent` reads,
- `SELECT *` projections,
- large `poll_runs.sources` JSONB payloads.

**Fixes:** config first, then scoped queries, SQL upserts, poll tuning, caching, projections,
retention, and monitoring. The plan targeted <500 MB/month with no API contract changes.

**Lesson:** measure egress by component before optimizing. The obvious suspect (the browser)
was innocent.

### 7.3 The poll that froze the API

**Symptom:** During a long poll, `/health`, the Telegram bot, and dashboard requests stalled.

**Cause:** synchronous Supabase REST calls inside `async def` held the event loop for the
duration of the run.

**Fix:** `asyncio.to_thread` around the heavy pipeline entry points, then a loop-keyed async
psycopg pool for the hottest queries, then a worker split in production.

**Lesson:** `async def` is not a performance feature if the body blocks. Offload blocking
I/O or use an async driver.

### 7.4 The first-poll flood

**Symptom:** Adding a large company board sent hundreds of "new job" alerts for roles that
had existed for months.

**Cause:** the pipeline treated the first fetch as new.

**Fix:** suppress notifications on `first_check`; the first poll is a baseline.

**Lesson:** "newly observed" and "newly published" are different events. Alerting must model
the latter.

### 7.5 Dead boards: deactivate, do not delete

**Symptom:** 10 dead Greenhouse boards produced 404s every hour and wasted egress.

**Options:** delete the source rows or set `active=false`.

**Decision:** deactivate. Deleting cascades to `jobs`, destroying history (one board had 78
jobs) and making rollback impossible. `sources.json` was already clean, so the sync would
not resurrect them.

**Lesson:** in an append-only discovery system, deletion is a product decision, not a
cleanup task.

### 7.6 The auth pivot: OTP to passwords

**Symptom:** The first multi-user design used email/Telegram OTP codes.

**Reality:** OTP added delivery dependencies and friction; email deliverability became a
prerequisite for login.

**Decision:** ship password login with signed session cookies; keep Telegram as a linked
identity and Mini App login path. Migrations 027–028 added passwords and Telegram login;
migration 048 dropped the OTP tables.

**Lesson:** authentication should not depend on the channel you are still trying to make
reliable.

### 7.7 The design direction pivot

**Symptom:** The first dashboard direction was a dark neo-glass console with cyan accents.

**Decision:** move public pages to a Warm Editorial system (ink on parchment, Fraunces,
offset shadows), keep the dashboard dark and dense. The design was chosen after a 15-way
exploration.

**Lesson:** a radar product can feel editorial and calm in marketing while staying
instrument-like in the dashboard. The cost is genuine inconsistency, tracked as debt.

### 7.8 The parity bug that is still open

**Symptom:** Python matching is whole-word, but preference saves sometimes behave like the
old substring matcher.

**Cause:** multiple historical `recompute_job_matches` overloads coexist in Postgres. The
signature called by `matcher.py` resolves to an older substring-based version instead of
the whole-word version from migration 064.

**Status:** known, documented, and a top priority. The fix is to drop/replace the stale
overloads and add a regression test that saves preferences and compares Python and SQL
results.

**Lesson:** two implementations of the same rule need a parity test, not good intentions.
Migration history is part of the API surface.

---

## 8. Scaling to 10,000 users

The 10k-hosting plan is the source of this section. It is a plan, not a claim that the
system has run at 10k users.

### 8.1 The four walls

In order of likely impact:

1. **Telegram** — ~30 messages/sec; a hot posting can match 10–20% of 10k users, producing
   1,000–2,000 sends in one drain tick.
2. **Email** (if enabled) — spam filtering and anti-spam law at 1k–3k recipients; SPF, DKIM,
   DMARC, unsubscribe, and bounce handling are required.
3. **Unbounded tables** — `notifications_sent` and `job_matches` grow without retention.
4. **Single box** — no tested restore, no failover, no uptime monitoring.

### 8.2 Existing scaling wins

These are already implemented and measured:

| Win | Effect |
|---|---|
| Match retention (24 h) | Prevents 10k × 500k = 5B rows |
| Grouped matching by signature | 150 users × 200 jobs: 30k → 1k evaluations; 1.335 s → 0.018 s |
| Per-ATS scheduling + advisory locks | Slow Workday runs do not block Greenhouse |
| Tiered/user delays | Spreads alert load instead of a burst |
| Per-source matching | Job → match latency bounded by source fetch time |
| Quiet-board backoff | ~26% of boards skipped per run at steady state |
| Async pools + `to_thread` | API and bot stay responsive during polls |
| Telegram pacing | 25 msg/sec sustained, burst 30 |

### 8.3 The build order

1. **Safety:** nightly `pg_dump --format=custom` to object storage and a rehearsed restore;
   email plumbing if email is in scope; CAPTCHA on register/login.
2. **Reliability:** Telegram pacing telemetry, 90-day sent retention (current code prunes
   at 24 h), production frontend build, worker split.
3. **Before 200 paying users:** live Razorpay, Sentry/uptime/stall alerting, synthetic
   load test.

### 8.4 Unit economics (from the plan)

| Paying users | Revenue | Razorpay | Email | Infra | Misc | Before salary/support |
|---:|---:|---:|---:|---:|---:|---:|
| 500 | ₹24,500 / $300 | −₹600 | −₹1,700 | −₹4,800 | −₹400 | ~₹17k / ~$200 |
| 1,000 | ₹49,000 / $600 | −₹1,200 | −₹3,400 | −₹4,800 | −₹400 | ~₹39k / ~$480 |

Assumptions: ₹49/month, 5–10% conversion at 10k users, ₹4,800 infra, email only if enabled.
The business works only if deliverability and retention hold; otherwise the unit economics
invert.

### 8.5 Readiness gates

- Restore performed in the last 7 days.
- One-click unsubscribe in under 2 seconds (if email exists).
- A synthetic 2k-user popular posting without a 429 flood.
- 90-day retention deletion verified.
- `/health` and a 70-minute stall alert running externally.
- CAPTCHA and legal pages live.
- Cohort rollout: 100 → 1,000 → 3,000 → 10,000.

---

## 9. Known limitations and debt

This section is deliberately blunt. A reviewer should not have to discover these alone.

### 9.1 Correctness and data

1. **Matcher SQL/Python parity bug.** Multiple `recompute_job_matches` overloads coexist;
   the one called by `matcher.py` can resolve to the older substring-based implementation
   instead of the whole-word version. Python and SQL can disagree after a preference save.
2. **Razorpay webhook dedup is storage-only.** Duplicate provider events are recorded with
   a unique constraint, but duplicate processing is not short-circuited at the entry point;
   side effects can run twice.
3. **`account_delete` audit writes violate the `auth_events` check constraint.** The audit
   path can fail instead of recording the event.
4. **Descriptions are gone.** Detail endpoints return `description: null`; matching is
   title-only. Users must click through to read the posting.
5. **Job reposts with new external IDs duplicate.** Dedup is stable-ID based by design.
6. **Location parsing is heuristic.** Ambiguous names (e.g., Georgia) can map incorrectly.

### 9.2 Security and operations

7. **`JOBQUEST_REQUIRE_AUTH=false` acts as the owner.** Convenient locally; catastrophic if
   exposed publicly. Production must set it to `true`.
8. **No RLS.** All authorization is route-level; one missed dependency is a breach.
9. **No per-session revocation.** Rotating `SECRET_KEY` invalidates all sessions; a stolen
   cookie remains valid until TTL.
10. **In-memory rate-limit fallback.** Used in tests and when the DB path fails; it is
    per-process and resets on restart.
11. **No CAPTCHA or email verification.** Rate limiting and the subscription/coupon gate are
    the current abuse controls.
12. **No password reset route.** The login page points users to support/unlock.
13. **No backups/restore drill.** A single-node database with no off-site dump.
14. **No error tracker, uptime probe, or metrics.** Only logs, `poll_runs`, source health,
    and a Telegram stall alert.
15. **`.env.example` omits `RAZORPAY_*` variables.** They are read by config but not
    documented in the example file.
16. **Email is legacy.** The queue cancels email rows at drain; `notify.py` is only used by
    a test script. The README and some plan docs still discuss email as if it were live.

### 9.3 Frontend

17. **Client gates are not security.** They are UX only; the API enforces access.
18. **Only `/matches` uses `PaywallGate`.** Locked users can load other dashboard shells;
    backend entitlement checks are essential.
19. **No middleware.** Route protection is client-side.
20. **No ESLint config.** `npm run lint` prompts for setup; CI runs tests, not lint.
21. **No component, E2E, visual-regression, or accessibility tests.** Four Vitest suites
    cover pure logic and legal guards.
22. **Design inconsistency.** Warm Editorial tokens, a dark Ink dashboard, a green auth
    layout, and a separate landing design coexist; `html/body` are hardcoded dark.
23. **Company logos call Google's favicon service.** A third-party request remains despite
    self-hosted fonts.
24. **No cross-device saved/hidden state.** localStorage only.
25. **`NEXT_PUBLIC_API_URL` is build-time.** The production compose runtime value cannot
    change a URL already inlined in the client bundle.
26. **Docker frontend build uses `npm install`, not `npm ci`.** Installs are not lockfile
    reproducible.
27. **Referral message is hardcoded** with a specific name/profile, not user data.
28. **Legal placeholders remain** (entity, address, contact, grievance officer, DMCA agent).

### 9.4 Scale and architecture

29. **Single-node Postgres.** No read replicas, partitioning, or tested failover.
30. **Free-tier Supabase egress risk.** The 500 MB → 8 GB plan boundary is a near-term
    concern; the egress plan is partially implemented.
31. **No automated SQL/RLS parity tests.** Migrations are validated manually and by the
    opt-in API suite.
32. **`poll_runs.sources` can be large** (~37 kB max before summarization); compression
    changes its shape.
33. **No dedicated AI layer.** Deliberate, but it limits semantic matching.

---

## 10. What I would do next

In priority order:

1. **Fix the matcher overload bug and add a Python-vs-SQL parity test.** This is the only
   known correctness issue that can change user-visible matches.
2. **Make Razorpay webhook processing idempotent at the entry point.** Store-and-skip
   duplicate provider events before any side effect.
3. **Backups + restore drill, Sentry, uptime monitoring, and stall alerting.** The system is
   observable enough to debug, not enough to sleep well.
4. **Decide email:** either complete it (SPF/DKIM/DMARC, verified domain, one-click
   unsubscribe, bounce/complaint webhooks, double opt-in) or delete the legacy path and
   remove it from the docs.
5. **Clean up the operational edges:** `auth_events` constraint, `RAZORPAY_*` in
   `.env.example`, password reset, and per-session revocation if needed.
6. **Frontend quality:** ESLint, component tests, one Playwright happy path, accessibility
   checks, and a pass to unify or explicitly scope the visual systems.
7. **Docker reproducibility:** `npm ci` with the lockfile.
8. **Scale work from the 10k plan:** Telegram telemetry, 90-day sent retention, external
   health checks, and a synthetic 2k-user alert burst.
9. **Then, and only then, consider optional AI:** natural-language preference parsing and
   match explanations, always off the critical path and cached.

---

## 11. Interview Q&A

### "Walk me through a job from source to Telegram."

The scheduler fires `poll-<ats>`; an advisory lock serializes the ATS. The poller syncs
sources, prunes old data, selects active boards, and fetches them concurrently with a
shared retrying client. Each adapter returns `NormalizedJob` objects. The pipeline filters
stale postings, dedupes within the batch, upserts with `ON CONFLICT`, and updates lifecycle
state. New IDs go to `match_and_enqueue`, which evaluates eligible users' preferences and
writes queue rows with `scheduled_for = now + user delay`. A drain worker sends due rows
through Telegram with pacing, records the ledger, and retries failures up to 3 times.

### "How do you prevent duplicate alerts?"

Three layers: a unique `(user_id, job_id, channel)` constraint on the queue and ledger;
`ON CONFLICT DO NOTHING` on insert; and a ledger check before sending. Delivery is
at-least-once, not exactly-once — an external API cannot guarantee exactly-once. The window
for a duplicate is a crash after Telegram accepts a message but before the ledger commit.

### "What happens when a source fails?"

Only that source fails. It records the error, HTTP status, error type, and duration. The run
continues. The source appears in `/api/sources/unhealthy` and the Runs page. Backoff and
quiet-run tracking prevent a broken board from dominating every run.

### "Why deterministic matching instead of an LLM or embeddings?"

Three reasons: explainability (every match shows why), cost/latency (matching runs for
every new job for every user), and testability (pure functions and SQL parity). The product
problem is discovery and noise reduction, not semantic ranking. An LLM can be an optional
later layer for natural-language preferences and explanations, never on the critical path.

### "How does the matcher actually score?"

Terms are whole-word matched. Roles, keywords, and seniority are OR'd; location is a hard
filter when set; excluded companies and roles disqualify. The score is the share of active
categories hit (0–100). No active categories means 100.

### "How would you scale to 10,000 users?"

Keep the monolith. Bound the match table (24 h retention), group users by preference
signature, match per source, pace Telegram, prune the sent ledger, use per-ATS scheduling
with locks, and add observability and backups. Move to a managed Postgres when revenue
justifies it; add Redis or a real broker only when a measured bottleneck demands it.

### "Why Postgres for the queue and locks instead of Redis/Celery?"

The queue volume is modest, the database is already a hard dependency, and constraints give
idempotency for free. Advisory locks are crash-safe and cross-process. Adding a broker would
add operational surface without solving a measured problem. If throughput or fan-out makes
Postgres the bottleneck, the queue interface makes a later swap possible.

### "Why no ORM?"

The schema relies on Postgres-specific features: `ON CONFLICT`, advisory locks, JSONB,
arrays, partial indexes, and SQL functions. Raw SQL is reviewable, explicit, and portable
to psql. The cost is no autogeneration or rollback framework, which is acceptable for a
small team and a Postgres-only product.

### "How is multi-user access secured?"

Signed httpOnly session cookies, PBKDF2-600k passwords, login lockout, DB-backed rate
limiting, server-side role/capability checks on every protected route, and a subscription
gate for plain users. The service-role key never leaves the server. Client gates are UX
only. The known weak spot is that there is no RLS; authorization discipline is enforced in
code and tests.

### "How do you keep payments idempotent?"

Coupons are claimed with an atomic conditional update. Razorpay events are stored with a
unique provider event key, and subscription state is checked before provisioning. The
known gap is that duplicate webhook events are recorded but not short-circuited before
processing; that is the next fix.

### "What was the hardest bug?"

The pagination early-stop. It looked like an obvious optimization, but measurement showed
it silently hid newly published jobs behind known pages and non-chronological ordering. We
rejected the optimization and documented why. The second hardest was the Supabase egress
blowup, which required measuring by component and changing access patterns rather than
adding infrastructure.

### "How do you test scrapers?"

Saved fixtures per ATS, offline parser tests, and a small live API suite that is opt-in.
Each adapter has tests for fetch, parse, missing fields, pagination, duplicates, and invalid
responses. Fixture staleness is a known risk; production source health catches shape
changes.

### "What would you change if you started over?"

I would build the observability and backup story earlier, avoid the duplicate SQL matcher
overloads by keeping one implementation or adding a parity test from day one, and decide
the email question before writing email code. I would also make the frontend design system
single-source-of-truth earlier. The core architecture — monolith, Postgres queue, isolated
adapters, deterministic matching — I would keep.

### "What are the biggest risks right now?"

The matcher parity bug (correctness), no verified backup (durability), the auth
compatibility mode if misconfigured (security), and Telegram rate limits under a viral
posting (delivery). None are architectural; all are operational hardening.

---

## 12. Numbers appendix

### 12.1 Codebase

| Metric | Value |
|---|---|
| Backend adapters | 24 |
| ATS families in `sources.json` | 22 (plus generic `custom`) |
| Configured boards | 2,519 |
| API endpoints | 77 + `/health` |
| Migrations | 64 (`001`–`065`, no `057`) |
| Backend test suites | 4 |
| Offline backend tests | ~207 |
| Live API tests | 19 |
| ATS fixture directories | 17 |
| Frontend pages | 35 page files |
| Frontend test files | 4 |
| Frontend tests | 24 |
| Python image | 3.13 slim; CI uses 3.12 |
| Frontend stack | Next 15.1.6, React 19, TS 5.7.3, Tailwind 3.4.17, Vitest 4.1.10 |

### 12.2 Operational defaults

| Setting | Default |
|---|---|
| Per-ATS interval | 3,600 s, jitter ±120 s |
| Full integrity sweep | 43,200 s (12 h) |
| Notification drain | 30 s |
| Subscription sweep | Daily 03:17 Asia/Kolkata |
| Stall watch | Every 600 s; alert at 70 min |
| Alert delay | 10 min privileged / 10 min normal (code default) |
| Queue retry | 3 attempts |
| Telegram pacing | ~25 msg/s sustained, burst 30 |
| Job retention | 30 days |
| Inactive job retention | 7 days |
| Match retention | 24 hours |
| Sent ledger retention | 24 hours |
| Auth event retention | 90 days |
| Rate event retention | 24 hours |
| Session TTL | 168 hours |
| Password hashing | PBKDF2-HMAC-SHA256, 600k iterations |
| Standard plan | ₹49/month (4,900 paise), INR |
| Coupon TTL | 12 hours, single-use |

### 12.3 Measured performance and scale

| Measurement | Result |
|---|---|
| Workday poll (87 boards) | 538 s vs 900 s baseline (−40%) |
| Global sweep | ~10–11 min |
| Quiet boards skipped | ~26% per run at steady state |
| Grouped matching | 30k → 1k evaluations; 1.335 s → 0.018 s |
| Existing-ID lookup | 20 REST round-trips → 1 SQL query |
| Per-source settings reads removed | ~280 queries/run |
| Egress before | 7.35 GB/14 days (~538 MB/day) |
| Egress target | <500 MB/month |
| `poll_runs.sources` average | ~2.4 kB (max ~37 kB) |
| Database snapshot | 129 MB (jobs 111 MB) at 185k rows |
| Jobs baseline | ~515k at 2,569 sources |
| Poll runs baseline | ~301/day; ~2.4 min average |

### 12.4 Historical stack facts

| Item | Value |
|---|---|
| Notification fan-out prediction at 10k | 1,000–2,000 sends per hot drain |
| Match table projection without retention | 10k × 500k = 5B rows |
| Telegram limit | ~30 messages/sec |
| Email volume at 10k/month | ~300k emails |
| Razorpay fees | ~2–3% |
| Merchant-of-record fees | ~5% (Paddle/Lemon Squeezy) |
| Stripe fees | ~2.9% + |
| Free Supabase tier | 5 GB egress/month |

---

## 13. Glossary

| Term | Meaning |
|---|---|
| **ATS** | Applicant Tracking System — the software a company uses to host job postings (Greenhouse, Workday, etc.). |
| **Board identifier** | The ATS-specific slug/URL used to fetch a company's postings. |
| **NormalizedJob** | The adapter-independent job representation produced by every source. |
| **Source** | One row in `sources`: a company board, its ATS type, and health state. |
| **First check** | The first successful poll of a source; treated as backfill and never alerted. |
| **Quiet board** | A healthy board with 5+ consecutive polls producing no new jobs; polled less often. |
| **Advisory lock** | A Postgres lock used to serialize a poll across processes. |
| **Match** | A row in `job_matches` connecting a user to a job with reasons and a score. |
| **Entitlement** | The effective access a user has, derived from role, capabilities, and subscription. |
| **Coupon** | A single-use, 12-hour code that grants access. |
| **Queue intent** | A row in `notification_queue` describing a message to send later. |
| **Sent ledger** | `notifications_sent`, the idempotency record of delivered alerts. |
| **Egress** | Data transferred out of the database provider; a major cost driver for Supabase. |
| **Ink / Warm Editorial** | The two main frontend visual systems (dashboard vs public pages). |
| **PostgREST** | The REST layer over Postgres used by supabase-py for table CRUD. |
| **Worker** | The process that runs the scheduler and Telegram bot without the HTTP API. |
| **Stall detector** | A scheduled check that alerts when no poll has completed in 70 minutes. |

---

<div align="center">
  <sub>If you are reviewing this for an interview: the strongest part of the system is the
  ingestion and lifecycle design; the most honest part is Section 9.</sub>
</div>
