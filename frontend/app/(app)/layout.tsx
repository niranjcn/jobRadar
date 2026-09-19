import { AuthGate } from "@/components/auth-gate";
import { InkShell } from "@/components/ink/InkShell";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGate>
      <InkShell>{children}</InkShell>
    </AuthGate>
  );
}
