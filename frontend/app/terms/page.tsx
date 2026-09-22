import { LEGAL, LegalShell } from "@/components/legal-shell";

export const metadata = {
  title: "JobQuest · Terms of Service",
  description: "Terms of Service for JobQuest job alerts.",
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

export default function TermsPage() {
  return (
    <LegalShell eyebrow="Legal" title="Terms of Service">
      <P>
        These Terms of Service (“Terms”) govern your use of JobQuest, a job-aggregation and alert
        service operated by {LEGAL.entity} (“we”, “us”). By creating an account you agree to these
        Terms and to our Privacy Policy.
      </P>
      <H>1. What JobQuest is</H>
      <P>
        JobQuest monitors public company career pages, normalizes the listings it finds, matches
        them against preferences you configure, and sends you alerts over Telegram. JobQuest is an
        aggregation and notification tool. It is <strong>not</strong> a recruiter, employer, or
        placement agency, and use of the service is <strong>not a guarantee</strong> of interviews,
        referrals, or employment.
      </P>
      <H>2. Accounts</H>
      <P>
        You must provide a valid email address and a password meeting our published strength rules.
        You are responsible for activity under your account. We may lock accounts after repeated
        failed logins, and suspend accounts used for abuse, scraping, or resale of access.
      </P>
      <H>3. Subscription and billing</H>
      <P>
        Paid access is billed monthly in advance through Razorpay (autopay where enabled). The
        current plan price is shown on the Pricing page before you pay; the amount actually charged
        is the plan price at checkout. Subscriptions renew automatically each month until cancelled.
      </P>
      <P>
        You can cancel at any time with one click from Billing (or by contacting us). Cancellation
        stops the next renewal; your access continues until the end of the paid period. See the
        Refund Policy for refund terms.
      </P>
      <H>4. Coupons</H>
      <P>
        Admin-issued coupon codes grant free access for their stated duration (1–12 months).
        Codes are single-use, expire 12 hours after issue, and cannot be transferred or redeemed
        for cash. Abusive redemption patterns may be throttled or voided.
      </P>
      <H>5. Acceptable use</H>
      <P>
        You agree not to: share your account, scrape or bulk-export other users&apos; data, attack
        or degrade the service, attempt to access other accounts, or use alerts for spam. We may
        rate-limit, suspend, or terminate accounts that do.
      </P>
      <H>6. Alerts are best-effort</H>
      <P>
        Alerts depend on third-party career pages, Telegram delivery, and polling schedules outside
        our control. We aim for timely delivery but do not warrant that every matching job will
        produce an alert, or that listings are accurate, current, or still open. Always verify
        details on the employer&apos;s own posting before applying.
      </P>
      <H>7. Job content</H>
      <P>
        Job titles, descriptions, and links belong to their respective employers. JobQuest displays
        short excerpts and links for discovery. If you are an employer and believe a listing should
        be removed or corrected, contact us and we will act promptly.
      </P>
      <H>8. Termination and deletion</H>
      <P>
        You may delete your account at any time (Billing → account deletion, or contact us);
        deletion removes your profile, preferences, matches, and alert history as described in the
        Privacy Policy. We may suspend or terminate accounts that violate these Terms.
      </P>
      <H>9. Liability</H>
      <P>
        To the maximum extent permitted by law, JobQuest is provided “as is” without warranties of
        any kind, and {LEGAL.entity} is not liable for indirect, incidental, or consequential
        damages, including missed job opportunities. Total liability is limited to the fees you paid
        in the 3 months before the claim.
      </P>
      <H>10. Changes and contact</H>
      <P>
        We may update these Terms; material changes will be announced in-app at least 7 days before
        they take effect. Continued use after that date constitutes acceptance. Questions:{" "}
        {LEGAL.email} · {LEGAL.address}.
      </P>
    </LegalShell>
  );
}
