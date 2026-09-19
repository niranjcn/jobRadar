const IST_TZ = "Asia/Kolkata";

export function timeAgo(iso: string | null | undefined): string {
  if (!iso) return "—";
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return "—";
  const diff = Date.now() - then;
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 30) return `${days}d ago`;
  return dateIST(iso);
}

export function dateIST(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "—";
  return d.toLocaleDateString("en-IN", { timeZone: IST_TZ });
}

export function timeIST(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "—";
  return d.toLocaleTimeString("en-IN", { timeZone: IST_TZ, hour: "2-digit", minute: "2-digit" });
}

export function initials(name: string): string {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return "?";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

const AVATAR_COLORS = [
  "bg-primary/20 text-primary",
  "bg-accent/20 text-accent",
  "bg-success/20 text-success",
  "bg-warning/20 text-warning",
  "bg-danger/20 text-danger",
];

export function avatarColor(seed: string): string {
  let h = 0;
  for (let i = 0; i < seed.length; i++) h = (h * 31 + seed.charCodeAt(i)) >>> 0;
  return AVATAR_COLORS[h % AVATAR_COLORS.length];
}

export function formatInterval(seconds: number): string {
  if (seconds % 3600 === 0) return `Every ${seconds / 3600}h`;
  if (seconds % 60 === 0) return `Every ${seconds / 60}m`;
  return `Every ${seconds}s`;
}

export function formatDateTime(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "—";
  return d.toLocaleString("en-IN", {
    timeZone: IST_TZ,
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export const INTERVAL_OPTIONS = [900, 1800, 3600, 10800, 21600, 43200, 86400];

export function atsLabel(ats: string): string {
  const map: Record<string, string> = {
    greenhouse: "Greenhouse",
    lever: "Lever",
    ashby: "Ashby",
    workday: "Workday",
    oracle: "Oracle",
    icims: "iCIMS",
    successfactors: "SAP SuccessFactors",
    phenom: "Phenom",
    avature: "Avature",
    emirates: "Emirates",
    google: "Google",
    amazon: "Amazon",
    custom: "Custom",
    remotive: "Remotive",
    weworkremotely: "We Work Remotely",
  };
  return map[ats] || ats;
}

export const ATS_ORDER = ["workday", "greenhouse", "lever", "ashby", "oracle", "icims", "successfactors", "phenom", "avature", "emirates", "google", "amazon", "remotive", "weworkremotely", "custom"];

export function formatDuration(ms: number | null | undefined): string {
  if (ms == null || Number.isNaN(ms)) return "—";
  if (ms < 1000) return `${ms}ms`;
  const s = ms / 1000;
  if (s < 60) return `${s.toFixed(1)}s`;
  const m = Math.floor(s / 60);
  const rem = (s % 60).toFixed(0);
  return `${m}m ${rem}s`;
}

export function formatRunDuration(startedAt: string | null, finishedAt: string | null): string {
  if (!startedAt || !finishedAt) return "—";
  const s = new Date(startedAt).getTime();
  const f = new Date(finishedAt).getTime();
  if (Number.isNaN(s) || Number.isNaN(f) || f < s) return "—";
  return formatDuration(f - s);
}

/** ISO timestamp (UTC) for the start of the current day (00:00 local). */
export function startOfTodayUTC(): string {
  const now = new Date();
  const d = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  return d.toISOString();
}

export function statusMeta(status: string): { label: string; dot: string } {
  switch (status) {
    case "healthy":
      return { label: "Healthy", dot: "bg-success" };
    case "stale":
      return { label: "Stale", dot: "bg-warning" };
    default:
      return { label: "Never checked", dot: "bg-text-muted" };
  }
}

/** Countdown for coupon expiry: '11h 58m left', '42m left', or 'expired'. */
export function timeLeft(iso: string | null | undefined, now = Date.now()): string {
  if (!iso) return "—";
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return "—";
  const diff = then - now;
  if (diff <= 0) return "expired";
  const minutes = Math.floor(diff / 60000);
  if (minutes < 60) return `${minutes}m left`;
  const hours = Math.floor(minutes / 60);
  return `${hours}h ${minutes % 60}m left`;
}

let regionNames: Intl.DisplayNames | null = null;

/** ISO code → full country name ("IN" → "India"). Full-name values stored
 *  in the DB ("Australia") are title-cased; anything else falls back as-is. */
export function countryName(code: string): string {
  const c = (code || "").trim();
  if (!c) return "";
  if (/^[A-Za-z]{2,3}$/.test(c)) {
    const up = c.toUpperCase();
    try {
      if (!regionNames) regionNames = new Intl.DisplayNames(["en"], { type: "region" });
      return regionNames.of(up) || up;
    } catch {
      return up;
    }
  }
  return c.toLowerCase().replace(/(^|[\s-])(\w)/g, (_, p1: string, p2: string) => p1 + p2.toUpperCase());
}

/** Compact number formatter: 12400 → "12.4K". */
export function fmtCompact(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1).replace(/\.0$/, "")}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1).replace(/\.0$/, "")}K`;
  return String(n);
}

/** Week-over-week % change of two equal-length halves. Null when flat/empty. */
export function pctChange(recent: number[], prior: number[]): number | null {
  const a = recent.reduce((s, v) => s + v, 0);
  const b = prior.reduce((s, v) => s + v, 0);
  if (b <= 0) return a > 0 ? 100 : null;
  const pct = Math.round(((a - b) / b) * 100);
  return pct === 0 ? null : pct;
}

/** "2026-09-12" → "Sep 12". */
export function shortDate(iso: string): string {
  const d = new Date(iso + "T00:00:00");
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

export function errText(err: unknown): string {
  if (err instanceof Error) {
    return err.message.replace(/^\d+ \w+: /, "").slice(0, 200);
  }
  return String(err);
}