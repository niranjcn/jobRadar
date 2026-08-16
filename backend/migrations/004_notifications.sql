create table if not exists notifications_sent (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null,
    job_id uuid not null references jobs (id) on delete cascade,
    channel text not null check (channel in ('email', 'telegram')),
    sent_at timestamptz not null default now(),
    unique (job_id, channel)
);

create index if not exists notifications_sent_user_id_idx on notifications_sent (user_id);
create index if not exists notifications_sent_channel_idx on notifications_sent (channel);