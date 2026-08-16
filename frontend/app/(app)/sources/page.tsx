"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { RadarLoading } from "@/components/radar-loading";
import { api } from "@/lib/api";
import { atsLabel, ATS_ORDER, formatInterval, statusMeta, timeAgo } from "@/lib/format";
import type { Source } from "@/lib/types";

export default function SourcesPage() {
  const [sources, setSources] = useState<Source[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);
  const [company, setCompany] = useState("");
  const [url, setUrl] = useState("");
  const [manual, setManual] = useState(false);
  const [ats, setAts] = useState("");
  const [board, setBoard] = useState("");
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);

  const load = useCallback(async () => {
    const res = await api.sources();
    setSources(res.sources);
  }, []);

  useEffect(() => {
    load().finally(() => setLoading(false));
  }, [load]);

  async function addSource(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setMsg(null);
    try {
      const payload: {
        company_name: string;
        url?: string;
        ats_type?: string;
        board_identifier?: string;
      } = { company_name: company };
      if (url) payload.url = url;
      if (manual) {
        payload.ats_type = ats;
        payload.board_identifier = board;
      }
      const created = await api.createSource(payload);
      setMsg({ ok: true, text: `${created.company_name} added as ${atsLabel(created.ats_type)} (${created.board_identifier})` });
      setCompany("");
      setUrl("");
      setShowAdd(false);
      await load();
    } catch (err) {
      setMsg({ ok: false, text: err instanceof Error ? err.message : "failed to add source" });
    } finally {
      setBusy(false);
    }
  }

  async function toggle(s: Source) {
    await api.updateSource(s.id, { active: !s.active });
    await load();
  }

  async function runNow(s: Source) {
    setBusy(true);
    await api.runSource(s.id);
    setBusy(false);
    await load();
  }

  const stats = useMemo(() => {
    const healthy = sources.filter((s) => s.status === "healthy").length;
    const stale = sources.filter((s) => s.status === "stale").length;
    const never = sources.filter((s) => s.status === "never").length;
    return { healthy, stale, never };
  }, [sources]);

  const byAts = sources.reduce<Record<string, Source[]>>((acc, s) => {
    (acc[s.ats_type] ||= []).push(s);
    return acc;
  }, {});

  const atsOrder = ATS_ORDER;

  return (
    <div className="mx-auto max-w-4xl p-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-[28px] font-semibold">Career Sources</h1>
          <p className="mt-1 text-sm text-text-secondary">{sources.length} sources monitored</p>
        </div>
        <button className="btn-primary" onClick={() => setShowAdd(!showAdd)}>
          {showAdd ? "Cancel" : "+ Add Source"}
        </button>
      </div>

      {!loading && (
        <div className="mt-5 grid grid-cols-3 gap-3">
          <div className="card p-4">
            <p className="text-2xl font-semibold text-success">{stats.healthy}</p>
            <p className="text-xs text-text-muted">Healthy</p>
          </div>
          <div className="card p-4">
            <p className="text-2xl font-semibold text-warning">{stats.stale}</p>
            <p className="text-xs text-text-muted">Unhealthy / stale</p>
          </div>
          <div className="card p-4">
            <p className="text-2xl font-semibold text-text-secondary">{stats.never}</p>
            <p className="text-xs text-text-muted">Never checked</p>
          </div>
        </div>
      )}

      {showAdd && (
        <form onSubmit={addSource} className="card mt-6 space-y-4 p-5">
          <div>
            <label className="text-xs font-medium uppercase tracking-wide text-text-muted">Company</label>
            <input
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              required
              placeholder="e.g. Adobe"
              className="search-input mt-1 w-full"
            />
          </div>
          <div>
            <label className="text-xs font-medium uppercase tracking-wide text-text-muted">
              Career page URL (optional — for Workday / Oracle / auto-detect)
            </label>
            <input
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://…"
              className="search-input mt-1 w-full"
            />
          </div>
          <label className="flex items-center gap-2 text-sm text-text-secondary">
            <input type="checkbox" checked={manual} onChange={(e) => setManual(e.target.checked)} />
            Enter ATS details manually
          </label>
          {manual && (
            <div className="grid grid-cols-2 gap-3">
              <select value={ats} onChange={(e) => setAts(e.target.value)} className="search-input">
                <option value="">ATS type</option>
                {ATS_ORDER.map((a) => (
                  <option key={a} value={a}>
                    {atsLabel(a)}
                  </option>
                ))}
              </select>
              <input
                value={board}
                onChange={(e) => setBoard(e.target.value)}
                placeholder="board identifier / slug"
                className="search-input"
              />
            </div>
          )}
          {msg && (
            <p className={`text-sm ${msg.ok ? "text-success" : "text-danger"}`}>{msg.text}</p>
          )}
          <div className="flex justify-end gap-2">
            <button type="submit" className="btn-primary" disabled={busy}>
              {busy ? "Detecting…" : "Add Source"}
            </button>
          </div>
        </form>
      )}

      <div className="mt-8 space-y-6">
        {loading ? (
          <RadarLoading label="Monitoring sources…" />
        ) : (
          atsOrder
            .filter((ats) => byAts[ats]?.length)
            .map((atsKey) => {
              const group = byAts[atsKey];
              const interval = group[0]?.poll_interval || 3600;
              const healthy = group.filter((s) => s.status === "healthy").length;
              return (
                <section key={atsKey}>
                  <div className="mb-2 flex items-baseline justify-between">
                    <h2 className="text-[15px] font-semibold">{atsLabel(atsKey)}</h2>
                    <span className="text-xs text-text-muted">
                      {healthy}/{group.length} healthy · {formatInterval(interval)}
                    </span>
                  </div>
                  <div className="card overflow-hidden">
                    {group.map((s) => {
                      const meta = statusMeta(s.status);
                      return (
                        <div
                          key={s.id}
                          className="border-b border-border/50 px-4 py-3 last:border-0 hover:bg-elevated"
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <span className={`h-2 w-2 rounded-full ${meta.dot}`} />
                              <span className={`font-medium ${s.active ? "text-text" : "text-text-muted"}`}>
                                {s.company_name}
                              </span>
                              {!s.active && (
                                <span className="rounded bg-elevated px-1.5 py-0.5 text-[11px] text-text-muted">paused</span>
                              )}
                              <span className="rounded bg-elevated px-1.5 py-0.5 text-[11px] text-text-muted">{meta.label}</span>
                            </div>
                            <div className="flex items-center gap-4 text-xs text-text-muted">
                              <span>{s.job_count} jobs</span>
                              <button
                                onClick={() => runNow(s)}
                                disabled={busy}
                                className="text-text-secondary hover:text-primary"
                              >
                                Run now
                              </button>
                              <button
                                onClick={() => toggle(s)}
                                className="text-text-secondary hover:text-warning"
                              >
                                {s.active ? "Pause" : "Resume"}
                              </button>
                            </div>
                          </div>
                          {s.reason && (
                            <p className="mt-1.5 pl-5 text-xs text-warning/90">
                              {s.reason}
                            </p>
                          )}
                          <p className="mt-1.5 pl-5 text-xs text-text-muted">
                            Last checked: {timeAgo(s.last_checked_at)} · Expected every {formatInterval(s.poll_interval)}
                          </p>
                        </div>
                      );
                    })}
                  </div>
                </section>
              );
            })
        )}
      </div>
    </div>
  );
}