import Link from "next/link";
import styles from "./privacy.module.css";

export type PrivacySection = {
  id: string;
  number: string;
  title: string;
  toc: string;
  body: React.ReactNode;
};

function P({ children, className }: { children: React.ReactNode; className?: string }) {
  return <p className={className}>{children}</p>;
}

function Ul({ children }: { children: React.ReactNode }) {
  return <ul>{children}</ul>;
}

export const PRIVACY_SECTIONS: PrivacySection[] = [
  {
    id: "scope",
    number: "01",
    title: "Scope",
    toc: "Scope",
    body: (
      <>
        <P>
          This Privacy Policy applies to the JobQuest website, the JobQuest application (dashboard,
          job search, preferences, billing), job alerts, the Telegram integration, and payment
          functionality.
        </P>
        <P>
          It does not apply to employer career pages or application pages you visit by clicking a
          job link, to Telegram&rsquo;s own service, or to Razorpay&rsquo;s checkout pages. Those
          services have their own privacy policies.
        </P>
      </>
    ),
  },
  {
    id: "collect",
    number: "02",
    title: "Information We Collect",
    toc: "Information We Collect",
    body: (
      <>
        <h3>2.1 Information you provide</h3>
        <Ul>
          <li>
            <strong>Email address</strong> — required to register and sign in. Stored lowercased and
            trimmed.
          </li>
          <li>
            <strong>Display name</strong> — 2–50 characters. If you skip it, it defaults to the part
            of your email before the @ sign.
          </li>
          <li>
            <strong>Password</strong> — your password itself is never stored. Only a one-way
            PBKDF2-HMAC-SHA256 hash of it is stored, so it cannot be recovered from our database.
          </li>
          <li>
            <strong>Telegram chat ID</strong> — only if you choose to link Telegram in settings. This
            is a numeric identifier for your chat, not your phone number.
          </li>
          <li>
            <strong>Job preferences</strong> — roles, keywords, locations, seniority, excluded
            companies, excluded roles, and alert settings (Telegram/email on or off, alert
            frequency, match scope, and whether the first check notifies you).
          </li>
          <li>
            <strong>Terms acceptance timestamp</strong> — the date and time you ticked the consent
            checkbox at registration. We do not currently record which policy version you accepted.
          </li>
        </Ul>
        <h3>2.2 Information collected automatically</h3>
        <Ul>
          <li>
            <strong>Security events</strong> — when you register, sign in (successfully or not), get
            locked out, change your password, sign out, or delete your account, we record the event
            type, your email address, IP address, browser user-agent string, and timestamp.
          </li>
          <li>
            <strong>Rate-limit records</strong> — to prevent abuse, we count recent registration,
            sign-in, password-change, and coupon attempts per IP address (and per email for
            sign-ins), with timestamps.
          </li>
          <li>
            <strong>Session cookie</strong> — signing in sets a single <code>jobquest_session</code>{" "}
            cookie (see §9). No advertising or tracking cookies are used.
          </li>
        </Ul>
        <P>
          We run no analytics, no error-tracking beacons, no pixels, and no fingerprinting scripts.
          Nothing on JobQuest reports your browsing behaviour to a third-party analytics provider.
        </P>
        <h3>2.3 Information generated through use</h3>
        <Ul>
          <li>
            <strong>Job matches</strong> — when a listing matches your preferences we store the
            match: which job, which preference terms matched, a 0–100 score, and when it matched.
          </li>
          <li>
            <strong>Alert-delivery records</strong> — which matched jobs were queued and sent to you,
            by which channel (Telegram), and when.
          </li>
          <li>
            <strong>Subscription records</strong> — your plan, status, billing provider, provider
            subscription reference, billing periods, and cancellation flag.
          </li>
          <li>
            <strong>Coupon records</strong> — coupon codes you redeem, the access granted, and when.
          </li>
          <li>
            <strong>Payment-provider records</strong> — raw event payloads received from Razorpay
            (see §6).
          </li>
          <li>
            <strong>Saved jobs and UI state</strong> — jobs you save, hide, or mark as applied, your
            theme choice, and search filters. These live only in your own browser
            (localStorage), not on our servers.
          </li>
        </Ul>
        <h3>2.4 Information received from third parties</h3>
        <P>
          We do not buy data or receive personal information about you from data brokers or other
          third parties. The only third-party information we receive about you is:
        </P>
        <Ul>
          <li>payment confirmations from Razorpay about your own transaction (see §6);</li>
          <li>messages you yourself send to the JobQuest Telegram bot.</li>
        </Ul>
        <P>JobQuest does not collect phone numbers, locations, resumes, or profile photos.</P>
      </>
    ),
  },
  {
    id: "use",
    number: "03",
    title: "How We Use Information",
    toc: "How We Use It",
    body: (
      <>
        <P>Each use below maps to functionality that actually exists in JobQuest:</P>
        <Ul>
          <li>
            <strong>Authentication</strong> — email and password hash verify your sign-ins; the
            session cookie keeps you signed in for 7 days.
          </li>
          <li>
            <strong>Job matching</strong> — your preferences are compared against job listings to
            produce your matches (see §4).
          </li>
          <li>
            <strong>Alerts</strong> — matches are queued and sent to your linked Telegram chat
            according to your alert settings.
          </li>
          <li>
            <strong>Subscriptions and billing</strong> — subscription records control which features
            are unlocked; provider references reconcile payments.
          </li>
          <li>
            <strong>Coupons</strong> — redemption records grant and track promotional access.
          </li>
          <li>
            <strong>Fraud and abuse prevention</strong> — failed-sign-in counts trigger temporary
            lockouts; rate limits block automated abuse of registration, sign-in, and coupons.
          </li>
          <li>
            <strong>Security and support</strong> — security-event logs help investigate
            unauthorized access and respond to your support requests.
          </li>
        </Ul>
        <P>
          Your information is not used for marketing. There are no marketing emails, no advertising
          profiles, and your preferences are never sold.
        </P>
      </>
    ),
  },
  {
    id: "matching",
    number: "04",
    title: "Job Matching and Automated Processing",
    toc: "Automated Matching",
    body: (
      <>
        <P>
          Matching is fully rule-based. JobQuest compares the words in a job&rsquo;s{" "}
          <strong>title</strong> against your roles, keywords, seniority, and locations, applies
          your excluded companies and roles, and computes a 0–100 score from how many preference
          categories matched. Job descriptions are not stored and do not influence matching.
        </P>
        <Ul>
          <li>No machine learning or AI model is involved.</li>
          <li>No external AI provider receives your information.</li>
          <li>No human reviews matches before they are shown or sent to you.</li>
        </Ul>
        <P>
          Matches are informational only: they do not guarantee employment outcomes, and a suitable
          job may be missed while an unsuitable one may be shown. Always verify details on the
          employer&rsquo;s own page.
        </P>
      </>
    ),
  },
  {
    id: "telegram",
    number: "05",
    title: "Telegram Integration",
    toc: "Telegram",
    body: (
      <>
        <P>
          Telegram is <strong>optional</strong>. Without a linked chat you can still use the
          dashboard, job search, preferences, and billing; only Telegram alerts are unavailable.
        </P>
        <P>When you link Telegram in settings:</P>
        <Ul>
          <li>we store only your numeric chat ID — not your username, name, photo, or phone number;</li>
          <li>
            each alert sent to you contains the job title, company, location, match score, and
            application link — nothing else about your account;
          </li>
          <li>
            if you use the bot&rsquo;s <code>/preferences</code> command, the bot replies in your
            own chat with a summary of your stored preferences;
          </li>
          <li>
            the bot reads updates via polling. It does not use a webhook and stores no message
            history beyond the delivery records in §2.3.
          </li>
        </Ul>
        <P>
          You can unlink Telegram at any time in settings (your stored chat ID is erased), or delete
          your account to erase it along with your queued and sent alerts (see §11). Telegram
          processes messages you exchange with the bot under{" "}
          <a href="https://telegram.org/privacy" target="_blank" rel="noreferrer">
            Telegram&rsquo;s own privacy policy
          </a>
          .
        </P>
      </>
    ),
  },
  {
    id: "payments",
    number: "06",
    title: "Payments and Razorpay",
    toc: "Payments",
    body: (
      <>
        <P>
          Payments are processed by <strong>Razorpay</strong>. Card, bank, and UPI details are
          entered in Razorpay&rsquo;s own checkout window and <strong>never touch JobQuest servers</strong>
          — our backend only receives payment, order, or subscription reference IDs plus a
          cryptographic signature it verifies.
        </P>
        <P>What each party holds:</P>
        <Ul>
          <li>
            <strong>JobQuest stores:</strong> your plan, subscription status, billing periods,
            Razorpay subscription/customer reference IDs, and raw Razorpay event payloads (kept as
            billing records).
          </li>
          <li>
            <strong>Razorpay processes:</strong> your payment credentials, the charge itself, and any
            receipts or invoices it issues, under{" "}
            <a href="https://razorpay.com/privacy/" target="_blank" rel="noreferrer">
              Razorpay&rsquo;s privacy policy
            </a>
            .
          </li>
          <li>
            <strong>Referenced only:</strong> amounts and currency shown at checkout; JobQuest does
            not maintain a separate invoice ledger.
          </li>
        </Ul>
        <P>
          Raw Razorpay event payloads are kept as billing records even after account deletion (see
          §11).
        </P>
      </>
    ),
  },
  {
    id: "sharing",
    number: "07",
    title: "Sharing and Third-Party Services",
    toc: "Sharing",
    body: (
      <>
        <P>JobQuest does not sell personal information. Information reaches third parties only as below:</P>
        <table>
          <thead>
            <tr>
              <th>Provider</th>
              <th>Purpose</th>
              <th>Information shared</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Razorpay</td>
              <td>Payment processing</td>
              <td>Name and email for the checkout prefill; payment credentials you enter directly with Razorpay</td>
            </tr>
            <tr>
              <td>Telegram</td>
              <td>Alert delivery</td>
              <td>Your chat ID; job title, company, location, score, and link per alert</td>
            </tr>
            <tr>
              <td>Hosting / database</td>
              <td>Running the service</td>
              <td>All stored data above, on the operator&rsquo;s server (PostgreSQL database operated alongside the application)</td>
            </tr>
            <tr>
              <td>Resend (email)</td>
              <td>Currently dormant</td>
              <td>No automated email is sent today; only a manual test script can send sample mail</td>
            </tr>
          </tbody>
        </table>
        <P>
          Employer career pages receive no personal information from us — JobQuest only reads their
          public listings (see §8).
        </P>
      </>
    ),
  },
  {
    id: "listings",
    number: "08",
    title: "Job Listings and Employer Websites",
    toc: "Job Listings",
    body: (
      <>
        <P>
          Job listings are collected from public employer career pages and contain only public
          information: title, company, location, application URL, and derived country/remote flags.
          Job descriptions are not stored. Listings contain no JobQuest user information.
        </P>
        <P>
          Viewing a listing sends nothing about you to the employer. Clicking an application link
          takes you to the employer&rsquo;s own website, which has its own privacy policy.
        </P>
      </>
    ),
  },
  {
    id: "cookies",
    number: "09",
    title: "Cookies and Similar Technologies",
    toc: "Cookies",
    body: (
      <>
        <h3>9.1 Essential authentication cookie</h3>
        <P>
          Signing in sets one cookie, <code>jobquest_session</code> (or{" "}
          <code>__Host-jobquest_session</code> when secure mode is enabled). It holds a signed,
          tamper-evident session token that expires after 7 days, is inaccessible to JavaScript
          (HttpOnly), and is sent only to JobQuest (SameSite=Lax; Secure flag when HTTPS is
          enforced). Signing out deletes it. There is no server-side session list to revoke — a
          copied cookie remains valid until it expires, so keep your device secure.
        </P>
        <h3>9.2 Browser-only storage</h3>
        <P>
          Your browser&rsquo;s localStorage holds saved/hidden/applied job IDs, theme choice,
          search filters, and notification read-times. These never leave your device and are not
          part of export or deletion (clearing browser data removes them).
        </P>
        <h3>9.3 What we do not use</h3>
        <P>
          No analytics cookies, no advertising cookies, no cross-site trackers. The only
          third-party code that runs in your browser is Razorpay&rsquo;s checkout window during
          payment.
        </P>
      </>
    ),
  },
  {
    id: "retention",
    number: "10",
    title: "Data Retention",
    toc: "Retention",
    body: (
      <>
        <P>Only the periods below are automated. Everything else is kept until you delete your account:</P>
        <table>
          <thead>
            <tr>
              <th>Data</th>
              <th>Retention</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Job matches</td>
              <td>24 hours, then automatically deleted</td>
            </tr>
            <tr>
              <td>Sent-alert records</td>
              <td>24 hours, then automatically deleted (queued alerts are kept until sent, failed, or cancelled)</td>
            </tr>
            <tr>
              <td>Security-event logs</td>
              <td>90 days, then automatically deleted</td>
            </tr>
            <tr>
              <td>Rate-limit counters</td>
              <td>24 hours, then automatically deleted</td>
            </tr>
            <tr>
              <td>Job listings</td>
              <td>Listings unseen for 30 days are deleted; postings that disappear are deleted 7 days after last seen</td>
            </tr>
            <tr>
              <td>Account, preferences, subscriptions, coupon redemptions</td>
              <td>Until you delete your account</td>
            </tr>
            <tr>
              <td>Razorpay billing-event records</td>
              <td>Retained as billing records (no automatic deletion)</td>
            </tr>
          </tbody>
        </table>
      </>
    ),
  },
  {
    id: "deletion",
    number: "11",
    title: "Account Deletion",
    toc: "Account Deletion",
    body: (
      <>
        <P>
          You can delete your account at any time via <code>DELETE /api/auth/me</code> (password
          confirmation required). There is currently no delete button in the interface — deletion
          is performed through that API endpoint.
        </P>
        <P>Deletion is immediate in the live database. It permanently erases:</P>
        <Ul>
          <li>your profile, email, password hash, and linked Telegram chat ID;</li>
          <li>your preferences, subscriptions, job matches, and queued and sent alerts;</li>
          <li>your authorship of shared preference presets (reassigned to the system owner).</li>
        </Ul>
        <P>What remains, and why:</P>
        <Ul>
          <li>
            <strong>Billing-event records</strong> — kept as the payment ledger (they carry no
            JobQuest account link).
          </li>
          <li>
            <strong>Coupon ledger rows</strong> — kept with your identity detached.
          </li>
          <li>
            <strong>Security-event logs</strong> — your rows are detached from your account but keep
            their email address, IP, and browser details until the 90-day deletion.
          </li>
        </Ul>
        <P>
          The application keeps no off-site backups today, so there is no backup copy that
          outlives the live database. Public job listings are unaffected by account deletion.
        </P>
      </>
    ),
  },
  {
    id: "rights",
    number: "12",
    title: "Your Privacy Rights and Choices",
    toc: "Your Rights",
    body: (
      <>
        <P>These are the rights the product actually supports today:</P>
        <Ul>
          <li>
            <strong>Access</strong> — <code>GET /api/auth/me/export</code> returns your profile
            (never the password hash), preferences, subscriptions, matches, sent alerts, redeemed
            coupons, and your last 200 security events. Pending queued alerts, raw billing payloads,
            and rate-limit counters are not included.
          </li>
          <li>
            <strong>Correction</strong> — update your display name and email in settings; update
            preferences any time; link or unlink Telegram in settings.
          </li>
          <li>
            <strong>Deletion</strong> — <code>DELETE /api/auth/me</code>, as described in §11.
          </li>
          <li>
            <strong>Consent withdrawal</strong> — registration requires ticking the Terms consent
            checkbox; withdrawing consent means deleting your account, since the service cannot
            operate without your email and preferences.
          </li>
        </Ul>
        <P>
          Role, account status, and alert-delay settings are administrator-managed and cannot be
          edited by you. To make a request you cannot perform yourself, contact{" "}
          <strong>[PRIVACY CONTACT EMAIL]</strong>.
        </P>
      </>
    ),
  },
  {
    id: "children",
    number: "13",
    title: "Children's Privacy",
    toc: "Children",
    body: (
      <>
        <P>
          Registration does not currently verify age, and the Terms of Service require users to be
          at least 18 years old and legally able to enter the agreement. If an account is found to
          belong to someone ineligible, it may be disabled or removed by the operator.
        </P>
      </>
    ),
  },
  {
    id: "security",
    number: "14",
    title: "Security",
    toc: "Security",
    body: (
      <>
        <P>Reasonable technical measures in place today:</P>
        <Ul>
          <li>Passwords hashed with PBKDF2-HMAC-SHA256 at 600,000 iterations with unique salts.</li>
          <li>12–128 character passwords requiring 3 of 4 character categories; common passwords and email/name reuse rejected.</li>
          <li>5 failed sign-ins lock an account for a fixed 15 minutes.</li>
          <li>Rate limits on registration, sign-in, password change, and coupon redemption.</li>
          <li>HttpOnly, SameSite=Lax session cookie with 7-day expiry (Secure flag where HTTPS is enforced).</li>
          <li>Role-based access (user / privileged / admin) with server-side checks.</li>
          <li>Security headers including a content-security policy that allowlists only JobQuest itself and Razorpay checkout.</li>
        </Ul>
        <P>
          Limits you should know: there is no two-factor authentication; signing out deletes the
          cookie but does not revoke the token server-side before its 7-day expiry; CSRF protection
          relies on SameSite cookies rather than per-request tokens; and there is currently no
          self-service password-reset email — if you lose access to your account, contact support
          to verify your identity.
        </P>
        <P>
          No method is perfect. If you suspect unauthorized access, change your password
          immediately and report it as described in §15.
        </P>
      </>
    ),
  },
  {
    id: "breach",
    number: "15",
    title: "Data Breach and Security Incidents",
    toc: "Security Incidents",
    body: (
      <>
        <P>
          JobQuest has no automated breach-notification workflow today. If you suspect unauthorized
          access to your account, report it to <strong>[SECURITY CONTACT EMAIL]</strong> with your
          account email and what you observed. Suspected vulnerabilities in the service itself may
          be reported to the same contact — please do not exploit or publicly disclose a
          vulnerability before the operator has had a reasonable opportunity to address it.
        </P>
      </>
    ),
  },
  {
    id: "international",
    number: "16",
    title: "International Users and Transfers",
    toc: "International Users",
    body: (
      <>
        <P>
          The website is publicly accessible, which alone does not grant any particular legal
          regime&rsquo;s rights. Where Telegram, Razorpay, or (if ever enabled) Resend email are
          used, your information may be processed outside India under those providers&rsquo; own
          terms. The rights described in §12 are provided by the product itself to all users.
        </P>
      </>
    ),
  },
  {
    id: "changes",
    number: "17",
    title: "Changes to This Privacy Policy",
    toc: "Changes",
    body: (
      <>
        <P>
          Material changes will be posted on this page with a new &ldquo;Last updated&rdquo; date.
          There is currently no in-app announcement system, so please review this page
          periodically. Continued use after changes take effect constitutes acceptance.
        </P>
      </>
    ),
  },
  {
    id: "contact",
    number: "18",
    title: "Contact and Grievance Redressal",
    toc: "Contact",
    body: (
      <>
        <P>
          JobQuest is an independently operated software service run by its individual developer —
          there is currently no registered company, and no Grievance Officer has been appointed.
        </P>
        <P className={styles.placeholderNote}>
          The following contacts must be completed before accepting real users or payments:
        </P>
        <Ul>
          <li>
            <strong>Privacy contact:</strong> [PRIVACY CONTACT EMAIL]
          </li>
          <li>
            <strong>Security contact:</strong> [SECURITY CONTACT EMAIL]
          </li>
          <li>
            <strong>Grievance contact / officer (if applicable):</strong> [GRIEVANCE CONTACT]
          </li>
          <li>
            <strong>Business address (if applicable):</strong> [BUSINESS ADDRESS]
          </li>
        </Ul>
      </>
    ),
  },
];
