import Link from "next/link";
import { RadarMark } from "@/components/radar-mark";
import styles from "@/components/ink/ink.module.css";

export const LEGAL_UPDATED = "September 2026";

// Business identity placeholders — replace before going live (see docs/10k-hosting-plan.md §4).
export const LEGAL = {
  entity: "[LEGAL_ENTITY_NAME]",
  email: "[SUPPORT_EMAIL]",
  address: "[BUSINESS_ADDRESS]",
  domain: "[DOMAIN]",
  grievanceName: "[GRIEVANCE_OFFICER_NAME]",
  grievanceEmail: "[GRIEVANCE_OFFICER_EMAIL]",
};

export function LegalShell({
  eyebrow,
  title,
  children,
}: {
  eyebrow: string;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className={styles.ink} style={{ zoom: 1 }}>
      <div className={`${styles.shell} flex-col items-center px-6 py-14`}>
        <Link href="/" className="mb-10 flex flex-col items-center gap-3">
          <RadarMark size={32} />
          <span className="font-display text-lg font-bold tracking-[0.14em]">JOBQUEST</span>
          <span className={styles.eyebrow}>{eyebrow}</span>
        </Link>

        <h1 className="max-w-2xl text-center font-display text-3xl font-bold">{title}</h1>
        <p className="mt-2 text-xs text-text-muted">Last updated: {LEGAL_UPDATED}</p>

        <div className={`${styles.panel} mt-10 w-full max-w-2xl`}>
          <div
            style={{
              padding: "26px 28px",
              position: "relative",
              fontSize: 14,
              lineHeight: 1.75,
              color: "var(--ink-text2)",
            }}
            className="legal-prose"
          >
            {children}
          </div>
        </div>

        <div
          className="mt-8 flex flex-wrap justify-center gap-x-5 gap-y-2 text-xs text-text-muted"
        >
          <Link href="/terms" className="hover:text-text">
            Terms
          </Link>
          <Link href="/privacy" className="hover:text-text">
            Privacy
          </Link>
          <Link href="/refund" className="hover:text-text">
            Refunds
          </Link>
          <Link href="/contact" className="hover:text-text">
            Contact
          </Link>
          <Link href="/pricing" className="hover:text-text">
            Pricing
          </Link>
        </div>
      </div>
    </div>
  );
}
