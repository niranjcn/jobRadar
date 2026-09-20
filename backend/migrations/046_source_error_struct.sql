-- Item 30: structured error state for sources.
-- last_error text is kept for human detail, but scheduler should not parse it.
-- Add code + type so "404 backoff" checks structured data, not substring.

alter table sources add column if not exists last_error_code int;
alter table sources add column if not exists last_error_type text;

-- Optional index for health dashboards filtering by error type
create index if not exists sources_error_type_idx on sources (last_error_type) where last_error_type is not null;
