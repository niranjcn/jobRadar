"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { JobCard } from "@/components/job-card";
import { RadarLoading } from "@/components/radar-loading";
import { api } from "@/lib/api";
import type { CompanyMatchSummary, Job } from "@/lib/types";

const PAGE_SIZE = 20;

export default function MatchesPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [summary, setSummary] = useState<CompanyMatchSummary[]>([]);
  const [selectedCompany, setSelectedCompany] = useState<string | null>(null);
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(true);
  const [companyLoading, setCompanyLoading] = useState(false);
  const [page, setPage] = useState(0);
  const [total, setTotal] = useState(0);

  const load = useCallback(async (company: string | null, pageNum: number) => {
    if (company) setCompanyLoading(true);
    try {
      const res = await api.matchedJobs({
        company: company || undefined,
        limit: PAGE_SIZE,
        offset: pageNum * PAGE_SIZE,
      });
      setJobs(res.jobs);
      setTotal(res.total);
    } finally {
      setCompanyLoading(false);
    }
  }, []);

  useEffect(() => {
    load(null, 0).finally(() => setLoading(false));
    api.matchesSummary().then((res) => setSummary(res.companies));
  }, [load]);

  function selectCompany(company: string) {
    if (selectedCompany === company) {
      setSelectedCompany(null);
      setPage(0);
      load(null, 0);
      return;
    }
    setSelectedCompany(company);
    setPage(0);
    load(company, 0);
  }

  const pageCount = useMemo(() => Math.max(1, Math.ceil(total / PAGE_SIZE)), [total]);

  const filteredSummary = useMemo(
    () => summary.filter((s) => s.company.toLowerCase().includes(q.trim().toLowerCase())),
    [summary, q],
  );

  return (
    <div className="mx-auto max-w-6xl p-8">
      <h1 className="text-[28px] font-semibold">Matches</h1>
      <p className="mt-1 text-sm text-text-secondary">Jobs that hit your preferences</p>

      <div className="mt-8">
        {loading ? (
          <RadarLoading label="Scanning matches…" />
        ) : summary.length === 0 ? (
          <div className="card p-10 text-center text-sm text-text-muted">
            No matches yet. Set preferences to start matching.
          </div>
        ) : (
          <>
            <section className="mb-6 flex items-center justify-between gap-3">
              <p className="text-sm text-text-secondary">
                {summary.length} compan{summary.length === 1 ? "y" : "ies"} with matches
              </p>
              <input
                value={q}
                onChange={(e) => setQ(e.target.value)}
                placeholder="Search matched companies…"
                className="search-input w-56"
              />
            </section>

            <section className="mb-6 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
              {filteredSummary.length === 0 ? (
                <div className="card p-6 text-center text-sm text-text-muted sm:col-span-2 lg:col-span-4">
                  No companies match your search.
                </div>
              ) : (
                filteredSummary.map((entry) => (
                  <button
                    key={entry.company}
                    onClick={() => selectCompany(entry.company)}
                    className={`card flex items-center justify-between p-4 text-left transition-colors ${
                      selectedCompany === entry.company ? "ring-2 ring-primary" : "hover:border-primary/60"
                    }`}
                  >
                    <div>
                      <p className="text-sm font-semibold text-text">{entry.company}</p>
                      <p className="text-xs text-text-muted">
                        {entry.matches} match{entry.matches === 1 ? "" : "es"}
                      </p>
                    </div>
                    <span className="text-xl font-semibold text-success">{entry.matches}</span>
                  </button>
                ))
              )}
            </section>

            {selectedCompany && (
              <p className="mb-3 text-sm text-text-muted">
                Showing all {total} matched role{total === 1 ? "" : "s"} for{" "}
                <span className="font-semibold text-text">{selectedCompany}</span>{" "}
                <button onClick={() => selectCompany(selectedCompany)} className="text-primary hover:underline">
                  (clear)
                </button>
              </p>
            )}

            {companyLoading ? (
              <RadarLoading label="Loading company matches…" />
            ) : jobs.length === 0 ? (
              <div className="card p-10 text-center text-sm text-text-muted">
                No visible matches. Try another company.
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
                    <button
                      className="btn-ghost"
                      disabled={page === 0 || companyLoading}
                      onClick={() => {
                        const next = page - 1;
                        setPage(next);
                        load(selectedCompany, next);
                      }}
                    >
                      Previous
                    </button>
                    <button
                      className="btn-ghost"
                      disabled={page >= pageCount - 1 || companyLoading}
                      onClick={() => {
                        const next = page + 1;
                        setPage(next);
                        load(selectedCompany, next);
                      }}
                    >
                      Next
                    </button>
                  </div>
                </div>
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
}