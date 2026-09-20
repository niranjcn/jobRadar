-- Item 35/36: remove OTP and Telegram-login artifacts.
-- Login is now strictly email+password (PBKDF2 600k). Telegram remains for *notifications* (telegram_chat_id),
-- but not for authentication. Drop the two tables and their indexes, plus the redundant token index.

drop table if exists login_codes;
drop table if exists telegram_login_tokens;

-- Users table: keep telegram_chat_id (for alerts, set via preferences), drop login-only columns
alter table users drop column if exists telegram_user_id;
alter table users drop column if exists telegram_username;
alter table users drop column if exists telegram_photo_url;

-- The remaining telegram_chat_id keeps its unique index for alerts (one chat per user)
-- No retention needed for dropped tables; auth_events retention handled separately
