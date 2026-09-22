import { LEGAL, LegalShell } from "@/components/legal-shell";

export const metadata = {
  title: "JobQuest · Privacy Policy",
  description: "Privacy Policy for JobQuest job alerts.",
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

export default function PrivacyPage() {
  return (
    <LegalShell eyebrow="Legal" title="Privacy Policy">
      <P>
        {LEGAL.entity} (“we”, “us”) operates JobQuest. This policy explains what personal data we
        collect, why, how long we keep it, and the rights you have under India&apos;s DPDP Act 2023
        (and GDPR/CAN-SPAM principles for users elsewhere). Contact: {LEGAL.email}.
      </P>
      <H>1. Data we collect</H>
      <P>
        <strong>Account:</strong> email address, display name, password hash (never the password),
        Telegram chat ID (only if you link it), and the timestamp of your Terms acceptance.{" "}
        <strong>Preferences:</strong> roles, keywords, locations, seniority, exclusions, and alert
        settings — used solely for matching and alerts. <strong>Service data:</strong> subscription
        and coupon records (via Razorpay, our payment processor), login/security events (IP address,
        user agent, timestamps), and rate-limit counters. <strong>Derived data:</strong> your job
        matches and alert-delivery records. We collect no marketing profiles and run no ad trackers.
      </P>
      <H>2. Why we use it (purpose limitation)</H>
      <P>
        Your data is used only to operate the service: authenticate you, match jobs to your stated
        preferences, deliver the alerts you enabled, bill your subscription, prevent abuse, and keep
        the service secure. Preferences are never used for marketing and never sold.
      </P>
      <H>3. Sharing</H>
      <P>
        We share data only with processors needed to run the service: Razorpay (payments), Telegram
        (alert delivery, message content only), and our hosting provider (database). We do not sell
        personal data. Employer career pages receive no personal data from us.
      </P>
      <H>4. Retention — how long we keep things</H>
      <P>We keep each category only as long as its purpose lasts:</P>
      <ul style={{ margin: "0 0 10px 18px", padding: 0, listStyle: "disc" }}>
        <li>Job matches: 24 hours, then automatically pruned.</li>
        <li>Alert-delivery records: 24 hours, then automatically pruned.</li>
        <li>Login/security events: 90 days, then automatically pruned.</li>
        <li>Job listings: 30 days after last seen (7 days once a posting disappears).</li>
        <li>Account, preferences, subscriptions: until you delete your account.</li>
        <li>Rate-limit counters: 24 hours.</li>
      </ul>
      <H>5. Your rights</H>
      <P>
        You may at any time: <strong>access</strong> everything we store about you (Billing → export,
        or API <code>/api/auth/me/export</code>), <strong>correct</strong> your profile and
        preferences, and <strong>erase</strong> your account including matches and alert history
        (Billing → delete account, or API <code>DELETE /api/auth/me</code>). Erasure is immediate
        except anonymized security logs retained for fraud prevention. To exercise any right, or to
        withdraw consent, write to {LEGAL.email} — we respond within 30 days.
      </P>
      <H>6. Children</H>
      <P>JobQuest is not directed at children under 16. Accounts found to belong to children are removed.</P>
      <H>7. Security</H>
      <P>
        Passwords are stored as salted PBKDF2 hashes (600,000 iterations), never plaintext. Sessions
        use HttpOnly, SameSite cookies; failed logins trigger progressive lockout. No method is
        perfect — if you suspect unauthorized access, change your password and contact us
        immediately.
      </P>
      <H>8. Grievance redressal</H>
      <P>
        Grievance Officer: {LEGAL.grievanceName} — {LEGAL.grievanceEmail}. We acknowledge grievances
        within 24 hours and resolve them within 15 days, per applicable law.
      </P>
      <H>9. Changes</H>
      <P>
        Material changes to this policy will be announced in-app at least 7 days before taking
        effect. {LEGAL.address}.
      </P>
    </LegalShell>
  );
}
