<div align="center">
  <img src="frontend/logo.png" width="88" alt="JobQuest logo" />
  <h1>JobQuest</h1>
  <p><strong>The job market, filtered while you sleep.</strong></p>
  <p>JobQuest watches thousands of company career pages, finds the postings that matter to you,<br />and sends them to Telegram before they reach the big job boards.</p>

  [![CI](https://github.com/niranjcn/jobRadar/actions/workflows/ci.yml/badge.svg)](https://github.com/niranjcn/jobRadar/actions/workflows/ci.yml)
  [![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
  [![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
  [![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org/)
  [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791.svg)](https://www.postgresql.org/)
</div>

> **Reading this as an interviewer or reviewer?** Start with
> **[Design Decisions & Tradeoffs](docs/DESIGN_DECISIONS.md)** — a complete engineering
> companion covering the architecture, every major decision, rejected alternatives,
> measurements, failure analyses, and known debt. For the exact implemented state of the
> repo, see **[docs/CODEBASE_MAP.md](docs/CODEBASE_MAP.md)**.

## Contents

- [What is JobQuest?](#what-is-jobquest)
- [Why people use it](#why-people-use-it)
- [Feature tour](#feature-tour)
- [How it works](#how-it-works)
- [Architecture](#architecture)
- [Data model](#data-model)
- [Tech stack](#tech-stack)
- [Quick start](#quick-start)
- [Using JobQuest](#using-jobquest)
- [Sources and adapters](#sources-and-adapters)
- [Preferences and matching](#preferences-and-matching)
- [Notifications](#notifications)
- [API](#api)
- [Scheduling and operations](#scheduling-and-operations)
- [Project layout](#project-layout)
- [Testing and CI](#testing-and-ci)
- [Deployment](#deployment)
- [Security and privacy](#security-and-privacy)
- [Status and roadmap](#status-and-roadmap)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

---

## What is JobQuest?

JobQuest is a **job discovery and alerting platform**. It continuously polls company
career pages across many applicant-tracking systems (ATSs), normalizes every posting into
one shared model, removes duplicates, matches jobs against a person's preferences, and
delivers relevant new roles through Telegram.

The problem it solves is simple: the best jobs often appear on a company's own careers
page — or on an obscure ATS board — long before they are syndicated to LinkedIn, Indeed,
or a job board. Refreshing hundreds of career pages by hand is impossible; checking job
boards means seeing the same posting five times, days late, buried under ads.

JobQuest turns that into a background process:

```text
Company career page  →  normalized job  →  deduplicated  →  matched to you  →  Telegram alert
        (many ATSs)                              (one row)     (your rules)      (seconds later)
```

### A concrete example

```text
09:12  A company publishes "Backend Engineer (Python)" on Greenhouse.
09:13  JobQuest's Greenhouse poll sees the new posting, normalizes it, and upserts it.
09:13  The matcher checks it against every eligible user's preferences.
09:13  A queue row is created for each user it matches, delayed by their alert setting.
09:23  The drain worker sends a Telegram message with title, company, location, score,
       and a direct application link.
09:25  You apply — before the role appears on a public job board.
```

A failing source never stops the rest. Each ATS has its own schedule, its own lock, and
its own health record, so a broken Workday tenant cannot delay a healthy Greenhouse feed.

---

## Why people use it

| Audience | What JobQuest gives them |
|---|---|
| **Active job seekers** | Early discovery from 2,500+ company boards without manually refreshing career pages. |
| **Early-career and niche candidates** | Filters for roles, keywords, locations, and seniority instead of an algorithmic feed built for engagement. |
| **People targeting specific companies** | Add any supported company board with one JSON line; track it forever without code changes. |
| **Privacy-conscious users** | Self-hostable. Jobs, preferences, and alerts stay in your own Postgres; no resume upload, no third-party tracker. |
| **Operators and small teams** | A multi-user dashboard, subscription access, coupons, admin controls, and public job search in one deployable stack. |
| **Engineers** | A readable reference for a production-grade ingestion pipeline: isolated adapters, deterministic matching, idempotent notifications, and measurable tradeoffs. |

The public side needs no account: anyone can browse normalized jobs at `/browse`. Accounts
add preferences, match scores, saved jobs, and Telegram alerts.

---

## Feature tour

| Area | What you get |
|---|---|
| **Ingestion** | 24 source adapters covering Greenhouse, Lever, Ashby, Workday, Oracle/Taleo, iCIMS, SuccessFactors, Phenom, Avature, Workable, SmartRecruiters, Breezy, Jobvite, JazzHR, BambooHR, Teamtailor, Rippling, Eightfold, Amazon, Google, Emirates, Remotive, We Work Remotely, and a generic custom adapter. |
| **Coverage** | `backend/sources.json` ships ~2,519 company boards; synced into the database automatically before the first poll. |
| **Deduplication** | Database-level `UNIQUE(source_id, external_job_id)`, plus lifecycle tracking for reposts and removals. |
| **Matching** | Deterministic, explainable matching over roles, keywords, locations, seniority, and exclusions. Every match stores a 0–100 score and the reasons it matched. |
| **Geo awareness** | Country aliases and remote normalization, so "UAE", "United Arab Emirates", and "Dubai" can resolve to the same preference. |
| **Notifications** | Postgres-backed queue, per-user delay, retries, and per-user/job/channel idempotency. Telegram is the live channel. |
| **Telegram** | Alert delivery, 14 bot commands, inline job search, and an optional Mini App dashboard. |
| **Dashboard** | Jobs, matches, companies, sources, schedules, runs, timings, preferences, notifications, billing, settings, onboarding. |
| **Public site** | Landing page, job browsing and detail pages, pricing, schema explorer, and legal pages — no login required. |
| **Accounts** | Password login, signed session cookies, 18+ registration, approval state, lockout, rate limiting, and account export/delete. |
| **Access and billing** | Standard plan at ₹49/month, single-use coupons, manual grants, and an optional Razorpay provider. |
| **Admin** | User management, roles and capabilities, coupons, preference presets, subscription comps, egress dashboard, and schema inspection. |
| **Operations** | Per-ATS scheduling, advisory locks, quiet-board backoff, source health, stale-run recovery, stall detection, and automatic SQL migrations. |
| **Quality** | Offline adapter tests with saved fixtures, matcher and billing unit tests, frontend Vitest suites, Ruff, TypeScript checking, GitHub Actions. |

---

## How it works

```text
                        ┌──────────────────────────────────────────────┐
                        │               Company career pages           │
                        │  Greenhouse · Lever · Workday · Oracle · ... │
                        └──────────────────────┬───────────────────────┘
                                               │  HTTPS (official APIs / JSON / HTML)
                                               ▼
                        ┌──────────────────────────────────────────────┐
                        │              Source adapters                 │
                        │   fetch → parse → validate → NormalizedJob   │
                        └──────────────────────┬───────────────────────┘
                                               │
                                               ▼
                        ┌──────────────────────────────────────────────┐
                        │           Normalization and dedup            │
                        │  shared Job model · (source_id, external_id) │
                        └──────────────────────┬───────────────────────┘
                                               │
                                               ▼
                        ┌──────────────────────────────────────────────┐
                        │        PostgreSQL / Supabase (shared)        │
                        │  sources · jobs · job_matches · users · ...  │
                        └──────────────────────┬───────────────────────┘
                                               │
                                               ▼
                        ┌──────────────────────────────────────────────┐
                        │        Deterministic preference matcher      │
                        │  roles · keywords · locations · seniority    │
                        └──────────────────────┬───────────────────────┘
                                               │
                                               ▼
                        ┌──────────────────────────────────────────────┐
                        │          Notification queue (Postgres)       │
                        │  scheduled_for · retries · idempotency       │
                        └──────────────────────┬───────────────────────┘
                                               │
                                               ▼
                        ┌──────────────────────────────────────────────┐
                        │                 Telegram                     │
                        │   direct message · bot commands · Mini App    │
                        └──────────────────────────────────────────────┘
```

Two properties matter more than the diagram:

1. **Adapters are disposable.** The core pipeline only sees `NormalizedJob`. Adding or
   removing an ATS never changes matching, storage, or notifications.
2. **The queue is the boundary.** Ingestion never sends a message directly. It writes an
   intent; a separate drain worker owns delivery, retries, and idempotency.

---

## Architecture

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                              Next.js 15 frontend                             │
│  Public: /, /browse, /pricing, /schema, legal   Dashboard: /dashboard, ...    │
│  Admin: /admin/*                         Client gates + backend enforcement   │
└───────────────────────────────────┬──────────────────────────────────────────┘
                                    │  REST (credentials: include)
                                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                          FastAPI application (Python)                        │
│                                                                              │
│  auth_routes   access_routes   public_routes   routes   admin_routes         │
│       │              │              │            │           │               │
│       └──────────────┴──────┬───────┴────────────┴───────────┘               │
│                             ▼                                                │
│  services: auth · users · access · entitlements · matcher · notifications     │
│                             │                                                │
│              ┌──────────────┼────────────────┐                               │
│              ▼              ▼                ▼                               │
│          adapters       poller/scheduler   Telegram bot                      │
│        (24 ATS files)   (APScheduler)      (long polling)                    │
└──────────────┬──────────────────────────────┬────────────────────────────────┘
               │                              │
               ▼                              ▼
┌──────────────────────────────┐   ┌───────────────────────────────────────────┐
│  PostgreSQL 15               │   │  Supabase PostgREST (optional)            │
│  raw SQL migrations          │   │  table reads/writes via supabase-py       │
│  psycopg 3 sync + async pools│   │  service-role key stays server-side       │
└──────────────────────────────┘   └───────────────────────────────────────────┘

Deployment shapes:
  Local dev        docker compose up -d          API + frontend + Postgres + PostgREST
  Production       docker compose --prod         API service + worker (scheduler + bot)
  Single-service   render.yaml                   API + in-process scheduler + bot
```

| Component | Responsibility |
|---|---|
| **Source adapters** (`backend/app/adapters/`) | Speak each ATS's language and return `NormalizedJob` objects. No database, matching, or notification logic. |
| **Poller** (`backend/app/poller.py`) | Orchestrates fetch → normalize → dedupe → upsert → lifecycle → match → enqueue → drain → record run. |
| **Scheduler** (`backend/app/main.py`) | APScheduler jobs per ATS, a 12-hour integrity sweep, a notification drain, subscription expiry, and stall detection. |
| **Matcher** (`backend/app/matcher.py`) | Deterministic whole-word matching, scoring, exclusions, and geographic aliases. |
| **Notification queue** (`backend/app/notification_queue.py`) | Builds per-user intents, schedules delays, drains due rows, retries, and deduplicates. |
| **Telegram bot** (`backend/app/telegram/`) | Long polling, commands, inline search, and Mini App entry points. |
| **FastAPI app** (`backend/app/main.py`) | API, lifespan bootstrap (migrations, owner, scheduler, bot), and `/health`. |
| **Worker** (`backend/app/worker.py`) | Runs scheduler and bot without HTTP, so a long poll cannot block the API. |
| **Frontend** (`frontend/`) | Next.js App Router UI for public browsing, accounts, dashboard, billing, and admin. |

---

## Data model

The schema is deliberately small and relational. Raw SQL lives in `backend/migrations/`
(64 files, `001`–`065`, no `057`) and is applied automatically at startup.

| Table | Purpose |
|---|---|
| `sources` | One row per company board: ATS type, board identifier, health, quiet-run counter, schedule state. |
| `jobs` | Shared, normalized postings. Unique on `(source_id, external_job_id)`. Lifecycle flags track active/removed/reposted rows. |
| `preferences` | One row per user: roles, keywords, locations (JSONB), seniority, exclusions, notification scopes, alert settings. |
| `job_matches` | Per-user matches with `matched_on` reasons and a deterministic `match_score`. Primary key `(user_id, job_id)`. |
| `notification_queue` | Pending/sent/failed intents with `scheduled_for`, attempts, and `UNIQUE(user_id, job_id, channel)`. |
| `notifications_sent` | Delivery ledger and idempotency guard. |
| `users` | Accounts, roles (`user`/`privileged`/`admin`), capabilities, approval and lock state, Telegram identity, password hash, alert delay. |
| `plans`, `subscriptions`, `coupon_codes`, `billing_events` | Subscription catalog, entitlements, single-use coupons, and provider event history. |
| `poll_runs` | Run history: status, counts, duration, per-source outcomes, skipped quiet boards. |
| `poll_schedule` | Live per-ATS interval overrides editable from the dashboard. |
| `preference_presets` | Admin-curated preference templates. |
| `auth_events`, `rate_events` | Security audit and DB-backed rate limiting. |
| `app_settings` | Runtime knobs such as tier delays and geo settings. |

Key design choices:

- **Jobs are global; matches are per-user.** One ingestion serves every account.
- **Descriptions are not stored.** Matching is title/location based by product decision,
  and detail endpoints return `description: null`; this keeps storage and egress small.
- **Database constraints are the source of truth** for deduplication and notification
  idempotency — not application-only checks.

---

## Tech stack

| Layer | Choice | Why |
|---|---|---|
| API | Python 3.12+ / FastAPI / Uvicorn | Async I/O, typed request models, automatic OpenAPI docs. |
| Ingestion | httpx, BeautifulSoup, APScheduler | Shared retrying HTTP client, official APIs first, in-process scheduling. |
| Database | PostgreSQL 15 | Constraints, JSONB, partial indexes, and `pg_try_advisory_lock`. |
| DB access | psycopg 3 (sync + async pools), supabase-py/PostgREST | Raw SQL where it matters; simple table CRUD where it does not. No ORM. |
| Migrations | Plain SQL + `schema_migrations` | Reviewable, deterministic, automatically applied. |
| Matching | Pure Python + a parity SQL function | Explainable and testable without an LLM. |
| Notifications | Postgres queue + Telegram Bot API | Idempotent, retryable, no extra infrastructure. |
| Frontend | Next.js 15, React 19, TypeScript 5.7, Tailwind 3.4 | App Router, fast static/public pages, no extra UI framework. |
| Frontend tests | Vitest 4 | Fast unit tests for API, formatting, storage, and legal guards. |
| Backend tests | pytest, saved fixtures | Offline adapter tests; live API tests are opt-in. |
| CI | GitHub Actions | Ruff + formatting + unit tests + frontend tests on every PR. |
| Deploy | Docker Compose, Render blueprint | One box by default; split API and worker when needed. |

---

## Quick start

### Prerequisites

- Docker + Docker Compose (recommended path)
- A PostgreSQL database — either a [Supabase](https://supabase.com) project or the
  local `postgres` service included in `docker-compose.yml`
- Optional: a Telegram bot token for alerts, and Razorpay keys for live billing

### 1. Configure the backend

```bash
cp backend/.env.example backend/.env
```

Fill in at minimum:

```dotenv
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_KEY=your-service-role-key        # server-side only
DATABASE_URL=postgresql://...              # Postgres URI, URL-encoded password
```

Generate a session secret once you enable authentication:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
# SECRET_KEY=<output>
# JOBQUEST_REQUIRE_AUTH=true
# SESSION_COOKIE_SECURE=true   # when served over HTTPS
```

### 2. Run the stack

```bash
docker compose up -d
```

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| OpenAPI docs | http://localhost:8000/docs |
| Health | http://localhost:8000/health |
| PostgREST (local, optional) | http://localhost:3001 |

The app applies pending migrations on startup. The first poll (or the scheduled poll)
syncs `backend/sources.json` into the `sources` table. No manual SQL is required.

Manual and worker profiles:

```bash
# One-shot sweep over all active sources
docker compose run --rm poll

# Scheduler + Telegram bot without the HTTP API
docker compose --profile worker up worker
```

### 3. Run without Docker

```bash
# Backend
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest tests/test_unit.py -q
uvicorn app.main:app --reload

# Frontend (second terminal)
cd frontend
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_URL=http://localhost:8000` for the frontend. Live reload is already
wired in Docker Compose for both services.

### Environment variables

All variables are documented in `backend/.env.example`. The main groups:

| Group | Variables |
|---|---|
| Core | `SUPABASE_URL`, `SUPABASE_KEY`, `DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS` |
| Ingestion | `POLL_INTERVAL_SECONDS`, `POLL_INTERVAL_<ATS>_SECONDS`, `POLL_CONCURRENCY_<ATS>`, `JOB_RETENTION_DAYS`, `MAX_POSTING_AGE_DAYS` |
| Preferences | `PREF_ROLES`, `PREF_KEYWORDS`, `PREF_LOCATIONS`, `PREF_SENIORITY`, `PREF_EXCLUDED_COMPANIES`, `PREF_EXCLUDED_ROLES` |
| Auth | `JOBQUEST_REQUIRE_AUTH`, `SESSION_TTL_HOURS`, `SESSION_COOKIE_SECURE` |
| Billing | `BILLING_PROVIDER`, `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`, `RAZORPAY_WEBHOOK_SECRET`, `RAZORPAY_PLAN_ID` |
| Telegram | `TELEGRAM_ENABLED`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `TELEGRAM_BOT_USERNAME`, `TELEGRAM_MINI_APP_URL`, `ADMIN_CHAT_ID` |
| Ops | `NOTIFY_DRAIN_SECONDS`, `JOBQUEST_DISABLE_SCHEDULER`, `JOBQUEST_DISABLE_BOT`, `APP_BASE_URL`, `POSTAL_ADDRESS` |

Never commit `backend/.env`. The service-role key bypasses row-level security and must
never appear in frontend code or browser bundles.

---

## Using JobQuest

### Public site — no account needed

| Route | What it does |
|---|---|
| `/` | Landing page with live public jobs and filters. |
| `/browse` | Search all active jobs by keyword, company, country, source, date, and remote status. |
| `/browse/[id]` | Job detail with an external apply link. |
| `/pricing` | Plan and coupon entry points. |
| `/schema` | Read-only public schema explorer. |
| `/contact`, `/dmca`, `/terms`, `/privacy`, `/refund` | Support and legal pages. |

### Account and access flow

```text
Register (email + password, 18+)
        │
        ▼
Account created in a locked state (admin can also hold it for review)
        │
        ├── Redeem a coupon  ──┐
        └── Subscribe (₹49/mo) ─┴──▶ Access unlocked
                                        │
                                        ▼
                              Onboarding: set preferences
                                        │
                                        ▼
                              Connect Telegram (chat ID or deep link)
                                        │
                                        ▼
                              Matches + alerts + dashboard
```

Dashboard pages: `/dashboard`, `/jobs`, `/new-jobs`, `/jobs/[id]`, `/matches`,
`/companies`, `/notifications`, `/preferences`, `/billing`, `/onboarding`, `/sources`,
`/schedule`, `/runs`, `/timings`, `/settings`.

Operator pages: `/admin`, `/admin/users`, `/admin/coupons`, `/admin/presets`,
`/admin/egress`, `/admin/schema`. Admin pages require the `admin` role.

### Telegram bot

Commands: `/start`, `/help`, `/stats`, `/jobs`, `/newjobs`, `/matches`, `/newmatches`,
`/companies`, `/sources`, `/schedule`, `/runs`, `/notifications`, `/preferences`, `/app`.

The bot supports long polling, an inline search mode (`@yourbot query`), and a Mini App
entry point for opening the dashboard inside Telegram. Alerts are batched per user rather
than sent per job.

### Admin console

Admins can approve or lock accounts, change roles and capabilities, set alert delays,
issue single-use coupons, apply preference presets, comp subscriptions, inspect database
size and egress estimates, and browse the schema. System/operator pages are admin-only by
design; they are not subscriber features.

---

## Sources and adapters

### Adding a company

Edit `backend/sources.json` — no code, no SQL:

```json
[
  {
    "company_name": "Stripe",
    "ats_type": "greenhouse",
    "board_identifier": "stripe",
    "active": true
  }
]
```

On the next poll or restart, the entry is upserted into `sources` and polled automatically.

- `company_name` — unique display name
- `ats_type` — one of the supported adapter types
- `board_identifier` — ATS-specific slug or board URL
- `active` — optional; `false` pauses polling without deleting history

Unknown career-page URLs can be probed through the source-detection endpoint
(`POST /api/sources`) to identify the ATS.

### Supported adapters (24)

| Family | Adapters |
|---|---|
| Core ATS | `greenhouse`, `lever`, `ashby`, `workday`, `workable`, `smartrecruiters`, `breezy`, `jobvite`, `jazzhr`, `bamboohr`, `teamtailor`, `rippling`, `eightfold` |
| Enterprise ATS | `oracle` (Taleo + Fusion), `icims`, `successfactors`, `phenom`, `avature` |
| Company-specific | `amazon`, `google`, `emirates` |
| Aggregators | `remotive`, `weworkremotely` |
| Generic | `custom` (JSON/HTML career pages) |

Each adapter lives in `backend/app/adapters/<name>.py`, implements
`JobSourceAdapter.fetch_jobs(board_identifier, client)`, and is registered in
`backend/app/adapters/__init__.py`. Saved fixtures under `backend/tests/fixtures/` keep
the suite offline and deterministic.

---

## Preferences and matching

A preference row contains six lists: roles, keywords, locations, seniority, excluded
companies, and excluded roles. The matcher is deterministic:

- Terms are matched as **whole words/phrases**, not substrings. `ai` matches `AI Engineer`
  and `AI/ML`, but not `said` or `maintenance`.
- A job matches when a category hits; hard exclusions (company or role) disqualify it.
- The score is the **share of active categories hit**, from 0 to 100. It is never a
  black-box ranking.
- Location is a hard filter when set. Country aliases and remote flags are normalized
  through a geo index, so `UAE`, `United Arab Emirates`, and `Dubai` can align.
- Every match stores `matched_on` reasons (e.g. `role:backend`, `keyword:python`) so the
  UI can explain itself.
- Preference saves trigger a Postgres `recompute_job_matches()` call for parity with the
  Python matcher.

Empty lists match everything. Matching runs per source as soon as that source's jobs are
upserted, so one slow board does not delay every user's alerts.

The full rationale, scoring examples, and the SQL/Python parity discussion are in
[Design Decisions](docs/DESIGN_DECISIONS.md#56-matching).

---

## Notifications

Ingestion creates **intents**, not messages:

```text
new job → job_matches → notification_queue (scheduled_for = now + user delay)
                              │
                    drain worker every ~30s
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
              Telegram send      (email legacy)
                    │
              retry up to 3
                    │
              notifications_sent ledger
```

Guarantees and limits:

- `UNIQUE(user_id, job_id, channel)` prevents duplicate intents and duplicate sends.
- Delivery is **at-least-once with idempotency**, not exactly-once.
- Failed sends retry up to 3 times, then become `failed` with the last error recorded.
- Each user has an `alert_delay_minutes` setting; changing it affects future intents only.
- The first poll of a source is treated as backfill and **never alerts** — otherwise a new
  company would flood every matching user with its entire history.
- Telegram delivery is paced (~25 messages/sec sustained, burst 30) to stay under the
  platform limit.
- **Email is legacy.** The current pipeline enqueues Telegram only; the Resend email code
  is retained for tooling and possible future use.

Telegram setup: create a bot with `@BotFather`, message it once, put the token and chat ID
in `backend/.env`, and set `TELEGRAM_ENABLED=true`. Set the bot username to enable
Telegram login/deep links, and a public HTTPS URL to enable the Mini App.

---

## API

`http://localhost:8000/docs` exposes the full interactive OpenAPI reference. The app
currently registers **77 endpoints plus `/health`**:

| Prefix | Endpoints | Purpose |
|---|---:|---|
| `/api` (`routes.py`) | 26 | Dashboard: stats, jobs, matches, companies, sources, poll runs, schedule, preferences, notifications, geo, location mapping |
| `/api/auth` | 11 | Register, password login/logout, profile, password change, export, delete, Telegram linking |
| `/api` (`access_routes.py`) | 9 | Plans, coupons, checkout, Razorpay create/verify/cancel, webhook |
| `/api/public` | 5 | No-auth jobs, filters, job detail, companies, schema |
| `/api/admin` | 26 | Users, roles/capabilities, coupons, presets, subscriptions, billing events, egress, schema, observability |

Access rules:

- Public endpoints are unauthenticated and rate-limited/limited by query caps.
- Dashboard endpoints require a valid session cookie in production.
- Admin endpoints require the `admin` role or owner.
- `JOBQUEST_REQUIRE_AUTH=false` is a compatibility mode for local single-user work:
  anonymous requests act as the owner. Never ship that mode publicly.

Health and readiness:

```bash
curl http://localhost:8000/health
```

---

## Scheduling and operations

APScheduler runs inside the application (or the worker) in the `Asia/Kolkata` timezone:

| Job | Default interval | Purpose |
|---|---|---|
| `poll-<ats>` | 3600 s, jitter ±120 s | One poll per ATS family, configurable live via the dashboard. |
| `poll-all-integrity` | 43,200 s (12 h) | Full sweep, including quiet boards and unhealthy sources. |
| `notify-drain` | ~30 s | Deliver due notification intents. |
| `subscription-sweep` | Daily at 03:17 | Expire ended subscriptions. |
| `stall-watch` | 600 s | Page the owner if no poll completes within 70 minutes. |

Operational protections:

- **Advisory locks** (`pg_try_advisory_lock`) serialize each ATS poll and the global
  sweep across processes. A second scheduler is harmless.
- **Quiet-board backoff** polls healthy boards with 5+ consecutive no-new runs every third
  interval. Manual and global runs still poll everything.
- **Source health** records the last error, HTTP status, error type, duration, and quiet
  runs. `GET /api/sources/unhealthy` and the Runs page surface degraded boards.
- **Lifecycle** reactivates reposted jobs, touches `last_seen_at` at most once per 24 h,
  and deactivates jobs unseen for 72 h. Inactive rows are retained 7 days for context.
- **Retention** deletes jobs by `first_seen_at` after 30 days, matches after 24 h, sent
  ledger rows after 24 h, auth events after 90 days, and rate events after 24 h.
- **Stale-run recovery** on startup clears orphaned `running` rows from crashed processes.
- **Migrations** apply automatically and retry the initial connection for up to 300 s
  while Postgres finishes WAL recovery.

---

## Project layout

```text
jobRadar/                          repository; product is branded JobQuest
├── backend/
│   ├── app/
│   │   ├── adapters/               one isolated module per ATS (24)
│   │   ├── api/                    auth, access, public, dashboard, admin routers
│   │   ├── telegram/               bot, messages, notifications
│   │   ├── auth.py                 sessions, passwords, rate limiting
│   │   ├── access.py               coupons, subscriptions, Razorpay
│   │   ├── entitlements.py         roles, capabilities, access gates
│   │   ├── matcher.py              deterministic matching
│   │   ├── notification_queue.py   queue, delays, retries, drain
│   │   ├── poller.py               ingestion pipeline
│   │   ├── main.py                 FastAPI app, lifespan, scheduler
│   │   └── worker.py               scheduler + bot without HTTP
│   ├── migrations/                 64 raw SQL migrations
│   ├── tests/                      4 suites + 17 fixture directories
│   ├── sources.json                ~2,519 company boards
│   ├── run_poll.py                 one-shot CLI poll
│   ├── Dockerfile                  Python 3.13 slim image
│   └── .env.example                configuration reference
├── frontend/
│   ├── app/                        public, auth, dashboard, admin, legal routes
│   ├── components/                 landing, Ink dashboard, job cards, gates
│   ├── lib/                        API client, auth context, types, storage, format
│   └── test/                       4 Vitest suites
├── docs/                           design decisions, codebase map, historical plans
├── .github/workflows/ci.yml        lint + tests
├── docker-compose.yml              local dev stack
├── docker-compose.prod.yml         API + worker production override
├── render.yaml                     single-service Render blueprint
└── AGENTS.md                       architecture intent and contributor rules
```

---

## Testing and CI

```bash
# Backend — offline, no live sites or database
cd backend
ruff check .
ruff format --check .
python -m pytest tests/test_unit.py tests/test_subscription_unit.py tests/test_public_filters.py -q

# Backend — live API suite (requires backend/.env with a real database)
python -m pytest tests/test_api.py -q

# Frontend
cd frontend
npm test            # vitest run
npx tsc --noEmit    # no ESLint config exists; use the TypeScript checker
```

Coverage at a glance:

- ~207 offline backend tests, including matcher behavior, adapter parsing, billing,
  entitlements, coupon atomicity, geo aliases, and public filters.
- 19 live API tests, gated behind real credentials.
- 24 frontend tests across 4 suites: API client, formatting, local job storage, and
  legal/privacy guards.
- 17 saved ATS fixture directories, so adapters do not depend on live career sites.
- CI runs Ruff lint/format, offline backend tests, and Vitest on every push to `main` and
  every pull request. API tests run only when the `RUN_API_TESTS` repository variable is
  enabled and Supabase secrets are configured.

---

## Deployment

### Docker Compose (API + worker)

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

The production override:

- serves the API without hot reload or host mounts,
- disables the scheduler and bot in the API process,
- runs `python -m app.worker` as a separate service that owns polling and Telegram.

This separation exists because a Workday poll can take minutes. Keeping it out of the API
process protects `/health`, manual runs, and dashboard requests.

### Render

`render.yaml` deploys a single Docker web service running the backend with the scheduler
and bot in-process. Point it at your Supabase/Postgres credentials and set the notification
variables. Migrations run on first start; `/health` is the health check.

### Backups

There is no automatic off-site backup today. Before treating a deployment as production,
add a nightly `pg_dump --format=custom` to object storage (or a second host) and rehearse a
restore. A dump you have never restored is not a backup.

---

## Security and privacy

- Secrets live in environment variables; `backend/.env` is gitignored and never baked into
  images. `.env.example` contains placeholders only.
- The Supabase **service-role** key and `DATABASE_URL` stay server-side.
- Passwords use PBKDF2-HMAC-SHA256 with 600,000 iterations and constant-time comparison.
- Sessions are HMAC-SHA256 signed, httpOnly cookies (`__Host-` prefixed in secure mode),
  with configurable TTL and login lockout after repeated failures.
- Rate limiting is DB-backed (`rate_events`) with an in-memory fallback for tests.
- All dashboard and admin authorization is enforced server-side; client guards are UX only.
- Registration is 18+ and validates password strength, email shape, display names, and
  consent. Account export and deletion are supported.
- The public API exposes only projected job fields and caps result sizes.
- Frontend fonts are self-hosted to avoid third-party font requests; a frontend test bans
  CDN font links and session-replay/keystroke trackers.
- External data is untrusted: adapters use timeouts, retries, and response validation;
  the app does not bypass CAPTCHAs, authentication, or anti-bot controls.

Operational notes:

- `JOBQUEST_REQUIRE_AUTH=false` is a **local compatibility mode** where anonymous requests
  act as the owner. Keep it `true` for anything reachable from the internet.
- There is no row-level security because all data access is server-side. Authorization is
  enforced in FastAPI and SQL, not delegated to the database.
- Legal pages are present, but entity/contact/address placeholders must be filled before
  a real commercial launch.

---

## Status and roadmap

**Shipped and running:** ingestion across 24 adapters, 2,519 configured boards, matching,
Telegram alerts, public browsing, multi-user auth, subscriptions and coupons, admin tools,
per-user delays, lifecycle tracking, source health, automatic migrations, CI, and tests.

**Known debt and next steps** (detailed in [Design Decisions](docs/DESIGN_DECISIONS.md#9-known-limitations-and-debt)):

1. Consolidate duplicate `recompute_job_matches` SQL overloads so preference-save and
   Python matching always use the same whole-word semantics.
2. Make Razorpay webhook processing short-circuit duplicate provider events before
   side effects (currently deduplicated in storage, not at the entry point).
3. Add off-site backups + a rehearsed restore, Sentry/uptime monitoring, and alerting.
4. Decide the email question: finish production email (SPF/DKIM/DMARC, unsubscribe,
   bounce handling) or remove the legacy code and docs.
5. Fix the `auth_events` check constraint for `account_delete`, and add the missing
   `RAZORPAY_*` variables to `.env.example`.
6. Add frontend component/E2E and accessibility tests; add an ESLint config.
7. Harden the Docker frontend build with `npm ci` and the lockfile.
8. Continue the 10k-user plan: Telegram pacing telemetry, 90-day sent retention,
   connection/egress monitoring, and a tested 2,000-user alert burst.

---

## Documentation

| Document | What it covers |
|---|---|
| **[docs/DESIGN_DECISIONS.md](docs/DESIGN_DECISIONS.md)** | The full engineering story: every major decision, tradeoffs, rejected alternatives, measurements, failure analyses, scaling plan, and interview Q&A. |
| [docs/CODEBASE_MAP.md](docs/CODEBASE_MAP.md) | The actual implemented state: real routes, adapters, tables, pages, pipelines, and gotchas. |
| [AGENTS.md](AGENTS.md) | Product vision, architecture principles, and rules for AI-assisted development. |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Setup, code style, adapter checklist, PR rules. |
| [CHANGELOG.md](CHANGELOG.md) | Release history. |
| [docs/](docs/) | Historical plans for auth, subscriptions, egress, hosting, and adapters. |
| [DESIGN.md](DESIGN.md) | Visual design system. |

> Planning documents are historical records. When code and docs disagree, trust
> `docs/CODEBASE_MAP.md` and the source.

---

## Contributing

Read [AGENTS.md](AGENTS.md) and [CONTRIBUTING.md](CONTRIBUTING.md) first. The short
version:

1. One logical change per pull request.
2. Adapters stay isolated: fetch, parse, normalize, return. No matching, no notifications.
3. Deterministic and explainable beats fuzzy and clever.
4. New behavior ships with tests.
5. Never commit secrets.
6. `main` is protected; CI must be green; changes land through pull requests.

```bash
cd backend && ruff check . && ruff format --check . && python -m pytest tests/test_unit.py
cd frontend && npm test
```

---

## License

Licensed under the [Apache License 2.0](LICENSE).

<div align="center">
  <sub>Built to make the job market a little less noisy.</sub>
</div>
