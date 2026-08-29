"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { AdminStats } from "@/lib/types";

const CARDS: { key: keyof AdminStats; label: string; money?: boolean }[] = [
  { key: "users_total", label: "Users" },
  { key: "active_subs", label: "Active subscriptions" },
  { key: "privileged", label: "Privileged" },
  { key: "locked", label: "Locked accounts" },
  { key: "coupons_open", label: "Open coupons" },
  { key: "mrr_cents", label: "MRR", money: true },
  { key: "alerts_7d", label: "Alerts sent · 7d" },
  { key: "disabled", label: "Disabled" },
];

export default function AdminOverviewPage() {
  const [stats, setStats] = useState<AdminStats | null>(null);

  useEffect(() => {
    api.adminStats().then(setStats);
  }, []);

  if (!stats) return <p className="text-sm text-text-muted">Loading…</p>;

  return (
    <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
      {CARDS.map(({ key, label, money }) => (
        <div key={key} className="card p-4">
          <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-text-muted">{label}</p>
          <p className="mt-1 text-2xl font-bold">
            {money ? `$${((stats[key] as number) / 100).toFixed(0)}` : (stats[key] as number)}
          </p>
        </div>
      ))}
    </div>
  );
}
