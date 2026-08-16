create table if not exists preferences (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null unique,
    keywords text[] not null default '{}',
    roles text[] not null default '{}',
    locations text[] not null default '{}',
    seniority text[] not null default '{}',
    excluded_companies text[] not null default '{}',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table if not exists job_matches (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null,
    job_id uuid not null references jobs (id) on delete cascade,
    matched_on text[] not null default '{}',
    created_at timestamptz not null default now(),
    unique (user_id, job_id)
);

create index if not exists job_matches_user_id_idx on job_matches (user_id);
create index if not exists job_matches_job_id_idx on job_matches (job_id);

insert into preferences (user_id)
values ('00000000-0000-0000-0000-000000000001')
on conflict (user_id) do nothing;