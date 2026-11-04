import { describe, expect, it } from "vitest";
import { readdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

// Legal guardrails: fail the build if anyone reintroduces a per-visitor
// liability the audit removed. See layout.tsx (fonts) and privacy §9 (cookies).

const TEST_DIR = dirname(fileURLToPath(import.meta.url));
const FRONTEND_ROOT = dirname(TEST_DIR);
const SCAN_DIRS = ["app", "components", "lib", "public"];

function walk(dir: string, out: string[] = []): string[] {
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    if (entry === "node_modules" || entry === ".next") continue;
    const st = statSync(full);
    if (st.isDirectory()) walk(full, out);
    else if (/\.(tsx?|css|mjs|js|html)$/.test(entry)) out.push(full);
  }
  return out;
}

describe("legal guards", () => {
  it("serves all fonts from this origin (no Google Fonts CDN requests)", () => {
    // next/font/google self-hosts at build time into /_next/static. A <link>
    // to fonts.googleapis.com/fonts.gstatic.com would leak every visitor's IP
    // to Google (GDPR risk: LG München, €100/visitor). Ban those hosts here.
    const files = SCAN_DIRS.flatMap((d) => walk(join(FRONTEND_ROOT, d)));
    const offenders: string[] = [];
    for (const file of files) {
      const content = readFileSync(file, "utf8");
      // Match real requests only (scheme + host), not explanatory comments.
      if (/https?:\/\/(fonts\.googleapis\.com|fonts\.gstatic\.com)/.test(content)) {
        offenders.push(file);
      }
    }
    expect(offenders).toEqual([]);
  });

  it("ships no session-replay / keystroke-recording trackers", () => {
    // Recording keystrokes without consent can count as wiretapping (CIPA,
    // $5k/session). No replay library may be added without explicit consent
    // UI + input masking. This test bans the known vendors outright.
    const pkg = JSON.parse(readFileSync(join(FRONTEND_ROOT, "package.json"), "utf8"));
    const deps = Object.keys(pkg.dependencies ?? {}).concat(
      Object.keys(pkg.devDependencies ?? {}),
    );
    const replayPkgs = [
      "@posthog",
      "posthog-js",
      "@hotjar",
      "fullstory",
      "logrocket",
      "@logrocket",
      "clarity",
      "@microsoft/clarity",
      "mixpanel-browser",
      "amplitude",
      "@amplitude",
      "rrweb",
      "@rrweb",
    ];
    expect(deps.filter((d) => replayPkgs.some((r) => d.includes(r)))).toEqual([]);

    const files = SCAN_DIRS.flatMap((d) => walk(join(FRONTEND_ROOT, d)));
    const offenders: string[] = [];
    for (const file of files) {
      if (file.endsWith("legal-guards.test.ts")) continue;
      const content = readFileSync(file, "utf8");
      if (/hotjar|fullstory|logrocket|posthog|microsoft\/clarity|mixpanel|amplitude|rrweb/i.test(content)) {
        offenders.push(file);
      }
    }
    expect(offenders).toEqual([]);
  });
});
