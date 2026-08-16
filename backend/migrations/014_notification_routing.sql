-- Per-channel notification routing.
--
-- Each channel gets a scope that controls WHAT it sends:
--   'all'     -> every newly discovered job (current Telegram behavior)
--   'matched' -> only jobs that match the user's preferences (current email
--                behavior)
--
-- Defaults preserve today's behavior so existing rows are unaffected.

alter table preferences add column if not exists telegram_scope text not null default 'all';
alter table preferences add column if not exists email_scope text not null default 'matched';