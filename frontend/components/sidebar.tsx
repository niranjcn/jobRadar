"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV = [
  { href: "/dashboard", label: "Dashboard", icon: "◉" },
  { href: "/jobs", label: "Jobs", icon: "▣" },
  { href: "/new-jobs", label: "New Jobs Today", icon: "✦" },
  { href: "/matches", label: "Matches", icon: "◎" },
  { href: "/new-matches", label: "New Matches Today", icon: "✧" },
  { href: "/companies", label: "Companies", icon: "□" },
];

const NAV2 = [
  { href: "/sources", label: "Sources", icon: "◈" },
  { href: "/schedule", label: "Schedule", icon: "⏱" },
  { href: "/runs", label: "Runs", icon: "▶" },
  { href: "/preferences", label: "Preferences", icon: "◉" },
  { href: "/notifications", label: "Notifications", icon: "✉" },
];

const NAV3 = [{ href: "/settings", label: "Settings", icon: "⚙" }];

function ThemeToggle() {
  const [theme, setTheme] = useState<string>("dark");

  useEffect(() => {
    const stored = localStorage.getItem("theme") || "dark";
    setTheme(stored);
    document.documentElement.setAttribute("data-theme", stored);
  }, []);

  const toggle = () => {
    const next = theme === "dark" ? "light" : "dark";
    setTheme(next);
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("theme", next);
  };

  return (
    <button
      onClick={toggle}
      title="Toggle light / dark"
      className="flex w-full items-center justify-between rounded-md px-3 py-2 text-xs text-text-muted transition-colors hover:text-text"
    >
      <span className="font-mono uppercase tracking-widest">
        {theme === "dark" ? "Dark" : "Light"}
      </span>
      <span className="text-text-muted">{theme === "dark" ? "◐" : "◑"}</span>
    </button>
  );
}

export function Sidebar() {
  const pathname = usePathname();

  const render = (item: { href: string; label: string; icon: string }) => {
    const active = pathname === item.href || pathname.startsWith(item.href + "/");
    return (
      <Link
        key={item.href}
        href={item.href}
        className={`flex items-center gap-3 rounded-[10px] px-3 py-2 text-sm transition-all duration-200 ${
          active
            ? "bg-primary/15 text-primary shadow-neo-pressed"
            : "text-text-secondary hover:bg-primary/5 hover:text-text"
        }`}
      >
        <span className="w-4 text-center">{item.icon}</span>
        {item.label}
      </Link>
    );
  };

  return (
    <aside className="sticky top-0 flex h-screen w-56 shrink-0 flex-col border-r border-[var(--glass-border)] bg-[var(--glass)] backdrop-blur-xl">
      <div className="flex items-center gap-2 px-5 py-5">
        <RadarMark />
        <span className="font-display text-sm font-bold tracking-[0.14em]">JOBRADAR</span>
      </div>
      <nav className="flex flex-1 flex-col gap-1 overflow-y-auto px-3">
        {NAV.map(render)}
        <div className="my-2 border-t border-[var(--glass-border)]" />
        {NAV2.map(render)}
        <div className="my-2 border-t border-[var(--glass-border)]" />
        {NAV3.map(render)}
      </nav>
      <div className="space-y-1 border-t border-[var(--glass-border)] px-3 py-3">
        <ThemeToggle />
        <div className="px-3 py-1 font-mono text-[10px] uppercase tracking-[0.18em] text-text-muted">
          Career intel · v0.1
        </div>
      </div>
    </aside>
  );
}

function RadarMark() {
  return (
    <span className="relative inline-flex h-5 w-5 items-center justify-center">
      <span className="absolute inset-0 rounded-full border border-primary/50" />
      <span className="radar-sweep absolute inset-0 rounded-full border-b-2 border-l-2 border-primary/70" />
      <span className="relative h-1.5 w-1.5 rounded-full bg-primary shadow-neo-glow" />
    </span>
  );
}