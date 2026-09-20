-- Item 45: price_cents is conceptually wrong for multi-currency.
-- Razorpay treats 900 as ₹9 (900 paise) while DB says USD 900¢ ($9).
-- Rename to price_minor_units: USD→cents, INR→paise, AED→fils.
-- Instant metadata-only rename, no data change.

alter table plans rename column price_cents to price_minor_units;
