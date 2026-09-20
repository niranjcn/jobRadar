"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { RadarLoading } from "@/components/radar-loading";
import { PageHeader, Stat } from "@/components/ink/ui";
import styles from "@/components/ink/ink.module.css";
import { api } from "@/lib/api";
import { atsLabel, formatDuration, formatRunDuration } from "@/lib/format";
import type { PollRun } from "@/lib/types";

// Estimated wall time for global ("All") runs: per-source durations execute N-way
// parallel per ATS, so wall ≈ Σ(duration_ms) ÷ concurrency. A raw Σ would show
// e.g. 160m for 284 workday boards that actually finished in ~9m at 20-way.
// Mirrors backend/app/config.py ATS_CONCURRENCY — keep in sync when tuning.
const ATS_CONCURRENCY: Record<string, number> = {
  greenhouse: 16,
  lever: 16,
  ashby: 16,
  remotive: 16,
  weworkremotely: 16,
  workday: 20,
  oracle: 10,
  successfactors: 10,
  phenom: 8,
  avature: 10,
  custom: 8,
  emirates: 8,
  icims: 8,
  google: 8,
  amazon: 8,
};

function estWallMs(ats: string, sumMs: number): { wall: number; conc: number } {
  const conc = ATS_CONCURRENCY[ats] || 8;
  return { wall: sumMs / conc, conc };
}

function runDurationMs(run: PollRun): number | null {
  if (!run.started_at || !run.finished_at) return null;
  const s = new Date(run.started_at).getTime();
  const f = new Date(run.finished_at).getTime();
  if (Number.isNaN(s) || Number.isNaN(f) || f < s) return null;
  return f - s;
}

function perAtsStats(runs: PollRun[]) {
  const byAts: Record<string, { runs: number; totalMs: number; avgMs: number; lastMs: number | null; sources: number; ok: number; sumMs: number; conc: number }> = {};
  for (const r of runs) {
    if (r.status !== "completed") continue;
    const dur = runDurationMs(r);
    // For per-ATS scheduled runs, the ats_type is the adapter.
    // For global runs, split by sources.
    if (r.ats_type) {
      const a = r.ats_type;
      if (!byAts[a]) byAts[a] = { runs: 0, totalMs: 0, avgMs: 0, lastMs: null, sources: 0, ok: 0, sumMs: 0, conc: 1 };
      byAts[a].runs += 1;
      if (dur != null) {
        byAts[a].totalMs += dur;
        byAts[a].lastMs = dur;
      }
      const ok = (r.sources || []).filter((s) => s.status === "ok").length;
      byAts[a].ok += ok;
      byAts[a].sources += (r.sources || []).length;
    } else {
      // Global: Σ(duration_ms) per ATS overstates wall time N-fold (N-way parallel),
      // so store the estimated wall (Σ ÷ concurrency) instead of the raw sum.
      const perAts: Record<string, number> = {};
      for (const s of r.sources || []) {
        const a = s.ats_type || "custom";
        perAts[a] = (perAts[a] || 0) + (s.duration_ms || 0);
      }
      const hasPerSource = Object.values(perAts).some((v) => v > 0);
      if (hasPerSource) {
        for (const [a, ms] of Object.entries(perAts)) {
          if (!byAts[a]) byAts[a] = { runs: 0, totalMs: 0, avgMs: 0, lastMs: null, sources: 0, ok: 0, sumMs: 0, conc: ATS_CONCURRENCY[a] || 8 };
          const { wall, conc } = estWallMs(a, ms);
          byAts[a].runs += 1;
          byAts[a].totalMs += wall;
          byAts[a].lastMs = wall;
          byAts[a].sumMs += ms;
          byAts[a].conc = conc;
          byAts[a].sources += (r.sources || []).filter((s) => s.ats_type === a).length;
          byAts[a].ok += (r.sources || []).filter((s) => s.ats_type === a && s.status === "ok").length;
        }
      } else if (dur != null) {
        // No per-source timing yet (old runs) — count as mixed
        const a = "mixed";
        if (!byAts[a]) byAts[a] = { runs: 0, totalMs: 0, avgMs: 0, lastMs: null, sources: 0, ok: 0, sumMs: 0, conc: 1 };
        byAts[a].runs += 1;
        byAts[a].totalMs += dur;
        byAts[a].lastMs = dur;
      }
    }
  }
  for (const v of Object.values(byAts)) v.avgMs = v.runs ? v.totalMs / v.runs : 0;
  return Object.entries(byAts)
    .map(([ats, v]) => ({ ats, ...v }))
    .sort((a, b) => b.avgMs - a.avgMs);
}

export default function TimingsPage() {
  const [runs, setRuns] = useState<PollRun[] | null>(null);

  const load = useCallback(() => {
    api.pollRuns(50).then((res) => setRuns(res.runs));
  }, []);

  useEffect(() => {
    load();
    const id = setInterval(() => {
      if (document.hidden) return;
      load();
    }, 15000);
    return () => clearInterval(id);
  }, [load]);

  const stats = useMemo(() => (runs ? perAtsStats(runs) : []), [runs]);
  const maxAvg = Math.max(1, ...stats.map((s) => s.avgMs));

  const avgs = useMemo(() => {
    const done = (runs || []).filter((r) => r.status === "completed");
    const durs = done.map(runDurationMs).filter((v): v is number => v != null);
    const avg = durs.length ? durs.reduce((s, v) => s + v, 0) / durs.length : null;
    return { avg };
  }, [runs]);

  if (!runs)
    return (
      <div className={styles.content}>
        <RadarLoading label="Loading poll timings…" />
      </div>
    );

  return (
    <div className={styles.content}>
      <PageHeader
        eyebrow="System"
        title="Timings"
        desc={`Understand how JobQuest's systems are performing.${runs.length ? ` Last ${runs.length} runs.` : ""}`}
      />

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4" style={{ marginBottom: 20 }}>
        <Stat label="Avg scrape time" value={avgs.avg != null ? formatDuration(Math.round(avgs.avg)) : "—"} />
        <Stat label="Runs analyzed" value={runs.length} />
        <Stat label="Adapters tracked" value={stats.length} />
        <Stat
          label="Slowest adapter"
          value={stats.length ? atsLabel(stats[0].ats) : "—"}
          sub={stats.length && stats[0].avgMs ? formatDuration(Math.round(stats[0].avgMs)) : undefined}
        />
      </div>

      <div className="mt-2 rounded-lg border border-primary/20 bg-primary/5 p-3 text-xs text-text-secondary">
        <span className="font-semibold text-text">Tier 1 live:</span> concurrency light 16 · workday 20 · oracle/successfactors/avature 10 · rest 8 · jitter ±120s · 404 backoff 12h · every adapter 1h. Global-run rows show ~est. wall (Σ ÷ concurrency); per-adapter runs show measured wall.
      </div>

      <section className={styles.panel} style={{ marginTop: 20, padding: 20 }}>
        <p style={{ fontSize: 14, fontWeight: 700, margin: "0 0 4px" }}>Scraping performance</p>
        <p style={{ fontSize: 12, color: "var(--ink-muted)", margin: "0 0 12px" }}>Total run duration, most recent last</p>
        {(() => {
          const seq = runs
            .slice(0, 24)
            .map(runDurationMs)
            .filter((v): v is number => v != null)
            .reverse();
          const max = Math.max(1, ...seq);
          if (!seq.length) return <p style={{ fontSize: 13, color: "var(--ink-muted)" }}>No completed runs yet.</p>;
          return (
            <div className={styles.bars} style={{ height: 110 }}>
              {seq.map((ms, i) => (
                <div key={i} className={styles.barCol} title={formatDuration(ms)}>
                  <div className={styles.bar} style={{ height: `${Math.max(4, Math.round((ms / max) * 100))}%` }} />
                </div>
              ))}
            </div>
          );
        })()}
      </section>

      <div className="mt-8 card overflow-hidden">
        <div className="grid grid-cols-12 gap-2 border-b border-border bg-elevated px-4 py-2 text-[11px] uppercase tracking-wide text-text-muted">
          <span className="col-span-3">Adapter</span>
          <span className="col-span-2 text-right">Avg per run</span>
          <span className="col-span-2 text-right">Last run</span>
          <span className="col-span-2 text-right">Runs</span>
          <span className="col-span-3 text-right">Sources ok/total</span>
        </div>
        {stats.length === 0 ? (
          <div className="p-8 text-center text-sm text-text-muted">No completed runs with timing yet. Trigger a poll.</div>
        ) : (
          stats.map((s) => (
            <div key={s.ats} className="grid grid-cols-12 items-center gap-2 border-b border-border/50 px-4 py-3 last:border-0">
              <span className="col-span-3 text-sm font-medium">{atsLabel(s.ats)}</span>
              <span className="col-span-2 text-right font-mono text-sm">
                {s.sumMs > 0 ? "~" : ""}{formatDuration(Math.round(s.avgMs))}
                {s.sumMs > 0 && s.runs > 0 ? (
                  <span className="block text-[10px] text-text-muted" title="Sum of per-source durations ÷ per-ATS concurrency ≈ wall time">
                    Σ{formatDuration(Math.round(s.sumMs / s.runs))} ÷{s.conc}
                  </span>
                ) : null}
              </span>
              <span className="col-span-2 text-right font-mono text-xs text-text-muted">{s.lastMs != null ? formatDuration(s.lastMs) : "—"}</span>
              <span className="col-span-2 text-right text-sm">{s.runs}</span>
              <span className="col-span-3 flex items-center justify-end gap-2 text-sm">
                <span className="text-text-muted">{s.ok}/{s.sources}</span>
                <div className="hidden h-1.5 w-16 overflow-hidden rounded bg-border sm:block">
                  <div className="h-full bg-primary" style={{ width: `${Math.max(4, (s.avgMs / maxAvg) * 100)}%` }} />
                </div>
              </span>
            </div>
          ))
        )}
      </div>

      <div className="mt-8">
        <h2 className="text-[15px] font-semibold">Recent runs — total + per-adapter split</h2>
        <div className="mt-3 space-y-3">
          {runs.slice(0, 20).map((r) => {
            const total = formatRunDuration(r.started_at, r.finished_at);
            const wallMs = runDurationMs(r);
            // Per-ATS run: the run wall IS this adapter's wall (measured).
            // Global run: Σ per ATS overstates wall N-fold → show Σ ÷ concurrency.
            const byAts: Record<string, { wall: number; conc: number; sum: number; est: boolean }> = {};
            if (r.ats_type && wallMs != null) {
              byAts[r.ats_type] = { wall: wallMs, conc: 1, sum: wallMs, est: false };
            } else {
              for (const s of r.sources || []) {
                const a = s.ats_type || "custom";
                if (!byAts[a]) {
                  const conc = ATS_CONCURRENCY[a] || 8;
                  byAts[a] = { wall: 0, conc, sum: 0, est: true };
                }
                byAts[a].sum += s.duration_ms || 0;
              }
              for (const v of Object.values(byAts)) v.wall = v.sum / v.conc;
            }
            const hasPerSource = Object.values(byAts).some((v) => v.sum > 0);
            const maxWall = Math.max(1, ...Object.values(byAts).map((v) => v.wall));
            return (
              <div key={r.id} className="card p-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="text-sm font-medium">
                    {r.triggered_by === "manual" ? "Manual" : "Scheduled"} {r.ats_type ? `· ${atsLabel(r.ats_type)}` : "· All"} · <span className={r.status === "completed" ? "text-success" : r.status === "failed" ? "text-danger" : "text-accent"}>{r.status}</span>
                  </span>
                  <span className="font-mono text-xs text-text-muted">total {total} · {r.jobs_fetched} fetched · {r.jobs_new} new</span>
                </div>
                {hasPerSource ? (
                  <div className="mt-3 space-y-1">
                    {Object.entries(byAts)
                      .sort((a, b) => b[1].wall - a[1].wall)
                      .map(([ats, v]) => (
                        <div key={ats} className="flex items-center gap-2 text-xs" title={v.est ? `Σ ${formatDuration(v.sum)} ÷ ${v.conc} parallel ≈ wall` : "Measured run wall time"}>
                          <span className="w-28 truncate text-text-secondary">{atsLabel(ats)}</span>
                          <div className="h-1 flex-1 overflow-hidden rounded bg-border">
                            <div className="h-full bg-primary/70" style={{ width: `${Math.max(2, (v.wall / maxWall) * 100)}%` }} />
                          </div>
                          <span className="w-16 text-right font-mono text-text-muted">{v.est ? "~" : ""}{formatDuration(v.wall)}</span>
                          <span className="w-12 text-right text-text-muted">{Object.values(byAts).length ? (r.sources || []).filter((s) => s.ats_type === ats && s.status === "ok").length : 0}/{ (r.sources || []).filter((s) => s.ats_type === ats).length }</span>
                        </div>
                      ))}
                  </div>
                ) : (
                  <p className="mt-2 text-xs text-text-muted">Per-adapter timing appears from next run (Tier 1 stores `duration_ms`). Total time above is from `started_at`/`finished_at`.</p>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
