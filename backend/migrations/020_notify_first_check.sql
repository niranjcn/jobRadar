-- Allow first-ever crawl of a source to send notifications for matching jobs.
alter table preferences add column if not exists notify_first_check boolean not null default true;
