"use client";

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

export type LegalSection = { id: string; title: string };

export function LegalShell({
  eyebrow,
  title,
  intro,
  sections,
  children,
}: {
  eyebrow: string;
  title: string;
  intro: string;
  sections: LegalSection[];
  children: React.ReactNode;
}) {
  return (
    <div className={styles.ink} style={{ zoom: 1 }}>
      <div className={`${styles.shell} flex-col items-center px-6 py-14`}>
        <Link href="/" className="mb-8 flex items-center gap-3">
          <RadarMark size={28} />
          <span className="font-display text-base font-bold tracking-[0.14em]">JOBQUEST</span>
        </Link>

        <p className={styles.eyebrow} style={{ textAlign: "center" }}>
          {eyebrow}
        </p>
        <h1
          className="font-display"
          style={{
            maxWidth: 720,
            textAlign: "center",
            fontSize: 34,
            fontWeight: 800,
            letterSpacing: "-0.02em",
            margin: "10px 0 0",
            color: "var(--ink-text)",
          }}
        >
          {title}
        </h1>
        <p
          style={{
            maxWidth: 640,
            textAlign: "center",
            fontSize: 14,
            color: "var(--ink-muted)",
            margin: "12px 0 0",
            lineHeight: 1.6,
          }}
        >
          {intro}
        </p>
        <p style={{ fontSize: 12, color: "var(--ink-muted)", margin: "10px 0 0" }}>
          Last updated: {LEGAL_UPDATED} · Operated by {LEGAL.entity}
        </p>

        <nav
          aria-label="Contents"
          style={{
            width: "100%",
            maxWidth: 720,
            marginTop: 28,
            border: "1px solid var(--ink-border)",
            borderRadius: 14,
            background: "rgba(255,255,255,0.03)",
            padding: "16px 20px",
          }}
        >
          <p
            style={{
              fontSize: 11,
              fontWeight: 800,
              letterSpacing: "0.14em",
              textTransform: "uppercase",
              color: "var(--ink-muted)",
              margin: "0 0 10px",
            }}
          >
            Contents
          </p>
          <ol style={{ margin: 0, padding: 0, listStyle: "none", display: "grid", gap: 6 }}>
            {sections.map((s, i) => (
              <li key={s.id} style={{ fontSize: 13.5 }}>
                <a
                  href={`#${s.id}`}
                  style={{ color: "var(--ink-text2)", textDecoration: "none" }}
                  onMouseEnter={(e) => ((e.target as HTMLAnchorElement).style.color = "var(--ink-text)")}
                  onMouseLeave={(e) => ((e.target as HTMLAnchorElement).style.color = "var(--ink-text2)")}
                >
                  <span style={{ color: "var(--ink-muted)", fontVariantNumeric: "tabular-nums" }}>
                    {String(i + 1).padStart(2, "0")}
                  </span>{" "}
                  {s.title}
                </a>
              </li>
            ))}
          </ol>
        </nav>

        <article
          style={{
            width: "100%",
            maxWidth: 720,
            marginTop: 8,
            fontSize: 14.5,
            lineHeight: 1.8,
            color: "var(--ink-text2)",
          }}
        >
          {children}
        </article>

        <div className="mt-10 flex flex-wrap justify-center gap-x-5 gap-y-2 text-xs text-text-muted">
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

export function LegalH({ id, index, children }: { id: string; index: number; children: React.ReactNode }) {
  return (
    <h2
      id={id}
      style={{
        color: "var(--ink-text)",
        fontSize: 17,
        fontWeight: 800,
        letterSpacing: "-0.01em",
        margin: "30px 0 10px",
        paddingTop: 6,
        scrollMarginTop: 24,
      }}
    >
      <span style={{ color: "var(--ink-muted)", fontWeight: 700, marginRight: 10, fontVariantNumeric: "tabular-nums" }}>
        {index}
      </span>
      {children}
    </h2>
  );
}

export function LegalP({ children }: { children: React.ReactNode }) {
  return <p style={{ margin: "0 0 12px" }}>{children}</p>;
}

export function LegalList({ children }: { children: React.ReactNode }) {
  return <ul style={{ margin: "0 0 12px 20px", padding: 0, listStyle: "disc", display: "grid", gap: 4 }}>{children}</ul>;
}
