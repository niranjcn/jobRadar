"use client";

import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import { errText, formatDateTime, timeLeft } from "@/lib/format";
import type { Coupon } from "@/lib/types";

type Filter = "open" | "claimed" | "expired" | "";

export default function AdminCouponsPage() {
  const [coupons, setCoupons] = useState<Coupon[]>([]);
  const [filter, setFilter] = useState<Filter>("");
  const [grantsRole, setGrantsRole] = useState<"user" | "privileged">("user");
  const [durationDays, setDurationDays] = useState("");
  const [note, setNote] = useState("");
  const [minted, setMinted] = useState<Coupon | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(() => {
    api
      .adminCoupons(filter || undefined)
      .then((r) => setCoupons(r.coupons))
      .catch((e) => setError(errText(e)));
  }, [filter]);

  useEffect(() => {
    load();
    const timer = setInterval(load, 60_000);
    return () => clearInterval(timer);
  }, [load]);

  async function mint() {
    setBusy(true);
    setError(null);
    try {
      const days = parseInt(durationDays, 10);
      const coupon = await api.mintCoupon({
        grants_role: grantsRole,
        duration_days: Number.isFinite(days) && days > 0 ? days : null,
        note: note.trim() || undefined,
      });
      setMinted(coupon);
      setNote("");
      setDurationDays("");
      load();
    } catch (e) {
      setError(errText(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-6">
      <section className="card space-y-3 p-5">
        <h2 className="text-[15px] font-semibold">
          Generate coupon code{" "}
          <span className="text-xs font-normal text-text-muted">— valid for 12 hours, single claim</span>
        </h2>
        <div className="flex flex-wrap items-center gap-2">
          <select
            className="search-input w-44"
            value={grantsRole}
            onChange={(e) => setGrantsRole(e.target.value as "user" | "privileged")}
          >
            <option value="user">For: user access</option>
            <option value="privileged">For: privileged (F&F)</option>
          </select>
          <input
            type="number"
            min={1}
            placeholder="Days (blank = until revoked)"
            value={durationDays}
            onChange={(e) => setDurationDays(e.target.value)}
            className="search-input w-56"
          />
          <input
            placeholder="Note — e.g. for Rahul"
            value={note}
            onChange={(e) => setNote(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !busy && mint()}
            className="search-input w-56"
          />
          <button onClick={mint} disabled={busy} className="btn-primary">
            {busy ? "Generating…" : "Generate code"}
          </button>
        </div>

        {minted && (
          <div className="rounded-[10px] border border-success/40 bg-success/10 p-4">
            <p className="text-xs text-text-muted">Share this code now — it expires in 12 hours:</p>
            <div className="mt-2 flex items-center gap-3">
              <code className="rounded bg-elevated px-3 py-2 font-mono text-xl tracking-[0.2em]">{minted.code}</code>
              <button
                className="btn-ghost text-xs"
                onClick={() => navigator.clipboard?.writeText(minted.code).catch(() => {})}
              >
                Copy
              </button>
              <span className={`text-xs font-mono ${timeLeft(minted.expires_at) === "expired" ? "text-danger" : "text-warning"}`}>
                {timeLeft(minted.expires_at)}
              </span>
              <span className="text-xs uppercase tracking-widest text-text-muted">{minted.grants_role}</span>
            </div>
          </div>
        )}
        {error && <p className="text-sm text-danger">{error}</p>}
      </section>

      <section>
        <div className="mb-3 flex gap-1">
          {(["", "open", "claimed", "expired"] as Filter[]).map((f) => (
            <button
              key={f || "all"}
              onClick={() => setFilter(f)}
              className={`rounded-full px-4 py-1.5 text-sm transition-colors ${
                filter === f ? "bg-primary/15 text-primary" : "text-text-secondary hover:bg-primary/5"
              }`}
            >
              {f === "" ? "All" : f}
            </button>
          ))}
        </div>

        <div className="card divide-y divide-border overflow-hidden">
          {coupons.map((c) => (
            <div key={c.id} className="flex flex-wrap items-center gap-x-4 gap-y-1 p-3.5">
              <code className="font-mono text-sm tracking-widest">{c.code}</code>
              <span
                className={`rounded border px-1.5 py-0.5 font-mono text-[9px] uppercase tracking-widest ${
                  c.grants_role === "privileged"
                    ? "border-success/30 bg-success/15 text-success"
                    : "border-border bg-elevated text-text-muted"
                }`}
              >
                {c.grants_role}
              </span>
              {c.note && <span className="max-w-48 truncate text-xs text-text-secondary">“{c.note}”</span>}
              <span className="ml-auto flex items-center gap-4 text-xs text-text-muted">
                <span>{c.claimed_by_email ? `claimed by ${c.claimed_by_email}` : timeLeft(c.expires_at)}</span>
                <span title={formatDateTime(c.created_at)}>created {formatDateTime(c.created_at)}</span>
                {!c.claimed_by_email && (
                  <button
                    className="text-text-muted hover:text-danger"
                    onClick={async () => {
                      try {
                        await api.voidCoupon(c.id);
                        load();
                      } catch (e) {
                        setError(errText(e));
                      }
                    }}
                  >
                    void
                  </button>
                )}
              </span>
            </div>
          ))}
          {coupons.length === 0 && (
            <div className="p-6 text-center text-sm text-text-muted">No coupons in this view.</div>
          )}
        </div>
      </section>
    </div>
  );
}
