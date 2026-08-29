# Auth & Multi-User Plan — Registration, Approval, Tiered Alerts, WebApp

> Status: Proposal (not implemented). Build incrementally, one phase at a time, per AGENTS.md.
> Each phase must be independently testable and must not break the existing single-user system.

---

## 1. Goals

1. Two registration paths — **Telegram** (`/start`) and **web** (registration form) — both requiring **admin approval** before anything else works.
2. **Account types**
   - **Telegram user** → gets job alerts, can set preferences **via Telegram commands and/or web**, and gets **full read + write** web access (delivered as a **Telegram Mini App / webapp** so it runs inside Telegram).
   - **Web-only user** → **no alerts**, but can see the latest jobs on the dashboard, filtered by preferences.
   - **Linked user** → registered one way, connected the other. A web user can link their Telegram (and then use the Telegram id to log in); a Telegram user can link an email (and log in on the web too).
3. **Approval gate** — every registration (Telegram or web) stays `pending` until the admin approves.
4. **Admin kill switch + granular control** — the admin can disable any single user completely (no login, no alerts, no commands) and re-enable them, **and** can grant/revoke individual features per user via a capabilities list.
5. **Privileged users** — users with `fast_alerts` get job alerts immediately; everyone else gets them **delayed** (30 min or 1 hour, admin-configurable).
6. Use AI sparingly and efficiently where it genuinely helps (see §8).

## 2. Account types & identity model

One `users` row per person; the "type" is derived from which identifiers are present.

| Type | `telegram_chat_id` | `email` | Alerts | Web access | Preferences |
|---|---|---|---|---|---|
| Telegram-only | set | null | yes (delayed unless `fast_alerts`) | full read+write via Mini App or browser **and Telegram commands** | yes — **via commands too** |
| Web-only | null | set | **no** | read-only dashboard (jobs/matches per prefs) | read-only unless `preferences` capability granted |
| Linked | set | set | yes (delayed unless `fast_alerts`) | full read+write | yes — via commands and web |

- **Owner/admin**: the existing sentinel user (`DEFAULT_USER_ID`), identified by env `ADMIN_TELEGRAM_CHAT_ID`. Approved by default, has every capability.
- Approval status is independent of type: a pending Telegram user is just as locked out as a pending web user.

### 2.1 Capabilities — feature-level admin control (not just on/off)

Access is governed by a per-user **capabilities** list (`users.capabilities text[]`). The admin can grant or revoke **individual features** for any single user — the "disable" switch stays as the full lockout, and capabilities give the fine-grained removal on top.

| Capability | Effect |
|---|---|
| `dashboard` | read-only web dashboard (jobs, matches, sources) |
| `preferences` | set/change preferences (Telegram commands **and** web) |
| `telegram_alerts` | receive Telegram job alerts |
| `email_alerts` | receive email job alerts |
| `fast_alerts` | privileged: alerts go out immediately (no delay) |
| `admin` | owner-only: approve/disable/capability/alert-delay controls |

Default sets by type (owner seeds all six):

| Type | Default capabilities on approval |
|---|---|
| Telegram-only / Linked | `{dashboard, preferences, telegram_alerts}` (+ `email_alerts` once an email is linked & email notify on) |
| Web-only | `{dashboard}` (admin may grant `preferences`, alerts, etc. individually) |
| Owner | `{dashboard, preferences, telegram_alerts, email_alerts, fast_alerts, admin}` |

`fast_alerts` supersedes the earlier separate "privileged/`tier`" flag — it's just one more capability the admin can toggle per user.

## 3. Current state (verified)

- **Single-user by design.** `DEFAULT_USER_ID = "00000000-0000-0000-0000-000000000001"` (`config.py:6`) is the only identity. No `users` table, no auth, no login, no sessions.
- **Telegram** bot (`bot.py`) long-polls; `authorized()` (`bot.py:88-89`) only replies to the configured `TELEGRAM_CHAT_ID`. `/start` (`bot.py:289-307`) sends a welcome, persists nothing. `/app` (`bot.py:745-761`) already sends a WebApp button to `telegram_mini_app_url`; `frontend/components/telegram-bridge.tsx` already reads `Telegram.WebApp` (theme only, no auth).
- **Preferences** live in a singleton `preferences` row keyed by `user_id` (`003_preferences_matcher.sql`), always written with the sentinel id (`matcher.py:181`, `routes.py:765,810`).
- **Notifications** go to `settings.telegram_chat_id` (`poller.py:525`) and `settings.notify_to` (`poller.py:541`) — not per-user. `notifications_sent` dedup is `(job_id, channel)` (`004_notifications.sql`).
- No FKs from `preferences`/`job_matches`/`notifications_sent.user_id` to any table.
- Frontend: no login page, no middleware/auth guard, `lib/api.ts` sends no identity.
- Highest migration: `021_google_amazon_ats.sql`.

## 4. Architecture decisions (D1–D10 — lock in first)

| # | Decision | Rationale |
|---|---|---|
| D1 | New `users` table; existing `user_id` columns stay `uuid`. | Minimal churn. |
| D2 | **Seed the owner**: `users` row with `id = DEFAULT_USER_ID`, `telegram_chat_id` from env `TELEGRAM_CHAT_ID`, `status='approved'`, full capabilities incl. `admin`. | Existing data survives; the sentinel becomes the owner's real identity. Zero data migration. |
| D3 | Login methods: **(a)** Telegram Mini App `initData` HMAC auth (instant, in-app), **(b)** web OTP — enter chat id → bot DMs 6-digit code, **(c)** email OTP via Resend for web-only users. No passwords. | Consistent OTP UX everywhere; HMAC proves identity inside Telegram; Resend already exists. |
| D4 | Auth = **httpOnly signed session cookie** (itsdangerous/JWT) + FastAPI `get_current_user` dependency. Stateless — no per-request DB session lookup. | Simple; works through the Next.js rewrite proxy; replaceable by Supabase Auth later. |
| D5 | **Permissions = per-user capabilities list** (`users.capabilities text[]`) enforced in one helper (`has_cap(user, cap)`). Admin can add/remove individual features per user; `disabled` remains the full lockout. | Fine-grained feature control; one place to change policy; no per-route drift. |
| D6 | **Notifications become queue-driven**: poll writes `notification_queue` rows with `scheduled_for`; a drain worker sends due rows. `fast_alerts` → `now`, others → `now + delayed_alert_minutes`. | Decouples ingest from send, implements delay tiers for free, batches sends, smooths load. |
| D7 | Per-user dedup = `notifications_sent` unique `(user_id, job_id, channel)`; `notification_queue` unique `(user_id, job_id, channel)`. | Each user is alerted per job per channel at most once, at their tier's time. |
| D8 | Jobs are **global/shared**; only `job_matches` and notifications are per-user. One ingest serves all users. | Avoids duplicating job storage per user. |
| D9 | Account linking requires **proof-of-ownership** (code DMed/emailed), both directions. | Prevents claiming someone else's Telegram id or email. |
| D10 | **Telegram commands are a first-class write surface**: every preference and notification setting has a bot command, not just the webapp/UI. | The bot is the primary interface for Telegram users (per requirement); web is the same data, different surface. |
| D11 | AI is opt-in, cached, async, and degrades to deterministic behavior. | AGENTS.md §11: deterministic first, LLM later. |

## 5. Database schema

### Migration `022_users_auth.sql`

```sql
create table users (
    id uuid primary key default gen_random_uuid(),
    telegram_chat_id bigint unique,
    telegram_user_id bigint unique,
    telegram_username text,
    email text unique,
    display_name text not null default '',
    status text not null default 'pending'
        check (status in ('pending', 'approved', 'disabled')),
    capabilities text[] not null default '{}',
    is_owner boolean not null default false,
    approved_at timestamptz,
    approved_by uuid references users (id),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

insert into users (id, telegram_chat_id, status, capabilities, is_owner, approved_at, display_name)
values (
    '00000000-0000-0000-0000-000000000001', null, 'approved',
    array['dashboard','preferences','telegram_alerts','email_alerts','fast_alerts','admin'],
    true, now(), 'owner'
)
on conflict (id) do nothing;   -- chat id stamped from env at first startup

alter table preferences        add constraint preferences_user_fk  foreign key (user_id) references users (id);
alter table job_matches        add constraint job_matches_user_fk  foreign key (user_id) references users (id) on delete cascade;
alter table notifications_sent add constraint notifications_user_fk foreign key (user_id) references users (id) on delete cascade;

alter table notifications_sent drop constraint notifications_sent_job_id_channel_key;
delete from notifications_sent a using notifications_sent b
 where a.user_id = b.user_id and a.job_id = b.job_id and a.channel = b.channel and a.id < b.id;
alter table notifications_sent add constraint notifications_sent_user_job_channel_key unique (user_id, job_id, channel);

create table login_codes (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references users (id),
    channel text not null check (channel in ('telegram', 'email')),
    code text not null,
    expires_at timestamptz not null,
    attempts int not null default 0,
    used_at timestamptz
);
create index login_codes_user_idx on login_codes (user_id, used_at);
```

### Migration `023_notification_queue.sql`

```sql
create table notification_queue (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references users (id),
    job_id uuid not null references jobs (id) on delete cascade,
    channel text not null check (channel in ('telegram', 'email')),
    scheduled_for timestamptz not null,
    status text not null default 'pending'
        check (status in ('pending', 'sent', 'failed')),
    attempts int not null default 0,
    created_at timestamptz not null default now(),
    unique (user_id, job_id, channel)
);
create index notification_queue_due_idx on notification_queue (status, scheduled_for);

-- global delay setting (admin-tunable; honored by drain worker)
insert into app_settings (key, value) values ('delayed_alert_minutes', '30')
on conflict (key) do nothing;
```

**Notes**
- Adding FKs is safe: all existing `user_id` rows reference the sentinel, which now exists in `users`.
- `login_codes` are also used for **account linking** (same proof-of-ownership primitive).

## 6. Auth flows

### 6.1 Login method (a) — Telegram Mini App (webapp)
1. Inside Telegram, `/app` opens the Next.js frontend (existing `telegram_mini_app_url`).
2. `telegram-bridge.tsx` sends `Telegram.WebApp.initData` to `POST /api/auth/telegram-webapp`.
3. Backend verifies the **HMAC-SHA256** signature of `initData` with the bot token; extracts `user.id`, `user.username`; resolves the `users` row by `telegram_user_id`.
4. `status != 'approved'` → 403. Approved → issue session cookie. **Zero typing.**

### 6.2 Login method (b) — Web browser OTP
1. `POST /api/auth/login` `{telegram_chat_id}` → 202 always (no enumeration). If user is approved, bot DMs a 6-digit code.
2. `POST /api/auth/verify` `{telegram_chat_id, code}` → session cookie. 5-min expiry, 5 attempts, single-use.

### 6.3 Login method (c) — Email OTP (web-only users)
Same shape as (b) with `{email}`, code delivered via **Resend** (`notify.py` already has the client). Works for any approved user with an email.

### 6.4 Account linking (both directions, proof-of-ownership)
- **Web → Telegram**: Settings page enters a Telegram chat id → bot DMs a code → user enters it → `telegram_chat_id`/`telegram_user_id`/`telegram_username` stamped on the row. User can now log in via (a)/(b) and **starts receiving alerts** (their type becomes "linked").
- **Telegram → Email**: Settings page enters an email → Resend sends a code → verified → `email` stamped. User can now log in via (c) on the web.
- Both flows reuse `login_codes` with `channel` = the target channel.

## 7. Permissions, bot write commands & tiered alerts

### 7.1 Permission matrix (single `has_cap(user, cap)` helper, gated on `status == 'approved'`)

| Capability | pending | approved · web-only | approved · telegram/linked | disabled |
|---|---|---|---|---|
| `dashboard` (read jobs/matches/sources) | ✗ | ✓ | ✓ | ✗ |
| `preferences` (write prefs) | ✗ | only if granted | ✓ | ✗ |
| `telegram_alerts` | ✗ | ✗ | ✓ (if granted) | ✗ |
| `email_alerts` | ✗ | ✗ | ✓ (if email linked) | ✗ |
| `fast_alerts` (immediate) | ✗ | ✗ | only if granted | ✗ |
| `admin` (owner) | — | — | — | ✓ |

### 7.2 Telegram = full write surface (commands)

Every user write action has a **Telegram command**, mirroring the web forms. All require `preferences`/respective capability and approved status. Deterministic subcommands are primary; the AI free-text command is a convenience (§8.2).

**Preferences**
```
/preferences                          — show current preferences (all categories)
/prefs roles <comma list>             — replace roles (e.g. /prefs roles backend, devops)
/prefs keywords <comma list>
/prefs locations <comma list>
/prefs seniority <comma list>
/prefs exclude-companies <list>
/prefs exclude-roles <list>
/prefs clear <category>               — reset one category to empty
```

**Notification settings**
```
/prefs notify-telegram on|off
/prefs notify-email on|off
/prefs scope matched|all              — telegram alert scope
/prefs email-scope matched|all
/prefs frequency immediate|daily|weekly
/prefs notify-first-check on|off
/subscribe                             — enable alerts (shorthand for the notify toggles)
/unsubscribe                           — disable alerts (no preference loss)
```

**AI convenience**
```
/prefs-nl <free text>                  — e.g. /prefs-nl "backend python, remote or dubai"
                                       → LLM parses → user confirms → saved (falls back to
                                         raw text via deterministic matching if LLM fails)
```

Implementation note: parse `/prefs <key> <value>` through a small mapping table → same `PUT /api/preferences` path the web uses → `recompute_matches(user_id)`. One code path for command + web + webapp.

### 7.3 Tiered alert timing
- `fast_alerts` capability present → `scheduled_for = now` at ingest.
- otherwise → `scheduled_for = now + delayed_alert_minutes` (global setting, default 30; admin sets 30/60).
- **Drain worker** (piggyback on the existing scheduler, 1-min tick or every poll): single SQL `select ... from notification_queue where status='pending' and scheduled_for <= now()` → group by `(user_id, channel)` → reuse existing `send_telegram_notifications`/`send_email_notifications` per user → mark `sent` and write `notifications_sent`. Failures: `attempts+1`, retry ≤3, then `failed`.
- Owner/admin always has `fast_alerts`.

### 7.4 Web-only "based on preferences" dashboard
- `dashboard` users see jobs/matches filtered by their preferences (same endpoints, user-scoped).
- Recommendation (my advice): grant `preferences` to web-only users too — a dashboard "based on preferences" is useless if the user can't set them. One capability per user; default off to match the strict spec, flip on via `/cap` or the admin page if you agree.

## 8. AI work — where it helps, done efficiently

Per AGENTS.md §11, AI is a **later enhancement** layered on deterministic logic. All uses share one client, so marginal cost is low.

### 8.1 Shared LLM service (`backend/app/services/llm.py`)
- One client wrapper: model, key, `timeout=15s`, retries, `max_tokens`, `temperature=0` for extraction.
- `parse_json_response()` with schema validation + **deterministic fallback** (LLM fails → raw text still flows through existing substring matching).
- **Response cache** (`llm_cache(key, result, created_at)`): key = hash(model+prompt+input); identical inputs never pay twice.
- Wrapped in `asyncio.to_thread` — never blocks the event loop.
- Cost control: cheap model for structured extraction, token caps, per-user daily quota.

### 8.2 Natural-language preferences (highest UX ROI)
Telegram `/prefs-nl <free text>` or the web box accepts free text → LLM returns `{roles, keywords, locations, seniority, excluded_companies, excluded_roles}` → user previews the parsed (deterministic) form and confirms. No AI → empty/unchanged; the deterministic `/prefs <key> <value>` subcommands are always the fallback.

### 8.3 Match explanations ("why this match")
1. **Deterministic first**: template from stored `matched_on` reasons (`matcher.py:56-58`) — free, instant.
2. **Optional LLM polish** (per user, off by default): one call per notification batch (not per job) for a 1–2 line human summary; cache by notification id.

### 8.4 Admin-approval screening (optional, off by default)
LLM classifies a registration as `human`/`likely-spam` from display name + username + email so the admin can bulk-approve. Strictly advisory.

**Efficiency rules:** deterministic path runs first; AI only improves; cached; batched (never per-job); async via `to_thread`; structured JSON out with fallback.

## 9. Implementation phases

### Phase 1 — Schema (`022` + `023`)
**Files:** the two migrations. `main.py` migration runner already applies new files.
**Tests:** fresh-DB apply; FK checks; sentinel row; old data intact; dedup constraint rebuild.
**Exit:** old test suite still green; migrations idempotent.

### Phase 2 — Telegram registration + admin controls
**Files:** `backend/app/users.py` (new), `bot.py`.
- `/start` rewrite: unknown chat → insert `pending`, reply "awaiting approval"; `pending` → status msg; `disabled` → "contact admin"; `approved` → welcome + `/app` webapp hint + `/prefs` tip.
- **Admin commands** (gated by owner): `/users`, `/approve <id|@name>`, `/reject`, `/disable <id>` (full lockout), `/enable <id>`, `/cap <id> add|remove <capability>` (granular feature control — e.g. `/cap 123 add email_alerts`, `/cap 123 remove preferences`), `/alertdelay <minutes>` (sets `delayed_alert_minutes`).
- `authorized()` → `user_status(chat_id) == 'approved'`; owner stamped from env at startup (`ensure_owner`); `has_cap()` gates each command surface.
**Tests:** status machine, admin-only gates, capability add/remove, delayed default.
**Exit:** `/start` registers; approval unlocks; `disable` locks instantly; `/cap` removes individual features per user.

### Phase 3 — Web registration + admin web page
**Files:** `frontend/app/register/page.tsx`, `app/(app)/users/page.tsx`, `routes.py`, `lib/api.ts`.
- `POST /api/auth/register` `{display_name, email, telegram_chat_id?}` → `pending` row (409 on duplicate id/email). Web-only users register with email.
- Admin page: table of users (type, status, capabilities, last login) with approve/reject/disable/enable buttons, **per-capability checkboxes** (mirrors `/cap`), and the `delayed_alert_minutes` setting.
**Tests:** register 409s, admin approval + capability toggle via web reflects in DB.
**Exit:** a web-only pending user exists; admin approves and tunes capabilities from web or Telegram; both stay in sync.

### Phase 4 — Login + sessions + frontend guard
**Files:** `backend/app/auth.py` (new), `routes.py`, `config.py` (add `SECRET_KEY`), `frontend/app/login/page.tsx`, `frontend/middleware.ts`, `lib/api.ts`, `telegram-bridge.tsx`.
- `POST /api/auth/telegram-webapp` (initData HMAC), `/api/auth/login` (OTP), `/api/auth/verify`, `/api/auth/login-email`, `/api/auth/verify-email`, `/api/auth/logout`, `/api/auth/me`.
- `get_current_user` dependency replaces `DEFAULT_USER_ID` across routes/matcher/notify/poller; `has_cap(user, cap)` enforced per route.
- Frontend middleware protects `/(app)/*`; `/login` offers "Continue with Telegram" (webapp) or chat-id/email OTP.
**Tests:** 401 without cookie, 403 for pending/disabled, 5-attempt OTP cap, HMAC verify vector, cookie issue/expiry.
**Exit:** approved user logs in all three ways; web-only user logs in via email; disabled user is blocked.

### Phase 5 — Telegram write commands (`/prefs` family)
**Files:** `bot.py`, `matcher.py` (parametrize `sync_preferences`/`load_preferences`/`recompute_matches` by user), `routes.py`.
- Implement the command table from §7.2: `/preferences`, `/prefs <key> <value>`, `/prefs clear`, `/prefs notify-*`, `/prefs scope`, `/prefs frequency`, `/subscribe`, `/unsubscribe`, `/prefs-nl` (AI, §8.2).
- All commands share `PUT /api/preferences`-equivalent write path → `recompute_matches(user_id)`; each gated by `preferences` capability.
**Tests:** each command writes the right column; capability check (no `preferences` cap → 403-ish reply); commands as an approved user vs pending.
**Exit:** a Telegram user can set every preference and notification setting via commands; web and bot read the same DB row.

### Phase 6 — Web-only read-only enforcement
**Files:** `routes.py`, `frontend` (hide write controls when `permissions` say read-only).
- `GET /api/auth/me` returns `{permissions}`; UI hides Preferences edit (unless `preferences` capability), hides notification settings, hides admin nav.
**Tests:** web-only user gets 403 on pref write; read endpoints OK.
**Exit:** dashboard works for web-only users; no write path leaks.

### Phase 7 — Tiered notification queue
**Files:** `poller.py`, `notify.py`, `telegram/notifications.py`, new `drain_queue` (in poller or scheduler).
- Poller replaces direct sends with queue inserts (batch, one upsert per user per channel): `fast_alerts` users `now`, others `now + delayed_alert_minutes`. **Users without the matching alert capability, web-only, or `notify_*`=false are skipped.**
- Drain worker sends due rows via existing per-channel senders; marks `sent` + `notifications_sent`.
- Owner path unchanged in effect (has `fast_alerts`).
**Tests:** immediate vs delayed scheduling unit tests; drain idempotency; retry/failed after 3 attempts; web-only and cap-less users never queued.
**Exit:** `fast_alerts` user gets instant alerts; standard user gets the same alert 30/60 min later; removing `email_alerts` stops email but not Telegram; per-user dedup holds.

### Phase 8 — Account linking
**Files:** `routes.py` (`POST /api/auth/link/telegram`, `POST /api/auth/link/email`, verify endpoints), `bot.py` (link-code DM), `notify.py` (email link-code), Settings UI (`frontend/app/(app)/settings/page.tsx`).
- Web user links Telegram (bot DMs code) → becomes "linked" → gains `telegram_alerts` (and full access) at their tier.
- Telegram user links email (Resend code) → gains `email_alerts` and can log in via email OTP.
**Tests:** link-proof-of-ownership (wrong chat/email never links), both directions, duplicate-link 409, capabilities updated on link.
**Exit:** web→tg and tg→web linking both work; alerts start/stop at the right points.

### Phase 9 — AI layer (optional, efficient)
As §8.4 → §8.2 → §8.3 in that order (admin screening, NL prefs, match explanations). Each independent.

## 10. My efficiency advice (beyond the flows)

1. **Queue-driven alerts are the big win** — they implement the privilege delay tier as a side effect, batch sends into one drain pass, and stop the poll loop from doing network I/O to Telegram/Resend. Piggyback the drain on the existing scheduler ticker.
2. **Jobs stay global; only matches/alerts per user** (D8). One ingest serves N users — do not fork storage per user.
3. **Stateless signed cookies** — no session table, no per-request DB hit. Optionally cache `users.status` in a 30s TTL dict to avoid a DB read on every bot command.
4. **Batch all user-scoped SQL** — resolve users once per poll; drain due queue with one `select`; upsert queue rows in batches; reuse the existing pooled `query()` path.
5. **Keep the sentinel→owner mapping** so nothing existing breaks; old code paths that read "the user" now read `get_current_user` — one mechanical change.
6. **Delay tier actually smooths load** — `fast_alerts` sends are few; delayed sends spread naturally; avoid adding another queue technology (Redis/Celery) until profiling demands it (AGENTS.md §3).
7. **Linking reuse** — the same `login_codes` primitive covers OTP login AND linking; one table, one expiry policy, less code.
8. **One write path for web + commands + webapp** — `/prefs <key> <value>` and the Mini App both call the same `PUT /api/preferences`-equivalent service. No duplicated logic to keep in sync.
9. **Capabilities = one `text[]` column** — add/remove features with a single array update; no schema churn for each new feature flag.
8. **AI first rules**: deterministic → AI, cache everything, batch, `to_thread`, JSON schema + fallback, cheap model. Never let an LLM sit on a per-poll critical path.

## 11. Security & edge cases

- **OTP/link codes**: 6-digit, single-use, 5-min expiry, 5-attempt cap, rate-limited (`/api/auth/*` per IP+chat/email). Never log codes.
- **Session**: httpOnly, `SameSite=Lax`, `Secure` in prod, signed fail-closed. `SECRET_KEY` added to `.env.example`.
- **initData auth**: verify HMAC-SHA256 (bot token) + `auth_date` recency (≤24h). Never trust `initData` client-side.
- **No enumeration**: login returns 202 for unknown/pending/approved; the DM/email is the only signal.
- **Approval is the gate**: every sensitive path checks `status == 'approved'` and the permission helper server-side. Never trust frontend.
- **Web registration spoofing**: registering someone else's chat id creates a `pending` row; approval targets the typed id, so the admin verifies in `/users` before approving.
- **Recompute cost**: `recompute_job_matches(user_id)` per user, only on pref change, never every poll; defer incremental recompute until profiling shows it matters.
- **RLS**: still not needed (self-hosted, all server-side); revisit only for public multi-tenant hosting.

## 12. Testing strategy

- **Unit**: status machine, capability add/remove (`/cap`, admin page), tier scheduling (`fast_alerts` vs delayed), OTP/link code lifecycle, HMAC initData verification, cookie signing, per-user dedup, queue drain idempotency + retry, `has_cap` matrix, `/prefs` command parsing → column mapping.
- **API**: 401/403 matrix (anonymous / pending / approved / disabled), web-only read-vs-write, per-capability 403s, admin endpoints, linking both directions.
- **Bot**: `/start` transitions, admin commands incl. `/cap`, `/prefs` family writes, blocked commands for missing capabilities, link-code DM.
- **Frontend**: middleware redirect, login via all three methods (mocked), register validation, read-only/capability-based UI hiding, Mini App bridge.
- **Fixtures** for LLM responses (never a live model in tests).
- **Live smoke**: owner + 2 Telegram accounts + 1 web-only user → register, approve, link, log in, verify `fast_alerts`=instant vs standard=delayed alerts; revoke a capability and confirm the feature disappears.

## 13. Definition of done

- Migrations 022/023 apply cleanly on fresh and existing DBs (no data loss, FKs valid).
- No one can log in, call APIs, or use bot commands without an approved account.
- Web-only users get a read-only, preferences-filtered dashboard and no alerts.
- Telegram/linked users get full read+write via webapp, browser, **and Telegram commands** (every preference + notification setting has a `/prefs` command).
- `fast_alerts` users get immediate alerts; others delayed by the admin-set value.
- Admin can disable any user individually (full lockout) **and** remove individual features via capabilities (`/cap` or admin page).
- Linking works both directions and gates alerts correctly.
- AI features are opt-in, cached, async, and degrade to deterministic behavior.
- Ruff clean; unit + API suites green; frontend build passes.

## 14. Out of scope (for now)

- Supabase Auth / RLS, email verification beyond codes, passwords/2FA.
- Per-user ATS/source selection, quotas, billing.
- A separate notification microservice/worker (queue lives in Postgres until profiling says otherwise).
