"use client";

import { useCallback, useEffect, useState } from "react";
import { Modal } from "@/components/admin-modal";
import { PageHeader } from "@/components/ink/ui";
import styles from "@/components/ink/ink.module.css";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { errText } from "@/lib/format";
import type { Preset, PresetField } from "@/lib/types";

const FIELDS: { field: PresetField; label: string }[] = [
  { field: "roles", label: "Roles" },
  { field: "keywords", label: "Skills" },
  { field: "locations", label: "Locations" },
  { field: "seniority", label: "Experience" },
  { field: "excluded_companies", label: "Excluded companies" },
  { field: "excluded_roles", label: "Excluded roles" },
];

type Draft = {
  id?: string;
  name: string;
  description: string;
  is_admin_only: boolean;
} & Record<PresetField, string>;

function toDraft(p?: Preset): Draft {
  return {
    id: p?.id,
    name: p?.name ?? "",
    description: p?.description ?? "",
    is_admin_only: p?.is_admin_only ?? false,
    roles: (p?.roles ?? []).join(", "),
    keywords: (p?.keywords ?? []).join(", "),
    locations: (p?.locations ?? []).join(", "),
    seniority: (p?.seniority ?? []).join(", "),
    excluded_companies: (p?.excluded_companies ?? []).join(", "),
    excluded_roles: (p?.excluded_roles ?? []).join(", "),
  };
}

const splitList = (s: string) =>
  s
    .split(/[,\n]/)
    .map((x) => x.trim())
    .filter(Boolean);

export default function AdminPresetsPage() {
  const { me } = useAuth();
  const [presets, setPresets] = useState<Preset[]>([]);
  const [draft, setDraft] = useState<Draft | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(() => {
    api
      .adminPresets()
      .then((r) => setPresets(r.presets))
      .catch((e) => setError(errText(e)));
  }, []);

  useEffect(load, [load]);

  async function save() {
    if (!draft || !draft.name.trim()) return;
    setBusy(true);
    setError(null);
    const payload = {
      name: draft.name.trim(),
      description: draft.description.trim(),
      is_admin_only: draft.is_admin_only,
      roles: splitList(draft.roles),
      keywords: splitList(draft.keywords),
      locations: splitList(draft.locations),
      seniority: splitList(draft.seniority),
      excluded_companies: splitList(draft.excluded_companies),
      excluded_roles: splitList(draft.excluded_roles),
    };
    try {
      if (draft.id) await api.updatePreset(draft.id, payload);
      else await api.createPreset(payload);
      setDraft(null);
      load();
    } catch (e) {
      setError(errText(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-4">
      <PageHeader
        eyebrow="Admin"
        title="Presets"
        desc="Create reusable job-search configurations for JobQuest."
      />
      <div className="flex items-center gap-2">
        <button className={styles.btnMint} onClick={() => setDraft(toDraft())}>
          + New preset
        </button>
        <button
          className="btn-ghost w-fit"
          onClick={() => {
            const name = window.prompt("Snapshot name:", `Snapshot ${new Date().toLocaleDateString()}`);
            if (!name) return;
            api
              .snapshotPreset({
                source_user_id: me!.id,
                name,
                description: "Snapshot of admin's current preferences",
                is_admin_only: true,
              })
              .then(load)
              .catch((e) => setError(errText(e)));
          }}
        >
          Snapshot my current preferences
        </button>
        {error && <span className="text-sm text-danger">{error}</span>}
      </div>

      <div className="grid gap-3 md:grid-cols-2">
        {presets.map((p) => (
          <div key={p.id} className="card space-y-2 p-5">
            <div className="flex items-center justify-between gap-2">
              <h3 className="font-semibold">{p.name}</h3>
              {p.is_admin_only && (
                <span className="rounded border border-primary/40 bg-primary/10 px-1.5 py-0.5 font-mono text-[9px] uppercase tracking-widest text-primary">
                  admin only
                </span>
              )}
            </div>
            {p.description && <p className="text-xs text-text-secondary">{p.description}</p>}
            {(
              [
                ["Locations", p.locations ?? []],
                ["Experience", p.seniority ?? []],
                ["Skills", p.keywords ?? []],
              ] as [string, string[]][]
            ).map(
              ([label, values]) =>
                values.length > 0 && (
                  <div key={label} style={{ fontSize: 12 }}>
                    <span style={{ color: "var(--ink-muted)", marginRight: 8 }}>{label}:</span>
                    {values.slice(0, 4).map((v) => (
                      <span key={v} className={styles.tagChip} style={{ cursor: "default", marginRight: 6 }}>
                        {v}
                      </span>
                    ))}
                    {values.length > 4 && (
                      <span style={{ color: "var(--ink-muted)" }}>+{values.length - 4} more</span>
                    )}
                  </div>
                ),
            )}
            <p className="flex flex-wrap gap-x-3 font-mono text-[11px] text-text-muted">
              <span>{(p.roles ?? []).length} roles</span>
              <span>{(p.keywords ?? []).length} skills</span>
              <span>{(p.locations ?? []).length} locations</span>
              <span>{(p.seniority ?? []).length} experience</span>
            </p>
            <div className="flex gap-1 pt-1">
              <button className="btn-ghost px-2 py-1 text-xs" onClick={() => setDraft(toDraft(p))}>
                Edit
              </button>
              <button
                className="btn-ghost px-2 py-1 text-xs disabled:opacity-40"
                disabled={p.name === "Admin Preference"}
                title={p.name === "Admin Preference" ? "The original snapshot cannot be deleted" : undefined}
                onClick={() => {
                  if (!window.confirm(`Delete preset "${p.name}"?`)) return;
                  api.deletePreset(p.id).then(load).catch((e) => setError(errText(e)));
                }}
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>

      {draft && (
        <Modal title={draft.id ? `Edit — ${draft.name}` : "New preset"} onClose={() => setDraft(null)}>
          <div className="space-y-3">
            <input
              className="search-input w-full"
              placeholder="Preset name"
              value={draft.name}
              onChange={(e) => setDraft({ ...draft, name: e.target.value })}
            />
            <input
              className="search-input w-full"
              placeholder="Description (optional)"
              value={draft.description}
              onChange={(e) => setDraft({ ...draft, description: e.target.value })}
            />
            {FIELDS.map(({ field, label }) => (
              <div key={field}>
                <p className="mb-1 text-xs uppercase tracking-wide text-text-muted">{label}</p>
                <textarea
                  rows={2}
                  className="search-input w-full resize-y"
                  placeholder="Comma-separated values"
                  value={draft[field]}
                  onChange={(e) => setDraft({ ...draft, [field]: e.target.value })}
                />
              </div>
            ))}
            <label className="flex items-center gap-2 text-sm text-text-secondary">
              <input
                type="checkbox"
                checked={draft.is_admin_only}
                onChange={(e) => setDraft({ ...draft, is_admin_only: e.target.checked })}
              />
              Admin only (hidden from user quick-start chips)
            </label>
          </div>
          <div className="mt-4 flex justify-end gap-2">
            <button className="btn-ghost" onClick={() => setDraft(null)}>
              Cancel
            </button>
            <button className="btn-primary" disabled={busy || !draft.name.trim()} onClick={save}>
              {busy ? "Saving…" : "Save preset"}
            </button>
          </div>
        </Modal>
      )}
    </div>
  );
}
