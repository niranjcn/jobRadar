-- Phase 2 of the job_matches index cleanup: natural primary key.
--
-- Evidence the surrogate id is dead weight (verified before writing this):
--   * no reader selects it: every query fetches job_id/matched_on/match_score
--     or counts/avgs (routes.py, bot.py, notification_queue.py, notify.py);
--     frontend never references job_matches at all; idx_scan on the pkey was 1.
--   * writers don't need it: upserts use on_conflict="user_id,job_id" and the
--     recompute function inserts an explicit column list without id.
-- Result: the 39 MB UNIQUE becomes the PK (same storage, one fewer index),
-- the 14 MB pkey index disappears, and random-uuid insert scatter ends.
-- DROP COLUMN is metadata-only in Postgres (instant, no rewrite).

alter table job_matches
drop constraint job_matches_pkey;

alter table job_matches
drop constraint job_matches_user_id_job_id_key;

alter table job_matches
add constraint job_matches_pkey
primary key (user_id, job_id);

alter table job_matches
drop column id;
