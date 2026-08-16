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
      <h1 className="text-[28px] font-semibold">{greeting}, Radar</h1>
      <p className="mt-1 text-sm text-text-secondary">
        Here&apos;s what&apos;s happening in your job market.
      </p>

      {loading ? (
        <RadarLoading />
      ) : error ? (
        <div className="card mt-8 p-6 text-sm text-danger">{error}</div>
      ) : (
        <>
          <div className="mt-8 grid grid-cols-2 gap-4 lg:grid-cols-4">
            <StatCard value={stats?.jobs_new_7d ?? 0} label="New jobs (7d)" accent="primary" />
            <StatCard value={stats?.matches ?? 0} label="Matches" accent="accent" />
            <StatCard value={stats?.companies ?? 0} label="Companies monitored" />
            <StatCard value={`${stats?.avg_match_score ?? 0}%`} label="Average match" accent="success" />
          </div>

          <div className="mt-10 flex items-center justify-between">
            <h2 className="text-lg font-semibold">New opportunities</h2>
            <span className="text-xs text-text-muted">
              {stats?.jobs_total ?? 0} total
            </span>
          </div>
          <div className="mt-4 grid grid-cols-1 gap-3 lg:grid-cols-2">
            {jobs.map((job) => (
              <JobCard key={job.id} job={job} />
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