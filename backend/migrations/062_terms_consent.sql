-- DPDP Act 2023: explicit, unticked consent at registration.
-- accepted_terms_at records when the user accepted the then-current Terms +
-- Privacy Policy. Pre-policy rows stay NULL (grandfathered test accounts);
-- all new registrations must send accept_terms=true (API 422 otherwise).
alter table users add column if not exists accepted_terms_at timestamptz;
