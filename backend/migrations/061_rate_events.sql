-- Shared rate limiter (replaces in-memory dict).
-- One row per event, pruned nightly; index supports the count query.
create table if not exists rate_events (
    id bigserial primary key,
    key text not null,
    created_at timestamptz not null default now()
);
create index if not exists rate_events_key_created_idx on rate_events (key, created_at);
-- Nightly prune is best-effort (see app.poller.prune_old_jobs); no FK.
