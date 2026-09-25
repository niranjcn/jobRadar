-- Single truth for pricing: Standard is Rs 49/month (4900 paise), INR.
-- Earlier seeds/fallbacks drifted (900 = Rs 9 in 024, ad-hoc 29900 on live).
-- Upsert so fresh and existing databases converge; frontend reads via /plans.
insert into plans (code, name, price_minor_units, currency, interval, limits, sort_order, is_active)
values (
    'standard', 'Standard', 4900, 'INR', 'month',
    '{"channels":["telegram","email"],"match_history_days":null,"digest":true}',
    1, true
)
on conflict (code) do update set
    price_minor_units = excluded.price_minor_units,
    currency = excluded.currency;
