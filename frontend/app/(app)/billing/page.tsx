"use client";

import { useState } from "react";
import Link from "next/link";
import { ApiError, api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { errText } from "@/lib/format";

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
  const [newPassword, setNewPassword] = useState("");
  const [currentPassword, setCurrentPassword] = useState("");
  const [pwdBusy, setPwdBusy] = useState(false);
  const [pwdMsg, setPwdMsg] = useState<string | null>(null);
  const [pwdErr, setPwdErr] = useState<string | null>(null);

  if (!me) return null;
  const sub = me.subscription;

  async function upgrade() {
    setBusy(true);
    setError(null);
    try {
      const res = await api.checkout("standard");
      setInstructions(res.instructions);
    } catch (err) {
      setError(err instanceof ApiError ? err.message.replace(/^\d+ \w+: /, "") : "Checkout failed.");
    } finally {
      setBusy(false);
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
    <div className="mx-auto max-w-2xl p-8">
      <h1 className="text-[28px] font-semibold">Billing</h1>

      <section className="card mt-6 space-y-3 p-5">
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

      {me.role === "user" && (!sub || sub.provider === "manual") && (
        <section className="card mt-4 space-y-3 p-5">
          <h2 className="text-[15px] font-semibold">Subscribe</h2>
          <p className="text-sm text-text-secondary">
            Upgrade to Standard for uninterrupted instant alerts and full history.
          </p>
          <Link href="/pricing" className="btn-primary w-fit">
            View plans
          </Link>
          {!instructions && !sub?.current_period_end && (
            <button onClick={upgrade} disabled={busy} className="btn-ghost w-fit text-xs">
              How do I pay? ({PROVIDER_LABELS["manual"]} flow)
            </button>
          )}
          {instructions && (
            <div className="rounded-[10px] border border-primary/40 bg-primary/5 p-4 text-sm text-text-secondary">
              {instructions}
            </div>
          )}
          {error && <p className="text-sm text-danger">{error}</p>}
        </section>
      )}
    </div>
  );
}
