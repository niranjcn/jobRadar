alter table sources
    drop constraint sources_ats_type_check,
    add constraint sources_ats_type_check
        check (ats_type in ('greenhouse', 'lever', 'ashby', 'workday', 'custom', 'oracle', 'icims', 'successfactors', 'phenom', 'avature', 'google', 'amazon'));