"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { CompanyLogo } from "@/components/company-logo";
import { EmptyState, ErrorState, LoadingState, PageHeader, Pager, ScoreRing } from "@/components/ink/ui";
import { PaywallGate } from "@/components/paywall-gate";
import styles from "@/components/ink/ink.module.css";
import { api } from "@/lib/api";
import { ATS_ORDER, atsLabel, startOfTodayUTC, timeAgo } from "@/lib/format";
import { loadSaved, toggleSaved } from "@/lib/job-store";
import { copyReferral } from "@/lib/referral";
import type { CompanyMatchSummary, Job } from "@/lib/types";

const PAGE_SIZE = 20;

type Range = "today" | "day";

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
  const [ats, setAts] = useState(() => searchParams.get("ats") || "");
  const [range, setRange] = useState<Range>("today");
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(true);
  const [companyLoading, setCompanyLoading] = useState(false);
  const [page, setPage] = useState(() => {
    const p = parseInt(searchParams.get("page") || "0", 10);
    return Number.isFinite(p) && p >= 0 ? p : 0;
  });
  const [total, setTotal] = useState(0);
  const [saved, setSaved] = useState<string[]>([]);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(
    async (company: string | null, atsVal: string, rangeVal: Range, pageNum: number) => {
      if (company) setCompanyLoading(true);
      try {
        const res = await api.matchedJobs({
          company: company || undefined,
          ats: atsVal || undefined,
          since: rangeVal === "today" ? startOfTodayUTC() : undefined,
          limit: PAGE_SIZE,
          offset: pageNum * PAGE_SIZE,
        });
        setJobs(res.jobs);
        setTotal(res.total);
      } finally {
        setCompanyLoading(false);
      }
    },
    [],
  );

  useEffect(() => {
    setSaved(loadSaved());
    const initialCompany = searchParams.get("company");
    const initialAts = searchParams.get("ats") || "";
    const initialPage = parseInt(searchParams.get("page") || "0", 10);
    const p = Number.isFinite(initialPage) && initialPage >= 0 ? initialPage : 0;
    setAts(initialAts);
    load(initialCompany, initialAts, "today", p)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load matches."))
      .finally(() => setLoading(false));
    api.matchesSummary().then((res) => setSummary(res.companies));
  }, [load, searchParams]);

  function syncUrl(next: { company?: string | null; ats?: string; page?: number }) {
    if (typeof window === "undefined") return;
    const url = new URL(window.location.href);
    const comp = next.company !== undefined ? next.company : selectedCompany;
    const atsVal = next.ats !== undefined ? next.ats : ats;
    const pageVal = next.page !== undefined ? next.page : page;
    if (comp) url.searchParams.set("company", comp);
    else url.searchParams.delete("company");
    if (atsVal) url.searchParams.set("ats", atsVal);
    else url.searchParams.delete("ats");
    if (pageVal > 0) url.searchParams.set("page", String(pageVal));
    else url.searchParams.delete("page");
    window.history.replaceState(null, "", url.pathname + url.search);
  }

  function reloadAll(company: string | null, atsVal: string, rangeVal: Range) {
    setPage(0);
    syncUrl({ company, ats: atsVal, page: 0 });
    load(company, atsVal, rangeVal, 0);
  }

  function selectCompany(company: string) {
    const next = selectedCompany === company ? null : company;
    setSelectedCompany(next);
    reloadAll(next, ats, range);
  }

  function changeAts(v: string) {
    setAts(v);
    reloadAll(selectedCompany, v, range);
  }

  function changeRange(v: Range) {
    setRange(v);
    setPage(0);
    load(selectedCompany, ats, v, 0);
  }

  async function handleReferral(job: Job) {
    if (await copyReferral(job)) {
      setCopiedId(job.id);
      window.setTimeout(() => {
        setCopiedId((cur) => (cur === job.id ? null : cur));
      }, 2000);
    }
  }

  function buildFrom(): string {
    const params = new URLSearchParams();
    if (selectedCompany) params.set("company", selectedCompany);
    if (ats) params.set("ats", ats);
    if (page) params.set("page", String(page));
    const qs = params.toString();
    return `/matches${qs ? `?${qs}` : ""}`;
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
          desc="Today's opportunities that align with your preferences."
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
        <ErrorState message={error} onRetry={() => load(selectedCompany, ats, range, page)} />
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
            <div style={{ display: "flex", gap: 8 }}>
              {(["today", "day"] as Range[]).map((r) => (
                <button
                  key={r}
                  type="button"
                  onClick={() => changeRange(r)}
                  className={range === r ? styles.pillActive : styles.pill}
                >
                  {r === "today" ? "Today" : "Last 24h"}
                </button>
              ))}
            </div>
            <span className={styles.spacer} />
            <select value={ats} onChange={(e) => changeAts(e.target.value)} className={styles.toolInput} aria-label="Source" style={{ width: 160 }}>
              <option value="">All sources</option>
              {ATS_ORDER.map((a) => (
                <option key={a} value={a}>
                  {atsLabel(a)}
                </option>
              ))}
            </select>
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Search matched companies…"
              className={styles.toolInput}
              style={{ width: 230 }}
              aria-label="Search matched companies"
            />
          </div>

          <div style={{ marginBottom: 12, fontSize: 13, color: "var(--ink-text2)" }}>
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
            <EmptyState title="No visible matches." desc="Try another company, source, or time range." />
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
                              href={`/jobs/${job.id}?from=${encodeURIComponent(buildFrom())}`}
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
                        <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 14 }}>
                          {job.url ? (
                            <a href={job.url} target="_blank" rel="noopener noreferrer" className={styles.btnMint} style={{ padding: "8px 16px", fontSize: 12.5 }}>
                              Apply
                            </a>
                          ) : (
                            <Link
                              href={`/jobs/${job.id}?from=${encodeURIComponent(buildFrom())}`}
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
                          <button
                            type="button"
                            className={styles.btnLine}
                            style={{ padding: "8px 16px", fontSize: 12.5 }}
                            onClick={() => handleReferral(job)}
                            title="Copy a referral request message for this job"
                          >
                            {copiedId === job.id ? "Copied ✓" : "Referral"}
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
                  syncUrl({ page: next });
                  load(selectedCompany, ats, range, next);
                }}
                onNext={() => {
                  const next = page + 1;
                  setPage(next);
                  syncUrl({ page: next });
                  load(selectedCompany, ats, range, next);
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
