import { describe, expect, it } from "vitest";
import {
  atsLabel,
  avatarColor,
  countryName,
  fmtCompact,
  formatInterval,
  initials,
  pctChange,
  shortDate,
  statusMeta,
  timeAgo,
} from "../lib/format";

describe("format helpers", () => {
  it("countryName resolves ISO codes", () => {
    expect(countryName("IN")).toBe("India");
    expect(countryName("us")).toBe("United States");
    expect(countryName("DE")).toBe("Germany");
    expect(countryName("")).toBe("");
    expect(countryName("Australia")).toBe("Australia");
    expect(countryName("CZECH REPUBLIC")).toBe("Czech Republic");
  });

  it("fmtCompact / pctChange / shortDate", () => {
    expect(fmtCompact(12400)).toBe("12.4K");
    expect(fmtCompact(900)).toBe("900");
    expect(pctChange([10, 10], [5, 5])).toBe(100);
    expect(pctChange([5], [5])).toBeNull();
    expect(pctChange([0], [0])).toBeNull();
    expect(shortDate("2026-09-12")).toBe("Sep 12");
  });

  it("initials", () => {
    expect(initials("Adobe")).toBe("AD");
    expect(initials("Nike")).toBe("NI");
    expect(initials("Salesforce")).toBe("SA");
    expect(initials("")).toBe("?");
    expect(initials("Open AI")).toBe("OA");
  });

  it("avatarColor is stable and in palette", () => {
    expect(avatarColor("Adobe")).toBe(avatarColor("Adobe"));
    expect(avatarColor("X")).toMatch(/^(bg|text)-/);
  });

  it("timeAgo", () => {
    expect(timeAgo(null)).toBe("—");
    expect(timeAgo(undefined)).toBe("—");
    expect(timeAgo("garbage")).toBe("—");
    const now = Date.now();
    expect(timeAgo(new Date(now - 2 * 60 * 1000).toISOString())).toBe("2m ago");
    expect(timeAgo(new Date(now - 3 * 3600 * 1000).toISOString())).toBe("3h ago");
    expect(timeAgo(new Date(now - 5 * 86400 * 1000).toISOString())).toBe("5d ago");
  });

  it("formatInterval", () => {
    expect(formatInterval(1800)).toBe("Every 30m");
    expect(formatInterval(3600)).toBe("Every 1h");
    expect(formatInterval(7200)).toBe("Every 2h");
    expect(formatInterval(900)).toBe("Every 15m");
  });

  it("atsLabel", () => {
    expect(atsLabel("greenhouse")).toBe("Greenhouse");
    expect(atsLabel("workday")).toBe("Workday");
    expect(atsLabel("google")).toBe("Google");
    expect(atsLabel("amazon")).toBe("Amazon");
    expect(atsLabel("emirates")).toBe("Emirates");
    expect(atsLabel("unknown")).toBe("unknown");
  });

  it("statusMeta", () => {
    expect(statusMeta("healthy")).toMatchObject({ label: "Healthy" });
    expect(statusMeta("stale")).toMatchObject({ label: "Stale" });
    expect(statusMeta("never")).toMatchObject({ label: "Never checked" });
  });
});
