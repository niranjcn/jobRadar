-- Add per-user notification settings to preferences
alter table preferences add column if not exists notify_telegram boolean not null default true;
alter table preferences add column if not exists notify_email boolean not null default true;
alter table preferences add column if not exists alert_frequency text not null default 'immediate';

-- Match score (0-100) for each user/job match
alter table job_matches add column if not exists match_score int;

-- Read-model view joining jobs to their source company for the API/frontend
create or replace view v_job_source as
select
    j.id,
    j.source_id,
    s.company_name,
    s.ats_type,
    j.external_job_id,
    j.title,
    j.location,
    j.url,
    j.description,
    j.raw_payload,
    j.first_seen_at
from jobs j
join sources s on s.id = j.source_id;