# Contributing to jobRadar

Thanks for helping out! jobRadar is a single-user project that aims to stay
small and reliable, so contributions should be focused and follow the existing
architecture. The authoritative design document is [AGENTS.md](AGENTS.md) —
**read it before making changes.**

## Ground rules

1. **One task at a time.** Don't rewrite working components or mix unrelated
   changes into one PR.
2. **Adapters are isolated.** Source adapters only fetch/parse/return jobs.
   They must never send notifications, apply preferences, or touch business
   logic.
3. **Deterministic before clever.** Prefer exact/DB-level dedup and explainable
   matching over fuzzy logic.
4. **No secrets.** Never commit `.env`, API keys, bot tokens, or database
   credentials. See [Security](#security).
5. **Everything testable.** New behavior ships with tests; Definition of Done
   is in AGENTS.md §25.

## Development setup

Requirements: Python 3.12+, Docker + Compose, Node 20+ (frontend).

```sh
# Backend
cp backend/.env.example backend/.env   # fill in Supabase values
cd backend
python -m venv .venv && .venv\Scripts\activate   # (Windows) — or source .venv/bin/activate
pip install -r requirements-dev.txt   # runtime deps + pytest + ruff
python -m pytest tests/test_unit.py

# Frontend
cd frontend
npm install
npm test
```

For the full stack with hot reload:

```sh
docker compose up -d
```

The `web` container runs `uvicorn --reload` and the `frontend` container runs
`next dev`, so code changes apply without rebuilding (see README).

## Code style

- Python: format and lint with **Ruff** (`ruff check .`, `ruff format .`).
  Type hints are expected.
- TypeScript/React: follow the existing App Router + Tailwind conventions.
- No comments unless they explain *why* (not *what*).

## Adding a new ATS adapter

1. Inspect the source first: check for an official API or public JSON endpoint
   before scraping HTML; determine stable IDs and pagination; respect
   `robots.txt` and rate limits.
2. Create `backend/app/adapters/<ats>.py` implementing
   `JobSourceAdapter` (see `backend/app/adapters/base.py` and the existing
   adapters for the pattern).
3. Register it in `backend/app/adapters/__init__.py`.
4. Add migrations if the ATS needs new columns (increment `backend/migrations/`).
5. Add tests with saved fixtures under `backend/tests/fixtures/<ats>/`:
   - `test_fetch_jobs`, `test_parse_job`, `test_missing_field`,
     `test_pagination`, `test_duplicate_job`, `test_invalid_response`.
6. Add a `POLL_INTERVAL_<ATS>_SECONDS` default in `backend/app/config.py`.
7. Update `backend/sources.json` documentation, README, and this file if
   behavior changes.

## Running checks before submitting

```sh
cd backend && ruff check . && ruff format --check . && python -m pytest tests/test_unit.py
cd frontend && npm test
```

## Commit messages

Small, focused commits following conventional-style prefixes:

```
feat: add oracle adapter
fix: handle missing workday location
test: add greenhouse pagination fixture
docs: update README for per-ATS scheduling
```

## Pull requests

A PR should state:

- **What** changed
- **Why**
- **How** it was tested
- Any **migration/config** requirements

Keep PRs reviewable — one logical change per PR; if a change is large, split it
into smaller ones.

`main` is branch-protected: direct pushes are disallowed, so every change lands
via a PR. CI (`.github/workflows/ci.yml`) runs lint, formatting, and tests on
every PR and must pass before merge. `.github/CODEOWNERS` auto-requests
reviewers based on changed files.

## Security

- Never commit real credentials. `.env` files and logs are gitignored.
- `backend/.env.example` must contain placeholders only.
- Supabase `service_role` keys and `DATABASE_URL` must stay server-side —
  never in frontend/browser code.
- External/scraped data is untrusted: validate and sanitize before storing.
- Use timeouts and retries for all outbound requests; never bypass CAPTCHAs,
  auth, or anti-bot protections.