-- COPPA / Terms age gate: signup must collect date of birth and refuse
-- under-18 accounts (Terms §03 requires 18+). New registrations persist the
-- birth date; pre-gate rows stay NULL (grandfathered test accounts).
alter table users add column if not exists date_of_birth date;
