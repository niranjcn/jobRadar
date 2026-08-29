"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { Modal } from "@/components/admin-modal";
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

function RoleBadge({ role }: { role: string }) {
  const styles =
    role === "admin"
      ? "bg-primary/20 text-primary border-primary/40"
      : role === "privileged"
        ? "bg-success/15 text-success border-success/30"
        : "bg-elevated text-text-muted border-border";
  return (
    <span className={`rounded border px-1.5 py-0.5 font-mono text-[9px] uppercase tracking-widest ${styles}`}>
      {role}
    </span>
  );
}

function StatusDot({ user }: { user: AdminUser }) {
  if (user.status === "disabled") return <span className="text-xs text-danger">disabled</span>;
  if (user.access_locked) return <span className="text-xs text-warning">locked</span>;
  return <span className="text-xs text-success">active</span>;
}

export default function AdminUsersPage() {
  const { me } = useAuth();
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [presets, setPresets] = useState<Preset[]>([]);
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [capsUser, setCapsUser] = useState<AdminUser | null>(null);
  const [presetUser, setPresetUser] = useState<AdminUser | null>(null);

  const load = useCallback(() => {
    api
      .adminUsers({ query_text: search, role: roleFilter })
      .then((r) => setUsers(r.users))
      .catch((e) => setError(errText(e)));
  }, [search, roleFilter]);

  useEffect(() => {
    load();
    api.adminPresets().then((r) => setPresets(r.presets));
  }, [load]);

  async function act(fn: () => Promise<unknown>) {
    setError(null);
    try {
      await fn();
      load();
    } catch (e) {
      setError(errText(e));
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        <input
          className="search-input w-72"
          placeholder="Search email or name…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select className="search-input w-36" value={roleFilter} onChange={(e) => setRoleFilter(e.target.value)}>
          <option value="">All roles</option>
          <option value="user">user</option>
          <option value="privileged">privileged</option>
          <option value="admin">admin</option>
        </select>
        <span className="ml-auto text-xs text-text-muted">{users.length} account(s)</span>
      </div>

      {error && <p className="text-sm text-danger">{error}</p>}

      <div className="card divide-y divide-border overflow-hidden">
        {users.map((u) => (
          <UserRow
            key={u.id}
            u={u}
            presets={presets}
            onAct={act}
            onCaps={() => setCapsUser(u)}
            onPreset={() => setPresetUser(u)}
            isSelf={me?.id === u.id}
          />
        ))}
        {users.length === 0 && (
          <div className="p-6 text-center text-sm text-text-muted">No accounts match.</div>
        )}
      </div>

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

function UserRow({
  u,
  presets,
  onAct,
  onCaps,
  onPreset,
  isSelf,
}: {
  u: AdminUser;
  presets: Preset[];
  onAct: (fn: () => Promise<unknown>) => void;
  onCaps: () => void;
  onPreset: () => void;
  isSelf: boolean;
}) {
  const [delay, setDelay] = useState(String(u.alert_delay_minutes));

  useEffect(() => setDelay(String(u.alert_delay_minutes)), [u.alert_delay_minutes]);

  function saveDelay() {
    const parsed = Math.max(0, parseInt(delay, 10) || 0);
    if (parsed !== u.alert_delay_minutes) {
      onAct(() => api.setUserDelay(u.id, parsed));
    }
  }

  return (
    <div className={`flex flex-wrap items-center gap-x-4 gap-y-2 p-4 ${isSelf ? "opacity-70" : ""}`}>
      <div className="min-w-52 flex-1">
        <div className="flex items-center gap-2">
          <span className="truncate text-sm font-medium">{u.email || u.display_name}</span>
          <RoleBadge role={u.role} />
          <StatusDot user={u} />
          {u.alert_delay_minutes > 0 && (
            <span className="font-mono text-[10px] text-warning">+{u.alert_delay_minutes}m</span>
          )}
        </div>
        <p className="mt-0.5 text-xs text-text-muted">
          joined {dateIST(u.created_at)} · last login {timeAgo(u.last_login_at)}
          {u.sub_plan ? ` · ${u.sub_plan} (${u.sub_provider ?? "—"})` : ""}
        </p>
      </div>

      <label className="flex items-center gap-1.5 text-xs text-text-muted">
        Delay min
        <input
          type="number"
          min={0}
          max={10080}
          value={delay}
          disabled={u.is_owner}
          onChange={(e) => setDelay(e.target.value)}
          onBlur={saveDelay}
          onKeyDown={(e) => e.key === "Enter" && saveDelay()}
          className="search-input w-20 px-2 py-1 text-right"
        />
      </label>

      <div className="flex flex-wrap gap-1">
        {(u.role === "user" || u.role === "privileged") && !u.is_owner && (
          <button
            className="btn-ghost px-2 py-1 text-xs"
            onClick={() => onAct(() => api.setUserRole(u.id, u.role === "user" ? "privileged" : "user"))}
          >
            {u.role === "user" ? "Make privileged" : "Revoke privileged"}
          </button>
        )}
        {!u.is_owner && (
          <>
            {u.status === "pending" && (
              <button className="btn-ghost px-2 py-1 text-xs" onClick={() => onAct(() => api.adminUserAction(u.id, "approve"))}>
                Approve
              </button>
            )}
            {u.status !== "disabled" ? (
              <button className="btn-ghost px-2 py-1 text-xs" onClick={() => onAct(() => api.adminUserAction(u.id, "disable"))}>
                Disable
              </button>
            ) : (
              <button className="btn-ghost px-2 py-1 text-xs" onClick={() => onAct(() => api.adminUserAction(u.id, "enable"))}>
                Enable
              </button>
            )}
            {!u.access_locked ? (
              <button className="btn-ghost px-2 py-1 text-xs" onClick={() => onAct(() => api.adminUserAction(u.id, "lock"))}>
                Lock
              </button>
            ) : (
              <button className="btn-ghost px-2 py-1 text-xs" onClick={() => onAct(() => api.adminUserAction(u.id, "unlock"))}>
                Unlock
              </button>
            )}
          </>
        )}
        <button className="btn-ghost px-2 py-1 text-xs" onClick={onCaps}>
          Caps ({(u.capabilities || []).length})
        </button>
        <button className="btn-ghost px-2 py-1 text-xs" onClick={onPreset}>
          Preset…
        </button>
        {!u.is_owner && (
          <button
            className="btn-ghost px-2 py-1 text-xs"
            onClick={() => {
              const input = window.prompt("Comp subscription days (blank = until revoked):");
              if (input === null) return;
              const days = parseInt(input, 10);
              onAct(() => api.compSubscription(u.id, "standard", Number.isFinite(days) ? days : null));
            }}
          >
            Comp…
          </button>
        )}
      </div>
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
  // Effective caps: explicit array if non-empty, else role defaults (mirrors backend).
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
