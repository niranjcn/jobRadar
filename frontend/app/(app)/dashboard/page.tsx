"use client";

import { useEffect, useState } from "react";
import { JobCard } from "@/components/job-card";
import { RadarLoading } from "@/components/radar-loading";
import { StatCard } from "@/components/stat-card";
import { api } from "@/lib/api";
import type { Job, Stats } from "@/lib/types";

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([api.stats(), api.jobs({ limit: 8 })])
      .then(([s, j]) => {
        setStats(s);
        setJobs(j.jobs);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const hour = new Date().getHours();
  const greeting = hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening";

  return (
    <div className="mx-auto max-w-6xl p-8">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="font-mono text-[11px] uppercase tracking-[0.16em] text-primary animate-rise">
            Edition · {new Date().toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })} ·{" "}
            {stats?.companies ?? 0} sources
          </p>
          <h1 className="font-fraunces mt-1 text-[28px] font-extrabold tracking-[-0.02em] animate-rise-1">
            {greeting}, Radar
          </h1>
          <p className="mt-1 text-sm text-text-secondary animate-rise-2">
            Here&apos;s what&apos;s happening in your job market.
          </p>
        </div>
        <div className="hidden shrink-0 rounded border-2 border-border bg-surface px-3 py-2 font-mono text-[10px] uppercase tracking-[0.12em] text-text-muted shadow-offset-sm lg:block animate-rise-2">
          Ink · Parchment · v0.2
        </div>
      </div>

      {loading ? (
        <RadarLoading />
      ) : error ? (
        <div className="card mt-8 p-6 text-sm text-danger">{error}</div>
      ) : (
        <>
          <div className="mt-6 h-[2px] w-full origin-left bg-border draw-line" />
          <div className="mt-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
            <StatCard value={stats?.jobs_new_7d ?? 0} label="New jobs (7d)" accent="primary" delay={80} />
            <StatCard value={stats?.matches ?? 0} label="Matches" accent="accent" delay={140} />
            <StatCard value={stats?.companies ?? 0} label="Companies monitored" delay={200} />
            <StatCard value={`${stats?.avg_match_score ?? 0}%`} label="Average match" accent="success" delay={260} />
          </div>

          <div className="mt-10 flex items-center justify-between">
            <h2 className="font-fraunces text-lg font-bold tracking-[-0.01em]">New opportunities</h2>
            <span className="rounded border-2 border-border bg-surface px-2.5 py-1 font-mono text-xs font-medium shadow-offset-sm">
              {stats?.jobs_total ?? 0} total
            </span>
          </div>
          <div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-2">
            {jobs.map((job, i) => (
              <JobCard key={job.id} job={job} index={i} />
            ))}
          </div>
          {jobs.length === 0 && (
            <p className="mt-6 text-sm text-text-muted">No jobs tracked yet.</p>
          )}
        </>
      )}
    </div>
  );
}