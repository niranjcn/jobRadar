-- No alerts on a company's first poll — first fetch is backfill, not news.
-- poller.py now always suppresses first_check; also set DB default and backfill
-- existing rows to false so new preferences don't default to true.
update preferences set notify_first_check = false where notify_first_check = true;
alter table preferences alter column notify_first_check set default false;
