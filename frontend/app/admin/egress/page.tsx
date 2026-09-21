"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import styles from "@/components/ink/ink.module.css";
import { ErrorState, LoadingState, PageHeader, Stat, StatusPill } from "@/components/ink/ui";
import { api } from "@/lib/api";
import { errText, formatDuration } from "@/lib/format";
import type { EgressResponse } from "@/lib/types";

/* ---- helpers ---- */
function fmtBytes(n: number): string {
  if (!Number.isFinite(n) || n <= 0) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  let v = n;
  let i = 0;
  while (v >= 1024 && i < units.length - 1) {
    v /= 1024;
    i += 1;
  }
  return `${v.toFixed(v >= 100 ? 0 : v >= 10 ? 1 : 1)} ${units[i]}`;
}

function pct(n: number, d: number): number {
  if (!d) return 0;
  return Math.min(100, (n / d) * 100);
}

function shortDateISO(iso: string): string {
  try {
    const d = new Date(iso + "T00:00:00");
    return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  } catch {
    return iso.slice(5);
  }
}

function timeAgo(iso: string | null): string {
  if (!iso) return "—";
  const ms = Date.now() - new Date(iso).getTime();
  if (Number.isNaN(ms)) return "—";
  const m = Math.floor(ms / 60000);
  if (m < 1) return "just now";
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}

function levelTone(level: string): "bad" | "warn" | "info" | "muted" {
  if (level === "critical") return "bad";
  if (level === "warn") return "warn";
  if (level === "info") return "info";
  return "muted";
}

/* ---- small ui ---- */
function Bar({ valuePct, color }: { valuePct: number; color?: string }) {
  return (
    <span
      style={{
        display: "block",
        height: 6,
        borderRadius: 999,
        background: "rgba(255,255,255,0.08)",
        overflow: "hidden",
      }}
    >
      <span
        style={{
          display: "block",
          height: "100%",
          width: `${Math.max(2, Math.min(100, valuePct))}%`,
          background: color || "var(--ink-mint)",
          borderRadius: 999,
        }}
      />
    </span>
  );
}

function Usage({ used, limit, label }: { used: number; limit: number; label: string }) {
  const p = pct(used, limit);
  const tone = p >= 90 ? "var(--ink-danger)" : p >= 70 ? "var(--ink-warn)" : "var(--ink-mint)";
  return (
    <div style={{ marginTop: 10 }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: "var(--ink-muted)" }}>
        <span>{label}</span>
        <span style={{ color: tone, fontWeight: 700 }}>{p.toFixed(1)}%</span>
      </div>
      <div style={{ marginTop: 6 }}>
        <Bar valuePct={p} color={tone} />
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: "var(--ink-muted)", marginTop: 4 }}>
        <span>{fmtBytes(used)} used</span>
        <span>{fmtBytes(limit)} limit</span>
      </div>
    </div>
  );
}

export default function EgressPage() {
  const [days, setDays] = useState<7 | 14 | 30>(30);
  const [data, setData] = useState<EgressResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);
  const [auto, setAuto] = useState(false);

  const load = useCallback(async () => {
    setErr(null);
    try {
      const r = await api.egress(days);
      setData(r);
    } catch (e) {
      setErr(errText(e));
    } finally {
      setLoading(false);
    }
  }, [days]);

  useEffect(() => {
    setLoading(true);
    load();
  }, [load]);

  useEffect(() => {
    if (!auto) return;
    const id = setInterval(load, 30_000);
    return () => clearInterval(id);
  }, [auto, load]);

  const jobsTable = useMemo(
    () => (data?.tables || []).find((t) => t.name === "jobs") || null,
    [data],
  );

  if (loading && !data) return <LoadingState label="Measuring database…" rows={8} />;
  if (err && !data) return <ErrorState message={err} onRetry={load} />;

  const db = data?.database;
  const totals = data?.totals;
  const retention = data?.retention;

  const chartMax = Math.max(1, ...((data?.daily || []).map((d) => d.bytes_est) || [1]));

  return (
    <div>
      <PageHeader
        eyebrow="Admin · Observability"
        title="Database Egress"
        desc="Live storage, ingest pressure and what actually leaves the DB. Storage = what you hold. Egress = what you send — every API read, poll write and alert."
        action={
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
            <select
              className={styles.toolInput}
              value={days}
              onChange={(e) => {
                setDays(Number(e.target.value) as 7 | 14 | 30);
                setLoading(true);
              }}
              aria-label="Days"
            >
              <option value={7}>Last 7 days</option>
              <option value={14}>Last 14 days</option>
              <option value={30}>Last 30 days</option>
            </select>
            <label style={{ display: "inline-flex", alignItems: "center", gap: 6, fontSize: 12, color: "var(--ink-text2)" }}>
              <span className={styles.switch} style={{ transform: "scale(0.92)" }}>
                <input type="checkbox" checked={auto} onChange={(e) => setAuto(e.target.checked)} />
                <span className={styles.switchTrack} />
              </span>
              Auto-refresh
            </label>
            <button type="button" className={styles.btnLine} onClick={load}>
              Refresh
            </button>
          </div>
        }
      />

      {data?.warnings && data.warnings.length > 0 && (
        <div style={{ display: "grid", gap: 10, marginBottom: 18 }}>
          {data.warnings.map((w, i) => (
            <div
              key={i}
              style={{
                display: "flex",
                gap: 12,
                alignItems: "flex-start",
                padding: "12px 14px",
                borderRadius: 12,
                border: `1px solid ${
                  w.level === "critical"
                    ? "rgba(242,109,109,0.4)"
                    : w.level === "warn"
                      ? "rgba(245,177,76,0.38)"
                      : "rgba(93,140,255,0.32)"
                }`,
                background:
                  w.level === "critical"
                    ? "rgba(242,109,109,0.08)"
                    : w.level === "warn"
                      ? "rgba(245,177,76,0.07)"
                      : "rgba(93,140,255,0.07)",
              }}
            >
              <span style={{ marginTop: 2 }}>
                <StatusPill tone={levelTone(w.level)}>{w.level === "critical" ? "CRITICAL" : w.level === "warn" ? "WARN" : "INFO"}</StatusPill>
              </span>
              <div style={{ minWidth: 0 }}>
                <div style={{ fontSize: 13, fontWeight: 700, color: "var(--ink-text)" }}>{w.title}</div>
                <div style={{ fontSize: 12.5, color: "var(--ink-text2)", marginTop: 2, lineHeight: 1.5 }}>{w.detail}</div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* KPI row */}
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4" style={{ marginBottom: 18 }}>
        <div className={styles.statMini}>
          <div className={`${styles.statMiniValue} ${db && db.free_pct >= 90 ? styles.toneBad : db && db.free_pct >= 70 ? styles.toneWarn : styles.toneOk}`}>
            {fmtBytes(db?.size_bytes || 0)}
          </div>
          <div className={styles.statMiniLabel}>Total DB size</div>
          <div className={styles.statMiniLabel} style={{ fontVariantNumeric: "tabular-nums" }}>
            {(totals?.jobs_total ?? 0).toLocaleString()} jobs · {(totals?.active_sources ?? 0).toLocaleString()} sources active
          </div>
          {db && <Usage used={db.size_bytes} limit={db.free_limit_bytes} label="Free tier (500 MB)" />}
          {db && (
            <div style={{ marginTop: 6, fontSize: 11, color: "var(--ink-muted)" }}>
              Pro headroom: {db.pro_pct.toFixed(2)}% of 8 GB · {fmtBytes(db.pro_limit_bytes - db.size_bytes)} free
            </div>
          )}
        </div>

        <div className={styles.statMini}>
          <div className={styles.statMiniValue}>{jobsTable ? fmtBytes(jobsTable.total_bytes) : "—"}</div>
          <div className={styles.statMiniLabel}>
            Jobs table
            {jobsTable && db ? ` · ${(pct(jobsTable.total_bytes, db.size_bytes)).toFixed(1)}% of DB` : ""}
          </div>
          {jobsTable && (
            <>
              <div style={{ marginTop: 8 }}>
                <Bar valuePct={db ? pct(jobsTable.total_bytes, db.size_bytes) : 0} />
              </div>
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: 8,
                  marginTop: 10,
                  fontSize: 11,
                  color: "var(--ink-muted)",
                }}
              >
                <span>Data {fmtBytes(jobsTable.table_bytes)}</span>
                <span>Index {fmtBytes(jobsTable.index_bytes)}</span>
                <span>TOAST {fmtBytes(jobsTable.toast_bytes)}</span>
                <span>Avg {fmtBytes(jobsTable.avg_row_bytes)}/row</span>
              </div>
            </>
          )}
        </div>

        <div className={styles.statMini}>
          <div className={styles.statMiniValue}>{fmtBytes(totals?.bytes_24h_est || 0)}</div>
          <div className={styles.statMiniLabel}>
            24h ingest · {(totals?.jobs_24h ?? 0).toLocaleString()} new jobs
          </div>
          <div className={styles.statMiniLabel}>
            7d ingest · {fmtBytes(totals?.bytes_7d_est || 0)} ({(totals?.jobs_7d ?? 0).toLocaleString()} jobs)
          </div>
          <div style={{ marginTop: 10, display: "flex", gap: 6, flexWrap: "wrap" }}>
            <span className={`${styles.statusTag} ${styles.ok}`} style={{ fontSize: 11 }}>
              30d {fmtBytes(totals?.bytes_30d_est || 0)}
            </span>
            <span className={`${styles.statusTag} ${styles.muted}`} style={{ fontSize: 11 }}>
              avg {fmtBytes(totals?.avg_job_bytes || 0)}/job
            </span>
          </div>
          <div style={{ marginTop: 8, fontSize: 11, color: "var(--ink-muted)", lineHeight: 1.4 }}>
            Baseline egress from new rows only. Actual egress higher — every API hit re-sends jobs to users.
          </div>
        </div>

        <div className={styles.statMini}>
          <div className={styles.statMiniValue}>{fmtBytes(totals?.proj_monthly_bytes || 0)}</div>
          <div className={styles.statMiniLabel}>
            Projected 30d · {(totals?.proj_monthly_jobs ?? 0).toLocaleString()} jobs
          </div>
          <div className={styles.statMiniLabel} style={{ marginTop: 4 }}>
            Retention {retention?.retention_days ?? 30}d · reclaimable {fmtBytes(retention?.reclaimable_bytes_est || 0)}
          </div>
          <div style={{ marginTop: 10 }}>
            <Bar
              valuePct={db ? pct((db.size_bytes || 0) + (totals?.proj_monthly_bytes || 0), db.free_limit_bytes) : 0}
              color={(db ? (db.size_bytes + (totals?.proj_monthly_bytes || 0)) / db.free_limit_bytes : 0) > 0.85 ? "var(--ink-warn)" : undefined}
            />
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: "var(--ink-muted)", marginTop: 4 }}>
              <span>Now {fmtBytes(db?.size_bytes || 0)}</span>
              <span>+30d {fmtBytes((db?.size_bytes || 0) + (totals?.proj_monthly_bytes || 0))}</span>
            </div>
          </div>
          {data?.cache?.hit_ratio != null && (
            <div style={{ marginTop: 8, fontSize: 11, color: data.cache.hit_ratio < 85 ? "var(--ink-warn)" : "var(--ink-muted)" }}>
              Buffer hit {data.cache.hit_ratio}% · {data.cache.hit_ratio < 85 ? "disk reads high" : "cache healthy"}
            </div>
          )}
        </div>
      </div>

      {/* Chart + top contributors */}
      <div className={styles.grid2} style={{ marginBottom: 18 }}>
        <div className={styles.panel} style={{ padding: 18 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
            <span style={{ fontSize: 14, fontWeight: 700 }}>Daily ingest — egress pressure</span>
            <span style={{ marginLeft: "auto", fontSize: 11, color: "var(--ink-muted)" }}>
              Est. bytes = jobs × {fmtBytes(totals?.avg_job_bytes || 0)}/row · match/alert overlay
            </span>
          </div>
          {(!data?.daily || data.daily.length === 0) ? (
            <p className={styles.emptyNote}>No daily data.</p>
          ) : (
            <>
              <div
                style={{
                  display: "flex",
                  alignItems: "flex-end",
                  gap: 6,
                  height: 132,
                  paddingTop: 22,
                }}
              >
                {data.daily.map((d) => {
                  const h = Math.max(3, Math.round((d.bytes_est / chartMax) * 100));
                  const isMax = d.bytes_est === chartMax && d.bytes_est > 0;
                  return (
                    <div key={d.date} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 6, height: "100%", justifyContent: "flex-end" }}>
                      <div
                        title={`${d.date}: ${d.jobs} jobs · ${fmtBytes(d.bytes_est)} · ${d.matches} matches · ${d.alerts} alerts`}
                        style={{
                          width: "100%",
                          maxWidth: 22,
                          height: `${h}%`,
                          borderRadius: "5px 5px 2px 2px",
                          background: "linear-gradient(180deg, #19e6a7, rgba(12,143,122,0.55))",
                          position: "relative",
                          minHeight: 4,
                        }}
                      >
                        {isMax && (
                          <span
                            style={{
                              position: "absolute",
                              top: -20,
                              left: "50%",
                              transform: "translateX(-50%)",
                              background: "var(--ink-mint)",
                              color: "#052e22",
                              fontSize: 10,
                              fontWeight: 800,
                              borderRadius: 6,
                              padding: "2px 6px",
                              whiteSpace: "nowrap",
                            }}
                          >
                            {fmtBytes(d.bytes_est)}
                          </span>
                        )}
                      </div>
                      <span style={{ fontSize: 9.5, color: "var(--ink-muted)", whiteSpace: "nowrap" }}>{shortDateISO(d.date)}</span>
                    </div>
                  );
                })}
              </div>
              <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginTop: 12, fontSize: 11, color: "var(--ink-muted)" }}>
                {data.daily.slice(-7).map((d) => (
                  <span key={d.date} style={{ display: "inline-flex", gap: 4 }}>
                    <strong style={{ color: "var(--ink-text2)" }}>{shortDateISO(d.date)}</strong> {d.jobs} jobs · {d.matches} matches
                  </span>
                ))}
              </div>
            </>
          )}
          {err && (
            <p style={{ fontSize: 12, color: "var(--ink-danger)", marginTop: 10 }}>{err}</p>
          )}
          <div style={{ marginTop: 12, fontSize: 11, color: "var(--ink-muted)", lineHeight: 1.5 }}>
            How to read this: each bar is new DB bytes for that day (jobs inserted × avg row size). Spikes = many new jobs or large rows. Matches/alerts ride on top — egress multiplies when the API serves the same jobs to many users.
          </div>

          {/* 24h hourly sparkline — early warning for 500 MB → 8 GB */}
          {data?.hourly && data.hourly.length > 0 && (
            <div style={{ marginTop: 18, paddingTop: 14, borderTop: "1px solid rgba(255,255,255,0.06)" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                <span style={{ fontSize: 12, fontWeight: 700, color: "var(--ink-text)" }}>Last 24h — hourly ingest</span>
                <span style={{ fontSize: 11, color: "var(--ink-muted)" }}>
                  {data.hourly.reduce((s, h) => s + h.jobs, 0).toLocaleString()} jobs · {fmtBytes(data.hourly.reduce((s, h) => s + h.bytes_est, 0))} · slope → Free / Pro
                </span>
              </div>
              <div style={{ display: "flex", alignItems: "flex-end", gap: 3, height: 48 }}>
                {(() => {
                  const maxH = Math.max(1, ...data.hourly.map((h) => h.bytes_est));
                  return data.hourly.map((h) => {
                    const pctH = Math.max(2, Math.round((h.bytes_est / maxH) * 100));
                    const hourLabel = h.hour.slice(11, 13) + ":00";
                    return (
                      <div
                        key={h.hour}
                        title={`${h.hour}: ${h.jobs} jobs · ${fmtBytes(h.bytes_est)} · ${h.matches} matches`}
                        style={{
                          flex: 1,
                          height: `${pctH}%`,
                          minHeight: 2,
                          borderRadius: 2,
                          background: h.jobs > 0 ? "rgba(25,230,167,0.85)" : "rgba(255,255,255,0.06)",
                        }}
                      />
                    );
                  });
                })()}
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 9, color: "var(--ink-muted)", marginTop: 4 }}>
                <span>{data.hourly[0]?.hour.slice(5, 13) || ""}</span>
                <span>now</span>
              </div>
            </div>
          )}
        </div>

        <div className={styles.rail} style={{ gap: 16 }}>
          <div className={styles.railCard}>
            <div className={styles.railHead}>
              <span className={styles.railTitle}>Top egress contributors</span>
              <span style={{ marginLeft: "auto", fontSize: 11, color: "var(--ink-muted)" }}>{(data?.top_sources || []).length} sources</span>
            </div>
            {(data?.top_sources || []).length === 0 ? (
              <p className={styles.emptyNote} style={{ padding: "12px 0" }}>
                No jobs yet.
              </p>
            ) : (
              (data!.top_sources.slice(0, 7).map((s) => (
                <div
                  key={s.company}
                  title={`${s.company} · ${s.job_count} jobs · ${fmtBytes(s.bytes_est)} · ${s.share_pct}%`}
                  style={{
                    display: "grid",
                    gridTemplateColumns: "1fr auto",
                    gap: 8,
                    padding: "9px 0",
                    borderTop: "1px solid rgba(255,255,255,0.05)",
                  }}
                >
                  <div style={{ minWidth: 0 }}>
                    <div style={{ fontSize: 13, fontWeight: 600, color: "var(--ink-text)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                      {s.company}
                    </div>
                    <div style={{ fontSize: 11, color: "var(--ink-muted)" }}>{s.ats_type}</div>
                    <div style={{ marginTop: 6 }}>
                      <Bar valuePct={Math.max(2, s.share_pct)} />
                    </div>
                  </div>
                  <div style={{ textAlign: "right", minWidth: 78 }}>
                    <div style={{ fontSize: 12, fontWeight: 700, fontVariantNumeric: "tabular-nums" }}>{fmtBytes(s.bytes_est)}</div>
                    <div style={{ fontSize: 11, color: "var(--ink-muted)" }}>
                      {s.job_count.toLocaleString()} · {s.share_pct}%
                    </div>
                  </div>
                </div>
              )))
            )}
          </div>

          <div className={styles.railCard}>
            <div className={styles.railHead}>
              <span className={styles.railTitle}>Retention</span>
              <span className={`${styles.statusTag} ${styles.muted}`} style={{ marginLeft: "auto", fontSize: 11 }}>
                {retention?.retention_days ?? 30}d
              </span>
            </div>
            <div style={{ fontSize: 13, color: "var(--ink-text2)", lineHeight: 1.5 }}>
              Jobs older than {retention?.retention_days ?? 30} days are pruned by the retention job.
            </div>
            <div style={{ display: "flex", gap: 8, marginTop: 12, flexWrap: "wrap" }}>
              <Stat label="Reclaimable jobs" value={(retention?.reclaimable_jobs ?? 0).toLocaleString()} sub={fmtBytes(retention?.reclaimable_bytes_est || 0)} />
            </div>
            <div style={{ marginTop: 10 }}>
              <Bar valuePct={totals ? pct(retention?.reclaimable_jobs || 0, totals.jobs_total || 1) : 0} color="var(--ink-warn)" />
              <div style={{ fontSize: 11, color: "var(--ink-muted)", marginTop: 4 }}>
                {totals ? pct(retention?.reclaimable_jobs || 0, totals.jobs_total || 1).toFixed(1) : "0"}% of all jobs would be removed
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Per-table breakdown */}
      <div className={styles.tableWrap} style={{ marginBottom: 18 }}>
        <div style={{ padding: "14px 16px 10px", display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
          <span style={{ fontWeight: 700, fontSize: 14 }}>Per-table breakdown</span>
          <span style={{ fontSize: 11, color: "var(--ink-muted)" }}>
            Total · Data · Index · TOAST · rows · avg row · bloat
          </span>
          <span style={{ marginLeft: "auto", fontSize: 11, color: "var(--ink-muted)" }}>
            Sort: largest first · {data?.tables?.length ?? 0} tables
          </span>
        </div>
        <table className={styles.inkTable} style={{ minWidth: 860 }}>
          <thead>
            <tr>
              <th>Table</th>
              <th style={{ textAlign: "right" }}>Rows</th>
              <th style={{ textAlign: "right" }}>Total</th>
              <th>Share</th>
              <th style={{ textAlign: "right" }}>Data</th>
              <th style={{ textAlign: "right" }}>Index</th>
              <th style={{ textAlign: "right" }}>TOAST</th>
              <th style={{ textAlign: "right" }}>Avg row</th>
              <th>Health</th>
            </tr>
          </thead>
          <tbody>
            {(data?.tables || []).map((t) => {
              const share = db ? pct(t.total_bytes, db.size_bytes) : 0;
              const deadPct = t.live_rows ? (t.dead_rows / Math.max(1, t.live_rows)) * 100 : 0;
              const needsVacuum = deadPct > 15 || t.dead_rows > 8000;
              return (
                <tr key={t.name}>
                  <td style={{ fontWeight: 600, fontFamily: "ui-monospace,monospace", fontSize: 12.5 }}>{t.name}</td>
                  <td style={{ textAlign: "right", fontVariantNumeric: "tabular-nums" }}>{t.live_rows.toLocaleString()}</td>
                  <td style={{ textAlign: "right", fontVariantNumeric: "tabular-nums", fontWeight: 600 }}>{fmtBytes(t.total_bytes)}</td>
                  <td style={{ minWidth: 90 }}>
                    <Bar valuePct={share} />
                    <span style={{ fontSize: 11, color: "var(--ink-muted)" }}>{share.toFixed(1)}%</span>
                  </td>
                  <td style={{ textAlign: "right", fontVariantNumeric: "tabular-nums", color: "var(--ink-text2)" }}>{fmtBytes(t.table_bytes)}</td>
                  <td style={{ textAlign: "right", fontVariantNumeric: "tabular-nums", color: "var(--ink-text2)" }}>{fmtBytes(t.index_bytes)}</td>
                  <td style={{ textAlign: "right", fontVariantNumeric: "tabular-nums", color: t.toast_bytes > 1024 ? "var(--ink-warn)" : "var(--ink-muted)" }}>
                    {fmtBytes(t.toast_bytes)}
                  </td>
                  <td style={{ textAlign: "right", fontVariantNumeric: "tabular-nums" }}>{fmtBytes(t.avg_row_bytes)}</td>
                  <td>
                    {needsVacuum ? (
                      <StatusPill tone="warn">dead {t.dead_rows.toLocaleString()}</StatusPill>
                    ) : t.dead_rows > 800 ? (
                      <StatusPill tone="muted">dead {t.dead_rows.toLocaleString()}</StatusPill>
                    ) : (
                      <StatusPill tone="ok">ok</StatusPill>
                    )}
                    <div style={{ fontSize: 11, color: "var(--ink-muted)", marginTop: 2 }}>
                      {t.last_autovacuum ? `vacuum ${timeAgo(t.last_autovacuum)}` : t.last_vacuum ? `vac ${timeAgo(t.last_vacuum)}` : "never"}
                    </div>
                  </td>
                </tr>
              );
            })}
            {(!data?.tables || data.tables.length === 0) && (
              <tr>
                <td colSpan={9} style={{ textAlign: "center", color: "var(--ink-muted)", padding: 20 }}>
                  No table stats.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Recent poll runs */}
      <div className={styles.tableWrap} style={{ marginBottom: 18 }}>
        <div style={{ padding: "14px 16px 10px", display: "flex", gap: 10, alignItems: "center" }}>
          <span style={{ fontWeight: 700, fontSize: 14 }}>Recent poll runs — egress footprint</span>
          <span style={{ fontSize: 11, color: "var(--ink-muted)" }}>fetched vs new × avg row = new bytes per run</span>
          <span style={{ marginLeft: "auto", fontSize: 11, color: "var(--ink-muted)" }}>{data?.recent_runs?.length ?? 0} runs</span>
        </div>
        <table className={styles.inkTable} style={{ minWidth: 780 }}>
          <thead>
            <tr>
              <th>When</th>
              <th>Trigger</th>
              <th>ATS</th>
              <th>Status</th>
              <th style={{ textAlign: "right" }}>Fetched</th>
              <th style={{ textAlign: "right" }}>New</th>
              <th style={{ textAlign: "right" }}>Bytes</th>
              <th style={{ textAlign: "right" }}>Duration</th>
              <th>Error</th>
            </tr>
          </thead>
          <tbody>
            {(data?.recent_runs || []).map((r) => (
              <tr key={r.id}>
                <td style={{ whiteSpace: "nowrap", fontSize: 12 }} title={r.started_at || ""}>
                  {timeAgo(r.started_at)}<br />
                  <span style={{ color: "var(--ink-muted)", fontSize: 11 }}>{r.started_at ? new Date(r.started_at).toLocaleString("en-IN", { timeZone: "Asia/Kolkata", month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }) : "—"}</span>
                </td>
                <td>
                  <span className={`${styles.statusTag} ${r.triggered_by === "manual" ? styles.info : styles.muted}`} style={{ fontSize: 11 }}>
                    {r.triggered_by}
                  </span>
                </td>
                <td style={{ fontSize: 12 }}>{r.ats_type || "—"}</td>
                <td>
                  <StatusPill tone={r.status === "completed" ? "ok" : r.status === "failed" ? "bad" : "warn"}>{r.status}</StatusPill>
                </td>
                <td style={{ textAlign: "right", fontVariantNumeric: "tabular-nums" }}>{r.jobs_fetched.toLocaleString()}</td>
                <td style={{ textAlign: "right", fontVariantNumeric: "tabular-nums", fontWeight: 700, color: r.jobs_new > 0 ? "var(--ink-mint)" : undefined }}>
                  {r.jobs_new.toLocaleString()}
                </td>
                <td style={{ textAlign: "right", fontVariantNumeric: "tabular-nums" }}>{fmtBytes(r.bytes_est)}</td>
                <td style={{ textAlign: "right", fontVariantNumeric: "tabular-nums", fontSize: 12 }}>{r.duration_ms != null ? formatDuration(r.duration_ms) : "—"}</td>
                <td style={{ maxWidth: 220, overflow: "hidden", textOverflow: "ellipsis", fontSize: 11, color: "var(--ink-danger)" }}>{r.error ? r.error.slice(0, 80) : "—"}</td>
              </tr>
            ))}
            {(!data?.recent_runs || data.recent_runs.length === 0) && (
              <tr>
                <td colSpan={9} style={{ textAlign: "center", color: "var(--ink-muted)", padding: 20 }}>
                  No runs yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Playbook */}
      <div className={styles.railCard}>
        <div className={styles.railHead}>
          <span className={styles.railTitle}>What to do when this page is red</span>
        </div>
        <div style={{ display: "grid", gap: 10, fontSize: 13, color: "var(--ink-text2)", lineHeight: 1.6 }}>
          <div>
            <strong style={{ color: "var(--ink-text)" }}>Storage high (&gt;70% free tier):</strong> lower <code>JOB_RETENTION_DAYS</code> (e.g. 30 → 14), disable low-value sources, or upgrade to Pro (8 GB). Descriptions are already stripped — retention is the biggest lever.
          </div>
          <div>
            <strong style={{ color: "var(--ink-text)" }}>Egress spike:</strong> check Daily ingest and Top contributors. A single noisy ATS can dominate — throttle its interval in <em>Schedule</em> or pause the source.
          </div>
          <div>
            <strong style={{ color: "var(--ink-text)" }}>Dead rows / bloat:</strong> VACUUM or wait for autovacuum. If a table stays red for hours, run <code>VACUUM (ANALYZE) table_name;</code> from Supabase SQL editor.
          </div>
          <div>
            <strong style={{ color: "var(--ink-text)" }}>API egress higher than ingest:</strong> expected — every <code>/api/jobs</code> call re-sends the same rows. Add frontend caching, pagination, or CDN if your public API is hot. This page shows the DB-side baseline; HTTP egress multiplies on reads.
          </div>
          <div style={{ fontSize: 11, color: "var(--ink-muted)", borderTop: "1px solid var(--ink-border)", paddingTop: 10 }}>
            Generated {data?.generated_at ? new Date(data.generated_at).toLocaleString("en-IN", { timeZone: "Asia/Kolkata" }) : "—"} IST · DB size via <code>pg_database_size</code> · table sizes via <code>pg_total_relation_size</code> · estimates use avg row size ({fmtBytes(totals?.avg_job_bytes || 0)}/row) · Supabase free 500 MB / pro 8 GB shown for reference.
          </div>
        </div>
      </div>
    </div>
  );
}
