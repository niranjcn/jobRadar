"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  ArrowRightIcon as ArrowRight,
  CheckIcon as Check,
  LockIcon as Lock,
  MailIcon as Mail,
  ShieldCheckIcon as ShieldCheck,
  SunIcon as Sun,
  UserIcon as User,
} from "./icons";
import { AuthLeft } from "./auth-left";
import styles from "./auth.module.css";
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
  const [acceptTerms, setAcceptTerms] = useState(false);

  const emailErr = useMemo(() => (email && !isValidEmail(email) ? "Enter a valid email address" : null), [email]);
  const nameErr = useMemo(() => (name ? displayNameError(name) : null), [name]);
  const pwIssues = useMemo(() => passwordIssues(password, email, name), [password, email, name]);
  const confirmErr = useMemo(() => (confirm && confirm !== password ? "Passwords do not match" : null), [confirm, password]);

  const ruleLen = password.length >= 12 && password.length <= 128;
  const ruleCats =
    [/[A-Z]/, /[a-z]/, /[0-9]/, /[!@#$%^&*()\-_=+[\]{}|;:',.<>?/`~]/].filter((r) => r.test(password)).length >= 3;
  const ruleClean = password.length > 0 && pwIssues.length === 0;

  const canSubmit = !busy && isValidEmail(email) && !nameErr && name.trim() && pwIssues.length === 0 && !confirmErr && password === confirm && password.length > 0 && acceptTerms;

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
        accept_terms: acceptTerms,
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
      <div className={styles.successWrap}>
        <div className={styles.successCard}>
          <div className={styles.successCheck}>
            <Check size={22} strokeWidth={2.5} />
          </div>
          <h1 style={{ fontSize: 20, fontWeight: 700, margin: "14px 0 0" }}>Account created</h1>
          <p style={{ fontSize: 14, lineHeight: 1.6, color: "#66716f", margin: "10px 0 0" }}>
            You can now <strong>sign in</strong> with your email and password. Your dashboard, <strong>New Jobs Today</strong> and
            preferences are ready — <strong>Matches / New Matches</strong> and Telegram alerts unlock after monthly payment or a
            coupon (1–12 months) in Billing.
          </p>
          <button onClick={() => router.replace("/login")} className={styles.submit} style={{ marginTop: 20 }}>
            Continue to sign in
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <AuthLeft />

      {/* RIGHT */}
      <div className={styles.right}>
        <div className={styles.topbar}>
          <span className={styles.sunIcon}>
            <Sun size={20} strokeWidth={1.8} />
          </span>
          <span>Already have an account?</span>
          <Link href="/login" className={styles.signInBtn}>
            Sign in
          </Link>
        </div>

        <div className={styles.card}>
          <div className={styles.cardHead}>
            <p className={styles.cardEyebrow}>Welcome to JobQuest</p>
            <div className={styles.dots} aria-hidden>
              <span className={styles.dot} style={{ background: "#43C596" }} />
              <span className={styles.dot} style={{ background: "#B9E9DA" }} />
              <span className={styles.dot} style={{ background: "#B9E9DA" }} />
            </div>
          </div>

          <h2 className={styles.cardTitle}>Create your account</h2>
          <p className={styles.cardDesc}>
            Dashboard, New Jobs, Preferences and Billing are instant; Matches and Telegram unlock after payment or coupon.
          </p>

          <form onSubmit={submit} noValidate className={styles.form}>
            <div>
              <label htmlFor="display_name" className={styles.fieldLabel}>
                Display name
              </label>
              <div className={styles.inputWrap}>
                <span className={styles.inputIcon}>
                  <User size={18} strokeWidth={1.8} />
                </span>
                <input
                  id="display_name"
                  autoComplete="name"
                  required
                  minLength={2}
                  maxLength={50}
                  placeholder="e.g. Niranj CN"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className={styles.input}
                  aria-invalid={!!nameErr}
                />
              </div>
              {nameErr ? (
                <p className={styles.fieldError}>{nameErr}</p>
              ) : (
                <p className={styles.helper}>2–50 chars, letters/numbers/space .. &apos; _ @ -</p>
              )}
            </div>

            <div>
              <label htmlFor="email" className={styles.fieldLabel}>
                Work email
              </label>
              <div className={styles.inputWrap}>
                <span className={styles.inputIcon}>
                  <Mail size={18} strokeWidth={1.8} />
                </span>
                <input
                  id="email"
                  type="email"
                  inputMode="email"
                  autoComplete="email"
                  required
                  placeholder="you@company.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className={styles.input}
                  aria-invalid={!!emailErr}
                />
              </div>
              {emailErr ? (
                <p className={styles.fieldError}>{emailErr}</p>
              ) : (
                <p className={styles.helper}>We’ll never share your email. Lowercased and trimmed.</p>
              )}
            </div>

            <div>
              <label htmlFor="password" className={styles.fieldLabel}>
                Password
              </label>
              <div className={styles.inputWrap}>
                <span className={styles.inputIcon}>
                  <Lock size={18} strokeWidth={1.8} />
                </span>
                <input
                  id="password"
                  type={showPw ? "text" : "password"}
                  autoComplete="new-password"
                  required
                  placeholder="Create a strong password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className={styles.input}
                  style={{ paddingRight: 64 }}
                />
                <button type="button" onClick={() => setShowPw((v) => !v)} className={styles.showBtn}>
                  {showPw ? "Hide" : "Show"}
                </button>
              </div>
              <ul className={styles.rules}>
                <li className={styles.rule}>
                  <span className={`${styles.ruleDot} ${ruleLen ? styles.ruleMet : ""}`} />
                  12+ chars (max 128)
                </li>
                <li className={styles.rule}>
                  <span className={`${styles.ruleDot} ${ruleCats ? styles.ruleMet : ""}`} />
                  upper, lower, number, special (3 of 4)
                </li>
                <li className={styles.rule}>
                  <span className={`${styles.ruleDot} ${ruleClean ? styles.ruleMet : ""}`} />
                  12+ characters
                </li>
              </ul>
            </div>

            <div>
              <label htmlFor="confirm" className={styles.fieldLabel}>
                Confirm password
              </label>
              <div className={styles.inputWrap}>
                <span className={styles.inputIcon}>
                  <Lock size={18} strokeWidth={1.8} />
                </span>
                <input
                  id="confirm"
                  type={showConfirm ? "text" : "password"}
                  autoComplete="new-password"
                  required
                  placeholder="Re-enter your password"
                  value={confirm}
                  onChange={(e) => setConfirm(e.target.value)}
                  className={styles.input}
                  style={{ paddingRight: 64 }}
                  aria-invalid={!!confirmErr}
                />
                <button type="button" onClick={() => setShowConfirm((v) => !v)} className={styles.showBtn}>
                  {showConfirm ? "Hide" : "Show"}
                </button>
              </div>
              {confirmErr ? <p className={styles.fieldError}>{confirmErr}</p> : <p className={styles.helper}>Re-enter to confirm.</p>}
            </div>

            <label className={styles.terms}>
              <input
                type="checkbox"
                checked={acceptTerms}
                onChange={(e) => setAcceptTerms(e.target.checked)}
                className={styles.checkbox}
              />
              <span>
                I agree to the{" "}
                <Link href="/terms" target="_blank">
                  Terms of Service
                </Link>{" "}
                and{" "}
                <Link href="/privacy" target="_blank">
                  Privacy Policy
                </Link>
                .
              </span>
            </label>

            <div className={styles.secure}>
              <ShieldCheck size={18} strokeWidth={1.8} />
              <span>Brute-force protected and lockout on login.</span>
            </div>

            <button type="submit" disabled={!canSubmit} className={styles.submit}>
              {busy ? "Creating…" : "Create your account"}
              <span className={styles.submitArrow}>
                <ArrowRight size={20} strokeWidth={2} />
              </span>
            </button>
            {error && (
              <p role="alert" className={styles.formError}>
                {error}
              </p>
            )}
          </form>

          <hr className={styles.divider} />
          <p className={styles.bottomSign}>
            Already have an account? <Link href="/login">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
