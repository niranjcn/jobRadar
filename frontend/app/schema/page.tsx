"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";

const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function fmtBytes(n: number): string {
  if (!n) return "0 B";
  const u = ["B", "KB", "MB", "GB"];
  let v = n, i = 0;
  while (v >= 1024 && i < u.length - 1) { v /= 1024; i++; }
  return `${v.toFixed(v >= 100 ? 0 : 1)} ${u[i]}`;
}

export default function StandaloneSchemaPage() {
  const [data, setData] = useState<{ generated_at: string; tables: any[]; issues: any[]; counts: { tables: number; total_bytes: number } } | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [q, setQ] = useState("");

  useEffect(() => {
    fetch(`${BASE}/api/public/schema`, { cache: "no-store" })
      .then((r) => {
        if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
        return r.json();
      })
      .then(setData)
      .catch((e) => setErr(e.message));
  }, []);

  const filtered = useMemo(() => {
    if (!data) return [];
    const needle = q.trim().toLowerCase();
    if (!needle) return data.tables;
    return data.tables.filter((t: any) => t.name.toLowerCase().includes(needle) || t.columns.some((c: any) => c.column_name.toLowerCase().includes(needle)));
  }, [data, q]);

  if (err) {
    return (
      <div style={{ minHeight: "100vh", background: "#061316", color: "#f5f7f7", padding: 32, fontFamily: "Inter,sans-serif" }}>
        <h1 style={{ fontSize: 22, fontWeight: 800, color: "#f26d6d" }}>Failed to fetch</h1>
        <p style={{ marginTop: 8, color: "#9bafb0" }}>{err}</p>
        <p style={{ marginTop: 8, fontSize: 12, color: "#657a7c" }}>Try: <code>docker compose restart web</code> then reload. Endpoint is <code>GET /api/public/schema</code> (public, no login). Also available as static file <a href="/schema.html" style={{ color: "#19e6a7" }}>/schema.html</a>.</p>
        <button onClick={() => location.reload()} style={{ marginTop: 16, background: "#19e6a7", color: "#052e22", border: 0, borderRadius: 8, padding: "8px 16px", fontWeight: 700, cursor: "pointer" }}>Try Again</button>
      </div>
    );
  }
  if (!data) {
    return <div style={{ minHeight: "100vh", background: "#061316", color: "#9bafb0", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "Inter,sans-serif" }}>Loading live schema…</div>;
  }

  return (
    <div style={{ minHeight: "100vh", background: "linear-gradient(180deg,#081a1d 0%,#061316 60%,#040e10 100%)", color: "#f5f7f7", fontFamily: "Inter,system-ui,sans-serif" }}>
      <div style={{ maxWidth: 1240, margin: "0 auto", padding: "28px 20px 40px" }}>
        <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
          <h1 style={{ fontSize: 28, fontWeight: 800, letterSpacing: "-0.02em", margin: 0 }}>Database Schema <span style={{ color: "#19e6a7" }}>Visual</span></h1>
          <span style={{ fontSize: 11, color: "#657a7c", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 999, padding: "4px 10px" }}>{data.counts.tables} tables · {fmtBytes(data.counts.total_bytes)} · {new Date(data.generated_at).toLocaleString("en-IN", { timeZone: "Asia/Kolkata" })} IST</span>
          <Link href="/schema.html" style={{ marginLeft: "auto", fontSize: 12, color: "#19e6a7", textDecoration: "none", border: "1px solid rgba(25,230,167,0.35)", background: "rgba(25,230,167,0.07)", borderRadius: 999, padding: "6px 12px" }}>Open static HTML →</Link>
        </div>
        <p style={{ marginTop: 6, color: "#9bafb0", fontSize: 13, lineHeight: 1.6, maxWidth: 720 }}>Standalone page — no login, no admin. Live <code style={{ background: "rgba(255,255,255,0.06)", borderRadius: 4, padding: "1px 5px", fontSize: 11 }}>GET /api/public/schema</code> + <code>information_schema</code> + <code>pg_total_relation_size</code>. PK mint · FK blue · UQ amber. For admin gated version see <code>/admin/schema</code>.</p>

        <div style={{ marginTop: 16, padding: 14, background: "linear-gradient(180deg,rgba(19,44,47,0.55),rgba(11,32,35,0.9))", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 12 }}>
          <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Filter tables or columns… (users, job_id, timestamptz)" style={{ width: "100%", maxWidth: 420, background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 10, color: "#f5f7f7", padding: "9px 12px", fontSize: 13, outline: "none" }} />
          <div style={{ marginTop: 10, display: "flex", flexWrap: "wrap", gap: 8 }}>
            {data.issues.slice(0, 6).map((iss: any, i: number) => (
              <span key={i} style={{ fontSize: 11, background: iss.level === "high" ? "rgba(242,109,109,0.12)" : iss.level === "medium" ? "rgba(245,177,76,0.10)" : "rgba(255,255,255,0.04)", border: `1px solid ${iss.level === "high" ? "rgba(242,109,109,0.3)" : iss.level === "medium" ? "rgba(245,177,76,0.28)" : "rgba(255,255,255,0.08)"}`, borderRadius: 999, padding: "4px 8px", color: iss.level === "high" ? "#f26d6d" : iss.level === "medium" ? "#f5b14c" : "#9bafb0" }}>{iss.level}: {iss.title}</span>
            ))}
            <span style={{ fontSize: 11, color: "#657a7c", marginLeft: 6 }}>{data.issues.length} notes total — see /admin/schema for full analysis</span>
          </div>
        </div>

        <div style={{ marginTop: 16, display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))", gap: 16 }}>
          {filtered.map((t: any) => {
            const pks = new Set<string>(t.pks);
            const fks = new Set<string>(t.fks.map((f: any) => f.column_name));
            const uqs = new Set<string>(t.uniques);
            return (
              <div key={t.name} style={{ background: "linear-gradient(180deg,rgba(19,44,47,0.55),rgba(11,32,35,0.9))", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 12, overflow: "hidden", display: "flex", flexDirection: "column" }}>
                <div style={{ padding: "12px 14px 10px", borderBottom: "1px solid rgba(255,255,255,0.08)", background: "rgba(255,255,255,0.015)" }}>
                  <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                    <span style={{ fontFamily: "ui-monospace,monospace", fontSize: 13, fontWeight: 800 }}>{t.name}</span>
                    <span style={{ fontSize: 11, color: "#657a7c" }}>{t.columns.length} cols</span>
                    <span style={{ marginLeft: "auto", fontSize: 11, color: "#9bafb0" }}>{fmtBytes(t.size.total_bytes)}</span>
                  </div>
                  <div style={{ fontSize: 11, color: "#657a7c", marginTop: 6 }}>rows ~{t.size.est_rows.toLocaleString()} {t.size.exact_rows !== null ? `· exact ${t.size.exact_rows.toLocaleString()}` : ""} · PK {t.pks.join(", ") || "—"}</div>
                </div>
                <div style={{ padding: "8px 14px", flex: 1 }}>
                  {t.columns.map((col: any) => (
                    <div key={col.column_name} style={{ display: "grid", gridTemplateColumns: "1fr 100px 70px", gap: 8, padding: "5px 0", borderBottom: "1px solid rgba(255,255,255,0.04)", fontSize: 12, alignItems: "center" }}>
                      <span style={{ display: "flex", gap: 6, alignItems: "center", overflow: "hidden" }}>
                        <span style={{ fontFamily: "ui-monospace,monospace", fontWeight: pks.has(col.column_name) ? 800 : 400, color: pks.has(col.column_name) ? "#19e6a7" : "#f5f7f7", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{col.column_name}</span>
                        {pks.has(col.column_name) && <span style={{ fontSize: 8, fontWeight: 800, background: "#19e6a7", color: "#052e22", borderRadius: 3, padding: "1px 4px" }}>PK</span>}
                        {fks.has(col.column_name) && <span style={{ fontSize: 8, fontWeight: 700, color: "#5d8cff", border: "1px solid rgba(93,140,255,0.35)", background: "rgba(93,140,255,0.08)", borderRadius: 3, padding: "1px 4px" }}>FK</span>}
                        {uqs.has(col.column_name) && !pks.has(col.column_name) && <span style={{ fontSize: 8, fontWeight: 700, color: "#f5b14c", border: "1px solid rgba(245,177,76,0.35)", background: "rgba(245,177,76,0.07)", borderRadius: 3, padding: "1px 4px" }}>UQ</span>}
                      </span>
                      <span style={{ fontFamily: "ui-monospace,monospace", fontSize: 10, color: "#9bafb0", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{col.udt_name}</span>
                      <span style={{ textAlign: "right", fontSize: 10, color: col.is_nullable === "YES" ? "#657a7c" : "#9bafb0" }}>{col.is_nullable === "YES" ? "NULL" : "NOT NULL"}</span>
                    </div>
                  ))}
                </div>
                <div style={{ padding: "8px 14px", borderTop: "1px solid rgba(255,255,255,0.08)", background: "rgba(0,0,0,0.12)" }}>
                  <div style={{ fontSize: 10, fontWeight: 700, letterSpacing: "0.08em", color: "#657a7c", textTransform: "uppercase" }}>Indexes ({t.indexes.length}) · FKs ({t.fks.length})</div>
                  {t.fks.length > 0 && <div style={{ marginTop: 6, display: "flex", flexWrap: "wrap", gap: 6 }}>{t.fks.map((fk: any) => <span key={fk.constraint_name} style={{ fontSize: 10, fontFamily: "ui-monospace,monospace", background: "rgba(93,140,255,0.08)", border: "1px solid rgba(93,140,255,0.18)", borderRadius: 5, padding: "2px 6px" }}>{fk.column_name} → {fk.foreign_table}.{fk.foreign_column} {fk.delete_rule}</span>)}</div>}
                </div>
              </div>
            );
          })}
        </div>
        <p style={{ marginTop: 16, fontSize: 11, color: "#657a7c", lineHeight: 1.6 }}>Public endpoint <code style={{ background: "rgba(255,255,255,0.06)", borderRadius: 4, padding: "1px 5px" }}>GET /api/public/schema</code> — no auth, never blank. Admin full analysis with HIGH/MEDIUM notes at <code>/admin/schema</code>.</p>
      </div>
    </div>
  );
}
