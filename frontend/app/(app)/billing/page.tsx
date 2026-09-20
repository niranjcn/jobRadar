"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { PageHeader } from "@/components/ink/ui";
import styles from "@/components/ink/ink.module.css";
import { ApiError, api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { errText } from "@/lib/format";
import type { Plan } from "@/lib/types";

function formatDate(iso?: string | null) {
  if (!iso) return null;
  return new Date(iso).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

const PROVIDER_LABELS: Record<string, string> = {
  manual: "Manual payment",
  coupon: "Coupon code",
  stripe: "Stripe",
  paddle: "Paddle",
  lemonsqueezy: "Lemon Squeezy",
  razorpay: "Razorpay",
};

export default function BillingPage() {
  const { me, refresh } = useAuth();
  const [instructions, setInstructions] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [coupon, setCoupon] = useState("");
  const [couponBusy, setCouponBusy] = useState(false);
  const [couponMsg, setCouponMsg] = useState<string | null>(null);
  const [couponErr, setCouponErr] = useState<string | null>(null);
  const [newPassword, setNewPassword] = useState("");
  const [currentPassword, setCurrentPassword] = useState("");
  const [pwdBusy, setPwdBusy] = useState(false);
  const [pwdMsg, setPwdMsg] = useState<string | null>(null);
  const [pwdErr, setPwdErr] = useState<string | null>(null);

  const [plans, setPlans] = useState<Plan[]>([]);

  useEffect(() => {
    api.plans().then((r) => setPlans(r.plans)).catch(() => {});
  }, []);

  if (!me) return null;
  const sub = me.subscription;
  const planPrice = plans.find((p) => p.code === sub?.plan_code);
  const priceLabel = planPrice
    ? `${planPrice.currency === "INR" ? "₹" : planPrice.currency === "USD" ? "$" : `${planPrice.currency} `}${(planPrice.price_minor_units / 100).toFixed(planPrice.price_minor_units % 100 === 0 ? 0 : 2)} / ${planPrice.interval}`
    : null;

  async function upgrade() {
    setBusy(true);
    setError(null);
    setInstructions(null);
    try {
      // Try Razorpay subscription/order creation via dedicated endpoint first (autopay)
      let res: unknown = null;
      let isRazorpay = false;
      try {
        const subRes = await api.razorpayCreateSubscription();
        res = subRes;
        isRazorpay = true;
        const keyId = (subRes as unknown as { key_id?: string }).key_id || "";
        const subId = (subRes as unknown as { subscription_id?: string }).subscription_id;
        const orderId = (subRes as unknown as { order_id?: string }).order_id;
        const loadRazorpay = () =>
          new Promise<boolean>((resolve) => {
            if ((window as unknown as { Razorpay?: unknown }).Razorpay) return resolve(true);
            const s = document.createElement("script");
            s.src = "https://checkout.razorpay.com/v1/checkout.js";
            s.onload = () => resolve(true);
            s.onerror = () => resolve(false);
            document.body.appendChild(s);
          });
        const ok = await loadRazorpay();
        if (!ok) {
          setError("Failed to load Razorpay. Check connection and try again.");
          return;
        }
        const Razorpay = (window as unknown as { Razorpay: new (opts: unknown) => { open: () => void } }).Razorpay;
        const opts: Record<string, unknown> = {
          key: keyId,
          name: "JobQuest Pro",
          description: subId ? "Monthly autopay — matches + Telegram alerts" : "Monthly — matches + Telegram alerts",
          prefill: { email: me?.email || "", name: me?.display_name || "" },
          theme: { color: "#0f766e" },
          handler: async (resp: { razorpay_payment_id: string; razorpay_subscription_id?: string; razorpay_order_id?: string; razorpay_signature: string }) => {
            const payload: Record<string, string> = {
              razorpay_payment_id: resp.razorpay_payment_id,
              razorpay_signature: resp.razorpay_signature,
            };
            if (resp.razorpay_subscription_id) payload.razorpay_subscription_id = resp.razorpay_subscription_id;
            else if (resp.razorpay_order_id) payload.razorpay_order_id = resp.razorpay_order_id;
            else if (subId) payload.razorpay_subscription_id = subId;
            else if (orderId) payload.razorpay_order_id = orderId;
            try {
              await api.razorpayVerify(payload as unknown as { razorpay_payment_id: string; razorpay_subscription_id: string; razorpay_signature: string });
              setInstructions("Payment verified — subscription active for 30 days. Matches and Telegram alerts are now unlocked.");
              await refresh();
            } catch (e) {
              setError(errText(e as Error));
            }
          },
          modal: { ondismiss: () => setBusy(false) },
        };
        if (subId) (opts as Record<string, unknown>).subscription_id = subId;
        else if (orderId) (opts as Record<string, unknown>).order_id = orderId;
        const rzp = new Razorpay(opts);
        rzp.open();
        return;
      } catch (e) {
        // Fallback to generic checkout instructions if Razorpay not enabled or failed
        if (isRazorpay) throw e;
      }
      const checkout = await api.checkout("standard");
      setInstructions(checkout.instructions);
      // Handle legacy checkout that already created subscription/order
      const subId2 = (checkout as unknown as { subscription_id?: string }).subscription_id;
      const orderId2 = (checkout as unknown as { order_id?: string }).order_id;
      const keyId2 = (checkout as unknown as { key_id?: string }).key_id;
      if (checkout.provider === "razorpay" && (subId2 || orderId2)) {
        const loadRazorpay = () =>
          new Promise<boolean>((resolve) => {
            if ((window as unknown as { Razorpay?: unknown }).Razorpay) return resolve(true);
            const s = document.createElement("script");
            s.src = "https://checkout.razorpay.com/v1/checkout.js";
            s.onload = () => resolve(true);
            s.onerror = () => resolve(false);
            document.body.appendChild(s);
          });
        const ok = await loadRazorpay();
        if (!ok) return;
        const Razorpay = (window as unknown as { Razorpay: new (opts: unknown) => { open: () => void } }).Razorpay;
        const opts: Record<string, unknown> = {
          key: keyId2,
          name: "JobQuest Pro",
          description: "Monthly — matches + Telegram alerts",
          prefill: { email: me?.email || "", name: me?.display_name || "" },
          theme: { color: "#0f766e" },
          handler: async (resp: { razorpay_payment_id: string; razorpay_subscription_id?: string; razorpay_order_id?: string; razorpay_signature: string }) => {
            const payload: Record<string, string> = {
              razorpay_payment_id: resp.razorpay_payment_id,
              razorpay_signature: resp.razorpay_signature,
            };
            if (resp.razorpay_subscription_id) payload.razorpay_subscription_id = resp.razorpay_subscription_id;
            else if (resp.razorpay_order_id) payload.razorpay_order_id = resp.razorpay_order_id;
            else if (subId2) payload.razorpay_subscription_id = subId2;
            else if (orderId2) payload.razorpay_order_id = orderId2;
            try {
              await api.razorpayVerify(payload as unknown as { razorpay_payment_id: string; razorpay_subscription_id: string; razorpay_signature: string });
              setInstructions("Payment verified — subscription active for 30 days.");
              await refresh();
            } catch (e) {
              setError(errText(e as Error));
            }
          },
        };
        if (subId2) (opts as Record<string, unknown>).subscription_id = subId2;
        else if (orderId2) (opts as Record<string, unknown>).order_id = orderId2;
        const rzp = new Razorpay(opts);
        rzp.open();
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message.replace(/^\d+ \w+: /, "") : "Checkout failed.");
    } finally {
      setBusy(false);
    }
  }

  async function cancelAutopay() {
    setBusy(true);
    setError(null);
    try {
      const res = await api.razorpayCancel();
      setInstructions(res.message);
      await refresh();
    } catch (err) {
      setError(errText(err as Error));
    } finally {
      setBusy(false);
    }
  }

  async function redeemCoupon() {
    setCouponBusy(true);
    setCouponErr(null);
    setCouponMsg(null);
    try {
      const res = await api.redeemCoupon(coupon.trim().toUpperCase());
      setCouponMsg(`Unlocked! Role: ${res.role} ${res.grant_duration_days ? `for ${res.grant_duration_days} days` : "until revoked"}. Refreshing…`);
      setCoupon("");
      await refresh();
    } catch (err) {
      setCouponErr(err instanceof ApiError ? err.message.replace(/^\d+ \w+: /, "") : errText(err as Error));
    } finally {
      setCouponBusy(false);
    }
  }

  async function savePassword() {
    setPwdBusy(true);
    setPwdMsg(null);
    setPwdErr(null);
    try {
      const res = await api.setPassword(newPassword, currentPassword);
      setPwdMsg(res.message);
      setNewPassword("");
      setCurrentPassword("");
      await refresh();
    } catch (err) {
      setPwdErr(errText(err));
    } finally {
      setPwdBusy(false);
    }
  }

  return (
    <div className={styles.content}>
      <PageHeader
        eyebrow="Personal"
        title="Billing"
        desc="Manage your JobQuest subscription."
      />

      <div style={{ maxWidth: 720 }}>
      <section className={styles.proCard}>
        <div className="flex items-center justify-between">
          <h2 className="text-[15px] font-semibold">JOBQUEST PRO</h2>
          {sub ? (
            <span className={styles.statusTag} style={{ marginLeft: 0 }}>
              <span className={styles.okDot} /> {sub.status}
            </span>
          ) : (
            <span className={styles.statusTag} style={{ marginLeft: 0, opacity: 0.8 }}>No plan</span>
          )}
        </div>
        <p style={{ fontSize: 30, fontWeight: 800, margin: "10px 0 0", letterSpacing: "-0.02em" }}>
          {priceLabel ?? (me.role === "user" ? "—" : "Included")}
          {me.role !== "user" && (
            <span style={{ fontSize: 12, fontWeight: 600, color: "var(--ink-mint)", marginLeft: 10 }}>
              {me.role === "privileged" ? "FRIENDS & FAMILY" : "OWNER"}
            </span>
          )}
        </p>
        {sub?.current_period_end && (
          <p className="text-sm text-text-secondary" style={{ marginTop: 6 }}>
            Next billing: {formatDate(sub.current_period_end)}
          </p>
        )}
        {me.role === "user" && (
          <div style={{ display: "flex", gap: 10, marginTop: 16, flexWrap: "wrap" }}>
            {!sub || sub.status !== "active" ? (
              <>
                <button onClick={upgrade} disabled={busy} className={styles.btnMint}>
                  {busy ? "Working…" : sub ? "Renew with Razorpay Autopay" : "Subscribe with Razorpay Autopay"}
                </button>
                <Link href="/pricing" className={styles.btnLine}>
                  View Pricing
                </Link>
              </>
            ) : sub.provider === "razorpay" ? (
              <button onClick={cancelAutopay} disabled={busy} className={styles.btnLine}>
                {busy ? "Working…" : "Cancel Autopay (keep until period end)"}
              </button>
            ) : (
              <Link href="/pricing" className={styles.btnMint}>
                Manage Subscription
              </Link>
            )}
            {sub?.provider === "manual" && !instructions && (
              <button onClick={upgrade} disabled={busy} className={styles.btnLine}>
                {busy ? "Working…" : "How do I pay?"}
              </button>
            )}
          </div>
        )}
        {instructions && (
          <div className="rounded-[10px] border border-primary/40 bg-primary/5 p-4 text-sm text-text-secondary" style={{ marginTop: 12 }}>
            {instructions}
          </div>
        )}
        {error && <p className="text-sm text-danger" style={{ marginTop: 8 }}>{error}</p>}
      </section>

      <section className="card mt-4 space-y-3 p-5">
        <div className="flex items-center justify-between">
          <h2 className="text-[15px] font-semibold">Current access</h2>
          {me.role !== "user" && (
            <span className="rounded border border-success/30 bg-success/10 px-2 py-0.5 font-mono text-[10px] uppercase tracking-widest text-success">
              {me.role === "privileged" ? "Friends & Family" : "Owner"}
            </span>
          )}
        </div>
        {sub ? (
          <dl className="grid grid-cols-[auto_1fr] gap-x-6 gap-y-2 text-sm">
            <dt className="text-text-muted">Plan</dt>
            <dd className="capitalize">{sub.plan_code}</dd>
            <dt className="text-text-muted">Status</dt>
            <dd className="capitalize">{sub.status}</dd>
            <dt className="text-text-muted">Payment method</dt>
            <dd>{PROVIDER_LABELS[sub.provider] ?? sub.provider}</dd>
            {sub.current_period_end && (
              <>
                <dt className="text-text-muted">{sub.status === "active" ? "Renews / expires" : "Ended"}</dt>
                <dd>{formatDate(sub.current_period_end)}</dd>
              </>
            )}
          </dl>
        ) : (
          <p className="text-sm text-text-secondary">
            {me.role === "user"
              ? "No active subscription on this account."
              : "Full access via your account role."}
          </p>
        )}
      </section>

      <section className="card mt-4 space-y-3 p-5">
        <h2 className="text-[15px] font-semibold">Alert delivery</h2>
        <p className="text-sm text-text-secondary">
          {me.alert_delay_minutes > 0 ? (
            <>
              Your alerts are intentionally delayed by{" "}
              <span className="font-semibold text-text">{me.alert_delay_minutes} minutes</span> behind the radar
              sweep — a setting your admin controls.
            </>
          ) : (
            <>Alerts reach you the moment matching jobs are detected.</>
          )}
        </p>
      </section>

      <section className="card mt-4 space-y-3 p-5">
        <h2 className="text-[15px] font-semibold">Account security</h2>
        <p className="text-sm text-text-secondary">
          {me.has_password
            ? "You have a password set. You can log in with email + password or an emailed code."
            : "No password yet — you currently log in with emailed codes. Set one to sign in directly."}
        </p>
        <div className="flex flex-wrap items-center gap-2">
          {me.has_password && (
            <input
              type="password"
              placeholder="Current password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              className="search-input w-52"
            />
          )}
          <input
            type="password"
            placeholder={me.has_password ? "New password" : "Set a password"}
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && newPassword && savePassword()}
            className="search-input w-52"
          />
          <button onClick={savePassword} disabled={pwdBusy || !newPassword} className="btn-primary w-fit">
            {pwdBusy ? "Saving…" : me.has_password ? "Change password" : "Set password"}
          </button>
        </div>
        {pwdMsg && <p className="text-sm text-success">{pwdMsg}</p>}
        {pwdErr && <p className="text-sm text-danger">{pwdErr}</p>}
      </section>

      <section className="card mt-4 space-y-3 p-5">
        <h2 className="text-[15px] font-semibold">Have a coupon?</h2>
        <p className="text-sm text-text-secondary">Admin-issued codes give 1–12 months free (single-use, 12h expiry). Paste it here to unlock instantly.</p>
        <div className="flex flex-wrap items-center gap-2">
          <input
            placeholder="JR-XXXX-XXXX"
            value={coupon}
            onChange={(e) => setCoupon(e.target.value.toUpperCase())}
            onKeyDown={(e) => e.key === "Enter" && coupon.trim() && redeemCoupon()}
            className="search-input w-56 font-mono uppercase"
          />
          <button onClick={redeemCoupon} disabled={couponBusy || !coupon.trim()} className="btn-primary w-fit">
            {couponBusy ? "Redeeming…" : "Redeem coupon"}
          </button>
        </div>
        {couponMsg && <p className="text-sm text-success">{couponMsg}</p>}
        {couponErr && <p className="text-sm text-danger">{couponErr}</p>}
        <p className="text-xs text-text-muted">Or go to <Link href="/unlock" className="hover:text-text">Unlock</Link> page. Codes are `JR-XXXX-XXXX`, case-insensitive.</p>
      </section>

      <section className="card mt-4 space-y-3 p-5">
        <h2 className="text-[15px] font-semibold">Payment method</h2>
        <p className="text-sm text-text-secondary">
          {sub ? (PROVIDER_LABELS[sub.provider] ?? sub.provider) : "No payment method on file."}
        </p>
        {(!sub || me.access_locked) && (
          <p className="text-xs text-text-muted">
            Razorpay monthly billing available when `BILLING_PROVIDER=razorpay` + `RAZORPAY_KEY_ID`/`RAZORPAY_KEY_SECRET` are set in `.env`. Until then, use manual or coupon.
          </p>
        )}
      </section>
      </div>
    </div>
  );
}
