"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { RadarLoading } from "@/components/radar-loading";
import styles from "@/components/ink/ink.module.css";

export function PaywallGate({ children, feature = "Matches" }: { children: React.ReactNode; feature?: string }) {
  const { me, loading } = useAuth();
  if (loading) return <RadarLoading label="Checking access…" />;
  if (!me) return null;
  if (me.is_owner || me.role === "privileged" || me.role === "admin") return <>{children}</>;
  if (!me.access_locked) return <>{children}</>;
  // Locked: show paywall
  return (
    <div className={styles.stateWrap} style={{ padding: 32 }}>
      <p className={styles.stateTitle}>🔒 {feature} locked</p>
      <p className={styles.stateDesc}>
        Your account is active but needs an active subscription to view {feature.toLowerCase()} and receive Telegram alerts.
        Subscribe monthly or redeem a coupon code (1–12 months) from your admin.
      </p>
      <div className={styles.stateAction}>
        <Link href="/billing" className={styles.btnMint}>Go to Billing</Link>
        <Link href="/unlock" className={styles.btnLine}>Redeem Coupon</Link>
        <Link href="/pricing" className={styles.btnLine}>View Pricing</Link>
      </div>
      <p style={{ marginTop: 12, fontSize: 11, color: "var(--ink-muted)" }}>
        After payment or coupon redemption, {feature.toLowerCase()} will appear instantly and Telegram alerts resume.
      </p>
    </div>
  );
}
