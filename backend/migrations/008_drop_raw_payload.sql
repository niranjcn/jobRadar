-- raw_payload is the largest column and duplicates title/location/description/url.
-- Drop it (and rebuild the read-model view that referenced it).

drop view if exists v_job_source;

alter table jobs drop column if exists raw_payload;

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
    j.first_seen_at
from jobs j
join sources s on s.id = j.source_id;
