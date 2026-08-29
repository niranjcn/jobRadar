-- Access layer: one paid plan today, coupon codes, subscription mirror,
-- raw webhook/billing audit trail. Provider-neutral (stripe/paddle/
-- lemonsqueezy/razorpay/coupon/manual).

create table plans (
    code text primary key,
    name text not null,
    price_cents int not null default 0,
    currency text not null default 'USD',
    interval text not null default 'month',
    limits jsonb not null default '{}',
    sort_order int not null default 0,
    is_active boolean not null default true
);

insert into plans (code, name, price_cents, limits, sort_order)
values (
    'standard', 'Standard', 900,
    '{"channels":["telegram","email"],"match_history_days":null,"digest":true}',
    1
)
on conflict (code) do nothing;

create table subscriptions (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references users (id),
    plan_code text not null references plans (code),
    status text not null default 'active'
        check (status in ('active', 'past_due', 'canceled', 'expired')),
    provider text not null default 'manual'
        check (provider in ('stripe', 'paddle', 'lemonsqueezy', 'razorpay', 'coupon', 'manual')),
    provider_customer_id text,
    provider_subscription_id text,
    current_period_start timestamptz,
    current_period_end timestamptz,          -- null = no expiry (coupons/grants)
    cancel_at_period_end boolean not null default false,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create unique index subscriptions_one_live_idx
    on subscriptions (user_id)
    where status in ('active', 'past_due');
create index subscriptions_plan_idx on subscriptions (plan_code, status);

-- Admin-minted access codes. Structural guarantees:
--   * single claim  -> claimed_by set atomically, one row per code
--   * 12-hour life  -> check constraint, enforced again in application code
create table coupon_codes (
    id uuid primary key default gen_random_uuid(),
    code text not null unique,
    grants_role text not null check (grants_role in ('user', 'privileged')),
    duration_days int,                        -- null = until revoked
    note text,
    created_by uuid not null references users (id),
    created_at timestamptz not null default now(),
    expires_at timestamptz not null,
    claimed_by uuid references users (id),
    claimed_at timestamptz,
    check (expires_at <= created_at + interval '12 hours')
);
create index coupon_codes_open_idx on coupon_codes (expires_at) where claimed_by is null;

create table billing_events (
    id uuid primary key default gen_random_uuid(),
    provider text not null,
    provider_event_id text not null,
    event_type text not null,
    payload jsonb not null,
    status text not null default 'received'
        check (status in ('received', 'processed', 'failed', 'ignored')),
    error text,
    received_at timestamptz not null default now(),
    processed_at timestamptz,
    unique (provider, provider_event_id)
);
