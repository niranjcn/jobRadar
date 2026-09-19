"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import styles from "./ink.module.css";
import { I } from "./icons";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

function useNow() {
  const [now, setNow] = useState(() => new Date());
  useEffect(() => {
    const t = setInterval(() => setNow(new Date()), 30_000);
    return () => clearInterval(t);
  }, []);
  return now;
}

export function InkHeader({ onMenu }: { onMenu: () => void }) {
  const router = useRouter();
  const { me } = useAuth();
  const [q, setQ] = useState("");
  const [notifCount, setNotifCount] = useState(0);
  const isNormalUser = !!me && me.role === "user" && !me.is_owner && !me.anonymous;

  useEffect(() => {
    if (isNormalUser) return;
    api
      .notifications()
      .then((r) => setNotifCount(r.notifications.length))
      .catch(() => {});
  }, [isNormalUser]);

  const displayName = me?.display_name || me?.email?.split("@")[0] || "User";
  const email = me?.email || "";
  const hour = new Date().getHours();
  const greet = hour < 12 ? "Good morning" : hour < 18 ? "Good afternoon" : "Good evening";

  return (
    <header className={styles.header}>
      <button type="button" className={styles.hamb} aria-label="Open menu" onClick={onMenu}>
        ☰
      </button>
      <div className={styles.headerLeft}>
        <h1 className={styles.headerGreet}>
          Welcome back, <span>{displayName}</span>
        </h1>
        <p className={styles.headerSub}>Track. Discover. Land your next opportunity.</p>
      </div>
      <div className={styles.searchWrap}>
        <I.search />
        <input
          className={styles.searchInput}
          placeholder="Search jobs, companies..."
          aria-label="Search"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") router.push(`/jobs${q.trim() ? `?q=${encodeURIComponent(q.trim())}` : ""}`);
          }}
        />
        <span className={styles.kbd} aria-hidden>
          <span>⌘</span>
          <span>K</span>
        </span>
      </div>
      <div className={styles.headRight}>
        {!isNormalUser && (
          <Link href="/notifications" className={styles.iconBtn} aria-label="Notifications">
            <I.bell />
            {notifCount > 0 && <span className={styles.dotRed} />}
          </Link>
        )}
        <Link href="/settings" className={styles.iconBtn} aria-label="Settings">
          <I.gear />
        </Link>
        <div className={styles.headerDivider} aria-hidden />
        <Link href="/preferences" className={styles.profilePill} aria-label="Account">
          <span className={styles.avatarSm} aria-hidden>
            {(me?.display_name || me?.email || (me?.anonymous ? "O" : "?")).trim()[0]?.toUpperCase() || "?"}
          </span>
          <span className={styles.profileMeta}>
            <span className={styles.profileName}>{displayName}</span>
            {email && <span className={styles.profileEmail}>{email}</span>}
          </span>
          <span className={styles.profileChev}>⌄</span>
        </Link>
      </div>
    </header>
  );
}
