-- Job descriptions are only needed transiently for NEW jobs (used for keyword
-- matching at first-seen). Existing jobs do not need them, so null out every
-- stored description to reclaim space. New descriptions are cleared after the
-- alert is sent (see app/poller.py clear_descriptions).

update jobs set description = null where description is not null;
