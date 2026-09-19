"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { CompanyLogo } from "@/components/company-logo";
import { EmptyState, ErrorState, LoadingState, PageHeader, Pager, ScoreRing } from "@/components/ink/ui";
import { PaywallGate } from "@/components/paywall-gate";
import styles from "@/components/ink/ink.module.css";
import { api } from "@/lib/api";
import { timeAgo } from "@/lib/format";
import { loadSaved, toggleSaved } from "@/lib/job-store";
import type { CompanyMatchSummary, Job } from "@/lib/types";

const PAGE_SIZE = 20;

function whyChips(job: Job): string[] {
  return (job.matched_on || []).map((r) => {
    const parts = r.split(":");
    return (parts[1] || r).replace(/,/g, " ").trim();
  }).filter(Boolean);
}

export default function MatchesPage() {
  const searchParams = useSearchParams();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [summary, setSummary] = useState<CompanyMatchSummary[]>([]);
  const [selectedCompany, setSelectedCompany] = useState<string | null>(() => searchParams.get("company"));
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(true);
  const [companyLoading, setCompanyLoading] = useState(false);
  const [page, setPage] = useState(() => {
    const p = parseInt(searchParams.get("page") || "0", 10);
    return Number.isFinite(p) && p >= 0 ? p : 0;
  });
  const [total, setTotal] = useState(0);
  const [saved, setSaved] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

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
    setSaved(loadSaved());
    const initialCompany = searchParams.get("company");
    const initialPage = parseInt(searchParams.get("page") || "0", 10);
    const p = Number.isFinite(initialPage) && initialPage >= 0 ? initialPage : 0;
    load(initialCompany, p)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load matches."))
      .finally(() => setLoading(false));
    api.matchesSummary().then((res) => setSummary(res.companies));
  }, [load, searchParams]);

  function selectCompany(company: string) {
    if (selectedCompany === company) {
      setSelectedCompany(null);
      setPage(0);
      if (typeof window !== "undefined") {
        const url = new URL(window.location.href);
        url.searchParams.delete("company");
        url.searchParams.delete("page");
        window.history.replaceState(null, "", url.pathname + url.search);
      }
      load(null, 0);
      return;
    }
    setSelectedCompany(company);
    setPage(0);
    if (typeof window !== "undefined") {
      const url = new URL(window.location.href);
      url.searchParams.set("company", company);
      url.searchParams.delete("page");
      window.history.replaceState(null, "", url.pathname + url.search);
    }
    load(company, 0);
  }

  const pageCount = useMemo(() => Math.max(1, Math.ceil(total / PAGE_SIZE)), [total]);

  const filteredSummary = useMemo(
    () => summary.filter((s) => s.company.toLowerCase().includes(q.trim().toLowerCase())),
    [summary, q],
  );

  const totalMatches = useMemo(() => summary.reduce((s, c) => s + c.matches, 0), [summary]);

  return (
    <PaywallGate feature="Matches">
      <div className={styles.content}>
        <PageHeader
          eyebrow="Matches"
          title="Your Matches"
          desc="Opportunities that align with your skills and preferences."
          action={
            <span style={{ fontSize: 13, color: "var(--ink-text2)" }}>
              <strong style={{ fontSize: 22, color: "var(--ink-text)", fontVariantNumeric: "tabular-nums" }}>
                {totalMatches.toLocaleString()}
              </strong>{" "}
              total across {summary.length} {summary.length === 1 ? "company" : "companies"}
            </span>
          }
        />

      {loading ? (
        <LoadingState label="Scanning matches…" rows={4} />
      ) : error ? (
        <ErrorState message={error} onRetry={() => load(selectedCompany, page)} />
      ) : summary.length === 0 ? (
        <EmptyState
          title="No matches yet"
          desc="Complete your preferences and JobQuest will start finding opportunities for you."
          action={
            <Link href="/preferences" className={styles.btnMint}>
              Set Preferences
            </Link>
          }
        />
      ) : (
        <>
          <div className={styles.toolbar}>
            <span style={{ fontSize: 13, color: "var(--ink-text2)" }}>
              {selectedCompany ? (
                <>
                  Showing matches for <strong style={{ color: "var(--ink-text)" }}>{selectedCompany}</strong>{" "}
                  <button
                    type="button"
                    onClick={() => selectCompany(selectedCompany)}
                    style={{ border: 0, background: "none", color: "var(--ink-mint)", cursor: "pointer", fontSize: 13 }}
                  >
                    (clear)
                  </button>
                </>
              ) : (
                `${summary.length} ${summary.length === 1 ? "company" : "companies"} with matches`
              )}
            </span>
            <span className={styles.spacer} />
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Search matched companies…"
              className={styles.toolInput}
              style={{ width: 230 }}
              aria-label="Search matched companies"
            />
          </div>

          <section className={styles.cardGrid} style={{ gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", marginBottom: 20 }}>
            {filteredSummary.length === 0 ? (
              <div className={styles.panel} style={{ padding: 24, textAlign: "center", gridColumn: "1/-1" }}>
                <p style={{ fontSize: 13, color: "var(--ink-muted)" }}>No companies match your search.</p>
              </div>
            ) : (
              filteredSummary.map((entry) => {
                const active = selectedCompany === entry.company;
                return (
                  <button
                    key={entry.company}
                    onClick={() => selectCompany(entry.company)}
                    className={styles.panel}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 12,
                      padding: 16,
                      cursor: "pointer",
                      textAlign: "left",
                      fontFamily: "inherit",
                      borderColor: active ? "rgba(25,230,167,0.5)" : undefined,
                      background: active ? "rgba(25,230,167,0.07)" : undefined,
                    }}
                  >
                    <CompanyLogo name={entry.company} domain={entry.domain} />
                    <span style={{ minWidth: 0, flex: 1 }}>
                      <span style={{ display: "block", fontSize: 13.5, fontWeight: 600, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                        {entry.company}
                      </span>
                      <span style={{ fontSize: 12, color: "var(--ink-muted)" }}>
                        {entry.matches} match{entry.matches === 1 ? "" : "es"}
                      </span>
                    </span>
                    <span style={{ fontSize: 20, fontWeight: 800, color: "var(--ink-mint)", fontVariantNumeric: "tabular-nums" }}>
                      {entry.matches}
                    </span>
                  </button>
                );
              })
            )}
          </section>

          {companyLoading ? (
            <LoadingState label="Loading company matches…" rows={3} />
          ) : jobs.length === 0 ? (
            <EmptyState title="No visible matches." desc="Try another company." />
          ) : (
            <>
              <div className={styles.cardGrid} style={{ gridTemplateColumns: "repeat(auto-fill, minmax(330px, 1fr))" }}>
                {jobs.map((job) => {
                  const isSaved = saved.includes(job.id);
                  const why = whyChips(job);
                  return (
                    <article key={job.id} className={styles.panel} style={{ padding: 20, display: "flex", gap: 16 }}>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                          <CompanyLogo name={job.company} domain={job.domain} size="md" />
                          <div style={{ minWidth: 0 }}>
                            <Link
                              href={`/jobs/${job.id}?from=${encodeURIComponent(`/matches${selectedCompany ? `?company=${encodeURIComponent(selectedCompany)}&page=${page}` : page ? `?page=${page}` : ""}`)}`}
                              style={{ fontSize: 15, fontWeight: 700, textDecoration: "none", color: "var(--ink-text)", display: "block", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}
                            >
                              {job.title}
                            </Link>
                            <div className={styles.fCompany}>{job.company}</div>
                          </div>
                        </div>
                        <p style={{ fontSize: 12.5, color: "var(--ink-muted)", margin: "8px 0 0" }}>
                          {job.location || "Remote / unspecified"} · {timeAgo(job.first_seen_at)}
                        </p>
                        {why.length > 0 && (
                          <div className={styles.chipRow} style={{ marginTop: 10 }}>
                            {why.slice(0, 4).map((w) => (
                              <span key={w} className={styles.tagChip} style={{ cursor: "default" }}>
                                {w}
                              </span>
                            ))}
                          </div>
                        )}
                        <div style={{ display: "flex", gap: 8, marginTop: 14 }}>
                          {job.url ? (
                            <a href={job.url} target="_blank" rel="noopener noreferrer" className={styles.btnMint} style={{ padding: "8px 16px", fontSize: 12.5 }}>
                              Apply
                            </a>
                          ) : (
                            <Link
                              href={`/jobs/${job.id}?from=${encodeURIComponent(`/matches${selectedCompany ? `?company=${encodeURIComponent(selectedCompany)}&page=${page}` : page ? `?page=${page}` : ""}`)}`}
                              className={styles.btnMint}
                              style={{ padding: "8px 16px", fontSize: 12.5 }}
                            >
                              View Job
                            </Link>
                          )}
                          <button
                            type="button"
                            className={styles.btnLine}
                            style={{ padding: "8px 16px", fontSize: 12.5 }}
                            onClick={() => setSaved((cur) => toggleSaved(cur, job.id))}
                          >
                            {isSaved ? "★ Saved" : "Save"}
                          </button>
                        </div>
                      </div>
                      <ScoreRing score={job.match_score} />
                    </article>
                  );
                })}
              </div>
              <Pager
                page={page}
                pageCount={pageCount}
                disabled={companyLoading}
                label={`Page ${page + 1} of ${pageCount} · ${total} total`}
                onPrev={() => {
                  const next = page - 1;
                  setPage(next);
                  if (typeof window !== "undefined") {
                    const url = new URL(window.location.href);
                    if (next > 0) url.searchParams.set("page", String(next));
                    else url.searchParams.delete("page");
                    window.history.replaceState(null, "", url.pathname + url.search);
                  }
                  load(selectedCompany, next);
                }}
                onNext={() => {
                  const next = page + 1;
                  setPage(next);
                  if (typeof window !== "undefined") {
                    const url = new URL(window.location.href);
                    url.searchParams.set("page", String(next));
                    window.history.replaceState(null, "", url.pathname + url.search);
                  }
                  load(selectedCompany, next);
                }}
              />
            </>
          )}
        </>
      )}
      </div>
    </PaywallGate>
  );
}
