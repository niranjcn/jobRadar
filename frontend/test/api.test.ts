import { afterEach, describe, expect, it, vi } from "vitest";
import { api } from "../lib/api";

function mockFetch(response: unknown, ok = true) {
  globalThis.fetch = vi.fn().mockResolvedValue({
    ok,
    status: ok ? 200 : 500,
    statusText: ok ? "OK" : "Server Error",
    text: async () => (ok ? "" : "boom"),
    json: async () => response,
  } as unknown as Response);
}

afterEach(() => {
  vi.restoreAllMocks();
});

describe("api client", () => {
  it("builds query string for jobs", async () => {
    mockFetch({ jobs: [], total: 0, limit: 10, offset: 0 });
    await api.jobs({ q: "engineer", ats: "greenhouse", limit: 10 });
    const [url] = (globalThis.fetch as any).mock.calls[0];
    expect(String(url)).toContain("/api/jobs?");
    expect(String(url)).toContain("q=engineer");
    expect(String(url)).toContain("ats=greenhouse");
    expect(String(url)).toContain("limit=10");
  });

  it("builds query string for public jobs with all filters", async () => {
    mockFetch({ jobs: [], total: 0, limit: 20, offset: 0 });
    await api.publicJobs({
      q: "engineer",
      ats: "emirates",
      company: "Emirates Group",
      country: "AE",
      since: "2026-01-01T00:00:00.000Z",
      remote_only: true,
      limit: 20,
    });
    const [url] = (globalThis.fetch as any).mock.calls[0];
    expect(String(url)).toContain("/api/public/jobs?");
    expect(String(url)).toContain("q=engineer");
    expect(String(url)).toContain("ats=emirates");
    expect(String(url)).toContain("remote_only=true");
  });

  it("fetches a single public job", async () => {
    mockFetch({ id: "1", title: "Engineer" });
    await api.publicJob("1");
    const [url] = (globalThis.fetch as any).mock.calls[0];
    expect(String(url)).toContain("/api/public/jobs/1");
  });

  it("calls stats with no query", async () => {
    mockFetch({ jobs_total: 10, jobs_new_7d: 2, companies: 3, matches: 1, avg_match_score: 80 });
    await api.stats();
    const [url] = (globalThis.fetch as any).mock.calls[0];
    expect(String(url)).toBe("http://localhost:8000/api/stats");
  });

  it("POSTs source creation", async () => {
    mockFetch({ id: "1", company_name: "Adobe", ats_type: "greenhouse", board_identifier: "adobe" });
    await api.createSource({ company_name: "Adobe" });
    const [url, init] = (globalThis.fetch as any).mock.calls[0];
    expect(String(url)).toContain("/api/sources");
    expect(init.method).toBe("POST");
    expect(JSON.parse(init.body)).toEqual({ company_name: "Adobe" });
  });

  it("throws on non-ok response", async () => {
    mockFetch({}, false);
    await expect(api.stats()).rejects.toThrow(/500/);
  });

  it("gets location mapping settings", async () => {
    mockFetch({
      settings: { enabled: true, remote_to: ["IN"], custom_aliases: {} },
      index_stats: { countries: 250, states: 5106, cities: 135657 },
    });
    await api.locationMapping();
    const [url] = (globalThis.fetch as any).mock.calls[0];
    expect(String(url)).toContain("/api/settings/location-mapping");
  });

  it("updates location mapping settings", async () => {
    mockFetch({ ok: true, settings: { enabled: true, remote_to: ["IN"], custom_aliases: { gotham: "US" } } });
    await api.updateLocationMapping({ enabled: true, remote_to: ["IN"], custom_aliases: { gotham: "US" } });
    const [url, init] = (globalThis.fetch as any).mock.calls[0];
    expect(String(url)).toContain("/api/settings/location-mapping");
    expect(init.method).toBe("PUT");
    expect(JSON.parse(init.body)).toEqual({ enabled: true, remote_to: ["IN"], custom_aliases: { gotham: "US" } });
  });

  it("previews a location", async () => {
    mockFetch({ location: "Bengaluru, India", countries: ["IN"], is_remote: false, matched: [], source: "country" });
    await api.previewLocation("Bengaluru, India");
    const [url, init] = (globalThis.fetch as any).mock.calls[0];
    expect(String(url)).toContain("/api/settings/location-mapping/preview");
    expect(init.method).toBe("POST");
    expect(JSON.parse(init.body)).toEqual({ location: "Bengaluru, India" });
  });
});
