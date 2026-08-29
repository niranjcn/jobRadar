"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { Preset, PresetField } from "@/lib/types";

const FIELD_LABELS: { field: PresetField; label: string; placeholder: string }[] = [
  { field: "roles", label: "Roles", placeholder: "e.g. Backend Engineer (Enter to add)" },
  { field: "keywords", label: "Skills", placeholder: "e.g. Python (Enter to add)" },
  { field: "locations", label: "Locations", placeholder: "e.g. Remote, India, Dubai (Enter)" },
  { field: "seniority", label: "Experience", placeholder: "e.g. Entry level (Enter)" },
];

export default function OnboardingPage() {
  const router = useRouter();
  const { me, refresh } = useAuth();
  const [presets, setPresets] = useState<Preset[]>([]);
  const [applied, setApplied] = useState<string | null>(null);
  const [values, setValues] = useState<Record<PresetField, string[]>>({
    roles: [],
    keywords: [],
    locations: [],
    seniority: [],
    excluded_companies: [],
    excluded_roles: [],
  });
  const [drafts, setDrafts] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState(false);
  const [done, setDone] = useState(false);
  const [profileName, setProfileName] = useState("");
  const [profileEmail, setProfileEmail] = useState("");
  const [profileError, setProfileError] = useState<string | null>(null);
  const needsProfile = !me?.email || !me?.display_name;

  useEffect(() => {
    api.userPresets().then((r) => setPresets(r.presets));
  }, []);

  useEffect(() => {
    if (me) {
      setProfileName(me.display_name || "");
      setProfileEmail(me.email || "");
    }
  }, [me]);

  function applyPreset(preset: Preset) {
    setApplied(preset.name);
    setValues((prev) => ({
      ...prev,
      roles: preset.roles ?? [],
      keywords: preset.keywords ?? [],
      locations: preset.locations ?? [],
      seniority: preset.seniority ?? [],
      excluded_roles: preset.excluded_roles ?? [],
      excluded_companies: preset.excluded_companies ?? [],
    }));
  }

  function addTag(field: PresetField) {
    const raw = drafts[field]?.trim();
    if (!raw) return;
    setDrafts((d) => ({ ...d, [field]: "" }));
    setValues((v) => ({
      ...v,
      [field]: v[field].some((x) => x.toLowerCase() === raw.toLowerCase()) ? v[field] : [...v[field], raw],
    }));
  }

  function removeTag(field: PresetField, value: string) {
    setValues((v) => ({ ...v, [field]: v[field].filter((x) => x !== value) }));
  }

  async function save() {
    setSaving(true);
    setProfileError(null);
    try {
      // Initial setup: save name/email if telegram user and missing
      if (needsProfile && (profileName.trim() !== (me?.display_name || "") || profileEmail.trim() !== (me?.email || ""))) {
        if (profileName.trim()) {
          try {
            await api.updateProfile({ display_name: profileName.trim(), email: profileEmail.trim() || undefined });
            await refresh();
          } catch (e) {
            const msg = e instanceof Error ? e.message.replace(/^\d+ \w+: /, "") : "Could not save profile";
            setProfileError(msg);
            setSaving(false);
            return;
          }
        }
      }
      await api.updatePreferences({
        roles: values.roles,
        keywords: values.keywords,
        locations: values.locations,
        seniority: values.seniority,
        excluded_companies: values.excluded_companies,
        excluded_roles: values.excluded_roles,
        notify_telegram: true,
        notify_email: true,
        alert_frequency: "immediate",
        telegram_scope: "matched",
        email_scope: "matched",
        notify_first_check: true,
      });
      setDone(true);
    } finally {
      setSaving(false);
    }
  }

  if (done) {
    return (
      <div className="mx-auto max-w-xl p-8 text-center">
        <h1 className="text-2xl font-semibold">You&apos;re all set 🎉</h1>
        <p className="mt-3 text-sm text-text-secondary">Your matches are building now. You&apos;ll get alerts via email based on your preferences.</p>
        <button onClick={() => router.push("/dashboard")} className="btn-primary mt-8">
          Go to dashboard
        </button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl p-8">
      <p className="font-mono text-xs uppercase tracking-[0.18em] text-text-muted">Welcome{me?.display_name ? `, ${me.display_name}` : ""}</p>
      <h1 className="mt-1 text-[28px] font-semibold">Set your job preferences</h1>
      <p className="mt-1 text-sm text-text-secondary">
        Start from a quick-start preset or build your own. You can fine-tune everything later.
      </p>

      {needsProfile && (
        <div className="card mt-6 space-y-4 p-5">
          <h2 className="text-[15px] font-semibold">Complete your profile</h2>
          <p className="text-sm text-text-secondary">Confirm your display name and email.</p>
          <div className="grid gap-3 sm:grid-cols-2">
            <div>
              <label className="text-xs text-text-muted">Display name</label>
              <input className="search-input mt-1 w-full" value={profileName} onChange={(e) => setProfileName(e.target.value)} placeholder="Your name" />
            </div>
            <div>
              <label className="text-xs text-text-muted">Email</label>
              <input className="search-input mt-1 w-full" type="email" value={profileEmail} onChange={(e) => setProfileEmail(e.target.value)} placeholder="you@example.com" />
            </div>
          </div>
          {profileError && <p className="text-sm text-danger">{profileError}</p>}
        </div>
      )}

      {presets.length > 0 && (
        <div className="mt-6 flex flex-wrap gap-2">
          {presets.map((p) => (
            <button
              key={p.id}
              onClick={() => applyPreset(p)}
              title={p.description}
              className={`rounded-full border px-4 py-1.5 text-sm transition-colors ${
                applied === p.name
                  ? "border-primary bg-primary/15 text-primary"
                  : "border-border text-text-secondary hover:border-primary hover:text-text"
              }`}
            >
              {p.name}
            </button>
          ))}
        </div>
      )}

      <div className="mt-8 space-y-6">
        {FIELD_LABELS.map(({ field, label, placeholder }) => (
          <section key={field} className="card space-y-3 p-5">
            <h2 className="text-[15px] font-semibold">{label}</h2>
            <div className="flex flex-wrap gap-1.5">
              {values[field].map((v) => (
                <span key={v} className="flex items-center gap-1 rounded bg-elevated px-2 py-1 text-sm text-text-secondary">
                  {v}
                  <button onClick={() => removeTag(field, v)} className="text-text-muted hover:text-danger">
                    ×
                  </button>
                </span>
              ))}
            </div>
            <div className="flex gap-2">
              <input
                className="search-input w-full"
                placeholder={placeholder}
                value={drafts[field] || ""}
                onChange={(e) => setDrafts((d) => ({ ...d, [field]: e.target.value }))}
                onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), addTag(field))}
              />
            </div>
            {field === "locations" && values.locations.length === 0 && (
              <p className="text-xs text-warning">Locations act as a hard filter — leave empty to see jobs everywhere.</p>
            )}
          </section>
        ))}
      </div>

      <div className="mt-8 flex items-center gap-3">
        <button onClick={save} disabled={saving} className="btn-primary">
          {saving ? "Saving…" : "Save & continue"}
        </button>
        <button onClick={() => setDone(true)} className="btn-ghost text-sm text-text-muted">
          Skip for now
        </button>
      </div>
    </div>
  );
}
