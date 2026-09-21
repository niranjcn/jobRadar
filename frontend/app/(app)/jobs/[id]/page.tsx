"use client";

import Link from "next/link";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { CountryBadges, MatchBadge } from "@/components/job-card";
import { CompanyLogo } from "@/components/company-logo";
import { RadarLoading } from "@/components/radar-loading";
import { api } from "@/lib/api";
import { timeAgo } from "@/lib/format";
import { referralMessage } from "@/lib/referral";
import type { Job } from "@/lib/types";

export default function JobDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const searchParams = useSearchParams();
  const from = searchParams.get("from");
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [referral, setReferral] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  function handleBack() {
    if (from && from.startsWith("/") && !from.startsWith("//")) {
      router.push(from);
      return;
    }
    if (typeof window !== "undefined" && window.history.length > 1) {
      router.back();
      return;
    }
    router.push("/jobs");
  }

  function backLabel(): string {
    if (!from) return "← Back";
    if (from.startsWith("/matches")) return "← Back to Matches";
    if (from.startsWith("/new-jobs")) return "← Back to New Jobs";
    if (from.startsWith("/jobs")) return "← Back to Jobs";
    return "← Back";
  }

  function backHref(): string {
    if (from && from.startsWith("/") && !from.startsWith("//")) return from;
    return "/jobs";
  }

  useEffect(() => {
    api
      .job(params.id)
      .then(setJob)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [params.id]);

  if (loading) return <RadarLoading label="Loading job…" />;
  if (error) return <div className="p-8 text-sm text-danger">{error}</div>;
  if (!job) return null;

  const reasons = job.matched_on;

  const generateReferral = () => {
    setReferral(referralMessage(job));
    setCopied(false);
  };

  const copyReferral = async () => {
    if (referral === null) return;
    try {
      await navigator.clipboard.writeText(referral);
      setCopied(true);
    } catch {
      setCopied(false);
    }
  };

  return (
    <div className="mx-auto max-w-3xl p-8">
      {from ? (
        <Link href={backHref()} className="text-sm text-text-secondary hover:text-text">
          {backLabel()}
        </Link>
      ) : (
        <button
          type="button"
          onClick={handleBack}
          className="text-sm text-text-secondary hover:text-text"
        >
          {backLabel()}
        </button>
      )}

      <div className="mt-6 flex items-start justify-between gap-6">
        <div className="flex items-center gap-4">
          <CompanyLogo name={job.company} domain={job.domain} size="lg" />
          <div>
            <p className="text-sm text-text-secondary">{job.company}</p>
            <h1 className="mt-0.5 text-2xl font-semibold">{job.title}</h1>
            <p className="mt-1 text-sm text-text-muted">
              {job.location || "Remote / unspecified"} · {timeAgo(job.first_seen_at)}
            </p>
            <div className="mt-1">
              <CountryBadges countries={job.countries} isRemote={job.is_remote} />
            </div>
          </div>
        </div>
        <div className="text-right">
          {job.match_score !== null && (
            <div className="text-xl font-semibold text-success">{job.match_score}% MATCH</div>
          )}
        </div>
      </div>

      {reasons.length > 0 && (
        <section className="card mt-8 p-5">
          <h2 className="text-[15px] font-semibold">Why this matches</h2>
          <ul className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-2">
            {reasons.map((reason) => {
              const value = reason.split(":")[1]?.replace(/,/g, " ") || reason;
              return (
                <li key={reason} className="flex items-center gap-2 text-sm text-text-secondary">
                  <span className="text-success">✓</span> {value}
                </li>
              );
            })}
          </ul>
        </section>
      )}

      <section className="card mt-6 p-5">
        <h2 className="text-[15px] font-semibold">Job Description</h2>
        <p className="mt-3 whitespace-pre-wrap text-sm leading-relaxed text-text-secondary">
          {job.description || "No description available."}
        </p>
      </section>

      <section className="card mt-8 p-5">
        <h2 className="text-[15px] font-semibold">Referral Message</h2>
        <p className="mt-2 text-sm text-text-muted">
          Generate a copy-ready referral message with the company, title and job ID filled in
          (leave the <code className="rounded bg-surface px-1">[Name]</code> placeholder for the
          recipient's name).
        </p>
        <div className="mt-4 flex gap-3">
          <button type="button" onClick={generateReferral} className="btn-primary">
            Generate Referral Message
          </button>
          {referral !== null && (
            <button type="button" onClick={copyReferral} className="btn-ghost">
              {copied ? "Copied ✓" : "Copy Message"}
            </button>
          )}
        </div>
        {referral !== null && (
          <textarea
            readOnly
            value={referral}
            rows={12}
            className="search-input mt-4 w-full resize-y rounded p-3 font-mono text-xs leading-relaxed"
            onFocus={(e) => e.currentTarget.select()}
          />
        )}
      </section>

      <div className="mt-8">
        {job.url ? (
          <a href={job.url} target="_blank" rel="noopener noreferrer" className="btn-primary">
            Apply Now →
          </a>
        ) : (
          <span className="text-sm text-text-muted">No external apply link.</span>
        )}
      </div>
    </div>
  );
}