-- Telegram-first multi-user: per-tier delays and admin bootstrap
-- Admin is single owner via ADMIN_CHAT_ID env. Privileged/normal are tiers.
-- Delays are per-tier (minutes) stored in app_settings.

insert into app_settings (key, value) values ('privileged_delay_minutes', '30'::jsonb) on conflict (key) do nothing;
insert into app_settings (key, value) values ('normal_delay_minutes', '360'::jsonb) on conflict (key) do nothing;

-- Ensure telegram_chat_id index exists for fast lookup on /start
create index if not exists users_telegram_chat_id_idx on users (telegram_chat_id);
create index if not exists users_role_idx on users (role);
