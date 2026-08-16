"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { JobCard } from "@/components/job-card";
import { RadarLoading } from "@/components/radar-loading";
import { api } from "@/lib/api";
import { ATS_ORDER, atsLabel, dateIST, startOfTodayUTC } from "@/lib/format";
import type { Job } from "@/lib/types";

const PAGE_SIZE = 20;

export default function NewJobsPage() {
  const [ats, setAts] = useState("");
  const [company, setCompany] = useState("");
  const [country, setCountry] = useState("");
  const [companyOptions, setCompanyOptions] = useState<string[]>([]);
  const [countryOptions, setCountryOptions] = useState<string[]>([]);
  const [atsOptions, setAtsOptions] = useState<string[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [loading, setLoading] = useState(true);

  const since = startOfTodayUTC();

  useEffect(() => {
    api.jobFilters().then((f) => {
      setCompanyOptions(f.companies);
      setCountryOptions(f.countries);
      setAtsOptions(f.ats_types);
    });
  }, []);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.jobs({ ats, company, country, since, limit: PAGE_SIZE, offset: page * PAGE_SIZE });
      setJobs(res.jobs);
      setTotal(res.total);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [ats, company, country, since, page]);

  useEffect(() => {
    load();
  }, [load]);

  const pageCount = useMemo(() => Math.max(1, Math.ceil(total / PAGE_SIZE)), [total]);

  function resetPage(fn: (v: string) => void, v: string) {
    setPage(0);
    fn(v);
  }

  return (
    <div className="mx-auto max-w-6xl p-8">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-[28px] font-semibold">New Jobs Today</h1>
          <p className="mt-1 text-sm text-text-secondary">
            {total} posting{total === 1 ? "" : "s"} first seen on {dateIST(since)}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <select value={company} onChange={(e) => resetPage(setCompany, e.target.value)} className="search-input w-44">
            <option value="">All companies</option>
            {companyOptions.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
          <select value={country} onChange={(e) => resetPage(setCountry, e.target.value)} className="search-input w-36">
            <option value="">All countries</option>
            {countryOptions.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
          <select value={ats} onChange={(e) => resetPage(setAts, e.target.value)} className="search-input w-36">
            <option value="">All sources</option>
            {ATS_ORDER.filter((a) => atsOptions.includes(a)).map((a) => (
              <option key={a} value={a}>
                {atsLabel(a)}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="mt-8">
        {loading ? (
          <RadarLoading label="Scanning today&apos;s jobs…" />
        ) : jobs.length === 0 ? (
          <div className="card p-10 text-center text-sm text-text-muted">
            No new jobs found today yet.
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
            {jobs.map((job) => (
              <JobCard key={job.id} job={job} />
            ))}
          </div>
        )}
      </div>

      <div className="mt-6 flex items-center justify-between text-sm text-text-muted">
        <span>
          Page {page + 1} of {pageCount}
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
    </div>
  );
}