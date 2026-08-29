-- Users, roles, per-user delays, session OTP codes.
-- Purely additive: the existing sentinel user becomes the owner/admin account,
-- every existing user_id reference stays valid, preference data is unchanged.

create table users (
    id uuid primary key default gen_random_uuid(),
    telegram_chat_id bigint unique,
    telegram_user_id bigint unique,
    telegram_username text,
    email text unique,
    display_name text not null default '',
    role text not null default 'user'
        check (role in ('user', 'privileged', 'admin')),
    status text not null default 'approved'
        check (status in ('pending', 'approved', 'disabled')),
    capabilities text[] not null default '{}',
    -- admin-set per-user alert delay (minutes). 0 = instant.
    alert_delay_minutes int not null default 0,
    -- lifted by payment / coupon redemption / admin grant
    access_locked boolean not null default true,
    is_owner boolean not null default false,
    last_login_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

-- Owner: the historical sentinel identity. Unlocked + approved so the
-- existing single-user behavior is preserved exactly.
insert into users (id, role, status, access_locked, is_owner, display_name)
values ('00000000-0000-0000-0000-000000000001', 'admin', 'approved', false, true, 'owner')
on conflict (id) do nothing;

alter table preferences
    add constraint preferences_user_fk foreign key (user_id) references users (id);
alter table job_matches
    add constraint job_matches_user_fk foreign key (user_id) references users (id) on delete cascade;
alter table notifications_sent
    add constraint notifications_user_fk foreign key (user_id) references users (id) on delete cascade;

-- Per-user notification dedup (was global job_id+channel, single-user era).
alter table notifications_sent drop constraint notifications_sent_job_id_channel_key;
alter table notifications_sent
    add constraint notifications_sent_user_job_channel_key unique (user_id, job_id, channel);

create table login_codes (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references users (id) on delete cascade,
    channel text not null check (channel in ('telegram', 'email')),
    code text not null,
    expires_at timestamptz not null,
    attempts int not null default 0,
    used_at timestamptz,
    created_at timestamptz not null default now()
);
create index login_codes_user_idx on login_codes (user_id, used_at);
create index login_codes_open_idx on login_codes (expires_at) where used_at is null;
