import { AuthGate } from "@/components/auth-gate";
import { Sidebar } from "@/components/sidebar";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGate>
      <div className="flex min-h-screen">
        <Sidebar />
        <main className="flex-1 overflow-y-auto">{children}</main>
      </div>
    </AuthGate>
  );
}