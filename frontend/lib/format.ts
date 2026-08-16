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
    custom: "Custom",
  };
  return map[ats] || ats;
}

export const ATS_ORDER = ["workday", "greenhouse", "lever", "ashby", "oracle", "icims", "successfactors", "phenom", "avature", "custom"];

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