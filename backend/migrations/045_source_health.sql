-- Source health tracking (item 29): split the ambiguous last_checked_at
-- (which advances on failures too) into success/failure timestamps plus
-- counters the scheduler and triage can actually use. All nullable/zeroed:
-- honest unknown until the first poll writes them, no backfill invented.
-- consecutive_empty_runs (fetched nothing) is distinct from quiet_runs
-- (fetched plenty, nothing new); errors never touch the empty counter.

alter table sources add column if not exists last_success_at timestamptz;
alter table sources add column if not exists last_failure_at timestamptz;
alter table sources add column if not exists consecutive_failures int not null default 0;
alter table sources add column if not exists consecutive_empty_runs int not null default 0;
alter table sources add column if not exists last_http_status int;
alter table sources add column if not exists last_duration_ms int;
alter table sources add column if not exists jobs_last_seen timestamptz;
