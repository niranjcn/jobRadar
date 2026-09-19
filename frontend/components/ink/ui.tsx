"use client";

import Link from "next/link";
import styles from "./ink.module.css";
import { timeAgo } from "@/lib/format";
import { CompanyLogo } from "@/components/company-logo";
import type { Job } from "@/lib/types";

/* ---------------- page chrome ---------------- */

export function PageHeader({
  eyebrow,
  title,
  desc,
  action,
}: {
  eyebrow: string;
  title: string;
  desc?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className={styles.pageHead}>
      <p className={styles.eyebrow}>{eyebrow}</p>
      <h1 className={styles.pageTitle}>{title}</h1>
      {desc && <p className={styles.pageDesc}>{desc}</p>}
      {action && <div className={styles.pageAction}>{action}</div>}
    </div>
  );
}

export function Stat({ label, value, sub, tone }: { label: string; value: React.ReactNode; sub?: string; tone?: "ok" | "warn" | "bad" | "info" | "muted" }) {
  const toneCls =
    tone === "ok" ? styles.toneOk : tone === "warn" ? styles.toneWarn : tone === "bad" ? styles.toneBad : tone === "info" ? styles.toneInfo : "";
  return (
    <div className={styles.statMini}>
      <div className={`${styles.statMiniValue} ${toneCls}`}>{value}</div>
      <div className={styles.statMiniLabel}>{label}</div>
      {sub && <div className={styles.statMiniLabel}>{sub}</div>}
    </div>
  );
}

/* ---------------- pills / badges ---------------- */

export function StatusPill({ tone, children }: { tone: "ok" | "warn" | "bad" | "info" | "muted"; children: React.ReactNode }) {
  return <span className={`${styles.statusTag} ${styles[tone]}`}>{children}</span>;
}

export function Avatar({ name, size = 36 }: { name: string; size?: number }) {
  return (
    <span className={styles.avatarLg} style={{ width: size, height: size, fontSize: Math.round(size * 0.38) }} aria-hidden>
      {(name.trim()[0] || "?").toUpperCase()}
    </span>
  );
}

export function ScoreRing({ score, size = 56 }: { score: number | null; size?: number }) {
  if (score === null || score === undefined) {
    return (
      <span className={styles.scoreRing} style={{ width: size, height: size }}>
        <span className={styles.scoreNum} style={{ color: "var(--ink-muted)" }}>
          —
        </span>
      </span>
    );
  }
  const color = score >= 80 ? "#19e6a7" : score >= 60 ? "#f5b14c" : "#6f8587";
  const r = 24;
  const c = 2 * Math.PI * r;
  return (
    <span>
      <span className={styles.scoreRing} style={{ width: size, height: size }}>
        <svg width={size} height={size} viewBox="0 0 56 56" aria-hidden>
          <circle cx="28" cy="28" r={r} fill="none" stroke="rgba(255,255,255,0.09)" strokeWidth="5" />
          <circle
            cx="28"
            cy="28"
            r={r}
            fill="none"
            stroke={color}
            strokeWidth="5"
            strokeLinecap="round"
            strokeDasharray={`${(Math.min(100, Math.max(0, score)) / 100) * c} ${c}`}
            transform="rotate(-90 28 28)"
          />
        </svg>
        <span className={styles.scoreNum} style={{ color }}>
          {score}
        </span>
      </span>
      <span className={styles.scoreCap} style={{ color }}>
        {score >= 80 ? "Excellent" : score >= 60 ? "Good" : "Fair"}
      </span>
    </span>
  );
}

/* ---------------- controls ---------------- */

export function Toggle({ checked, onChange, label }: { checked: boolean; onChange: (v: boolean) => void; label?: string }) {
  return (
    <label style={{ display: "inline-flex", alignItems: "center", gap: 8, cursor: "pointer", fontSize: 13 }}>
      <span className={styles.switch}>
        <input type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)} />
        <span className={styles.switchTrack} />
      </span>
      {label && <span style={{ color: "var(--ink-text2)" }}>{label}</span>}
    </label>
  );
}

export function Pager({
  page,
  pageCount,
  onPrev,
  onNext,
  disabled,
  label,
}: {
  page: number;
  pageCount: number;
  onPrev: () => void;
  onNext: () => void;
  disabled?: boolean;
  label?: string;
}) {
  return (
    <div className={styles.pager}>
      <span>
        {label ?? `Page ${page + 1} of ${pageCount}`}
      </span>
      <div className={styles.pagerBtns}>
        <button type="button" className={styles.btnLine} disabled={page === 0 || disabled} onClick={onPrev}>
          Previous
        </button>
        <button type="button" className={styles.btnLine} disabled={page >= pageCount - 1 || disabled} onClick={onNext}>
          Next
        </button>
      </div>
    </div>
  );
}

/* ---------------- states ---------------- */

export function EmptyState({ title, desc, action }: { title: string; desc?: string; action?: React.ReactNode }) {
  return (
    <div className={styles.stateWrap}>
      <p className={styles.stateTitle}>{title}</p>
      {desc && <p className={styles.stateDesc}>{desc}</p>}
      {action && <div className={styles.stateAction}>{action}</div>}
    </div>
  );
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className={styles.stateWrap}>
      <p className={styles.stateTitle}>Something went wrong.</p>
      <p className={styles.stateDesc}>{message || "We couldn't load this information."}</p>
      {onRetry && (
        <div className={styles.stateAction}>
          <button type="button" className={styles.btnMint} onClick={onRetry}>
            Try Again
          </button>
        </div>
      )}
    </div>
  );
}

export function LoadingState({ label, rows = 5 }: { label?: string; rows?: number }) {
  return (
    <div className={styles.panel} style={{ padding: 20 }} aria-label={label || "Loading"}>
      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className={styles.skel} style={{ height: 54 }} />
        ))}
      </div>
      {label && <p className={styles.emptyNote}>{label}</p>}
    </div>
  );
}

/* ---------------- tables ---------------- */

export function DataTable({ head, children }: { head: React.ReactNode[]; children: React.ReactNode }) {
  return (
    <div className={styles.tableWrap}>
      <table className={styles.inkTable}>
        <thead>
          <tr>
            {head.map((h, i) => (
              <th key={i}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>{children}</tbody>
      </table>
    </div>
  );
}

/* ---------------- job feed row ---------------- */

export function BookmarkBtn({ saved, onToggle }: { saved: boolean; onToggle: () => void }) {
  return (
    <button
      type="button"
      aria-label={saved ? "Unsave job" : "Save job"}
      onClick={onToggle}
      className={`${styles.fSave} ${saved ? styles.saved : ""}`}
    >
      <svg viewBox="0 0 24 24" fill={saved ? "currentColor" : "none"} stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" aria-hidden>
        <path d="M6.5 3.5h11a1 1 0 0 1 1 1V21l-6.5-4-6.5 4V4.5a1 1 0 0 1 1-1z" />
      </svg>
    </button>
  );
}

export function OpportunityRow({
  job,
  saved,
  onToggleSave,
  isNew,
  trailing,
}: {
  job: Job;
  saved: boolean;
  onToggleSave: () => void;
  isNew?: boolean;
  trailing?: React.ReactNode;
}) {
  return (
    <div className={styles.feedRow}>
      <div className={styles.fMain}>
        <CompanyLogo name={job.company} domain={job.domain} size="md" />
        <div style={{ minWidth: 0 }}>
          <Link href={`/jobs/${job.id}`} className={styles.fTitle} style={{ display: "block", textDecoration: "none" }}>
            {job.title}
            {isNew && <span className={styles.newBadge}>NEW</span>}
          </Link>
          <div className={styles.fCompany}>{job.company}</div>
          <div className={styles.fSub}>
            {job.location || "Remote / unspecified"} · {timeAgo(job.first_seen_at)}
          </div>
        </div>
      </div>
      <span className={styles.fLoc}>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden>
          <path d="M12 21s-6.5-5.4-6.5-10.5a6.5 6.5 0 0 1 13 0C18.5 15.6 12 21 12 21z" />
          <circle cx="12" cy="10.5" r="2.3" />
        </svg>
        <span style={{ overflow: "hidden", textOverflow: "ellipsis" }}>{job.location || "Remote"}</span>
      </span>
      <span className={styles.fSrcWrap}>
        <span className={styles.srcPill}>{job.countries[0] || "—"}</span>
      </span>
      <span className={styles.fPosted}>{timeAgo(job.first_seen_at)}</span>
      <span style={{ display: "inline-flex", alignItems: "center", gap: 2 }}>
        {trailing}
        <BookmarkBtn saved={saved} onToggle={onToggleSave} />
      </span>
    </div>
  );
}
