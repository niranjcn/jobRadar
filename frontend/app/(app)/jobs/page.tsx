"use client";

import { Suspense, useCallback, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { CompanySelect } from "@/components/company-select";
import { domainsFromJobs } from "@/components/company-logo";
import { OpportunityRow, Pager, PageHeader, EmptyState, LoadingState, Toggle } from "@/components/ink/ui";
import styles from "@/components/ink/ink.module.css";
import { api } from "@/lib/api";
import { ATS_ORDER, atsLabel, countryName } from "@/lib/format";
import { loadSaved, toggleSaved } from "@/lib/job-store";
import type { Job } from "@/lib/types";

const PAGE_SIZE = 20;

export default function JobsPage() {
  return (
    <Suspense fallback={<div className={styles.content}>Loading jobs…</div>}>
      <JobsInner />
    </Suspense>
  );
}

function JobsInner() {
  const searchParams = useSearchParams();
  const [q, setQ] = useState("");
  const [ats, setAts] = useState("");
  const [company, setCompany] = useState("");
  const [country, setCountry] = useState("");
  const [remoteOnly, setRemoteOnly] = useState(false);
  const [companyOptions, setCompanyOptions] = useState<string[]>([]);
  const [countryOptions, setCountryOptions] = useState<string[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [saved, setSaved] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  // Deep links (dashboard Top Companies, sidebar search) prefill filters.
  useEffect(() => {
    const cq = searchParams.get("q");
    const cc = searchParams.get("company");
    if (cq) setQ(cq);
    if (cc) setCompany(cc);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    setSaved(loadSaved());
    api.jobFilters().then((f) => {
      setCompanyOptions(f.companies);
      setCountryOptions(f.countries);
    });
  }, []);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.jobs({
        q: q || undefined,
        ats: ats || undefined,
        company: company || undefined,
        country: country || undefined,
        remote_only: remoteOnly || undefined,
        limit: PAGE_SIZE,
        offset: page * PAGE_SIZE,
      });
      setJobs(res.jobs);
      setTotal(res.total);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [q, ats, company, country, remoteOnly, page]);

  useEffect(() => {
    const t = setTimeout(load, 250);
    return () => clearTimeout(t);
  }, [load]);

  const pageCount = useMemo(() => Math.max(1, Math.ceil(total / PAGE_SIZE)), [total]);
  const companyDomains = useMemo(() => domainsFromJobs(jobs), [jobs]);

  function resetPage(fn: (v: string) => void, v: string) {
    setPage(0);
    fn(v);
  }

  return (
    <div className={styles.content}>
      <PageHeader
        eyebrow="Jobs"
        title="All Jobs"
        desc={`Explore ${total.toLocaleString()} opportunities collected from across the job market.`}
      />

      <div className={styles.toolbar}>
        <input
          value={q}
          onChange={(e) => resetPage(setQ, e.target.value)}
          placeholder="Search jobs, companies, skills…"
          className={styles.toolInput}
          style={{ width: 260 }}
          aria-label="Search jobs"
        />
        <div style={{ width: 190 }}>
          <CompanySelect
            companies={companyOptions}
            value={company}
            onChange={(v) => resetPage(setCompany, v)}
            domains={companyDomains}
          />
        </div>
        <select value={country} onChange={(e) => resetPage(setCountry, e.target.value)} className={styles.toolInput} aria-label="Country">
          <option value="">All countries</option>
          {countryOptions.map((c) => (
            <option key={c} value={c}>
              {countryName(c)}
            </option>
          ))}
        </select>
        <select value={ats} onChange={(e) => resetPage(setAts, e.target.value)} className={styles.toolInput} aria-label="Source">
          <option value="">All sources</option>
          {ATS_ORDER.map((a) => (
            <option key={a} value={a}>
              {atsLabel(a)}
            </option>
          ))}
        </select>
        <Toggle checked={remoteOnly} onChange={(v) => { setPage(0); setRemoteOnly(v); }} label="Remote" />
      </div>

      {loading ? (
        <LoadingState label="Scanning jobs…" rows={6} />
      ) : jobs.length === 0 ? (
        <EmptyState title="No jobs found." desc="Try widening your search or clearing a filter." />
      ) : (
        <section className={styles.panel}>
          <div className={styles.colHead}>
            <span>Job / Company</span>
            <span>Location</span>
            <span>Source</span>
            <span>Posted</span>
            <span />
          </div>
          <div>
            {jobs.map((job) => (
              <OpportunityRow
                key={job.id}
                job={job}
                saved={saved.includes(job.id)}
                onToggleSave={() => setSaved((cur) => toggleSaved(cur, job.id))}
              />
            ))}
          </div>
        </section>
      )}

      <Pager
        page={page}
        pageCount={pageCount}
        disabled={loading}
        label={`Page ${page + 1} of ${pageCount} · ${total.toLocaleString()} total`}
        onPrev={() => setPage((p) => Math.max(0, p - 1))}
        onNext={() => setPage((p) => Math.min(pageCount - 1, p + 1))}
      />
    </div>
  );
}
