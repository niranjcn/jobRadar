import { LEGAL, LegalH, LegalP, LegalShell } from "@/components/legal-shell";

export const metadata = {
  title: "JobQuest · Contact",
  description: "Contact JobQuest support, billing, and grievance redressal.",
};

const SECTIONS = [
  { id: "support", title: "Support & billing" },
  { id: "listings", title: "Employer listing corrections" },
  { id: "grievance", title: "Grievance redressal" },
];

export default function ContactPage() {
  return (
    <LegalShell
      eyebrow="Legal"
      title="Contact"
      intro="How to reach us for support, billing, listing corrections, and grievance redressal."
      sections={SECTIONS}
    >
      <LegalH id="support" index={1}>Support & billing</LegalH>
      <LegalP>
        Email: {LEGAL.email}
        <br />
        {LEGAL.entity} · {LEGAL.address}
      </LegalP>
      <LegalP>
        For billing issues include your account email and Razorpay payment ID (from your bank
        statement or the checkout receipt). Most issues are resolved within 48 hours.
      </LegalP>

      <LegalH id="listings" index={2}>Employer listing corrections</LegalH>
      <LegalP>
        If a job listing on JobQuest is stale, wrong, or should not be shown, write to{" "}
        {LEGAL.email} with the job link and we will correct or remove it promptly.
      </LegalP>

      <LegalH id="grievance" index={3}>Grievance redressal (DPDP Act)</LegalH>
      <LegalP>
        Grievance Officer: {LEGAL.grievanceName} — {LEGAL.grievanceEmail}. Acknowledgement within 24
        hours, resolution within 15 days.
      </LegalP>
    </LegalShell>
  );
}
