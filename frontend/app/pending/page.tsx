"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { RadarMark } from "@/components/radar-mark";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";

export default function PendingPage() {
  const router = useRouter();
  const { me, loading, refresh } = useAuth();

  useEffect(() => {
    if (!loading && me && me.status === "approved" && !me.access_locked) router.replace("/");
    if (!loading && me && me.status === "approved" && me.access_locked) router.replace("/unlock");
  }, [loading, me, router]);

  async function logout() {
    await api.logout();
    await refresh();
    router.replace("/login");
  }

  if (loading) return null;

  return (
    <div className="flex min-h-screen items-center justify-center p-6">
      <div className="w-full max-w-md">
        <div className="mb-8 flex flex-col items-center gap-3">
          <RadarMark />
          <span className="font-display text-lg font-bold tracking-[0.14em]">JOBRADAR</span>
        </div>
        <div className="card space-y-4 p-6 text-center">
          <h1 className="text-lg font-semibold">Awaiting admin approval</h1>
          <p className="text-sm text-text-secondary">
            Your account <span className="font-medium text-text">{me?.email || ""}</span> is pending approval. An admin will review it shortly. You&apos;ll be able to sign in once approved.
          </p>
          <p className="text-xs text-text-muted">You can close this page — you&apos;ll get access automatically after approval. Try signing in again later.</p>
          <button onClick={logout} className="btn-ghost w-full text-sm">
            Sign out
          </button>
        </div>
      </div>
    </div>
  );
}
