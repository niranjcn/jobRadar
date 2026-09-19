"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import styles from "./ink.module.css";
import { Spark } from "./charts";
import { I } from "./icons";
import { BookmarkBtn, ScoreRing } from "./ui";
import { CompanyLogo } from "@/components/company-logo";
import { api } from "@/lib/api";
import { fmtCompact, pctChange, shortDate, timeAgo } from "@/lib/format";
import { loadSaved, toggleSaved } from "@/lib/job-store";
import type { Company, DailyStats, Job, Stats } from "@/lib/types";

/* ---------------- data ---------------- */

export interface OverviewData {
  stats: Stats | null;
  daily: DailyStats | null;
  feed: Job[];
  companies: Company[];
  sourcesActive: number;
  sourcesTotal: number;
  lastRunAt: string | null;
  lastRunOk: boolean;
  notifSent: number;
  dbMs: number | null;
  loading: boolean;
  error: string | null;
}

export function useOverviewData(feedLimit = 30): OverviewData & { saved: string[]; toggleSave: (id: string) => void } {
  const [stats, setStats] = useState<Stats | null>(null);
  const [daily, setDaily] = useState<DailyStats | null>(null);
  const [feed, setFeed] = useState<Job[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [sourcesActive, setSourcesActive] = useState(0);
  const [sourcesTotal, setSourcesTotal] = useState(0);
  const [lastRunAt, setLastRunAt] = useState<string | null>(null);
  const [lastRunOk, setLastRunOk] = useState(true);
  const [notifSent, setNotifSent] = useState(0);
  const [dbMs, setDbMs] = useState<number | null>(null);
  const [saved, setSaved] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setSaved(loadSaved());
    const t0 = performance.now();
    Promise.all([
      api.stats(),
      api.statsDaily(30),
      api.jobs({ limit: feedLimit }),
      api.companies(),
      api.sources(),
      api.pollRuns(1),
      api.notifications(),
    ])
      .then(([s, d, j, c, src, runs, n]) => {
        setStats(s);
        setDaily(d);
        setFeed(j.jobs);
        setCompanies([...c.companies].sort((a, b) => b.job_count - a.job_count));
        setSourcesActive(src.sources.filter((x) => x.active).length);
        setSourcesTotal(src.sources.length);
        if (runs.runs.length) {
          setLastRunAt(runs.runs[0].finished_at || runs.runs[0].started_at);
          setLastRunOk(runs.runs[0].status === "completed");
        }
        setNotifSent(n.notifications.length);
        setDbMs(Math.round(performance.now() - t0));
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [feedLimit]);

  return {
    stats,
    daily,
    feed,
    companies,
    sourcesActive,
    sourcesTotal,
    lastRunAt,
    lastRunOk,
    notifSent,
    dbMs,
    loading,
    error,
    saved,
    toggleSave: (id: string) => setSaved((cur) => toggleSaved(cur, id)),
  };
}

function Trend({ value }: { value: number | null }) {
  if (value === null) return <span className={`${styles.mTrend} ${styles.flat}`}>—</span>;
  const cls = value > 0 ? styles.up : value < 0 ? styles.down : styles.flat;
  const sign = value > 0 ? "↑ +" : value < 0 ? "↓ " : "";
  return (
    <span className={`${styles.mTrend} ${cls}`}>
      {sign}
      {Math.abs(value)}%
    </span>
  );
}

/* ---------------- greeting ---------------- */

export function Greeting({ kick, name, sub }: { kick: string; name: string; sub: string }) {
  return (
    <section className={styles.hero}>
      <div>
        <p className={styles.greetKick}>{kick}</p>
        <h1 className={styles.greetBig}>
          <span>{name}</span>
        </h1>
        <p className={styles.greetSub}>{sub}</p>
      </div>
    </section>
  );
}

export function timeGreeting(): string {
  const hour = new Date().getHours();
  return hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening";
}

/* ---------------- metrics ---------------- */

export function MetricsRow({ stats, daily, sourcesActive }: { stats: Stats | null; daily: DailyStats | null; sourcesActive: number }) {
  const last14 = daily?.days.slice(-14) ?? [];
  const prior7 = last14.slice(0, 7);
  const last7 = last14.slice(-7);
  const jobsTrend = pctChange(last7.map((d) => d.jobs), prior7.map((d) => d.jobs));
  const matchTrend = pctChange(last7.map((d) => d.matches), prior7.map((d) => d.matches));
  return (
    <section className={styles.metrics}>
      <div className={styles.metric}>
        <span className={styles.mIcon}>
          <I.briefcase />
        </span>
        <div className={styles.mBody}>
          <span className={styles.mLabel}>New jobs (7d)</span>
          <div className={styles.mValue}>{(stats?.jobs_new_7d ?? 0).toLocaleString()}</div>
          <div className={styles.mFoot}>
            <Trend value={jobsTrend} />
            <Spark values={last7.map((d) => d.jobs)} />
          </div>
        </div>
      </div>
      <div className={styles.metric}>
        <span className={`${styles.mIcon} ${styles.blue}`}>
          <I.target />
        </span>
        <div className={styles.mBody}>
          <span className={styles.mLabel}>Matches</span>
          <div className={styles.mValue}>{(stats?.matches ?? 0).toLocaleString()}</div>
          <div className={styles.mFoot}>
            <Trend value={matchTrend} />
            <Spark values={last7.map((d) => d.matches)} blue />
          </div>
        </div>
      </div>
      <div className={styles.metric}>
        <span className={`${styles.mIcon} ${styles.blue}`}>
          <I.building />
        </span>
        <div className={styles.mBody}>
          <span className={styles.mLabel}>Companies monitored</span>
          <div className={styles.mValue}>{(stats?.companies ?? 0).toLocaleString()}</div>
          <div className={styles.mFoot}>
            <span className={`${styles.mTrend} ${styles.flat}`}>{sourcesActive} active</span>
          </div>
        </div>
      </div>
      <div className={styles.metric}>
        <span className={styles.mIcon}>
          <I.trend />
        </span>
        <div className={styles.mBody}>
          <span className={styles.mLabel}>Average match</span>
          <div className={styles.mValue}>{stats?.avg_match_score ?? 0}%</div>
          <div className={styles.mFoot}>
            <span className={`${styles.mTrend} ${styles.flat}`}>
              across {(stats?.matches ?? 0).toLocaleString()} matches
            </span>
          </div>
        </div>
      </div>
    </section>
  );
}

/* ---------------- opportunity feed ---------------- */

type FeedPill = "latest" | "top" | "remote" | "all";
type FeedRange = "" | "24h" | "7d";

export function OpportunityFeed({
  jobs,
  total,
  saved,
  onToggleSave,
}: {
  jobs: Job[];
  total: number;
  saved: string[];
  onToggleSave: (id: string) => void;
}) {
  const [pill, setPill] = useState<FeedPill>("latest");
  const [range, setRange] = useState<FeedRange>("24h");

  const visible = useMemo(() => {
    let list = jobs;
    if (range === "24h" || range === "7d") {
      const cutoff = Date.now() - (range === "24h" ? 24 : 7 * 24) * 3600 * 1000;
      list = list.filter((j) => j.first_seen_at && new Date(j.first_seen_at).getTime() >= cutoff);
    }
    if (pill === "remote") list = list.filter((j) => j.is_remote);
    if (pill === "top") list = [...list].sort((a, b) => (b.match_score ?? 0) - (a.match_score ?? 0));
    return list.slice(0, 8);
  }, [jobs, pill, range]);

  return (
    <section className={styles.panel}>
      <div className={styles.panelHead}>
        <span className={styles.liveDot} />
        <span className={styles.panelTitle}>New opportunities</span>
        <span className={styles.panelTotal}>{total.toLocaleString()} total</span>
        <Link href="/jobs" className={styles.viewAll}>
          View all →
        </Link>
      </div>
      <div className={styles.pills}>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          {(
            [
              ["latest", "Latest"],
              ["top", "Top Matches"],
              ["remote", "Remote"],
              ["all", "All"],
            ] as [FeedPill, string][]
          ).map(([key, label]) => (
            <button
              key={key}
              type="button"
              className={`${styles.pill} ${pill === key ? styles.pillActive : ""}`}
              onClick={() => setPill(key)}
            >
              {label}
            </button>
          ))}
        </div>
        <div style={{ display: "flex", gap: 8, marginLeft: "auto", flexWrap: "wrap" }}>
          {(["24h", "7d"] as FeedRange[]).map((key) => (
            <button
              key={key}
              type="button"
              className={`${styles.pill} ${range === key ? styles.pillActive : ""}`}
              onClick={() => setRange(range === key ? "" : key)}
            >
              {key === "24h" ? "Last 24h" : "Last 7 days"}
            </button>
          ))}
        </div>
      </div>
      <div className={styles.colHead}>
        <span>Job / Company</span>
        <span>Location</span>
        <span>Source</span>
        <span>Posted</span>
        <span />
      </div>
      <div>
        {visible.map((job) => (
          <div key={job.id} className={styles.feedRow}>
            <div className={styles.fMain}>
              <CompanyLogo name={job.company} domain={job.domain} size="md" />
              <div style={{ minWidth: 0 }}>
                <Link href={`/jobs/${job.id}`} className={styles.fTitle} style={{ display: "block", textDecoration: "none" }}>
                  {job.title}
                </Link>
                <div className={styles.fCompany}>{job.company}</div>
                <div className={styles.fSub}>
                  {job.location || "Remote / unspecified"} · {timeAgo(job.first_seen_at)}
                </div>
              </div>
            </div>
            <span className={styles.fLoc}>
              <I.pin />
              <span style={{ overflow: "hidden", textOverflow: "ellipsis" }}>{job.location || "Remote"}</span>
            </span>
            <span className={styles.fSrcWrap}>
              <span className={styles.srcPill}>{job.countries[0] || "—"}</span>
            </span>
            <span className={styles.fPosted}>{timeAgo(job.first_seen_at)}</span>
            <BookmarkBtn saved={saved.includes(job.id)} onToggle={() => onToggleSave(job.id)} />
          </div>
        ))}
        {visible.length === 0 && <p className={styles.emptyNote}>No jobs match this view yet.</p>}
      </div>
    </section>
  );
}

/* ---------------- analytics rail ---------------- */

export function AnalyticsRail({
  daily,
  companies,
  sourcesActive,
  sourcesTotal,
  lastRunAt,
  lastRunOk,
  notifSent,
  dbMs,
}: {
  daily: DailyStats | null;
  companies: Company[];
  sourcesActive: number;
  sourcesTotal: number;
  lastRunAt: string | null;
  lastRunOk: boolean;
  notifSent: number;
  dbMs: number | null;
}) {
  const [trendDays, setTrendDays] = useState(7);
  const chartDays = (daily?.days ?? []).slice(-trendDays);
  const chartMax = Math.max(1, ...chartDays.map((d) => d.jobs));

  function ago(iso: string | null): string {
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

  // Build line path for trend – purple line with soft fill
  const trendMax = Math.max(1, ...chartDays.map((d) => d.jobs));
  const trendMin = Math.min(...chartDays.map((d) => d.jobs), 0);
  const w = 320;
  const h = 120;
  const pad = 12;
  const stepX = chartDays.length > 1 ? (w - pad * 2) / (chartDays.length - 1) : 0;
  const points = chartDays.map((d, i) => {
    const x = pad + i * stepX;
    const y = h - pad - ((d.jobs - trendMin) / (trendMax - trendMin || 1)) * (h - pad * 2);
    return { x, y, d };
  });
  const linePath = points.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`).join(" ");
  const fillPath = points.length
    ? `${linePath} L ${points[points.length - 1].x} ${h - pad} L ${points[0].x} ${h - pad} Z`
    : "";
  const lastPoint = points.length ? points[points.length - 1] : null;
  const maxPoint = points.reduce((acc, p) => (p.d.jobs > (acc?.d.jobs ?? -1) ? p : acc), null as any);

  return (
    <div className={styles.rail}>
      <section className={styles.railCard}>
        <div className={styles.railHead}>
          <I.calendar />
          <span className={styles.railTitle}>Jobs Trend</span>
          <div style={{ marginLeft: "auto", display: "flex", gap: 6 }}>
            {[7, 14, 30].map((n) => (
              <button
                key={n}
                type="button"
                className={`${styles.pill} ${trendDays === n ? styles.pillActive : ""}`}
                style={{ fontSize: 11, padding: "5px 10px" }}
                onClick={() => setTrendDays(n)}
              >
                Last {n} days
              </button>
            ))}
          </div>
        </div>
        <div style={{ position: "relative", height: 148, paddingTop: 8 }}>
          <svg viewBox={`0 0 ${w} ${h}`} width="100%" height="148" preserveAspectRatio="none" style={{ display: "block" }}>
            {/* grid */}
            {[0, 1, 2, 3].map((i) => (
              <line
                key={i}
                x1={pad}
                x2={w - pad}
                y1={pad + (i * (h - pad * 2)) / 3}
                y2={pad + (i * (h - pad * 2)) / 3}
                stroke="rgba(255,255,255,0.06)"
                strokeWidth={1}
              />
            ))}
            {/* fill */}
            <path d={fillPath} fill="url(#trend-grad)" opacity={0.22} />
            <defs>
              <linearGradient id="trend-grad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#a78bfa" stopOpacity={0.9} />
                <stop offset="100%" stopColor="#8b5cf6" stopOpacity={0} />
              </linearGradient>
            </defs>
            {/* line */}
            <path d={linePath} fill="none" stroke="#a78bfa" strokeWidth={2} strokeLinejoin="round" strokeLinecap="round" />
            {/* points */}
            {points.map((p) => (
              <circle key={p.d.date} cx={p.x} cy={p.y} r={p === maxPoint || p === lastPoint ? 3.5 : 2} fill={p === maxPoint ? "#a78bfa" : "#c4b5fd"} stroke="#1c1c22" strokeWidth={1.2} />
            ))}
            {/* max label */}
            {maxPoint && (
              <g>
                <rect x={maxPoint.x - 22} y={maxPoint.y - 28} width={44} height={18} rx={6} fill="#a78bfa" />
                <text x={maxPoint.x} y={maxPoint.y - 16} textAnchor="middle" fontSize={9} fontWeight={700} fill="#fff">
                  {fmtCompact(maxPoint.d.jobs)}
                </text>
              </g>
            )}
            {/* dashed vertical for last point */}
            {lastPoint && <line x1={lastPoint.x} x2={lastPoint.x} y1={lastPoint.y} y2={h - pad} stroke="#a78bfa" strokeWidth={1} strokeDasharray="4 4" opacity={0.35} />}
          </svg>
          <div style={{ display: "flex", justifyContent: "space-between", padding: `6px ${pad}px 0`, fontSize: 9, color: "#71717b" }}>
            {chartDays.map((d) => (
              <span key={d.date} style={{ fontSize: 9 }}>
                {shortDate(d.date)}
              </span>
            ))}
          </div>
        </div>
      </section>

      <section className={styles.railCard}>
        <div className={styles.railHead}>
          <I.building />
          <span className={styles.railTitle}>Top Companies</span>
          <Link href="/companies" className={styles.viewAll} style={{ padding: "5px 12px", fontSize: 12 }}>
            View all
          </Link>
        </div>
        {companies.slice(0, 10).map((c) => (
          <Link key={c.company_name} href={`/jobs?company=${encodeURIComponent(c.company_name)}`} className={styles.coRow}>
            <CompanyLogo name={c.company_name} domain={c.domain} size="sm" />
            <span className={styles.coName}>{c.company_name}</span>
            <span className={styles.coCount}>{c.job_count.toLocaleString()}</span>
          </Link>
        ))}
      </section>
    </div>
  );
}

export function SystemStatusWide({
  sourcesActive,
  sourcesTotal,
  lastRunAt,
  lastRunOk,
  notifSent,
  dbMs,
}: {
  sourcesActive: number;
  sourcesTotal: number;
  lastRunAt: string | null;
  lastRunOk: boolean;
  notifSent: number;
  dbMs: number | null;
}) {
  function ago(iso: string | null): string {
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
  return (
    <section className={styles.systemWide}>
      <div className={styles.systemWideHead}>
        <span className={styles.systemWideTitle}>System Status</span>
        <span className={styles.statusPill} style={{ marginLeft: 12 }}>
          <span className={styles.okDot} /> All systems operational
        </span>
      </div>
      <div className={styles.systemGrid}>
        <div className={styles.systemCard}>
          <span className={styles.systemIcon}>
            <I.db />
          </span>
          <div>
            <div className={styles.systemName}>Job Scrapers</div>
            <div className={styles.systemVal}>
              <span className={styles.okDot} /> Running
            </div>
            <div className={styles.systemMeta}>{sourcesTotal} sources</div>
          </div>
        </div>
        <div className={styles.systemCard}>
          <span className={styles.systemIcon}>
            <I.db />
          </span>
          <div>
            <div className={styles.systemName}>Database</div>
            <div className={styles.systemVal}>
              <span className={styles.okDot} /> Healthy
            </div>
            <div className={styles.systemMeta}>{dbMs === null ? "…" : `${dbMs}ms`}</div>
          </div>
        </div>
        <div className={styles.systemCard}>
          <span className={styles.systemIcon}>
            <I.gear />
          </span>
          <div>
            <div className={styles.systemName}>Match Engine</div>
            <div className={styles.systemVal}>
              <span className={styles.okDot} /> {lastRunOk ? "Running" : "Attention"}
            </div>
            <div className={styles.systemMeta}>{lastRunAt ? `Last run ${ago(lastRunAt)}` : "—"}</div>
          </div>
        </div>
        <div className={styles.systemCard}>
          <span className={styles.systemIcon}>
            <I.bell />
          </span>
          <div>
            <div className={styles.systemName}>Notifications</div>
            <div className={styles.systemVal}>
              <span className={styles.okDot} /> Healthy
            </div>
            <div className={styles.systemMeta}>{notifSent} sent</div>
          </div>
        </div>
      </div>
      <div className={styles.systemQuote}>
        <span className={styles.systemQuoteMark} aria-hidden>
          &ldquo;
        </span>
        <p>Keep going.</p>
        <p>Better opportunities are out there.</p>
      </div>
    </section>
  );
}

export { ScoreRing };
