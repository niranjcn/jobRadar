-- Schedule management: per-ATS poll interval overrides that can be set at
-- runtime (on top of the env-based defaults) and source health tracking.

create table if not exists poll_schedule (
    ats_type text primary key,
    interval_seconds int not null,
    updated_at timestamptz not null default now()
);

alter table sources add column if not exists last_error text;