"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { CompanyLogo } from "@/components/company-logo";
import { EmptyState, LoadingState, PageHeader, Pager } from "@/components/ink/ui";
import styles from "@/components/ink/ink.module.css";
import { api } from "@/lib/api";
import { atsLabel, timeAgo } from "@/lib/format";
import type { Company } from "@/lib/types";

const PAGE_SIZE = 18;

type Sort = "jobs" | "alpha";

export default function CompaniesPage() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [q, setQ] = useState("");
  const [sort, setSort] = useState<Sort>("jobs");
  const [page, setPage] = useState(0);

  useEffect(() => {
    api
      .companies()
      .then((res) => setCompanies(res.companies))
      .finally(() => setLoading(false));
  }, []);

  const filtered = useMemo(() => {
    const list = companies.filter((c) => c.company_name.toLowerCase().includes(q.trim().toLowerCase()));
    if (sort === "alpha") list.sort((a, b) => a.company_name.localeCompare(b.company_name));
    else list.sort((a, b) => b.job_count - a.job_count);
    return list;
  }, [companies, q, sort]);

  const pageCount = useMemo(() => Math.max(1, Math.ceil(filtered.length / PAGE_SIZE)), [filtered]);
  const visible = filtered.slice(page * PAGE_SIZE, page * PAGE_SIZE + PAGE_SIZE);

  return (
    <div className={styles.content}>
      <PageHeader
        eyebrow="Directory"
        title="Companies"
        desc={`Explore ${filtered.length} ${filtered.length === 1 ? "company" : "companies"} and the opportunities they are hiring for.`}
      />

      <div className={styles.toolbar}>
        <input
          value={q}
          onChange={(e) => {
            setQ(e.target.value);
            setPage(0);
          }}
          placeholder="Search companies…"
          className={styles.toolInput}
          style={{ width: 250 }}
          aria-label="Search companies"
        />
        <span className={styles.spacer} />
        {(
          [
            ["jobs", "Most jobs"],
            ["alpha", "Alphabetical"],
          ] as [Sort, string][]
        ).map(([key, label]) => (
          <button
            key={key}
            type="button"
            className={`${styles.pill} ${sort === key ? styles.pillActive : ""}`}
            onClick={() => setSort(key)}
          >
            {label}
          </button>
        ))}
      </div>

      {loading ? (
        <LoadingState rows={6} />
      ) : visible.length === 0 ? (
        <EmptyState title="No companies match your search." />
      ) : (
        <>
          <div className={styles.cardGrid} style={{ gridTemplateColumns: "repeat(auto-fill, minmax(250px, 1fr))" }}>
            {visible.map((c) => (
              <Link
                key={c.id}
                href={`/jobs?company=${encodeURIComponent(c.company_name)}`}
                className={styles.panel}
                style={{ padding: 18, textDecoration: "none", display: "block" }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                  <CompanyLogo name={c.company_name} domain={c.domain} size="md" />
                  <div style={{ minWidth: 0 }}>
                    <p style={{ fontSize: 15, fontWeight: 700, margin: 0, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                      {c.company_name}
                    </p>
                    <p style={{ fontSize: 12, color: "var(--ink-muted)", margin: "2px 0 0" }}>
                      {atsLabel(c.ats_type)}
                    </p>
                  </div>
                </div>
                <p style={{ fontSize: 26, fontWeight: 800, margin: "14px 0 0", fontVariantNumeric: "tabular-nums" }}>
                  {c.job_count.toLocaleString()}
                  <span style={{ fontSize: 12, fontWeight: 500, color: "var(--ink-muted)", marginLeft: 6 }}>
                    job{c.job_count === 1 ? "" : "s"}
                  </span>
                </p>
                <p style={{ display: "flex", alignItems: "center", gap: 7, fontSize: 12, color: "var(--ink-text2)", margin: "10px 0 0" }}>
                  <span className={styles.okDot} /> Monitoring · checked {timeAgo(c.last_checked_at)}
                </p>
              </Link>
            ))}
          </div>
          <Pager
            page={page}
            pageCount={pageCount}
            label={`Page ${page + 1} of ${pageCount}`}
            onPrev={() => setPage((p) => Math.max(0, p - 1))}
            onNext={() => setPage((p) => Math.min(pageCount - 1, p + 1))}
          />
        </>
      )}
    </div>
  );
}
