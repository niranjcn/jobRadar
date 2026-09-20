-- Fix poll_runs_status_check to allow 'skipped' (advisory lock held)
-- poll_all_sources returns skipped when pg_try_advisory_lock fails for a manual
-- run that already holds the lock; the previous CHECK only allowed running/completed/failed.
alter table poll_runs drop constraint poll_runs_status_check;
alter table poll_runs add constraint poll_runs_status_check
  check (status = any (array['running'::text, 'completed'::text, 'failed'::text, 'skipped'::text]));
