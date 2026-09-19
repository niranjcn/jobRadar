export interface Stats {
  jobs_total: number;
  jobs_new_7d: number;
  companies: number;
  matches: number;
  avg_match_score: number;
  sources_active: number;
}

export interface DailyPoint {
  date: string;
  jobs: number;
  matches: number;
  avg_score: number;
}

export interface DailyStats {
  days: DailyPoint[];
  total_jobs: number;
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
  domain?: string | null;
  countries: string[];
  is_remote: boolean;
  is_active?: boolean;
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
  domain?: string | null;
  last_checked_at: string | null;
  active: boolean;
  job_count: number;
}

export interface Source {
  id: string;
  company_name: string;
  ats_type: string;
  domain?: string | null;
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
  concurrency: number;
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
  status: "ok" | "error" | "skipped";
  fetched?: number;
  new?: number;
  first_check?: boolean;
  error?: string | null;
  duration_ms?: number;
  reason?: string | null;
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
  domain?: string | null;
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
  domain?: string | null;
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

export interface PublicCompany {
  company_name: string;
  domain?: string | null;
  ats_type: string;
  job_count: number;
  latest_job_at: string | null;
}

// ---------- access / subscription ----------

export interface SubscriptionInfo {
  plan_code: string;
  status: string;
  provider: string;
  current_period_end?: string | null;
  plan_limits?: Record<string, unknown> | null;
}

export type Role = "user" | "privileged" | "admin";

export interface Me {
  id: string;
  email: string | null;
  display_name?: string;
  role: Role;
  status: string;
  capabilities: string[];
  alert_delay_minutes: number;
  access_locked: boolean;
  is_owner: boolean;
  telegram_chat_id?: number | null;
  telegram_linked?: boolean;
  telegram_username?: string | null;
  telegram_photo_url?: string | null;
  has_password?: boolean;
  needs_onboarding?: boolean;
  anonymous: boolean;
  subscription?: SubscriptionInfo | null;
}

export interface Plan {
  code: string;
  name: string;
  price_cents: number;
  currency: string;
  interval: string;
}

export type PresetField =
  | "roles"
  | "keywords"
  | "locations"
  | "seniority"
  | "excluded_companies"
  | "excluded_roles";

export interface Preset {
  id: string;
  name: string;
  description: string;
  roles: string[];
  keywords: string[];
  locations: string[];
  seniority: string[];
  excluded_companies: string[];
  excluded_roles: string[];
  is_admin_only: boolean;
}

export interface AdminUser {
  id: string;
  email: string | null;
  display_name: string;
  role: Role;
  status: "pending" | "approved" | "disabled";
  access_locked: boolean;
  alert_delay_minutes: number;
  capabilities: string[];
  is_owner: boolean;
  created_at: string | null;
  last_login_at: string | null;
  sub_plan?: string | null;
  sub_provider?: string | null;
  sub_period_end?: string | null;
}

export interface Coupon {
  id: string;
  code: string;
  grants_role: "user" | "privileged";
  duration_days: number | null;
  note: string | null;
  created_at: string;
  expires_at: string;
  claimed_at: string | null;
  claimed_by_email?: string | null;
  created_by_email?: string | null;
}

export interface AdminStats {
  users_total: number;
  privileged: number;
  locked: number;
  disabled: number;
  active_subs: number;
  coupons_open: number;
  mrr_cents: number;
  alerts_7d: number;
}

export interface EgressTable {
  name: string;
  total_bytes: number;
  table_bytes: number;
  index_bytes: number;
  toast_bytes: number;
  live_rows: number;
  dead_rows: number;
  avg_row_bytes: number;
  last_vacuum: string | null;
  last_autovacuum: string | null;
}

export interface EgressDaily {
  date: string;
  jobs: number;
  matches: number;
  alerts: number;
  bytes_est: number;
}

export interface EgressTopSource {
  company: string;
  ats_type: string;
  job_count: number;
  bytes_est: number;
  share_pct: number;
}

export interface EgressRun {
  id: string;
  triggered_by: string;
  ats_type: string | null;
  status: string;
  started_at: string | null;
  finished_at: string | null;
  jobs_fetched: number;
  jobs_new: number;
  bytes_est: number;
  duration_ms: number | null;
  sources_count: number | null;
  error: string | null;
}

export interface EgressResponse {
  generated_at: string;
  days: number;
  database: {
    size_bytes: number;
    free_limit_bytes: number;
    pro_limit_bytes: number;
    free_pct: number;
    pro_pct: number;
  };
  tables: EgressTable[];
  totals: {
    jobs_total: number;
    sources_total: number;
    active_sources: number;
    jobs_24h: number;
    jobs_7d: number;
    jobs_30d: number;
    avg_job_bytes: number;
    db_size_bytes: number;
    bytes_24h_est: number;
    bytes_7d_est: number;
    bytes_30d_est: number;
    proj_monthly_jobs: number;
    proj_monthly_bytes: number;
    notif_total?: number;
    queue_total?: number;
    runs_24h?: number;
  };
  daily: EgressDaily[];
  top_sources: EgressTopSource[];
  recent_runs: EgressRun[];
  cache: { blks_hit?: number; blks_read?: number; hit_ratio?: number | null };
  retention: { retention_days: number; reclaimable_jobs: number; reclaimable_bytes_est: number };
  warnings: { level: "critical" | "warn" | "info"; title: string; detail: string }[];
}

export interface SchemaColumn {
  table_name: string;
  column_name: string;
  data_type: string;
  udt_name: string;
  is_nullable: string;
  column_default: string | null;
}
export interface SchemaFK {
  table_name: string;
  constraint_name: string;
  column_name: string;
  foreign_table: string;
  foreign_column: string;
  delete_rule: string;
}
export interface SchemaTable {
  name: string;
  columns: SchemaColumn[];
  pks: string[];
  fks: SchemaFK[];
  uniques: string[];
  indexes: { table_name: string; indexname: string; indexdef: string }[];
  size: { total_bytes: number; data_bytes: number; est_rows: number; exact_rows: number | null };
}
export interface SchemaIssue {
  level: "high" | "medium" | "low" | "info";
  table: string;
  title: string;
  detail: string;
}