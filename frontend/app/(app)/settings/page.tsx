"use client";

import Link from "next/link";
import { RadarLoading } from "@/components/radar-loading";
import { PageHeader } from "@/components/ink/ui";
import styles from "@/components/ink/ink.module.css";
import { useCallback, useEffect, useState } from "react";
import { ApiError, api } from "@/lib/api";
import { formatInterval } from "@/lib/format";
import { useAuth } from "@/lib/auth-context";
import type { LocationMappingResult, SourceResult } from "@/lib/types";

const SECTIONS = [
  { id: "profile", label: "Profile" },
  { id: "mapping", label: "Location Mapping" },
  { id: "polling", label: "Polling" },
];

export default function SettingsPage() {
  const { me, refresh } = useAuth();
  const [sources, setSources] = useState<SourceResult | null>(null);
  const [geo, setGeo] = useState<LocationMappingResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [profileName, setProfileName] = useState("");
  const [profileEmail, setProfileEmail] = useState("");
  const [profileBusy, setProfileBusy] = useState(false);
  const [profileMsg, setProfileMsg] = useState<string | null>(null);

  const [remoteTo, setRemoteTo] = useState<string[]>([]);
  const [aliases, setAliases] = useState<[string, string][]>([]);
  const [aliasKey, setAliasKey] = useState("");
  const [aliasCode, setAliasCode] = useState("");
  const [previewInput, setPreviewInput] = useState("");
  const [preview, setPreview] = useState<{ countries: string[]; is_remote: boolean; source: string } | null>(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const load = useCallback(() => {
    Promise.all([api.sources(), api.locationMapping()])
      .then(([s, g]) => {
        setSources(s);
        setGeo(g);
        setRemoteTo(g.settings.remote_to || []);
        setAliases(Object.entries(g.settings.custom_aliases || {}));
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    if (me) {
      setProfileName(me.display_name || "");
      setProfileEmail(me.email || "");
    }
  }, [me]);

  async function saveProfile() {
    setProfileBusy(true);
    setProfileMsg(null);
    try {
      await api.updateProfile({ display_name: profileName.trim(), email: profileEmail.trim() || undefined });
      await refresh();
      setProfileMsg("Saved ✓");
      setTimeout(() => setProfileMsg(null), 2000);
    } catch (e) {
      setProfileMsg(e instanceof ApiError ? e.message.replace(/^\d+ \w+: /, "") : "Save failed");
    } finally {
      setProfileBusy(false);
    }
  }

  async function save() {
    if (!geo) return;
    setSaving(true);
    try {
      const custom: Record<string, string> = {};
      for (const [k, v] of aliases) {
        if (k.trim() && v.trim()) custom[k.trim()] = v.trim().toUpperCase();
      }
      await api.updateLocationMapping({
        enabled: geo.settings.enabled,
        remote_to: remoteTo,
        custom_aliases: custom,
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
      load();
    } finally {
      setSaving(false);
    }
  }

  async function runPreview() {
    if (!previewInput.trim()) return;
    const res = await api.previewLocation(previewInput.trim());
    setPreview(res);
  }

  if (loading)
    return (
      <div className={styles.content}>
        <RadarLoading label="Loading settings…" />
      </div>
    );

  return (
    <div className={styles.content}>
      <PageHeader
        eyebrow="System"
        title="Settings"
        desc="Configure your JobQuest environment — profile, location mapping and polling."
      />

      <div className={styles.setLayout}>
        <nav className={styles.setNav} aria-label="Settings sections">
          {SECTIONS.map((s) => (
            <a key={s.id} href={`#${s.id}`} className={styles.setNavBtn}>
              {s.label}
            </a>
          ))}
        </nav>
        <div style={{ minWidth: 0, display: "flex", flexDirection: "column", gap: 20 }}>

      <section id="profile" className="card space-y-4 p-5" style={{ scrollMarginTop: 76 }}>
        <h2 className="text-[15px] font-semibold">Profile</h2>
        <div className="space-y-3">
          <input className="search-input w-full" placeholder="Display name" value={profileName} onChange={(e) => setProfileName(e.target.value)} />
          <input className="search-input w-full" placeholder="Email" type="email" value={profileEmail} onChange={(e) => setProfileEmail(e.target.value)} />
          <button onClick={saveProfile} disabled={profileBusy} className="btn-primary w-full">
            {profileBusy ? "Saving…" : "Save profile"}
          </button>
          {profileMsg && <p className={`text-sm ${profileMsg.includes("✓") ? "text-success" : "text-danger"}`}>{profileMsg}</p>}
        </div>
      </section>

      <section id="polling" className="card space-y-4 p-5" style={{ scrollMarginTop: 76 }}>
        <h2 className="text-[15px] font-semibold">Polling schedule (APScheduler)</h2>
        {sources ? (
          <ul className="space-y-2 text-sm text-text-secondary">
            {Object.entries(sources.intervals).map(([ats, seconds]) => (
              <li key={ats} className="flex items-center justify-between border-b border-border/50 pb-2 last:border-0">
                <span className="capitalize">{ats}</span>
                <span className="text-text-muted">{formatInterval(seconds)}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-text-muted">No intervals loaded (is the API running?).</p>
        )}
        <p className="text-xs text-text-muted">
          Intervals are configured via <code>POLL_INTERVAL_&lt;ATS&gt;_SECONDS</code> and{" "}
          <code>POLL_INTERVAL_SECONDS</code> in the backend .env.
        </p>
      </section>

      {geo && (
        <section id="mapping" className="card space-y-4 p-5" style={{ scrollMarginTop: 76 }}>
          <div className="flex items-center justify-between">
            <h2 className="text-[15px] font-semibold">Location → Country mapping</h2>
            <label className="flex items-center gap-2 text-sm text-text-secondary">
              <input
                type="checkbox"
                checked={geo.settings.enabled}
                onChange={(e) => setGeo({ ...geo, settings: { ...geo.settings, enabled: e.target.checked } })}
              />
              Enabled
            </label>
          </div>
          <p className="text-xs text-text-muted">
            Job locations are mapped to countries using a bundled index (
            {geo.index_stats.countries.toLocaleString()} countries,{" "}
            {geo.index_stats.states.toLocaleString()} states,{" "}
            {geo.index_stats.cities.toLocaleString()} cities from the{" "}
            <a
              className="underline"
              href="https://github.com/dr5hn/countries-states-cities-database"
              target="_blank"
              rel="noreferrer"
            >
              countries-states-cities database
            </a>
            ). Stored on each job, then used for location matching.
          </p>

          <div>
            <p className="mb-2 text-xs uppercase tracking-wide text-text-muted">
              Remote jobs map to countries (ISO codes)
            </p>
            <div className="flex flex-wrap gap-1.5">
              {remoteTo.map((code) => (
                <span key={code} className="flex items-center gap-1 rounded bg-elevated px-2 py-1 text-sm text-text-secondary">
                  {code}
                  <button
                    onClick={() => setRemoteTo(remoteTo.filter((c) => c !== code))}
                    className="text-text-muted hover:text-danger"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
            <input
              className="search-input mt-2 w-full"
              placeholder="Add ISO code e.g. IN (press Enter)"
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  const v = (e.target as HTMLInputElement).value.trim().toUpperCase();
                  if (v && !remoteTo.includes(v)) setRemoteTo([...remoteTo, v]);
                  (e.target as HTMLInputElement).value = "";
                }
              }}
            />
          </div>

          <div>
            <p className="mb-2 text-xs uppercase tracking-wide text-text-muted">
              Custom aliases (keyword → ISO code)
            </p>
            <div className="space-y-1.5">
              {aliases.map(([k, v]) => (
                <div key={k} className="flex items-center gap-2 text-sm text-text-secondary">
                  <span className="rounded bg-elevated px-2 py-1">
                    {k} → {v}
                  </span>
                  <button onClick={() => setAliases(aliases.filter(([a]) => a !== k))} className="text-text-muted hover:text-danger">
                    ×
                  </button>
                </div>
              ))}
            </div>
            <div className="mt-2 flex gap-2">
              <input
                className="search-input flex-1"
                placeholder="keyword, e.g. gotham"
                value={aliasKey}
                onChange={(e) => setAliasKey(e.target.value)}
              />
              <input
                className="search-input w-28"
                placeholder="ISO, e.g. US"
                value={aliasCode}
                onChange={(e) => setAliasCode(e.target.value)}
              />
              <button
                className="btn-primary"
                onClick={() => {
                  if (aliasKey.trim() && aliasCode.trim()) {
                    setAliases([...aliases.filter(([a]) => a !== aliasKey.trim()), [aliasKey.trim(), aliasCode.trim().toUpperCase()]]);
                    setAliasKey("");
                    setAliasCode("");
                  }
                }}
              >
                Add
              </button>
            </div>
          </div>

          <div>
            <p className="mb-2 text-xs uppercase tracking-wide text-text-muted">Test a location</p>
            <div className="flex gap-2">
              <input
                className="search-input flex-1"
                placeholder="e.g. Remote - Germany, BLR, Bengaluru, India"
                value={previewInput}
                onChange={(e) => setPreviewInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    runPreview();
                  }
                }}
              />
              <button className="btn-primary" onClick={runPreview}>
                Test
              </button>
            </div>
            {preview && (
              <div className="mt-2 text-sm text-text-secondary">
                {preview.countries.length ? (
                  <span>
                    → <span className="font-semibold text-text">{preview.countries.join(", ")}</span>
                    {preview.is_remote && <span className="ml-2 text-accent">remote</span>}
                    <span className="ml-2 text-text-muted">({preview.source})</span>
                  </span>
                ) : (
                  <span className="text-text-muted">No country detected</span>
                )}
              </div>
            )}
          </div>

          <div className="flex items-center gap-3">
            <button onClick={save} disabled={saving} className="btn-primary">
              {saving ? "Saving…" : "Save Mapping"}
            </button>
            {saved && <span className="text-sm text-success">Saved ✓</span>}
          </div>
        </section>
      )}

      <section className="card mt-6 space-y-3 p-5 text-sm text-text-secondary">
        <Link href="/sources" className="block hover:text-primary">→ Manage career sources</Link>
        <Link href="/schedule" className="block hover:text-primary">→ Polling schedule & next checks</Link>
        <Link href="/preferences" className="block hover:text-primary">→ Edit matching preferences</Link>
      </section>

      <p className="text-xs text-text-muted">
        Backend API: <code>{process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}</code>
      </p>
        </div>
      </div>
    </div>
  );
}
