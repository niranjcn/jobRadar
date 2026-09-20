-- 66-69: domain integrity — smallint + CHECKs + updated_at trigger
-- 66: match_score is 0-100, fits smallint; also cleaner domain model
alter table job_matches alter column match_score type smallint using match_score::smallint;
alter table job_matches add constraint job_matches_match_score_check check (match_score between 0 and 100);

-- 67: alert_delay_minutes must not be negative or absurd (app already caps 0..10080)
alter table users add constraint users_alert_delay_minutes_check check (alert_delay_minutes between 0 and 10080);
alter table users add constraint users_failed_login_attempts_check check (failed_login_attempts >= 0);

-- 68: counters must never go negative (cheap protection against math bugs)
alter table notification_queue add constraint notification_queue_attempts_check check (attempts >= 0);
alter table sources add constraint sources_quiet_runs_check check (quiet_runs >= 0);
alter table sources add constraint sources_consecutive_failures_check check (consecutive_failures >= 0);
alter table sources add constraint sources_consecutive_empty_runs_check check (consecutive_empty_runs >= 0);
alter table poll_runs add constraint poll_runs_jobs_fetched_check check (jobs_fetched >= 0);
alter table poll_runs add constraint poll_runs_jobs_new_check check (jobs_new >= 0);
alter table poll_runs add constraint poll_runs_matches_new_check check (matches_new >= 0);
alter table poll_runs add constraint poll_runs_telegram_sent_check check (telegram_sent >= 0);
alter table poll_runs add constraint poll_runs_email_sent_check check (email_sent >= 0);

-- 69: standardize updated_at — DB trigger wins over app forgetting to set it
create or replace function set_updated_at() returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

drop trigger if exists set_updated_at on users;
create trigger set_updated_at before update on users
  for each row execute function set_updated_at();

drop trigger if exists set_updated_at on preferences;
create trigger set_updated_at before update on preferences
  for each row execute function set_updated_at();

drop trigger if exists set_updated_at on subscriptions;
create trigger set_updated_at before update on subscriptions
  for each row execute function set_updated_at();

drop trigger if exists set_updated_at on preference_presets;
create trigger set_updated_at before update on preference_presets
  for each row execute function set_updated_at();

drop trigger if exists set_updated_at on app_settings;
create trigger set_updated_at before update on app_settings
  for each row execute function set_updated_at();

drop trigger if exists set_updated_at on poll_schedule;
create trigger set_updated_at before update on poll_schedule
  for each row execute function set_updated_at();
