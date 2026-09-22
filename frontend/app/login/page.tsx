"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  ArrowRightIcon as ArrowRight,
  LockIcon as Lock,
  MailIcon as Mail,
  ShieldCheckIcon as ShieldCheck,
  SunIcon as Sun,
} from "../register/icons";
import { AuthLeft } from "../register/auth-left";
import styles from "../register/auth.module.css";
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
    <div className={styles.page}>
      <AuthLeft />

      {/* RIGHT */}
      <div className={styles.right}>
        <div className={styles.topbar}>
          <span className={styles.sunIcon}>
            <Sun size={20} strokeWidth={1.8} />
          </span>
          <span>New to JobQuest?</span>
          <Link href="/register" className={styles.signInBtn}>
            Create account
          </Link>
        </div>

        <div className={styles.cardCenterWrap}>
        <div className={styles.card}>
          <div className={styles.cardHead}>
            <p className={styles.cardEyebrow}>Welcome back</p>
            <div className={styles.dots} aria-hidden>
              <span className={styles.dot} style={{ background: "#43C596" }} />
              <span className={styles.dot} style={{ background: "#B9E9DA" }} />
              <span className={styles.dot} style={{ background: "#B9E9DA" }} />
            </div>
          </div>

          <h2 className={styles.cardTitle}>Sign in</h2>
          <p className={styles.cardDesc}>
            Use your email and password. New accounts require admin approval before access.
          </p>

          <form onSubmit={submitPassword} noValidate className={styles.form}>
            <div>
              <label htmlFor="email" className={styles.fieldLabel}>
                Email
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
                  autoFocus
                  required
                  placeholder="you@company.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className={styles.input}
                  aria-invalid={email ? !isValidEmail(email) : undefined}
                />
              </div>
              {email && !isValidEmail(email) ? (
                <p className={styles.fieldError}>Enter a valid email address</p>
              ) : (
                <p className={styles.helper}>The email you registered with.</p>
              )}
            </div>

            <div>
              <div className={styles.labelRow}>
                <label htmlFor="password" className={styles.fieldLabel}>
                  Password
                </label>
                <Link href="/unlock" className={styles.forgotLink}>
                  Forgot?
                </Link>
              </div>
              <div className={styles.inputWrap}>
                <span className={styles.inputIcon}>
                  <Lock size={18} strokeWidth={1.8} />
                </span>
                <input
                  id="password"
                  type={showPw ? "text" : "password"}
                  autoComplete="current-password"
                  required
                  placeholder="Your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className={styles.input}
                  style={{ paddingRight: 64 }}
                />
                <button type="button" onClick={() => setShowPw((v) => !v)} className={styles.showBtn}>
                  {showPw ? "Hide" : "Show"}
                </button>
              </div>
              <p className={styles.helper}>Lockout after 5 failures/15 min. Rate-limited 10/5 min.</p>
            </div>

            <div className={styles.secure}>
              <ShieldCheck size={18} strokeWidth={1.8} />
              <span>Brute-force protected and lockout on login.</span>
            </div>

            <button type="submit" disabled={!canSubmit} className={styles.submit}>
              {busy ? "Signing in…" : "Sign in"}
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
            Don&rsquo;t have an account? <Link href="/register">Create account</Link>
          </p>
        </div>
        </div>
      </div>
    </div>
  );
}
