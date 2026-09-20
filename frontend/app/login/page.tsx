"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { RadarMark } from "@/components/radar-mark";
import styles from "@/components/ink/ink.module.css";
import { ApiError, api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { errText } from "@/lib/format";

function isValidEmail(v: string): boolean {
  return /^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$/.test(v.trim()) && v.trim().length <= 254;
}

export default function LoginPage() {
  const router = useRouter();
  const { refresh, me, loading: authLoading } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPw, setShowPw] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && me && !me.anonymous) {
      if (me.status === "pending") router.replace("/pending");
      else if (me.status === "approved") router.replace("/dashboard");
    }
  }, [authLoading, me, router]);

  const canSubmit = isValidEmail(email) && password.length > 0 && !busy;

  async function submitPassword(e?: React.FormEvent) {
    e?.preventDefault();
    if (!canSubmit) return;
    setBusy(true);
    setError(null);
    try {
      await api.loginPassword(email.trim().toLowerCase(), password);
      await refresh();
      router.replace("/dashboard");
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.status === 401) setError("Invalid email or password — check for typos. Passwords are case-sensitive.");
        else if (err.status === 422) setError(err.message.replace(/^\d+ \w+: /, "").slice(0, 220));
        else if (err.status === 423) setError("Account temporarily locked due to 5 failed attempts — try again in 15 minutes. Contact support if you need a reset.");
        else if (err.status === 429) setError("Too many attempts — wait 5 minutes before retrying. Your IP is rate-limited.");
        else if (err.status === 403) {
          const msg = err.message.toLowerCase();
          if (msg.includes("pending")) setError("Your account is awaiting admin approval. You’ll be notified once approved.");
          else if (msg.includes("disabled")) setError("Your account has been disabled. Contact support.");
          else setError(errText(err));
        } else setError(errText(err));
      } else setError(errText(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className={styles.ink}>
      <div className={`${styles.shell} items-center justify-center`}>
      <div className="w-full max-w-[400px]">
        <div className="mb-8 flex flex-col items-center gap-3">
          <RadarMark />
          <span className="font-display text-lg font-bold tracking-[0.14em]">JOBQUEST</span>
          <span className={styles.eyebrow}>Secure sign in</span>
        </div>

        <form onSubmit={submitPassword} noValidate className="card space-y-4 p-6">
          <div>
            <h1 className="text-lg font-semibold">Sign in</h1>
            <p className="mt-1 text-sm text-text-secondary">Use your email and password. New accounts require admin approval before access.</p>
          </div>

          <div className={styles.field}>
            <label htmlFor="email" className={styles.fieldLabel}>Email</label>
            <input
              id="email"
              type="email"
              inputMode="email"
              autoComplete="email"
              autoFocus
              required
              placeholder="you@company.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="search-input w-full"
              aria-invalid={email ? !isValidEmail(email) : undefined}
            />
            {email && !isValidEmail(email) && <p className="mt-1 text-xs text-danger">Enter a valid email address</p>}
          </div>

          <div className={styles.field}>
            <div className="mb-1 flex items-center justify-between">
              <label htmlFor="password" className={styles.fieldLabel}>Password</label>
              <Link href="/unlock" className="text-xs text-text-muted hover:text-text">Forgot?</Link>
            </div>
            <div className="relative">
              <input
                id="password"
                type={showPw ? "text" : "password"}
                autoComplete="current-password"
                required
                placeholder="Your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="search-input w-full pr-10"
              />
              <button type="button" onClick={() => setShowPw((v) => !v)} className="absolute right-2 top-1/2 -translate-y-1/2 rounded px-2 py-1 text-xs text-text-muted hover:text-text" aria-label={showPw ? "Hide password" : "Show password"}>
                {showPw ? "Hide" : "Show"}
              </button>
            </div>
            <p className={styles.fieldHelp}>12+ characters, 3/4 categories. Lockout after 5 failures/15 min. Rate-limited 10/5 min.</p>
          </div>

          <button type="submit" disabled={!canSubmit} className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed">
            {busy ? "Signing in…" : "Sign in"}
          </button>
          {error && <p role="alert" className="rounded bg-danger/10 p-2 text-center text-sm leading-relaxed text-danger">{error}</p>}

          <div className="flex items-center gap-2 py-1">
            <span className="h-px flex-1 bg-border" />
            <span className="text-xs text-text-muted">or</span>
            <span className="h-px flex-1 bg-border" />
          </div>
          <p className="text-center text-xs text-text-muted">
            Don’t have an account? <Link href="/register" className="font-medium text-text hover:underline">Create account</Link>
          </p>
        </form>

        <div className="mt-4 flex justify-center gap-4 text-xs text-text-muted">
          <Link href="/pricing" className="hover:text-text">Pricing</Link>
          <span>•</span>
          <Link href="/unlock" className="hover:text-text">Unlock</Link>
        </div>
        <p className="mt-3 text-center text-xs leading-relaxed text-text-muted">Protected by HttpOnly Lax cookies, 7-day TTL, HSTS, and in-memory + DB lockout. Audit logged.</p>
      </div>
      </div>
    </div>
  );
}
