-- Telegram-first login: nonce-based deep-link flow + widget data.
-- Supports hybrid Widget + Bot Deep-Link login alongside email.

-- Add photo URL column for Telegram avatar (available from widget).
alter table users add column if not exists telegram_photo_url text;

-- Store one-time nonces for the bot deep-link login flow.
-- Web generates a nonce, user opens t.me/<bot>?start=login_<nonce>, bot
-- marks it authenticated, web polls and then consumes it to create a session.
create table if not exists telegram_login_tokens (
    id uuid primary key default gen_random_uuid(),
    token text not null unique,
    -- Filled when the user taps Start inside Telegram
    telegram_user_id bigint,
    telegram_chat_id bigint,
    telegram_username text,
    telegram_first_name text,
    telegram_last_name text,
    telegram_photo_url text,
    initiated_by_ip text,
    created_at timestamptz not null default now(),
    expires_at timestamptz not null,
    authenticated_at timestamptz,
    consumed_at timestamptz,
    consumed_by uuid references users (id) on delete set null,
    -- Keep tokens short-lived; enforce check constraint for max 10 minutes
    check (expires_at <= created_at + interval '10 minutes')
);

create index if not exists telegram_login_tokens_expires_idx on telegram_login_tokens (expires_at);
create index if not exists telegram_login_tokens_token_idx on telegram_login_tokens (token);

-- Allow telegram-only users without email: email already nullable from 022,
-- but ensure index for case-insensitive lookup tolerates nulls (already unique).
-- No new constraint; auto-create from Telegram may have email = null.

-- Optional housekeeping: expired tokens older than 1 day are not needed.
-- No TTL job; the app lazily purges on read and can schedule cleanup.
