import Link from "next/link";

export type RefundSection = {
  id: string;
  number: string;
  title: string;
  toc: string;
  body: React.ReactNode;
};

function P({ children }: { children: React.ReactNode }) {
  return <p>{children}</p>;
}

function Ul({ children }: { children: React.ReactNode }) {
  return <ul>{children}</ul>;
}

export const REFUND_SECTIONS: RefundSection[] = [
  {
    id: "billing",
    number: "01",
    title: "Subscriptions and Billing",
    toc: "Billing",
    body: (
      <>
        <P>
          JobQuest offers a <strong>Standard</strong> plan billed <strong>monthly in advance</strong>{" "}
          in <strong>INR</strong>. The current price is shown on the{" "}
          <Link href="/pricing">Pricing</Link> page and at checkout — the amount you authorize is
          the amount shown there.
        </P>
        <P>
          Payments are processed by <strong>Razorpay</strong>. The usual path is a true recurring
          Razorpay subscription (monthly, up to 12 renewals, with payment notifications enabled).
          If recurring setup is unavailable, checkout falls back to a one-time Razorpay order for
          the same 30-day access. The checkout window tells you which of the two you are paying
          with.
        </P>
        <P>
          Tax treatment is still being finalized: there is currently no GSTIN, no tax breakdown,
          and no invoice document issued by JobQuest. The amount charged is exactly the amount
          displayed before you pay.
        </P>
      </>
    ),
  },
  {
    id: "subscription",
    number: "02",
    title: "Starting a Subscription",
    toc: "Subscription",
    body: (
      <>
        <P>When you subscribe:</P>
        <Ul>
          <li>you pick the plan in Billing and complete payment in Razorpay&rsquo;s checkout;</li>
          <li>
            JobQuest verifies Razorpay&rsquo;s cryptographic signature on the payment, then
            activates <strong>30 days</strong> of access immediately;
          </li>
          <li>
            if verification succeeds but activation is delayed (for example a slow webhook),
            activation completes when Razorpay confirms the charge — you are never charged twice
            for the wait;
          </li>
          <li>
            if the payment itself fails, nothing is activated and nothing is owed — simply try
            again from Billing.
          </li>
        </Ul>
      </>
    ),
  },
  {
    id: "cancellation",
    number: "03",
    title: "Cancellation",
    toc: "Cancellation",
    body: (
      <>
        <P>
          You can cancel yourself in <strong>Billing → &ldquo;Cancel Autopay (keep until period
          end)&rdquo;</strong>. There is no cancellation fee and no lock-in.
        </P>
        <P>
          <strong>Important limitation you must know:</strong> this button currently records the
          cancellation in JobQuest only — it does <strong>not</strong> cancel the recurring
          mandate at Razorpay. To stop future Razorpay charges, also cancel the autopay mandate in
          Razorpay (or your bank&rsquo;s autopay/UPI-autopay section), or contact{" "}
          <strong>[BILLING CONTACT EMAIL]</strong> and we will guide you. A renewal charge that
          reaches us will re-activate access automatically.
        </P>
        <P>
          There is no separate &ldquo;undo cancel&rdquo; action: paying again (or redeeming a
          coupon) starts fresh access and supersedes the cancelled record.
        </P>
      </>
    ),
  },
  {
    id: "access",
    number: "04",
    title: "Access After Cancellation",
    toc: "Access",
    body: (
      <>
        <P>
          Cancellation never cuts access immediately. Until the end of your already-paid 30-day
          period you keep everything: dashboard, New Jobs, Matches, preferences, history, billing,
          and Telegram alerts.
        </P>
        <P>
          After the period ends without renewal, your account is re-locked: Matches, notifications,
          and saved presets show the paywall, and Telegram alerts stop (queued alerts resume if you
          renew). Dashboard, job browsing, preferences, and billing stay available. Billing will
          offer <strong>&ldquo;Renew with Razorpay Autopay&rdquo;</strong> to restore full access.
        </P>
      </>
    ),
  },
  {
    id: "refunds",
    number: "05",
    title: "Refunds",
    toc: "Refunds",
    body: (
      <>
        <P>
          Subscription charges are <strong>non-refundable</strong>, and we do not give partial-period
          refunds when you cancel mid-period — your access already continues to the end of the paid
          period instead. This is the intended business rule; its enforceability should be confirmed
          with legal counsel before it is relied upon.
        </P>
        <P>Exceptions we will handle manually (see §6):</P>
        <Ul>
          <li>a duplicate charge caused by our error;</li>
          <li>a charge taken after a cancellation that was confirmed on both sides;</li>
          <li>a payment that succeeded but never activated any access and cannot be activated.</li>
        </Ul>
      </>
    ),
  },
  {
    id: "refund-request",
    number: "06",
    title: "Refund Requests",
    toc: "Refund Request",
    body: (
      <>
        <P>
          There is no automated refund button and no fixed processing timeline. To request a
          manual review, write to <strong>[BILLING CONTACT EMAIL]</strong> with:
        </P>
        <Ul>
          <li>your account email;</li>
          <li>the Razorpay payment ID (and subscription ID for renewals);</li>
          <li>the date and amount of the charge;</li>
          <li>what happened, in your own words.</li>
        </Ul>
        <P>
          Each request is reviewed individually. If a refund is agreed, it is issued through
          Razorpay to the original payment method, and processing time then depends on Razorpay
          and your bank.
        </P>
      </>
    ),
  },
  {
    id: "billing-errors",
    number: "07",
    title: "Duplicate Charges and Billing Errors",
    toc: "Billing Errors",
    body: (
      <>
        <P>If something looks wrong, contact us as described in §6. How each case behaves today:</P>
        <Ul>
          <li>
            <strong>Charged twice:</strong> the system does not merge payments — the second payment
            starts its own fresh 30-day period. Tell us and we will review the overlap.
          </li>
          <li>
            <strong>Charged after cancellation:</strong> see §3 — confirm the Razorpay mandate was
            also cancelled; renewals that reach us re-activate access automatically.
          </li>
          <li>
            <strong>Wrong amount:</strong> the checkout amount always governs; send the payment ID
            so we can compare it against the plan price.
          </li>
          <li>
            <strong>Paid but not activated:</strong> retry from Billing, or wait for Razorpay&rsquo;s
            confirmation to arrive — delayed confirmations activate automatically.
          </li>
        </Ul>
      </>
    ),
  },
  {
    id: "failed-payments",
    number: "08",
    title: "Failed Payments",
    toc: "Failed Payments",
    body: (
      <>
        <P>
          A failed initial payment activates nothing and locks nothing beyond your current state —
          just retry. A failed renewal simply means no new period starts: your existing access runs
          to its period end and then the account re-locks as described in §4. JobQuest does not
          retry charges itself, offers no grace period beyond the paid period, and sends no
          payment-failure notices today — watch your renewal date in Billing.
        </P>
      </>
    ),
  },
  {
    id: "chargebacks",
    number: "09",
    title: "Chargebacks and Payment Disputes",
    toc: "Chargebacks",
    body: (
      <>
        <P>
          If a charge looks wrong, please contact us first — most billing issues are a duplicate or
          a mandate that was never cancelled, and both are faster to fix directly than through a
          dispute. Nothing in this policy discourages a legitimate dispute, and no automation
          suspends your account over one; disputes are processed through Razorpay&rsquo;s dispute
          flow.
        </P>
      </>
    ),
  },
  {
    id: "coupons",
    number: "10",
    title: "Coupons and Promotional Access",
    toc: "Coupons",
    body: (
      <>
        <P>Coupon codes grant free access for their stated duration subject to their conditions:</P>
        <Ul>
          <li>single use, non-transferable, no cash value;</li>
          <li>
            redeeming a coupon while a paid subscription is active <strong>replaces</strong> it —
            the two cannot be combined or stacked for the same period;
          </li>
          <li>coupons themselves are never refunded;</li>
          <li>
            when coupon access ends without renewal, the account re-locks exactly as in §4.
          </li>
        </Ul>
      </>
    ),
  },
  {
    id: "taxes",
    number: "11",
    title: "Taxes",
    toc: "Taxes",
    body: (
      <>
        <P>
          JobQuest currently issues no tax invoices and displays no GST breakdown — the checkout
          amount is the final amount. Tax treatment (including whether GST applies and whether a
          GSTIN will be registered) is still being finalized with the operator&rsquo;s accountant
          and will be stated here once confirmed.
        </P>
      </>
    ),
  },
  {
    id: "payment-processor",
    number: "12",
    title: "Third-Party Payment Processor",
    toc: "Processor",
    body: (
      <>
        <P>
          Card, bank, and UPI credentials are entered in Razorpay&rsquo;s checkout and never touch
          JobQuest servers. JobQuest keeps only billing references (plan, status, periods, provider
          subscription/customer IDs, and raw provider event records); Razorpay handles the money
          under{" "}
          <a href="https://razorpay.com/privacy/" target="_blank" rel="noreferrer">
            Razorpay&rsquo;s privacy policy
          </a>
          .
        </P>
      </>
    ),
  },
  {
    id: "account-deletion",
    number: "13",
    title: "Account Deletion",
    toc: "Account Deletion",
    body: (
      <>
        <P>
          Deleting your account erases your local subscription record immediately — but it does{" "}
          <strong>not</strong> cancel a live Razorpay autopay mandate. <strong>Cancel autopay first
          (Billing, plus Razorpay/bank as in §3)</strong>, otherwise renewals can keep charging
          after your account is gone. Deletion ends remaining paid time without refund, consistent
          with §5.
        </P>
      </>
    ),
  },
  {
    id: "contact",
    number: "14",
    title: "Contact",
    toc: "Contact",
    body: (
      <>
        <P>
          Billing questions and refund requests: <strong>[BILLING CONTACT EMAIL]</strong>. Include
          your account email and Razorpay payment ID so the charge can be traced. General help:{" "}
          <Link href="/contact">Contact page</Link>.
        </P>
      </>
    ),
  },
  {
    id: "changes",
    number: "15",
    title: "Policy Changes",
    toc: "Changes",
    body: (
      <>
        <P>
          Material changes will be posted on this page with a new &ldquo;Last updated&rdquo; date.
          Continued use after changes take effect constitutes acceptance.
        </P>
      </>
    ),
  },
];
