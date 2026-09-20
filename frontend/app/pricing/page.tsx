"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { RadarMark } from "@/components/radar-mark";
import styles from "@/components/ink/ink.module.css";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { Plan } from "@/lib/types";

function formatPrice(cents: number, currency: string) {
  const symbol = currency === "USD" ? "$" : currency === "INR" ? "₹" : `${currency} `;
  return `${symbol}${(cents / 100).toFixed(cents % 100 === 0 ? 0 : 2)}`;
}

const FEATURES = [
  "Instant job matches tuned to your preferences",
  "Telegram + email alerts the moment jobs drop",
  "Match scores and reasons for every hit",
  "Companies across Greenhouse, Lever, Workday, Ashby & more",
];

export default function PricingPage() {
  const { me, loading } = useAuth();
  const [plans, setPlans] = useState<Plan[]>([]);

  useEffect(() => {
    api.plans().then((r) => setPlans(r.plans));
  }, []);

  const ctaHref = !me ? "/register" : me.access_locked ? "/unlock" : "/billing";
  const ctaLabel = !me ? "Get started" : me.access_locked ? "Unlock now" : "Manage billing";

  return (
    <div className={styles.ink} style={{ zoom: 1 }}>
      <div className={`${styles.shell} flex-col items-center px-6 py-14`}>
      <Link href="/" className="mb-10 flex flex-col items-center gap-3">
        <RadarMark size={32} />
        <span className="font-display text-lg font-bold tracking-[0.14em]">JOBQUEST</span>
        <span className={styles.eyebrow}>Pricing</span>
      </Link>

      <h1 className="max-w-xl text-center font-display text-3xl font-bold">
        Never miss a fresh posting again
      </h1>
      <p className="mt-3 max-w-md text-center text-sm text-text-secondary">
        JobQuest watches career pages around the clock and alerts you within seconds when something
        matches.
      </p>

      {!loading && (
        <div className={`mt-12 grid w-full max-w-md gap-4 ${plans.length > 1 ? "md:grid-cols-2 md:max-w-2xl" : ""}`}>
          {plans.map((plan) => (
            <div key={plan.code} className="card flex flex-col p-6">
              <span className="font-mono text-xs uppercase tracking-widest text-text-muted">{plan.name}</span>
              <div className="mt-2 text-4xl font-bold">
                {formatPrice(plan.price_minor_units, plan.currency)}
                <span className="text-base font-normal text-text-muted">/{plan.interval}</span>
              </div>
              <ul className="mt-4 flex-1 space-y-2 text-sm text-text-secondary">
                {FEATURES.map((f) => (
                  <li key={f}>✦ {f}</li>
                ))}
              </ul>
              <Link href={ctaHref} className="btn-primary mt-6 w-full text-center">
                {ctaLabel}
              </Link>
            </div>
          ))}
        </div>
      )}

      <p className="mt-8 text-xs text-text-muted">
        Have a coupon?{" "}
        <Link href={me ? "/unlock" : "/register"} className="hover:text-text">
          Redeem it here
        </Link>{" "}
        — no payment needed.
      </p>
      </div>
    </div>
  );
}
