-- No more telegram-only accounts (per product decision).
-- Backfill the 2 existing NULL-email rows with deterministic placeholders,
-- then enforce NOT NULL. The UNIQUE on email already exists and will now be
-- truly unique (no more multiple NULLs).
update users set email = 'tg_' || coalesce(telegram_chat_id::text, id::text) || '@telegram.local', updated_at = now()
where email is null;

alter table users alter column email set not null;

-- Keep the case-insensitive index (already exists) for login lookups
-- No change to users_email_key (unique) – now truly unique
