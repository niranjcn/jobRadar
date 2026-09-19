import type {
  AdminStats,
  AdminUser,
  Company,
  Coupon,
  DailyStats,
  GeoCountry,
  Job,
  JobFilters,
  JobsResponse,
  LocationMappingResult,
  LocationMappingSettings,
  LocationPreview,
  MatchesSummary,
  Me,
  Notification,
  Plan,
  PollRunsResult,
  Preferences,
  Preset,
  PublicCompany,
  Role,
  ScheduleResult,
  SourceResult,
  Stats,
  SubscriptionInfo,
  UnhealthySource,
} from "./types";

const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(status: number, statusText: string, body: string) {
    super(`${status} ${statusText}: ${body.slice(0, 200)}`);
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    credentials: "include",
    cache: "no-store",
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new ApiError(res.status, res.statusText, body);
  }
  return res.json() as Promise<T>;
}

export const api = {
  stats: () => request<Stats>("/api/stats"),
  statsDaily: (days = 14) => request<DailyStats>(`/api/stats/daily?days=${days}`),
  matchesSummary: () => request<MatchesSummary>("/api/matches/summary"),
  matchedJobs: (params?: {
    company?: string;
    ats?: string;
    since?: string;
    limit?: number;
    offset?: number;
  }) => {
    const search = new URLSearchParams();
    if (params?.company) search.set("company", params.company);
    if (params?.ats) search.set("ats", params.ats);
    if (params?.since) search.set("since", params.since);
    if (params?.limit) search.set("limit", String(params.limit));
    if (params?.offset) search.set("offset", String(params.offset));
    const qs = search.toString();
    return request<JobsResponse>(`/api/matches/jobs${qs ? `?${qs}` : ""}`);
  },
  jobs: (params?: {
    q?: string;
    ats?: string;
    company?: string;
    country?: string;
    since?: string;
    remote_only?: boolean;
    limit?: number;
    offset?: number;
  }) => {
    const search = new URLSearchParams();
    if (params?.q) search.set("q", params.q);
    if (params?.ats) search.set("ats", params.ats);
    if (params?.company) search.set("company", params.company);
    if (params?.country) search.set("country", params.country);
    if (params?.since) search.set("since", params.since);
    if (params?.remote_only) search.set("remote_only", "true");
    if (params?.limit) search.set("limit", String(params.limit));
    if (params?.offset) search.set("offset", String(params.offset));
    const qs = search.toString();
    return request<JobsResponse>(`/api/jobs${qs ? `?${qs}` : ""}`);
  },
  publicJobs: (params?: {
    q?: string;
    ats?: string;
    company?: string;
    companies?: string;
    sources?: string;
    country?: string;
    countries?: string;
    since?: string;
    remote_only?: boolean;
    mode?: string;
    loc?: string;
    locs?: string;
    types?: string;
    exp?: string;
    skills?: string;
    cats?: string;
    min_salary?: string;
    max_salary?: string;
    sort?: "newest" | "oldest";
    limit?: number;
    offset?: number;
  }) => {
    const search = new URLSearchParams();
    if (params?.q) search.set("q", params.q);
    if (params?.ats) search.set("ats", params.ats);
    if (params?.company) search.set("company", params.company);
    if (params?.companies) search.set("companies", params.companies);
    if (params?.sources) search.set("sources", params.sources);
    if (params?.country) search.set("country", params.country);
    if (params?.countries) search.set("countries", params.countries);
    if (params?.since) search.set("since", params.since);
    if (params?.remote_only) search.set("remote_only", "true");
    if (params?.mode) search.set("mode", params.mode);
    if (params?.loc) search.set("loc", params.loc);
    if (params?.locs) search.set("locs", params.locs);
    if (params?.types) search.set("types", params.types);
    if (params?.exp) search.set("exp", params.exp);
    if (params?.skills) search.set("skills", params.skills);
    if (params?.cats) search.set("cats", params.cats);
    if (params?.min_salary) search.set("min_salary", params.min_salary);
    if (params?.max_salary) search.set("max_salary", params.max_salary);
    if (params?.sort) search.set("sort", params.sort);
    if (params?.limit) search.set("limit", String(params.limit));
    if (params?.offset) search.set("offset", String(params.offset));
    const qs = search.toString();
    return request<JobsResponse>(`/api/public/jobs${qs ? `?${qs}` : ""}`);
  },
  publicJob: (id: string) => request<Job>(`/api/public/jobs/${id}`),
  publicCompanies: () => request<{ companies: PublicCompany[] }>("/api/public/companies"),
  jobFilters: () => request<JobFilters>("/api/jobs/filters"),
  job: (id: string) => request<Job>(`/api/jobs/${id}`),
  companies: () => request<{ companies: Company[] }>("/api/companies"),
  sources: () => request<SourceResult>("/api/sources"),
  createSource: (payload: {
    company_name: string;
    url?: string;
    ats_type?: string;
    board_identifier?: string;
    domain?: string;
  }) =>
    request<{ id: string; company_name: string; ats_type: string; board_identifier: string; domain?: string | null }>(
      "/api/sources",
      { method: "POST", body: JSON.stringify(payload) },
    ),
  updateSource: (id: string, payload: { active?: boolean; board_identifier?: string; domain?: string }) =>
    request<{ ok: boolean }>(`/api/sources/${id}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),
  runSource: (id: string) =>
    request<{ ok: boolean; fetched: number; new: number; first_check: boolean }>(
      `/api/sources/${id}/run`,
      { method: "POST" },
    ),
  runPoll: (atsType?: string) =>
    request<{ run_id: string; status: string; ats_type: string | null }>("/api/poll/run", {
      method: "POST",
      body: JSON.stringify({ ats_type: atsType ?? null }),
    }),
  runUnhealthyPoll: () =>
    request<{ run_id: string | null; status: string; sources: UnhealthySource[] }>("/api/poll/run-unhealthy", {
      method: "POST",
    }),
  unhealthySources: () =>
    request<{ unhealthy: UnhealthySource[] }>("/api/sources/unhealthy"),
  pollRuns: (limit?: number) =>
    request<PollRunsResult>(`/api/poll/runs${limit ? `?limit=${limit}` : ""}`),
  schedule: () => request<ScheduleResult>("/api/schedule"),
  updateSchedule: (atsType: string, intervalSeconds: number) =>
    request<{ ok: boolean; ats_type: string; interval_seconds: number; rescheduled: boolean }>(
      `/api/schedule/${atsType}`,
      { method: "PUT", body: JSON.stringify({ interval_seconds: intervalSeconds }) },
    ),
  resetSchedule: (atsType: string) =>
    request<{ ok: boolean; ats_type: string }>(`/api/schedule/${atsType}`, { method: "DELETE" }),
  preferences: () => request<Preferences>("/api/preferences"),
  updatePreferences: (prefs: Preferences) =>
    request<{ ok: boolean }>("/api/preferences", {
      method: "PUT",
      body: JSON.stringify(prefs),
    }),
  notifications: () => request<{ notifications: Notification[] }>("/api/notifications"),
  geoCountries: () => request<{ countries: GeoCountry[] }>("/api/geo/countries"),
  locationMapping: () => request<LocationMappingResult>("/api/settings/location-mapping"),
  updateLocationMapping: (
    payload: Partial<{
      enabled: boolean;
      remote_to: string[];
      custom_aliases: Record<string, string>;
    }>,
  ) =>
    request<{ ok: boolean; settings: LocationMappingSettings }>("/api/settings/location-mapping", {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  previewLocation: (location: string) =>
    request<LocationPreview>("/api/settings/location-mapping/preview", {
      method: "POST",
      body: JSON.stringify({ location }),
    }),

  // ---------- auth / access ----------

  me: () => request<Me>("/api/auth/me"),
  register: (payload: { email: string; display_name?: string; password: string }) =>
    request<{ ok: boolean; access_locked: boolean; user_id: string; status: string } & Me>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  loginPassword: (email: string, password: string) =>
    request<Me>("/api/auth/login-password", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  updateProfile: (payload: { display_name?: string; email?: string }) =>
    request<Me>("/api/auth/profile", {
      method: "PUT",
      body: JSON.stringify(payload),
    }),
  logout: () => request<{ ok: boolean }>("/api/auth/logout", { method: "POST" }),
  setPassword: (new_password: string, current_password = "") =>
    request<{ ok: boolean; message: string }>("/api/auth/password", {
      method: "POST",
      body: JSON.stringify({ new_password, current_password }),
    }),
  setTelegramChatId: (telegram_chat_id: string) =>
    request<{ ok: boolean; telegram_chat_id: number | null }>("/api/auth/telegram-chat-id", {
      method: "PUT",
      body: JSON.stringify({ telegram_chat_id }),
    }),

  plans: () => request<{ plans: Plan[] }>("/api/plans"),
  redeemCoupon: (code: string) =>
    request<{ ok: boolean; role: Role; duration_days: number | null }>("/api/coupons/redeem", {
      method: "POST",
      body: JSON.stringify({ code }),
    }),
  checkout: (plan_code = "standard") =>
    request<{ provider: string; instructions: string; subscription_id?: string; key_id?: string; amount?: number; currency?: string }>("/api/billing/checkout", {
      method: "POST",
      body: JSON.stringify({ plan_code }),
    }),
  razorpayCreateSubscription: () =>
    request<{ ok: boolean; subscription_id: string; key_id: string; plan_id: string; customer_id: string }>("/api/billing/razorpay/create-subscription", { method: "POST" }),
  razorpayVerify: (payload: { razorpay_payment_id: string; razorpay_subscription_id: string; razorpay_signature: string }) =>
    request<{ ok: boolean; subscription_id: string; period_end: string }>("/api/billing/razorpay/verify", { method: "POST", body: JSON.stringify(payload) }),
  razorpayCancel: () => request<{ ok: boolean; message: string }>("/api/billing/razorpay/cancel", { method: "POST" }),
  userPresets: () => request<{ presets: Preset[] }>("/api/presets"),

  // ---------- admin ----------

  adminStats: () => request<AdminStats>("/api/admin/stats"),
  adminUsers: (params?: { query_text?: string; role?: string; status?: string; limit?: number }) => {
    const search = new URLSearchParams();
    if (params?.query_text) search.set("query_text", params.query_text);
    if (params?.role) search.set("role", params.role);
    if (params?.status) search.set("status", params.status);
    if (params?.limit) search.set("limit", String(params.limit));
    const qs = search.toString();
    return request<{ users: AdminUser[]; total: number }>(`/api/admin/users${qs ? `?${qs}` : ""}`);
  },
  adminUserAction: (
    id: string,
    action: "approve" | "disable" | "enable" | "lock" | "unlock",
  ) => request<AdminUser>(`/api/admin/users/${id}/${action}`, { method: "POST" }),
  setUserRole: (id: string, role: Role) =>
    request<AdminUser>(`/api/admin/users/${id}/role`, {
      method: "PUT",
      body: JSON.stringify({ role }),
    }),
  setUserDelay: (id: string, alert_delay_minutes: number) =>
    request<AdminUser>(`/api/admin/users/${id}/delay`, {
      method: "PUT",
      body: JSON.stringify({ alert_delay_minutes }),
    }),
  setUserCapabilities: (id: string, add: string[], remove: string[]) =>
    request<AdminUser>(`/api/admin/users/${id}/capabilities`, {
      method: "POST",
      body: JSON.stringify({ add, remove }),
    }),
  compSubscription: (id: string, plan_code = "standard", duration_days?: number | null) =>
    request<{ ok: boolean; subscription: SubscriptionInfo }>(`/api/admin/users/${id}/subscription`, {
      method: "PUT",
      body: JSON.stringify({ plan_code, duration_days: duration_days ?? null }),
    }),
  applyPresetToUser: (id: string, preset_id: string) =>
    request<{ ok: boolean; preset: string }>(`/api/admin/users/${id}/apply-preset`, {
      method: "POST",
      body: JSON.stringify({ preset_id }),
    }),
  adminCoupons: (state?: "open" | "claimed" | "expired") =>
    request<{ coupons: Coupon[] }>(
      `/api/admin/coupons${state ? `?state=${state}` : ""}`,
    ),
  mintCoupon: (payload: { grants_role: "user" | "privileged"; duration_days?: number | null; note?: string }) =>
    request<Coupon>("/api/admin/coupons", { method: "POST", body: JSON.stringify(payload) }),
  voidCoupon: (id: string) => request<{ ok: boolean }>(`/api/admin/coupons/${id}`, { method: "DELETE" }),
  adminPresets: () => request<{ presets: Preset[] }>("/api/admin/presets"),
  createPreset: (payload: Partial<Preset> & { name: string }) =>
    request<{ id: string; name: string }>("/api/admin/presets", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  updatePreset: (id: string, patch: Partial<Preset>) =>
    request<Preset>(`/api/admin/presets/${id}`, {
      method: "PATCH",
      body: JSON.stringify(patch),
    }),
  deletePreset: (id: string) => request<{ ok: boolean }>(`/api/admin/presets/${id}`, { method: "DELETE" }),
  snapshotPreset: (payload: { source_user_id: string; name: string; description?: string; is_admin_only?: boolean }) =>
    request<{ id: string; name: string }>("/api/admin/presets/snapshot", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  egress: (days = 30) =>
    request<import("./types").EgressResponse>(`/api/admin/egress?days=${days}`),
  adminSchema: () => request<{ generated_at: string; tables: import("./types").SchemaTable[]; issues: import("./types").SchemaIssue[]; counts: { tables: number; total_bytes: number } }>("/api/admin/schema"),
};