-- Geo mapping version stamp (item 21): jobs carry the mapping output
-- (countries[], is_remote) but nothing recorded under which rules they were
-- mapped, so one admin alias edit silently splits the warehouse into
-- pre/post vintages. geo_version labels each row; NULL means pre-versioning
-- (honest unknown — no backfill fakes history). The reprocessing job that
-- consumes this (remap where version is stale) comes later, when stale rows
-- actually exist; no query filters on this column yet, so no index either.

alter table jobs add column if not exists geo_version int;
