-- Fix ON DELETE actions per ownership vs ledger semantics (not blanket CASCADE).
--
-- CASCADE (owned rows, die with the user):
--   preferences.user_id      1:1 row seeded at registration, meaningless without the user
--   subscriptions.user_id    subscription is owned by the account; audit survives in
--                            billing_events, which has no user FK by design
--
-- KEPT AS NO ACTION (deliberate, do not "fix"):
--   subscriptions.plan_code -> plans.code
--       Catalog-to-fact reference. History (even expired subscriptions, used for MRR
--       reporting) must never be cascade-deleted with a plan. The supported
--       "delete" is plans.is_active = false (soft delete, already the design).
--   coupon_codes.claimed_by / created_by, preference_presets.created_by
--       Ledger attribution, not ownership. CASCADE would destroy the audit trail;
--       SET NULL on claimed_by would resurrect single-use codes because the redeem
--       guard checks claimed_by IS NULL. NO ACTION forces explicit admin handling.

alter table preferences
drop constraint preferences_user_fk;

alter table preferences
add constraint preferences_user_fk
foreign key (user_id)
references users (id)
on delete cascade;

alter table subscriptions
drop constraint subscriptions_user_id_fkey;

alter table subscriptions
add constraint subscriptions_user_id_fkey
foreign key (user_id)
references users (id)
on delete cascade;
