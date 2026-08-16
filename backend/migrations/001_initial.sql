create extension if not exists pgcrypto;

create table if not exists sources (
    id uuid primary key default gen_random_uuid(),
    company_name text not null unique,
    ats_type text not null check (ats_type in ('greenhouse', 'lever', 'ashby', 'workday', 'custom')),
    board_identifier text not null,
    active boolean not null default true,
    last_checked_at timestamptz,
    created_at timestamptz not null default now()
);

create table if not exists jobs (
    id uuid primary key default gen_random_uuid(),
    source_id uuid not null references sources (id) on delete cascade,
    external_job_id text not null,
    title text not null,
    location text,
    url text,
    raw_payload jsonb,
    first_seen_at timestamptz not null default now(),
    unique (source_id, external_job_id)
);

create index if not exists jobs_source_id_idx on jobs (source_id);
create index if not exists jobs_first_seen_at_idx on jobs (first_seen_at desc);

insert into sources (company_name, ats_type, board_identifier)
values ('Stripe', 'greenhouse', 'stripe')
on conflict (company_name) do nothing;
