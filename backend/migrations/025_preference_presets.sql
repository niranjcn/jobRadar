-- Preference presets: reusable preference bundles admins can apply to a user.
-- The live operator configuration is snapshotted as the admin-only preset
-- "Admin Preference" (a COPY — the original preferences row is not modified).

create table preference_presets (
    id uuid primary key default gen_random_uuid(),
    name text not null unique,
    description text not null default '',
    roles text[] not null default '{}',
    keywords text[] not null default '{}',
    locations text[] not null default '{}',
    seniority text[] not null default '{}',
    excluded_companies text[] not null default '{}',
    excluded_roles text[] not null default '{}',
    is_admin_only boolean not null default false,
    created_by uuid references users (id),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

insert into preference_presets (
    name, description, roles, keywords, locations, seniority,
    excluded_companies, excluded_roles, is_admin_only, created_by
)
select
    'Admin Preference',
    'Snapshot of the original operator configuration',
    p.roles, p.keywords, p.locations, p.seniority,
    p.excluded_companies, p.excluded_roles,
    true, p.user_id
from preferences p
where p.user_id = '00000000-0000-0000-0000-000000000001'
on conflict (name) do nothing;

insert into preference_presets (name, description, roles, keywords, seniority, is_admin_only)
values (
    'Entry Level Software Engineer',
    'New-grad / junior SWE roles',
    array['software engineer', 'software developer', 'swe'],
    array['entry level', 'junior', 'graduate', 'new grad', 'associate'],
    array['internship', 'entry level', 'new grad'],
    false
)
on conflict (name) do nothing;
