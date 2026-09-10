import { avatarColor, initials, timeAgo } from "@/lib/format";
import type { Job } from "@/lib/types";
import Link from "next/link";
import { CompanyLogo } from "@/components/company-logo";

export function Avatar({ name, size = "md" }: { name: string; size?: "md" | "lg" }) {
  const cls = size === "lg" ? "h-12 w-12 text-sm" : "h-9 w-9 text-xs";
  return (
    <div
      className={`flex ${cls} shrink-0 items-center justify-center rounded-[10px] border-2 border-border font-fraunces font-extrabold shadow-offset-sm ${avatarColor(name)}`}
    >
      {initials(name)}
    </div>
  );
}

export function MatchBadge({ score }: { score: number | null }) {
  if (score === null || score === undefined) return null;
  const tone = score >= 90 ? "text-success" : score >= 75 ? "text-warning" : "text-text-secondary";
  return (
    <span className={`font-mono text-xs font-semibold ${tone}`}>{score}% MATCH</span>
  );
}

export function CountryBadges({ countries, isRemote }: { countries: string[]; isRemote: boolean }) {
  const list = countries.filter(Boolean);
  if (!list.length && !isRemote) return null;
  return (
    <>
      {list.map((c) => (
        <span
          key={c}
          className="rounded-[10px] border border-[var(--glass-border)] bg-elevated px-2 py-0.5 font-mono text-xs font-medium text-accent"
        >
          {c}
        </span>
      ))}
      {isRemote && (
        <span className="rounded-[10px] border border-[var(--glass-border)] bg-elevated px-2 py-0.5 font-mono text-xs font-medium text-text-secondary">
          Remote
        </span>
      )}
    </>
  );
}

export function JobCard({ job, index = 0, hrefPrefix = "/jobs" }: { job: Job; index?: number; hrefPrefix?: string }) {
  return (
    <Link
      href={`${hrefPrefix}/${job.id}`}
      className="card group block p-4 animate-rise hover:translate-y-[-2px] hover:shadow-offset-hover"
      style={{ animationDelay: `${150 + index * 60}ms`, animationFillMode: "both" }}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <CompanyLogo name={job.company} domain={job.domain} />
          <div>
            <h3 className="font-fraunces text-[15px] font-bold leading-snug tracking-[-0.01em] text-text group-hover:text-primary">
              {job.title}
            </h3>
            <p className="text-sm font-medium text-text-secondary">{job.company}</p>
          </div>
        </div>
        <MatchBadge score={job.match_score} />
      </div>
      <div className="mt-3 flex items-center gap-2">
        <p className="font-mono text-[12px] text-text-muted">
          {job.location || "Remote / unspecified"} · {timeAgo(job.first_seen_at)}
        </p>
        <CountryBadges countries={job.countries} isRemote={job.is_remote} />
      </div>
      {job.matched_on.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {job.matched_on.map((reason) => (
            <span
              key={reason}
              className="rounded-[10px] border border-[var(--glass-border)] bg-elevated px-2 py-0.5 text-xs text-text-secondary"
            >
              {reason.split(":")[1]?.replace(/,/g, " ") || reason}
            </span>
          ))}
        </div>
      )}
    </Link>
  );
}