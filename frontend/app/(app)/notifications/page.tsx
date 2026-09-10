"use client";

import { useCallback, useEffect, useState } from "react";
import { CompanyLogo } from "@/components/company-logo";
import { RadarLoading } from "@/components/radar-loading";
import { api } from "@/lib/api";
import type { Notification, Preferences } from "@/lib/types";

type Scope = "all" | "matched";

function ScopeOption({
  active,
  label,
  detail,
  onSelect,
}: {
  active: boolean;
  label: string;
  detail: string;
  onSelect: () => void;
}) {
  return (
    <button
      onClick={onSelect}
      className={`rounded-lg border p-3 text-left transition-colors ${
        active
          ? "border-primary bg-primary/10"
          : "border-border hover:border-primary/60"
      }`}
    >
      <p className="text-sm font-medium text-text">{label}</p>
      <p className="mt-0.5 text-xs text-text-muted">{detail}</p>
    </button>
  );
}

function ChannelCard({
  title,
  badge,
  enabled,
  scope,
  onEnabled,
  onScope,
  preview,
}: {
  title: string;
  badge: string;
  enabled: boolean;
  scope: Scope;
  onEnabled: (v: boolean) => void;
  onScope: (v: Scope) => void;
  preview: Notification[];
}) {
  return (
    <section className="card space-y-4 p-5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h2 className="text-[15px] font-semibold">{title}</h2>
          <span className="rounded bg-elevated px-1.5 py-0.5 text-[11px] text-text-muted">{badge}</span>
        </div>
        <label className="flex items-center gap-2 text-sm text-text-secondary">
          <input
            type="checkbox"
            checked={enabled}
            onChange={(e) => onEnabled(e.target.checked)}
            className="h-4 w-4"
          />
          Enabled
        </label>
      </div>

      <div>
        <p className="mb-2 text-xs uppercase tracking-wide text-text-muted">Send</p>
        <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
          <ScopeOption
            active={scope === "all"}
            label="All new jobs"
            detail="Every newly discovered job, whether it matches your preferences or not."
            onSelect={() => onScope("all")}
          />
          <ScopeOption
            active={scope === "matched"}
            label="Only matched jobs"
            detail="Only jobs that match your roles, skills, locations, and exclusions."
            onSelect={() => onScope("matched")}
          />
        </div>
      </div>

      {preview.length > 0 && (
        <div>
          <p className="mb-2 text-xs uppercase tracking-wide text-text-muted">Recent sends</p>
          <ul className="space-y-1">
            {preview.map((n) => (
              <li key={n.id} className="flex items-center justify-between text-sm">
                <span className="flex min-w-0 items-center gap-2 truncate text-text-secondary">
                  <CompanyLogo name={n.company_name || "?"} domain={n.domain} size="sm" />
                  <span className="truncate">
                    {n.title || "—"}
                    <span className="text-text-muted"> · {n.company_name || "unknown"}</span>
                  </span>
                </span>
                <span className="ml-3 shrink-0 text-xs text-text-muted">
                  {new Date(n.sent_at).toLocaleString()}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}

export default function NotificationsPage() {
  const [prefs, setPrefs] = useState<Preferences | null>(null);
  const [recent, setRecent] = useState<Notification[]>([]);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const load = useCallback(() => {
    api.preferences().then(setPrefs);
    api.notifications().then((res) => setRecent(res.notifications.slice(0, 5)));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

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

  if (!prefs) return <RadarLoading label="Loading notification settings…" />;

  const telegram = recent.filter((n) => n.channel === "telegram");
  const email = recent.filter((n) => n.channel === "email");

  return (
    <div className="mx-auto max-w-3xl p-8">
      <h1 className="text-[28px] font-semibold">Notifications</h1>
      <p className="mt-1 text-sm text-text-secondary">
        Control what each channel sends. Telegram and email are independent — you can send everything to
        one and only matches to the other. Changes apply to the next poll.
      </p>

      <div className="mt-8 space-y-6">
        <ChannelCard
          title="Telegram"
          badge="messaging"
          enabled={prefs.notify_telegram}
          scope={prefs.telegram_scope}
          onEnabled={(v) => setPrefs({ ...prefs, notify_telegram: v })}
          onScope={(v) => setPrefs({ ...prefs, telegram_scope: v })}
          preview={telegram}
        />

        <ChannelCard
          title="Email"
          badge="resend"
          enabled={prefs.notify_email}
          scope={prefs.email_scope}
          onEnabled={(v) => setPrefs({ ...prefs, notify_email: v })}
          onScope={(v) => setPrefs({ ...prefs, email_scope: v })}
          preview={email}
        />

        <section className="card space-y-3 p-5">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h2 className="text-[15px] font-semibold">First check</h2>
              <p className="mt-1 text-sm text-text-secondary">
                When a source is added for the first time, its jobs are new. Notify me about matching jobs
                found during the initial crawl too.
              </p>
            </div>
            <label className="flex items-center gap-2 text-sm text-text-secondary">
              <input
                type="checkbox"
                checked={prefs.notify_first_check}
                onChange={(e) => setPrefs({ ...prefs, notify_first_check: e.target.checked })}
                className="h-4 w-4"
              />
              On
            </label>
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