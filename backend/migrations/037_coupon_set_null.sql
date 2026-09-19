-- Coupon attribution: SET NULL instead of NO ACTION.
--
-- Coupon rows are an audit ledger (who minted, what was claimed). Deleting a user
-- must not delete that history (CASCADE, wrong) and must not be blocked by it
-- (NO ACTION, wrong — it makes admin/claimant accounts undeletable).
--
-- Subtlety: claimed_by IS NULL is also the redeem guard's "unused" marker. After
-- SET NULL, a claimed-then-claimant-deleted row would look unused and become
-- re-claimable. So claimed_at becomes the canonical single-use marker everywhere
-- (it is only ever set at claim time and never cleared); see access.py and
-- admin_routes.py guards updated alongside this migration.
--
-- created_by must become nullable first: SET NULL is impossible on NOT NULL.

alter table coupon_codes
alter column created_by drop not null;

alter table coupon_codes
drop constraint coupon_codes_claimed_by_fkey;

alter table coupon_codes
add constraint coupon_codes_claimed_by_fkey
foreign key (claimed_by)
references users (id)
on delete set null;

alter table coupon_codes
drop constraint coupon_codes_created_by_fkey;

alter table coupon_codes
add constraint coupon_codes_created_by_fkey
foreign key (created_by)
references users (id)
on delete set null;

-- Unused-marker index follows the new canonical guard.
drop index if exists coupon_codes_open_idx;

create index coupon_codes_open_idx on coupon_codes (expires_at)
where claimed_by is null and claimed_at is null;
