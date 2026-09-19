"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { Modal } from "@/components/admin-modal";
import { Avatar, DataTable, EmptyState, LoadingState, PageHeader, Stat, StatusPill } from "@/components/ink/ui";
import styles from "@/components/ink/ink.module.css";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { dateIST, errText, timeAgo } from "@/lib/format";
import type { AdminUser, Preset, Role } from "@/lib/types";

const KNOWN_CAPS = [
  { cap: "dashboard", label: "Dashboard access" },
  { cap: "preferences", label: "Edit preferences" },
  { cap: "telegram_alerts", label: "Telegram alerts" },
  { cap: "email_alerts", label: "Email alerts" },
  { cap: "fast_alerts", label: "Fast alerts (legacy)" },
  { cap: "admin", label: "Admin" },
];

function planOf(u: AdminUser): string {
  if (u.sub_plan) return u.sub_plan;
  if (u.role === "privileged") return "Friends & Family";
  if (u.role === "admin") return "Owner";
  return "—";
}

function statusOf(u: AdminUser): { tone: "ok" | "warn" | "bad" | "info" | "muted"; label: string } {
  if (u.status === "disabled") return { tone: "bad", label: "Suspended" };
  if (u.status === "pending") return { tone: "warn", label: "Trial" };
  if (u.access_locked) return { tone: "warn", label: "Locked" };
  if (u.sub_plan) return { tone: "ok", label: "Pro" };
  return { tone: "ok", label: "Active" };
}

export default function AdminUsersPage() {
  const { me } = useAuth();
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [presets, setPresets] = useState<Preset[]>([]);
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [capsUser, setCapsUser] = useState<AdminUser | null>(null);
  const [presetUser, setPresetUser] = useState<AdminUser | null>(null);
  const [menuFor, setMenuFor] = useState<string | null>(null);

  const load = useCallback(() => {
    api
      .adminUsers({ query_text: search || undefined, role: roleFilter || undefined })
      .then((r) => setUsers(r.users))
      .catch((e) => setError(errText(e)))
      .finally(() => setLoading(false));
  }, [search, roleFilter]);

  useEffect(() => {
    const t = setTimeout(load, 250);
    return () => clearTimeout(t);
  }, [load]);

  useEffect(() => {
    api.adminPresets().then((r) => setPresets(r.presets));
  }, []);

  async function act(fn: () => Promise<unknown>) {
    setError(null);
    try {
      await fn();
      load();
    } catch (e) {
      setError(errText(e));
    } finally {
      setMenuFor(null);
    }
  }

  const metrics = useMemo(() => {
    const weekAgo = Date.now() - 7 * 24 * 3600 * 1000;
    return {
      total: users.length,
      active: users.filter((u) => u.status === "approved" && !u.access_locked).length,
      pro: users.filter((u) => u.sub_plan).length,
      fresh: users.filter((u) => u.created_at && new Date(u.created_at).getTime() >= weekAgo).length,
    };
  }, [users]);

  const visible = useMemo(
    () =>
      users.filter((u) => {
        if (!statusFilter) return true;
        return statusOf(u).label.toLowerCase() === statusFilter;
      }),
    [users, statusFilter],
  );

  return (
    <div>
      <PageHeader eyebrow="Admin" title="Users" desc="Manage accounts, subscriptions and user activity." />

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4" style={{ marginBottom: 20 }}>
        <Stat label="Total users" value={metrics.total.toLocaleString()} />
        <Stat label="Active users" value={metrics.active.toLocaleString()} tone="ok" />
        <Stat label="Pro users" value={metrics.pro.toLocaleString()} tone="ok" />
        <Stat label="New users (7d)" value={metrics.fresh.toLocaleString()} tone="info" />
      </div>

      <div className={styles.toolbar}>
        <input
          className={styles.toolInput}
          style={{ width: 250 }}
          placeholder="Search name or email…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          aria-label="Search users"
        />
        <select className={styles.toolInput} value={roleFilter} onChange={(e) => setRoleFilter(e.target.value)} aria-label="Role">
          <option value="">All roles</option>
          <option value="user">user</option>
          <option value="privileged">privileged</option>
          <option value="admin">admin</option>
        </select>
        <select className={styles.toolInput} value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} aria-label="Status">
          <option value="">All statuses</option>
          <option value="active">Active</option>
          <option value="trial">Trial</option>
          <option value="pro">Pro</option>
          <option value="locked">Locked</option>
          <option value="suspended">Suspended</option>
        </select>
        <span className={styles.spacer} />
        <span style={{ fontSize: 12, color: "var(--ink-muted)" }}>{visible.length} account(s)</span>
      </div>

      {error && (
        <p style={{ fontSize: 13, color: "var(--ink-danger)", marginBottom: 12 }}>{error}</p>
      )}

      {loading ? (
        <LoadingState rows={6} />
      ) : visible.length === 0 ? (
        <EmptyState title="No accounts match." />
      ) : (
        <DataTable head={["User", "Email", "Plan", "Status", "Joined", "Last active", ""]}>
          {visible.map((u) => {
            const st = statusOf(u);
            const isSelf = me?.id === u.id;
            return (
              <tr key={u.id} style={isSelf ? { opacity: 0.65 } : undefined}>
                <td>
                  <span style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <Avatar name={u.display_name || u.email || "?"} size={32} />
                    <span style={{ fontWeight: 600 }}>
                      {u.display_name || u.email || u.id.slice(0, 8)}
                      {u.alert_delay_minutes > 0 && (
                        <span style={{ fontFamily: "ui-monospace,monospace", fontSize: 10, color: "var(--ink-warn)", marginLeft: 8 }}>
                          +{u.alert_delay_minutes}m
                        </span>
                      )}
                    </span>
                  </span>
                </td>
                <td style={{ color: "var(--ink-text2)", maxWidth: 220, overflow: "hidden", textOverflow: "ellipsis" }}>
                  {u.email || "—"}
                </td>
                <td style={{ textTransform: "capitalize" }}>{planOf(u)}</td>
                <td>
                  <StatusPill tone={st.tone}>● {st.label}</StatusPill>
                </td>
                <td style={{ color: "var(--ink-text2)", whiteSpace: "nowrap" }}>{dateIST(u.created_at)}</td>
                <td style={{ color: "var(--ink-text2)", whiteSpace: "nowrap" }}>{timeAgo(u.last_login_at)}</td>
                <td style={{ textAlign: "right", position: "relative" }}>
                  <button
                    type="button"
                    aria-label="User actions"
                    onClick={() => setMenuFor(menuFor === u.id ? null : u.id)}
                    className={styles.btnLine}
                    style={{ padding: "6px 12px", fontSize: 15, lineHeight: 1 }}
                  >
                    ⋯
                  </button>
                  {menuFor === u.id && (
                    <RowMenu
                      u={u}
                      onAct={act}
                      onCaps={() => {
                        setCapsUser(u);
                        setMenuFor(null);
                      }}
                      onPreset={() => {
                        setPresetUser(u);
                        setMenuFor(null);
                      }}
                      onClose={() => setMenuFor(null)}
                    />
                  )}
                </td>
              </tr>
            );
          })}
        </DataTable>
      )}

      {capsUser && (
        <CapabilitiesModal
          user={capsUser}
          onClose={() => setCapsUser(null)}
          onSave={async (add, remove) => {
            await act(() => api.setUserCapabilities(capsUser.id, add, remove));
            setCapsUser(null);
          }}
        />
      )}

      {presetUser && (
        <ApplyPresetModal
          presets={presets}
          userName={presetUser.email || presetUser.id.slice(0, 8)}
          onClose={() => setPresetUser(null)}
          onApply={async (presetId) => {
            await act(() => api.applyPresetToUser(presetUser.id, presetId));
            setPresetUser(null);
          }}
        />
      )}
    </div>
  );
}

function RowMenu({
  u,
  onAct,
  onCaps,
  onPreset,
  onClose,
}: {
  u: AdminUser;
  onAct: (fn: () => Promise<unknown>) => void;
  onCaps: () => void;
  onPreset: () => void;
  onClose: () => void;
}) {
  const [delay, setDelay] = useState(String(u.alert_delay_minutes));

  function saveDelay() {
    const parsed = Math.max(0, parseInt(delay, 10) || 0);
    if (parsed !== u.alert_delay_minutes) {
      onAct(() => api.setUserDelay(u.id, parsed));
    }
  }

  const item: React.CSSProperties = {
    display: "flex",
    width: "100%",
    alignItems: "center",
    gap: 8,
    border: 0,
    background: "none",
    color: "var(--ink-text)",
    fontSize: 12.5,
    padding: "8px 12px",
    cursor: "pointer",
    fontFamily: "inherit",
    textAlign: "left",
    borderRadius: 8,
  };

  return (
    <div
      style={{
        position: "absolute",
        right: 0,
        top: "calc(100% + 4px)",
        zIndex: 20,
        minWidth: 210,
        background: "#0e2b2e",
        border: "1px solid rgba(255,255,255,0.1)",
        borderRadius: 12,
        padding: 6,
        boxShadow: "0 16px 40px rgba(0,0,0,0.5)",
      }}
      onMouseLeave={onClose}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "8px 12px", fontSize: 12, color: "var(--ink-muted)" }}>
        Alert delay (min)
        <input
          type="number"
          min={0}
          max={10080}
          value={delay}
          disabled={u.is_owner}
          onChange={(e) => setDelay(e.target.value)}
          onBlur={saveDelay}
          onKeyDown={(e) => e.key === "Enter" && saveDelay()}
          className={styles.toolInput}
          style={{ width: 64, padding: "5px 8px", textAlign: "right" }}
        />
      </div>
      {(u.role === "user" || u.role === "privileged") && !u.is_owner && (
        <button
          type="button"
          style={item}
          onClick={() => onAct(() => api.setUserRole(u.id, u.role === "user" ? "privileged" : "user"))}
        >
          {u.role === "user" ? "Make privileged" : "Revoke privileged"}
        </button>
      )}
      {!u.is_owner && (
        <>
          {u.status === "pending" && (
            <button type="button" style={item} onClick={() => onAct(() => api.adminUserAction(u.id, "approve"))}>
              Approve
            </button>
          )}
          {u.status !== "disabled" ? (
            <button type="button" style={item} onClick={() => onAct(() => api.adminUserAction(u.id, "disable"))}>
              Disable
            </button>
          ) : (
            <button type="button" style={item} onClick={() => onAct(() => api.adminUserAction(u.id, "enable"))}>
              Enable
            </button>
          )}
          {!u.access_locked ? (
            <button type="button" style={item} onClick={() => onAct(() => api.adminUserAction(u.id, "lock"))}>
              Lock
            </button>
          ) : (
            <button type="button" style={item} onClick={() => onAct(() => api.adminUserAction(u.id, "unlock"))}>
              Unlock
            </button>
          )}
        </>
      )}
      <button type="button" style={item} onClick={onCaps}>
        Capabilities ({(u.capabilities || []).length})
      </button>
      <button type="button" style={item} onClick={onPreset}>
        Apply preset…
      </button>
      {!u.is_owner && (
        <button
          type="button"
          style={item}
          onClick={() => {
            const input = window.prompt("Comp subscription days (blank = until revoked):");
            if (input === null) return;
            const days = parseInt(input, 10);
            onAct(() => api.compSubscription(u.id, "standard", Number.isFinite(days) ? days : null));
          }}
        >
          Comp subscription…
        </button>
      )}
    </div>
  );
}

function CapabilitiesModal({
  user,
  onClose,
  onSave,
}: {
  user: AdminUser;
  onClose: () => void;
  onSave: (add: string[], remove: string[]) => Promise<void>;
}) {
  const effective = useMemo(() => {
    if ((user.capabilities || []).length > 0) return new Set(user.capabilities);
    const defaults: Record<Role, string[]> = {
      user: ["dashboard", "preferences", "telegram_alerts", "email_alerts"],
      privileged: ["dashboard", "preferences", "telegram_alerts", "email_alerts"],
      admin: ["dashboard", "preferences", "telegram_alerts", "email_alerts", "fast_alerts", "admin"],
    };
    return new Set(defaults[user.role]);
  }, [user]);
  const [selected, setSelected] = useState<Set<string>>(effective);
  const [busy, setBusy] = useState(false);

  function toggle(cap: string) {
    const next = new Set(selected);
    if (next.has(cap)) next.delete(cap);
    else next.add(cap);
    setSelected(next);
  }

  return (
    <Modal title={`Capabilities — ${user.email || user.id.slice(0, 8)}`} onClose={onClose}>
      <div className="space-y-2">
        {KNOWN_CAPS.map(({ cap, label }) => (
          <label key={cap} className="flex items-center gap-3 rounded-md px-2 py-1.5 text-sm hover:bg-elevated/60">
            <input type="checkbox" checked={selected.has(cap)} onChange={() => toggle(cap)} />
            <span className="font-mono text-xs">{cap}</span>
            <span className="text-text-muted">— {label}</span>
          </label>
        ))}
      </div>
      <p className="mt-3 text-xs text-text-muted">
        Saving stores an explicit capability list for this account; empty means &quot;role defaults&quot;.
      </p>
      <div className="mt-4 flex justify-end gap-2">
        <button onClick={onClose} className="btn-ghost">
          Cancel
        </button>
        <button
          className="btn-primary"
          disabled={busy}
          onClick={async () => {
            setBusy(true);
            try {
              await onSave(
                [...selected].filter((c) => !effective.has(c)),
                [...effective].filter((c) => !selected.has(c)),
              );
            } finally {
              setBusy(false);
            }
          }}
        >
          Save
        </button>
      </div>
    </Modal>
  );
}

function ApplyPresetModal({
  presets,
  userName,
  onClose,
  onApply,
}: {
  presets: Preset[];
  userName: string;
  onClose: () => void;
  onApply: (presetId: string) => Promise<void>;
}) {
  const [presetId, setPresetId] = useState(presets[0]?.id ?? "");
  const [busy, setBusy] = useState(false);

  return (
    <Modal title={`Apply preset — ${userName}`} onClose={onClose}>
      {presets.length === 0 ? (
        <p className="text-sm text-text-muted">No presets exist yet.</p>
      ) : (
        <select className="search-input w-full" value={presetId} onChange={(e) => setPresetId(e.target.value)}>
          {presets.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
              {p.is_admin_only ? " (admin only)" : ""}
            </option>
          ))}
        </select>
      )}
      <p className="mt-3 text-xs text-warning">
        This overwrites the user&apos;s roles/skills/locations/exclusions with the preset&apos;s values and re-matches their jobs.
      </p>
      <div className="mt-4 flex justify-end gap-2">
        <button onClick={onClose} className="btn-ghost">
          Cancel
        </button>
        <button
          className="btn-primary"
          disabled={!presetId || busy}
          onClick={async () => {
            setBusy(true);
            try {
              await onApply(presetId);
            } finally {
              setBusy(false);
            }
          }}
        >
          Apply preset
        </button>
      </div>
    </Modal>
  );
}
