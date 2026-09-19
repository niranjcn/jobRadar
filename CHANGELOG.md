# Changelog

All notable changes to jobQuest are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Emirates Group adapter (`emirates` ATS type) using the official public JSON
  API at `emiratesgroupcareers.com/api/v1/jobs`; source auto-detection for
  `emiratesgroupcareers.com` URLs; `Emirates Group` added to `sources.json`.
- Public jobs API (`/api/public/jobs`, `/api/public/jobs/filters`,
  `/api/public/jobs/{id}`) with keyword, company, country, source, posted-date,
  and remote-only filters — no login required.
- Public `/browse` jobs page (plus `/browse/[id]` detail) with every available
  filter; filters persist across refresh via URL query params + localStorage.
- GitHub Actions CI (ruff lint + format, backend unit tests, frontend tests).
- Pull request and issue templates; `CONTRIBUTING.md` and `CHANGELOG.md`.

### Changed

- License switched to Apache-2.0.
- Backend lint policy codified in `pyproject.toml` and applied across the
  codebase (ruff, deterministic and pinned).

### Planned

- AI-assisted job matching (post-deterministic).
- Multi-user support and API authentication.
- Frontend polish and additional adapters.

## [0.1.0] - 2026-08-16

Initial release — foundation, ingestion, matching, and notifications.

### Added

- **Backend (FastAPI)**
  - Automatic schema migrations on startup (`backend/migrations/`, 020 files)
    with a `schema_migrations` tracking table.
  - Source registry synced from `backend/sources.json` into Supabase.
  - Health endpoint and 25 REST endpoints for the dashboard
    (`/api/stats`, `/api/jobs`, `/api/sources`, `/api/schedule`,
    `/api/preferences`, `/api/notifications`, geo/location mapping, and more).
  - Source auto-detection for unknown career-page URLs (`/api/sources`).

- **Source adapters (10 ATS)**
  - Greenhouse, Lever, Ashby, Workday, Oracle, iCIMS, SAP SuccessFactors,
    Phenom, Avature, and a generic `custom` adapter.
  - Normalization into a common `Job` model; source-specific data kept in
    JSON metadata.

- **Ingestion pipeline**
  - Fetch → parse → validate → normalize → deduplicate → upsert.
  - DB-level dedup on `(source_id, external_job_id)` with unique constraints.
  - Incremental job-description fetching for newly seen jobs (5 concurrent
    requests).
  - Per-source failure isolation — a failing source never blocks the rest.
  - Job retention and max-posting-age windows.

- **Scheduling**
  - In-app APScheduler with one poll job per ATS type; configurable per-ATS
    intervals (env vars or dashboard), plus a 12-hour full integrity sweep.
  - Poll-run tracking, stale/orphaned run recovery, and source health.
  - `run_poll.py` one-shot entrypoint for manual runs.

- **Matching & preferences**
  - Deterministic matcher over roles, keywords, locations, seniority, and
    excluded companies/roles.
  - Geo mapping (`geo_index.json`) with country normalization, remote
    handling, and customizable aliases.

- **Notifications**
  - Telegram via Bot API (all new jobs or preference matches only).
  - Email via Resend (matched jobs), async and channel-independent.
  - Idempotent delivery tracked in `notifications_sent` by `(job_id, channel)`.

- **Frontend (Next.js 15 + Tailwind)**
  - Dashboard, jobs, matches, new-jobs, new-matches, companies, sources,
    preferences, runs, schedule, notifications, and settings pages.

- **Infrastructure**
  - `docker-compose.yml` local stack (poll + web + frontend) with live reload.
  - `render.yaml` blueprint for deploying the backend as a Render web service.
  - Backend and frontend test suites (pytest + Vitest) using saved fixtures.

### Security

- All secrets read from environment variables; `.env` files gitignored and
  excluded from Docker builds.
- `.env.example` ships with placeholders only; `service_role` keys and DB
  credentials never touch the frontend.