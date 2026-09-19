"use client";

import { useEffect, useState } from "react";

type User = { id: string; chat_id: number; role: string; is_admin: boolean; display_name?: string };
type Prefs = { roles: string[]; keywords: string[]; locations: string[]; seniority: string[]; excluded_companies: string[]; excluded_roles: string[] };

export default function MiniAppPage() {
  const [initData, setInitData] = useState<string>("");
  const [user, setUser] = useState<User | null>(null);
  const [prefs, setPrefs] = useState<Prefs>({ roles: [], keywords: [], locations: [], seniority: [], excluded_companies: [], excluded_roles: [] });
  const [tab, setTab] = useState<"jobs" | "matches" | "prefs" | "users">("jobs");
  const [jobs, setJobs] = useState<any[]>([]);
  const [users, setUsers] = useState<any[]>([]);
  const [delays, setDelays] = useState<{ privileged_delay_minutes: number; normal_delay_minutes: number }>({ privileged_delay_minutes: 30, normal_delay_minutes: 360 });
  const [msg, setMsg] = useState<string>("");

  useEffect(() => {
    const tg = (window as any).Telegram?.WebApp;
    if (tg) {
      tg.ready();
      tg.expand();
      setInitData(tg.initData || "");
    } else {
      // For local testing without Telegram, try query param
      const params = new URLSearchParams(window.location.search);
      setInitData(params.get("initData") || "");
    }
  }, []);

  useEffect(() => {
    if (!initData) return;
    const api = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    fetch(`${api}/api/miniapp/auth`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ initData }),
    })
      .then((r) => r.json())
      .then((d) => {
        if (d.ok) setUser(d.user);
        else setMsg(d.detail || "auth failed: open via Telegram");
      })
      .catch((e) => setMsg(String(e)));
  }, [initData]);

  const loadPrefs = () => {
    if (!initData) return;
    const api = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    fetch(`${api}/api/miniapp/preferences`, { headers: { "X-Telegram-Init-Data": initData } })
      .then((r) => r.json())
      .then((d) => setPrefs(d))
      .catch(() => {});
  };

  const savePrefs = () => {
    const api = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    fetch(`${api}/api/miniapp/preferences`, {
      method: "PUT",
      headers: { "Content-Type": "application/json", "X-Telegram-Init-Data": initData },
      body: JSON.stringify({ initData, ...prefs }),
    })
      .then((r) => r.json())
      .then(() => setMsg("Saved! You will get matches for your settings."))
      .catch((e) => setMsg(String(e)));
  };

  const loadJobs = () => {
    // Placeholder: fetch jobs filtered for this user (future: per-user jobs endpoint)
    setJobs([]);
  };

  const loadUsers = () => {
    if (!initData || !user?.is_admin) return;
    const api = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    fetch(`${api}/api/miniapp/admin/users`, { headers: { "X-Telegram-Init-Data": initData } })
      .then((r) => r.json())
      .then((d) => setUsers(d.users || []));
    fetch(`${api}/api/miniapp/admin/delays`, { headers: { "X-Telegram-Init-Data": initData } })
      .then((r) => r.json())
      .then((d) => setDelays(d));
  };

  const setRole = (uid: string, role: string) => {
    const api = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    fetch(`${api}/api/miniapp/admin/users/${uid}/role`, {
      method: "PUT",
      headers: { "Content-Type": "application/json", "X-Telegram-Init-Data": initData },
      body: JSON.stringify({ initData, role }),
    }).then(() => loadUsers());
  };

  const saveDelays = () => {
    const api = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    fetch(`${api}/api/miniapp/admin/delays`, {
      method: "PUT",
      headers: { "Content-Type": "application/json", "X-Telegram-Init-Data": initData },
      body: JSON.stringify({ initData, ...delays }),
    }).then(() => setMsg("Delays saved"));
  };

  if (!initData) {
    return (
      <div className="mx-auto max-w-xl p-8">
        <h1 className="font-fraunces text-2xl font-extrabold">JobQuest Mini App</h1>
        <p className="mt-2 text-sm text-text-secondary">Open this page inside Telegram. Tap the bot’s Mini App button.</p>
        <p className="mt-4 font-mono text-xs text-text-muted">No initData found. For local testing, add ?initData=... to URL.</p>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="mx-auto max-w-xl p-8">
        <p className="font-mono text-sm">Authenticating…</p>
        {msg && <p className="mt-2 text-sm text-danger">{msg}</p>}
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-xl p-4">
      <div className="flex items-center justify-between border-b-2 border-border pb-3">
        <div>
          <h1 className="font-fraunces text-xl font-extrabold">JobQuest</h1>
          <p className="font-mono text-[11px] uppercase tracking-[0.12em] text-text-muted">
            {user.display_name || user.chat_id} · {user.role} {user.is_admin ? "· admin" : ""}
          </p>
        </div>
        <span className="rounded border-2 border-border bg-surface px-2 py-1 font-mono text-xs shadow-offset-sm">
          {user.is_admin ? "Admin" : user.role}
        </span>
      </div>

      <div className="mt-4 flex gap-2">
        <button onClick={() => setTab("jobs")} className={`rounded-[10px] border-2 px-3 py-2 text-sm font-medium ${tab === "jobs" ? "bg-text text-surface border-border shadow-offset-sm" : "bg-surface border-border shadow-offset-sm"}`}>
          Jobs
        </button>
        <button onClick={() => { setTab("matches"); loadJobs(); }} className={`rounded-[10px] border-2 px-3 py-2 text-sm font-medium ${tab === "matches" ? "bg-text text-surface border-border shadow-offset-sm" : "bg-surface border-border shadow-offset-sm"}`}>
          Matches
        </button>
        <button onClick={() => { setTab("prefs"); loadPrefs(); }} className={`rounded-[10px] border-2 px-3 py-2 text-sm font-medium ${tab === "prefs" ? "bg-text text-surface border-border shadow-offset-sm" : "bg-surface border-border shadow-offset-sm"}`}>
          Preferences
        </button>
        {user.is_admin && (
          <button onClick={() => { setTab("users"); loadUsers(); }} className={`rounded-[10px] border-2 px-3 py-2 text-sm font-medium ${tab === "users" ? "bg-primary text-white border-primary shadow-offset" : "bg-surface border-border shadow-offset-sm"}`}>
            Users
          </button>
        )}
      </div>

      {msg && <div className="card mt-4 p-3 text-sm">{msg}</div>}

      {tab === "prefs" && (
        <div className="mt-4 space-y-4">
          <div className="card p-4">
            <h3 className="font-fraunces font-bold">Your Preferences</h3>
            <p className="font-mono text-xs text-text-muted">Isolated per chat ID. Only your matches go to your chat.</p>
            {(["roles", "keywords", "locations", "seniority"] as const).map((field) => (
              <div key={field} className="mt-3">
                <label className="font-mono text-xs uppercase tracking-[0.12em]">{field}</label>
                <input
                  className="search-input mt-1 w-full"
                  placeholder="comma separated"
                  value={(prefs as any)[field].join(", ")}
                  onChange={(e) => setPrefs({ ...prefs, [field]: e.target.value.split(",").map((s) => s.trim()).filter(Boolean) })}
                />
              </div>
            ))}
            <button onClick={savePrefs} className="btn-primary mt-4 w-full">
              Save Preferences
            </button>
          </div>
        </div>
      )}

      {tab === "users" && user.is_admin && (
        <div className="mt-4 space-y-4">
          <div className="card p-4">
            <h3 className="font-fraunces font-bold">Per-Tier Delays</h3>
            <div className="mt-2 grid grid-cols-2 gap-3">
              <div>
                <label className="font-mono text-xs uppercase tracking-[0.12em]">Privileged (min)</label>
                <input type="number" className="search-input mt-1 w-full" value={delays.privileged_delay_minutes} onChange={(e) => setDelays({ ...delays, privileged_delay_minutes: parseInt(e.target.value) || 0 })} />
              </div>
              <div>
                <label className="font-mono text-xs uppercase tracking-[0.12em]">Normal (min)</label>
                <input type="number" className="search-input mt-1 w-full" value={delays.normal_delay_minutes} onChange={(e) => setDelays({ ...delays, normal_delay_minutes: parseInt(e.target.value) || 0 })} />
              </div>
            </div>
            <button onClick={saveDelays} className="btn-primary mt-3 w-full">Save Delays</button>
            <p className="font-mono mt-2 text-xs text-text-muted">Admin 0 · Privileged {delays.privileged_delay_minutes}m · Normal {delays.normal_delay_minutes}m</p>
          </div>

          <div className="card p-4">
            <h3 className="font-fraunces font-bold">All Users ({users.length})</h3>
            <div className="mt-3 space-y-2">
              {users.map((u) => (
                <div key={u.id} className="flex items-center justify-between rounded-[10px] border-2 border-border bg-surface p-3 shadow-offset-sm">
                  <div>
                    <div className="text-sm font-medium">{u.display_name || u.telegram_username || u.telegram_chat_id}</div>
                    <div className="font-mono text-xs text-text-muted">{u.telegram_chat_id} · {u.role} · {u.created_at?.slice(0, 10)}</div>
                    <div className="font-mono text-xs text-text-muted">{(u.roles || []).join(", ") || "—"} · {(u.locations || []).join(", ") || "—"}</div>
                  </div>
                  <div className="flex gap-2">
                    {u.role !== "privileged" ? (
                      <button onClick={() => setRole(u.id, "privileged")} className="rounded border-2 border-border bg-bg px-2 py-1 font-mono text-xs">Make Privileged</button>
                    ) : (
                      <button onClick={() => setRole(u.id, "user")} className="rounded border-2 border-border bg-bg px-2 py-1 font-mono text-xs">Make Normal</button>
                    )}
                  </div>
                </div>
              ))}
              {users.length === 0 && <p className="font-mono text-sm text-text-muted">No users yet. Share your bot link.</p>}
            </div>
          </div>
        </div>
      )}

      {(tab === "jobs" || tab === "matches") && (
        <div className="card mt-4 p-8 text-center">
          <p className="font-mono text-sm text-text-muted">Your {tab} will appear here, filtered to your preferences.</p>
          <p className="font-mono mt-2 text-xs text-text-muted">Polling already separates per user via notification_queue.</p>
        </div>
      )}
    </div>
  );
}
