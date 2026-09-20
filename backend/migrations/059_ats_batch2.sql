-- Batch-2 ATS adapters: HTML/JSON/RSS boards verified live (no auth).
insert into ats_types (code, name, default_interval, default_concurrency) values
    ('breezy', 'Breezy HR', 3600, 10),
    ('jobvite', 'Jobvite', 3600, 6),
    ('jazzhr', 'JazzHR', 3600, 10),
    ('bamboohr', 'BambooHR', 3600, 10),
    ('teamtailor', 'Teamtailor', 3600, 10),
    ('rippling', 'Rippling', 3600, 6),
    ('eightfold', 'Eightfold', 3600, 10)
on conflict (code) do nothing;
