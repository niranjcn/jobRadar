import { LEGAL, LegalH, LegalP, LegalShell } from "@/components/legal-shell";

export const metadata = {
  title: "JobQuest · Refund & Cancellation Policy",
  description: "Refund and cancellation terms for JobQuest subscriptions.",
};

const SECTIONS = [
  { id: "cancel", title: "Cancel anytime" },
  { id: "access", title: "Access until period end" },
  { id: "refunds", title: "Refunds" },
  { id: "coupons", title: "Coupons" },
  { id: "chargebacks", title: "Chargebacks" },
  { id: "contact", title: "Contact" },
];

export default function RefundPage() {
  return (
    <LegalShell
      eyebrow="Legal"
      title="Refund & Cancellation Policy"
      intro="JobQuest subscriptions are billed monthly in advance through Razorpay (autopay where enabled). All prices are in INR and inclusive of GST."
      sections={SECTIONS}
    >
      <LegalH id="cancel" index={1}>Cancel anytime</LegalH>
      <LegalP>
        Cancel in one click from Billing → Cancel Autopay (or write to {LEGAL.email} and we will do
        it for you). Cancellation stops the next renewal; there is no lock-in and no cancellation
        fee.
      </LegalP>

      <LegalH id="access" index={2}>Access until period end</LegalH>
      <LegalP>
        After cancellation you keep full access until the end of the paid billing period. Matches,
        history, and Telegram alerts continue normally during that window.
      </LegalP>

      <LegalH id="refunds" index={3}>Refunds</LegalH>
      <LegalP>
        Because access continues to period end and plans are monthly, billed amounts are{" "}
        <strong>non-refundable and not prorated</strong> — except where required by applicable
        consumer-protection law, duplicate charges, or a billing error on our side. If you were
        charged twice or charged after a confirmed cancellation, contact {LEGAL.email} within 30
        days with your payment ID and we will reverse it within 7 business days.
      </LegalP>

      <LegalH id="coupons" index={4}>Coupons</LegalH>
      <LegalP>
        Coupon codes grant free access for their stated duration and have no cash value. They cannot
        be refunded, transferred, or combined with a paid subscription for the same period.
      </LegalP>

      <LegalH id="chargebacks" index={5}>Chargebacks</LegalH>
      <LegalP>
        Please contact us before raising a dispute — most billing issues are resolved within 48
        hours, and an open chargeback suspends the account until the processor resolves it.
      </LegalP>

      <LegalH id="contact" index={6}>Contact</LegalH>
      <LegalP>
        Billing questions: {LEGAL.email} · {LEGAL.address}.
      </LegalP>
    </LegalShell>
  );
}
