"use client";

import { useCallback, useEffect, useState } from "react";
import { DataTable, EmptyState, LoadingState, PageHeader, StatusPill } from "@/components/ink/ui";
import styles from "@/components/ink/ink.module.css";
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
  const [loading, setLoading] = useState(true);

  const load = useCallback(() => {
    api
      .adminCoupons(filter || undefined)
      .then((r) => setCoupons(r.coupons))
      .catch((e) => setError(errText(e)))
      .finally(() => setLoading(false));
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

  // claimed_at is canonical: after ON DELETE SET NULL a claimed row can have
  // no claimed_by_email (claimant purged) while claimed_at stays set.
  function couponStatus(c: Coupon): { tone: "ok" | "warn" | "bad" | "muted"; label: string } {
    if (c.claimed_at) return { tone: "muted", label: "Claimed" };
    if (timeLeft(c.expires_at) === "expired") return { tone: "bad", label: "Expired" };
    return { tone: "ok", label: "Active" };
  }

  return (
    <div>
      <PageHeader
        eyebrow="Admin"
        title="Coupons"
        desc="Create and manage promotional offers. Codes are single-use and expire 12 hours after minting."
        action={
          <button onClick={mint} disabled={busy} className={styles.btnMint}>
            {busy ? "Generating…" : "+ Create coupon"}
          </button>
        }
      />

      <section className={styles.panel} style={{ padding: 20, marginBottom: 20 }}>
        <div className={styles.toolbar} style={{ marginBottom: minted || error ? 14 : 0 }}>
          <select
            className={styles.toolInput}
            style={{ width: 210 }}
            value={grantsRole}
            onChange={(e) => setGrantsRole(e.target.value as "user" | "privileged")}
            aria-label="Coupon flavor"
          >
            <option value="user">For: user access</option>
            <option value="privileged">For: privileged (F&F)</option>
          </select>
          <select
            className={styles.toolInput}
            style={{ width: 220 }}
            value={durationDays}
            onChange={(e) => setDurationDays(e.target.value)}
            aria-label="Duration months"
          >
            <option value="">Until revoked (no expiry)</option>
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((m) => (
              <option key={m} value={String(m === 12 ? 365 : m * 30)}>
                {m} month{m > 1 ? "s" : ""} ({m === 12 ? 365 : m * 30} days)
              </option>
            ))}
          </select>
          <input
            placeholder="Note — e.g. for Rahul"
            value={note}
            onChange={(e) => setNote(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !busy && mint()}
            className={styles.toolInput}
            style={{ width: 220 }}
          />
        </div>

        {minted && (
          <div style={{ border: "1px solid rgba(25,230,167,0.4)", background: "rgba(25,230,167,0.07)", borderRadius: 12, padding: 16 }}>
            <p style={{ fontSize: 12, color: "var(--ink-muted)" }}>Share this code now — it expires in 12 hours:</p>
            <div style={{ marginTop: 8, display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
              <code style={{ borderRadius: 8, background: "rgba(255,255,255,0.06)", padding: "8px 14px", fontFamily: "ui-monospace,monospace", fontSize: 20, letterSpacing: "0.2em" }}>
                {minted.code}
              </code>
              <button
                type="button"
                className={styles.btnLine}
                style={{ fontSize: 12 }}
                onClick={() => navigator.clipboard?.writeText(minted.code).catch(() => {})}
              >
                Copy
              </button>
              <span style={{ fontSize: 12, fontFamily: "ui-monospace,monospace", color: "var(--ink-warn)" }}>
                {timeLeft(minted.expires_at)}
              </span>
              <span style={{ fontSize: 11, textTransform: "uppercase", letterSpacing: "0.1em", color: "var(--ink-muted)" }}>
                {minted.grants_role}
              </span>
            </div>
          </div>
        )}
        {error && <p style={{ fontSize: 13, color: "var(--ink-danger)", marginTop: 10 }}>{error}</p>}
      </section>

      <div className={styles.toolbar}>
        {(["", "open", "claimed", "expired"] as Filter[]).map((f) => (
          <button
            key={f || "all"}
            type="button"
            onClick={() => setFilter(f)}
            className={`${styles.pill} ${filter === f ? styles.pillActive : ""}`}
          >
            {f === "" ? "All" : f[0].toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {loading ? (
        <LoadingState rows={5} />
      ) : coupons.length === 0 ? (
        <EmptyState title="No coupons in this view." />
      ) : (
        <DataTable head={["Code", "Type", "Usage", "Limit", "Expiration", "Status", ""]}>
          {coupons.map((c) => {
            const st = couponStatus(c);
            return (
              <tr key={c.id}>
                <td style={{ fontFamily: "ui-monospace,monospace", letterSpacing: "0.12em", fontWeight: 700 }}>{c.code}</td>
                <td style={{ textTransform: "capitalize" }}>{c.grants_role}</td>
                <td style={{ color: "var(--ink-text2)", fontVariantNumeric: "tabular-nums" }}>
                  {c.claimed_at ? `1 / 1 · ${c.claimed_by_email ?? "(account deleted)"}` : "0 / 1"}
                </td>
                <td style={{ color: "var(--ink-text2)" }}>
                  Single use{c.duration_days ? ` · ${c.duration_days}d access` : ""}
                </td>
                <td style={{ color: "var(--ink-text2)", whiteSpace: "nowrap" }} title={formatDateTime(c.created_at)}>
                  {c.claimed_at ? "—" : timeLeft(c.expires_at)}
                </td>
                <td>
                  <StatusPill tone={st.tone}>● {st.label}</StatusPill>
                </td>
                <td style={{ textAlign: "right" }}>
                  {!c.claimed_at && (
                    <button
                      type="button"
                      style={{ border: 0, background: "none", color: "var(--ink-muted)", cursor: "pointer", fontSize: 12 }}
                      onClick={async () => {
                        try {
                          await api.voidCoupon(c.id);
                          load();
                        } catch (e) {
                          setError(errText(e));
                        }
                      }}
                    >
                      Void
                    </button>
                  )}
                </td>
              </tr>
            );
          })}
        </DataTable>
      )}
    </div>
  );
}
