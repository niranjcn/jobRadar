-- Item 39: push important invariants into DB, not just app code.
-- A direct psql/supabase write bypasses app validation; CHECKs fail fast.

alter table preferences add constraint preferences_alert_frequency_check
check (alert_frequency in ('immediate','every 6 hours','daily digest'));

alter table preferences add constraint preferences_telegram_scope_check
check (telegram_scope in ('matched','all'));

alter table preferences add constraint preferences_email_scope_check
check (email_scope in ('matched','all'));

-- seniority values are free-form text[] (internship, senior, etc.) – no CHECK,
-- but excluded_roles / locations are also free-form by design (no CHECK).
