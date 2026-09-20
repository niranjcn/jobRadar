-- Item 31: ATS as lookup table instead of giant CHECK constraint.
-- Adding a new ATS no longer requires rewriting a CHECK; just insert a row.
-- Existing sources.ats_type values are preserved, FK ensures integrity.

create table if not exists ats_types (
    code text primary key,
    name text not null,
    active boolean not null default true,
    default_interval int not null default 3600,
    default_concurrency int not null default 8,
    created_at timestamptz not null default now()
);

-- Seed from current CHECK constraint values + config defaults
insert into ats_types (code, name, default_interval, default_concurrency) values
    ('greenhouse', 'Greenhouse', 3600, 16),
    ('lever', 'Lever', 3600, 16),
    ('ashby', 'Ashby', 3600, 16),
    ('workday', 'Workday', 3600, 20),
    ('custom', 'Custom', 3600, 8),
    ('oracle', 'Oracle', 3600, 10),
    ('icims', 'iCIMS', 3600, 8),
    ('successfactors', 'SAP SuccessFactors', 7200, 10),
    ('phenom', 'Phenom', 3600, 8),
    ('avature', 'Avature', 21600, 10),
    ('google', 'Google', 3600, 8),
    ('amazon', 'Amazon', 3600, 8),
    ('remotive', 'Remotive', 3600, 16),
    ('weworkremotely', 'We Work Remotely', 3600, 16),
    ('emirates', 'Emirates', 3600, 8)
on conflict (code) do nothing;

-- Drop the old CHECK and add FK. Use NOT VALID initially to avoid long lock on large sources, then validate.
alter table sources drop constraint if exists sources_ats_type_check;

alter table sources add constraint sources_ats_type_fkey foreign key (ats_type) references ats_types (code) on update cascade on delete restrict;

-- Ensure any future ATS can be added via insert, not migration
create index if not exists ats_types_active_idx on ats_types (active) where active;
