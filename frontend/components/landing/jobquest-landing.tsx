"use client";

import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";
import styles from "./jobquest-landing.module.css";
import { api } from "@/lib/api";
import { ATS_ORDER, atsLabel, countryName, timeAgo } from "@/lib/format";
import {
  filterHidden,
  hideJob,
  loadHidden,
  loadSaved,
  splitCsvParam,
  toggleSaved,
  unhideAll,
} from "@/lib/job-store";
import type { Job, PublicCompany } from "@/lib/types";

/* ------------------------------ icons ------------------------------ */

function SearchIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden>
      <circle cx="9" cy="9" r="6" stroke="currentColor" strokeWidth="1.8" />
      <path d="M13.5 13.5L17 17" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function PinIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" aria-hidden>
      <path
        d="M10 17.5S4.5 11.6 4.5 7.75a5.5 5.5 0 0111 0C15.5 11.6 10 17.5 10 17.5z"
        stroke="currentColor"
        strokeWidth="1.8"
      />
      <circle cx="10" cy="7.75" r="2" stroke="currentColor" strokeWidth="1.8" />
    </svg>
  );
}

function BookmarkIcon({ filled = false }: { filled?: boolean }) {
  return (
    <svg width="17" height="17" viewBox="0 0 18 18" fill="none" aria-hidden>
      <path
        d="M5 2.5h8a.5.5 0 01.5.5v12.1a.3.3 0 01-.48.24L9 12.37l-4.02 2.97a.3.3 0 01-.48-.24V3a.5.5 0 01.5-.5z"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
        fill={filled ? "currentColor" : "none"}
      />
    </svg>
  );
}

function SunIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 20 20" fill="none" aria-hidden>
      <circle cx="10" cy="10" r="4" stroke="currentColor" strokeWidth="1.7" />
      <path
        d="M10 1.8v2M10 16.2v2M1.8 10h2M16.2 10h2M4.2 4.2l1.4 1.4M14.4 14.4l1.4 1.4M15.8 4.2l-1.4 1.4M5.6 14.4l-1.4 1.4"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinecap="round"
      />
    </svg>
  );
}

function CrownIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 20 20" fill="none" aria-hidden>
      <path
        d="M2.5 7l3.5 3 4-5.5L14 10l3.5-3L16 15.5H4L2.5 7z"
        stroke="#FBBF24"
        strokeWidth="1.7"
        strokeLinejoin="round"
      />
      <path d="M4 17.5h12" stroke="#FBBF24" strokeWidth="1.7" strokeLinecap="round" />
    </svg>
  );
}

function SparkleIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden>
      <path
        d="M8 1.5l1.4 4.1 4.1 1.4-4.1 1.4L8 12.5l-1.4-4.1-4.1-1.4 4.1-1.4L8 1.5z"
        stroke="currentColor"
        strokeWidth="1.4"
        strokeLinejoin="round"
      />
      <path d="M12.5 11l.7 2 2 .7-2 .7-.7 2-.7-2-2-.7 2-.7.7-2z" fill="currentColor" />
    </svg>
  );
}

function LogoMark() {
  return (
    <svg width="40" height="40" viewBox="0 0 40 40" fill="none" aria-hidden>
      <circle cx="20" cy="20" r="18" stroke="#0b1b33" strokeWidth="2.4" />
      <circle cx="20" cy="20" r="12.5" stroke="#22c55e" strokeWidth="2.4" />
      <circle cx="20" cy="20" r="7" stroke="#3b82f6" strokeWidth="2.4" />
      <circle cx="20" cy="20" r="2.6" fill="#0b1b33" />
      <path d="M20 2a18 18 0 0112.7 5.3" stroke="#22c55e" strokeWidth="2.4" strokeLinecap="round" />
    </svg>
  );
}

/* --------------------------- brand logos --------------------------- */

function BrandLogo({ name, domain }: { name: string; domain?: string | null }) {
  const [failed, setFailed] = useState(false);
  const src =
    domain && !failed
      ? `https://www.google.com/s2/favicons?domain=${encodeURIComponent(domain)}&sz=128`
      : null;
  if (!src) {
    return (
      <span className={styles.jobLogo} style={{ background: "#eef3f9", color: "#24406b" }} aria-hidden>
        {(name.trim()[0] || "?").toUpperCase()}
      </span>
    );
  }
  return (
    <span className={styles.jobLogo} aria-hidden>
      <img src={src} alt="" loading="lazy" onError={() => setFailed(true)} />
    </span>
  );
}

/* ------------------------------ options ------------------------------ */

const PAGE_SIZE = 6;
const FILTERS_KEY = "jobquest:landing-filters:v1";

const SINCE_OPTIONS = [
  { value: "", label: "Any time" },
  { value: "24h", label: "Last 24 hours" },
  { value: "3d", label: "Last 3 days" },
  { value: "7d", label: "Last 7 days" },
  { value: "14d", label: "Last 14 days" },
  { value: "30d", label: "Last 30 days" },
];

const POPULAR_COUNTRY_CODES = ["IN", "US", "DE", "GB", "CA", "AU", "AE", "SG"];

const BASE_COMPANIES = ["Google", "Amazon", "Adobe", "Stripe"];

const FALLBACK_SOURCES = [
  "greenhouse",
  "lever",
  "ashby",
  "workday",
  "oracle",
  "icims",
  "successfactors",
  "phenom",
];

const TRY_TAGS = ["Software Engineer", "Remote", "Internship", "Python", "Product Manager", "DevOps"];

const TRENDING = [
  "Software Engineer",
  "Remote Jobs",
  "Internships 2026",
  "Product Manager",
  "DevOps",
  "Data Analyst",
];

/** Skills detected in posting text for the pill row (word-boundary matched). */
const SKILL_PATTERNS = [
  "JavaScript",
  "TypeScript",
  "Node.js",
  "React",
  "Python",
  "Java",
  "Go",
  "C++",
  "SQL",
  "PostgreSQL",
  "MySQL",
  "AWS",
  "Azure",
  "Docker",
  "Kubernetes",
  "Terraform",
  "Kafka",
  "System Design",
  "Microservices",
  "Distributed Systems",
  "Machine Learning",
  "REST API",
  "GraphQL",
  "CI/CD",
  "DevOps",
  "Cloud",
  "Linux",
  "Git",
  "Figma",
  "Agile",
  "Scrum",
];

function escapeRegExp(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function detectSkills(text: string): string[] {
  const found: string[] = [];
  for (const s of SKILL_PATTERNS) {
    if (new RegExp(`(?<!\\w)${escapeRegExp(s)}(?!\\w)`, "i").test(text)) found.push(s);
  }
  return found
    .filter((s) => !found.some((o) => o !== s && o.toLowerCase().includes(s.toLowerCase())))
    .slice(0, 5);
}

function jobMode(job: Job): string {
  if (job.is_remote) return "Remote";
  if (/hybrid/i.test(`${job.title} ${job.location || ""}`)) return "Hybrid";
  return "On-site";
}

function isoDaysAgo(days: number): string {
  return new Date(Date.now() - days * 24 * 3600 * 1000).toISOString();
}

function sinceToIso(preset: string): string {
  if (preset === "24h") return isoDaysAgo(1);
  if (preset === "3d") return isoDaysAgo(3);
  if (preset === "7d") return isoDaysAgo(7);
  if (preset === "14d") return isoDaysAgo(14);
  if (preset === "30d") return isoDaysAgo(30);
  return "";
}

type Tab = "all" | "saved";
type Sort = "relevant" | "newest" | "oldest";

interface LandingFilters {
  terms: string[];
  locText: string;
  countries: string[];
  sources: string[];
  companies: string[];
  sincePreset: string;
  sort: Sort;
  newOnly: boolean;
}

const DEFAULT_FILTERS: LandingFilters = {
  terms: [],
  locText: "",
  countries: [],
  sources: [],
  companies: [],
  sincePreset: "",
  sort: "relevant",
  newOnly: false,
};

function loadStoredFilters(): LandingFilters {
  if (typeof window === "undefined") return DEFAULT_FILTERS;
  try {
    const raw = localStorage.getItem(FILTERS_KEY);
    if (!raw) return DEFAULT_FILTERS;
    const p = JSON.parse(raw) as Partial<LandingFilters>;
    const strArr = (v: unknown) =>
      Array.isArray(v) ? v.filter((x): x is string => typeof x === "string") : [];
    const dedupe = (items: string[]) => [...new Set(items)];
    return {
      terms: strArr(p.terms),
      locText: typeof p.locText === "string" ? p.locText : "",
      countries: dedupe(
        strArr(p.countries).map((c) => c.trim().toUpperCase()).filter(Boolean),
      ),
      sources: dedupe(strArr(p.sources)),
      companies: dedupe(strArr(p.companies).map((c) => c.trim()).filter(Boolean)),
      sincePreset: typeof p.sincePreset === "string" ? p.sincePreset : "",
      sort: p.sort === "newest" || p.sort === "oldest" ? p.sort : "relevant",
      newOnly: p.newOnly === true,
    };
  } catch {
    return DEFAULT_FILTERS;
  }
}

function Check({
  label,
  checked,
  onChange,
}: {
  label: string;
  checked: boolean;
  onChange: (next: boolean) => void;
}) {
  return (
    <label className={styles.checkRow}>
      <input type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)} />
      {label}
    </label>
  );
}

function toggleInArray(list: string[], value: string): string[] {
  return list.includes(value) ? list.filter((v) => v !== value) : [...list, value];
}

/* ------------------------------ page ------------------------------ */

export function JobQuestLanding() {
  const [f, setF] = useState<LandingFilters>(loadStoredFilters);
  const [kwDraft, setKwDraft] = useState("");
  const [tab, setTab] = useState<Tab>("all");
  const [page, setPage] = useState(0);

  const [jobs, setJobs] = useState<Job[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [weekCount, setWeekCount] = useState<number | null>(null);
  const [extraCompanies, setExtraCompanies] = useState<PublicCompany[]>([]);
  const [allCountries, setAllCountries] = useState<string[]>([]);
  const [sourceOptions, setSourceOptions] = useState<string[]>(FALLBACK_SOURCES);

  const [saved, setSaved] = useState<string[]>([]);
  const [hidden, setHidden] = useState<string[]>([]);
  const [detailCache, setDetailCache] = useState<Record<string, Job>>({});

  const [metaLoaded, setMetaLoaded] = useState(false);
  const [companyQuery, setCompanyQuery] = useState("");
  const [locationQuery, setLocationQuery] = useState("");
  const [locDropOpen, setLocDropOpen] = useState(false);
  const [compDropOpen, setCompDropOpen] = useState(false);
  const [moreSources, setMoreSources] = useState(false);
  const locDropRef = useRef<HTMLDivElement>(null);
  const compDropRef = useRef<HTMLDivElement>(null);

  const fetchingRef = useRef<Set<string>>(new Set());

  useEffect(() => {
    function onDocClick(e: MouseEvent) {
      const target = e.target as Node;
      if (locDropRef.current && !locDropRef.current.contains(target)) {
        setLocDropOpen(false);
      }
      if (compDropRef.current && !compDropRef.current.contains(target)) {
        setCompDropOpen(false);
      }
    }
    document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, []);

  // Filters persist across refresh; only Reset clears them.
  useEffect(() => {
    try {
      localStorage.setItem(FILTERS_KEY, JSON.stringify(f));
    } catch {}
  }, [f]);

  useEffect(() => {
    setSaved(loadSaved());
    setHidden(loadHidden());
    api
      .publicCompanies()
      .then((res) =>
        setExtraCompanies(res.companies.filter((c) => !BASE_COMPANIES.includes(c.company_name))),
      )
      .catch(() => {});
    api
      .jobFilters()
      .then((res) => {
        if (res.countries.length) setAllCountries(res.countries);
        setMetaLoaded(true);
        if (res.ats_types.length) {
          const order = new Map(ATS_ORDER.map((a, i) => [a, i]));
          setSourceOptions(
            [...res.ats_types].sort((a, b) => (order.get(a) ?? 99) - (order.get(b) ?? 99)),
          );
        }
      })
      .catch(() => {});
    api
      .publicJobs({ since: isoDaysAgo(7), limit: 1 })
      .then((res) => setWeekCount(res.total))
      .catch(() => setWeekCount(null));
  }, []);

  // Warm the detail cache for saved ids so Recommended can rank on them.
  useEffect(() => {
    const missing = saved
      .filter((id) => !detailCache[id] && !fetchingRef.current.has(id))
      .slice(0, 60);
    if (!missing.length) return;
    missing.forEach((id) => fetchingRef.current.add(id));
    let cancelled = false;
    Promise.all(
      missing.map((id) => api.publicJob(id).then((job) => ({ id, job })).catch(() => null)),
    ).then((rows) => {
      if (cancelled || !rows.some(Boolean)) return;
      setDetailCache((prev) => {
        const next = { ...prev };
        for (const row of rows) if (row) next[row.id] = row.job;
        return next;
      });
    });
    return () => {
      cancelled = true;
    };
  }, [saved, detailCache]);

  const filterParams = useMemo(
    () => ({
      // Comma-joined: the backend splits keywords on commas only, so each
      // chip stays one term and terms union (spaces inside a chip are kept).
      q: f.terms.join(",") || undefined,
      loc: f.locText.trim() || undefined,
      companies: splitCsvParam(f.companies),
      countries: splitCsvParam(f.countries),
      sources: splitCsvParam(f.sources),
      since: (f.newOnly ? isoDaysAgo(1) : sinceToIso(f.sincePreset)) || undefined,
      sort: f.sort === "relevant" ? undefined : f.sort,
    }),
    [f],
  );

  const filterKey = useMemo(() => JSON.stringify(filterParams), [filterParams]);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    async function run() {
      try {
        if (tab === "saved") {
          const ids = saved.filter((id) => !hidden.includes(id));
          const rows = await Promise.all(
            ids.map((id) =>
              detailCache[id]
                ? Promise.resolve(detailCache[id])
                : api
                    .publicJob(id)
                    .then((job) => {
                      setDetailCache((prev) => ({ ...prev, [id]: job }));
                      return job;
                    })
                    .catch(() => null),
            ),
          );
          if (cancelled) return;
          const list = rows.filter((j): j is Job => j !== null);
          setJobs(list);
          setTotal(list.length);
        } else {
          const res = await api.publicJobs({
            ...filterParams,
            limit: PAGE_SIZE,
            offset: page * PAGE_SIZE,
          });
          if (cancelled) return;
          setJobs(filterHidden(res.jobs, hidden));
          setTotal(res.total);
        }
      } catch (e) {
        console.error(e);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    const t = setTimeout(run, 300);
    return () => {
      cancelled = true;
      clearTimeout(t);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filterKey, tab, page, saved, hidden]);

  const clientPaged = tab !== "all";
  const visibleJobs = clientPaged ? jobs.slice(page * PAGE_SIZE, page * PAGE_SIZE + PAGE_SIZE) : jobs;
  const pageCount = Math.max(1, Math.ceil(total / PAGE_SIZE));

  function patch(p: Partial<LandingFilters>) {
    setPage(0);
    setF((prev) => ({ ...prev, ...p }));
  }

  function toggleMulti(key: "countries" | "sources" | "companies", value: string) {
    patch({ [key]: toggleInArray(f[key], value) } as Partial<LandingFilters>);
  }

  function commitDraft() {
    // Comma-separated keywords only — spaces stay inside a term ("Software
    // Engineer" is one keyword, matching the backend split).
    const terms = kwDraft
      .split(",")
      .map((t) => t.trim())
      .filter(Boolean)
      .filter((t) => !f.terms.some((e) => e.toLowerCase() === t.toLowerCase()));
    if (!terms.length) {
      setKwDraft("");
      return;
    }
    setKwDraft("");
    patch({ terms: [...f.terms, ...terms] });
  }

  function resetFilters() {
    setKwDraft("");
    setPage(0);
    setF(DEFAULT_FILTERS);
  }

  function onToggleSave(id: string) {
    setSaved((cur) => toggleSaved(cur, id));
  }

  function onHide(id: string) {
    setHidden((cur) => hideJob(cur, id));
  }

  function scrollToJobs() {
    document.getElementById("landing-jobs")?.scrollIntoView({ behavior: "smooth" });
  }

  function applyTag(tag: string) {
    const term = tag.trim();
    setKwDraft("");
    setPage(0);
    setF((prev) => ({ ...prev, terms: term ? [term] : [] }));
    scrollToJobs();
  }

  const companyPool = useMemo(() => {
    const seen = new Set(BASE_COMPANIES.map((c) => c.toLowerCase()));
    const extra: string[] = [];
    for (const c of extraCompanies) {
      const name = (c.company_name || "").trim();
      if (name && !seen.has(name.toLowerCase())) {
        seen.add(name.toLowerCase());
        extra.push(name);
      }
    }
    return [...BASE_COMPANIES, ...extra];
  }, [extraCompanies]);

  const compMatches = useMemo(() => {
    const query = companyQuery.trim().toLowerCase();
    const pool = query
      ? companyPool.filter((c) => c.toLowerCase().includes(query))
      : companyPool;
    return pool.slice(0, 50);
  }, [companyPool, companyQuery]);

  const countryLabel = (code: string) => countryName(code);

  const popularCodes = useMemo(() => POPULAR_COUNTRY_CODES, []);

  const countryPool = useMemo(() => {
    // Dedupe by display label: stored full names ("Australia") collapse into
    // the code entry ("AU"), and the backend variant matching still finds
    // rows stored under either spelling.
    const seen = new Set<string>();
    const pool: string[] = [];
    for (const raw of [...popularCodes, ...allCountries]) {
      const value = (raw || "").trim();
      if (!value) continue;
      const normalized = /^[A-Za-z]{2,3}$/.test(value) ? value.toUpperCase() : value;
      const label = countryName(normalized).toLowerCase();
      if (seen.has(label)) continue;
      seen.add(label);
      pool.push(normalized);
    }
    return pool;
  }, [allCountries, popularCodes]);

  const dropMatches = useMemo(() => {
    const query = locationQuery.trim().toLowerCase();
    const pool = query
      ? countryPool.filter(
          (c) => c.toLowerCase().includes(query) || countryLabel(c).toLowerCase().includes(query),
        )
      : countryPool;
    return pool.slice(0, 50);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [countryPool, locationQuery]);

  // Drop saved country selections that no longer exist in the pool (e.g.
  // raw full names stored before display dedupe) so no invisible filter lingers.
  useEffect(() => {
    if (!metaLoaded) return;
    setF((prev) => {
      const valid = prev.countries.filter((c) => countryPool.includes(c));
      return valid.length === prev.countries.length ? prev : { ...prev, countries: valid };
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [metaLoaded, countryPool]);

  const sourceList = useMemo(
    () => (moreSources ? sourceOptions : sourceOptions.slice(0, 6)),
    [sourceOptions, moreSources],
  );

  const pageNumbers = useMemo(() => {
    if (pageCount <= 7) return Array.from({ length: pageCount }, (_, i) => i + 1);
    const cur = page + 1;
    const set = new Set([1, 2, 3, 4, 5, pageCount]);
    if (cur > 3) {
      set.add(cur - 1);
      set.add(cur);
      if (cur + 1 < pageCount) set.add(cur + 1);
    }
    return [...set].filter((n) => n >= 1 && n <= pageCount).sort((a, b) => a - b);
  }, [page, pageCount]);

  const countText =
    tab === "saved"
      ? `${total.toLocaleString()} saved job${total === 1 ? "" : "s"}`
      : `${total.toLocaleString()} jobs found`;

  const hasActiveFilters =
    f.terms.length > 0 ||
    f.locText.trim() !== "" ||
    f.countries.length > 0 ||
    f.sources.length > 0 ||
    f.companies.length > 0 ||
    f.sincePreset !== "" ||
    f.newOnly;

  return (
    <div className={styles.page}>
      {/* Navbar */}
      <nav className={styles.nav}>
        <div className={styles.navInner}>
          <Link href="/" className={styles.brand}>
            <LogoMark />
            <span>
              <span className={styles.brandName}>JobQuest</span>
              <br />
              <span className={styles.brandSub}>Jobs find you.</span>
            </span>
          </Link>
          <div className={styles.navLinks}>
            <Link href="/" className={styles.navLink}>
              Jobs
            </Link>
            <Link href="/browse" className={styles.navLink}>
              Companies
            </Link>
            <Link href="/browse" className={styles.navLink}>
              Salary Insights
            </Link>
            <Link href="/browse" className={styles.navLink}>
              Career Hub
            </Link>
            <span className={styles.navLink} style={{ cursor: "pointer" }}>
              More <span style={{ display: "inline-flex" }}>⌄</span>
            </span>
          </div>
          <div className={styles.navActions}>
            <button type="button" className={styles.iconBtn} aria-label="Theme">
              <SunIcon />
            </button>
            <Link href="/login" className={styles.btnLogin}>
              Login
            </Link>
            <Link href="/pricing" className={styles.btnSubscribe}>
              Subscribe
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className={styles.hero}>
        <div className={styles.heroBlobLeft} aria-hidden />
        <div className={styles.heroBlobRight} aria-hidden />
        <div className={styles.heroInner}>
          <div>
            <span className={styles.liveBadge}>
              <span style={{ color: "#7c3aed" }}>✦</span>{" "}
              {weekCount === null
                ? "Live · fresh jobs this week"
                : `Live · ${weekCount.toLocaleString()} new jobs this week`}
            </span>
            <h1 className={styles.heroTitle}>
              Your Next Opportunity
              <br />
              Is <span className={styles.heroTitleGreen}>Closer</span> Than You Think.
            </h1>
            <p className={styles.heroSub}>
              Discover the best jobs, from top companies, tailored to your skills and goals.
            </p>
          </div>
          <svg className={styles.heroArt} viewBox="0 0 560 360" fill="none" aria-hidden>
            <circle cx="360" cy="118" r="72" fill="#FDE68A" opacity="0.55" />
            <circle cx="360" cy="118" r="48" fill="#FCD34D" opacity="0.75" />
            <g opacity="0.55">
              <rect x="238" y="150" width="34" height="130" rx="4" fill="#C4B5FD" />
              <rect x="278" y="120" width="40" height="160" rx="4" fill="#A5B4FC" />
              <rect x="324" y="140" width="30" height="140" rx="4" fill="#F9A8D4" />
              <rect x="360" y="105" width="44" height="175" rx="4" fill="#93C5FD" />
              <rect x="410" y="145" width="32" height="135" rx="4" fill="#C4B5FD" />
              <rect x="448" y="125" width="38" height="155" rx="4" fill="#F9A8D4" />
            </g>
            <g>
              <rect x="252" y="190" width="36" height="110" rx="4" fill="#6366F1" />
              <rect x="294" y="165" width="42" height="135" rx="4" fill="#3B82F6" />
              <rect x="342" y="185" width="34" height="115" rx="4" fill="#8B5CF6" />
              <rect x="382" y="160" width="44" height="140" rx="4" fill="#6366F1" />
              <rect x="432" y="190" width="36" height="110" rx="4" fill="#3B82F6" />
            </g>
            <g fill="#E0E7FF" opacity="0.8">
              <rect x="300" y="175" width="8" height="8" rx="1" />
              <rect x="312" y="175" width="8" height="8" rx="1" />
              <rect x="300" y="188" width="8" height="8" rx="1" />
              <rect x="388" y="170" width="8" height="8" rx="1" />
              <rect x="400" y="170" width="8" height="8" rx="1" />
              <rect x="388" y="183" width="8" height="8" rx="1" />
              <rect x="258" y="200" width="7" height="7" rx="1" />
              <rect x="269" y="200" width="7" height="7" rx="1" />
            </g>
            <rect x="150" y="298" width="400" height="8" rx="4" fill="#C7D2FE" opacity="0.7" />
            <g>
              <rect x="128" y="212" width="34" height="62" rx="12" fill="#111827" />
              <rect x="128" y="212" width="34" height="14" rx="7" fill="#1F2937" />
              <path
                d="M170 205c14 4 22 16 24 34l4 60c.6 9-6 15-15 15h-44c-9 0-15.6-6-15-15l4-60c2-18 10-30 24-34 5 3 13 3 18 0z"
                fill="#1F2937"
              />
              <circle cx="179" cy="182" r="21" fill="#F2C9A4" />
              <path
                d="M158 178c-2-16 8-28 21-28s23 12 21 28c-1 8-3 12-5 14 1-10-2-14-4-20-6 5-16 6-22 2-3 3-6 6-6 14-2-2-4-5-5-10z"
                fill="#111827"
              />
              <path d="M162 208l-6 44M196 208l6 44" stroke="#0B1220" strokeWidth="6" strokeLinecap="round" />
            </g>
            <g className={styles.hand} fill="#64748B" fontSize="21">
              <text x="30" y="120">Same</text>
              <text x="48" y="152">You</text>
              <text x="30" y="184">Bigger</text>
              <text x="8" y="216">Opportunities</text>
            </g>
            <path
              d="M150 220c40-6 70-18 92-44"
              stroke="#64748B"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeDasharray="1 7"
              fill="none"
            />
            <path d="M242 176l-12 3 7 10z" fill="#64748B" />
            <g>
              <rect x="438" y="42" width="112" height="128" rx="12" fill="#FFFFFF" stroke="#E5EAF2" strokeWidth="1.5" />
              <g className={styles.hand} fill="#334155" fontSize="19" textAnchor="middle">
                <text x="494" y="72">Dream</text>
                <text x="494" y="98">Apply</text>
                <text x="494" y="124">Grow</text>
                <text x="494" y="150">Repeat</text>
              </g>
              <path
                d="M494 158c-2.5-3.5-8-2.5-8 1 0 2.8 4.5 5.5 8 7.5 3.5-2 8-4.7 8-7.5 0-3.5-5.5-4.5-8-1z"
                fill="#F87171"
              />
            </g>
          </svg>
        </div>
      </section>

      {/* Search */}
      <div className={styles.searchWrap}>
        <div className={styles.searchBar}>
          <div className={styles.searchField} style={{ flexWrap: "wrap", rowGap: 6 }}>
            <SearchIcon />
            {f.terms.map((t) => (
              <span key={t.toLowerCase()} className={styles.kwChip}>
                {t}
                <button
                  type="button"
                  aria-label={`Remove keyword ${t}`}
                  onClick={() =>
                    patch({ terms: f.terms.filter((x) => x.toLowerCase() !== t.toLowerCase()) })
                  }
                >
                  ✕
                </button>
              </span>
            ))}
            <input
              className={styles.kwInput}
              placeholder={
                f.terms.length ? "Add another keyword…" : "Search jobs, skills, companies, or keywords..."
              }
              aria-label="Search keywords"
              value={kwDraft}
              onChange={(e) => {
                const v = e.target.value;
                if (v.endsWith(",")) {
                  setKwDraft(v.slice(0, -1));
                  setTimeout(commitDraft, 0);
                } else {
                  setKwDraft(v);
                }
              }}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  commitDraft();
                  scrollToJobs();
                } else if (e.key === "Backspace" && kwDraft === "" && f.terms.length) {
                  patch({ terms: f.terms.slice(0, -1) });
                }
              }}
              onBlur={commitDraft}
            />
          </div>
          <div className={styles.searchDivider} aria-hidden />
          <label className={styles.searchLoc} style={{ flex: 1, cursor: "text" }}>
            <PinIcon />
            <input
              style={{
                border: 0,
                outline: 0,
                background: "transparent",
                width: "100%",
                fontSize: 15,
                fontFamily: "inherit",
                color: "#0b1b33",
              }}
              placeholder="Location"
              aria-label="Location"
              value={f.locText}
              onChange={(e) => patch({ locText: e.target.value })}
              onKeyDown={(e) => {
                if (e.key === "Enter") scrollToJobs();
              }}
            />
          </label>
          <button
            type="button"
            className={styles.btnFind}
            onClick={() => {
              commitDraft();
              scrollToJobs();
            }}
          >
            Find Jobs <span aria-hidden>→</span>
          </button>
        </div>
        <div className={styles.tryRow}>
          <span>Try:</span>
          {TRY_TAGS.map((t) => (
            <button key={t} type="button" className={styles.tryPill} onClick={() => applyTag(t)}>
              {t}
            </button>
          ))}
        </div>
      </div>

      {/* Main */}
      <div className={styles.main} id="landing-jobs">
        {/* Filters */}
        <aside className={`${styles.card} ${styles.filters}`}>
          <div className={styles.filtersHead}>
            <span className={styles.filtersTitle}>Filters</span>
            <button type="button" className={styles.resetBtn} onClick={resetFilters}>
              Reset
            </button>
          </div>

          <div className={styles.filterGroup}>
            <h3 className={styles.filterHeading}>Date posted</h3>
            <div className={styles.pillRow}>
              {SINCE_OPTIONS.map((o) => (
                <button
                  key={o.value || "any"}
                  type="button"
                  onClick={() => patch({ sincePreset: o.value })}
                  className={`${styles.pillBtn} ${f.sincePreset === o.value ? styles.pillBtnActive : ""}`}
                >
                  {f.sincePreset === o.value ? "✓ " : ""}
                  {o.label}
                </button>
              ))}
            </div>
          </div>

          <div className={styles.filterGroup}>
            <h3 className={styles.filterHeading}>Location</h3>
            <div ref={locDropRef} className={styles.dropWrap}>
              <label className={styles.miniSearch}>
                <SearchIcon />
                <input
                  placeholder="Search location..."
                  aria-label="Search location"
                  value={locationQuery}
                  onChange={(e) => {
                    setLocationQuery(e.target.value);
                    setLocDropOpen(true);
                  }}
                  onFocus={() => setLocDropOpen(true)}
                  onKeyDown={(e) => {
                    if (e.key === "Escape") setLocDropOpen(false);
                  }}
                />
              </label>
              {locDropOpen && (
                <div className={styles.dropPanel}>
                  {dropMatches.length === 0 ? (
                    <div className={styles.dropEmpty}>No countries match.</div>
                  ) : (
                    dropMatches.map((code) => {
                      const active = f.countries.includes(code);
                      return (
                        <button
                          key={code}
                          type="button"
                          className={styles.dropItem}
                          onClick={() => toggleMulti("countries", code)}
                        >
                          <span>{countryLabel(code)}</span>
                          {active && <span className={styles.dropCheck}>✓</span>}
                        </button>
                      );
                    })
                  )}
                  <div className={styles.dropFoot}>{countryPool.length} countries tracked</div>
                </div>
              )}
            </div>
            {popularCodes.map((code) => (
              <Check
                key={code}
                label={countryLabel(code)}
                checked={f.countries.includes(code)}
                onChange={() => toggleMulti("countries", code)}
              />
            ))}
          </div>

          <div className={styles.filterGroup}>
            <h3 className={styles.filterHeading}>Sources</h3>
            {sourceList.map((s) => (
              <Check
                key={s}
                label={atsLabel(s)}
                checked={f.sources.includes(s)}
                onChange={() => toggleMulti("sources", s)}
              />
            ))}
            {sourceOptions.length > 6 && (
              <button
                type="button"
                className={styles.showMore}
                onClick={() => setMoreSources((v) => !v)}
              >
                {moreSources ? "Show less" : "Show more"}
              </button>
            )}
          </div>

          <div className={styles.filterGroup}>
            <h3 className={styles.filterHeading}>Company</h3>
            <div ref={compDropRef} className={styles.dropWrap}>
              <label className={styles.miniSearch}>
                <SearchIcon />
                <input
                  placeholder="Search company..."
                  aria-label="Search company"
                  value={companyQuery}
                  onChange={(e) => {
                    setCompanyQuery(e.target.value);
                    setCompDropOpen(true);
                  }}
                  onFocus={() => setCompDropOpen(true)}
                  onKeyDown={(e) => {
                    if (e.key === "Escape") setCompDropOpen(false);
                  }}
                />
              </label>
              {compDropOpen && (
                <div className={styles.dropPanel}>
                  {compMatches.length === 0 ? (
                    <div className={styles.dropEmpty}>No companies match.</div>
                  ) : (
                    compMatches.map((c) => {
                      const active = f.companies.includes(c);
                      return (
                        <button
                          key={c}
                          type="button"
                          className={styles.dropItem}
                          onClick={() => toggleMulti("companies", c)}
                        >
                          <span>{c}</span>
                          {active && <span className={styles.dropCheck}>✓</span>}
                        </button>
                      );
                    })
                  )}
                  <div className={styles.dropFoot}>{companyPool.length} companies tracked</div>
                </div>
              )}
            </div>
            {BASE_COMPANIES.map((c) => (
              <Check
                key={c}
                label={c}
                checked={f.companies.includes(c)}
                onChange={() => toggleMulti("companies", c)}
              />
            ))}
          </div>
        </aside>

        {/* Jobs */}
        <section className={`${styles.card} ${styles.jobsPanel}`}>
          <div className={styles.tabs}>
            {(
              [
                ["all", "All Jobs"],
                ["saved", "Saved"],
              ] as [Tab, string][]
            ).map(([key, label]) => (
              <button
                key={key}
                type="button"
                className={`${styles.tab} ${tab === key ? styles.tabActive : ""}`}
                onClick={() => {
                  setTab(key);
                  setPage(0);
                }}
              >
                {label}
              </button>
            ))}
          </div>
          <div className={styles.jobsBar}>
            <span className={styles.jobsCount}>{countText}</span>
            <div className={styles.jobsBarRight}>
              <label className={styles.switch}>
                <input
                  type="checkbox"
                  checked={f.newOnly}
                  onChange={(e) => patch({ newOnly: e.target.checked })}
                />
                <span className={styles.switchTrack} />
              </label>
              <span>New jobs only</span>
              <span className={styles.sortLabel}>Sort by</span>
              <select
                className={styles.sortDrop}
                aria-label="Sort jobs"
                value={f.sort}
                onChange={(e) => patch({ sort: e.target.value as Sort })}
              >
                <option value="relevant">Most Relevant</option>
                <option value="newest">Newest first</option>
                <option value="oldest">Oldest first</option>
              </select>
            </div>
          </div>

          <div className={styles.jobList}>
            {loading ? (
              <p style={{ padding: "32px 0", textAlign: "center", color: "#8a94a6", fontSize: 14 }}>
                Scanning jobs…
              </p>
            ) : visibleJobs.length === 0 ? (
              <p style={{ padding: "32px 0", textAlign: "center", color: "#8a94a6", fontSize: 14 }}>
                {hasActiveFilters
                  ? "No jobs match these filters — try widening them or press Reset."
                  : "No jobs found yet — check back soon."}
              </p>
            ) : (
              visibleJobs.map((job, i) => {
                const isSaved = saved.includes(job.id);
                const pills = detectSkills(`${job.title} ${job.location || ""}`);
                const shownCountries = pills.length
                  ? []
                  : job.countries.filter(Boolean).slice(0, 4).map(countryName);
                return (
                  <article
                    key={job.id}
                    className={`${styles.jobCard} ${i === 0 && tab === "all" ? styles.jobCardFeatured : ""}`}
                  >
                    <BrandLogo name={job.company} domain={job.domain} />
                    <div className={styles.jobMain}>
                      <h3 className={styles.jobTitle}>{job.title}</h3>
                      <p className={styles.jobCompany}>{job.company}</p>
                      <p className={styles.jobMeta}>
                        {job.location || "Location not specified"} · {jobMode(job)}
                      </p>
                      <p className={styles.jobDesc}>
                        {(job as Job & { description?: string | null }).description ||
                          "No description available yet."}
                      </p>
                      {(pills.length > 0 || shownCountries.length > 0) && (
                        <div className={styles.skillRow}>
                          {pills.map((s) => (
                            <span key={s} className={styles.skillPill}>
                              {s}
                            </span>
                          ))}
                          {shownCountries.map((s) => (
                            <span key={s} className={styles.skillPill}>
                              {s}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                    <div className={styles.jobSide}>
                      <div className={styles.jobSideTop}>
                        <span>{timeAgo(job.first_seen_at)}</span>
                        <button
                          type="button"
                          className={styles.bookmarkBtn}
                          style={isSaved ? { color: "#2563eb" } : undefined}
                          aria-label={isSaved ? "Unsave job" : "Save job"}
                          onClick={() => onToggleSave(job.id)}
                        >
                          <BookmarkIcon filled={isSaved} />
                        </button>
                        <button
                          type="button"
                          className={styles.bookmarkBtn}
                          aria-label="Hide job"
                          title="Hide"
                          onClick={() => onHide(job.id)}
                          style={{ fontSize: 14 }}
                        >
                          ✕
                        </button>
                      </div>
                      {job.url ? (
                        <a
                          href={job.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className={`${styles.btnApply} ${i === 0 && tab === "all" ? styles.btnApplyGreen : ""}`}
                        >
                          Apply
                        </a>
                      ) : (
                        <Link
                          href={`/browse/${job.id}`}
                          className={`${styles.btnApply} ${i === 0 && tab === "all" ? styles.btnApplyGreen : ""}`}
                        >
                          Details
                        </Link>
                      )}
                    </div>
                  </article>
                );
              })
            )}
          </div>

          <div className={styles.pagination}>
            <button
              type="button"
              className={`${styles.pageBtn} ${styles.pageArrow}`}
              aria-label="Previous page"
              disabled={page === 0}
              onClick={() => setPage((p) => Math.max(0, p - 1))}
            >
              ←
            </button>
            {pageNumbers.map((n, idx, arr) => (
              <span key={n} style={{ display: "inline-flex", alignItems: "center", gap: 8 }}>
                {idx > 0 && n - arr[idx - 1] > 1 && <span className={styles.pageEllipsis}>...</span>}
                <button
                  type="button"
                  className={`${styles.pageBtn} ${page + 1 === n ? styles.pageActive : ""}`}
                  onClick={() => setPage(n - 1)}
                >
                  {n}
                </button>
              </span>
            ))}
            <button
              type="button"
              className={`${styles.pageBtn} ${styles.pageArrow}`}
              aria-label="Next page"
              disabled={page >= pageCount - 1}
              onClick={() => setPage((p) => Math.min(pageCount - 1, p + 1))}
            >
              →
            </button>
          </div>
          {hidden.length > 0 && tab === "all" && (
            <p style={{ textAlign: "center", fontSize: 12, color: "#8a94a6", paddingBottom: 16 }}>
              {hidden.length} hidden job{hidden.length === 1 ? "" : "s"} ·{" "}
              <button
                type="button"
                onClick={() => setHidden(unhideAll())}
                style={{
                  border: 0,
                  background: "none",
                  color: "#6d5ef0",
                  cursor: "pointer",
                  fontSize: 12,
                  fontWeight: 600,
                }}
              >
                Unhide all
              </button>
            </p>
          )}
        </section>

        {/* Sidebar */}
        <aside className={styles.side}>
          <div className={styles.proCard}>
            <svg className={styles.proTrophy} viewBox="0 0 150 170" fill="none" aria-hidden>
              <path d="M45 30h60v45a30 30 0 01-60 0V30z" fill="#FBBF24" opacity="0.9" />
              <path
                d="M45 40H25a5 5 0 005 5c0 14 8 24 18 27M105 40h20a5 5 0 01-5 5c0 14-8 24-18 27"
                stroke="#FBBF24"
                strokeWidth="7"
                strokeLinecap="round"
                opacity="0.9"
              />
              <rect x="68" y="103" width="14" height="26" rx="4" fill="#FBBF24" opacity="0.9" />
              <rect x="52" y="129" width="46" height="12" rx="6" fill="#FBBF24" opacity="0.9" />
              <path d="M75 8l2.2 5.4 5.4 2.2-5.4 2.2L75 23l-2.2-5.2-5.4-2.2 5.4-2.2L75 8z" fill="#FDE68A" />
              <circle cx="118" cy="30" r="3" fill="#FDE68A" />
              <circle cx="30" cy="60" r="2.5" fill="#FDE68A" />
            </svg>
            <div className={styles.proTop}>
              <CrownIcon />
              JobQuest Pro
              <span className={styles.proTopRight}>
                <SparkleIcon />
              </span>
            </div>
            <h3 className={styles.proHead}>
              Get ahead.
              <br />
              Stay informed.
            </h3>
            <p className={styles.proDesc}>Unlock premium features and never miss the opportunity.</p>
            <ul className={styles.proList}>
              <li>
                <span className={styles.proCheck}>✓</span> Personalized job matches
              </li>
              <li>
                <span className={styles.proCheck}>✓</span> Instant job alerts
              </li>
              <li>
                <span className={styles.proCheck}>✓</span> Advanced filters
              </li>
              <li>
                <span className={styles.proCheck}>✓</span> Track your applications
              </li>
              <li>
                <span className={styles.proCheck}>✓</span> Ad-free experience
              </li>
            </ul>
            <button
              type="button"
              className={styles.btnTrial}
              onClick={() => (window.location.href = "/pricing")}
            >
              Start 3-day free trial
            </button>
            <p className={styles.proFine}>Then just ₹49/month. Cancel anytime.</p>
          </div>

          <div className={`${styles.card} ${styles.testimonial}`}>
            <span className={styles.quoteMark} aria-hidden>
              &ldquo;
            </span>
            <p className={styles.testimonialText}>
              &ldquo;JobQuest helped me find my dream role in just 2 weeks! The alerts are super
              relevant.&rdquo;
            </p>
            <div className={styles.testimonialWho}>
              <span className={styles.avatar} aria-hidden>
                A
              </span>
              <span>
                <span className={styles.testimonialName}>Akhil M.</span>
                <br />
                <span className={styles.testimonialRole}>SDE @ Google</span>
              </span>
            </div>
          </div>

          <div className={`${styles.card} ${styles.trending}`}>
            <h3 className={styles.trendingTitle}>🔥 Trending Searches</h3>
            {TRENDING.map((t) => (
              <button
                key={t}
                type="button"
                className={styles.trendItem}
                onClick={() => applyTag(t)}
              >
                <span className={styles.trendUp}>↗</span> {t}
              </button>
            ))}
          </div>

          <div className={styles.promoGreen}>
            <h3 className={styles.promoGreenTitle}>
              Better jobs.
              <br />A brighter you.
            </h3>
            <div className={styles.promoBrand}>
              <svg width="18" height="18" viewBox="0 0 40 40" fill="none" aria-hidden>
                <circle cx="20" cy="20" r="18" stroke="#0b3b2e" strokeWidth="3" />
                <circle cx="20" cy="20" r="11" stroke="#0b3b2e" strokeWidth="3" />
                <circle cx="20" cy="20" r="3.5" fill="#0b3b2e" />
              </svg>
              JobQuest
            </div>
            <svg className={styles.promoArt} viewBox="0 0 300 130" fill="none" aria-hidden>
              <circle cx="248" cy="30" r="16" fill="#FDE68A" />
              <path d="M0 100 Q75 55 150 92 T300 84 V130 H0 Z" fill="#6EE7B7" />
              <path d="M0 112 Q90 78 180 104 T300 100 V130 H0 Z" fill="#34D399" />
              <g stroke="#064E3B" strokeWidth="3" strokeLinecap="round">
                <circle cx="150" cy="72" r="5" fill="#064E3B" />
                <path d="M150 77v14M150 82l-8 6M150 82l8 6M150 91l-7 12M150 91l7 12" />
              </g>
            </svg>
          </div>

          <div className={`${styles.card} ${styles.quoteCard}`}>
            <span className={styles.quoteMark} aria-hidden>
              &ldquo;
            </span>
            <p className={styles.quoteCardText}>
              &ldquo;Opportunities don&rsquo;t happen. You find them.&rdquo;
            </p>
          </div>
        </aside>
      </div>
    </div>
  );
}
