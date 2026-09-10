"use client";

import { useState } from "react";
import { avatarColor, initials } from "@/lib/format";

/** Google favicon URL for a company domain, or null when unknown. */
export function logoUrl(domain?: string | null): string | null {
  const d = (domain || "").trim().toLowerCase();
  if (!d) return null;
  return `https://www.google.com/s2/favicons?domain=${encodeURIComponent(d)}&sz=128`;
}

/** Build a company → domain map from loaded jobs (for filter dropdowns). */
export function domainsFromJobs(
  jobs: { company: string; domain?: string | null }[],
): Record<string, string | null> {
  const m: Record<string, string | null> = {};
  for (const j of jobs) {
    if (!(j.company in m)) m[j.company] = j.domain ?? null;
  }
  return m;
}

const SIZES = {
  sm: "h-7 w-7 text-[10px] rounded-lg",
  md: "h-9 w-9 text-xs rounded-[10px]",
  lg: "h-12 w-12 text-sm rounded-[10px]",
} as const;

export function CompanyLogo({
  name,
  domain,
  size = "md",
}: {
  name: string;
  domain?: string | null;
  size?: keyof typeof SIZES;
}) {
  const [failed, setFailed] = useState(false);
  const src = logoUrl(domain);
  if (!src || failed) {
    return (
      <div
        className={`flex ${SIZES[size]} shrink-0 items-center justify-center border-2 border-border font-fraunces font-extrabold shadow-offset-sm ${avatarColor(name)}`}
      >
        {initials(name)}
      </div>
    );
  }
  return (
    <img
      src={src}
      alt=""
      loading="lazy"
      onError={() => setFailed(true)}
      className={`${SIZES[size]} shrink-0 border-2 border-border bg-white object-contain p-0.5 shadow-offset-sm`}
    />
  );
}
