"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { RadarMark } from "@/components/radar-mark";
import styles from "@/components/ink/ink.module.css";
import { ApiError, api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

// MNC: OWASP-aligned client-side checks mirror backend/app/auth.py
function isValidEmail(v: string): boolean {
  const s = v.trim();
  if (!s || s.length > 254 || s.split("@").length !== 2) return false;
  return /^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$/.test(s);
}
function displayNameError(v: string): string | null {
  const raw = v.trim().replace(/\s+/g, " ");
  if (!raw) return "Display name is required";
  if (raw.length < 2) return "At least 2 characters";
  if (raw.length > 50) return "At most 50 characters";
  if (!/^[A-Za-z0-9 .'_@\-]+$/.test(raw)) return "Letters, numbers, space, . ' _ @ - only";
  if (raw.includes("<") || raw.includes(">")) return "Must not contain < or >";
  return null;
}
function passwordIssues(pwd: string, email?: string, name?: string): string[] {
  const issues: string[] = [];
  if (pwd.length < 12) issues.push("12+ characters");
  if (pwd.length > 128) issues.push("at most 128 characters");
  const hasUpper = /[A-Z]/.test(pwd),
    hasLower = /[a-z]/.test(pwd),
    hasDigit = /[0-9]/.test(pwd),
    hasSpecial = /[!@#$%^&*()\-_=+[\]{}|;:',.<>?/`~"\\ ]/.test(pwd);
  const cats = [hasUpper, hasLower, hasDigit, hasSpecial].filter(Boolean).length;
  if (cats < 3) issues.push("3 of: upper, lower, number, special");
  if (["password", "123456", "qwerty", "admin", "welcome", "abc123", "password123"].includes(pwd.toLowerCase()))
    issues.push("too common");
  if (email) {
    const local = email.split("@")[0]?.toLowerCase();
    if (local && local.length >= 3 && pwd.toLowerCase().includes(local)) issues.push("must not contain email");
  }
  if (name) {
    for (const part of name.trim().split(/\s+/)) {
      if (part.length >= 3 && pwd.toLowerCase().includes(part.toLowerCase())) {
        issues.push("must not contain your name");
        break;
      }
    }
  }
  return issues;
}
function strengthScore(pwd: string): number {
  let s = 0;
  if (pwd.length >= 12) s++;
  if (/[A-Z]/.test(pwd) && /[a-z]/.test(pwd)) s++;
  if (/[0-9]/.test(pwd)) s++;
  if (/[!@#$%^&*()\-_=+[\]{}|;:',.<>?/`~]/.test(pwd)) s++;
  return Math.min(s, 4);
}

export default function RegisterPage() {
  const router = useRouter();
  const { refresh } = useAuth();
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [showPw, setShowPw] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const emailErr = useMemo(() => (email && !isValidEmail(email) ? "Enter a valid email address" : null), [email]);
  const nameErr = useMemo(() => (name ? displayNameError(name) : null), [name]);
  const pwIssues = useMemo(() => passwordIssues(password, email, name), [password, email, name]);
  const pwScore = useMemo(() => strengthScore(password), [password]);
  const confirmErr = useMemo(() => (confirm && confirm !== password ? "Passwords do not match" : null), [confirm, password]);

  const canSubmit = !busy && isValidEmail(email) && !nameErr && name.trim() && pwIssues.length === 0 && !confirmErr && password === confirm && password.length > 0;

  async function submit(e?: React.FormEvent) {
    e?.preventDefault();
    if (!canSubmit) return;
    setBusy(true);
    setError(null);
    try {
      await api.register({
        email: email.trim().toLowerCase(),
        display_name: name.trim(),
        password: password,
      });
      await refresh();
      router.replace("/dashboard");
      return;
    } catch (err) {
      let msg = "Please check your details and try again.";
      if (err instanceof ApiError) {
        if (err.status === 409) msg = "An account with this email already exists.";
        else if (err.status === 429) msg = "Too many registrations from this address — try again in an hour.";
        else if (err.status === 422) msg = err.message.replace(/^\d+ \w+: /, "").slice(0, 220);
        else msg = err.message.replace(/^\d+ \w+: /, "").slice(0, 220);
      }
      setError(msg);
    } finally {
      setBusy(false);
    }
  }

  if (success) {
    return (
      <div className={`flex min-h-screen items-center justify-center p-6 ${styles.ink}`}>
        <div className="w-full max-w-sm">
          <div className="mb-8 flex flex-col items-center gap-3">
            <RadarMark />
            <span className="font-display text-lg font-bold tracking-[0.14em]">JOBQUEST</span>
            <span className={styles.eyebrow}>Account created</span>
          </div>
          <div className="card space-y-4 p-6 text-center">
            <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-full bg-success/10 text-success">✓</div>
            <h1 className="text-lg font-semibold">Account created</h1>
            <p className="text-sm leading-relaxed text-text-secondary">
              You can now <strong>sign in</strong> with your email and password. Your dashboard, <strong>New Jobs Today</strong> and preferences are ready — <strong>Matches / New Matches</strong> and Telegram alerts unlock after monthly payment or a coupon (1–12 months) in Billing.
            </p>
            <button onClick={() => router.replace("/login")} className="btn-primary w-full">
              Continue to sign in
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`flex min-h-screen items-center justify-center p-6 ${styles.ink}`}>
      <div className="w-full max-w-[420px]">
        <div className="mb-8 flex flex-col items-center gap-3">
          <RadarMark />
          <span className="font-display text-lg font-bold tracking-[0.14em]">JOBQUEST</span>
          <span className={styles.eyebrow}>Create your account</span>
        </div>

        <form onSubmit={submit} noValidate className="card space-y-4 p-6">
          <div>
            <h1 className="text-lg font-semibold">Create your account</h1>
            <p className="mt-1 text-sm text-text-secondary">Sign in immediately after. <strong>Dashboard / New Jobs / Preferences / Billing</strong> are instant; <strong>Matches / New Matches / Telegram</strong> unlock after monthly payment or coupon.</p>
          </div>

          <div className={styles.field}>
            <label htmlFor="display_name" className={styles.fieldLabel}>Display name</label>
            <input
              id="display_name"
              autoComplete="name"
              required
              minLength={2}
              maxLength={50}
              placeholder="Alex Carter"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="search-input w-full"
              aria-invalid={!!nameErr}
              aria-describedby={nameErr ? "name-err" : undefined}
            />
            {nameErr ? <p id="name-err" className="mt-1 text-xs text-danger">{nameErr}</p> : <p className="mt-1 text-xs text-text-muted">2–50 chars, letters/numbers/space . &apos; _ @ -</p>}
          </div>

          <div className={styles.field}>
            <label htmlFor="email" className={styles.fieldLabel}>Work email</label>
            <input
              id="email"
              type="email"
              inputMode="email"
              autoComplete="email"
              required
              placeholder="you@company.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="search-input w-full"
              aria-invalid={!!emailErr}
              aria-describedby={emailErr ? "email-err" : undefined}
            />
            {emailErr ? <p id="email-err" className="mt-1 text-xs text-danger">{emailErr}</p> : <p className="mt-1 text-xs text-text-muted">We’ll never share your email. Lowercased and trimmed.</p>}
          </div>

          <div className={styles.field}>
            <label htmlFor="password" className={styles.fieldLabel}>Password</label>
            <div className="relative">
              <input
                id="password"
                type={showPw ? "text" : "password"}
                autoComplete="new-password"
                required
                placeholder="At least 12 characters"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="search-input w-full pr-10"
                aria-describedby="pw-help"
              />
              <button type="button" onClick={() => setShowPw((v) => !v)} className="absolute right-2 top-1/2 -translate-y-1/2 rounded px-2 py-1 text-xs text-text-muted hover:text-text" aria-label={showPw ? "Hide password" : "Show password"}>
                {showPw ? "Hide" : "Show"}
              </button>
            </div>
            {/* strength meter */}
            <div className="mt-2 flex gap-1">
              {[0, 1, 2, 3].map((i) => (
                <span key={i} className="h-1 flex-1 rounded" style={{ background: i < pwScore ? (pwScore >= 4 ? "#10b981" : pwScore >= 3 ? "#f59e0b" : "#ef4444") : "rgba(0,0,0,0.08)" }} />
              ))}
            </div>
            <ul id="pw-help" className="mt-2 grid grid-cols-1 gap-1 text-xs">
              <li className={password.length >= 12 ? "text-success" : "text-text-muted"}>{password.length >= 12 ? "✓" : "•"} 12+ characters (max 128)</li>
              <li className={[/[A-Z]/, /[a-z]/, /[0-9]/, /[!@#$%^&*()\-_=+[\]{}|;:',.<>?/`~]/].filter((r) => r.test(password)).length >= 3 ? "text-success" : "text-text-muted"}>
                {[/[A-Z]/, /[a-z]/, /[0-9]/, /[!@#$%^&*()\-_=+[\]{}|;:',.<>?/`~]/].filter((r) => r.test(password)).length >= 3 ? "✓" : "•"} 3 of: upper, lower, number, special
              </li>
              <li className={pwIssues.length === 0 && password ? "text-success" : "text-text-muted"}>
                {pwIssues.length === 0 && password ? "✓ Strong" : pwIssues.length ? `• ${pwIssues[0]}` : "• Not containing email or name, not common"}
              </li>
            </ul>
          </div>

          <div className={styles.field}>
            <label htmlFor="confirm" className={styles.fieldLabel}>Confirm password</label>
            <div className="relative">
              <input
                id="confirm"
                type={showConfirm ? "text" : "password"}
                autoComplete="new-password"
                required
                placeholder="Repeat password"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                className="search-input w-full pr-10"
                aria-invalid={!!confirmErr}
              />
              <button type="button" onClick={() => setShowConfirm((v) => !v)} className="absolute right-2 top-1/2 -translate-y-1/2 rounded px-2 py-1 text-xs text-text-muted hover:text-text" aria-label={showConfirm ? "Hide" : "Show"}>
                {showConfirm ? "Hide" : "Show"}
              </button>
            </div>
            {confirmErr ? <p className="mt-1 text-xs text-danger">{confirmErr}</p> : <p className="mt-1 text-xs text-text-muted">Re-enter to confirm.</p>}
          </div>

          <button type="submit" disabled={!canSubmit} className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed">
            {busy ? "Creating…" : "Create account"}
          </button>
          {error && <p role="alert" className="rounded bg-danger/10 p-2 text-center text-sm text-danger">{error}</p>}
          <p className="text-center text-xs leading-relaxed text-text-muted">
            By creating an account you agree to our Terms and acknowledge our security policy. Brute-force protected (5/h per IP) and lockout on login.
          </p>
        </form>

        <p className="mt-4 text-center text-xs text-text-muted">
          Already have an account? <Link href="/login" className="font-medium text-text hover:underline">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
