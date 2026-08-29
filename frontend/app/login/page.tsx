"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { RadarMark } from "@/components/radar-mark";
import { ApiError, api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { errText } from "@/lib/format";

export default function LoginPage() {
  const router = useRouter();
  const { refresh, me, loading: authLoading } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && me && !me.anonymous) {
      if (me.status === "pending") router.replace("/pending");
      else if (me.status === "approved" && !me.access_locked) router.replace("/");
    }
  }, [authLoading, me, router]);

  async function submitPassword() {
    setBusy(true);
    setError(null);
    try {
      await api.loginPassword(email.trim(), password);
      await refresh();
      router.replace("/");
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.status === 401) {
          setError("Invalid email or password.");
        } else if (err.status === 403) {
          const msg = err.message.toLowerCase();
          if (msg.includes("pending")) setError("Your account is awaiting admin approval. You'll be notified once approved.");
          else if (msg.includes("disabled")) setError("Your account has been disabled. Contact support.");
          else setError(errText(err));
        } else {
          setError(errText(err));
        }
      } else {
        setError(errText(err));
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-6">
      <div className="w-full max-w-sm">
        <div className="mb-8 flex flex-col items-center gap-3">
          <RadarMark />
          <span className="font-display text-lg font-bold tracking-[0.14em]">JOBRADAR</span>
        </div>

        <div className="card space-y-4 p-6">
          <h1 className="text-lg font-semibold">Sign in</h1>
          <p className="text-sm text-text-secondary">Use your email and password. New accounts require admin approval.</p>
          <input
            type="email"
            autoFocus
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="search-input w-full"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && email.trim() && password && !busy && submitPassword()}
            className="search-input w-full"
          />
          <button onClick={submitPassword} disabled={busy || !email.trim() || !password} className="btn-primary w-full">
            {busy ? "Signing in…" : "Sign in"}
          </button>
          {error && <p className="text-center text-sm text-danger">{error}</p>}
        </div>

        <div className="mt-4 flex justify-center text-xs text-text-muted">
          <Link href="/pricing" className="hover:text-text">
            Pricing
          </Link>
        </div>
      </div>
    </div>
  );
}
