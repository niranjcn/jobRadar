-- Location -> country mapping (geo) support.
--
-- Adds per-job snapshot of mapped countries + remote flag, and a generic
-- app_settings table where the location-mapping behaviour is configured
-- (editable from the website, see /api/settings/location-mapping).

alter table jobs
    add column if not exists countries text[] not null default '{}';

alter table jobs
    add column if not exists is_remote boolean not null default false;

create index if not exists jobs_countries_idx on jobs using gin (countries);

create table if not exists app_settings (
    key text primary key,
    value jsonb not null,
    updated_at timestamptz not null default now()
);

insert into app_settings (key, value)
values (
    'location_mapping',
    '{"enabled": true, "remote_to": ["IN"], "custom_aliases": {}}'::jsonb
)
on conflict (key) do nothing;