"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { RadarLoading } from "@/components/radar-loading";
import { useAuth } from "@/lib/auth-context";

export function AuthGate({ children }: { children: React.ReactNode }) {
  const { me, loading } = useAuth();
  const router = useRouter();
  const [holding, setHolding] = useState(true);

  useEffect(() => {
    if (loading) return;
    if (!me) {
      router.replace("/login");
      return;
    }
    if (me.status === "pending") {
      router.replace("/pending");
      return;
    }
    // Locked users can still access dashboard/new-jobs/preferences/billing — paywalled pages handle their own gate
    setHolding(false);
  }, [loading, me, router]);

  if (loading || holding || !me || me.status === "pending") {
    return <RadarLoading label="Checking access…" />;
  }
  return <>{children}</>;
}
