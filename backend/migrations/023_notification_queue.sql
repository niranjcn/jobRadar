-- Notification queue: alerts are enqueued the moment a job is matched, with
-- scheduled_for = enqueue time + the user's alert_delay_minutes. A drain
-- worker releases due rows, replacing the inline sends inside the poll loop.

create table notification_queue (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references users (id) on delete cascade,
    job_id uuid not null references jobs (id) on delete cascade,
    channel text not null check (channel in ('telegram', 'email')),
    scheduled_for timestamptz not null,
    status text not null default 'pending'
        check (status in ('pending', 'sent', 'failed', 'canceled')),
    attempts int not null default 0,
    last_error text,
    created_at timestamptz not null default now(),
    sent_at timestamptz,
    unique (user_id, job_id, channel)
);
create index notification_queue_due_idx on notification_queue (status, scheduled_for);

-- Faster match browsing per user.
create index job_matches_user_created_idx on job_matches (user_id, created_at desc);

-- Historical ledger entries become already-sent queue rows so nothing old is
-- ever re-alerted after the switch.
insert into notification_queue (user_id, job_id, channel, scheduled_for, status, sent_at)
select n.user_id, n.job_id, n.channel, n.sent_at, 'sent', n.sent_at
from notifications_sent n
on conflict (user_id, job_id, channel) do nothing;
