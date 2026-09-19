# Plan — Telegram-First JobQuest (Mini App Only)

**Date:** 2026-08-28
**Owner:** Admin chat ID from env (`ADMIN_CHAT_ID` = your `TELEGRAM_CHAT_ID`)
**Source of truth:** This doc + `AGENTS.md:24` rule 11 (explain simply but keep technical accuracy)

---

## 1. What You Asked For (in plain English)

You want JobQuest to live **completely inside Telegram**. No separate website login.

*   **You are the single owner (admin).** Your chat ID is set in `backend/.env` as `ADMIN_CHAT_ID`. Only you can see all users and make someone “privileged”.
*   **Everyone else** who taps `/start` on your bot is instantly a **normal user**. Their Telegram `chat_id` is saved, they get a welcome, and they can immediately use the Mini App.
*   **Privileged** is a special tier you grant (family/friends). You can turn it on/off for any user.
*   **Delay:** You get new jobs instantly (0 min). Privileged get them after X minutes (e.g., 30m). Normal get them after Y minutes (e.g., 360m = 6h). You set X and Y once for everyone in that tier (per-tier, not per-person).
*   **Preferences:** Every chat ID has its **own** preferences (roles, keywords, locations, etc.). They set it themselves in the Mini App, and only **their** matched jobs go to **their** chat. You can view but not edit their prefs.
*   **Mini App only:** Users never open `localhost:3000` in a browser. They tap a button in Telegram that opens your Next.js app *inside* Telegram. You as admin see an extra “Users” tab there.

**Technical translation:** We move from single-user (one `preferences` row, one `chat_id` env) to multi-user (one row per `chat_id`, queue per user with `scheduled_for = first_seen + tier_delay`).

---

## 2. How It Will Work (User Flows)

### A. New user joins
```
User -> Telegram -> /start
  -> Bot captures chat_id, username, first_name
  -> Creates row in `users` (role=normal, delay = normal_delay)
  -> Sends welcome: "Welcome to JobQuest. Open Mini App to set preferences."
  -> Mini App button appears below chat
```

### B. User sets preferences (Mini App)
```
User taps "Open Radar" (Mini App)
  -> Frontend loads inside Telegram, gets `Telegram.WebApp.initData` (signed by Telegram)
  -> Sends initData to backend `POST /api/miniapp/auth` -> backend validates with bot token, returns user
  -> Showstabs: Jobs | Matches | Preferences
  -> User edits roles/keywords/locations, hits Save -> `PUT /api/preferences` with chat_id from initData
```

### C. New job arrives
```
Poll fetches Stripe job (Greenhouse)
  -> For each user, check if job matches *their* preferences (via `match_and_enqueue` per user)
  -> If match, insert into `notification_queue` with:
     - admin: scheduled_for = now
     - privileged: scheduled_for = now + 30m
     - normal: scheduled_for = now + 360m
  -> Every 30s `drain_due_notifications` sends due rows via Telegram to that chat_id
```

### D. Admin manages users (Mini App, admin only)
```
You open same Mini App (your chat_id == ADMIN_CHAT_ID)
  -> Backend sees you are admin, returns extra tab: Users
  -> Users tab shows table: chat_id, name, role (normal/privileged), joined, prefs summary
  -> For any row: [Make Privileged] / [Make Normal] button
  -> Top controls: "Privileged delay: [30] min" , "Normal delay: [360] min" -> saves to `app_settings`
```

---

## 3. Mini App Setup (How to Host It)

You already have the Next.js frontend. Mini App is **the same app**, just opened inside Telegram.

**What Telegram needs:**
1.  **HTTPS URL** — Mini App must be `https://` (Telegram blocks `http`). Options:
    *   Deploy `frontend` to Vercel/Render (you already have `render.yaml` for backend) — get `https://jobquest.vercel.app`
    *   For local testing, use `ngrok` or `cloudflare tunnel`: `ngrok http 3000` -> gives `https://abc.ngrok.io`
2.  **Tell BotFather:** In Telegram, message `@BotFather` -> `/mybots` -> your bot `JobQuestScannerbot` -> **Bot Settings** -> **Menu Button** -> set URL to `https://your-frontend/miniapp` (or `/`).
    *   Also `/setdomain` -> paste your domain (`vercel.app` or `ngrok.io`) so “Login with Telegram” widget works.

**What we build in code:**
*   `frontend/app/miniapp/page.tsx` (or reuse `app/page.tsx` with `if (window.Telegram?.WebApp)`)
*   Use `telegram-web-app` JS: `window.Telegram.WebApp.ready()` and `WebApp.initData` to authenticate.
*   Backend `POST /api/miniapp/auth` validates `initData` with `TELEGRAM_BOT_TOKEN` (HMAC SHA256 per Telegram docs) — no cookies needed.

---

## 4. Data Model Changes (What Changes in Postgres)

Current local DB (just migrated: `sources 201`, `jobs 180736`) is single-user. Changes:

*   `users` table already exists (1 row for you). Add/ensure:
    *   `chat_id` (bigint, unique) — Telegram chat ID
    *   `role` (enum: `admin` | `privileged` | `normal`)
    *   `created_via` (`/start`)
*   `preferences` already has `user_id` — will now have one row per `chat_id` (isolated). New users get empty prefs (match everything until they set, or we can copy a default).
*   `app_settings` new keys:
    *   `privileged_delay_minutes` (default 30)
    *   `normal_delay_minutes` (default 360)
*   `notification_queue` already has `user_id`, `scheduled_for`, `status` — we will set `scheduled_for = now + tier_delay` per user.
*   No change to `jobs`/`sources` — they stay global (all users share same job pool, just filtered per user).

Migration file: `029_telegram_multiuser.sql` (adds `ADMIN_CHAT_ID` handling, ensures admin user).

---

## 5. Backend Changes (Simple List)

*   **Env:** `ADMIN_CHAT_ID=1415590254` (your current `TELEGRAM_CHAT_ID`), plus `privileged_delay`/`normal_delay` in DB not env.
*   **Bot `/start`:** If `chat_id` not in `users`, insert `role=normal`. If `chat_id == ADMIN_CHAT_ID`, ensure `role=admin`. Send welcome.
*   **Auth for Mini App:** New endpoint `POST /api/miniapp/auth` validates `initData`, returns user, sets `request.state.user`.
*   **Preferences API:** Change `GET/PUT /api/preferences` to use `chat_id` from initData, not session cookie.
*   **Admin API:** `GET /api/admin/users` (admin only), `POST /api/admin/users/{id}/role`, `PUT /api/admin/delays`.
*   **Poller:** In `match_and_enqueue`, loop over all active users, compute `scheduled_for` per tier, insert per user. Admin `0`, privileged `+X`, normal `+Y`.
*   **Remove web auth:** Keep `JOBQUEST_REQUIRE_AUTH` but Mini App uses initData, not `SECRET_KEY` session.

---

## 6. Frontend Changes (Mini App Only)

*   Detect `window.Telegram?.WebApp` — if present, hide normal header, use Telegram theme colors, use `initData` for API calls.
*   Tabs for normal: `Jobs (filtered to their matches)`, `Matches`, `Preferences` (form with roles/keywords/locations).
*   Extra tab for admin: `Users` — table + delay controls + privilege toggle.
*   No separate “Login” page inside Mini App — auth is automatic via Telegram.

---

## 7. What We Keep vs Remove

*   **Keep:** `docker-compose.yml` with `postgres`+`postgrest` (local), `web` polling, `frontend` Next.js. All 180k jobs stay.
*   **Keep but hide:** Web dashboard at `localhost:3000` still works for local debugging, but normal users will never see it — they use Mini App.
*   **Remove later (optional):** Email notifications per user (keep Telegram only for now to simplify).

---

## 8. Steps to Build (in order, 1 task at a time)

1.  **Env + migration:** Add `ADMIN_CHAT_ID` to `.env`, create `029_...sql`.
2.  **Bot `/start`:** Capture `chat_id`, create `normal` user, welcome.
3.  **Mini App auth:** `POST /api/miniapp/auth` with initData validation.
4.  **Preferences per user:** Make `preferences` isolated, Mini App can save per `chat_id`.
5.  **Delay:** Add `app_settings` tier delays, update `match_and_enqueue` to set `scheduled_for` per tier.
6.  **Admin Users tab in Mini App:** `GET /api/admin/users` + toggle + delay controls (admin-only).
7.  **Deploy frontend to HTTPS + set in BotFather.**
8.  **Test with 2 accounts:** your admin (instant) + a normal (delayed) — verify same job arrives at different times.

---

## 9. Questions Already Answered

*   Single owner admin, per-tier delay, isolated prefs, mini app only, instant active — all captured above. No pending questions.

**Next:** If you say “approve this plan,” I will start at Step 1 and implement one task at a time, explaining simply but keeping the technical parts visible.
