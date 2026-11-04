# Codebase Map — actual implemented state

Last verified: 2026-11-04, branch `feature/lifecycle-ingestion-access`, HEAD `e93a4f1`.

Purpose: AGENTS.md describes the *intended* architecture from early planning. This file maps
*what is actually in the repo right now* — real routes, adapters, tables, pages, pipelines, and
work in progress. Read this before starting a task; update it when files move or behavior changes.

## Quick commands

```powershell
# Backend lint + tests (offline, no live sites/DB)
cd backend; ruff check .; ruff format --check .; python -m pytest tests/test_unit.py -q

# Frontend tests
cd frontend; npm test          # vitest run

# Frontend typecheck (no eslint config exists — `npm run lint` would prompt for setup)
cd frontend; npx tsc --noEmit
```

Full API tests (`backend/tests/test_api.py`) need a real `.env` DB and run a local uvicorn on
127.0.0.1:8100 with scheduler + bot disabled.

## Repo layout

```
jobRadar/                      (branded "JobQuest"; delta is cosmetic)
├── backend/                   FastAPI + poller + scheduler + Telegram bot (Python 3.13 Docker)
├── frontend/                  Next.js 15 + React 19 + Tailwind 3 + Vitest
├── docs/                      design decisions + this map + plans (10k-hosting, subscription, egress, etc.)
├── docker-compose.yml         dev stack (postgres, postgrest, web, frontend; poll/worker opt-in)
├── docker-compose.prod.yml    prod override: API-only web + worker service
├── render.yaml                Render deploy (single web service, hourly loops in-process)
├── .github/workflows/ci.yml   ruff + unit tests + vitest on push(main)/PR
└── AGENTS.md                  design intent (partly stale — see "Stale docs" below)
```

## Backend map

Entry points:
- `backend/app/main.py` — FastAPI app + lifespan (migrations → owner bootstrap → scheduler + bot) + `/health`.
- `backend/app/worker.py` — standalone scheduler + bot process, no HTTP (used by prod compose).
- `backend/run_poll.py` — one-shot CLI poll (`docker compose run --rm poll`).

### API routers (77 endpoints total + /health)

| File | Prefix | Count | Purpose |
|---|---|---|---|
| `app/api/routes.py` | `/api` | 26 | Dashboard: stats, jobs, matches, companies, sources CRUD/run, poll runs, schedule, preferences, notifications, geo countries, location mapping |
| `app/api/auth_routes.py` | `/api/auth` | 11 | register/login-password/logout, profile, password, me, me/export, me/delete, telegram-chat-id |
| `app/api/access_routes.py` | `/api` | 9 | presets, plans, coupons/redeem, billing checkout/portal, Razorpay create/verify/cancel, webhook |
| `app/api/public_routes.py` | `/api/public` | 5 | no-auth jobs/filters/detail, companies, schema (limit capped 100) |
| `app/api/admin_routes.py` | `/api/admin` | 26 | users CRUD/actions, coupons, presets, subscriptions, billing-events, egress, schema, db-observability, stats (whole router admin-gated) |

`app/api/detect.py` is a helper (ATS auto-detection), not a router.
All dashboard/admin/billing endpoints go through `get_current_user` / `get_current_admin`; in
compat mode (`JOBQUEST_REQUIRE_AUTH` unset) anonymous = owner (see Gotchas).

### Adapters — `backend/app/adapters/` (24 ATS + custom)

Interface: `base.py::JobSourceAdapter.fetch_jobs(board_identifier, client) -> list[NormalizedJob]`;
registry `__init__.py::adapter_for(ats_type)`; shared retrying httpx client `http.py::RetryingClient`.

Implemented: greenhouse, lever, ashby, workday, oracle (Taleo + Fusion), icims, successfactors,
phenom, avature, amazon, google, remotive, weworkremotely, workable, smartrecruiters, breezy,
jobvite, jazzhr, bamboohr, teamtailor, rippling, eightfold, custom (J2W), emirates.

Source registry: `backend/sources.json` (~2,519 sources; workday 618, greenhouse 513, ashby 241,
workable 195, smartrecruiters 171, lever 138, oracle 138, ...). Synced to DB via `sync_sources`.

### Ingestion pipeline (`app/poller.py`, 1,132 lines)

`sync_sources` → per-ATS advisory lock (`pg_try_advisory_lock('poll-{ats|global}')`) →
`prune_old_jobs` → `fetch_sources` → backoff filters (`mark_error`/404 12h, quiet-board: 5 quiet
runs → poll every 3rd) → shared client + `asyncio.gather` per source (per-ATS semaphores from
`config.ATS_CONCURRENCY`) → adapter fetch/parse → `map_location` + 90-day age filter →
`dedupe_rows` → `upsert_jobs_returning` (chunks of 500, `ON CONFLICT (source_id, external_job_id)`,
new ids via `(xmax = 0)`) → lifecycle txn (`reactivate_jobs`, `touch_seen_jobs` 24h,
`sweep_missing_jobs` 72h, `mark_checked`) → `match_and_enqueue` (skip on first-ever poll) →
`drain_due_notifications` → `finish_poll_run`.

### Matching + notifications

- `app/matcher.py` — deterministic; whole-word regex matching (`term_matches_text`), scoring =
  share of active categories hit; hard exclusions for companies/roles; preference saves trigger
  Postgres `recompute_job_matches()` (parity with SQL via migration 064 `term_matches()`).
- `app/notification_queue.py` — per-user alert delay (`app_settings` privileged/normal tier
  minutes, default 10/10), upsert `job_matches`, enqueue `notification_queue`, drain with retry
  (max 3), per-(user, job, channel) idempotency.
- **Telegram is the only live channel.** Email (`app/notify.py`, Resend) is legacy code used only
  by `send_test_notification.py`; email queue rows are canceled at drain.
- `app/telegram/bot.py` — long polling, commands: `/start /help /stats /jobs /newjobs /matches
  /newmatches /companies /sources /schedule /runs /notifications /preferences /app`, inline mode.
- `app/ops.py` — scheduler stall detector (70-min window) pages owner via Telegram.

### Database

- Client: **both** `psycopg 3` (`app/db.py`: sync pool + `query()`, async pool + `query_async`)
  for SQL, and supabase-py PostgREST (`get_supabase()`) for table CRUD. No ORM/Alembic.
- Migrations: `backend/migrations/*.sql`, 001–065 (no 057), 64 files; runner `app/migrate.py`
  (`schema_migrations`, auto-applies at API/worker/poll startup, retries the initial connect
  for up to 300s while Postgres finishes WAL recovery — `MIGRATION_CONNECT_WAIT_SECONDS`).
- Main tables: `sources`, `jobs`, `job_matches`, `preferences`, `notification_queue`,
  `notifications_sent`, `poll_runs`, `poll_schedule`, `plans`, `subscriptions`, `coupon_codes`,
  `billing_events`, `users`, `auth_events`, `rate_events`, `app_settings`, `preference_presets`.
- Key constraints: `UNIQUE(source_id, external_job_id)` on jobs; PK `(user_id, job_id)` on
  job_matches; `UNIQUE(user_id, job_id, channel)` on queue + sent ledger.
- Note: `jobs.description` was dropped; `NormalizedJob.to_row()` persists only id fields, title,
  location, url, countries, is_remote.

### Auth, billing, entitlements

- Auth (`app/auth.py`, `app/users.py`): HMAC-SHA256 signed session cookies (`jobquest_session`,
  `__Host-` prefixed when `SESSION_COOKIE_SECURE`), PBKDF2-SHA256 600k, login lockout 5/15min,
  DB-backed rate limiting (`rate_events`), audit `auth_events` (90d prune), `validate_date_of_birth` (18+).
- Billing (`app/access.py`, `app/entitlements.py`): provider switch `BILLING_PROVIDER`
  (`manual` default | `razorpay`); coupons `JR-XXXX-XXXX` 12h TTL; Razorpay autopay subscription →
  verify → `provision_subscription` (+30d) → unlock → recompute; webhook idempotent via
  `billing_events`; daily 03:17 sweep expires subscriptions. Plan: `standard` ₹49/mo (migration 063).
- Regular users gated on: approved + unlocked + active subscription; `privileged`/`admin` bypass.

### Scheduler (`app/main.py::_build_scheduler`, timezone Asia/Kolkata)

Per-ATS `poll-{ats}` (IntervalTrigger, default 3600s, jitter 120) → `poll-all-integrity` 12h →
`notify-drain` every ~30s → `subscription-sweep` daily 03:17 → `stall-watch` every 10min.
Live interval changes via `PUT /api/schedule/{ats_type}` → `reschedule_ats` (stored in `poll_schedule`).
`JOBQUEST_DISABLE_SCHEDULER=1` / `JOBQUEST_DISABLE_BOT=1` disable them (prod: worker owns both).

### Config + tests

- `app/config.py` env names: `SUPABASE_URL/KEY`, `DATABASE_URL`, `POLL_INTERVAL_{ATS}_SECONDS`,
  `POLL_CONCURRENCY_{ATS}`, `PREF_*`, `SECRET_KEY`, `JOBQUEST_REQUIRE_AUTH`, `SESSION_TTL_HOURS`,
  `SESSION_COOKIE_SECURE`, `BILLING_PROVIDER`, `RAZORPAY_*`, `TELEGRAM_*`, `ADMIN_CHAT_ID`,
  `RESEND_API_KEY`, `NOTIFY_ENABLED`, `APP_BASE_URL`, `POSTAL_ADDRESS`, `CORS_ORIGINS`, `JOB_RETENTION_DAYS`.
- Tests: `tests/test_unit.py` (~167 offline), `test_subscription_unit.py` (21), `test_public_filters.py` (19),
  `test_api.py` (19, live DB). Fixtures: `tests/fixtures/` (17 ATS dirs). Deps: fastapi, uvicorn,
  apscheduler<4, supabase, httpx, psycopg[binary,pool], razorpay; ruff pinned 0.16.3.

## Frontend map (`frontend/`)

Stack: Next 15.1.6, React 19, TypeScript 5.7, Tailwind 3.4, Vitest 4. No middleware; all
auth/route protection is client-side gates + backend.

Public routes: `/` (landing), `/browse`, `/browse/[id]`, `/login`, `/register`, `/pending`,
`/pricing`, `/unlock`, `/schema`, `/contact`, `/dmca`, `/terms`, `/privacy`, `/refund` (legal pages
via `components/legal-shell.tsx`).

Dashboard `(app)/` (all inside `AuthGate` + `InkShell`): `/dashboard`, `/jobs`, `/jobs/[id]`,
`/new-jobs`, `/matches` (only page in `PaywallGate`), `/companies`, `/notifications`,
`/preferences`, `/billing`, `/onboarding`, `/sources`, `/schedule`, `/runs`, `/timings`, `/settings`.

Admin `/admin/*` (`AdminGuard`): overview, `/users`, `/coupons`, `/presets`, `/egress`, `/schema`.

Key components: `components/ink/` is the dashboard design system (InkShell, InkSidebar — nav
arrays, `ui.tsx` primitives, `overview.tsx` dashboard widgets, `ink.module.css` dark purple glass);
`components/landing/jobquest-landing.tsx` is the public landing; gates in
`components/auth-gate.tsx` + `paywall-gate.tsx`; `job-card.tsx`, `country-select.tsx`,
`company-select.tsx`, `company-logo.tsx`.

`lib/`: `api.ts` (all REST calls, `credentials: "include"`, base `NEXT_PUBLIC_API_URL` default
`http://localhost:8000`; `next.config.mjs` also rewrites `/api/:path*` to it), `auth-context.tsx`
(`useAuth` via `api.me()`), `job-store.ts` (localStorage saved/hidden/applied), `format.ts`,
`types.ts`, `referral.ts`.

Styling: two systems — "Warm Editorial" (public pages, `app/globals.css`) and "Ink" dark glass
(dashboard, scoped under `.ink`). Fonts self-hosted via `next/font` (CDN links forbidden, enforced
by `test/legal-guards.test.ts`). Tests: `api.test.ts`, `format.test.ts`, `job-store.test.ts`,
`legal-guards.test.ts`. Legacy/unused: `components/sidebar.tsx`, `components/stat-card.tsx`.

## Infra / CI / review

- Dev: `docker compose up -d` (postgres + postgrest + web with reload + frontend dev; `poll` and
  `worker` are opt-in profiles). Prod: `-f docker-compose.prod.yml` (web API-only, worker owns
  scheduler + bot). Windows dev needs the watchfiles polling envs already set in compose.
- Render: single `jobquest` web service (Docker, backend/Dockerfile, health `/health`).
- CI (`ci.yml`): backend ruff check + format + `pytest tests/test_unit.py` (Python 3.12); optional
  API tests (repo var `RUN_API_TESTS`, needs Supabase secrets); frontend `npm ci && npm test`. Node 20.
- Review: CODEOWNERS → @niranjcn; PR template + CodeRabbit assertive/review-requested; Dependabot weekly.

## Current working state (2026-10-19)

Branch `feature/lifecycle-ingestion-access`, 5 commits ahead of origin/main (last 5 pushed commits:
whole-word matcher, ₹49 plan, refund/privacy pages, geo aliases). All CI inputs green per PR draft.

Uncommitted WIP — a legal/regulatory compliance pass (not yet committed):
- **Age gate**: `validate_date_of_birth` in `auth.py`, `date_of_birth` in register route/users,
  migration `065_age_gate.sql` (untracked), register page DOB input + client validation, +7 tests.
- **CAN-SPAM email compliance**: `APP_BASE_URL` + `POSTAL_ADDRESS` config, List-Unsubscribe header
  and footer with manage/preferences link in email builder, visible placeholder when unconfigured,
  "Email alerts" opt-out toggle on preferences page, auto-renewal disclosures on billing/pricing/unlock.
- **DMCA**: new `app/dmca/page.tsx` (untracked), `dmcaEmail` placeholder in legal-shell, links from
  footers and privacy/terms sidebars.
- **Legal guards test**: `frontend/test/legal-guards.test.ts` (untracked) bans CDN font links and
  session-replay vendors.
- Also modified: `backend/.env.example`, `notify.py`, `telegram/messages.py`, `send_test_notification.py`,
  several frontend legal/auth pages. `pr_description.md` (untracked) is the PR draft for this arc.

Other local branches are fully merged into origin/main; local `main` ref is stale (behind by ~172
commits) — always `git fetch origin` before comparing/branching (see AGENTS.md §23).

## Stale docs + gotchas

- README was refreshed on 2026-11-04 and now reflects auth, billing, and 24 adapters.
  `docs/DESIGN_DECISIONS.md` is the interview/deep-dive companion; prefer code + this map
  when they disagree. CHANGELOG stops at 0.1.0 (2026-08-16); PR drafts in
  `pr_description.md` are the most current narrative. `ARCHITECTURE_REVIEW.md` is gitignored,
  local-only; its C1 (unauthenticated API) is fixed, C2 (matcher parity) has a known live
  overload mismatch (see DESIGN_DECISIONS.md §9.1).
- **Compat mode**: with `JOBQUEST_REQUIRE_AUTH` unset, anonymous requests act as owner — easy to
  forget when testing endpoints.
- **First poll of a source never alerts** (`first_check` suppression) — expected, not a bug.
- **Email is legacy**: pipeline enqueues Telegram only; `notify.py` only used by test script.
- `backend/scripts/` is ruff-excluded dev tooling (add/verify/probe scripts), not product code.
- Frontend has no ESLint config; `npm run lint` prompts for setup. Use `npx tsc --noEmit`.
- Never commit `.env`; `ARCHITECTURE_REVIEW.md`, `PR_DESCRIPTIONS.md`, `pr_description.md` are
  local-only working docs (two are gitignored).
