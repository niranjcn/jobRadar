-- Item 46: duration_days is ambiguous (redeem window vs grant length).
-- expires_at is the redeem window (12h), duration is the grant length (30-365d).
-- Rename to grant_duration_days for clarity. Keep old column as view for compat
-- during rollout, but app uses new name.

alter table coupon_codes rename column duration_days to grant_duration_days;
