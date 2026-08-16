export interface Stats {
  jobs_total: number;
  jobs_new_7d: number;
  companies: number;
  matches: number;
  avg_match_score: number;
  sources_active: number;
}

export interface Job {
  id: string;
  source_id: string;
  external_job_id: string;
  title: string;
  location: string | null;
  url: string | null;
  description: string | null;
  first_seen_at: string | null;
  company: string;
  ats_type: string;
  countries: string[];
  is_remote: boolean;
  match_score: number | null;
  matched_on: string[];
}

export interface JobsResponse {
  jobs: Job[];
  total: number;
  limit: number;
  offset: number;
}

export interface Company {
  id: string;
  company_name: string;
  ats_type: string;
  last_checked_at: string | null;
  active: boolean;
  job_count: number;
}

export interface Source {
  id: string;
  company_name: string;
  ats_type: string;
  board_identifier: string;
  last_checked_at: string | null;
  active: boolean;
  job_count: number;
  poll_interval: number;
  status: "healthy" | "stale" | "never";
  reason?: string | null;
}

export interface UnhealthySource {
  id: string;
  company_name: string;
  ats_type: string;
  status: "stale" | "never";
  reason: string | null;
}

export interface ScheduleEntry {
  ats_type: string;
  interval_seconds: number;
  overridden: boolean;
  env_interval_seconds: number;
  last_checked_at: string | null;
  next_run_at: string | null;
  source_count: number;
}

export interface ScheduleResult {
  schedule: ScheduleEntry[];
}

export interface SourceResult {
  sources: Source[];
  intervals: Record<string, number>;
}

export interface PollSourceResult {
  company: string;
  ats_type: string;
  status: "ok" | "error";
  fetched?: number;
  new?: number;
  first_check?: boolean;
  error?: string | null;
}

export interface PollRun {
  id: string;
  triggered_by: "scheduled" | "manual";
  ats_type: string | null;
  status: "running" | "completed" | "failed";
  started_at: string | null;
  finished_at: string | null;
  jobs_fetched: number;
  jobs_new: number;
  matches_considered: number;
  matches_new: number;
  telegram_sent: number;
  email_sent: number;
  sources: PollSourceResult[];
  error: string | null;
}

export interface PollRunsResult {
  runs: PollRun[];
}

export interface Notification {
  id: string;
  job_id: string;
  channel: "email" | "telegram";
  sent_at: string;
  title: string | null;
  company_name: string | null;
}

export interface Preferences {
  roles: string[];
  keywords: string[];
  locations: string[];
  seniority: string[];
  excluded_companies: string[];
  excluded_roles: string[];
  notify_telegram: boolean;
  notify_email: boolean;
  alert_frequency: string;
  telegram_scope: "all" | "matched";
  email_scope: "all" | "matched";
  notify_first_check: boolean;
}

export interface CompanyMatchSummary {
  company: string;
  matches: number;
}

export interface MatchesSummary {
  total: number;
  companies: CompanyMatchSummary[];
}

export interface LocationMappingSettings {
  enabled: boolean;
  remote_to: string[];
  custom_aliases: Record<string, string>;
}

export interface LocationMappingResult {
  settings: LocationMappingSettings;
  index_stats: { countries: number; states: number; cities: number };
}

export interface GeoCountry {
  name: string;
  code: string;
}

export interface LocationPreview {
  location: string;
  countries: string[];
  is_remote: boolean;
  matched: string[];
  source: string;
}

export interface CompanyGroup {
  company: string;
  ats_type: string;
  jobs: number;
  last_checked_at: string | null;
}

export interface JobFilters {
  companies: string[];
  countries: string[];
  ats_types: string[];
}