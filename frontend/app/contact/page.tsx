import { LEGAL, LegalShell } from "@/components/legal-shell";

export const metadata = {
  title: "JobQuest · Contact",
  description: "Contact JobQuest support, billing, and grievance redressal.",
};

function H({ children }: { children: React.ReactNode }) {
  return (
    <h2 style={{ color: "var(--ink-text)", fontSize: 16, fontWeight: 700, margin: "22px 0 8px" }}>
      {children}
    </h2>
  );
}

function P({ children }: { children: React.ReactNode }) {
  return <p style={{ margin: "0 0 10px" }}>{children}</p>;
}

export default function ContactPage() {
  return (
    <LegalShell eyebrow="Legal" title="Contact">
      <H>Support & billing</H>
      <P>
        Email: {LEGAL.email}
        <br />
        {LEGAL.entity} · {LEGAL.address}
      </P>
      <P>
        For billing issues include your account email and Razorpay payment ID (from your bank
        statement or the checkout receipt). Most issues are resolved within 48 hours.
      </P>
      <H>Employer listing corrections</H>
      <P>
        If a job listing on JobQuest is stale, wrong, or should not be shown, write to{" "}
        {LEGAL.email} with the job link and we will correct or remove it promptly.
      </P>
      <H>Grievance redressal (DPDP Act)</H>
      <P>
        Grievance Officer: {LEGAL.grievanceName} — {LEGAL.grievanceEmail}. Acknowledgement within 24
        hours, resolution within 15 days.
      </P>
    </LegalShell>
  );
}
