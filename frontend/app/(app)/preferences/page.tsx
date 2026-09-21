"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { CountrySelect } from "@/components/country-select";
import { RadarLoading } from "@/components/radar-loading";
import { PageHeader } from "@/components/ink/ui";
import styles from "@/components/ink/ink.module.css";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { errText } from "@/lib/format";
import type { GeoCountry, Preferences } from "@/lib/types";

const ROLES_PRESET = ["Software Engineer", "Backend Engineer", "DevOps Engineer", "SRE", "Platform Engineer", "MTS", "Full Stack Engineer", "Cloud Engineer"];
const LOCATIONS_PRESET = ["Remote", "India", "United States", "Bengaluru", "Hyderabad", "Mumbai", "Delhi", "Pune", "Chennai", "Dubai", "Singapore", "Germany"];

export default function PreferencesPage() {
  const { me, refresh } = useAuth();
  const [prefs, setPrefs] = useState<Preferences | null>(null);
  const [countries, setCountries] = useState<GeoCountry[]>([]);
  const [countryPreview, setCountryPreview] = useState<Record<string, string[]>>({});
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [telegramChatId, setTelegramChatId] = useState("");
  const [tgSaving, setTgSaving] = useState(false);
  const [tgMsg, setTgMsg] = useState<string | null>(null);
  const [tgErr, setTgErr] = useState<string | null>(null);

  const load = useCallback(() => {
    api.preferences().then(setPrefs);
  }, []);

  useEffect(() => {
    load();
    api.geoCountries().then((res) => setCountries(res.countries));
  }, [load]);

  useEffect(() => {
    if (me?.telegram_chat_id) setTelegramChatId(String(me.telegram_chat_id));
    else if (me && me.telegram_chat_id === null) setTelegramChatId("");
  }, [me?.telegram_chat_id, me]);

  async function saveTelegram() {
    setTgSaving(true);
    setTgMsg(null);
    setTgErr(null);
    try {
      const res = await api.setTelegramChatId(telegramChatId.trim());
      setTgMsg(res.telegram_chat_id ? `Saved — alerts will go to ${res.telegram_chat_id}` : "Cleared — no Telegram alerts until you set a chat ID.");
      await refresh();
    } catch (e) {
      setTgErr(errText(e as Error));
    } finally {
      setTgSaving(false);
    }
  }

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

  if (!prefs)
    return (
      <div className={styles.content}>
        <RadarLoading label="Loading preferences…" />
      </div>
    );

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

  const BulkTagInput = ({ field, placeholder, presets, addLabel = "Add roles" }: { field: keyof Preferences; placeholder: string; presets: string[]; addLabel?: string }) => {
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
            {addLabel}
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

  const roleCount = (prefs.roles as string[]).length;
  const locCount = (prefs.locations as string[]).length;
  const exclCount =
    (prefs.excluded_roles as string[]).length + (prefs.excluded_companies as string[]).length;

  return (
    <div className={styles.content}>
      <PageHeader
        eyebrow="Personal"
        title="Preferences"
        desc="Tell JobQuest what kind of opportunities you're looking for. Locations act as a hard filter — a job matches if it hits ANY of your roles."
        action={
          <span style={{ fontSize: 13, color: "var(--ink-text2)" }}>
            <strong style={{ fontSize: 22, color: "var(--ink-text)", fontVariantNumeric: "tabular-nums" }}>
              {roleCount}
            </strong>{" "}
            roles · <strong style={{ fontSize: 22, color: "var(--ink-text)", fontVariantNumeric: "tabular-nums" }}>{locCount}</strong> locations ·{" "}
            <strong style={{ fontSize: 22, color: "var(--ink-text)", fontVariantNumeric: "tabular-nums" }}>{exclCount}</strong> exclusions
          </span>
        }
      />

      <div style={{ maxWidth: 780 }} className="space-y-4">
        <section className={styles.panel}>
          <div className={styles.panelHead}>
            <span className={styles.eyebrow}>01 · Target roles</span>
            <span className={styles.panelTotal}>
              {roleCount} selected
            </span>
          </div>
          <div style={{ padding: "0 22px 22px", position: "relative" }}>
            <p style={{ fontSize: 13, color: "var(--ink-muted)", margin: "0 0 12px" }}>
              Job titles that qualify. Add variants — matching hits ANY of them.
            </p>
            <BulkTagInput
              field="roles"
              placeholder={"Paste roles separated by commas, e.g. Software Engineer, SDE I, MTS, Backend Developer…\nPress Ctrl+Enter to add."}
              presets={ROLES_PRESET}
            />
          </div>
        </section>

        <section className={styles.panel}>
          <div className={styles.panelHead}>
            <span className={styles.eyebrow}>02 · Locations</span>
            <span className={styles.panelTotal}>
              {locCount} selected · hard filter
            </span>
          </div>
          <div style={{ padding: "0 22px 22px", position: "relative" }}>
            <p style={{ fontSize: 13, color: "var(--ink-muted)", margin: "0 0 12px" }}>
              Cities and states map to their country automatically — e.g. Bengaluru→India, Austin→USA.
            </p>
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
          </div>
        </section>

        <section className={styles.panel}>
          <div className={styles.panelHead}>
            <span className={styles.eyebrow}>03 · Exclusions</span>
            <span className={styles.panelTotal}>
              {exclCount} total · never match
            </span>
          </div>
          <div style={{ padding: "0 22px 22px", position: "relative" }}>
            <p style={{ fontSize: 13, color: "var(--ink-muted)", margin: "0 0 12px" }}>
              Jobs whose title contains any of these terms will never match. E.g. add{" "}
              <code>staff</code>, <code>principal</code>, <code>lead</code> so a &quot;Staff Software
              Engineer&quot; doesn&apos;t match your &quot;Software Engineer&quot; role.
            </p>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <p className={styles.fieldLabel}>Exclude roles</p>
                <BulkTagInput
                  field="excluded_roles"
                  placeholder={"staff, principal, lead, senior…\nPress Ctrl+Enter to add."}
                  presets={["staff", "principal", "lead", "senior", "manager", "director"]}
                  addLabel="Add exclusions"
                />
              </div>
              <div>
                <p className={styles.fieldLabel}>Excluded companies</p>
                <TagInput field="excluded_companies" placeholder="e.g. Stripe (press Enter)" presets={[]} />
              </div>
            </div>
          </div>
        </section>

        <section className={styles.panel}>
          <div className={styles.panelHead}>
            <span className={styles.eyebrow}>04 · Telegram alerts</span>
            <span className={styles.panelTotal}>
              {me?.telegram_linked ? `linked · ${me.telegram_chat_id}` : "not linked"}
            </span>
          </div>
          <div style={{ padding: "0 22px 22px", position: "relative" }}>
          <p className="text-sm text-text-secondary">
            Your <strong>matched jobs</strong> will be sent instantly to this Telegram chat ID after payment is active. Find your ID via{" "}
            <a href="https://t.me/userinfobot" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
              @userinfobot
            </a>{" "}
            on Telegram (send <code>/start</code>), or use a channel/group ID like <code>-1001234567890</code>.
          </p>
          <div className="flex flex-wrap items-center gap-2">
            <input
              placeholder="e.g. 1415590254 or -1001234567890"
              value={telegramChatId}
              onChange={(e) => setTelegramChatId(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && telegramChatId.trim() && saveTelegram()}
              className="search-input w-64 font-mono"
            />
            <button onClick={saveTelegram} disabled={tgSaving} className="btn-primary w-fit">
              {tgSaving ? "Saving…" : "Save Telegram ID"}
            </button>
            {telegramChatId && (
              <button
                type="button"
                onClick={() => {
                  setTelegramChatId("");
                  setTgMsg(null);
                  setTgErr(null);
                }}
                className="btn-ghost w-fit"
              >
                Clear
              </button>
            )}
          </div>
          {tgMsg && <p className="text-sm text-success">{tgMsg}</p>}
          {tgErr && <p className="text-sm text-danger">{tgErr}</p>}
          <p className="text-xs text-text-muted">
            {me?.access_locked ? "Subscribe via Billing to activate alerts." : "Alerts active (1 message per new match batch, respects your delay)."}
          </p>
          </div>
        </section>

        <div className={styles.panel} style={{ padding: "16px 22px", display: "flex", alignItems: "center", gap: 12, position: "sticky", bottom: 12 }}>
          <button onClick={save} disabled={saving} className="btn-primary">
            {saving ? "Saving…" : "Save Changes"}
          </button>
          {saved && <span className="text-sm text-success">Saved ✓</span>}
          <span style={{ marginLeft: "auto", fontSize: 12.5, color: "var(--ink-muted)" }}>
            {roleCount} roles · {locCount} locations · {exclCount} exclusions
          </span>
        </div>
      </div>
    </div>
  );
}