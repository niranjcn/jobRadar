-- New ATS adapters: Workable (public accounts API) + SmartRecruiters (public postings API).
-- sources.ats_type FK requires lookup rows before any source can use them.
insert into ats_types (code, name, default_interval, default_concurrency) values
    ('workable', 'Workable', 3600, 16),
    ('smartrecruiters', 'SmartRecruiters', 3600, 16)
on conflict (code) do nothing;
