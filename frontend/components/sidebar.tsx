"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { RadarMark } from "@/components/radar-mark";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

const NAV = [
  { href: "/dashboard", label: "Dashboard", icon: "◉" },
  { href: "/jobs", label: "Jobs", icon: "▣" },
  { href: "/new-jobs", label: "New Jobs Today", icon: "✦" },
  { href: "/matches", label: "Matches", icon: "◎" },
  { href: "/new-matches", label: "New Matches Today", icon: "✧" },
  { href: "/companies", label: "Companies", icon: "□" },
];

const USER_NAV = [
  { href: "/preferences", label: "Preferences", icon: "◉" },
  { href: "/notifications", label: "Notifications", icon: "✉" },
  { href: "/billing", label: "Billing", icon: "▤" },
];

const SYSTEM_NAV = [
  { href: "/sources", label: "Sources", icon: "◈" },
  { href: "/schedule", label: "Schedule", icon: "⏱" },
  { href: "/runs", label: "Runs", icon: "▶" },
  { href: "/timings", label: "Timings", icon: "◷" },
  { href: "/settings", label: "Settings", icon: "⚙" },
];

const ADMIN_NAV = [
  { href: "/admin", label: "Overview", icon: "⌂" },
  { href: "/admin/users", label: "Users", icon: "☺" },
  { href: "/admin/coupons", label: "Coupons", icon: "✗" },
  { href: "/admin/presets", label: "Presets", icon: "☰" },
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

function ThemeToggle() {
  const [theme, setTheme] = useState<string>("warm");

  useEffect(() => {
    const stored = localStorage.getItem("theme") || "warm";
    setTheme(stored);
    document.documentElement.setAttribute("data-theme", stored);
  }, []);

  const toggle = () => {
    const next = theme === "warm" ? "dark" : "warm";
    setTheme(next);
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("theme", next);
  };

  return (
    <button
      onClick={toggle}
      title="Toggle warm / dark"
      className="flex w-full items-center justify-between rounded-[10px] border-2 border-border bg-surface px-3 py-2 text-xs font-medium shadow-offset-sm transition-all hover:translate-y-[-1px] hover:shadow-offset"
    >
      <span className="font-mono text-[10px] uppercase tracking-[0.14em]">
        {theme === "warm" ? "Warm" : "Dark"}
      </span>
      <span>{theme === "warm" ? "◐" : "◑"}</span>
    </button>
  );
}

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { me, refresh } = useAuth();

  // Compat mode (auth not enforced): /me reports the anonymous owner — treat
  // it as admin so every existing surface stays visible.
  const isAdmin = !!me && (me.role === "admin" || me.anonymous);

  const render = (item: { href: string; label: string; icon: string }) => {
    const active = pathname === item.href || pathname.startsWith(item.href + "/");
    return (
      <Link
        key={item.href}
        href={item.href}
        className={`flex items-center gap-3 rounded-[10px] border-2 px-3 py-2 text-sm font-medium transition-all duration-150 ${
          active
            ? "border-border bg-text text-surface shadow-offset-sm"
            : "border-transparent text-text-secondary hover:border-border hover:bg-surface hover:text-text hover:shadow-offset-sm"
        }`}
      >
        <span className="w-4 text-center font-mono text-xs">{item.icon}</span>
        {item.label}
      </Link>
    );
  };

  async function logout() {
    try {
      await api.logout();
    } finally {
      await refresh();
      router.push("/login");
    }
  }

  return (
    <aside className="sticky top-0 flex h-screen w-56 shrink-0 flex-col border-r-2 border-border bg-bg">
      <div className="flex items-center gap-2.5 border-b-2 border-border px-5 py-5">
        <RadarMark />
        <span className="font-fraunces text-[15px] font-extrabold tracking-[-0.02em]">JOBRADAR</span>
        <span className="ml-auto rounded bg-primary px-1.5 py-0.5 font-mono text-[8px] font-bold uppercase tracking-widest text-white">
          ED. 28
        </span>
      </div>
      <nav className="flex flex-1 flex-col gap-1 overflow-y-auto px-3 py-3">
        {NAV.map(render)}
        <div className="my-2 border-t-2 border-border" />
        {USER_NAV.map(render)}
        {isAdmin && (
          <>
            <div className="my-2 border-t-2 border-border" />
            <p className="relative mb-1 ml-3 inline-flex bg-primary px-1.5 py-0.5 font-mono text-[9px] font-bold uppercase tracking-[0.14em] text-white">
              Admin
            </p>
            {ADMIN_NAV.map(render)}
            {SYSTEM_NAV.map(render)}
          </>
        )}
      </nav>
      <div className="space-y-2 border-t-2 border-border px-3 py-3">
        {me && (
          <div className="rounded-[10px] border-2 border-border bg-bg px-3 py-2 shadow-offset-sm">
            <div className="flex items-center justify-between gap-2">
              <span className="truncate text-xs font-medium text-text" title={me.email || undefined}>
                {me.display_name || me.email || (me.anonymous ? "owner" : me.id.slice(0, 8))}
              </span>
              <RoleBadge role={me.role} />
            </div>
            <div className="mt-1 flex items-center justify-between">
              {me.alert_delay_minutes > 0 && (
                <span className="font-mono text-[10px] text-warning">+{me.alert_delay_minutes}m delay</span>
              )}
              {!me.anonymous && (
                <button onClick={logout} className="ml-auto text-[11px] text-text-muted hover:text-danger">
                  Log out
                </button>
              )}
            </div>
          </div>
        )}
        <ThemeToggle />
        <div className="px-3 py-1 font-mono text-[10px] uppercase tracking-[0.12em] text-text-muted">
          Ink · Parchment · v0.2
        </div>
      </div>
    </aside>
  );
}
