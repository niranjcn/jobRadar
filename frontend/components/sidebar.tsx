"use client";

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

const NAV3 = [
  { href: "/settings", label: "Settings", icon: "⚙" },
];

export function Sidebar() {
  const pathname = usePathname();

  const render = (item: { href: string; label: string; icon: string }) => {
    const active = pathname === item.href || pathname.startsWith(item.href + "/");
    return (
      <Link
        key={item.href}
        href={item.href}
        className={`flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors ${
          active
            ? "bg-primary/10 text-primary"
            : "text-text-secondary hover:bg-surface hover:text-text"
        }`}
      >
        <span className="w-4 text-center">{item.icon}</span>
        {item.label}
      </Link>
    );
  };

  return (
    <aside className="sticky top-0 flex h-screen w-56 shrink-0 flex-col border-r border-border bg-surface">
      <div className="flex items-center gap-2 px-5 py-5">
        <RadarMark />
        <span className="text-sm font-semibold tracking-wide">JOBRADAR</span>
      </div>
      <nav className="flex flex-1 flex-col gap-1 overflow-y-auto px-3">
        {NAV.map(render)}
        <div className="my-2 border-t border-border" />
        {NAV2.map(render)}
        <div className="my-2 border-t border-border" />
        {NAV3.map(render)}
      </nav>
      <div className="px-5 py-4 text-xs text-text-muted">Career intelligence · v0.1</div>
    </aside>
  );
}

function RadarMark() {
  return (
    <span className="relative inline-flex h-5 w-5 items-center justify-center">
      <span className="absolute inset-0 rounded-full border border-accent/60" />
      <span className="radar-sweep absolute inset-0 rounded-full border-b-2 border-l-2 border-accent/70" />
      <span className="relative h-1.5 w-1.5 rounded-full bg-accent" />
    </span>
  );
}