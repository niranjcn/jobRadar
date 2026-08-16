"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { JobCard } from "@/components/job-card";
import { RadarLoading } from "@/components/radar-loading";
import { api } from "@/lib/api";
import { ATS_ORDER, atsLabel, dateIST, startOfTodayUTC } from "@/lib/format";
import type { Job } from "@/lib/types";

const PAGE_SIZE = 20;

export default function NewMatchesPage() {
  const [ats, setAts] = useState("");
  const [atsOptions, setAtsOptions] = useState<string[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [loading, setLoading] = useState(true);

  const since = startOfTodayUTC();

  useEffect(() => {
    api.jobFilters().then((f) => setAtsOptions(f.ats_types));
  }, []);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.matchedJobs({ ats: ats || undefined, since, limit: PAGE_SIZE, offset: page * PAGE_SIZE });
      setJobs(res.jobs);
      setTotal(res.total);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [ats, since, page]);

  useEffect(() => {
    load();
  }, [load]);

  const pageCount = useMemo(() => Math.max(1, Math.ceil(total / PAGE_SIZE)), [total]);

  return (
    <div className="mx-auto max-w-6xl p-8">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-[28px] font-semibold">New Matches Today</h1>
          <p className="mt-1 text-sm text-text-secondary">
            {total} match{total === 1 ? "" : "es"} found on {dateIST(since)}
          </p>
        </div>
        <select value={ats} onChange={(e) => { setAts(e.target.value); setPage(0); }} className="search-input w-36">
          <option value="">All sources</option>
          {ATS_ORDER.filter((a) => atsOptions.includes(a)).map((a) => (
            <option key={a} value={a}>
              {atsLabel(a)}
            </option>
          ))}
        </select>
      </div>

      <div className="mt-8">
        {loading ? (
          <RadarLoading label="Scanning today&apos;s matches…" />
        ) : jobs.length === 0 ? (
          <div className="card p-10 text-center text-sm text-text-muted">
            No new matches found today yet.
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
              {jobs.map((job) => (
                <JobCard key={job.id} job={job} />
              ))}
            </div>
            <div className="mt-6 flex items-center justify-between text-sm text-text-muted">
              <span>
                Page {page + 1} of {pageCount} · {total} total
              </span>
              <div className="flex gap-2">
                <button className="btn-ghost" disabled={page === 0 || loading} onClick={() => setPage((p) => Math.max(0, p - 1))}>
                  Previous
                </button>
                <button
                  className="btn-ghost"
                  disabled={page >= pageCount - 1 || loading}
                  onClick={() => setPage((p) => Math.min(pageCount - 1, p + 1))}
                >
                  Next
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}