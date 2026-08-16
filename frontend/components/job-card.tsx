import { avatarColor, initials, timeAgo } from "@/lib/format";
import type { Job } from "@/lib/types";
import Link from "next/link";

export function Avatar({ name, size = "md" }: { name: string; size?: "md" | "lg" }) {
  const cls = size === "lg" ? "h-12 w-12 text-sm" : "h-9 w-9 text-xs";
  return (
    <div
      className={`flex ${cls} shrink-0 items-center justify-center rounded-md font-semibold ${avatarColor(name)}`}
    >
      {initials(name)}
    </div>
  );
}

export function MatchBadge({ score }: { score: number | null }) {
  if (score === null || score === undefined) return null;
  return (
    <span className="text-xs font-semibold text-success">{score}% MATCH</span>
  );
}

export function CountryBadges({ countries, isRemote }: { countries: string[]; isRemote: boolean }) {
  const list = countries.filter(Boolean);
  if (!list.length && !isRemote) return null;
  return (
    <>
      {list.map((c) => (
        <span key={c} className="rounded bg-elevated px-2 py-0.5 text-xs font-medium text-accent">
          {c}
        </span>
      ))}
      {isRemote && (
        <span className="rounded bg-elevated px-2 py-0.5 text-xs font-medium text-text-secondary">
          Remote
        </span>
      )}
    </>
  );
}

export function JobCard({ job }: { job: Job }) {
  return (
    <Link
      href={`/jobs/${job.id}`}
      className="group block rounded-lg border border-border bg-surface p-4 transition-colors hover:border-primary/60"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-3">
          <Avatar name={job.company} />
          <div>
            <h3 className="text-[15px] font-semibold leading-snug text-text group-hover:text-primary">
              {job.title}
            </h3>
            <p className="text-sm text-text-secondary">{job.company}</p>
          </div>
        </div>
        <MatchBadge score={job.match_score} />
      </div>
      <div className="mt-3 flex items-center gap-2">
        <p className="text-[13px] text-text-muted">
          {job.location || "Remote / unspecified"} · {timeAgo(job.first_seen_at)}
        </p>
        <CountryBadges countries={job.countries} isRemote={job.is_remote} />
      </div>
      {job.matched_on.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {job.matched_on.map((reason) => (
            <span
              key={reason}
              className="rounded bg-elevated px-2 py-0.5 text-xs text-text-secondary"
            >
              {reason.split(":")[1]?.replace(/,/g, " ") || reason}
            </span>
          ))}
        </div>
      )}
    </Link>
  );
}
