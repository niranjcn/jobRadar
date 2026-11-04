"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { RadarMark } from "@/components/radar-mark";
import { RadarLoading } from "@/components/radar-loading";
import { ApiError, api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { Plan } from "@/lib/types";

function formatPrice(cents: number, currency: string) {
  const symbol = currency === "USD" ? "$" : currency === "INR" ? "₹" : `${currency} `;
  return `${symbol}${(cents / 100).toFixed(cents % 100 === 0 ? 0 : 2)}`;
}

export default function UnlockPage() {
  const router = useRouter();
  const { me, loading, refresh } = useAuth();
  const [plans, setPlans] = useState<Plan[]>([]);
  const [coupon, setCoupon] = useState("");
  const [instructions, setInstructions] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!loading && me && !me.access_locked) router.replace("/");
    api.plans().then((r) => setPlans(r.plans));
  }, [loading, me, router]);

  async function pay() {
    setBusy(true);
    setError(null);
    try {
      const res = await api.checkout(plans[0]?.code ?? "standard");
      setInstructions(res.instructions);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Checkout failed.");
    } finally {
      setBusy(false);
    }
  }

  async function redeem() {
    setBusy(true);
    setError(null);
    try {
      await api.redeemCoupon(coupon.trim());
      await refresh();
      router.replace("/onboarding");
    } catch (err) {
      setError(err instanceof ApiError ? err.message.replace(/^\d+ \w+: /, "") : "Redemption failed.");
    } finally {
      setBusy(false);
    }
  }

  if (loading || (me && !me.access_locked)) return <RadarLoading label="Loading…" />;

  return (
    <div className="flex min-h-screen items-center justify-center p-6">
      <div className="w-full max-w-md">
        <div className="mb-8 flex flex-col items-center gap-3">
          <RadarMark />
          <span className="font-display text-lg font-bold tracking-[0.14em]">JOBQUEST</span>
          {me?.email && <p className="text-xs text-text-muted">{me.email}</p>}
        </div>

        <div className="card space-y-6 p-6">
          <h1 className="text-center text-lg font-semibold">Unlock JobQuest</h1>

          {plans.map((plan) => (
            <div key={plan.code} className="rounded-[10px] border border-border p-4">
              <div className="flex items-baseline justify-between">
                <span className="font-semibold">{plan.name}</span>
                <span className="text-2xl font-bold">
                  {formatPrice(plan.price_minor_units, plan.currency)}
                  <span className="text-sm font-normal text-text-muted">/{plan.interval}</span>
                </span>
              </div>
              <ul className="mt-2 space-y-1 text-sm text-text-secondary">
                <li>✦ Instant job matches for your preferences</li>
                <li>✦ Telegram + email alerts</li>
                <li>✦ Full match history with scores</li>
              </ul>
              <button onClick={pay} disabled={busy} className="btn-primary mt-4 w-full">
                Subscribe
              </button>
              <p className="mt-2 text-xs text-text-muted">
                {formatPrice(plan.price_minor_units, plan.currency)}/{plan.interval} — auto-renews
                each {plan.interval} until cancelled. Cancel anytime from Billing; you keep access
                until the end of the paid period.
              </p>
            </div>
          ))}

          {instructions && (
            <div className="rounded-[10px] border border-primary/40 bg-primary/5 p-4 text-sm text-text-secondary">
              {instructions}
            </div>
          )}

          <div className="flex items-center gap-3 text-xs text-text-muted">
            <span className="h-px flex-1 bg-border" />
            or
            <span className="h-px flex-1 bg-border" />
          </div>

          <div className="space-y-2">
            <p className="text-sm text-text-secondary">Have a coupon code?</p>
            <div className="flex gap-2">
              <input
                placeholder="JR-XXXX-XXXX"
                value={coupon}
                onChange={(e) => setCoupon(e.target.value.toUpperCase())}
                onKeyDown={(e) => e.key === "Enter" && coupon.trim() && !busy && redeem()}
                className="search-input w-full font-mono uppercase"
              />
              <button onClick={redeem} disabled={busy || !coupon.trim()} className="btn-ghost shrink-0">
                Redeem
              </button>
            </div>
            <p className="text-xs text-text-muted">Codes are single-use and expire 12 hours after they&apos;re issued.</p>
          </div>

          {error && <p className="text-center text-sm text-danger">{error}</p>}
        </div>
      </div>
    </div>
  );
}
