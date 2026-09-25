# JobQuest — Hosting for 10,000 Users

> **Status:** draft · 2026-09-20
> **Scope:** what breaks between 4 users and 10,000, and what to build before strangers pay you.
> **Principle:** keep the modular monolith. No Kubernetes, no microservices, no Kafka on day one. Scale the boring things.

---

## Table of Contents

1. [Where We Stand Right Now](#1-where-we-stand-right-now)
2. [What Will Break First (Four Walls)](#2-what-will-break-first-four-walls)
3. [Deep Dive — Each Issue & The Fix](#3-deep-dive--each-issue--the-fix)
   - 3.1 Telegram rate limits
   - 3.2 Email deliverability, spam law, and bounces
   - 3.3 The ledger that grows forever
   - 3.4 One box, no safety net
   - 3.5 Abuse, fake accounts, and coupon farming
   - 3.6 The database under real load
   - 3.7 Frontend and workers
   - 3.8 Auth at scale
   - 3.9 You are flying blind
4. [Legal Checklist (India + Global)](#4-legal-checklist-india--global)
5. [Money — What 10k Actually Costs](#5-money--what-10k-actually-costs)
6. [Build Order — Do This First](#6-build-order--do-this-first)
7. [The “Do NOT Do Yet” List](#7-the-do-not-do-yet-list)
8. [How You Know You Are Ready](#8-how-you-know-you-are-ready)
9. [Appendix — Useful Queries & Signals](#appendix--useful-queries--signals)

---

## 1. Where We Stand Right Now

A single VPS runs everything:

```
Next.js (next dev)  ─┐
FastAPI (uvicorn)    ─┤─► Postgres 15 (local volume pgdata)
APScheduler (15 ATS) ─┤─► PostgREST (Supabase REST shim)
Telegram bot (poll)  ─┘
jobquest-poll        ─── one-off manual runner, profiles: [manual]
```

**Live numbers (2026-09-20):**

| Thing | Count | Notes |
|-------|-------|-------|
| `sources` | 2,569 | 15 ATS families, ~626 Workday |
| `jobs` | 515,119 | 269 MB, all `first_seen_at = today` after the wipe |
| `poll_runs` | ~301 / 24h | avg 2.4 min per run, ~18× ATS × 24 h |
| `users` | 4 | `owner` + 3 test accounts |
| `notifications_sent` | 94 ever, 94 in last 7d | tiny today |
| `pg_database_size` | 378 MB | on a single disk, no off-site backup verified |

**Decisions that already help at 10k:**

- Match table is **bounded**. `060_match_retention.sql` prunes `job_matches` after 24 h and `recompute_job_matches` only rebuilds the last 24 h of jobs. Without this, `10k users × 500k jobs = 5B rows` would appear. With it, per-user growth is capped at daily inflow.
- Matching is **grouped**. One evaluation per distinct preference signature, not `jobs × users`. 150 users × 200 jobs went from 30k evaluations to 1k, `1.335s → 0.018s`.
- Polling is **per-ATS with advisory locks** (`pg_try_advisory_lock`) and `IntervalTrigger` (wall-clock 1 h, jitter ±120s). A slow Workday run no longer blocks Greenhouse.
- Alert delay is **tiered** (`30m privileged / 360m normal`). That already spreads Telegram load without any code change.

**What that does NOT cover** is the next four walls. They will arrive in this order.

---

## 2. What Will Break First (Four Walls)

| # | Wall | When it appears | Symptom the user sees |
|---|------|-----------------|-----------------------|
| 1 | **Telegram 30 msg/sec** | first broadly-matched popular posting | Many users get nothing, `notification_queue` fills with `failed`, no 429 counter exists |
| 2 | **Email spam folder + law** | 1k–3k recipients | Gmail throttles you, Resend suspends the domain, **no unsubscribe link = legal exposure** |
| 3 | **Ledger without end** | ~30–90 days of `notifications_sent` at 10k | DB balloons to GBs on a 500 MB plan |
| 4 | **One box dies** | any disk failure | Everything gone, no tested restore, `next dev` in prod, in-memory rate limits vanish on second worker |

Fix them in that order. Everything else is behind them.

---

## 3. Deep Dive — Each Issue & The Fix

### 3.1 Telegram Will Be Rate-Limited

**How it works today:**

`notification_queue.drain_due_notifications()` (`app/notification_queue.py:483`) groups due rows by `(user, channel)`, builds one message per user, and calls `_send_message` **in a tight loop with no pause**. There is no token bucket, no 429 handling beyond the generic retry in the queue, no metric.

Telegram Bot API documents roughly **30 messages/second** to distinct chats, with bursts penalised by `429 Too Many Requests` + `retry_after`. The code today will happily try to send 2,000 messages in one drain tick if one job matches 2,000 users.

**At 10k:**

One hot posting (e.g. “Remote Backend Engineer”) can match 10–20% of the base. One drain tick = 1,000–2,000 Telegram sends → immediate 429 flood → 3 attempts (`MAX_ATTEMPTS = 3`) → `failed` → permanent silent loss. The user sees “I never get Telegram alerts” and you see nothing in the dashboard.

**Fix (concrete):**

1. **Paced sender.** Token bucket, e.g. 25 sends/sec sustained, burst 30, with `+ jitter 0–200ms`. Sleep inside the drain loop; do not `asyncio.gather` all sends at once.
2. **Respect `retry_after`.** When Telegram returns `429`, read `retry_after` from the JSON body, sleep exactly that long, then retry *that chunk* (do not fail the whole drain).
3. **Keep the batching you already have.** One message per user per drain (today's behaviour) is correct — do not switch to one message per job.
4. **Keep tier delays.** `30m` (privileged) + `360m` (normal) already spreads the same logical send over hours without code. Don't remove them.
5. **Add a gauge:** `telegram_429_total` + `telegram_sent_per_sec` (1m avg) on the admin page next to the poll timings you already collect. When 429s > 0, you know you're at the wall.

**Not needed:** a separate Telegram worker process yet. The pacing can live inside the existing drain; extract a worker only when you run 2+ app replicas.

---

### 3.2 Email — Where Deliverability and Law Meet

**How it works today:**

One batched HTML email per user per drain via Resend, one `Resend-API-Key` from `.env`, no unsubscribe link, no double opt-in, no bounce handling, no custom domain auth. Four test users are fine.

**At 10k, three problems arrive together:**

1. **ISP filtering.** Gmail/Outlook throttle any new domain that suddenly sends to 10k recipients without `List-Unsubscribe` and without a warmed, authenticated domain (SPF + DKIM + DMARC). You land in Spam for *everyone*, including transactional mail.
2. **No verification → bounces → suspension.** No email verification on register → typos and fake addresses → hard bounces → Resend (and any ESP) will throttle or suspend the sending domain.
3. **Law.** India (DPDP Act 2023), EU (GDPR), US (CAN-SPAM) all require a working unsubscribe, a clear sender identity, and honoring it quickly. There is currently **no unsubscribe mechanism at all**.

**Fix:**

- **Sending domain.** Put mail on a subdomain (`mail.jobquest.example` or `notify.*`), add the three DNS records Resend gives you (SPF/DKIM/DMARC), warm it: 50/day → 200/day → 1k/day over 1–2 weeks before contacting 10k.
- **Unsubscribe every mail.** Add `List-Unsubscribe: <https://jobquest.example/unsubscribe?token=…>` *header* and a one-click link in the footer. Token = `HMAC(user_id, secret)` so no login is required. Store `email_unsubscribed_at` on `users`; `notification_queue` must check it before enqueuing (like `access_locked` is checked today).
- **Double opt-in.** On register, send a “confirm your email” mail with the same token; `preferences` row stays, but queue building skips until `email_verified_at` is set. One extra column, zero change to matching.
- **Bounce/complaint webhook.** Resend posts hard-bounces and spam complaints to a URL — add `POST /webhooks/resend` (you already have a Razorpay webhook as a template) that sets `email_suppressed = true` and logs to `auth_events`-style ledger.
- **Keep what you have:** batched HTML (`build_html`) and the dedicated queue rows are the right shape. Don't switch to per-job mails.

**Cost check:** `10k × ~30 mails/mo = 300k/mo`. Resend at that volume is roughly $20–80/mo depending on plan. Budget it.

---

### 3.3 The Ledger That Grows Forever

**Bounded:** `job_matches` — the 24h prune saved the project. No action.

**Unbounded:** `notifications_sent` — every delivered alert appends one row and there is **no `DELETE` or TTL**. At 10k, even 10% match rate = `~1k matches/day × 10k users × ~10%` is illustrative, but concretely even 100 sends/day × 10k = 1M rows/day. On Postgres on a 500 MB plan that is GBs within months.

**Fix:**

- **90-day retention** on `notifications_sent` (keep the recent window auditors and “why didn't I get yesterday's alert?” need; drop the rest). The `UNIQUE(user, job, channel)` idempotency that prevents re-sends only needs the recent window; older resends are meaningless after the 7-day inactive prune.
- Implement as the same pattern you just used for matches: `DELETE … WHERE sent_at < now() - interval '90 days'` inside the existing `prune_*` call that already runs every poll.
- Do not prune `notification_queue` pending rows — only `sent`.

---

### 3.4 One Box, No Safety Net

Today the entire product lives on one VPS: `web` + `scheduler` + `bot` share a process, Postgres is a local volume, `pgdata` is on the same disk. If the disk dies, the company dies. No nightly dump has been verified, no restore has been rehearsed, frontend runs `next dev` (not `next start`), and `rate_limit()` (`app/auth.py:219`) is a **dict in process memory** — the moment you run two replicas it forgets half the counts.

**Fix, in the cheapest order that actually reduces risk:**

1. **Tonight: `pg_dump --format=custom` nightly to object storage** (S3 / R2 / even a second VM's disk) + **documented, rehearsed restore** on a fresh VM. A dump you have never restored is not a backup.
2. **Tomorrow: `next build && next start`** in the frontend image; keep `next dev` only for local.
3. **This week: split the scheduler+bot into a `worker` service** (same image, different `command`). `docker-compose.yml` already has the shape; add a `worker` that runs `python -m app.workers` (or just the scheduler + bot loop) so API latency is never blocked by a 9-minute Workday poll.
4. **When revenue starts: managed Postgres** ($15–25/mo — Supabase, Neon, RDS). You keep `PostgREST`, but data lives on a replicated, point-in-time-recoverable host.
5. **Only when you run 2+ app replicas:** put rate limits and advisory locks in Redis (or keep DB advisory locks — they already survive restarts). Do not add Redis just to have Redis.

---

### 3.5 Abuse, Fake Accounts, and Coupon Farming

Today: no captcha on `/register`, no email verification, `rate_limit()` is per-process memory with a 2,000-bucket LRU cap. A bot can create thousands of accounts, scrape job cards, and burn free coupons while your Resend domain reputation collapses.

**Fix:**

- **Captcha on register/login** — Cloudflare Turnstile or hCaptcha, one widget, server-side verify before `create_registered_user`.
- **Email verification** (ties to 3.2) — queue requires `email_verified_at` and `email_unsubscribed_at IS NULL`.
- **Shared rate limiting** — move `rate_limit` from `dict` to the DB (a tiny `rate_events` table) or Redis when it exists. Keep the same `max_events / window_seconds` API so call sites don't change.
- **Coupon abuse:** one-code–one-user is already enforced; add per-IP and per-domain throttling on `redeem`.

---

### 3.6 The Database Under Real Load

You just made two calls: `sync_sources` now diffs (one `SELECT` + upserts only changed rows) instead of 2,569 blind upserts per poll, and matching is already grouped. Leave those. What remains:

- **Write spikes at poll time.** Each `poll_source` does `INSERT … ON CONFLICT … RETURNING`, `touch`, `sweep`, `mark_checked` inside one short transaction. Under 10k, that is fine; do not prematurely move matching into the DB.
- **What to watch, not change yet:** `pg_stat_user_tables` (`seq_scan` vs `idx_scan`), `pg_stat_user_indexes` (`idx_scan = 0` after a week of live traffic). You already export sizes and bloat hints on `/admin/egress` (added recently) — keep that, but add a 24 h sparkline so you see the 500 MB Free → 8 GB Pro crossing weeks before it happens.
- **What NOT to add:** read replicas, partitioning, or Elasticsearch. `jobs` + `job_matches` with the 24 h bound comfortably fits a single Postgres at 10k. The bottleneck will be Telegram/email long before the DB.

---

### 3.7 Frontend and Workers

`frontend` runs `next dev` with chokidar polling — correct for local, wrong for prod. Switch the production image to `next build`; keep `dev` behind a `NODE_ENV != production` guard.

`web` runs API + APScheduler + Telegram bot in one event loop via `run_pipeline_in_thread`. It has been the source of two bugs you already fixed (the `IntervalTrigger` vs `CronTrigger` 30-minute drift and the `pool-global` orphan). The next step is not more threads — it is a second container (`worker`) so a 9-minute Workday poll never blocks `GET /health` or `POST /poll/run`.

---

### 3.8 Auth at Scale

PBKDF2-600k (`app/auth.py:30`) is ~0.5s CPU per login — correct and intentionally slow, but it means 10 parallel logins = 10 × 0.5s of CPU. That's acceptable. What is not acceptable is a **per-process** `failed_login_attempts` and lockout that resets on restart. Keep the 5-fail / 15-min lockout you already have, but persist it in `users` (you do) and add a DB-backed `rate_limit` table so a second replica sees the same counters. Also actually use `auth_events` (you log to it — good) and alert on spikes.

---

### 3.9 You Are Flying Blind

Today: `print()` → Docker logs. No error tracker, no uptime check, no “scheduler stalled” alarm. At 10k, the first failure you hear about will be from a paying customer's tweet.

**Add:**

- **Sentry** (or equivalent) for backend + frontend — one DSN, 5 minutes, gives you stack traces instead of `docker compose logs | grep`.
- **Uptime:** `GET /health` every minute from an external probe — you already have the endpoint.
- **Stall detector:** “no `poll_runs` with `status = completed` and `finished_at > now() - 70m`” → page. A silent scheduler is worse than a crash — a crash at least restarts.
- **Keep the DB as truth for timings.** `poll_runs` + `sources.last_duration_ms` (what you show on `/timings`) is better than any APM for this product.

---

## 4. Legal Checklist (India + Global)

Don't treat this as optional — payment processors and app stores will ask for these pages verbatim, and the DPDP Act (2023) carries real penalties.

### India (DPDP Act 2023 + Consumer Protection)

- [ ] **Terms of Service** — what the product is (aggregation), not a placement guarantee, subscription auto-renewal, cancellation path (one click, same channel as purchase), refund window, and that alerts are best-effort.
- [ ] **Privacy Policy** — what you collect (email, Telegram chat id, preferences, IP), why (matching + alerts), where it is stored (DB region), how long (90d ledger retention you are about to add), and contact of the **Data Fiduciary** (you).
- [ ] **Refund & Cancellation Policy** — Razorpay requires a URL. “Monthly, auto-renew, cancel any time, no prorated refund, access until period end” is the common 10k-friendly model; pick one sentence and keep it.
- [ ] **GST handling** — `₹49` must state whether GST is included. If you are under GST composition, say so. Keep invoices (Razorpay gives them) and store `current_period_end` as truth.
- [x] **DPDP specifics:** unticked consent checkbox on register + server-side 422 + `accepted_terms_at` timestamp (`062`); purpose limitation + retention table in Privacy; grievance contact on `/contact` (name/email still `[PLACEHOLDER]` — fill before launch).

### Global (GDPR / CAN-SPAM / CASL)

- [x] **No bulk email, no unsubscribe burden** — email alerts removed entirely (Telegram-only since `75ed8c7`); the only sender left is the manual `send_test_notification.py` script. Unsubscribe / List-Unsubscribe / double-opt-in / bounce-webhook items are N/A until/unless bulk mail returns.
- [ ] **Data export / erasure:** `GET /api/auth/me/export` and `DELETE /api/auth/me` shipped (`2564a64`) — password-confirm delete, owner-guarded, presets reassigned, cascades verified live with a synthetic user (0 residue).
- [x] **Legal pages live:** `/terms`, `/privacy`, `/refund`, `/contact` (Ink-themed, footer-linked). Retention table in Privacy matches actual prunes (matches 24h, sent 24h, auth 90d, jobs 30d/7d).
- [ ] **Razorpay pages** — copy is live at the URLs above, but `[PLACEHOLDERS]` (entity, contact, address, domain, grievance officer) must be replaced with real details before live-mode review. Copy is short; the URLs must be public.
- [x] **Price truth:** landing CTA, `standard` plan, and checkout all charge **₹49/mo** (migration `063`, `access.py` fallbacks 4900 paise). Verify the live DB row and Refund page agree before charging anyone.

---

## 5. Money — What 10k Actually Costs

Assumptions: ₹49/mo, 5–10% conversion at 10k registered = 500–1,000 paying. Cold math, not a pitch.

| Line | 500 paying | 1,000 paying |
|------|------------|--------------|
| Revenue | ₹24,500 / $300 | ₹49,000 / $600 |
| Razorpay fee (~2% + GST) | −₹600 | −₹1,200 |
| Email (Resend 300k/mo, batched) | −₹1,700 ($20) | −₹3,400 ($40) |
| Infra (VPS $12 + managed DB $20 + object storage $5 + Sentry $20) | −₹4,800 ($60) | −₹4,800 |
| Domain + misc | −₹400 | −₹400 |
| **Before your salary/support** | **~₹17k / ~$200** | **~₹39k / ~$480** |

The business works **iff** deliverability holds (Wall 2). If mails land in Spam, paying users churn and the math inverts.

---

## 6. Build Order — Do This First

### Week 1 (no feature work — just safety)

1. **Nightly `pg_dump --format=custom` to S3/R2 + documented restore** — do it tonight; rehearsal on a fresh VM tomorrow. A dump you have never restored is not a backup.
2. **Email plumbing:** custom subdomain (`mail.*`) SPF/DKIM/DMARC + warm, `List-Unsubscribe` header + one-click link + `email_unsubscribed_at` gate, double opt-in mail.
3. **Captcha on `/register` and `/login`** (Turnstile), per-IP + per-account throttling backed by DB, not memory.

### Week 2 (reliability)

4. **Telegram pacing** — token bucket 25/sec + `retry_after` respect + `telegram_429_total` gauge on admin.
5. **`notifications_sent` 90-day retention** — one nightly `DELETE`.
6. **Production frontend** — `next build` image; `dev` only locally.
7. **Split `worker`** — same image, `command: python -m app.workers` (APScheduler + bot), `web` becomes API-only.

### Before you charge the 200th paying user

8. **Live Razorpay keys** — swap test → live, webhook signature verified (you already do), add Refund/Cancel pages + GST line on invoices.
9. **Sentry + uptime + stall detector** — `GET /health` (external) and “no completed run in 70 min” (internal).
10. **Synthetic 10k load test** — fabricate 10k `AudienceUser` rows, run one synthetic poll → `match_and_enqueue` → `drain` on a staging copy; measure drain msgs/sec, match upsert p95, `GET /stats/daily` p95.

### Nice to have, not day one

- Read replica, partitioning, Redis (only with ≥2 workers), LLM matching, recommendation feed, Elasticsearch.

---

## 7. The “Do NOT Do Yet” List

Explicitly out of scope at 10k; they add cost without moving any wall:

Kubernetes, microservices, Kafka, Elasticsearch, read replicas now, partitioning `jobs`, Redis for everything, LLM as primary matcher (keep it as later enhancement after deterministic matching proves stable), and rewriting the poller again.

---

## 8. How You Know You Are Ready

**Green for “invite 10k”:**

- `pg_dump` restored successfully on a clean VM in the last 7 days.
- Every email has `List-Unsubscribe`, one-click works in under 2 seconds, double opt-in required for new accounts, bounce webhook → suppression tested with a fake `bounces@` address.
- `drain_due_notifications` can sustain one synthetic popular posting (2k users) without a `429`.
- `notifications_sent` nightly delete removes `>90d` rows (check row count before/after).
- `https://jobquest.example/health` + “no completed run in 70 min” both alert to Telegram.
- Register with a throwaway email requires solving Turnstile.
- Legal: `/terms`, `/privacy`, `/refund`, `/contact` are live, linked from register + checkout, and Razorpay's live-mode checklist passes.

Keep 4, expand to 10k in cohorts (`100 → 1k → 3k → 10k`), watch `telegram_429` and DB size after each cohort.

---

## Appendix — Useful Queries & Signals

```sql
-- Are we pacing Telegram?
SELECT count(*) FILTER (WHERE error ILIKE '%429%') AS telegram_429s_last_24h
FROM poll_runs WHERE finished_at > now() - interval '24 hours';

-- Is the ledger growing without bound?
SELECT pg_size_pretty(pg_total_relation_size('notifications_sent')),
       count(*) AS rows, count(*) FILTER (WHERE sent_at < now() - interval '90 days') AS prunable
FROM notifications_sent;

-- Will we hit 500 MB?
SELECT pg_size_pretty(pg_database_size(current_database())),
       pg_size_pretty(pg_total_relation_size('jobs')),
       pg_size_pretty(pg_total_relation_size('job_matches'));

-- Is anyone stuck without mail/Telegram destination?
SELECT count(*) FILTER (WHERE status = 'pending') AS pending,
       count(*) FILTER (WHERE status = 'failed')  AS failed
FROM notification_queue;
```

Good signals to keep on the admin page: drain `sent/sec` (1m), `telegram_429_total` (24h), `notifications_sent` 90d prunable, DB % of 8 GB Pro, `has_orphaned_running` from `poll_runs`.

---

*This plan is intentionally boring. The product is aggregation + matching + alerting; the moat at 10k is reliable delivery and low DB churn, not new infrastructure. Do the boring parts first.*
