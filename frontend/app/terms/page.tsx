import { LEGAL, LegalH, LegalList, LegalP, LegalShell } from "@/components/legal-shell";

export const metadata = {
  title: "JobQuest · Terms of Service",
  description: "Terms of Service for JobQuest job alerts.",
};

const SECTIONS = [
  { id: "service", title: "The service" },
  { id: "accounts", title: "Accounts and eligibility" },
  { id: "subscription", title: "Subscriptions and billing" },
  { id: "coupons", title: "Coupons and referrals" },
  { id: "acceptable-use", title: "Acceptable use" },
  { id: "listings", title: "Job listings" },
  { id: "ip", title: "Intellectual property" },
  { id: "availability", title: "Availability and changes" },
  { id: "liability", title: "Limitation of liability" },
  { id: "termination", title: "Termination" },
  { id: "law", title: "Governing law and grievance" },
  { id: "changes", title: "Changes to these terms" },
];

export default function TermsPage() {
  return (
    <LegalShell
      eyebrow="Legal"
      title="Terms of Service"
      intro="These Terms form a binding agreement between you and JobQuest. By creating an account or using the service, you agree to them — if you do not agree, do not use JobQuest."
      sections={SECTIONS}
    >
      <LegalH id="service" index={1}>The service</LegalH>
      <LegalP>
        {LEGAL.entity} (“we”, “us”, “our”) provides JobQuest, a job-discovery and alerting service
        that monitors public company career pages and sends you alerts for jobs matching your stated
        preferences. JobQuest is an <strong>aggregator</strong>: we surface publicly posted listings
        and link to the employer&apos;s own application page. Applications, hiring decisions, and
        employment relationships are solely between you and the employer.
      </LegalP>

      <LegalH id="accounts" index={2}>Accounts and eligibility</LegalH>
      <LegalP>
        You must be at least 16 years old to use JobQuest. You must provide a valid email address
        and keep your credentials confidential. One account per person. You are responsible for all
        activity under your account, including Telegram chat IDs you choose to link.
      </LegalP>

      <LegalH id="subscription" index={3}>Subscriptions and billing</LegalH>
      <LegalP>
        Paid plans are billed <strong>monthly in advance</strong> in INR, inclusive of GST, through
        our payment processor Razorpay. Prices are shown at{" "}
        <a href="/pricing" style={{ color: "var(--ink-text)" }}>
          /pricing
        </a>{" "}
        before you pay. Subscriptions renew automatically until cancelled. Cancelling stops the next
        renewal; you keep full access until the end of the paid period. See the{" "}
        <a href="/refund" style={{ color: "var(--ink-text)" }}>
          Refund &amp; Cancellation Policy
        </a>{" "}
        for details.
      </LegalP>

      <LegalH id="coupons" index={4}>Coupons and referrals</LegalH>
      <LegalP>
        Coupon codes grant time-limited free access as stated on the code. Codes have no cash value,
        cannot be transferred or combined, and we may revoke codes obtained by fraud or abuse. Your
        personal referral link is for genuine referrals only.
      </LegalP>

      <LegalH id="acceptable-use" index={5}>Acceptable use</LegalH>
      <LegalP>You agree not to:</LegalP>
      <LegalList>
        <li>Share your account, resell access, or scrape the service.</li>
        <li>Use the service for spam, harassment, or any unlawful purpose.</li>
        <li>Attempt to bypass access controls, rate limits, or security measures.</li>
        <li>Submit false information or impersonate another person.</li>
      </LegalList>
      <LegalP>
        We may suspend or terminate accounts that violate these Terms, abuse the alert system, or
        threaten the security of the service — typically with notice, immediately where required for
        security or legal reasons.
      </LegalP>

      <LegalH id="listings" index={6}>Job listings</LegalH>
      <LegalP>
        Listings are collected from public employer sources and are provided <strong>as-is</strong>.
        We do not guarantee that a listing is current, accurate, complete, or still open — always
        verify details on the employer&apos;s own page before applying. If a listing is stale or
        wrong, tell us at {LEGAL.email} and we will correct or remove it.
      </LegalP>

      <LegalH id="ip" index={7}>Intellectual property</LegalH>
      <LegalP>
        The JobQuest name, logo, interface, and software are our property. You receive a personal,
        non-transferable licence to use the service while your account is in good standing. Job
        listing content belongs to the respective employers.
      </LegalP>

      <LegalH id="availability" index={8}>Availability and changes</LegalH>
      <LegalP>
        We aim for continuous availability but do not guarantee uninterrupted service. We may modify,
        suspend, or discontinue features with reasonable notice; where a paid feature is removed
        permanently we will offer a pro-rata remedy or equivalent alternative.
      </LegalP>

      <LegalH id="liability" index={9}>Limitation of liability</LegalH>
      <LegalP>
        To the maximum extent permitted by law, JobQuest is provided without warranties of any kind.
        Our total liability for any claim arising from the service is limited to the amount you paid
        in the 12 months before the claim. We are not liable for employment outcomes, missed
        applications, or decisions made on the basis of alerts. Nothing here limits rights that
        consumer-protection law does not allow us to limit.
      </LegalP>

      <LegalH id="termination" index={10}>Termination</LegalH>
      <LegalP>
        You may delete your account at any time (Billing → delete account), which erases your
        profile, preferences, matches, and history per our{" "}
        <a href="/privacy" style={{ color: "var(--ink-text)" }}>
          Privacy Policy
        </a>
        . We may terminate for Terms violations as described above.
      </LegalP>

      <LegalH id="law" index={11}>Governing law and grievance</LegalH>
      <LegalP>
        These Terms are governed by the laws of India. Disputes will first be attempted to be
        resolved informally by contacting {LEGAL.email}. Grievance Officer: {LEGAL.grievanceName} —{" "}
        {LEGAL.grievanceEmail} (acknowledgement within 24 hours, resolution within 15 days).{" "}
        {LEGAL.address}.
      </LegalP>

      <LegalH id="changes" index={12}>Changes to these terms</LegalH>
      <LegalP>
        Material changes will be announced in-app at least 7 days before taking effect. Continued
        use after the effective date constitutes acceptance.
      </LegalP>
    </LegalShell>
  );
}
