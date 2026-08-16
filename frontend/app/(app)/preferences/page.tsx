"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { CountrySelect } from "@/components/country-select";
import { RadarLoading } from "@/components/radar-loading";
import { api } from "@/lib/api";
import type { GeoCountry, Preferences } from "@/lib/types";

const ROLES_PRESET = ["Software Engineer", "Backend Engineer", "DevOps Engineer", "SRE", "Platform Engineer", "MTS", "Full Stack Engineer", "Cloud Engineer"];
const SKILLS_PRESET = ["Python", "Go", "Java", "AWS", "Docker", "Kubernetes", "Terraform", "PostgreSQL", "Linux"];
const SENIORITY_PRESET = ["Internship", "New Grad", "Entry", "Junior", "Mid", "Senior", "Lead"];
const LOCATIONS_PRESET = ["Remote", "India", "United States", "Bengaluru", "Hyderabad", "Mumbai", "Delhi", "Pune", "Chennai", "Dubai", "Singapore", "Germany"];

export default function PreferencesPage() {
  const [prefs, setPrefs] = useState<Preferences | null>(null);
  const [countries, setCountries] = useState<GeoCountry[]>([]);
  const [countryPreview, setCountryPreview] = useState<Record<string, string[]>>({});
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const load = useCallback(() => {
    api.preferences().then(setPrefs);
  }, []);

  useEffect(() => {
    load();
    api.geoCountries().then((res) => setCountries(res.countries));
  }, [load]);

  const locations = useMemo(() => (prefs?.locations || []).slice(0, 12), [prefs?.locations]);

  useEffect(() => {
    if (locations.length === 0) return;
    const timer = setTimeout(() => {
      let cancelled = false;
      Promise.all(
        locations.map((loc) =>
          api
            .previewLocation(loc)
            .then((r) => ({ loc, codes: r.countries }))
            .catch(() => ({ loc, codes: [] })),
        ),
      ).then((results) => {
        if (cancelled) return;
        const next: Record<string, string[]> = {};
        for (const { loc, codes } of results) next[loc] = codes;
        setCountryPreview(next);
      });
      return () => {
        cancelled = true;
      };
    }, 250);
    return () => clearTimeout(timer);
  }, [locations]);

  function addTag(field: keyof Preferences, value: string) {
    if (!prefs) return;
    if (!value.trim()) return;
    const list = prefs[field] as string[];
    if (list.some((v) => v.toLowerCase() === value.trim().toLowerCase())) return;
    setPrefs({ ...prefs, [field]: [...list, value.trim()] });
  }

  function addBulk(field: keyof Preferences, value: string) {
    if (!prefs) return;
    const items = value
      .split(/[,\n]/)
      .map((s) => s.trim())
      .filter(Boolean);
    if (items.length === 0) return;
    const list = prefs[field] as string[];
    const next = [...list];
    for (const item of items) {
      if (!next.some((v) => v.toLowerCase() === item.toLowerCase())) {
        next.push(item);
      }
    }
    setPrefs({ ...prefs, [field]: next });
  }

  function removeTag(field: keyof Preferences, value: string) {
    if (!prefs) return;
    const list = prefs[field] as string[];
    setPrefs({ ...prefs, [field]: list.filter((v) => v !== value) });
  }

  function clearAll(field: keyof Preferences) {
    if (!prefs) return;
    setPrefs({ ...prefs, [field]: [] });
  }

  function addCountry(name: string) {
    if (!name.trim()) return;
    addTag("locations", name);
  }

  async function save() {
    if (!prefs) return;
    setSaving(true);
    try {
      await api.updatePreferences(prefs);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } finally {
      setSaving(false);
    }
  }

  if (!prefs) return <RadarLoading label="Loading preferences…" />;

  const TagInput = ({ field, placeholder, presets }: { field: keyof Preferences; placeholder: string; presets: string[] }) => (
    <div>
      <div className="flex flex-wrap gap-1.5">
        {(prefs[field] as string[]).map((v) => (
          <span key={v} className="flex items-center gap-1 rounded bg-elevated px-2 py-1 text-sm text-text-secondary">
            {v}
            <button onClick={() => removeTag(field, v)} className="text-text-muted hover:text-danger">
              ×
            </button>
          </span>
        ))}
      </div>
      <div className="mt-2 flex gap-2">
        <input
          className="search-input w-full"
          placeholder={placeholder}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              addTag(field, (e.target as HTMLInputElement).value);
              (e.target as HTMLInputElement).value = "";
            }
          }}
        />
        {(prefs[field] as string[]).length > 0 && (
          <button onClick={() => clearAll(field)} className="btn-ghost shrink-0 whitespace-nowrap px-3 text-xs">
            Clear all
          </button>
        )}
      </div>
      <div className="mt-2 flex flex-wrap gap-1.5">
        {presets
          .filter((p) => !(prefs[field] as string[]).some((v) => v.toLowerCase() === p.toLowerCase()))
          .map((p) => (
            <button
              key={p}
              onClick={() => addTag(field, p)}
              className="rounded border border-border px-2 py-0.5 text-xs text-text-muted hover:border-primary hover:text-text"
            >
              + {p}
            </button>
          ))}
      </div>
    </div>
  );

  const BulkTagInput = ({ field, placeholder, presets }: { field: keyof Preferences; placeholder: string; presets: string[] }) => {
    const [draft, setDraft] = useState("");
    return (
      <div>
        <div className="flex flex-wrap gap-1.5">
          {(prefs[field] as string[]).map((v) => (
            <span key={v} className="flex items-center gap-1 rounded bg-elevated px-2 py-1 text-sm text-text-secondary">
              {v}
              <button onClick={() => removeTag(field, v)} className="text-text-muted hover:text-danger">
                ×
              </button>
            </span>
          ))}
        </div>
        <textarea
          className="search-input mt-2 w-full resize-y"
          rows={4}
          placeholder={placeholder}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
              e.preventDefault();
              addBulk(field, draft);
              setDraft("");
            }
          }}
        />
        <div className="mt-2 flex gap-2">
          <button
            onClick={() => {
              addBulk(field, draft);
              setDraft("");
            }}
            className="btn-ghost"
          >
            Add roles
          </button>
          {(prefs[field] as string[]).length > 0 && (
            <button onClick={() => clearAll(field)} className="btn-ghost text-xs">
              Clear all
            </button>
          )}
        </div>
        <div className="mt-2 flex flex-wrap gap-1.5">
          {presets
            .filter((p) => !(prefs[field] as string[]).some((v) => v.toLowerCase() === p.toLowerCase()))
            .map((p) => (
              <button
                key={p}
                onClick={() => addTag(field, p)}
                className="rounded border border-border px-2 py-0.5 text-xs text-text-muted hover:border-primary hover:text-text"
              >
                + {p}
              </button>
            ))}
        </div>
      </div>
    );
  };

  return (
    <div className="mx-auto max-w-3xl p-8">
      <h1 className="text-[28px] font-semibold">Your Job Preferences</h1>
      <p className="mt-1 text-sm text-text-secondary">
        Locations act as a hard filter — a job must be in one of your selected locations. Roles, skills,
        and experience are OR'd: a job matches if it hits ANY of them.
      </p>

      <div className="mt-8 space-y-8">
        <section className="card space-y-4 p-5">
          <h2 className="text-[15px] font-semibold">Roles</h2>
          <BulkTagInput
            field="roles"
            placeholder={"Paste roles separated by commas, e.g. Software Engineer, SDE I, MTS, Backend Developer…\nPress Ctrl+Enter to add."}
            presets={ROLES_PRESET}
          />
        </section>

        <section className="card space-y-4 p-5">
          <h2 className="text-[15px] font-semibold">Skills</h2>
          <TagInput field="keywords" placeholder="e.g. Python (press Enter)" presets={SKILLS_PRESET} />
        </section>

        <section className="card space-y-4 p-5">
          <h2 className="text-[15px] font-semibold">
            Locations{" "}
            <span className="text-xs font-normal text-text-muted">
              (cities and states map to their country automatically — e.g. Bengaluru→India, Austin→USA)
            </span>
          </h2>
          <div>
            <div className="flex flex-wrap gap-1.5">
              {(prefs.locations as string[]).map((v) => (
                <span key={v} className="flex items-center gap-1.5 rounded bg-elevated px-2 py-1 text-sm text-text-secondary">
                  {v}
                  {countryPreview[v] && countryPreview[v].length > 0 && (
                    <span className="text-xs text-text-muted">→ {countryPreview[v].join(", ")}</span>
                  )}
                  <button onClick={() => removeTag("locations", v)} className="text-text-muted hover:text-danger">
                    ×
                  </button>
                </span>
              ))}
            </div>
            <input
              className="search-input mt-2 w-full"
              placeholder="e.g. Remote, India, Bengaluru, Austin (press Enter)"
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  addTag("locations", (e.target as HTMLInputElement).value);
                  (e.target as HTMLInputElement).value = "";
                }
              }}
            />
            {(prefs.locations as string[]).length > 0 && (
              <button onClick={() => clearAll("locations")} className="btn-ghost mt-2 text-xs">
                Clear all locations
              </button>
            )}
            <div className="mt-2 flex flex-wrap gap-1.5">
              {LOCATIONS_PRESET.filter((p) => !(prefs.locations as string[]).some((v) => v.toLowerCase() === p.toLowerCase())).map((p) => (
                <button
                  key={p}
                  onClick={() => addTag("locations", p)}
                  className="rounded border border-border px-2 py-0.5 text-xs text-text-muted hover:border-primary hover:text-text"
                >
                  + {p}
                </button>
              ))}
            </div>
            <div className="mt-3 border-t border-border pt-3">
              <p className="mb-1.5 text-xs uppercase tracking-wide text-text-muted">Add a country</p>
              <CountrySelect countries={countries} onSelect={addCountry} />
            </div>
          </div>
        </section>

        <section className="card space-y-4 p-5">
          <h2 className="text-[15px] font-semibold">Experience</h2>
          <TagInput field="seniority" placeholder="e.g. Senior (press Enter)" presets={SENIORITY_PRESET} />
        </section>

        <section className="card space-y-4 p-5">
          <h2 className="text-[15px] font-semibold">Exclude roles</h2>
          <p className="text-xs text-text-muted">
            Jobs whose title contains any of these terms will never match. E.g. add{" "}
            <code>staff</code>, <code>principal</code>, <code>lead</code> so a &quot;Staff Software
            Engineer&quot; doesn&apos;t match your &quot;Software Engineer&quot; role.
          </p>
          <BulkTagInput
            field="excluded_roles"
            placeholder={"Paste excluded role terms separated by commas, e.g. staff, principal, lead, senior…\nPress Ctrl+Enter to add."}
            presets={["staff", "principal", "lead", "senior", "manager", "director"]}
          />
        </section>

        <section className="card space-y-4 p-5">
          <h2 className="text-[15px] font-semibold">Excluded companies</h2>
          <TagInput field="excluded_companies" placeholder="e.g. Stripe (press Enter)" presets={[]} />
        </section>

        <section className="card space-y-4 p-5">
          <h2 className="text-[15px] font-semibold">Notification preferences</h2>
          <div className="flex items-center gap-6">
            <label className="flex items-center gap-2 text-sm text-text-secondary">
              <input
                type="checkbox"
                checked={prefs.notify_telegram}
                onChange={(e) => setPrefs({ ...prefs, notify_telegram: e.target.checked })}
              />
              Telegram
            </label>
            <label className="flex items-center gap-2 text-sm text-text-secondary">
              <input
                type="checkbox"
                checked={prefs.notify_email}
                onChange={(e) => setPrefs({ ...prefs, notify_email: e.target.checked })}
              />
              Email
            </label>
          </div>
          <div>
            <p className="mb-2 text-xs uppercase tracking-wide text-text-muted">Alert frequency</p>
            <div className="flex flex-wrap gap-2">
              {["immediate", "every 6 hours", "daily digest"].map((f) => (
                <button
                  key={f}
                  onClick={() => setPrefs({ ...prefs, alert_frequency: f })}
                  className={`rounded px-3 py-1.5 text-sm transition-colors ${
                    prefs.alert_frequency === f
                      ? "bg-primary text-white"
                      : "border border-border text-text-secondary hover:border-primary"
                  }`}
                >
                  {f.charAt(0).toUpperCase() + f.slice(1)}
                </button>
              ))}
            </div>
          </div>
        </section>

        <div className="flex items-center gap-3">
          <button onClick={save} disabled={saving} className="btn-primary">
            {saving ? "Saving…" : "Save Changes"}
          </button>
          {saved && <span className="text-sm text-success">Saved ✓</span>}
        </div>
      </div>
    </div>
  );
}