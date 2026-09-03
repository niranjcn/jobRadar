# Board Adapters Expansion — Analysis & Incremental Plan

> **Request:** 1) Remove 10 dead Greenhouse boards, 2) Create 25 adapters for freelance / remote / tech job aggregators.
> **Principle:** Build incrementally (`AGENTS.md:2`), prefer official APIs (`AGENTS.md:19`), keep adapters isolated (`AGENTS.md:5`), do not mix freelance-gig semantics with full-time ATS semantics without a data-model decision.

---

## Part 1 — Dead Boards Removed

**Done 2026-08-31, zero code change, DB only:**

```sql
-- backend/app/poller.py:43 fetch_sources() respects active=false, so poller skips them
UPDATE sources SET active=false
WHERE company_name IN ('Retool','Weights & Biases','Benchling','Phonepay','Neon','Segment','Coda','Snyk','Outreach','Rippling');
-- 10 rows, verified: SELECT company_name, active FROM sources WHERE company_name IN (...) -> all f
```

* **Why not delete?** History kept (`Phonepay` has 78 jobs). `DELETE` would cascade to `jobs` (`migrations/001_initial.sql: ON DELETE CASCADE`). Deactivate is reversible: `UPDATE sources SET active=true WHERE ...`.
* **`sources.json` already clean:** 127 entries, none of the 10 are in the file, so `backend/app/poller.py:28` `sync_sources()` will not re-add them. DB now 192 active / 10 inactive.
* **Egress saving:** ~5% of poller REST errors + `mark_error` writes. No more `Client error 404 for .../boards/<slug>/jobs` logged for those 10 every 3600s.
* **Next:** If you want the 78 Phonepay jobs purged, run `DELETE FROM jobs WHERE source_id = (SELECT id FROM sources WHERE company_name='Phonepay')` — ask before doing.

---

## Part 2 — The 25 Requested Boards: Feasibility Matrix

Probed live endpoints 2026-08-31 (see probes in analysis). Classification by `AGENTS.md:19` ladder: `Official API > Public JSON > Server HTML > Browser automation`.

| # | Board | Requested URL | Real capability | Verdict |
|---|-------|---------------|-----------------|---------|
| **TECH / INTERNSHIPS** |
| 01 | SimplyHired | simplyhired.com | No API since 2016. HTML only, Cloudflare/WAF, search needs JS. | **HTML + anti-bot** — violates ladder step 4, breaks often, high egress. **Not recommended.** |
| 02 | Jobspresso | jobspresso.co | WP `wp-json/wp/v2/job_listing` returns 404 (tested). Feeds/search are HTML. | **HTML** — fragile. |
| 03 | Stack Overflow Jobs | stackoverflow.com/jobs | **Shut down Jan 2022**, redirects to Indeed. No adapter possible. | **Dead** — skip. |
| 04 | Wellfound / AngelList | wellfound.com | Private GraphQL (`/graphql`), requires auth + pagination tokens, ToS forbids scraping. | **Auth + ToS risk** — needs partnership. |
| 05 | Indeed | indeed.com | Publisher API deprecated 2020. No public search API. HTML scraping violates ToS + CAPTCHAs (`AGENTS.md:19` "Do not bypass CAPTCHAs"). | **Do not scrape** — legal risk. |
| 06 | Glassdoor | glassdoor.com | Partnership API only, otherwise HTML behind login. | **Do not scrape**. |
| **FREELANCE / GIG** |
| 07 | Toptal | toptal.com | Invite-only, no feed, JS-rendered. | **Browser automation** — expensive. |
| 08 | Outsourcely | outsourcely.com | HTML small board. | **HTML** |
| 09 | Freelancer | freelancer.com | **Public API** `api/projects/0.1/projects/active` — 200 OK tested (134kB JSON). Auth optional for listing. | **API — feasible** but data is gigs (hourly/budget), not `full-time` jobs. |
| 10 | Remote Freelance | remotefreelance.com | HTML only. | **HTML** |
| 11 | Remote Rocketship | lnkd.in/gS2nRtV3 | **Not a board** — LinkedIn short link to a newsletter. | **Invalid** — skip. |
| 12 | Upwork | upwork.com | GraphQL API requires OAuth (`api.upwork.com`). Doable with app key. | **Auth API — feasible** but quota + gig semantics mismatch. |
| **GLOBAL / EUROPE REMOTE** |
| 13 | Europe Remotely | europeremotely.com | WP HTML, no JSON. | **HTML** |
| 14 | Working Nomads | workingnomads.com | `GET /api/jobs` now 403, RSS `jobs.rss` 404 (tested). Feeds gone; HTML only. | **HTML** now — was API, now dead. |
| 15 | Virtual Vocations | virtualvocations.com | Paywall, no API. | **Paywalled HTML** — skip. |
| 16 | We Work Remotely | weworkremotely.com | **RSS stable** `weworkremotely.com/categories/remote-programming-jobs.rss` 200 OK (166kB XML) + `remote-jobs.rss` 847kB XML tested. | **RSS — feasible, recommended**. |
| 17 | FlexJobs | flexjobs.com | Paywall / subscription, ToS forbids scraping. | **Skip**. |
| 18 | Jobspresso Remote | jobspresso.co | Duplicate of 02. | **HTML** |
| **REMOTE-FIRST** |
| 19 | NoDesk | nodesk.co | RSS `remote-jobs/rss.xml` 404 now (tested). HTML fallback. | **HTML** |
| 20 | Remotive | remotive.com | **Public API** `remotive.com/api/remote-jobs` 200 OK (224kB JSON) tested. Docs: supports `?search=` + category. | **API — feasible, recommended**. |
| 21 | Remote4Me | remote4me.com | HTML small. | **HTML** |
| 22 | Pangian | pangian.com | HTML. | **HTML** |
| 23 | Remotees | remotees.com | HTML. | **HTML** |
| 24 | RemoteHabits | remotehabits.com | HTML aggregator. | **HTML** |
| 25 | Skip The Drive | skipthechive.com (typo: skipthedrive.com) | HTML. | **HTML** |

**Summary:** Of 25, only **3 are cleanly feasible today** with public, stable, ToS-compliant feeds:

* **Remotive API** (`remotive.com/api/remote-jobs`) — JSON, no auth, category + search.
* **We Work Remotely RSS** (`weworkremotely.com/...rss`) — XML, no auth, categories.
* **Freelancer/Upwork APIs** — feasible but **different product** (gigs vs jobs); require auth + mapping decisions.

**Stack Overflow is dead**, **Remote Rocketship is a LinkedIn link**, **Indeed/Glassdoor/Wellfound/FlexJobs are ToS-blocked**, the rest are HTML scrapes that would need `Playwright` (`AGENTS.md:19` last resort, high egress, brittle).

**Egress warning:** Adding 22 HTML scrapers would *increase* Supabase egress (more `upsert_jobs` writes) and worker egress (more external HTML fetches, 300-400kB each) — opposite of `docs/supabase-egress-plan.md`.

---

## Part 3 — Architecture Mismatch (Why 25 Adapters Is Not 25 ATS Rows)

Current model (`AGENTS.md:6`, `backend/app/models.py:18`):

```
sources.company_name + ats_type + board_identifier  ->  one company, one board
jobs.source_id + external_job_id                    ->  stable, deduped
```

* Greenhouse/Lever/Ashby/Workday: **1 source = 1 company**. Adapter `fetch_jobs(board_identifier)` returns that company's jobs. Company name is known up front.

* Remote/freelance boards: **1 source = many companies** (e.g., Remotive returns 500 jobs from 400 companies in one call). `sources.company_name` would be the *board* name, not the hiring company. `jobs.source_id` would point to "Remotive" but real company lives inside `job.company` / payload.

This needs a **new `ats_type`** handling:

```
Option A — one row per board:
  sources: { company_name: "Remotive", ats_type: "remotive", board_identifier: "remotive" }
  jobs:    { source_id: remotive_id, company: job["company_name"], title, ... }
  -> Simplest, 1 poll = 1 HTTP call per board.

Option B — per-category rows (e.g., WWR programming/design):
  sources: { company_name: "WWR-Programming", ats_type: "weworkremotely", board_identifier: "programming" }
  -> More control per category, but more rows.

Chosen: Option A. `company_name` on `sources` becomes board brand; per-job `company` is extracted from payload and stored via `jobs.url` + `metadata` JSONB (or add `jobs.company_name` denormalized later if needed for filtering).
```

Without this decision, 25 adapters would incorrectly create 25 fake "companies" that each return 500 mixed-company jobs and pollute `GET /api/companies` (`backend/app/api/routes.py:381`).

---

## Part 4 — Incremental Plan (Do Not Build 25 At Once)

Per `AGENTS.md:24` "One task at a time" and `docs/supabase-egress-plan.md` egress budget:

### Phase A — Prove the board pattern with 2 stable feeds (1-2 days)

1. Add `ats_type` `remotive` + `weworkremotely` to `migrations/021_google_amazon_ats.sql` check constraint (`sources_ats_type_check`).
2. Add adapters `backend/app/adapters/remotive.py` + `backend/app/adapters/weworkremotely.py` via `backend/app/adapters/__init__.py:16` `adapter_for`.
   * `RemotiveAdapter.fetch_jobs` — `httpx GET https://remotive.com/api/remote-jobs?search=python` -> normalize `id/title/company_name/candidate_required_location/url`.
   * `WWRAdapter.fetch_jobs` — `httpx GET https://weworkremotely.com/categories/remote-programming-jobs.rss` -> parse `feedparser`/`xml`.
3. Add 2 rows to `backend/sources.json` (brand as company) and `backend/app/adapters/__init__.py` registration.
4. Tests: `backend/tests/fixtures/remotive/`, `wwr/` + `tests/test_adapters_*.py` using saved JSON/RSS, no live hits (`AGENTS.md:22`).
5. Verify egress: `SELECT count(*) FROM jobs WHERE source_id IN (SELECT id FROM sources WHERE ats_type IN ('remotive','weworkremotely'))`.

**Effort:** ~4h, 1 PR, reversible by `UPDATE sources SET active=false`.

### Phase B — Decide freelance vs jobs (product, not code)

* Current matching (`backend/app/matcher.py:job_matches_preferences`) expects `title + description + location`. Freelance gigs have `hourly_rate/budget/skills`. If you keep them in `jobs`, matching will surface mismatched results ("Mechanical 2D Drafting in INR" showed up in Freelancer probe).
* **Options:**
  * Keep in same `jobs` table but add `job_type: 'freelance'` and let preferences filter it out by default.
  * Separate `gigs` table — out of scope until Phase A proves demand.
* **Recommendation:** Do Phase B only if Phase A metrics prove users want freelance. Do not add 6 freelance adapters now; they dilute full-time relevance.

### Phase C — Auth boards (Freelancer/Upwork) — only if product wants gigs

* Requires `FREELANCER_API_KEY` / `UPWORK_OAUTH` in `backend/.env.example`, token refresh, rate-limit handling. 1 adapter each, 1 day each + legal check.

### Phase D — HTML boards — do not build custom scrapers

* 18/25 fall here. Building/scaling HTML scrapers needs `Playwright`, proxy rotation, anti-bot bypass — `AGENTS.md:19` forbids CAPTCHA bypass and recommends against browser automation unless no API exists.
* **Better:** If you must cover them, use a *single* aggregator API (e.g., Adzuna, Jooble, or JSearch) instead of 18 scrapers. One adapter, one contract, lower egress.

---

## Recommendation

1. **Immediate:** 10 dead boards already deactivated (done). Optionally purge 78 Phonepay jobs.
2. **Next PR:** Ship **Phase A (Remotive + WWR)** as 2 adapters — demonstrates the board pattern with zero ToS/anti-bot risk, minimal egress (RSS/JSON ~200kB per poll vs 400kB HTML), and preserves `AGENTS.md` ladder.
3. **Do not ship** the other 23 in this batch. Validate Phase A for one `JOB_RETENTION_DAYS=30` cycle (`backend/app/poller.py:128`), check match quality + egress, then revisit Phase B/C.
4. **If you still want broader coverage:** Replace the HTML list with one aggregator adapter (1 file, not 18) — ask and I can draft that adapter.

**Rollback any board:** `UPDATE sources SET active=false WHERE ats_type='remotive'` or remove the row from `sources.json` and `backend/app/poller.py:28` `sync_sources()` will keep it inactive on next poll (active flag respected per `poller.py:43` `eq("active", True)`).

---

## Files Touched (only if Phase A approved)

```
backend/migrations/030_board_ats.sql          # extend sources_ats_type_check
backend/app/adapters/remotive.py              # NEW
backend/app/adapters/weworkremotely.py        # NEW
backend/app/adapters/__init__.py:16           # +2 branches
backend/app/config.py:8                       # + intervals remotive=3600, wwr=3600
backend/sources.json                          # +2 entries
backend/tests/fixtures/remotive/...           # NEW
backend/tests/fixtures/weworkremotely/...     # NEW
```
