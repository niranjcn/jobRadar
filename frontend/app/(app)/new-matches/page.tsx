"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { CompanySelect } from "@/components/company-select";
import { CompanyLogo, domainsFromJobs } from "@/components/company-logo";
import { EmptyState, LoadingState, PageHeader, Pager, ScoreRing } from "@/components/ink/ui";
import { PaywallGate } from "@/components/paywall-gate";
import styles from "@/components/ink/ink.module.css";
import { api } from "@/lib/api";
import { ATS_ORDER, atsLabel, dateIST, startOfTodayUTC, timeAgo } from "@/lib/format";
import { loadSaved, toggleSaved } from "@/lib/job-store";
import type { Job } from "@/lib/types";

const PAGE_SIZE = 20;

function whyChips(job: Job): string[] {
  return (job.matched_on || [])
    .map((r) => {
      const parts = r.split(":");
      return (parts[1] || r).replace(/,/g, " ").trim();
    })
    .filter(Boolean);
}

export default function NewMatchesPage() {
  const searchParams = useSearchParams();
  const [ats, setAts] = useState(() => searchParams.get("ats") || "");
  const [company, setCompany] = useState(() => searchParams.get("company") || "");
  const [companyOptions, setCompanyOptions] = useState<string[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(() => {
    const p = parseInt(searchParams.get("page") || "0", 10);
    return Number.isFinite(p) && p >= 0 ? p : 0;
  });
  const [saved, setSaved] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  const since = startOfTodayUTC();

  useEffect(() => {
    setSaved(loadSaved());
    api.jobFilters().then((f) => {
      setCompanyOptions(f.companies);
    });
  }, []);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.matchedJobs({
        company: company || undefined,
        ats: ats || undefined,
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
  }, [ats, company, since, page]);

  useEffect(() => {
    load();
  }, [load]);

  const pageCount = useMemo(() => Math.max(1, Math.ceil(total / PAGE_SIZE)), [total]);
  const companyDomains = useMemo(() => domainsFromJobs(jobs), [jobs]);

  function syncUrl(next: { ats?: string; company?: string; page?: number }) {
    if (typeof window === "undefined") return;
    const url = new URL(window.location.href);
    const atsVal = next.ats !== undefined ? next.ats : ats;
    const compVal = next.company !== undefined ? next.company : company;
    const pageVal = next.page !== undefined ? next.page : page;
    if (atsVal) url.searchParams.set("ats", atsVal);
    else url.searchParams.delete("ats");
    if (compVal) url.searchParams.set("company", compVal);
    else url.searchParams.delete("company");
    if (pageVal) url.searchParams.set("page", String(pageVal));
    else url.searchParams.delete("page");
    window.history.replaceState(null, "", url.pathname + url.search);
  }

  function resetPage(fn: (v: string) => void, v: string) {
    setPage(0);
    fn(v);
    if (typeof window !== "undefined") {
      const url = new URL(window.location.href);
      // defer url sync to next tick so state has updated
      setTimeout(() => syncUrl({ page: 0, [fn === setAts ? "ats" : "company"]: v } as unknown as { ats?: string; company?: string; page?: number }), 0);
    }
  }

  function buildFrom(): string {
    const params = new URLSearchParams();
    if (company) params.set("company", company);
    if (ats) params.set("ats", ats);
    if (page) params.set("page", String(page));
    const qs = params.toString();
    return `/new-matches${qs ? `?${qs}` : ""}`;
  }

  return (
    <PaywallGate feature="New Matches Today">
      <div className={styles.content}>
        <PageHeader
          eyebrow="Fresh matches"
          title="New Matches Today"
          desc={`Your latest high-quality opportunities — found on ${dateIST(since)}.`}
        action={
          <span style={{ display: "inline-flex", alignItems: "center", gap: 10 }}>
            <span className={styles.glowDot} />
            <span style={{ fontSize: 28, fontWeight: 800, letterSpacing: "-0.02em", fontVariantNumeric: "tabular-nums" }}>
              {total.toLocaleString()}
            </span>
            <span style={{ fontSize: 13, color: "var(--ink-text2)" }}>new matches</span>
          </span>
        }
      />

      <div className={styles.toolbar}>
        <div style={{ width: 190 }}>
          <CompanySelect
            companies={companyOptions}
            value={company}
            onChange={(v) => resetPage(setCompany, v)}
            domains={companyDomains}
          />
        </div>
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
        <LoadingState label="Scanning today's matches…" rows={5} />
      ) : jobs.length === 0 ? (
        <EmptyState title="No new matches today yet." desc="Fresh matches appear here as soon as polls discover them." />
      ) : (
        <>
          <section className={styles.panel}>
            <div>
              {jobs.map((job) => {
                const isSaved = saved.includes(job.id);
                const why = whyChips(job);
                return (
                  <div key={job.id} className={styles.feedRow}>
                    <div className={styles.fMain}>
                      <CompanyLogo name={job.company} domain={job.domain} size="md" />
                      <div style={{ minWidth: 0 }}>
                        <p style={{ fontSize: 10.5, fontWeight: 800, letterSpacing: "0.12em", color: "var(--ink-mint)", margin: 0 }}>
                          ● NEW MATCH
                        </p>
                        <Link href={`/jobs/${job.id}?from=${encodeURIComponent(buildFrom())}`} className={styles.fTitle} style={{ display: "block", textDecoration: "none" }}>
                          {job.title}
                        </Link>
                        <div className={styles.fCompany}>{job.company}</div>
                        {why.length > 0 && (
                          <div className={styles.chipRow} style={{ marginTop: 6 }}>
                            {why.slice(0, 3).map((w) => (
                              <span key={w} className={styles.tagChip} style={{ cursor: "default", fontSize: 11 }}>
                                {w}
                              </span>
                            ))}
                          </div>
                        )}
                        <div className={styles.fSub}>
                          {job.location || "Remote / unspecified"} · {timeAgo(job.first_seen_at)}
                        </div>
                      </div>
                    </div>
                    <span className={styles.fLoc}>
                      <span style={{ overflow: "hidden", textOverflow: "ellipsis" }}>{job.location || "Remote"}</span>
                    </span>
                    <span className={styles.fSrcWrap}>
                      <span className={styles.srcPill}>{job.countries[0] || "—"}</span>
                    </span>
                    <span style={{ display: "flex", alignItems: "center", gap: 10 }}>
                      <ScoreRing score={job.match_score} size={46} />
                      <button
                        type="button"
                        className={styles.fSave}
                        style={isSaved ? { color: "var(--ink-mint)" } : undefined}
                        aria-label={isSaved ? "Unsave job" : "Save job"}
                        onClick={() => setSaved((cur) => toggleSaved(cur, job.id))}
                      >
                        <svg viewBox="0 0 24 24" width="17" height="17" fill={isSaved ? "currentColor" : "none"} stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" aria-hidden>
                          <path d="M6.5 3.5h11a1 1 0 0 1 1 1V21l-6.5-4-6.5 4V4.5a1 1 0 0 1 1-1z" />
                        </svg>
                      </button>
                    </span>
                  </div>
                );
              })}
            </div>
          </section>
          <Pager
            page={page}
            pageCount={pageCount}
            disabled={loading}
            label={`Page ${page + 1} of ${pageCount} · ${total} total`}
            onPrev={() => {
              const next = Math.max(0, page - 1);
              setPage(next);
              syncUrl({ page: next });
            }}
            onNext={() => {
              const next = Math.min(pageCount - 1, page + 1);
              setPage(next);
              syncUrl({ page: next });
            }}
          />
        </>
      )}
      </div>
    </PaywallGate>
  );
}
