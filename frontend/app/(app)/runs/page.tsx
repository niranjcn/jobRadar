"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { RadarLoading } from "@/components/radar-loading";
import { api } from "@/lib/api";
import { atsLabel, ATS_ORDER, formatDateTime, formatDuration, formatRunDuration, timeIST } from "@/lib/format";
import type { PollRun, UnhealthySource } from "@/lib/types";

const STATUS_META: Record<PollRun["status"], { label: string; className: string }> = {
  running: { label: "Running", className: "bg-accent/15 text-accent" },
  completed: { label: "Completed", className: "bg-success/15 text-success" },
  failed: { label: "Failed", className: "bg-danger/15 text-danger" },
};

function RunStatusCard({ run }: { run: PollRun }) {
  const meta = STATUS_META[run.status];
  const sourcesOk = (run.sources || []).filter((s) => s.status === "ok").length;
  const sourcesErr = (run.sources || []).filter((s) => s.status === "error").length;
  const sourcesSkipped = (run.sources || []).filter((s) => s.status === "skipped").length;
  const totalDur = formatRunDuration(run.started_at, run.finished_at);
  // Per-adapter time from duration_ms (Tier 1). Group by ats_type for the simple bar.
  const byAts = (() => {
    const m: Record<string, { count: number; totalMs: number; ok: number }> = {};
    for (const s of run.sources || []) {
      const a = s.ats_type || "custom";
      if (!m[a]) m[a] = { count: 0, totalMs: 0, ok: 0 };
      m[a].count += 1;
      if (s.status === "ok") m[a].ok += 1;
      if (typeof s.duration_ms === "number") m[a].totalMs += s.duration_ms;
    }
    return Object.entries(m)
      .map(([ats, v]) => ({ ats, ...v }))
      .sort((a, b) => b.totalMs - a.totalMs);
  })();

  return (
    <div className="card p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <h2 className="text-[15px] font-semibold">
            {run.triggered_by === "manual" ? "Manual poll" : "Scheduled poll"}
            {run.ats_type ? ` · ${atsLabel(run.ats_type)}` : " · All sources"}
          </h2>
          <span className={`rounded px-2 py-0.5 text-[11px] ${meta.className}`}>{meta.label}</span>
          {run.status === "running" && (
            <span className="flex items-center gap-1.5 text-[11px] text-accent">
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-accent" />
              in progress…
            </span>
          )}
          {totalDur !== "—" && (
            <span className="rounded bg-elevated px-2 py-0.5 text-[11px] text-text-muted">⏱ {totalDur} total</span>
          )}
        </div>
        <span className="text-xs text-text-muted">
          Started {run.started_at ? timeIST(run.started_at) : "—"}
          {run.finished_at ? ` · Finished ${timeIST(run.finished_at)}` : ""}
        </span>
      </div>

      {run.error && (
        <p className="mt-3 rounded bg-danger/10 p-3 text-xs text-danger">{run.error}</p>
      )}

      <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
        <MiniStat value={run.jobs_fetched} label="Jobs fetched" />
        <MiniStat value={run.jobs_new} label="New jobs" accent="primary" />
        <MiniStat value={run.matches_new} label="New matches" accent="accent" />
        <MiniStat value={run.telegram_sent} label="Telegram sent" accent="success" />
        <MiniStat value={run.email_sent} label="Email sent" accent="success" />
        <MiniStat
          value={
            run.status === "running" ? "…" : `${sourcesOk}/${(run.sources || []).length}`
          }
          label="Sources OK"
        />
      </div>

      {byAts.length > 0 && byAts.some((a) => a.totalMs > 0) && (
        <div className="mt-4 rounded-lg bg-elevated p-3">
          <p className="mb-2 text-xs uppercase tracking-wide text-text-muted">Time per adapter (Tier 1 per-ATS concurrency)</p>
          <div className="space-y-1.5">
            {byAts.map((a) => (
              <div key={a.ats} className="flex items-center gap-2 text-xs">
                <span className="w-32 truncate text-text-secondary">{atsLabel(a.ats)}</span>
                <div className="h-1.5 flex-1 overflow-hidden rounded bg-border">
                  <div
                    className="h-full bg-primary"
                    style={{ width: `${Math.max(4, (a.totalMs / Math.max(1, Math.max(...byAts.map((x) => x.totalMs)))) * 100)}%` }}
                  />
                </div>
                <span className="w-20 text-right font-mono text-text-muted">{formatDuration(a.totalMs)}</span>
                <span className="w-16 text-right text-text-muted">
                  {a.ok}/{a.count}
                </span>
              </div>
            ))}
          </div>
          <p className="mt-1.5 text-[11px] text-text-muted">
            Concurrency now: light 16 (greenhouse/lever/ashby/remotive/wwr) · heavy 4-6 (workday/successfactors) · jitter ±120s
          </p>
        </div>
      )}

      {(run.sources || []).length > 0 && (
        <div className="mt-4">
          <p className="mb-1.5 text-xs uppercase tracking-wide text-text-muted">
            Per source {sourcesSkipped ? <span className="text-warning">· {sourcesSkipped} skipped (404 backoff 12h)</span> : null}
          </p>
          <ul className="divide-y divide-border/50">
            {(run.sources || []).map((s, i) => (
              <li key={i} className="flex items-center justify-between py-1.5 text-sm">
                <span className="flex items-center gap-2">
                  <span
                    className={`h-1.5 w-1.5 rounded-full ${
                      s.status === "ok" ? "bg-success" : s.status === "skipped" ? "bg-warning" : "bg-danger"
                    }`}
                  />
                  <span className="text-text">{s.company}</span>
                  <span className="text-[11px] text-text-muted">{atsLabel(s.ats_type)}</span>
                  {s.status === "skipped" && (
                    <span className="rounded bg-warning/10 px-1.5 py-0.5 text-[10px] text-warning">skipped</span>
                  )}
                </span>
                {s.status === "ok" ? (
                  <span className="flex items-center gap-2 text-xs text-text-muted">
                    <span>
                      {s.fetched ?? 0} fetched · {s.new ?? 0} new
                      {s.first_check ? " · first check" : ""}
                    </span>
                    {typeof s.duration_ms === "number" && (
                      <span className="font-mono text-[11px] text-text-muted">· {formatDuration(s.duration_ms)}</span>
                    )}
                  </span>
                ) : s.status === "skipped" ? (
                  <span className="max-w-[50%] truncate text-xs text-warning" title={s.reason || ""}>
                    {s.reason || "404 backoff 12h"}
                  </span>
                ) : (
                  <span className="max-w-[50%] truncate text-xs text-danger" title={s.error || ""}>
                    {s.error || "failed"}
                  </span>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function MiniStat({
  value,
  label,
  accent,
}: {
  value: string | number;
  label: string;
  accent?: "primary" | "accent" | "success";
}) {
  const color =
    accent === "primary"
      ? "text-primary"
      : accent === "accent"
        ? "text-accent"
        : accent === "success"
          ? "text-success"
          : "text-text";
  return (
    <div className="rounded-lg bg-elevated p-3">
      <div className={`font-serif text-2xl font-semibold ${color}`}>{value}</div>
      <div className="mt-0.5 text-[11px] text-text-muted">{label}</div>
    </div>
  );
}

export default function RunsPage() {
  const [runs, setRuns] = useState<PollRun[] | null>(null);
  const [triggering, setTriggering] = useState(false);
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);
  const [ats, setAts] = useState<string>("all");
  const [unhealthy, setUnhealthy] = useState<UnhealthySource[] | null>(null);
  const [rerunning, setRerunning] = useState(false);
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);

  const load = useCallback(() => {
    api.pollRuns(10).then((res) => setRuns(res.runs));
  }, []);

  const loadUnhealthy = useCallback(() => {
    api.unhealthySources().then((res) => setUnhealthy(res.unhealthy));
  }, []);

  useEffect(() => {
    load();
    loadUnhealthy();
    // Polling strategy:
    // - pollRuns: only when the latest run is "running" (active ingestion), every 4s — already conditional above.
    // - unhealthySources: cheap but still hits DB; 15s is plenty, and pause when tab is hidden to cut the
    //   thundering herd seen in web logs (multiple tabs * 4s = 10+ req/s of /api/poll/runs + /api/sources/unhealthy + CORS OPTIONS).
    let unhealthyTick = 0;
    timer.current = setInterval(() => {
      if (document.hidden) return;
      setRuns((prev) => {
        const latest = prev && prev[0];
        if (latest && latest.status === "running") {
          api.pollRuns(10).then((res) => setRuns(res.runs));
        }
        return prev;
      });
      unhealthyTick += 1;
      // 4s * ~4 = 16s for unhealthy
      if (unhealthyTick % 4 === 0) {
        api.unhealthySources().then((res) => setUnhealthy(res.unhealthy));
      }
    }, 4000);
    return () => {
      if (timer.current) clearInterval(timer.current);
    };
  }, [load, loadUnhealthy]);

  async function rerunUnhealthy() {
    setRerunning(true);
    setMsg(null);
    try {
      const res = await api.runUnhealthyPoll();
      if (res.run_id) {
        setMsg({ ok: true, text: `Re-poll of ${res.sources.length} unhealthy source(s) started (${res.run_id.slice(0, 8)}…)` });
      } else {
        setMsg({ ok: true, text: "No unhealthy sources to re-run." });
      }
      load();
    } catch (e) {
      setMsg({
        ok: false,
        text: e instanceof Error ? e.message.replace(/^.*?: /, "") : "failed to start re-poll",
      });
    } finally {
      setRerunning(false);
    }
  }

  async function runPoll() {
    setTriggering(true);
    setMsg(null);
    try {
      const res = await api.runPoll(ats === "all" ? undefined : ats);
      setMsg({ ok: true, text: `Poll started (${res.run_id.slice(0, 8)}…) — refreshing…` });
      load();
    } catch (e) {
      setMsg({
        ok: false,
        text: e instanceof Error ? e.message.replace(/^.*?: /, "") : "failed to start poll",
      });
    } finally {
      setTriggering(false);
    }
  }

  const latest = runs && runs[0];
  const isRunning = latest && latest.status === "running";

  return (
    <div className="mx-auto max-w-4xl p-8">
      <h1 className="text-[28px] font-semibold">Poll Runs</h1>
      <p className="mt-1 text-sm text-text-secondary">
        Trigger a poll manually or watch the latest scheduled run. After every poll completes, new
        jobs are matched against your preferences and alerts are sent for new matches.
      </p>

      <div className="mt-8 flex flex-wrap items-center gap-3">
        <select
          value={ats}
          onChange={(e) => setAts(e.target.value)}
          disabled={triggering || !!isRunning}
          className="search-input w-40"
        >
          <option value="all">All sources</option>
          {ATS_ORDER.map((a) => (
            <option key={a} value={a}>
              {atsLabel(a)}
            </option>
          ))}
        </select>
        <button onClick={runPoll} disabled={triggering || !!isRunning} className="btn-primary">
          {triggering ? "Starting…" : isRunning ? "Poll in progress…" : "Run poll now"}
        </button>
        <span className="text-xs text-text-muted">
          {isRunning ? "A run is active — new runs are blocked until it finishes." : ""}
        </span>
      </div>

      {msg && (
        <div className={`card mt-4 p-4 text-sm ${msg.ok ? "text-success" : "text-danger"}`}>
          {msg.text}
        </div>
      )}

      {unhealthy !== null && unhealthy.length > 0 && (
        <div className="card mt-6 border-warning/30 p-5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="text-[15px] font-semibold">
                Unhealthy sources <span className="text-text-muted">({unhealthy.length})</span>
              </h2>
              <p className="mt-1 text-xs text-text-secondary">
                Sources that failed or haven't been checked in time. Re-run them now.
              </p>
            </div>
            <button onClick={rerunUnhealthy} disabled={rerunning || !!isRunning} className="btn-primary">
              {rerunning ? "Starting…" : isRunning ? "Poll in progress…" : "Re-run all unhealthy"}
            </button>
          </div>
          <ul className="mt-4 divide-y divide-border/50">
            {unhealthy.map((s) => (
              <li key={s.id} className="flex flex-wrap items-center justify-between gap-2 py-2 text-sm">
                <span className="flex items-center gap-2">
                  <span
                    className={`h-1.5 w-1.5 rounded-full ${s.status === "stale" ? "bg-warning" : "bg-text-muted"}`}
                  />
                  <span className="text-text">{s.company_name}</span>
                  <span className="text-[11px] text-text-muted">{atsLabel(s.ats_type)}</span>
                  <span className="rounded bg-warning/10 px-1.5 py-0.5 text-[10px] text-warning">
                    {s.status}
                  </span>
                </span>
                <span className="max-w-[55%] truncate text-xs text-text-muted" title={s.reason || ""}>
                  {s.reason || s.status}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="mt-8 space-y-4" data-running={isRunning ? "true" : undefined}>
        {runs === null ? (
          <RadarLoading label="Loading poll runs…" />
        ) : runs.length === 0 ? (
          <div className="card p-10 text-center text-sm text-text-muted">
            No poll runs recorded yet. Trigger a manual poll to get started.
          </div>
        ) : (
          <>
            <RunStatusCard run={runs[0]} />
            {runs.length > 1 && (
              <div>
                <h3 className="mb-2 text-sm font-semibold text-text-secondary">Earlier runs</h3>
                <div className="card divide-y divide-border/50">
                  {runs.slice(1).map((run) => {
                    const meta = STATUS_META[run.status];
                    return (
                      <div
                        key={run.id}
                        className="flex flex-wrap items-center justify-between gap-2 px-5 py-3 text-sm"
                      >
                        <span className="flex items-center gap-2">
                          <span
                            className={`rounded px-1.5 py-0.5 text-[10px] ${meta.className}`}
                          >
                            {meta.label}
                          </span>
                          <span className="text-text-secondary">
                            {run.triggered_by === "manual" ? "Manual" : "Scheduled"}
                            {run.ats_type ? ` · ${atsLabel(run.ats_type)}` : " · All"}
                          </span>
                        </span>
                        <span className="text-xs text-text-muted">
                          {run.started_at ? formatDateTime(run.started_at) : "—"} ·{" "}
                          {run.jobs_new} new · {run.matches_new} match
                          {run.matches_new === 1 ? "" : "es"} · TG {run.telegram_sent} · EM{" "}
                          {run.email_sent}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}