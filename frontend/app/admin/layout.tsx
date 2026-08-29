"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { AuthGate } from "@/components/auth-gate";
import { RadarLoading } from "@/components/radar-loading";
import { useAuth } from "@/lib/auth-context";

const TABS = [
  { href: "/admin", label: "Overview" },
  { href: "/admin/users", label: "Users" },
  { href: "/admin/coupons", label: "Coupons" },
  { href: "/admin/presets", label: "Presets" },
];

function AdminGuard({ children }: { children: React.ReactNode }) {
  const { me } = useAuth();
  if (!me) return <RadarLoading label="Checking access…" />;
  if (!(me.role === "admin" || me.anonymous)) {
    return (
      <div className="flex min-h-screen items-center justify-center p-8">
        <div className="card p-8 text-center">
          <p className="text-lg font-semibold">403</p>
          <p className="mt-1 text-sm text-text-secondary">Admin access required.</p>
        </div>
      </div>
    );
  }
  return <>{children}</>;
}

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  return (
    <AuthGate>
      <AdminGuard>
        <div className="mx-auto max-w-6xl p-8">
          <h1 className="font-display text-2xl font-bold tracking-wide">ADMIN</h1>
          <nav className="mt-4 flex gap-1 border-b border-border pb-3">
            {TABS.map((tab) => {
              const active =
                tab.href === "/admin" ? pathname === "/admin" : pathname.startsWith(tab.href);
              return (
                <Link
                  key={tab.href}
                  href={tab.href}
                  className={`rounded-full px-4 py-1.5 text-sm transition-colors ${
                    active
                      ? "bg-primary/15 text-primary"
                      : "text-text-secondary hover:bg-primary/5 hover:text-text"
                  }`}
                >
                  {tab.label}
                </Link>
              );
            })}
          </nav>
          <div className="mt-6">{children}</div>
        </div>
      </AdminGuard>
    </AuthGate>
  );
}
