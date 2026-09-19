"use client";

import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { CompanySelect } from "@/components/company-select";
import { CompanyLogo, domainsFromJobs } from "@/components/company-logo";
import { RadarLoading } from "@/components/radar-loading";
import { RadarMark } from "@/components/radar-mark";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { ATS_ORDER, atsLabel, timeAgo } from "@/lib/format";
import {
  filterHidden,
  hideJob,
  loadHidden,
  loadSaved,
  toggleSaved,
  unhideAll,
} from "@/lib/job-store";
import type { Job, PublicCompany } from "@/lib/types";

const STORAGE_KEY = "jobquest:browse-filters:v2";

const SINCE_OPTIONS = [
  { value: "", label: "Any time" },
  { value: "24h", label: "Last 24 hours" },
  { value: "3d", label: "Last 3 days" },
  { value: "7d", label: "Last 7 days" },
  { value: "14d", label: "Last 14 days" },
  { value: "30d", label: "Last 30 days" },
];

const PAGE_SIZES = [20, 50];

const POPULAR_SEARCHES = [
  "Software Engineer",
  "Backend Engineer",
  "Data Analyst",
  "DevOps",
  "Marketing",
  "Sales",
  "Designer",
  "Customer Support",
];

function sinceToIso(preset: string): string {
  if (!preset) return "";
  const now = Date.now();
  const day = 24 * 3600 * 1000;
  if (preset === "24h") return new Date(now - day).toISOString();
  if (preset === "3d") return new Date(now - 3 * day).toISOString();
  if (preset === "7d") return new Date(now - 7 * day).toISOString();
  if (preset === "14d") return new Date(now - 14 * day).toISOString();
  if (preset === "30d") return new Date(now - 30 * day).toISOString();
  return "";
}

function sinceLabel(value: string): string {
  return SINCE_OPTIONS.find((o) => o.value === value)?.label ?? value;
}

type Mode = "" | "remote" | "hybrid" | "onsite";
type Sort = "newest" | "oldest";
const ENVIRONMENTS: { value: Mode; label: string }[] = [
  { value: "", label: "All environments" },
  { value: "remote", label: "Remote" },
  { value: "hybrid", label: "Hybrid" },
  { value: "onsite", label: "On-site" },
];

function modeLabel(m: Mode): string {
  return m === "" ? "All environments" : (ENVIRONMENTS.find((e) => e.value === m)?.label ?? m);
}

/** Display work mode for a row (same heuristic the API filter uses). */
function jobMode(job: Job): "Remote" | "Hybrid" | "On-site" {
  if (job.is_remote) return "Remote";
  const hay = `${job.title} ${job.location || ""}`.toLowerCase();
  if (hay.includes("hybrid")) return "Hybrid";
  return "On-site";
}

interface Filters {
  q: string;
  loc: string;
  ats: string;
  company: string;
  country: string;
  since: string;
  remoteOnly: boolean;
  mode: Mode;
  sort: Sort;
  pageSize: number;
  page: number;
}

const EMPTY: Filters = {
  q: "",
  loc: "",
  ats: "",
  company: "",
  country: "",
  since: "",
  remoteOnly: false,
  mode: "",
  sort: "newest",
  pageSize: 20,
  page: 0,
};

function readMode(v: string | null): Mode {
  return v === "remote" || v === "hybrid" || v === "onsite" ? v : "";
}

function readSort(v: string | null): Sort {
  return v === "oldest" ? "oldest" : "newest";
}

function readUrlParams(sp: URLSearchParams): Filters | null {
  const keys = ["q", "loc", "ats", "company", "country", "since", "remote", "mode", "sort", "size", "page"];
  const hasAny = keys.some((k) => sp.get(k) !== null);
  if (!hasAny) return null;
  const page = Math.max(0, parseInt(sp.get("page") || "0", 10) || 0);
  const size = parseInt(sp.get("size") || "20", 10);
  return {
    q: sp.get("q") || "",
    loc: sp.get("loc") || "",
    ats: sp.get("ats") || "",
    company: sp.get("company") || "",
    country: sp.get("country") || "",
    since: sp.get("since") || "",
    remoteOnly: sp.get("remote") === "1",
    mode: readMode(sp.get("mode")),
    sort: readSort(sp.get("sort")),
    pageSize: PAGE_SIZES.includes(size) ? size : 20,
    page,
  };
}

function readStored(): Filters | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as Partial<Filters>;
    return {
      ...EMPTY,
      ...parsed,
      mode: readMode((parsed.mode as string) ?? ""),
      sort: readSort((parsed.sort as string) ?? ""),
      pageSize: PAGE_SIZES.includes(Number(parsed.pageSize)) ? Number(parsed.pageSize) : 20,
      page: Math.max(0, Number(parsed.page) || 0),
    };
  } catch {
    return null;
  }
}

function FilterGroup({
  title,
  children,
  defaultOpen = true,
}: {
  title: string;
  children: React.ReactNode;
  defaultOpen?: boolean;
}) {
  return (
    <details open={defaultOpen} className="border-b border-border/60 pb-4 last:border-0 last:pb-0">
      <summary className="cursor-pointer list-none font-mono text-[11px] uppercase tracking-widest text-text-muted hover:text-text [&::-webkit-details-marker]:hidden">
        <span className="flex items-center justify-between">
          {title}
          <span aria-hidden>＋</span>
        </span>
      </summary>
      <div className="mt-3">{children}</div>
    </details>
  );
}

export function BrowseJobs() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { me } = useAuth();

  const [filters, setFilters] = useState<Filters>(() => readUrlParams(searchParams) || EMPTY);
  const [hydrated, setHydrated] = useState(false);
  const [filtersOpen, setFiltersOpen] = useState(false);
  const [companyOptions, setCompanyOptions] = useState<string[]>([]);
  const [countryOptions, setCountryOptions] = useState<string[]>([]);
  const [atsOptions, setAtsOptions] = useState<string[]>(ATS_ORDER);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [topCompanies, setTopCompanies] = useState<PublicCompany[]>([]);
  const [saved, setSaved] = useState<string[]>([]);
  const [hidden, setHidden] = useState<string[]>([]);
  const [savedOnly, setSavedOnly] = useState(false);
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
    setSaved(loadSaved());
    setHidden(loadHidden());
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
    if (filters.loc) sp.set("loc", filters.loc);
    if (filters.ats) sp.set("ats", filters.ats);
    if (filters.company) sp.set("company", filters.company);
    if (filters.country) sp.set("country", filters.country);
    if (filters.since) sp.set("since", filters.since);
    if (filters.remoteOnly) sp.set("remote", "1");
    if (filters.mode) sp.set("mode", filters.mode);
    if (filters.sort !== "newest") sp.set("sort", filters.sort);
    if (filters.pageSize !== 20) sp.set("size", String(filters.pageSize));
    if (filters.page > 0) sp.set("page", String(filters.page));
    const qs = sp.toString();
    router.replace(`${pathname}${qs ? `?${qs}` : ""}`, { scroll: false });
  }, [filters, hydrated, pathname, router]);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await api.publicJobs({
        q: filters.q || undefined,
        loc: filters.loc || undefined,
        ats: filters.ats || undefined,
        company: filters.company || undefined,
        country: filters.country || undefined,
        since: sinceToIso(filters.since) || undefined,
        remote_only: filters.remoteOnly || undefined,
        mode: filters.mode || undefined,
        sort: filters.sort,
        limit: filters.pageSize,
        offset: filters.page * filters.pageSize,
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

  const pageCount = useMemo(
    () => Math.max(1, Math.ceil(total / filters.pageSize)),
    [total, filters.pageSize],
  );
  const companyDomains = useMemo(() => domainsFromJobs(jobs), [jobs]);

  const visibleJobs = useMemo(() => {
    let list = filterHidden(jobs, hidden);
    if (savedOnly) {
      const set = new Set(saved);
      list = list.filter((j) => set.has(j.id));
    }
    return list;
  }, [jobs, hidden, saved, savedOnly]);

  function update(patch: Partial<Filters>, resetPage = true) {
    setFilters((f) => ({ ...f, ...patch, page: resetPage ? 0 : (patch.page ?? f.page) }));
  }

  function onToggleSave(id: string) {
    setSaved((cur) => toggleSaved(cur, id));
  }

  function onHide(id: string) {
    setHidden((cur) => hideJob(cur, id));
  }

  const chips: { key: string; label: string; clear: () => void }[] = [];
  if (filters.q) chips.push({ key: "q", label: `“${filters.q}”`, clear: () => update({ q: "" }) });
  if (filters.loc)
    chips.push({ key: "loc", label: `Location: ${filters.loc}`, clear: () => update({ loc: "" }) });
  if (filters.company)
    chips.push({ key: "company", label: filters.company, clear: () => update({ company: "" }) });
  if (filters.country)
    chips.push({ key: "country", label: filters.country, clear: () => update({ country: "" }) });
  if (filters.ats)
    chips.push({ key: "ats", label: atsLabel(filters.ats), clear: () => update({ ats: "" }) });
  if (filters.mode)
    chips.push({ key: "mode", label: modeLabel(filters.mode), clear: () => update({ mode: "" }) });
  if (filters.since)
    chips.push({ key: "since", label: sinceLabel(filters.since), clear: () => update({ since: "" }) });
  if (filters.remoteOnly)
    chips.push({ key: "remote", label: "Remote only", clear: () => update({ remoteOnly: false }) });

  const hasActiveFilters = chips.length > 0;

  function clearAll() {
    setFilters((f) => ({ ...EMPTY, sort: f.sort, pageSize: f.pageSize }));
    setSavedOnly(false);
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch {}
  }

  const sidebar = (
    <div className="space-y-4">
      <FilterGroup title="Date posted">
        <div className="flex flex-wrap gap-1.5">
          {SINCE_OPTIONS.map((o) => (
            <button
              key={o.value || "any"}
              type="button"
              onClick={() => update({ since: o.value })}
              className={`rounded-full border px-3 py-1.5 text-xs font-medium transition-colors ${
                filters.since === o.value
                  ? "border-primary bg-primary/15 text-text"
                  : "border-border bg-elevated text-text-secondary hover:text-text"
              }`}
            >
              {filters.since === o.value ? "✓ " : ""}
              {o.label}
            </button>
          ))}
        </div>
      </FilterGroup>

      <FilterGroup title="Company">
        <CompanySelect
          companies={companyOptions}
          value={filters.company}
          onChange={(v) => update({ company: v })}
          domains={companyDomains}
        />
      </FilterGroup>

      <FilterGroup title="Location">
        <select
          value={filters.country}
          onChange={(e) => update({ country: e.target.value })}
          className="search-input w-full"
          aria-label="Country"
        >
          <option value="">All countries</option>
          {countryOptions.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </FilterGroup>

      <FilterGroup title="Source">
        <select
          value={filters.ats}
          onChange={(e) => update({ ats: e.target.value })}
          className="search-input w-full"
          aria-label="Job source"
        >
          <option value="">All sources</option>
          {atsOptions.map((a) => (
            <option key={a} value={a}>
              {atsLabel(a)}
            </option>
          ))}
        </select>
      </FilterGroup>

      <FilterGroup title="My jobs" defaultOpen={false}>
        <div className="space-y-2 text-sm">
          <button
            type="button"
            onClick={() => setSavedOnly((v) => !v)}
            className={`w-full rounded-lg border px-3 py-1.5 text-left text-xs font-medium transition-colors ${
              savedOnly
                ? "border-primary bg-primary/10 text-text"
                : "border-border text-text-secondary hover:text-text"
            }`}
          >
            {savedOnly ? "✓ " : ""}Show saved only ({saved.length})
          </button>
          {hidden.length > 0 && (
            <button
              type="button"
              onClick={() => setHidden(unhideAll())}
              className="w-full rounded-lg border border-border px-3 py-1.5 text-left text-xs text-text-secondary hover:text-text"
            >
              Unhide {hidden.length} hidden job{hidden.length === 1 ? "" : "s"}
            </button>
          )}
          {saved.length === 0 && hidden.length === 0 && (
            <p className="text-xs text-text-muted">
              Tap Save on any job to build your shortlist here.
            </p>
          )}
        </div>
      </FilterGroup>

      {hasActiveFilters && (
        <button type="button" onClick={clearAll} className="btn-ghost w-full">
          Clear all filters
        </button>
      )}
    </div>
  );

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="sticky top-0 z-30 border-b-2 border-border bg-surface/95 backdrop-blur">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-3 px-4 py-3 sm:px-6">
          <Link href="/" className="flex items-center gap-2.5">
            <RadarMark />
            <span className="leading-tight">
              <span className="block font-display text-base font-bold tracking-[0.14em]">
                JOBQUEST
              </span>
              <span className="block font-mono text-[10px] uppercase tracking-widest text-text-muted">
                {total.toLocaleString()} jobs · {companyOptions.length} companies
              </span>
            </span>
          </Link>
          <div className="flex-1" />
          <div className="flex items-center gap-2">
            {me && !me.anonymous ? (
              <Link href="/dashboard" className="btn-ghost hidden sm:inline-flex">
                Dashboard
              </Link>
            ) : (
              <Link href="/login" className="btn-ghost hidden sm:inline-flex">
                Sign in
              </Link>
            )}
            <Link href={me && !me.anonymous ? "/billing" : "/register"} className="btn-primary">
              Get job alerts
            </Link>
          </div>
        </div>
      </header>

      {/* Alerts strip */}
      <div className="border-b border-border bg-primary/5">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-2 px-4 py-2.5 sm:px-6">
          <p className="text-[13px] text-text-secondary">
            <span className="font-semibold text-text">Never miss a match.</span> Register or log
            in, set your preferences once, and get new matching jobs on Telegram.
          </p>
          <div className="flex gap-2 text-xs">
            <Link href="/register" className="font-semibold text-primary hover:underline">
              Create free account →
            </Link>
            <Link href="/pricing" className="text-text-secondary hover:text-text">
              See alerts pricing
            </Link>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-7xl px-4 sm:px-6">
        {/* Search panel */}
        <section className="mt-6 rounded-2xl border-2 border-border bg-surface p-4 shadow-offset sm:p-5">
          <div className="grid gap-2.5 md:grid-cols-2">
            <input
              value={filters.q}
              onChange={(e) => update({ q: e.target.value })}
              placeholder="Job title or keyword"
              aria-label="Job title or keyword"
              className="search-input w-full !py-3 text-[15px]"
            />
            <input
              value={filters.loc}
              onChange={(e) => update({ loc: e.target.value })}
              placeholder="Location"
              aria-label="Location"
              className="search-input w-full !py-3 text-[15px]"
            />
          </div>
          <div className="mt-3 flex flex-wrap items-center gap-1.5">
            {ENVIRONMENTS.map((env) => (
              <button
                key={env.value || "all"}
                type="button"
                onClick={() => update({ mode: env.value })}
                className={`rounded-full border px-3 py-1.5 text-xs font-medium transition-colors ${
                  filters.mode === env.value
                    ? "border-primary bg-primary/15 text-text"
                    : "border-border bg-elevated text-text-secondary hover:text-text"
                }`}
              >
                {filters.mode === env.value ? "✓ " : ""}
                {env.label}
              </button>
            ))}
            <span className="mx-1 h-4 w-px bg-border" aria-hidden />
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
              onClick={() => setFiltersOpen((v) => !v)}
              className="rounded-full border border-border bg-elevated px-3 py-1.5 text-xs font-medium text-text-secondary hover:text-text lg:hidden"
            >
              {filtersOpen ? "Hide filters" : `Filters${hasActiveFilters ? ` (${chips.length})` : ""}`}
            </button>
          </div>
        </section>

        {/* Body: sidebar + feed */}
        <div className="mt-5 flex items-start gap-5 pb-4">
          <aside className="sticky top-24 hidden w-64 shrink-0 rounded-xl border-2 border-border bg-surface p-4 shadow-offset-sm lg:block">
            <h2 className="mb-3 font-fraunces text-base font-bold text-text">Filters</h2>
            {sidebar}
          </aside>

          <div className="min-w-0 flex-1">
            {filtersOpen && (
              <div className="mb-4 rounded-xl border-2 border-border bg-surface p-4 lg:hidden">
                <h2 className="mb-3 font-fraunces text-base font-bold text-text">Filters</h2>
                {sidebar}
              </div>
            )}

            {/* Feed header */}
            <div className="mb-2 flex flex-wrap items-baseline justify-between gap-2">
              <h1 className="font-fraunces text-lg font-bold text-text">
                {savedOnly ? "Your saved jobs" : "Latest jobs"}
                <span className="ml-2 font-mono text-xs font-normal text-text-muted">
                  {total.toLocaleString()} jobs · {companyOptions.length} companies
                </span>
              </h1>
              <label className="flex items-center gap-1.5 text-xs text-text-muted">
                Sort by:
                <select
                  value={filters.sort}
                  onChange={(e) => update({ sort: e.target.value as Sort })}
                  className="search-input !py-1 !text-xs"
                  aria-label="Sort jobs"
                >
                  <option value="newest">Newest</option>
                  <option value="oldest">Oldest</option>
                </select>
              </label>
            </div>

            {chips.length > 0 && (
              <div className="mb-3 flex flex-wrap items-center gap-1.5">
                {chips.map((chip) => (
                  <button
                    key={chip.key}
                    type="button"
                    onClick={chip.clear}
                    title="Remove filter"
                    className="rounded-full border border-primary/50 bg-primary/10 px-2.5 py-1 text-xs font-medium text-text hover:bg-primary/20"
                  >
                    {chip.label} ✕
                  </button>
                ))}
                <button
                  type="button"
                  onClick={clearAll}
                  className="text-xs text-text-muted hover:text-text"
                >
                  Clear all
                </button>
              </div>
            )}

            {/* Job rows */}
            <div>
              {loading ? (
                <RadarLoading label="Scanning jobs…" />
              ) : visibleJobs.length === 0 ? (
                <div className="rounded-xl border-2 border-border bg-surface p-10 text-center text-sm text-text-muted shadow-offset-sm">
                  {savedOnly ? (
                    <>No saved jobs on this page. Tap Save on any job to shortlist it.</>
                  ) : (
                    <>
                      No jobs found. Try widening your filters — or{" "}
                      <Link href="/register" className="font-semibold text-primary hover:underline">
                        register for alerts
                      </Link>{" "}
                      so the next match finds you.
                    </>
                  )}
                </div>
              ) : (
                <div className="overflow-hidden rounded-xl border-2 border-border bg-surface shadow-offset-sm">
                  <div className="divide-y divide-border/60">
                    {visibleJobs.map((job) => {
                      const isSaved = saved.includes(job.id);
                      const mode = jobMode(job);
                      return (
                        <article key={job.id} className="p-4 transition-colors hover:bg-elevated/40 sm:p-5">
                          <div className="flex items-center gap-2 font-mono text-[11px] text-text-muted">
                            <span>{timeAgo(job.first_seen_at)}</span>
                            <span aria-hidden>·</span>
                            <button
                              type="button"
                              onClick={() => onToggleSave(job.id)}
                              className={`font-semibold hover:text-text ${isSaved ? "text-primary" : ""}`}
                            >
                              {isSaved ? "★ Saved" : "Save"}
                            </button>
                            <span aria-hidden>·</span>
                            <button
                              type="button"
                              onClick={() => onHide(job.id)}
                              className="hover:text-text"
                            >
                              Hide
                            </button>
                          </div>

                          <div className="mt-1.5 flex items-start gap-3">
                            <CompanyLogo name={job.company} domain={job.domain} size="md" />
                            <div className="min-w-0">
                              <Link
                                href={`/browse/${job.id}`}
                                className="font-fraunces text-lg font-bold leading-snug text-text hover:text-primary"
                              >
                                {job.title}
                              </Link>
                              <p className="mt-0.5 text-sm text-text-secondary">
                                {job.location || "Remote / unspecified"}
                              </p>
                            </div>
                          </div>

                          <div className="mt-2 flex flex-wrap items-center gap-1.5">
                            <span
                              className={`rounded-full border px-2.5 py-0.5 font-mono text-[11px] font-semibold ${
                                mode === "Remote"
                                  ? "border-success/40 bg-success/10 text-success"
                                  : "border-border bg-elevated text-text-secondary"
                              }`}
                            >
                              {mode}
                            </span>
                            {job.countries
                              .filter(Boolean)
                              .slice(0, 4)
                              .map((c) => (
                                <span
                                  key={c}
                                  className="rounded-full border border-border bg-elevated px-2.5 py-0.5 font-mono text-[11px] text-text-secondary"
                                >
                                  {c}
                                </span>
                              ))}
                            {job.is_remote && mode !== "Remote" && (
                              <span className="rounded-full border border-border bg-elevated px-2.5 py-0.5 font-mono text-[11px] text-text-secondary">
                                Remote
                              </span>
                            )}
                          </div>

                          <p className="mt-2 text-[13px] text-text-secondary">
                            <span className="font-semibold text-text">{job.company}</span>
                            <span className="text-text-muted"> · via {atsLabel(job.ats_type)}</span>
                          </p>

                          <div className="mt-2 flex items-center gap-3 text-[13px]">
                            {job.url ? (
                              <a
                                href={job.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="font-semibold text-primary hover:underline"
                              >
                                Apply →
                              </a>
                            ) : (
                              <span className="text-text-muted">No apply link</span>
                            )}
                            <Link
                              href={`/browse/${job.id}`}
                              className="text-text-secondary hover:text-text"
                            >
                              Details
                            </Link>
                          </div>
                        </article>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>

            {/* Pagination */}
            <div className="mt-5 flex flex-wrap items-center justify-between gap-2 text-sm text-text-muted">
              <span>
                Page {filters.page + 1} of {pageCount}
              </span>
              <div className="flex items-center gap-2">
                <select
                  value={filters.pageSize}
                  onChange={(e) => update({ pageSize: Number(e.target.value) })}
                  className="search-input !py-1 !text-xs"
                  aria-label="Jobs per page"
                >
                  {PAGE_SIZES.map((s) => (
                    <option key={s} value={s}>
                      {s}/page
                    </option>
                  ))}
                </select>
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

            {/* Bottom alerts CTA */}
            <section className="mt-6 flex flex-wrap items-center justify-between gap-4 rounded-xl border-2 border-border bg-surface p-5 shadow-offset-sm">
              <div>
                <h2 className="font-fraunces text-lg font-bold text-text">
                  Get matching jobs on Telegram.
                </h2>
                <p className="mt-1 text-sm text-text-secondary">
                  Register or log in, set your preferences once — new matches find you.
                </p>
              </div>
              <div className="flex gap-2">
                <Link href="/login" className="btn-ghost">
                  Log in
                </Link>
                <Link href="/register" className="btn-primary">
                  Register for alerts
                </Link>
              </div>
            </section>

            {/* SEO footer */}
            <footer className="mt-8 grid gap-6 border-t-2 border-border pb-10 pt-6 text-sm sm:grid-cols-2 lg:grid-cols-4">
              <div>
                <h3 className="font-mono text-[11px] uppercase tracking-widest text-text-muted">
                  Popular searches
                </h3>
                <ul className="mt-2 space-y-1.5">
                  {POPULAR_SEARCHES.map((s) => (
                    <li key={s}>
                      <button
                        type="button"
                        onClick={() => update({ q: s })}
                        className="text-text-secondary hover:text-primary hover:underline"
                      >
                        {s} jobs
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h3 className="font-mono text-[11px] uppercase tracking-widest text-text-muted">
                  By country
                </h3>
                <ul className="mt-2 space-y-1.5">
                  {countryOptions.slice(0, 8).map((c) => (
                    <li key={c}>
                      <button
                        type="button"
                        onClick={() => update({ country: c })}
                        className="text-text-secondary hover:text-primary hover:underline"
                      >
                        Jobs in {c}
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h3 className="font-mono text-[11px] uppercase tracking-widest text-text-muted">
                  Work your way
                </h3>
                <ul className="mt-2 space-y-1.5">
                  <li>
                    <button
                      type="button"
                      onClick={() => update({ mode: "remote" })}
                      className="text-text-secondary hover:text-primary hover:underline"
                    >
                      Remote jobs
                    </button>
                  </li>
                  <li>
                    <button
                      type="button"
                      onClick={() => update({ mode: "hybrid" })}
                      className="text-text-secondary hover:text-primary hover:underline"
                    >
                      Hybrid jobs
                    </button>
                  </li>
                  <li>
                    <button
                      type="button"
                      onClick={() => update({ mode: "onsite" })}
                      className="text-text-secondary hover:text-primary hover:underline"
                    >
                      On-site jobs
                    </button>
                  </li>
                  <li>
                    <button
                      type="button"
                      onClick={() => update({ since: "24h" })}
                      className="text-text-secondary hover:text-primary hover:underline"
                    >
                      Posted in the last 24 hours
                    </button>
                  </li>
                </ul>
              </div>
              <div>
                <h3 className="font-mono text-[11px] uppercase tracking-widest text-text-muted">
                  Top companies
                </h3>
                <ul className="mt-2 space-y-1.5">
                  {topCompanies.slice(0, 8).map((c) => (
                    <li key={c.company_name}>
                      <button
                        type="button"
                        onClick={() => update({ company: c.company_name })}
                        className="text-text-secondary hover:text-primary hover:underline"
                      >
                        {c.company_name} jobs
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            </footer>
          </div>
        </div>
      </div>
    </div>
  );
}
