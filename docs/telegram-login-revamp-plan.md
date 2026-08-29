# Telegram-First Login Revamp — Plan

> **Status:** Proposal — replaces the current email-only + "already linked" Telegram MiniApp login with a true Telegram-first onboarding, preserving email as an alternative. Covers both ideas you raised (OAuth-like "Connect Telegram" + manual chat-id) and recommends a hybrid that is best for users and for us.

---

## 1. Goal

Change login from the current state:

- `register` requires email (optionally password) → locked until payment
- `login` offers email-password OR emailed 6-digit code
- Telegram `initData` login exists but **requires the account to already be linked** (`login-telegram` returns 403 if not linked) and only works inside the Telegram Mini App

To:

> **"Connect with Telegram like Google"** — one tap creates/links your account, then a short initial setup collects name + email (optional) + preferences. Manual `telegram_chat_id` typing remains only as a low-priority fallback for edge cases.

Additional guarantees:
- A user who logs in via Telegram is immediately able to receive Telegram alerts (no separate "link" step).
- Email-only users can still register/log in and later link Telegram in one tap.
- No enumeration, no spoofing of someone else's Telegram account, no blocking of the poller/bot if one identity check fails.

---

## 2. Current state (verified)

- **Auth** (`backend/app/auth.py:1`): PBKDF2 passwords, signed session cookie (`jobradar_session`), OTP `login_codes` table, `verify_init_data` for MiniApp initData (HMAC with `WebAppData`). No Telegram Widget verification.
- **Routes** (`backend/app/api/auth_routes.py:193`): `POST /api/auth/login-telegram` — `verify_init_data(...)` → `fetch_user_by_telegram(id)` → **403 if not linked**. No auto-creation, no widget handler.
- **Users** (`backend/app/users.py:116`): `create_registered_user` requires email; telegram fields (`telegram_chat_id`, `telegram_user_id`, `telegram_username`) remain null until linked elsewhere.
- **Bot** (`backend/app/telegram/bot.py:88`): `authorized(chat_id)` checks `settings.telegram_chat_id` — **single-user** check. `dispatch_command` + `handle_update` still reference `DEFAULT_USER_ID` for queries; multi-user bot will reject everyone except the owner.
- **Frontend** (`frontend/app/login/page.tsx:26`): MiniApp auto-login is best-effort fallback; the visible UI is password/code Tabs only. No Telegram button outside the Mini App. `register/page.tsx:19` is email+password only.
- **Onboarding** (`frontend/app/(app)/onboarding/page.tsx:64`): preferences only; no name/email completion step.

**Pain points the revamp fixes:**
1. Telegram login cannot onboard new users — it only authenticates those you have manually linked via DB.
2. Email is mandatory; many users coming from Telegram don't want to type an email to start.
3. Manual `chat_id` proposal is friction (users don't know their id) and requires ownership proof anyway.
4. Bot still enforces single-user authorization, so even if you linked two accounts the bot would refuse the second.

---

## 3. Telegram auth primitives — which mechanism maps to which proposal

Your two ideas correspond to two real Telegram mechanisms plus the manual-id fallback. There is no "one official Google-equivalent" — Telegram offers two first-class ways to prove identity outside the bot:

### 3.1 "Connect with Telegram like Google" → **Telegram Login Widget**

Spec: <https://core.telegram.org/widgets/login>

- Frontend embeds `https://telegram.org/js/telegram-widget.js?22` and renders a `Log in with Telegram` button bound to your bot's username.
- User clicks → Telegram auth popup (or Telegram mobile app) → upon allowing, Telegram redirects/calls your `data-onauth` handler with a data dict: `{id, first_name, last_name, username, photo_url, auth_date, hash}`.
- Backend verifies `hash` = `HMAC-SHA256(data_check_string, SHA256(bot_token))` and checks `auth_date` freshness (≤24h). This cryptographically proves ownership of that Telegram account — same trust level as "Sign in with Google".
- Requires one BotFather setup: `/setdomain` → your frontend domain (e.g. `dashboard.example.com` or `localhost`). Fails closed if domain not whitelisted.
- Works on **any web surface outside Telegram** (desktop and mobile browsers). No need to have started the bot, but sending alerts still requires `user has started bot` (Telegram delivery prerequisite).

**Mapping:** This is proposal 1 ("connect with telegram account directly just like we do with google") in pure web form.

### 3.2 "Connect directly to this bot in their app" → **Bot Deep Link login**

Spec: <https://core.telegram.org/bots/features#deep-linking> + `start` parameter

- Frontend generates a short random `nonce` (e.g. 32 hex chars) via `POST /api/auth/telegram/nonce` → receives `{nonce, link: https://t.me/<bot>?start=login_<nonce>, expires_at}`.
- Frontend shows a big button `Open in Telegram` (link) + QR for desktop + polling indicator ("Waiting for confirmation…").
- User taps link → Telegram opens bot chat with `Start` pre-filled → bot receives `/start login_<nonce>` → looks up nonce, binds `telegram_user_id`, `telegram_chat_id`, `telegram_username`, marks nonce as `authenticated`.
- Frontend polls `GET /api/auth/telegram/poll?nonce=…` (or SSE/long-poll) every 2s; when authenticated it calls `POST /api/auth/telegram/consume` (cookie is set) or the poll response already sets the session cookie via token exchange.
- Deep link proves the user **controls the Telegram app** and **has started the bot**, so notification delivery is guaranteed from minute zero.

**Mapping:** This is proposal 1 variant ("connect directly to this bot in their app instead of whole telegram login"). It is especially good on mobile where the widget's popup is awkward.

### 3.3 "Ask them to add the telegram chat id" → **Manual chat_id + OTP proof**

- Frontend asks for numeric `chat_id` (or `@username`) → backend looks up user with that id → DMs a 6-digit code → user types code on web → link verified.
- This is what you described as proposal 2 ("add the telegram chat id with the initial setup").

**Properties:** Most friction, most error, users don't know their id (needs `/getid` command or @userinfobot), and name-typing already proves ownership-of-id weaker than cryptographic hash/nonce. Still implementable as a hidden fallback but not a primary.

### Decision matrix

| Criterion (weight →) | UX (★★★) | Mobile | Desktop | Can deliver alerts immediately | Dev complexity | Ops extra | Blocked-by-adblock | Security |
|---|:---:|---|---|---|---|---|---|
| **Widget** | 5/5 | 3 | 5 | 3 (needs extra /start) | medium (verify hash, domain) | `/setdomain` must be set | yes (rare) | HMAC proof |
| **Deep Link** | 4/5 | 5 | 3 | 5 | medium (nonce + bot handler) | none | no | nonce proof |
| **Manual chat_id+OTP** | 2/5 | 2 | 2 | 4 | low | none | no | OTP proof, but enumerable |

---

## 4. Recommended approach — **Hybrid Widget + Deep Link, manual id only as fallback**

Offer **both first-class Telegram methods** under one hero section, then email as secondary. This covers your two ideas without forcing a false choice:

```
┌────────────────────────────────────────────┐
│           Continue with Telegram           │
│                                            │
│  [🔷 Log in with Telegram]  ← Widget       │  desktop primary
│  ─────────── or ───────────                │
│  [✈️ Open in Telegram app]  ← Deep Link    │  mobile primary + fallback
│              ↓ QR on desktop               │
│                                            │
│  ────────── or continue with email ─────── │
│  [Email + Password]   [Email code]         │
│  [Create account with email]               │
└────────────────────────────────────────────┘
```

**Post-Telegram, the initial setup you requested (`backend/app/users.py:116` concern):**

- If `POST /api/auth/telegram-...` identifies a **new** Telegram user → auto-create account on the spot (no email required):
  ```sql
  insert into users(email, display_name, telegram_user_id, telegram_chat_id,
                    telegram_username, role, status, access_locked)
  values (null, telegram_first_name, tg_id, tg_id, tg_username, 'user', 'approved', true)
  ```
  Then issue a session cookie and redirect to `/onboarding?new=telegram` (your "initial setup").

- Initial-setup modal/page (`/onboarding` or new `/welcome`) pre-fills name from Telegram `first_name` + `last_name`, asks for:
  - Display name (required, prefilled)
  - Email (optional but prompted — "Add email to enable email alerts & password recovery")
  - Preferences shortcut (reuse existing presets)
  - Scope toggles (`notify_telegram: true` default)

- If the Telegram account matches an **existing** email user (by `telegram_user_id` or `telegram_username`), link instantly: update that user's telegram columns, then log in. If the Telegram id is already linked to a *different* account, surface a conflict ("This Telegram account is already linked to another profile") with a link to merge/support.

- Email users can later tap the same Telegram hero in **Settings → Connected accounts** to link.

**Why manual chat_id is not the primary (recommend keeping it but de-emphasized):**

- Users don't know their id; asking for it creates support load.
- Verifying ownership still needs the OTP DM, so typing the id saves nothing over the widget/deep-link flows (which verify ownership in one tap *without* an extra code).
- Input is spoofable: anyone can paste another person's id before verification; widget/nonce flows are non-spoofable (hash/nonce ties to a Telegram session).
- **Keep as fallback only:** under "Having trouble?" → collapsed panel with `chat_id` input + `Send code to Telegram` → verify; reuses existing `login_codes` table and requires exactly the code you planned as proposal 2. This satisfies the "ask them to add chat id with initial setup" request without making it the main path.

---

## 5. Detailed flows

### 5.1 Widget flow (web → telegram auth → web)

1. User visits `/login` → component mounts, `telegram-widget.js` renders button (domain must be allowlisted).
2. User clicks widget → Telegram auth window → grants → JS handler `onTelegramAuth(user)` receives data object.
3. Handler calls `POST /api/auth/telegram/widget` with the data object as JSON.
4. Backend `verify_telegram_widget(bot_token, data)` → on success, upsert-or-login logic:
   - if `telegram_user_id` exists → log in (touch_login, set cookie)
   - else if `email` present and matching row exists (future: `email` may come from Telegram via manual email addition?) -> link and log in
   - else create new user (seed preferences, access_locked per current billing) → set cookie
5. Return `{ok, user, is_new}` → frontend routes `is_new` to onboarding, otherwise to `/dashboard` or `/unlock` if locked.
6. Post-login, show banner if `bot_started == false`: "Tap /start in Telegram to enable alerts" with a deep link.

### 5.2 Deep-link flow (web → Telegram bot → back to web)

1. User clicks `Open in Telegram app` → calls `POST /api/auth/telegram/nonce` → `{nonce, expires_at, link}`.
2. Frontend shows `Waiting…` and starts `GET /api/auth/telegram/poll?nonce=…` every 2 s (or 30 s SSE). Also shows QR (link encoded) for desktop → phone continuation.
3. User → Telegram → taps Start → bot sees `/start login_<nonce>` → handler:
   ```py
   row = fetch_login_token(nonce)
   if row.expired or row.consumed: reply "Expired link"
   else: update telegram_login_tokens set telegram_user_id, telegram_chat_id, telegram_username, authenticated_at
         reply "✅ Linked! Return to the site — you're logged in."
         # optionally call backend to pre-associate
   ```
4. Next poll sees authenticated row → backend verifies not expired/consumed, then same upsert-or-login as widget → sets session cookie on `POST /api/auth/telegram/consume` (or poll returns a one-time session token that the frontend exchanges).
5. Poll stops → redirect like widget.

**Nonce lifecycle table** (`telegram_login_tokens`): `id uuid pk`, `token text unique`, `telegram_user_id bigint`, `telegram_chat_id bigint`, `telegram_username text`, `initiated_by_ip text`, `created_at timestamptz`, `expires_at timestamptz` (5 min), `authenticated_at timestamptz`, `consumed_at timestamptz`, `session_consumed_by uuid`. Single-use; expired rows cleaned by cron.

### 5.3 Email flow (unchanged in cost, new placement)

- Keep `POST /api/auth/login-password` and `POST /api/auth/login` + `verify` exactly as-is (`backend/app/api/auth_routes.py:107`).
- Move email UI below the Telegram hero as a collapsed alternative ("Continue with email"). Add a small `Info` line: "Email users can link Telegram later from Settings for mobile alerts."
- Registration via email still exists at `/register`; after register, show `Link Telegram` hero to encourage alerts.

### 5.4 Linking an email account to Telegram (settings)

- In Settings → Connected accounts, same hero appears. Both widget and deep link call `POST /api/auth/link/telegram` equivalents but behind `get_current_user` (authenticated). Server verifies widget hash / nonce and links by updating caller's `telegram_*` columns (check conflict: `tg_id` not already taken).

### 5.5 MiniApp initData flow (retain, but upgrade)

- Keep existing `verify_init_data` path, but modify `POST /api/auth/login-telegram` to **auto-create** when missing (like widget) instead of 403, to support true Telegram-in-app onboarding. Current tests rely on 403 — update them or keep a flag.

---

## 6. Backend changes

### 6.1 Migration

- **`028_telegram_login.sql`**
  - `telegram_login_tokens` table (above).
  - Optionally `alter table users add column telegram_photo_url text` (from widget).
  - Index `users_telegram_user_id` already exists via unique; keep.
  - No change to `login_codes`; keep for email + manual chat_id OTP.

### 6.2 `backend/app/auth.py`

- Add `verify_telegram_widget(bot_token, data_dict)` — implement Telegram Login Widget HMAC verification:
  ```py
  check_string = "\n".join(f"{k}={v}" for k,v in sorted(data.items()) if k != "hash")
  secret = hashlib.sha256(bot_token.encode()).digest()
  expected = hmac.new(secret, check_string.encode(), hashlib.sha256).hexdigest()
  ```
  + `auth_date` staleness (e.g. 86400s) + constant-time compare. Return normalized user dict or None.
- Add `generate_telegram_nonce()` helper and token helpers: `create_login_token(ip)`, `claim_login_token(token, tg_identity)`, `consume_login_token(token)`.
- Keep `verify_init_data` as-is but import widget verifier alongside.

### 6.3 `backend/app/api/auth_routes.py`

- New endpoints (all under `/api/auth`):
  - `POST /api/auth/telegram/widget` — body = widget data; rate-limit by IP; verify hash → upsert/login → set cookie → `{is_new, ...me}`
  - `POST /api/auth/telegram/nonce` — returns `{nonce, link, expires_at}`; rate-limit.
  - `GET /api/auth/telegram/poll?nonce=...` — returns `{status: "pending"|"authenticated"|"expired"|"consumed", ...}`; no auth.
  - `POST /api/auth/telegram/consume` — body `{nonce}`; verifies nonce authenticated & not consumed → login/create → sets cookie → 204.
  - `POST /api/auth/telegram/link/widget` — behind `get_current_user`; same widget verification but links caller.
  - `POST /api/auth/telegram/link/nonce/consume` analog for linking.
  - Legacy: keep `POST /api/auth/login-telegram` but change to auto-create (or gate behind feature flag `TELEGRAM_AUTO_CREATE=true`). Update its `_me_payload` path to include `telegram_linked`.

- Modify rate limits: widget/nonce endpoints per-IP (5/10 min), poll slightly higher.

### 6.4 `backend/app/users.py`

- New helpers:
  - `fetch_user_by_telegram_chat(chat_id)` (exists partially)
  - `create_user_from_telegram(supabase, tg_user: dict)` — inserts `display_name = first_name + last_name`, `telegram_*`, `email=None`, `access_locked` default, seeds preferences.
  - `link_telegram_to_user(settings, user_id, tg_identity)` — `update users set telegram_user_id, telegram_chat_id, telegram_username` with conflict check.
- `ensure_owner` and `fetch_user_by_telegram` handle both `telegram_user_id` and `telegram_chat_id` (they are often equal for private chats but distinct conceptually).

### 6.5 `backend/app/telegram/bot.py`

- Extend `/start` handler to parse `start_param`:
  - If `args.startswith("login_")` → handle nonce auth flow (above), not stats.
  - If plain `/start` → if user not in DB → auto-create (like widget) OR reply "Welcome — account created, open app to finish setup" depending on phase. Otherwise existing welcome + menu.
- Fix `authorized(chat_id, settings)` — replace single-id check with DB membership check:
  ```py
  def is_registered(chat_id): return query(..., "select 1 from users where telegram_chat_id=%s or telegram_user_id=%s", ...)
  ```
  plus `status != 'disabled'` gate. Keep owner (`settings.telegram_chat_id`) as super-admin bypass for backwards compat when DB empty.
- Dispatch must route queries by `user_id` (telegram caller) not just `DEFAULT_USER_ID`; reading/writing job_matches etc. becomes per-user where relevant (already handled via user_id param in many queries, but verify).
- Add helpers `_handle_login_nonce` + success/error messages.

### 6.6 Config (`backend/app/config.py`, `.env.example`)

- New env: `TELEGRAM_BOT_USERNAME` (derived from token if not set, but needed for deep links), `TELEGRAM_LOGIN_DOMAIN` documentation, `TELEGRAM_WIDGET_TIMEOUT_SECONDS`, `TELEGRAM_NONCE_TTL_MINUTES=5`.
- Document `/setdomain` requirement in `.env.example`.

---

## 7. Frontend changes

### 7.1 `/login` revamp (`frontend/app/login/page.tsx`)

- New hero above the email tabs:
  - Widget container: `<div id="telegram-login-root">` + script loader. Provide `data-onauth="onTelegramAuth(user)"` global handler.
  - Deep-link section: button `✈️ Open in Telegram app` → calls `api.createTelegramNonce()` → shows spinner + link + QR (`qrcode.react` or simple inline). Poll effect with backoff.
  - Error states: if widget script fails to load (domain not set), show "Domain not configured — use bot link" with deep link.
- Email tabs collapse below with label "or continue with email".
- After Telegram success: `refresh()` + redirect based on `is_new` or `needs_profile_completion` flag.

### 7.2 New onboarding step (`frontend/app/(app)/onboarding/page.tsx` + `/welcome`)

- Telegram-first users land here: prefill `name = tg.first_name`, prompt for display name + email (optional). Validate email uniqueness. Save via `PUT /api/me/profile` (new endpoint) or reuse `PUT /api/auth/register`-like upsert.
- Show presets selector as currently; Telegram hint changes to "You're connected — Telegram alerts are on."

### 7.3 Register page (`frontend/app/register/page.tsx`)

- Add Telegram hero at top ("Recommended: Connect Telegram first") with same widget/deep link; email form below.

### 7.4 Settings / Billing / Sidebar

- `lib/api.ts` — add methods: `telegramWidget(data)`, `createTelegramNonce()`, `pollTelegramNonce(nonce)`, `consumeTelegramNonce(nonce)`, `linkTelegramWidget(data)`, `updateProfile(payload)`.
- `components/sidebar.tsx` — show Telegram connected indicator (photo, username) vs. "Link Telegram" CTA.
- Bot fallback panel in settings: "Having trouble? Enter chat id manually" — shows input + send-code flow if needed.

### 7.5 `telegram-bridge.tsx`

- Keep MiniApp bridge; add auto-login via `verify_init_data` auto-create path (to match web flow).

---

## 8. Security & edge cases

- **No enumeration:** widget/consume endpoints return same timing whether new or existing user. Poll always 200 with generic status.
- **Hash freshness:** reject widget `auth_date` > 24 h old; reject nonce `expires_at < now()` and `consumed_at not null`.
- **Single use:** nonce `consumed_at` stamp; widget login is idempotent but poll consume only once.
- **Rate limits:** per-IP + per-telegram-id where applicable; reuse `rate_limit` helper (`backend/app/auth.py:233`).
- **Conflict:** `telegram_user_id` unique — honest error "already linked to another account" (user-facing), with support/admin-merge path (do not auto-merge).
- **Alert delivery:** right after linking, user must have `telegram_chat_id` === `telegram_user_id` (for private chats) and `users.capabilities` includes `telegram_alerts`; notify drain honors it (`backend/app/main.py:119`).
- **Domain:** document `/setdomain` failure mode; degrade to deep-link only if widget blocked.
- **Supabase RLS:** not needed yet (self-hosted); guard with `require_product_access`.
- **Secrets:** `TELEGRAM_BOT_TOKEN` stays server-side; widget verification reuses same token.

---

## 9. Implementation phases (incremental, each independently testable)

**Phase 1 — Migration + auth verifier (backend-only, no UI)**
- `028_telegram_login.sql`, `verify_telegram_widget` helper (+ unit test vectors from Telegram docs). Old suite stays green.

**Phase 2 — Backend endpoints (widget + nonce + poll + consume)**
- `auth_routes.py` new routes, `users.py` create/link helpers. Integration tests with mocked BotFather data. No frontend yet.

**Phase 3 — Bot deep-link start handler + authorized fix**
- `bot.py` `/start login_<nonce>` path, per-user `is_registered` authorization. Manual QA with real bot + nonce.

**Phase 4 — Frontend hero on /login + /register**
- Login hero (widget + deep link + poll), `lib/api.ts` additions, domain-error handling. Cypress/Vitest for widget callback, poll mock.

**Phase 5 — Initial-setup onboarding**
- Auto-create + `/welcome` or expanded onboarding, profile-completion API. E2E: widget → new user → name/email prompt → preferences.

**Phase 6 — Linking & manual-id fallback (settings)**
- Connected-accounts UI, linking endpoints, collapsed manual `chat_id → code` fallback (reuses `login_codes`).

**Phase 7 — Hardening**
- Rate-limit tuning, expiry sweeps for `telegram_login_tokens`, observability (log `telegram_login: widget|nonce`), RLS/docs update.

---

## 10. What we will NOT do (explicit non-goals)

- No password requirement for Telegram users (password stays optional, set later via `POST /api/auth/password`).
- No Telegram OAuth `allow_write_access` hijack — we request only identity.
- No Redux of the matching/alert system; only identity plumbing changes.
- No deletion of email flow — email remains for non-Telegram users.

---

## 11. Recommended next action

Build **Phase 1 + 2** (migration + widget verifier + nonce endpoints) first — that unblocks the entire UI and can be tested headlessly with mocked Telegram payloads. Then wire the frontend hero and the bot handler (Phases 3–4).

### Open questions (need your decision before coding)

1. **Should Telegram-first account creation be open (anyone who proves a Telegram identity gets an account) or still gated (needs admin approval / payment)?** Today `access_locked=true` but `status=approved`; we will keep the same gate for the new flows (new Telegram accounts start `approved + locked`, unlock via subscription/coupon) — confirm?
2. **Domain for the widget:** what is the deployed frontend domain where we should run `/setdomain`? For localhost testing we can skip widget and use deep link; production widget won't work without this. Provide the domain or say "deep-link only for now".
3. **Keep email optional for Telegram users?** Recommendation: yes (allow `email = null` on auto-create, then prompt but allow skip). The drain/email channel simply never queues if email is null.

> Once you confirm the three questions, I'll mark the plan as approved and implement Phase 1–2 immediately (one focused PR per phase).

---

## 12. How to tell the plan succeeded

- `POST /api/auth/telegram/widget` with a valid Telegram hash creates a user on first call, logs in on second, and never leaks whether the id existed.
- Deep link `GET telegram_login_tokens` row transitions `pending → authenticated → consumed` with correct TTL and single-use guarantee.
- `/start login_<nonce>` sent from the Telegram app authenticates the matching web session in ≤5 s.
- A user who completes the initial setup (name + optional email) receives Telegram alerts on the next poll; an email-only user can add Telegram later from Settings in one tap.
- Old `login-password` / email-OTP still works; existing users are unaffected; `ruff` + `pytest` remain green.

