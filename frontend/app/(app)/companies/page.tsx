"use client";

import { useEffect, useMemo, useState } from "react";
import { CompanyLogo } from "@/components/company-logo";
import { RadarLoading } from "@/components/radar-loading";
import { api } from "@/lib/api";
import { atsLabel, timeAgo } from "@/lib/format";
import type { Company } from "@/lib/types";

const PAGE_SIZE = 20;

export default function CompaniesPage() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [q, setQ] = useState("");
  const [page, setPage] = useState(0);

  useEffect(() => {
    api
      .companies()
      .then((res) => setCompanies(res.companies))
      .finally(() => setLoading(false));
  }, []);

  const filtered = useMemo(
    () =>
      companies.filter((c) => c.company_name.toLowerCase().includes(q.trim().toLowerCase())),
    [companies, q],
  );

  const pageCount = useMemo(() => Math.max(1, Math.ceil(filtered.length / PAGE_SIZE)), [filtered]);
  const visible = filtered.slice(page * PAGE_SIZE, page * PAGE_SIZE + PAGE_SIZE);

  return (
    <div className="mx-auto max-w-4xl p-8">
      <h1 className="text-[28px] font-semibold">Companies</h1>
      <p className="mt-1 text-sm text-text-secondary">
        {filtered.length} company{filtered.length === 1 ? "" : "s"} monitored across your sources
      </p>

      <div className="mt-6 flex items-center gap-2">
        <input
          value={q}
          onChange={(e) => {
            setQ(e.target.value);
            setPage(0);
          }}
          placeholder="Search companies…"
          className="search-input w-64"
        />
      </div>

      <div className="mt-4">
        {loading ? (
          <RadarLoading />
        ) : (
          <>
            <div className="card overflow-hidden">
              <table className="w-full text-sm">
                <thead className="border-b border-border text-left text-xs uppercase tracking-wide text-text-muted">
                  <tr>
                    <th className="px-4 py-3 font-medium">Company</th>
                    <th className="px-4 py-3 font-medium">ATS</th>
                    <th className="px-4 py-3 font-medium">Jobs</th>
                    <th className="px-4 py-3 font-medium">Last checked</th>
                  </tr>
                </thead>
                <tbody>
                  {visible.map((c) => (
                    <tr key={c.id} className="border-b border-border/50 last:border-0 hover:bg-elevated">
                      <td className="px-4 py-3 font-medium text-text">
                        <span className="flex items-center gap-2.5">
                          <CompanyLogo name={c.company_name} domain={c.domain} size="sm" />
                          {c.company_name}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-text-secondary">{atsLabel(c.ats_type)}</td>
                      <td className="px-4 py-3 text-text-secondary">{c.job_count}</td>
                      <td className="px-4 py-3 text-text-muted">{timeAgo(c.last_checked_at)}</td>
                    </tr>
                  ))}
                  {visible.length === 0 && (
                    <tr>
                      <td colSpan={4} className="px-4 py-8 text-center text-sm text-text-muted">
                        No companies match your search.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
            <div className="mt-6 flex items-center justify-between text-sm text-text-muted">
              <span>
                Page {page + 1} of {pageCount}
              </span>
              <div className="flex gap-2">
                <button className="btn-ghost" disabled={page === 0} onClick={() => setPage((p) => Math.max(0, p - 1))}>
                  Previous
                </button>
                <button
                  className="btn-ghost"
                  disabled={page >= pageCount - 1}
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