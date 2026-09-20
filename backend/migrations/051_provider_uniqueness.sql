-- Item 44: provider objects must be unique per provider.
-- A retry or double webhook could otherwise create two active rows for the same
-- Razorpay/Stripe object, and two users could share a provider_subscription_id.
-- Partial index: allow multiple NULLs (manual/coupon rows have NULL provider ids).

create unique index if not exists subscriptions_provider_sub_idx
on subscriptions (provider, provider_subscription_id)
where provider_subscription_id is not null;

-- provider_customer_id is less strict (one customer can have many subscriptions
-- over time), so we do NOT add a unique there – only subscription_id is per-object.
