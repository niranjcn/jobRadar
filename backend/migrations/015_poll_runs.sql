-- Poll run tracking + matched-only alert defaults.
--
-- poll_runs records every poll execution (scheduled or manual) so the UI can
-- show, for each run: how many jobs were fetched, how many were new, how many
-- matched, and how many alerts each channel actually sent.

create table if not exists poll_runs (
    id uuid primary key default gen_random_uuid(),
    triggered_by text not null default 'scheduled'
        check (triggered_by in ('scheduled', 'manual')),
    ats_type text,
    status text not null default 'running'
        check (status in ('running', 'completed', 'failed')),
    started_at timestamptz not null default now(),
    finished_at timestamptz,
    jobs_fetched int not null default 0,
    jobs_new int not null default 0,
    matches_considered int not null default 0,
    matches_new int not null default 0,
    telegram_sent int not null default 0,
    email_sent int not null default 0,
    sources jsonb not null default '[]',
    error text
);

create index if not exists poll_runs_started_at_idx on poll_runs (started_at desc);

-- Alert routing: both channels default to matched-only per product decision.
-- Also migrate any existing 'all' telegram scope to 'matched'.
alter table preferences alter column telegram_scope set default 'matched';
update preferences set telegram_scope = 'matched' where telegram_scope = 'all';