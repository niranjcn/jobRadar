-- MNC-grade auth hardening: lockout, password rotation tracking, verification placeholder
alter table users add column if not exists failed_login_attempts int not null default 0;
alter table users add column if not exists lockout_until timestamptz;
alter table users add column if not exists last_failed_at timestamptz;
alter table users add column if not exists password_changed_at timestamptz;
alter table users add column if not exists password_hash_updated_at timestamptz;

-- index for lockout checks & email lookups already exists on lower(email)
create index if not exists users_lockout_idx on users (lockout_until) where lockout_until is not null;

-- audit table for auth events (login success/failure, register, lockout)
create table if not exists auth_events (
    id uuid primary key default gen_random_uuid(),
    user_id uuid references users(id) on delete set null,
    email text,
    event_type text not null check (event_type in ('register','login_success','login_failure','lockout','password_change','logout')),
    ip text,
    user_agent text,
    created_at timestamptz not null default now()
);
create index if not exists auth_events_email_idx on auth_events (email, created_at desc);
create index if not exists auth_events_user_idx on auth_events (user_id, created_at desc);
