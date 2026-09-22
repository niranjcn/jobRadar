import { LEGAL, LegalShell } from "@/components/legal-shell";

export const metadata = {
  title: "JobQuest · Refund & Cancellation Policy",
  description: "Refund and cancellation terms for JobQuest subscriptions.",
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

export default function RefundPage() {
  return (
    <LegalShell eyebrow="Legal" title="Refund & Cancellation Policy">
      <P>
        JobQuest subscriptions are billed <strong>monthly in advance</strong> through Razorpay
        (autopay where enabled). All prices are in INR and <strong>inclusive of GST</strong>.
      </P>
      <H>1. Cancel anytime</H>
      <P>
        Cancel in one click from Billing → Cancel Autopay (or write to {LEGAL.email} and we will do
        it for you). Cancellation stops the next renewal; there is no lock-in and no cancellation
        fee.
      </P>
      <H>2. Access until period end</H>
      <P>
        After cancellation you keep full access until the end of the paid billing period. Matches,
        history, and Telegram alerts continue normally during that window.
      </P>
      <H>3. Refunds</H>
      <P>
        Because access continues to period end and plans are monthly, billed amounts are{" "}
        <strong>non-refundable and not prorated</strong> — except where required by applicable
        consumer-protection law, duplicate charges, or a billing error on our side. If you were
        charged twice or charged after a confirmed cancellation, contact {LEGAL.email} within 30
        days with your payment ID and we will reverse it within 7 business days.
      </P>
      <H>4. Coupons</H>
      <P>
        Coupon codes grant free access for their stated duration and have no cash value. They cannot
        be refunded, transferred, or combined with a paid subscription for the same period.
      </P>
      <H>5. Chargebacks</H>
      <P>
        Please contact us before raising a dispute — most billing issues are resolved within 48
        hours, and an open chargeback suspends the account until the processor resolves it.
      </P>
      <H>6. Contact</H>
      <P>
        Billing questions: {LEGAL.email} · {LEGAL.address}.
      </P>
    </LegalShell>
  );
}
