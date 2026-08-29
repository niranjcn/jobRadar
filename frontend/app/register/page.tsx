"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { RadarMark } from "@/components/radar-mark";
import { ApiError, api } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  async function submit() {
    setBusy(true);
    setError(null);
    try {
      await api.register({
        email: email.trim(),
        display_name: name.trim(),
        password: password,
      });
      setSuccess(true);
    } catch (err) {
      const message =
        err instanceof ApiError && err.status === 409
          ? "An account with this email already exists."
          : err instanceof ApiError && err.status === 422
            ? err.message.replace(/^\d+ \w+: /, "")
            : "Please enter a valid email and password.";
      setError(message);
    } finally {
      setBusy(false);
    }
  }

  if (success) {
    return (
      <div className="flex min-h-screen items-center justify-center p-6">
        <div className="w-full max-w-sm">
          <div className="mb-8 flex flex-col items-center gap-3">
            <RadarMark />
            <span className="font-display text-lg font-bold tracking-[0.14em]">JOBRADAR</span>
          </div>
          <div className="card space-y-4 p-6 text-center">
            <h1 className="text-lg font-semibold">Registration submitted</h1>
            <p className="text-sm text-text-secondary">
              Your account is awaiting admin approval. You&apos;ll be able to sign in once an admin approves it.
            </p>
            <button onClick={() => router.replace("/login")} className="btn-primary w-full">
              Back to sign in
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-6">
      <div className="w-full max-w-sm">
        <div className="mb-8 flex flex-col items-center gap-3">
          <RadarMark />
          <span className="font-display text-lg font-bold tracking-[0.14em]">JOBRADAR</span>
        </div>

        <div className="card space-y-4 p-6">
          <h1 className="text-lg font-semibold">Create your account</h1>
          <p className="text-sm text-text-secondary">Admin approval is required before you can sign in.</p>
          <input
            className="search-input w-full"
            placeholder="Display name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <input
            type="email"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="search-input w-full"
          />
          <div>
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && email.trim() && password && !busy && submit()}
              className="search-input w-full"
            />
            <p className="mt-1 text-xs text-text-muted">Min 8 characters with a letter and number.</p>
          </div>
          <button onClick={submit} disabled={busy || !email.trim() || !password} className="btn-primary w-full">
            {busy ? "Creating…" : "Create account"}
          </button>
          {error && <p className="text-center text-sm text-danger">{error}</p>}
        </div>

        <p className="mt-4 text-center text-xs text-text-muted">
          Already have an account?{" "}
          <Link href="/login" className="hover:text-text">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
