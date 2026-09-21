"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import styles from "./ink.module.css";
import { I } from "./icons";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

const PRIMARY = [
  { href: "/dashboard", label: "Dashboard", icon: I.home },
  { href: "/jobs", label: "Jobs", icon: I.briefcase },
  { href: "/new-jobs", label: "New Jobs Today", icon: I.bolt },
  { href: "/matches", label: "Matches", icon: I.target },
  { href: "/companies", label: "Companies", icon: I.building },
];

const PERSONAL_ALL = [
  { href: "/preferences", label: "Preferences", icon: I.sliders },
  { href: "/notifications", label: "Notifications", icon: I.bell, badgeKey: "notifications" },
  { href: "/billing", label: "Billing", icon: I.card },
];

const ADMIN = [
  { href: "/admin", label: "Overview", icon: I.home },
  { href: "/admin/users", label: "Users", icon: I.users },
  { href: "/admin/coupons", label: "Coupons", icon: I.tag },
  { href: "/admin/presets", label: "Presets", icon: I.list },
  { href: "/sources", label: "Sources", icon: I.db },
  { href: "/schedule", label: "Schedule", icon: I.clock },
  { href: "/runs", label: "Runs", icon: I.play },
  { href: "/timings", label: "Timings", icon: I.gauge },
  { href: "/settings", label: "Settings", icon: I.gear },
];

function LogoMark() {
  return (
    <img
      src="/logo.png"
      alt="JobQuest"
      width={52}
      height={52}
      style={{ borderRadius: 14, objectFit: "cover", flexShrink: 0 }}
    />
  );
}

export function InkSidebar({ open, onClose }: { open: boolean; onClose: () => void }) {
  const pathname = usePathname();
  const router = useRouter();
  const { me, refresh } = useAuth();
  const [notifCount, setNotifCount] = useState(0);

  // Compat mode (auth not enforced): anonymous owner sees everything.
  const isAdmin = !!me && (me.role === "admin" || me.anonymous);
  const isNormalUser = !!me && me.role === "user" && !me.anonymous;
  const PERSONAL = isNormalUser ? PERSONAL_ALL.filter((p) => p.href !== "/notifications") : PERSONAL_ALL;

  useEffect(() => {
    const isNormal = !!me && me.role === "user" && !me.is_owner && !me.anonymous;
    if (!isNormal) {
      api
        .notifications()
        .then((r) => setNotifCount(r.notifications.length))
        .catch(() => {});
    }
  }, [me]);

  async function logout() {
    try {
      await api.logout();
    } finally {
      await refresh();
      router.push("/login");
    }
  }

  function render(item: { href: string; label: string; icon: () => React.JSX.Element; badgeKey?: string }) {
    const active = pathname === item.href || pathname.startsWith(item.href + "/");
    const Icon = item.icon;
    const showBadge = item.badgeKey === "notifications" && notifCount > 0;
    return (
      <Link
        key={item.href}
        href={item.href}
        onClick={onClose}
        className={`${styles.navItem} ${active ? styles.navActive : ""}`}
      >
        <Icon />
        {item.label}
        {showBadge && <span className={styles.navBadge} />}
      </Link>
    );
  }

  return (
    <>
      {open && <button type="button" aria-label="Close menu" className={styles.scrim} onClick={onClose} />}
      <aside className={`${styles.sidebar} ${open ? styles.open : ""}`}>
        <Link href="/dashboard" className={styles.brandRow} onClick={onClose}>
          <LogoMark />
          <span className={styles.brandName}>
            <span className={styles.job}>JOB</span>
            <span className={styles.quest}>QUEST</span>
          </span>
        </Link>

        <nav className={styles.nav}>
          {PRIMARY.map(render)}
          <div className={styles.navDivider} />
          {PERSONAL.map(render)}
          {isAdmin && (
            <>
              <div className={styles.navDivider} />
              <p className={styles.navLabel}>Admin</p>
              {ADMIN.map(render)}
            </>
          )}
        </nav>

        <div className={styles.sideFoot}>
          {me && (
            <Link href="/preferences" className={styles.userCard} onClick={onClose}>
              <span className={styles.avatar} aria-hidden>
                {(me.display_name || me.email || (me.anonymous ? "O" : "?")).trim()[0]?.toUpperCase() || "?"}
              </span>
              <span className={styles.userMeta}>
                <span className={styles.userName}>
                  {me.display_name || me.email || (me.anonymous ? "owner" : me.id.slice(0, 8))}
                </span>
                <span className={styles.userRole}>{me.anonymous ? "owner" : me.role}</span>
              </span>
              <span className={styles.userChev}>›</span>
            </Link>
          )}
          {!me?.anonymous && (
            <button type="button" className={styles.logoutBtn} onClick={logout}>
              <I.logout /> Log out
            </button>
          )}
        </div>
      </aside>
    </>
  );
}
