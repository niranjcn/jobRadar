-- Follow-up to 022: databases that already ran the original 022 lack the
-- auto-generated id default, which breaks self-registration inserts.
alter table users alter column id set default gen_random_uuid();
