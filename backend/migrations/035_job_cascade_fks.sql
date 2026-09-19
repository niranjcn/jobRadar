-- Restore job_id CASCADE FKs claimed by 003/023 but missing live.
-- 003 created job_matches.job_id references jobs(id) on delete cascade and
-- 023 created notification_queue.job_id references jobs(id) on delete cascade,
-- but neither constraint exists in production (CREATE TABLE IF NOT EXISTS never
-- re-applied them). Without them, the retention prune (delete from jobs) leaves
-- orphan job_matches / notification_queue rows pointing at non-existent jobs.
-- Clean orphans first so the constraints validate, then add them.

delete from job_matches m
where not exists (select 1 from jobs j where j.id = m.job_id);

delete from notification_queue q
where not exists (select 1 from jobs j where j.id = q.job_id);

alter table job_matches
add constraint job_matches_job_fk
foreign key (job_id)
references jobs (id)
on delete cascade;

alter table notification_queue
add constraint notification_queue_job_fk
foreign key (job_id)
references jobs (id)
on delete cascade;
