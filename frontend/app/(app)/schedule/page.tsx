"use client";

import { useCallback, useEffect, useState } from "react";
import { RadarLoading } from "@/components/radar-loading";
import { api } from "@/lib/api";
import { atsLabel, formatDateTime, formatInterval, INTERVAL_OPTIONS, timeAgo } from "@/lib/format";
import type { ScheduleEntry } from "@/lib/types";

const FREQ_LABEL: Record<number, string> = {
  900: "15 min",
  1800: "30 min",
  3600: "1 hour",
  10800: "3 hours",
  21600: "6 hours",
  43200: "12 hours",
  86400: "1 day",
};

export default function SchedulePage() {
  const [entries, setEntries] = useState<ScheduleEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);

  const load = useCallback(() => {
    api.schedule().then((res) => setEntries(res.schedule));
  }, []);

  useEffect(() => {
    load();
    setLoading(false);
  }, [load]);

  async function setInterval(entry: ScheduleEntry, seconds: number) {
    setBusy(true);
    setMsg(null);
    try {
      const res = await api.updateSchedule(entry.ats_type, seconds);
      setMsg({
        ok: true,
        text: `${atsLabel(entry.ats_type)} now polls ${formatInterval(seconds)}${
          res.rescheduled ? " (scheduler updated)" : " (applies after restart)"
        }`,
      });
      load();
    } catch (e) {
      setMsg({ ok: false, text: e instanceof Error ? e.message : "failed to update schedule" });
    } finally {
      setBusy(false);
    }
  }

  async function reset(entry: ScheduleEntry) {
    setBusy(true);
    setMsg(null);
    try {
      await api.resetSchedule(entry.ats_type);
      setMsg({ ok: true, text: `${atsLabel(entry.ats_type)} reset to env default` });
      load();
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-4xl p-8">
      <h1 className="text-[28px] font-semibold">Schedule Management</h1>
      <p className="mt-1 text-sm text-text-secondary">
        When each source type was last checked, how often it runs, and when the next check happens.
      </p>

      {msg && (
        <div className={`card mt-6 p-4 text-sm ${msg.ok ? "text-success" : "text-danger"}`}>{msg.text}</div>
      )}

      <div className="mt-8">
        {loading ? (
          <RadarLoading label="Loading schedule…" />
        ) : entries.length === 0 ? (
          <div className="card p-10 text-center text-sm text-text-muted">No schedule configured.</div>
        ) : (
          <div className="card divide-y divide-border/50">
            {entries.map((entry) => (
              <div key={entry.ats_type} className="flex flex-wrap items-center justify-between gap-4 px-5 py-4">
                <div className="min-w-40">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-text">{atsLabel(entry.ats_type)}</span>
                    {entry.source_count > 0 && (
                      <span className="rounded bg-elevated px-1.5 py-0.5 text-[11px] text-text-muted">
                        {entry.source_count} source{entry.source_count === 1 ? "" : "s"}
                      </span>
                    )}
                    <span className="rounded bg-elevated px-1.5 py-0.5 font-mono text-[11px] text-text-muted">
                      ×{entry.concurrency ?? 8}
                    </span>
                    {entry.overridden && (
                      <span className="rounded bg-accent/15 px-1.5 py-0.5 text-[11px] text-accent">custom</span>
                    )}
                  </div>
                  <p className="mt-1 text-xs text-text-muted">
                    Last check: <span className="text-text-secondary">{timeAgo(entry.last_checked_at)}</span> ·{" "}
                    Next: <span className="text-text-secondary">{formatDateTime(entry.next_run_at)}</span>
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <div className="mr-1 text-xs uppercase tracking-wide text-text-muted">Every</div>
                  <select
                    value={entry.interval_seconds}
                    onChange={(e) => setInterval(entry, Number(e.target.value))}
                    disabled={busy}
                    className="search-input w-32"
                  >
                    {INTERVAL_OPTIONS.map((s) => (
                      <option key={s} value={s}>
                        {FREQ_LABEL[s]}
                      </option>
                    ))}
                  </select>
                  {entry.overridden && (
                    <button onClick={() => reset(entry)} disabled={busy} className="btn-ghost text-xs">
                      Reset
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <p className="mt-6 text-xs text-text-muted">
        All times are in India Standard Time (IST). Defaults come from{" "}
        <code>POLL_INTERVAL_&lt;ATS&gt;_SECONDS</code> in the backend .env. Choosing a value
        here overrides it immediately; Reset returns to the env default. Integrity sweep runs every 12 hours.
      </p>
    </div>
  );
}