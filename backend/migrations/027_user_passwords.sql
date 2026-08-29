-- Optional password login alongside email OTP codes.
-- password_hash is nullable: accounts without one keep using the code method.

alter table users add column if not exists password_hash text;

-- fetch_user_by_email matches on lower(email); give it an index.
create index if not exists users_email_lower_idx on users (lower(email));
