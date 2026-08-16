# jobRadar

[![CI](https://github.com/niranjcn/jobRadar/actions/workflows/ci.yml/badge.svg)](https://github.com/niranjcn/jobRadar/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org/)

Personal job-alert system that continuously polls company career pages, stores
job postings in Supabase/Postgres, matches them against your preferences, and
alerts you via Telegram and email.

It is built to work across many applicant-tracking systems (ATSs) through
isolated source adapters, so the core application never cares where a job came
from. The full product plan and phased build order live in `AGENTS.md`.

## Features

- **10 ATS adapters** — Greenhouse, Lever, Ashby, Workday, Oracle, iCIMS,
  SAP SuccessFactors, Phenom, Avature, and a generic `custom` adapter for
  plain JSON/HTML career pages.
- **Automated ingestion** — per-ATS polling schedules (APScheduler), job
  normalization, deduplication via `(source_id, external_job_id)`, and
  incremental job-description fetching.
- **Deterministic matching** — role, keyword, location, seniority, and
  exclude-company filters plus country/remote geo mapping. Explainable,
  no LLM required.
- **Notifications** — Telegram (Bot API) and email (Resend), with idempotency
  so a job is never alerted twice.
- **Dashboard** — Next.js UI for browsing jobs, matches, sources, runs,
  schedule, preferences, settings, and notifications.
- **Self-healing** — source health tracking, stale-run recovery, per-source
  failure isolation, and automatic database migrations on startup.

## Repository layout

```
backend/               # FastAPI app + poll worker + Docker image
  app/                 # application package (config, db, adapters, matcher, poller, API)
  app/adapters/        # one module per ATS (isolated from business logic)
  app/api/             # REST endpoints for the dashboard
  migrations/          # raw SQL schema — applied AUTOMATICALLY on startup
  scripts/             # one-off dev/research scripts
  tests/               # pytest suite + saved source fixtures
  sources.json         # your company list — add companies here
  run_poll.py          # one-shot poll entrypoint (manual runs / testing)
  .env.example         # copy to .env and fill in values
  Dockerfile
frontend/              # Next.js dashboard (App Router, Tailwind, Vitest)
docker-compose.yml     # local orchestration (poll + web + frontend)
render.yaml            # Render blueprint for the backend web service
AGENTS.md              # architecture guide + agent instructions
```

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) + Docker Compose
- A [Supabase](https://supabase.com) project (free tier is fine)
- Optional: a [Telegram](https://core.telegram.org/bots) bot and/or a
  [Resend](https://resend.com) API key for notifications

## Setup

1. Copy `backend/.env.example` to `backend/.env` and fill in the values:
   - `SUPABASE_URL` — your project URL
   - `SUPABASE_KEY` — the **service_role** key (bypasses RLS; the app needs it
     to write). Keep it server-side only — never in frontend/browser code.
   - `DATABASE_URL` — the Postgres **URI connection string** from Supabase
     Dashboard → Project Settings → Database. Use your database password (not
     the service role key). URL-encode special characters (e.g. `@` → `%40`).
2. Done — **no manual SQL needed.** On startup the app runs any pending files
   in `backend/migrations/` (tracked in a `schema_migrations` table) and syncs
   `sources.json` into the `sources` table.

## Running with Docker

```sh
docker compose build

# Run the poll once manually (one-shot sweep over all active sources)
docker compose run --rm poll

# Run the full stack: web API + scheduler + frontend dashboard
docker compose up -d
```

Secrets are read from `backend/.env` at runtime (not baked into the image).
Without it, both services fail with a clear "missing required env vars"
message.

### Live reload in dev

`backend/` and `frontend/` are bind-mounted into the containers and both
servers run with hot reload, so code changes take effect without rebuilding:

- `web` runs `uvicorn --reload` — editing a Python file restarts it.
- `frontend` runs `next dev` — editing a TSX/TS file hot-reloads the page.
- `poll` is one-shot (`docker compose run --rm poll`), so it always runs the
  latest code.

Only dependency changes need a rebuild (and force-recreate the anonymous
frontend volumes so the fresh install is used):

```sh
docker compose up --build -V web frontend
```

## Scheduling (in-app)

The scheduler lives inside the FastAPI app: on startup it starts an
APScheduler loop with one job per ATS type. Intervals are configurable per
ATS (`POLL_INTERVAL_<ATS>_SECONDS`, defaults in `app/config.py`) and can be
tweaked live from the dashboard. A full integrity sweep runs every 12 hours.

- Runs are serialized per ATS, so a slow sweep never overlaps the next one.
- A failure in one source is logged and doesn't stop the loop.
- If the process restarts, orphaned `running` rows are cleaned up and polling
  resumes immediately.
- Set `JOBRADAR_DISABLE_SCHEDULER=1` to run the API without any scheduled
  polling (e.g. when an external cron handles it).

## Adding a company

Edit `backend/sources.json` and add an entry — no code, no SQL:

```json
[
  { "company_name": "Stripe", "ats_type": "greenhouse", "board_identifier": "stripe" },
  { "company_name": "GitLab", "ats_type": "greenhouse", "board_identifier": "gitlab" }
]
```

On the next poll run (or app restart), the entry is upserted into the
`sources` table and polled automatically. Fields:

- `company_name` — any name you'll recognize (must be unique)
- `ats_type` — `greenhouse` | `lever` | `ashby` | `workday` | `oracle` |
  `icims` | `successfactors` | `phenom` | `avature` | `custom`
- `board_identifier` — the ATS-specific slug/URL for this company
- `active` — optional, defaults to `true`; set `false` to pause a company
  without deleting its data

Greenhouse boards live at
`https://boards-api.greenhouse.io/v1/boards/{slug}/jobs` — the slug is usually
the lowercase company name. Unknown URLs can be probed via
`POST /api/sources` (the `detect_source` endpoint identifies the ATS).

## Preferences & matching

Preferences are set via env vars (`PREF_ROLES`, `PREF_KEYWORDS`,
`PREF_LOCATIONS`, `PREF_SENIORITY`, `PREF_EXCLUDED_COMPANIES`,
`PREF_EXCLUDED_ROLES` in `backend/.env.example`) or through the dashboard
(`/preferences`). A job matches when its title/description/location matches
any listed value per category; empty lists match everything. "remote" as a
location also matches jobs whose location contains "remote", and the geo
mapping (see `/settings/location-mapping`) normalizes countries/aliases.

## Notifications

Notifications are independent of ingestion — a failure in one channel never
blocks the other, and `notifications_sent` dedupes by
`(job_id, channel)`.

- **Telegram** (`TELEGRAM_ENABLED=true`, `TELEGRAM_BOT_TOKEN`,
  `TELEGRAM_CHAT_ID`) — every new posting, or only preference matches
  (dashboard → Preferences → Telegram scope). Send `/start` to your bot to get
  a welcome message; the app long-polls for it (a webhook on the bot would
  stop that loop).
- **Email** (`NOTIFY_ENABLED=true`, `RESEND_API_KEY`, `NOTIFY_TO`) — Resend
  test mode sends to the address you signed up with; verify a domain in
  Resend to send elsewhere.

## API

FastAPI app with docs at `http://localhost:8000/docs`. Main endpoints:

```
GET    /health
GET    /api/stats
GET    /api/jobs            GET /api/jobs/{id}
GET    /api/matches/jobs    GET /api/matches/summary
GET    /api/companies
GET    /api/sources         POST /api/sources  PATCH /api/sources/{id}
GET    /api/sources/unhealthy
POST   /api/sources/{id}/run
POST   /api/poll/run        POST /api/poll/run-unhealthy
GET    /api/poll/runs
GET    /api/schedule        PUT/DELETE /api/schedule/{ats_type}
GET    /api/preferences     PUT /api/preferences
GET    /api/notifications
GET    /api/geo/countries
GET/PUT /api/settings/location-mapping
POST   /api/settings/location-mapping/preview
```

Auth is intentionally out of scope for now — this is a single-user,
self-hosted system and secrets stay server-side. Lock it down (reverse proxy
auth, VPN, or Supabase auth) before exposing it to the internet.

## Tests

```sh
# Backend (pytest, uses saved fixtures — no live sites needed)
cd backend && python -m pytest

# Frontend (Vitest)
cd frontend && npm test
```

## Deploying to Render

`render.yaml` deploys the backend as a Render **Web Service** (Docker). The
hourly per-ATS poll loops run inside the process — no cron service needed.
Set `SUPABASE_URL`, `SUPABASE_KEY`, `DATABASE_URL` and your notification env
vars as Render env vars (`sync: false` entries are filled in the dashboard).
Migrations apply automatically on first start.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Architecture guidance for AI-assisted
development is in [AGENTS.md](AGENTS.md).

## License

[MIT](LICENSE)