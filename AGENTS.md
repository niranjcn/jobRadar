# AGENTS.md — JobQuest

## 1. Project Overview

JobQuest is a job discovery and alerting platform that continuously monitors company career pages and job platforms, detects newly published jobs, filters them according to user preferences, deduplicates results, and delivers relevant alerts through Telegram and email.

The initial goal is to build the system incrementally, starting with reliable job ingestion and normalization before adding advanced matching, notifications, and UI features.

### Core workflow

```text
Career Sources
     |
     v
Source Adapters / Scrapers
     |
     v
Raw Job Data
     |
     v
Normalization
     |
     v
Deduplication
     |
     v
Supabase PostgreSQL
     |
     v
Preference Matching
     |
     +----------+----------+
     |                     |
     v                     v
 Telegram                Email
```

---

## 2. Development Philosophy

### Build incrementally

Do NOT attempt to implement the entire system in one step.

Development should follow this order:

1. Project skeleton
2. Database schema
3. One job source
4. Job normalization
5. Deduplication
6. Scheduled ingestion
7. Preference matching
8. Telegram notifications
9. Email notifications
10. API layer
11. Frontend/dashboard
12. Additional job-source adapters
13. Reliability, observability, and scaling
14. AI-powered job matching

Each milestone must be independently testable.

### Prefer simple architecture first

JobQuest should begin as a modular monolith with background workers.

Avoid introducing microservices, Kubernetes, Kafka, or other infrastructure until there is a demonstrated need.

---

## 3. Planned Technology Stack

### Backend

- Python 3.12+
- FastAPI
- Pydantic
- SQLAlchemy or Supabase Python client
- httpx
- BeautifulSoup
- Playwright for JavaScript-heavy sources
- pytest
- Ruff
- mypy where practical

### Database

- Supabase
- PostgreSQL
- PostgreSQL Row Level Security if/when multi-user functionality is introduced

### Background Processing

Initial implementation:

- Python worker
- Scheduled jobs

Potential later additions:

- Redis
- Celery / RQ / Arq

Do not add Redis merely for the sake of having Redis.

### Frontend

Preferred future stack:

- Next.js
- TypeScript
- Tailwind CSS

The frontend should communicate with the backend API for application/business logic.

Supabase may be accessed directly from the frontend only for carefully chosen operations where this provides a clear benefit and does not bypass required backend logic or security boundaries.

### Notifications

- Telegram Bot API
- Email provider/API
- SMTP may be used for early development

### Infrastructure

- Docker
- Docker Compose for local development
- GitHub Actions for CI/CD
- Environment variables for secrets

---

## 4. Architecture

The initial architecture should look approximately like:

```text
                         +-------------------+
                         |     Next.js UI    |
                         +---------+---------+
                                   |
                              REST / HTTP
                                   |
                         +---------v---------+
                         |      FastAPI      |
                         +---------+---------+
                                   |
                 +-----------------+-----------------+
                 |                 |                 |
          +------v------+   +------v------+   +------v------+
          | Supabase /  |   | Job Service |   | Preferences |
          | PostgreSQL  |   |             |   |   Service   |
          +-------------+   +------+------+   +-------------+
                                   |
                           +-------v--------+
                           | Source Workers |
                           +-------+--------+
                                   |
              +--------------------+--------------------+
              |          |          |          |        |
          Workday    Greenhouse   Lever      Ashby   Custom
```

The backend should be organized by responsibility rather than by framework feature.

Suggested structure:

```text
jobQuest/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── workers/
│   │   ├── adapters/
│   │   │   ├── base.py
│   │   │   ├── greenhouse.py
│   │   │   ├── lever.py
│   │   │   ├── ashby.py
│   │   │   ├── workday.py
│   │   │   └── custom.py
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   └── ...
│
├── scripts/
├── docs/
├── docker-compose.yml
├── .env.example
├── .gitignore
└── AGENTS.md
```

The exact structure can evolve, but source adapters must remain isolated from core business logic.

---

## 5. Source Adapter Architecture

Every job source must implement a common interface.

Example conceptual interface:

```python
class JobSourceAdapter:
    async def fetch_jobs(self) -> list[RawJob]: ...
```

Adapters are responsible only for:

1. Connecting to the source
2. Fetching job listings
3. Parsing source-specific data
4. Returning normalized/raw source data
5. Reporting source-specific errors

Adapters must NOT:

- Send Telegram messages
- Send emails
- Apply user preferences
- Contain database business logic
- Decide whether a job is relevant to a user

Those responsibilities belong to separate services.

### Adapter priority

Implement sources from easiest to hardest.

Suggested progression:

```text
1. Greenhouse
2. Lever
3. Ashby
4. Simple company APIs / JSON endpoints
5. Workday
6. Custom company career pages
7. JavaScript-heavy / unusual systems
```

This order may change based on actual technical findings.

---

## 6. Job Data Model

All sources must eventually map into a common job representation.

A normalized job should contain fields such as:

```text
id
source
source_job_id
company
title
description
location
employment_type
department
team
remote_status
job_url
company_url
posted_at
first_seen_at
last_seen_at
metadata
```

Source-specific information may be preserved inside a JSON/JSONB metadata field.

Do not create source-specific columns for every unusual field unless that field becomes important to the core product.

---

## 7. Deduplication

Duplicate detection is a core requirement.

The same job may appear:

- Multiple times on the same source
- Through different URLs
- Through different company pages
- After minor changes to the job description
- Across repeated crawler executions

Preferred initial strategy:

```text
source + source_job_id
```

when a stable source job ID exists.

Fallback strategy:

```text
normalized company
+ normalized title
+ normalized location
+ source
```

Potential future strategy:

- Canonical URL
- Content hash
- Job-description fingerprint
- Similarity matching

Do not introduce fuzzy matching until deterministic approaches have been exhausted.

---

## 8. Job Ingestion Pipeline

Every ingestion run should conceptually perform:

```text
Fetch
  ↓
Parse
  ↓
Validate
  ↓
Normalize
  ↓
Deduplicate
  ↓
Upsert
  ↓
Identify Newly Discovered Jobs
  ↓
Match Preferences
  ↓
Queue Notifications
```

A failed source must not cause the entire ingestion process to fail.

Example:

```text
Workday     SUCCESS
Greenhouse  SUCCESS
Lever       FAILED
Ashby       SUCCESS
```

The successful sources should still be processed.

Errors should be recorded with enough context for debugging.

---

## 9. Scheduling

Job sources will eventually be checked at configurable intervals.

Examples:

```text
Every 15 minutes
Every 30 minutes
Every hour
Every 6 hours
Daily
```

The scheduler should trigger ingestion jobs rather than containing scraping logic itself.

Avoid putting long-running scraping operations directly inside FastAPI request handlers.

Bad:

```text
POST /scrape
    |
    +--> scrape 500 companies
    |
    +--> wait 10 minutes
```

Preferred:

```text
POST /scrape
    |
    +--> enqueue job
    |
    +--> return immediately
```

---

## 10. Preferences

Preferences should eventually support:

### Roles

- Software Engineer
- Backend Engineer
- DevOps Engineer
- Cloud Engineer
- SRE
- Platform Engineer

### Locations

- Country
- City
- Remote
- Hybrid
- On-site

### Experience

- Internship
- New Grad
- Entry Level
- 0–2 years
- 2–5 years

### Skills

Examples:

```text
Python
Go
Java
AWS
Docker
Kubernetes
Terraform
PostgreSQL
Linux
```

### Companies

Users should be able to include/exclude specific companies.

---

## 11. Matching Engine

The first matching engine should be deterministic and explainable.

Example:

```text
Job:
Backend Software Engineer

Location:
Dubai

Skills:
Python, AWS, PostgreSQL

User:
Backend Engineer
Dubai
Python, AWS
```

Result:

```text
MATCH
```

Do not start with an LLM.

AI matching should be a later enhancement after deterministic matching works reliably.

Future AI matching could provide:

```text
Match Score: 91%

Why:
- Strong Python match
- Strong backend match
- Location matches
- AWS requirement matches
- Experience level compatible
```

---

## 12. Notifications

Notifications should be separated from job ingestion.

The ingestion system should create a notification event such as:

```text
New matching job detected
```

Then notification handlers can process it.

Example:

```text
Job Match
   |
   +--> Telegram Notification
   |
   +--> Email Notification
```

A failure in Telegram should not prevent email delivery.

Notification records should track:

```text
job_id
user_id
channel
status
sent_at
error
```

Use idempotency to prevent sending the same alert repeatedly.

---

## 13. Telegram

Telegram is the first preferred notification channel.

A notification should be concise and actionable.

Example:

```text
🚨 New Job Match

Software Engineer
Adobe

📍 Dubai
💼 Full-time
🎯 Match: 92%

🔗 Apply
```

Avoid sending excessive information.

The message should prioritize:

1. Job title
2. Company
3. Location
4. Match score
5. Application link

---

## 14. Email

Email can initially use a simple template.

Later versions may support:

- Immediate alerts
- Daily digest
- Weekly digest
- Grouping by company
- Grouping by location
- Match-score sorting

Email delivery should be handled asynchronously.

---

## 15. API Design

Potential initial endpoints:

```text
GET    /health

GET    /jobs
GET    /jobs/{id}

GET    /companies
GET    /sources

GET    /preferences
PUT    /preferences

POST   /sources/{id}/run
GET    /sources/{id}/status
```

Authentication and user management should be introduced when multi-user support is implemented.

Do not expose internal scraping functionality publicly without authentication and authorization.

---

## 16. Frontend

The frontend is not the first milestone.

Build it after the ingestion pipeline and API are working.

Initial dashboard:

```text
Dashboard
├── New Jobs
├── Matching Jobs
├── Companies
├── Sources
├── Preferences
└── Notifications
```

Job card:

```text
Software Engineer
Adobe

Dubai · Full-time

Match: 92%

[View Job]
```

The UI should be fast because the backend should return already-normalized database records.

Do not make the frontend scrape career pages.

---

## 17. Database Principles

Use PostgreSQL constraints and indexes aggressively where appropriate.

Potential indexes:

```text
jobs(source, source_job_id)
jobs(company_id)
jobs(posted_at)
jobs(first_seen_at)
jobs(location)
```

Use database-level uniqueness where possible.

Example:

```text
UNIQUE(source, source_job_id)
```

Never rely only on application-level duplicate checks.

---

## 18. Security

Never commit:

```text
.env
API keys
Telegram bot tokens
Database passwords
SMTP credentials
Supabase service-role keys
```

Use:

```text
.env
.env.example
```

The `.env.example` file must contain placeholders only.

Important:

- Supabase anon/public keys may be used where appropriate.
- Supabase service-role keys must remain server-side.
- Never expose service-role credentials to the frontend.
- Validate all external input.
- Sanitize/validate scraped data before persistence.
- Use timeouts for external requests.

---

## 19. Scraping Rules

JobQuest should prefer official/public endpoints and APIs when available.

Before implementing a scraper:

1. Inspect the career page.
2. Determine whether jobs are exposed through an API.
3. Inspect network requests where appropriate.
4. Identify stable identifiers.
5. Determine pagination behavior.
6. Determine rate limits.
7. Check robots.txt and applicable terms.
8. Implement the smallest reliable extraction method.

Prefer:

```text
Official API
    >
Public JSON endpoint
    >
Server-rendered HTML
    >
Browser automation
```

Do not use browser automation when a reliable API exists.

Use Playwright only when necessary.

Implement respectful request rates, retries, exponential backoff, and timeouts.

Do not attempt to bypass CAPTCHAs, authentication, access controls, or anti-bot protections.

---

## 20. Error Handling

External sources are unreliable.

Expected failures include:

- HTTP 403
- HTTP 429
- HTTP 500
- Timeout
- HTML structure changes
- Missing fields
- Invalid JSON
- Pagination failures
- Temporary DNS/network errors

The system must:

- Catch source-specific failures
- Log useful context
- Retry transient failures
- Avoid infinite retries
- Continue processing other sources
- Record source health

Never silently discard errors.

---

## 21. Observability

Initial logging should include:

```text
source
run_id
start_time
duration
jobs_fetched
jobs_new
jobs_updated
jobs_skipped
errors
```

Later add:

- Prometheus
- Grafana
- Structured logging
- Metrics
- Alerting
- Source health dashboards

Do not add Prometheus/Grafana before basic logging and application health are working.

---

## 22. Testing

Every adapter should have tests.

Minimum adapter tests:

```text
test_fetch_jobs
test_parse_job
test_missing_field
test_pagination
test_duplicate_job
test_invalid_response
```

Use saved fixtures rather than hitting live career pages for most unit tests.

Example:

```text
tests/
├── fixtures/
│   ├── greenhouse/
│   ├── lever/
│   ├── ashby/
│   └── workday/
└── adapters/
```

Integration tests may use controlled endpoints or carefully limited live tests.

Never make the entire test suite dependent on a live third-party career site.

---

## 23. Git Workflow

### Always sync before pushing

Before any push to GitHub, ALWAYS:

1. `git fetch origin`
2. Compare the local branch against `origin/main` (and the branch's own remote tracking ref, if it exists).
3. If `origin/main` has advanced, rebase the working branch onto `origin/main` (`git rebase origin/main`) and re-run the relevant checks (lint + tests).
4. Resolve any conflicts before pushing.
5. Only then push (use `--force-with-lease` if the push follows a rebase).

Never push a stale branch. Never assume the remote is in the state you last saw it.

Use small, focused commits.

Good:

```text
feat: add greenhouse adapter
feat: add job normalization
fix: handle missing workday location
test: add greenhouse pagination fixture
```

Avoid:

```text
update stuff
changes
final
```

Recommended branches:

```text
main
develop
feature/*
fix/*
```

Use descriptive branch names:

```text
feature/add-auth
feature/telegram-start-command
fix/login-crash
fix/ci-workflow
```

GitHub workflow rules:

1. **Branch protection** — `main` is protected: direct pushes are disallowed,
   every change lands via a pull request.
2. **PR reviews** — pull requests require an approved review before merge.
3. **CI checks** — lint, formatting, and tests run automatically on every PR
   (`.github/workflows/ci.yml`); the checklist items are verified by CI, not
   self-reported, and CI must be green to merge.
4. **CODEOWNERS** — `.github/CODEOWNERS` auto-requests the right reviewers
   based on which files changed.
5. **Issue templates** — bug reports and feature requests use
   `.github/ISSUE_TEMPLATE/`.
6. **Small PRs** — one logical change per PR; a 2,000-line diff is a red flag.

Pull requests should contain:

- What changed
- Why
- How it was tested
- Any migration/configuration requirements

---

## 24. AI-Assisted Development Rules

JobQuest is being developed with AI assistance.

AI agents must:

1. Read `AGENTS.md` before modifying the project.
2. Understand the existing architecture before adding code.
3. Avoid rewriting working components unnecessarily.
4. Make small, reviewable changes.
5. Run relevant tests after changes.
6. Never invent external API behavior.
7. Inspect actual source behavior before implementing an adapter.
8. Preserve existing interfaces unless there is a clear reason to change them.
9. Update documentation when architecture changes.
10. Never expose secrets in code, logs, or commits.
11. **Always explain in a way that is easier to understand** — use simple language, short sentences, everyday analogies, and clear examples first, then add the technical detail. The reader should grasp *what* happens and *why* before reading code or jargon, while still keeping technical accuracy (file paths, concepts, and precise terms).

### One task at a time

Do not ask an AI agent to:

```text
Build the entire JobQuest platform.
```

Instead:

```text
Implement the database schema.
```

Then:

```text
Implement the JobSourceAdapter interface.
```

Then:

```text
Implement the Greenhouse adapter.
```

Then:

```text
Add tests for the Greenhouse adapter.
```

This makes failures easier to identify and prevents uncontrolled architecture changes.

---

## 25. Definition of Done

A feature is not complete merely because the code compiles.

A feature is considered complete when:

- Code is implemented
- Tests are added
- Tests pass
- Error cases are handled
- Logging is present where useful
- Configuration is documented
- Secrets are not hardcoded
- Existing functionality still works
- Documentation is updated if required

---

## 26. Current Development Strategy

JobQuest should currently focus on the foundation.

### Phase 1

```text
Repository
   ↓
Docker
   ↓
FastAPI
   ↓
Supabase
   ↓
Database schema
   ↓
Basic health endpoint
```

### Phase 2

```text
Source adapter interface
   ↓
First source
   ↓
Fetch jobs
   ↓
Normalize jobs
   ↓
Store jobs
```

### Phase 3

```text
Deduplication
   ↓
Scheduled ingestion
   ↓
Source health
```

### Phase 4

```text
User preferences
   ↓
Matching engine
```

### Phase 5

```text
Telegram
   ↓
Email
```

### Phase 6

```text
REST API
   ↓
Next.js dashboard
```

### Phase 7

```text
Greenhouse
Lever
Ashby
Workday
Custom company adapters
```

### Phase 8

```text
AI matching
Analytics
Observability
Scaling
```

---

## 27. Important Architectural Principle

The most important rule in JobQuest is:

> **Sources should be replaceable, but the rest of the system should not care where a job came from.**

The core application should operate on a normalized `Job` model.

For example:

```text
Workday ──────┐
Greenhouse ───┤
Lever ────────┤
Ashby ────────┤──> RawJob ──> Normalized Job
Custom ───────┘
```

Once normalized, the rest of JobQuest should not need to know whether a job came from Workday, Greenhouse, Lever, Ashby, or a custom career page.

This separation is what will allow JobQuest to grow from a personal project into a reliable multi-source job monitoring platform.
