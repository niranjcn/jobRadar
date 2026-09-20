-- notifications_sent.job_id FK missing live (claimed inline by 004,
-- same drift class as 035). Ledger rows for pruned jobs are undisplayable
-- (history joins are inner), so delete the orphans, then enforce CASCADE:
-- pruning a job cleans its send records with it.
-- The drain ledger only records communicated jobs (see _record_ledger call
-- site), so pruned-mid-flight rows can never violate this constraint.

delete from notifications_sent n
where not exists (select 1 from jobs j where j.id = n.job_id);

alter table notifications_sent
add constraint notifications_sent_job_fk
foreign key (job_id)
references jobs (id)
on delete cascade;
