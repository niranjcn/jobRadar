import type {
  Company,
  GeoCountry,
  Job,
  JobFilters,
  JobsResponse,
  LocationMappingResult,
  LocationMappingSettings,
  LocationPreview,
  MatchesSummary,
  Notification,
  PollRunsResult,
  Preferences,
  ScheduleResult,
  SourceResult,
  Stats,
  UnhealthySource,
} from "./types";

const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    cache: "no-store",
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText}: ${body.slice(0, 200)}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  stats: () => request<Stats>("/api/stats"),
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
    limit?: number;
    offset?: number;
  }) => {
    const search = new URLSearchParams();
    if (params?.q) search.set("q", params.q);
    if (params?.ats) search.set("ats", params.ats);
    if (params?.company) search.set("company", params.company);
    if (params?.country) search.set("country", params.country);
    if (params?.since) search.set("since", params.since);
    if (params?.limit) search.set("limit", String(params.limit));
    if (params?.offset) search.set("offset", String(params.offset));
    const qs = search.toString();
    return request<JobsResponse>(`/api/jobs${qs ? `?${qs}` : ""}`);
  },
  jobFilters: () => request<JobFilters>("/api/jobs/filters"),
  job: (id: string) => request<Job>(`/api/jobs/${id}`),
  companies: () => request<{ companies: Company[] }>("/api/companies"),
  sources: () => request<SourceResult>("/api/sources"),
  createSource: (payload: {
    company_name: string;
    url?: string;
    ats_type?: string;
    board_identifier?: string;
  }) =>
    request<{ id: string; company_name: string; ats_type: string; board_identifier: string }>(
      "/api/sources",
      { method: "POST", body: JSON.stringify(payload) },
    ),
  updateSource: (id: string, payload: { active?: boolean; board_identifier?: string }) =>
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
};