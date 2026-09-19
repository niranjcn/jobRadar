"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { CompanyLogo } from "@/components/company-logo";
import { RadarLoading } from "@/components/radar-loading";
import { PageHeader } from "@/components/ink/ui";
import styles from "@/components/ink/ink.module.css";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
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

const READ_KEY = "jobquest:notif-read-at";

export default function NotificationsPage() {
  const { me } = useAuth();
  const isNormalUser = !!me && me.role === "user" && !me.is_owner && !me.anonymous;
  const [prefs, setPrefs] = useState<Preferences | null>(null);
  const [recent, setRecent] = useState<Notification[]>([]);
  const [readAt, setReadAt] = useState(0);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  if (isNormalUser) {
    return (
      <div className={styles.content}>
        <PageHeader eyebrow="Personal" title="Notifications" desc="Notifications are now handled directly via Telegram." />
        <div className={styles.stateWrap} style={{ padding: 32 }}>
          <p className={styles.stateTitle}>No separate page needed</p>
          <p className={styles.stateDesc}>
            For your account, just set your <strong>Telegram Chat ID</strong> in <Link href="/preferences" className="text-primary hover:underline">Preferences</Link> — matched jobs are sent there instantly after your subscription is active. No email/Telegram toggles needed.
          </p>
          <div className={styles.stateAction}>
            <Link href="/preferences" className={styles.btnMint}>Go to Preferences</Link>
            <Link href="/billing" className={styles.btnLine}>Billing</Link>
          </div>
        </div>
      </div>
    );
  }

  const load = useCallback(() => {
    api.preferences().then(setPrefs);
    api.notifications().then((res) => setRecent(res.notifications));
  }, []);

  useEffect(() => {
    load();
    try {
      setReadAt(Number(localStorage.getItem(READ_KEY) || 0));
    } catch {}
  }, [load]);

  function markAllRead() {
    const now = Date.now();
    setReadAt(now);
    try {
      localStorage.setItem(READ_KEY, String(now));
    } catch {}
  }

  const unread = recent.filter((n) => new Date(n.sent_at).getTime() > readAt).length;

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

  if (!prefs)
    return (
      <div className={styles.content}>
        <RadarLoading label="Loading notification settings…" />
      </div>
    );

  const telegram = recent.filter((n) => n.channel === "telegram").slice(0, 5);
  const email = recent.filter((n) => n.channel === "email").slice(0, 5);

  return (
    <div className={styles.content}>
      <PageHeader
        eyebrow="Personal"
        title="Notifications"
        desc="Stay updated on opportunities that matter. Telegram and email are independent — changes apply to the next poll."
      />

      <div style={{ maxWidth: 760 }} className="space-y-5">
        <section className={styles.panel}>
          <div className={styles.panelHead}>
            <span className={styles.panelTitle}>Recent activity</span>
            {unread > 0 && (
              <span className={styles.statusTag} style={{ marginLeft: 0 }}>
                <span className={styles.okDot} /> {unread} new
              </span>
            )}
            <span style={{ marginLeft: "auto" }} />
            <button type="button" className={styles.btnLine} style={{ fontSize: 12.5, padding: "7px 14px" }} onClick={markAllRead}>
              Mark all as read
            </button>
          </div>
          <div className={styles.timeline}>
            {recent.slice(0, 12).map((n) => {
              const isUnread = new Date(n.sent_at).getTime() > readAt;
              return (
                <div key={n.id} className={`${styles.tItem} ${isUnread ? styles.unread : ""}`}>
                  <span className={`${styles.tIcon} ${n.channel === "email" ? styles.blue : ""}`}>
                    <CompanyLogo name={n.company_name || "?"} domain={n.domain} size="sm" />
                  </span>
                  <span style={{ minWidth: 0 }}>
                    <span style={{ display: "block", fontSize: 13.5, fontWeight: isUnread ? 700 : 500 }}>
                      {n.title || "—"}
                      <span style={{ color: "var(--ink-muted)", fontWeight: 400 }}> · {n.company_name || "unknown"}</span>
                    </span>
                    <span style={{ display: "block", fontSize: 12, color: "var(--ink-muted)", marginTop: 2, textTransform: "capitalize" }}>
                      {n.channel} alert
                    </span>
                  </span>
                  <span style={{ display: "flex", alignItems: "center", gap: 8, marginLeft: "auto", flexShrink: 0 }}>
                    {isUnread && <span className={styles.okDot} />}
                    <span className={styles.tTime}>{new Date(n.sent_at).toLocaleString()}</span>
                  </span>
                </div>
              );
            })}
            {recent.length === 0 && <p className={styles.emptyNote}>No alerts sent yet.</p>}
          </div>
        </section>

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