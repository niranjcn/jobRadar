"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { CompanySelect } from "@/components/company-select";
import { domainsFromJobs } from "@/components/company-logo";
import { OpportunityRow, Pager, PageHeader, EmptyState, LoadingState, Toggle } from "@/components/ink/ui";
import styles from "@/components/ink/ink.module.css";
import { api } from "@/lib/api";
import { ATS_ORDER, atsLabel, countryName, dateIST } from "@/lib/format";
import { loadSaved, toggleSaved } from "@/lib/job-store";
import type { Job } from "@/lib/types";

const PAGE_SIZE = 20;
const NEW_BADGE_MS = 3 * 3600 * 1000;

type Window = "today" | "6h" | "12h";

function windowSince(w: Window): string {
  const now = Date.now();
  if (w === "today") {
    const d = new Date();
    return new Date(d.getFullYear(), d.getMonth(), d.getDate()).toISOString();
  }
  return new Date(now - (w === "6h" ? 6 : 12) * 3600 * 1000).toISOString();
}

const WINDOW_LABEL: Record<Window, string> = { today: "Today", "6h": "Last 6 hours", "12h": "Last 12 hours" };

export default function NewJobsPage() {
  const [win, setWin] = useState<Window>("today");
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

  const since = useMemo(() => windowSince(win), [win]);

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
        ats: ats || undefined,
        company: company || undefined,
        country: country || undefined,
        remote_only: remoteOnly || undefined,
        since,
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
  }, [ats, company, country, remoteOnly, since, page]);

  useEffect(() => {
    load();
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
        eyebrow="Fresh feed"
        title="New Jobs Today"
        desc={`Fresh opportunities discovered ${win === "today" ? "in the last 24 hours" : `in the ${WINDOW_LABEL[win].toLowerCase()}`}, first seen on ${dateIST(since)}.`}
        action={
          <span style={{ display: "inline-flex", alignItems: "center", gap: 10 }}>
            <span className={styles.liveDot} />
            <span style={{ fontSize: 28, fontWeight: 800, letterSpacing: "-0.02em", fontVariantNumeric: "tabular-nums" }}>
              {total.toLocaleString()}
            </span>
            <span style={{ fontSize: 13, color: "var(--ink-text2)" }}>new jobs</span>
          </span>
        }
      />

      <div className={styles.toolbar}>
        {(Object.keys(WINDOW_LABEL) as Window[]).map((w) => (
          <button
            key={w}
            type="button"
            className={`${styles.pill} ${win === w ? styles.pillActive : ""}`}
            onClick={() => {
              setWin(w);
              setPage(0);
            }}
          >
            {WINDOW_LABEL[w]}
          </button>
        ))}
        <Toggle checked={remoteOnly} onChange={(v) => { setPage(0); setRemoteOnly(v); }} label="Remote" />
        <span className={styles.spacer} />
        <div style={{ width: 180 }}>
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
      </div>

      {loading ? (
        <LoadingState label="Scanning today's jobs…" rows={6} />
      ) : jobs.length === 0 ? (
        <EmptyState title="No new jobs found yet." desc="Check back after the next poll sweep." />
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
            {jobs.map((job) => {
              const fresh =
                job.first_seen_at != null && Date.now() - new Date(job.first_seen_at).getTime() < NEW_BADGE_MS;
              return (
                <OpportunityRow
                  key={job.id}
                  job={job}
                  saved={saved.includes(job.id)}
                  onToggleSave={() => setSaved((cur) => toggleSaved(cur, job.id))}
                  isNew={fresh}
                />
              );
            })}
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
