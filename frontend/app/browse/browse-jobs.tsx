"use client";

import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { CompanySelect } from "@/components/company-select";
import { CompanyLogo, domainsFromJobs } from "@/components/company-logo";
import { JobCard } from "@/components/job-card";
import { RadarLoading } from "@/components/radar-loading";
import { api } from "@/lib/api";
import { ATS_ORDER, atsLabel } from "@/lib/format";
import type { Job, PublicCompany } from "@/lib/types";

const PAGE_SIZE = 20;
const STORAGE_KEY = "jobradar:browse-filters:v1";

const SINCE_OPTIONS = [
  { value: "", label: "Any time" },
  { value: "24h", label: "Last 24 hours" },
  { value: "7d", label: "Last 7 days" },
  { value: "30d", label: "Last 30 days" },
];

function sinceToIso(preset: string): string {
  if (!preset) return "";
  const now = Date.now();
  const day = 24 * 3600 * 1000;
  if (preset === "24h") return new Date(now - day).toISOString();
  if (preset === "7d") return new Date(now - 7 * day).toISOString();
  if (preset === "30d") return new Date(now - 30 * day).toISOString();
  return "";
}

type Mode = "" | "remote" | "hybrid" | "onsite";
const MODES: { value: Exclude<Mode, "">; label: string; blurb: string }[] = [
  { value: "remote", label: "Remote", blurb: "work from anywhere" },
  { value: "hybrid", label: "Hybrid", blurb: "mix of home + office" },
  { value: "onsite", label: "On-site", blurb: "at the office" },
];

interface Filters {
  q: string;
  ats: string;
  company: string;
  country: string;
  since: string;
  remoteOnly: boolean;
  mode: Mode;
  page: number;
}

const EMPTY: Filters = { q: "", ats: "", company: "", country: "", since: "", remoteOnly: false, mode: "", page: 0 };

function readMode(v: string | null): Mode {
  return v === "remote" || v === "hybrid" || v === "onsite" ? v : "";
}

function readUrlParams(sp: URLSearchParams): Filters | null {
  const keys = ["q", "ats", "company", "country", "since", "remote", "mode", "page"];
  const hasAny = keys.some((k) => sp.get(k) !== null);
  if (!hasAny) return null;
  const page = Math.max(0, parseInt(sp.get("page") || "0", 10) || 0);
  return {
    q: sp.get("q") || "",
    ats: sp.get("ats") || "",
    company: sp.get("company") || "",
    country: sp.get("country") || "",
    since: sp.get("since") || "",
    remoteOnly: sp.get("remote") === "1",
    mode: readMode(sp.get("mode")),
    page,
  };
}

function readStored(): Filters | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as Partial<Filters>;
    return { ...EMPTY, ...parsed, page: Math.max(0, Number(parsed.page) || 0) };
  } catch {
    return null;
  }
}

export function BrowseJobs() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const [filters, setFilters] = useState<Filters>(() => readUrlParams(searchParams) || EMPTY);
  const [hydrated, setHydrated] = useState(false);
  const [companyOptions, setCompanyOptions] = useState<string[]>([]);
  const [countryOptions, setCountryOptions] = useState<string[]>([]);
  const [atsOptions, setAtsOptions] = useState<string[]>(ATS_ORDER);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [topCompanies, setTopCompanies] = useState<PublicCompany[]>([]);
  const [board, setBoard] = useState<Record<string, { total: number; jobs: Job[] }>>({});
  const firstRender = useRef(true);

  // Filters survive a refresh in two layers: the URL query string (primary,
  // shareable) and localStorage (fallback when the URL has no params).
  useEffect(() => {
    const fromUrl = readUrlParams(searchParams);
    if (fromUrl) {
      setFilters(fromUrl);
    } else {
      const stored = readStored();
      if (stored) setFilters(stored);
    }
    setHydrated(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    api
      .jobFilters()
      .then((f) => {
        setCompanyOptions(f.companies);
        setCountryOptions(f.countries);
        if (f.ats_types.length) setAtsOptions(f.ats_types);
      })
      .catch(() => {});
    api
      .publicCompanies()
      .then((res) => setTopCompanies(res.companies.slice(0, 12)))
      .catch(() => {});
    Promise.all(
      MODES.map((m) =>
        api
          .publicJobs({ mode: m.value, limit: 5 })
          .then((res) => [m.value, { total: res.total, jobs: res.jobs }] as const)
          .catch(() => [m.value, { total: 0, jobs: [] }] as const),
      ),
    )
      .then((entries) => setBoard(Object.fromEntries(entries)))
      .catch(() => {});
  }, []);

  // Persist every change to both the URL and localStorage.
  useEffect(() => {
    if (!hydrated || firstRender.current) {
      firstRender.current = false;
      return;
    }
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(filters));
    } catch {}
    const sp = new URLSearchParams();
    if (filters.q) sp.set("q", filters.q);
    if (filters.ats) sp.set("ats", filters.ats);
    if (filters.company) sp.set("company", filters.company);
    if (filters.country) sp.set("country", filters.country);
    if (filters.since) sp.set("since", filters.since);
    if (filters.remoteOnly) sp.set("remote", "1");
    if (filters.mode) sp.set("mode", filters.mode);
    if (filters.page > 0) sp.set("page", String(filters.page));
    const qs = sp.toString();
    router.replace(`${pathname}${qs ? `?${qs}` : ""}`, { scroll: false });
  }, [filters, hydrated, pathname, router]);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.publicJobs({
        q: filters.q || undefined,
        ats: filters.ats || undefined,
        company: filters.company || undefined,
        country: filters.country || undefined,
        since: sinceToIso(filters.since) || undefined,
        remote_only: filters.remoteOnly || undefined,
        mode: filters.mode || undefined,
        limit: PAGE_SIZE,
        offset: filters.page * PAGE_SIZE,
      });
      setJobs(res.jobs);
      setTotal(res.total);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    if (!hydrated) return;
    const t = setTimeout(load, 250);
    return () => clearTimeout(t);
  }, [load, hydrated]);

  const pageCount = useMemo(() => Math.max(1, Math.ceil(total / PAGE_SIZE)), [total]);
  const companyDomains = useMemo(() => domainsFromJobs(jobs), [jobs]);

  function update(patch: Partial<Filters>, resetPage = true) {
    setFilters((f) => ({ ...f, ...patch, page: resetPage ? 0 : (patch.page ?? f.page) }));
  }

  const hasActiveFilters =
    filters.q !== "" ||
    filters.ats !== "" ||
    filters.company !== "" ||
    filters.country !== "" ||
    filters.since !== "" ||
    filters.mode !== "" ||
    filters.remoteOnly;

  function clearAll() {
    setFilters(EMPTY);
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch {}
  }

  return (
    <div className="mx-auto max-w-6xl p-8">
      {/* Hero */}
      <section className="relative overflow-hidden rounded-2xl border border-border bg-surface p-8 sm:p-10">
        <div className="pointer-events-none absolute -right-16 -top-16 h-64 w-64 rounded-full bg-primary/15 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-20 -left-10 h-56 w-56 rounded-full bg-accent/15 blur-3xl" />
        <div className="relative">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <p className="font-mono text-xs uppercase tracking-[0.28em] text-primary">
              Public · No login required
            </p>
            <Link href="/login" className="btn-primary">
              Get job alerts
            </Link>
          </div>
          <h1 className="mt-3 max-w-2xl font-fraunces text-4xl font-extrabold leading-tight tracking-[-0.02em] text-text sm:text-5xl">
            Find your next role, fresh from career pages.
          </h1>
          <p className="mt-3 max-w-xl text-[15px] leading-relaxed text-text-secondary">
            {total.toLocaleString()} open postings across {companyOptions.length} companies,
            tracked daily — no signup needed to browse.
          </p>
          <div className="mt-6 flex max-w-xl items-center gap-2">
            <input
              value={filters.q}
              onChange={(e) => update({ q: e.target.value })}
              placeholder="Try 'backend engineer'…"
              className="search-input w-full !py-3 text-[15px]"
            />
          </div>
          <div className="mt-3 flex flex-wrap items-center gap-2">
            <button
              type="button"
              onClick={() => update({ remoteOnly: !filters.remoteOnly })}
              className={`rounded-full border px-3 py-1.5 text-xs font-medium transition-colors ${
                filters.remoteOnly
                  ? "border-primary bg-primary/15 text-text"
                  : "border-border bg-elevated text-text-secondary hover:text-text"
              }`}
            >
              {filters.remoteOnly ? "✓ " : ""}Remote only
            </button>
            <button
              type="button"
              onClick={() => update({ since: filters.since === "24h" ? "" : "24h" })}
              className={`rounded-full border px-3 py-1.5 text-xs font-medium transition-colors ${
                filters.since === "24h"
                  ? "border-primary bg-primary/15 text-text"
                  : "border-border bg-elevated text-text-secondary hover:text-text"
              }`}
            >
              {filters.since === "24h" ? "✓ " : ""}Last 24 hours
            </button>
            {hasActiveFilters && (
              <button type="button" onClick={clearAll} className="text-xs text-text-muted hover:text-text">
                Clear all filters
              </button>
            )}
          </div>
        </div>
      </section>

      {/* Company directory */}
      {topCompanies.length > 0 && (
        <section className="mt-8">
          <div className="mb-3 flex items-baseline justify-between">
            <h2 className="font-fraunces text-lg font-bold text-text">Companies hiring now</h2>
            <p className="text-xs text-text-muted">Tap a company to filter the feed</p>
          </div>
          <div className="grid grid-cols-2 gap-2.5 sm:grid-cols-3 lg:grid-cols-4">
            {topCompanies.map((c) => {
              const active = filters.company === c.company_name;
              const fresh =
                c.latest_job_at &&
                Date.now() - new Date(c.latest_job_at).getTime() < 24 * 3600 * 1000;
              return (
                <button
                  key={c.company_name}
                  type="button"
                  onClick={() => update({ company: active ? "" : c.company_name })}
                  title={`${c.company_name} · ${c.job_count} open roles`}
                  className={`flex items-center gap-3 rounded-xl border p-3 text-left transition-colors ${
                    active
                      ? "border-primary bg-primary/10"
                      : "border-border bg-surface hover:border-primary/60"
                  }`}
                >
                  <CompanyLogo name={c.company_name} domain={c.domain} size="md" />
                  <span className="min-w-0">
                    <span className="block truncate text-[13px] font-semibold text-text">
                      {c.company_name}
                    </span>
                    <span className="block text-[11px] text-text-muted">
                      {c.job_count.toLocaleString()} role{c.job_count === 1 ? "" : "s"}
                      {fresh && <span className="ml-1 font-bold text-success">· new today</span>}
                    </span>
                  </span>
                </button>
              );
            })}
          </div>
        </section>
      )}

      {/* Work-mode board */}
      <section className="mt-8">
        <div className="mb-3 flex items-baseline justify-between">
          <h2 className="font-fraunces text-lg font-bold text-text">Browse by work mode</h2>
          <p className="text-xs text-text-muted">Latest in each lane</p>
        </div>
        <div className="grid grid-cols-1 gap-3 lg:grid-cols-3">
          {MODES.map((m) => {
            const lane = board[m.value] || { total: 0, jobs: [] };
            const active = filters.mode === m.value;
            return (
              <div key={m.value} className="card flex flex-col p-4">
                <div className="flex items-baseline justify-between">
                  <h3 className="text-[15px] font-bold text-text">{m.label}</h3>
                  <span className="font-mono text-xs text-text-muted">
                    {lane.total.toLocaleString()}
                  </span>
                </div>
                <p className="mb-3 text-xs text-text-muted">{m.blurb}</p>
                <div className="min-h-40 flex-1 space-y-2.5">
                  {lane.jobs.length === 0 ? (
                    <p className="text-xs text-text-muted">Loading…</p>
                  ) : (
                    lane.jobs.map((job) => (
                      <Link
                        key={job.id}
                        href={`/browse/${job.id}`}
                        className="flex items-center gap-2.5 rounded-lg border border-border/60 bg-elevated/40 p-2 transition-colors hover:border-primary/60"
                      >
                        <CompanyLogo name={job.company} domain={job.domain} size="sm" />
                        <span className="min-w-0">
                          <span className="block truncate text-[13px] font-semibold text-text">
                            {job.title}
                          </span>
                          <span className="block truncate text-[11px] text-text-muted">
                            {job.company} · {job.location || "Remote"}
                          </span>
                        </span>
                      </Link>
                    ))
                  )}
                </div>
                <button
                  type="button"
                  onClick={() => {
                    update({ mode: active ? "" : m.value, page: 0 });
                    document
                      .getElementById("browse-results")
                      ?.scrollIntoView({ behavior: "smooth" });
                  }}
                  className={`mt-3 rounded-lg border px-3 py-1.5 text-xs font-bold transition-colors ${
                    active
                      ? "border-primary bg-primary/10 text-text"
                      : "border-border text-text-secondary hover:text-text"
                  }`}
                >
                  {active ? "✓ Showing — tap to clear" : `View all ${m.label.toLowerCase()} →`}
                </button>
              </div>
            );
          })}
        </div>
        <p className="mt-2 text-[11px] text-text-muted">
          Hybrid = flagged in the posting text; everything not remote sits in On-site.
        </p>
      </section>

      {/* Filters */}
      <div className="card mt-8 p-4">
        <div className="flex flex-wrap items-center gap-2">
          <div className="w-44">
            <CompanySelect
              companies={companyOptions}
              value={filters.company}
              onChange={(v) => update({ company: v })}
              domains={companyDomains}
            />
          </div>
          <select
            value={filters.country}
            onChange={(e) => update({ country: e.target.value })}
            className="search-input w-36"
          >
            <option value="">All countries</option>
            {countryOptions.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
          <select
            value={filters.ats}
            onChange={(e) => update({ ats: e.target.value })}
            className="search-input w-40"
          >
            <option value="">All sources</option>
            {atsOptions.map((a) => (
              <option key={a} value={a}>
                {atsLabel(a)}
              </option>
            ))}
          </select>
          <select
            value={filters.mode}
            onChange={(e) => update({ mode: e.target.value as Mode })}
            className="search-input w-32"
          >
            <option value="">Any mode</option>
            {MODES.map((m) => (
              <option key={m.value} value={m.value}>
                {m.label}
              </option>
            ))}
          </select>
          <select
            value={filters.since}
            onChange={(e) => update({ since: e.target.value })}
            className="search-input w-36"
          >
            {SINCE_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
          <label className="flex cursor-pointer items-center gap-2 text-sm text-text-secondary">
            <input
              type="checkbox"
              checked={filters.remoteOnly}
              onChange={(e) => update({ remoteOnly: e.target.checked })}
              className="h-4 w-4 accent-[var(--color-primary)]"
            />
            Remote only
          </label>
          {hasActiveFilters && (
            <button type="button" onClick={clearAll} className="btn-ghost">
              Clear all
            </button>
          )}
        </div>
      </div>

      <div id="browse-results" className="mb-3 mt-8 flex scroll-mt-6 items-baseline justify-between">
        <h2 className="font-fraunces text-lg font-bold text-text">
          {hasActiveFilters ? "Matching jobs" : "Latest jobs"}
        </h2>
        <p className="text-xs text-text-muted">
          {total.toLocaleString()} posting{total === 1 ? "" : "s"}
          {hasActiveFilters ? " match your filters" : ""}
        </p>
      </div>
      <div>
        {loading ? (
          <RadarLoading label="Scanning jobs…" />
        ) : jobs.length === 0 ? (
          <div className="card p-10 text-center text-sm text-text-muted">
            No jobs found. Try widening your filters.
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
            {jobs.map((job, i) => (
              <JobCard key={job.id} job={job} index={i} hrefPrefix="/browse" />
            ))}
          </div>
        )}
      </div>

      <div className="mt-6 flex items-center justify-between text-sm text-text-muted">
        <span>
          Page {filters.page + 1} of {pageCount}
        </span>
        <div className="flex gap-2">
          <button
            className="btn-ghost"
            disabled={filters.page === 0 || loading}
            onClick={() => update({ page: Math.max(0, filters.page - 1) }, false)}
          >
            Previous
          </button>
          <button
            className="btn-ghost"
            disabled={filters.page >= pageCount - 1 || loading}
            onClick={() => update({ page: Math.min(pageCount - 1, filters.page + 1) }, false)}
          >
            Next
          </button>
        </div>
      </div>

      {/* Bottom CTA */}
      <section className="card mt-10 flex flex-wrap items-center justify-between gap-4 p-6">
        <div>
          <h2 className="font-fraunces text-xl font-bold text-text">
            Never miss a matching role.
          </h2>
          <p className="mt-1 text-sm text-text-secondary">
            Tell JobRadar what you want once — get new matches on Telegram and email.
          </p>
        </div>
        <div className="flex gap-2">
          <Link href="/" className="btn-ghost">
            ← Home
          </Link>
          <Link href="/login" className="btn-primary">
            Get job alerts
          </Link>
        </div>
      </section>
    </div>
  );
}
