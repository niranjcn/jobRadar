import { LEGAL, LegalH, LegalList, LegalP, LegalShell } from "@/components/legal-shell";

export const metadata = {
  title: "JobQuest · Privacy Policy",
  description: "Privacy Policy for JobQuest job alerts.",
};

const SECTIONS = [
  { id: "collection", title: "Data we collect" },
  { id: "purpose", title: "Why we use it" },
  { id: "sharing", title: "Sharing" },
  { id: "retention", title: "How long we keep things" },
  { id: "rights", title: "Your rights" },
  { id: "children", title: "Children" },
  { id: "security", title: "Security" },
  { id: "grievance", title: "Grievance redressal" },
  { id: "changes", title: "Changes to this policy" },
];

export default function PrivacyPage() {
  return (
    <LegalShell
      eyebrow="Legal"
      title="Privacy Policy"
      intro="This policy explains what personal data we collect, why, how long we keep it, and the rights you have under India's DPDP Act 2023 (and GDPR/CAN-SPAM principles for users elsewhere)."
      sections={SECTIONS}
    >
      <LegalH id="collection" index={1}>Data we collect</LegalH>
      <LegalList>
        <li>
          <strong>Account:</strong> email address, display name, password hash (never the password
          itself), Telegram chat ID (only if you link it), and the timestamp of your Terms
          acceptance.
        </li>
        <li>
          <strong>Preferences:</strong> roles, keywords, locations, seniority, exclusions, and alert
          settings — used solely for matching and alerts.
        </li>
        <li>
          <strong>Service data:</strong> subscription and coupon records (via Razorpay, our payment
          processor), login/security events (IP address, user agent, timestamps), and rate-limit
          counters.
        </li>
        <li>
          <strong>Derived data:</strong> your job matches and alert-delivery records.
        </li>
      </LegalList>
      <LegalP>We collect no marketing profiles and run no ad trackers.</LegalP>

      <LegalH id="purpose" index={2}>Why we use it</LegalH>
      <LegalP>
        Your data is used only to operate the service: authenticate you, match jobs to your stated
        preferences, deliver the alerts you enabled, bill your subscription, prevent abuse, and keep
        the service secure. Preferences are never used for marketing and never sold.
      </LegalP>

      <LegalH id="sharing" index={3}>Sharing</LegalH>
      <LegalP>
        We share data only with processors needed to run the service: Razorpay (payments), Telegram
        (alert delivery, message content only), and our hosting provider (database). We do not sell
        personal data. Employer career pages receive no personal data from us.
      </LegalP>

      <LegalH id="retention" index={4}>How long we keep things</LegalH>
      <LegalP>We keep each category only as long as its purpose lasts:</LegalP>
      <LegalList>
        <li>Job matches: 24 hours, then automatically pruned.</li>
        <li>Alert-delivery records: 24 hours, then automatically pruned.</li>
        <li>Login/security events: 90 days, then automatically pruned.</li>
        <li>Job listings: 30 days after last seen (7 days once a posting disappears).</li>
        <li>Account, preferences, subscriptions: until you delete your account.</li>
        <li>Rate-limit counters: 24 hours.</li>
      </LegalList>

      <LegalH id="rights" index={5}>Your rights</LegalH>
      <LegalP>You may at any time:</LegalP>
      <LegalList>
        <li>
          <strong>Access</strong> everything we store about you — Billing → export, or API{" "}
          <code>/api/auth/me/export</code>.
        </li>
        <li>
          <strong>Correct</strong> your profile and preferences.
        </li>
        <li>
          <strong>Erase</strong> your account including matches and alert history — Billing → delete
          account, or API <code>DELETE /api/auth/me</code>. Erasure is immediate except anonymized
          security logs retained for fraud prevention.
        </li>
      </LegalList>
      <LegalP>
        To exercise any right, or to withdraw consent, write to {LEGAL.email} — we respond within 30
        days.
      </LegalP>

      <LegalH id="children" index={6}>Children</LegalH>
      <LegalP>
        JobQuest is not directed at children under 16. Accounts found to belong to children are
        removed.
      </LegalP>

      <LegalH id="security" index={7}>Security</LegalH>
      <LegalP>
        Passwords are stored as salted PBKDF2 hashes (600,000 iterations), never plaintext. Sessions
        use HttpOnly, SameSite cookies; failed logins trigger progressive lockout. No method is
        perfect — if you suspect unauthorized access, change your password and contact us
        immediately.
      </LegalP>

      <LegalH id="grievance" index={8}>Grievance redressal</LegalH>
      <LegalP>
        Grievance Officer: {LEGAL.grievanceName} — {LEGAL.grievanceEmail}. We acknowledge grievances
        within 24 hours and resolve them within 15 days, per applicable law.
      </LegalP>

      <LegalH id="changes" index={9}>Changes to this policy</LegalH>
      <LegalP>
        Material changes will be announced in-app at least 7 days before taking effect.{" "}
        {LEGAL.address}.
      </LegalP>
    </LegalShell>
  );
}
