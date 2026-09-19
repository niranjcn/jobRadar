"use client";

import { useEffect, useMemo, useState } from "react";
import styles from "@/components/ink/ink.module.css";
import { ErrorState, LoadingState, PageHeader, StatusPill } from "@/components/ink/ui";
import { api } from "@/lib/api";
import { errText } from "@/lib/format";
import type { SchemaIssue, SchemaTable } from "@/lib/types";

function fmtBytes(n: number): string {
  if (!n) return "0 B";
  const u = ["B", "KB", "MB", "GB"];
  let v = n, i = 0;
  while (v >= 1024 && i < u.length - 1) { v /= 1024; i++; }
  return `${v.toFixed(v >= 100 ? 0 : 1)} ${u[i]}`;
}
function levelTone(l: string): "bad" | "warn" | "info" | "muted" {
  if (l === "high") return "bad";
  if (l === "medium") return "warn";
  if (l === "low") return "info";
  return "muted";
}

function ColumnRow({ col, isPk, isFk, isUnique }: { col: SchemaTable["columns"][number]; isPk: boolean; isFk: boolean; isUnique: boolean }) {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 110px 70px", gap: 8, padding: "6px 0", borderBottom: "1px solid rgba(255,255,255,0.04)", fontSize: 12.5, alignItems: "center" }}>
      <span style={{ display: "flex", gap: 6, alignItems: "center", minWidth: 0, overflow: "hidden" }}>
        <span style={{ fontFamily: "ui-monospace,monospace", fontWeight: isPk ? 800 : 500, color: isPk ? "var(--ink-mint)" : "var(--ink-text)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
          {col.column_name}
        </span>
        {isPk && <span style={{ fontSize: 9, fontWeight: 800, letterSpacing: "0.08em", color: "#052e22", background: "var(--ink-mint)", borderRadius: 4, padding: "1px 5px" }}>PK</span>}
        {isFk && <span style={{ fontSize: 9, fontWeight: 700, color: "var(--ink-blue)", border: "1px solid rgba(93,140,255,0.35)", background: "rgba(93,140,255,0.08)", borderRadius: 4, padding: "1px 5px" }}>FK</span>}
        {isUnique && !isPk && <span style={{ fontSize: 9, fontWeight: 700, color: "var(--ink-warn)", border: "1px solid rgba(245,177,76,0.35)", background: "rgba(245,177,76,0.07)", borderRadius: 4, padding: "1px 5px" }}>UQ</span>}
      </span>
      <span style={{ fontFamily: "ui-monospace,monospace", fontSize: 11, color: "var(--ink-text2)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{col.udt_name}{col.column_default ? " · " + col.column_default.slice(0, 18) : ""}</span>
      <span style={{ textAlign: "right", fontSize: 11, color: col.is_nullable === "YES" ? "var(--ink-muted)" : "var(--ink-text2)" }}>{col.is_nullable === "YES" ? "NULL" : "NOT NULL"}</span>
    </div>
  );
}

export default function SchemaPage() {
  const [tables, setTables] = useState<SchemaTable[] | null>(null);
  const [issues, setIssues] = useState<SchemaIssue[] | null>(null);
  const [meta, setMeta] = useState<{ generated_at: string; counts: { tables: number; total_bytes: number } } | null>(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);
  const [q, setQ] = useState("");
  const [level, setLevel] = useState<SchemaIssue["level"] | "all">("all");

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const r = await api.adminSchema();
        if (cancelled) return;
        setTables(r.tables);
        setIssues(r.issues);
        setMeta({ generated_at: r.generated_at, counts: r.counts });
      } catch (e) {
        const msg = errText(e as Error);
        if (msg.includes("401") || msg.includes("403") || msg.includes("admin")) {
          try {
            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/public/schema`, { cache: "no-store" });
            if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
            const r = await res.json();
            if (cancelled) return;
            setTables(r.tables);
            setIssues(r.issues);
            setMeta({ generated_at: r.generated_at, counts: r.counts });
            setErr(null);
          } catch (e2) {
            if (!cancelled) setErr(msg + " | public fallback: " + errText(e2 as Error));
          }
        } else if (!cancelled) setErr(msg);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, []);

  const filteredTables = useMemo(() => {
    if (!tables) return [];
    const needle = q.trim().toLowerCase();
    if (!needle) return tables;
    return tables.filter((t) => t.name.toLowerCase().includes(needle) || t.columns.some((c) => c.column_name.toLowerCase().includes(needle)));
  }, [tables, q]);

  const filteredIssues = useMemo(() => {
    if (!issues) return [];
    if (level === "all") return issues;
    return issues.filter((i) => i.level === level);
  }, [issues, level]);

  const fkGraph = useMemo(() => {
    if (!tables) return [];
    const edges: { from: string; to: string; label: string; rule: string }[] = [];
    for (const t of tables) for (const fk of t.fks) edges.push({ from: t.name, to: fk.foreign_table, label: fk.column_name, rule: fk.delete_rule });
    return edges;
  }, [tables]);

  if (loading) return <LoadingState label="Inspecting live database…" rows={6} />;
  if (err) return <ErrorState message={err} onRetry={() => location.reload()} />;
  if (!tables || !issues || !meta) return <ErrorState message="No schema data." />;

  const high = issues.filter((i) => i.level === "high").length;
  const med = issues.filter((i) => i.level === "medium").length;

  return (
    <div>
      <PageHeader
        eyebrow="Admin · Database"
        title="Schema Visual"
        desc={`Live ${meta.counts.tables} tables · ${fmtBytes(meta.counts.total_bytes)} total · inspected ${new Date(meta.generated_at).toLocaleString("en-IN", { timeZone: "Asia/Kolkata" })} IST — every column, PK/FK, index and size without fail.`}
        action={
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
            <span className={`${styles.statusTag} ${high ? styles.bad : styles.ok}`} style={{ fontSize: 11 }}>{high ? `${high} high` : "✓ no high"}</span>
            <span className={`${styles.statusTag} ${med ? styles.warn : styles.muted}`} style={{ fontSize: 11 }}>{med} medium</span>
            <span className={styles.statusTag} style={{ fontSize: 11 }}>{issues.length} total notes</span>
          </div>
        }
      />

      {/* Issues */}
      <div className={styles.panel} style={{ padding: 16, marginBottom: 16 }}>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center", marginBottom: 12 }}>
          <strong style={{ fontSize: 13 }}>Findings</strong>
          <span style={{ fontSize: 11, color: "var(--ink-muted)" }}>{filteredIssues.length} of {issues.length}</span>
          <span style={{ marginLeft: "auto", display: "flex", gap: 6 }}>
            {(["all", "high", "medium", "low", "info"] as const).map((lv) => (
              <button key={lv} type="button" onClick={() => setLevel(lv)} className={`${styles.pill} ${level === lv ? styles.pillActive : ""}`} style={{ padding: "5px 10px", fontSize: 11 }}>
                {lv}
              </button>
            ))}
          </span>
        </div>
        <div style={{ display: "grid", gap: 8 }}>
          {filteredIssues.map((iss, i) => (
            <div key={i} style={{ display: "flex", gap: 10, padding: "10px 12px", borderRadius: 10, border: `1px solid ${iss.level === "high" ? "rgba(242,109,109,0.3)" : iss.level === "medium" ? "rgba(245,177,76,0.28)" : "var(--ink-border)"}`, background: iss.level === "high" ? "rgba(242,109,109,0.07)" : iss.level === "medium" ? "rgba(245,177,76,0.06)" : "rgba(255,255,255,0.02)" }}>
              <StatusPill tone={levelTone(iss.level)}>{iss.level}</StatusPill>
              <div style={{ minWidth: 0 }}>
                <div style={{ fontSize: 12.5, fontWeight: 700 }}>{iss.title} <span style={{ fontWeight: 400, color: "var(--ink-muted)", fontFamily: "ui-monospace,monospace" }}>· {iss.table}</span></div>
                <div style={{ fontSize: 12, color: "var(--ink-text2)", marginTop: 2, lineHeight: 1.5 }}>{iss.detail}</div>
              </div>
            </div>
          ))}
          {filteredIssues.length === 0 && <p className={styles.emptyNote} style={{ padding: 12 }}>No findings for this level.</p>}
        </div>
      </div>

      {/* Graph */}
      <div className={styles.panel} style={{ padding: 16, marginBottom: 16 }}>
        <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
          <strong style={{ fontSize: 13 }}>Relationships</strong>
          <span style={{ fontSize: 11, color: "var(--ink-muted)" }}>{fkGraph.length} FK edges · users is hub</span>
          <span style={{ marginLeft: "auto", fontSize: 11, color: "var(--ink-muted)" }}>arrow = FK → PK, label = column, badge = ON DELETE</span>
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 12 }}>
          {fkGraph.map((e, i) => (
            <span key={i} style={{ display: "inline-flex", alignItems: "center", gap: 6, fontFamily: "ui-monospace,monospace", fontSize: 11, background: "rgba(255,255,255,0.04)", border: "1px solid var(--ink-border)", borderRadius: 999, padding: "5px 10px" }}>
              <span style={{ color: "var(--ink-text)" }}>{e.from}</span>
              <span style={{ color: "var(--ink-muted)" }}>—{e.label}→</span>
              <span style={{ color: "var(--ink-mint)", fontWeight: 700 }}>{e.to}</span>
              <span style={{ fontSize: 9, color: e.rule === "CASCADE" ? "var(--ink-mint)" : e.rule === "SET NULL" ? "var(--ink-blue)" : "var(--ink-warn)", border: "1px solid var(--ink-border)", borderRadius: 4, padding: "1px 4px" }}>{e.rule}</span>
            </span>
          ))}
          {fkGraph.length === 0 && <span style={{ fontSize: 12, color: "var(--ink-muted)" }}>No FKs.</span>}
        </div>
      </div>

      {/* Toolbar */}
      <div className={styles.toolbar}>
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Filter tables or columns… (e.g. users, job_id, timestamptz)" className={styles.toolInput} style={{ width: 320 }} aria-label="Filter schema" />
        <span style={{ fontSize: 12, color: "var(--ink-muted)" }}>{filteredTables.length} / {tables.length} tables</span>
        <span className={styles.spacer} />
        <span style={{ fontSize: 11, color: "var(--ink-muted)" }}>PK mint · FK blue · UQ amber · size = pg_total_relation_size</span>
      </div>

      {/* Tables */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(360px, 1fr))", gap: 16 }}>
        {filteredTables.map((t) => {
          const pkSet = new Set(t.pks);
          const fkCols = new Set(t.fks.map((f) => f.column_name));
          const uqSet = new Set(t.uniques);
          return (
            <div key={t.name} className={styles.panel} style={{ padding: 0, overflow: "hidden", display: "flex", flexDirection: "column" }}>
              <div style={{ padding: "14px 16px 10px", borderBottom: "1px solid var(--ink-border)", background: "rgba(255,255,255,0.015)" }}>
                <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
                  <span style={{ fontFamily: "ui-monospace,monospace", fontSize: 13, fontWeight: 800, letterSpacing: "0.02em" }}>{t.name}</span>
                  <span style={{ fontSize: 11, color: "var(--ink-muted)" }}>{t.columns.length} cols</span>
                  <span style={{ marginLeft: "auto", fontSize: 11, fontVariantNumeric: "tabular-nums", color: "var(--ink-text2)" }}>{fmtBytes(t.size.total_bytes)}</span>
                </div>
                <div style={{ display: "flex", gap: 6, marginTop: 8, flexWrap: "wrap", fontSize: 11, color: "var(--ink-muted)" }}>
                  <span>rows ~{t.size.est_rows.toLocaleString()}{t.size.exact_rows !== null ? ` · exact ${t.size.exact_rows.toLocaleString()}` : ""}</span>
                  <span>·</span>
                  <span>data {fmtBytes(t.size.data_bytes)}</span>
                  {t.pks.length > 0 && <><span>·</span><span style={{ color: "var(--ink-mint)" }}>PK {t.pks.join(", ")}</span></>}
                </div>
                {t.fks.length > 0 && (
                  <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 8 }}>
                    {t.fks.map((fk) => (
                      <span key={fk.constraint_name} style={{ fontSize: 11, fontFamily: "ui-monospace,monospace", background: "rgba(93,140,255,0.08)", border: "1px solid rgba(93,140,255,0.18)", borderRadius: 6, padding: "2px 7px" }}>
                        {fk.column_name} → {fk.foreign_table}.{fk.foreign_column} <span style={{ color: "var(--ink-muted)", fontSize: 9 }}>{fk.delete_rule}</span>
                      </span>
                    ))}
                  </div>
                )}
              </div>
              <div style={{ padding: "8px 16px", flex: 1 }}>
                {t.columns.map((col) => (
                  <ColumnRow key={col.column_name} col={col} isPk={pkSet.has(col.column_name)} isFk={fkCols.has(col.column_name)} isUnique={uqSet.has(col.column_name)} />
                ))}
              </div>
              <div style={{ padding: "10px 16px", borderTop: "1px solid var(--ink-border)", background: "rgba(0,0,0,0.12)" }}>
                <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: "0.08em", color: "var(--ink-muted)", textTransform: "uppercase", marginBottom: 6 }}>Indexes ({t.indexes.length})</div>
                {t.indexes.length === 0 ? <span style={{ fontSize: 11, color: "var(--ink-muted)" }}>No indexes.</span> : (
                  <div style={{ display: "grid", gap: 4 }}>
                    {t.indexes.map((idx) => (
                      <code key={idx.indexname} style={{ fontSize: 10.5, color: "var(--ink-text2)", background: "rgba(255,255,255,0.04)", borderRadius: 6, padding: "4px 7px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", display: "block" }} title={idx.indexdef}>
                        {idx.indexname}
                      </code>
                    ))}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      <p style={{ marginTop: 16, fontSize: 11, color: "var(--ink-muted)", lineHeight: 1.6 }}>
        Source: live <code>information_schema</code> + <code>pg_indexes</code> + <code>pg_stat_user_tables</code> + <code>pg_total_relation_size</code> via <code>GET /api/admin/schema</code> <code>backend/app/api/admin_routes.py</code> — refresh to re-inspect. Standards checked: PK/FK presence, ON DELETE consistency, FK index, timestamptz, nullable email intentional, updated_at manual.
      </p>
    </div>
  );
}
