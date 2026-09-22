import Link from "next/link";
import { LEGAL } from "./legal";

export type TermsSection = {
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

function Ol({ children }: { children: React.ReactNode }) {
  return <ol>{children}</ol>;
}

export const TERMS_SECTIONS: TermsSection[] = [
  {
    id: "definitions",
    number: "01",
    title: "Definitions",
    toc: "Definitions",
    body: (
      <>
        <P>For purposes of these Terms:</P>
        <h3>1.1 &ldquo;Account&rdquo;</h3>
        <P>Means the registered JobQuest account created by a User to access the Service.</P>
        <h3>1.2 &ldquo;Job Listing&rdquo;</h3>
        <P>
          Means information about an employment opportunity displayed, indexed, summarized, or linked
          through JobQuest.
        </P>
        <h3>1.3 &ldquo;Employer&rdquo;</h3>
        <P>
          Means the company, organization, recruiter, or other party responsible for an original Job
          Listing.
        </P>
        <h3>1.4 &ldquo;Subscription&rdquo;</h3>
        <P>
          Means a paid plan that provides access to specified JobQuest features for a defined billing
          period.
        </P>
        <h3>1.5 &ldquo;Free Features&rdquo;</h3>
        <P>
          Means features made available without requiring payment, subject to availability and these
          Terms.
        </P>
        <h3>1.6 &ldquo;Coupon&rdquo;</h3>
        <P>
          Means a promotional code or offer that provides specified benefits subject to its applicable
          conditions.
        </P>
        <h3>1.7 &ldquo;User Content&rdquo;</h3>
        <P>
          Means information, preferences, feedback, profile information, or other content submitted by
          you through the Service.
        </P>
      </>
    ),
  },
  {
    id: "about",
    number: "02",
    title: "About JobQuest",
    toc: "About JobQuest",
    body: (
      <>
        <P>
          JobQuest is a job-discovery and job-alert platform designed to help users discover publicly
          available employment opportunities.
        </P>
        <P>JobQuest may:</P>
        <Ul>
          <li>monitor publicly accessible employer career pages and other permitted sources;</li>
          <li>collect and normalize publicly available job information;</li>
          <li>identify and organize job listings;</li>
          <li>filter listings according to user preferences;</li>
          <li>provide automated or algorithmic job matching;</li>
          <li>send job alerts and notifications;</li>
          <li>provide links to employer application pages;</li>
          <li>provide optional Telegram notifications;</li>
          <li>provide dashboards and tools for managing job searches and preferences.</li>
        </Ul>
        <P>
          JobQuest is an <strong>aggregator and discovery service</strong>.
        </P>
        <P>Unless explicitly stated otherwise, JobQuest is not:</P>
        <Ul>
          <li>an employer;</li>
          <li>an employment agency;</li>
          <li>a recruitment agency;</li>
          <li>an agent of an employer;</li>
          <li>a party to any employment relationship between you and an Employer.</li>
        </Ul>
        <P>
          Applications, interviews, hiring decisions, employment contracts, compensation, benefits,
          and employment relationships are solely between you and the applicable Employer.
        </P>
      </>
    ),
  },
  {
    id: "eligibility",
    number: "03",
    title: "Eligibility",
    toc: "Eligibility",
    body: (
      <>
        <P>
          You must meet the minimum age and legal eligibility requirements applicable to your use of
          the Service.
        </P>
        <P>
          <strong>Default JobQuest policy: Users must be at least 18 years old.</strong>
        </P>
        <P>
          If JobQuest later permits users under 18, the eligibility, consent, and data-processing
          provisions must be separately reviewed and implemented before enabling such accounts.
        </P>
        <P>You must also have the legal capacity to enter into these Terms.</P>
        <P>You may not use the Service if applicable law prohibits you from doing so.</P>
      </>
    ),
  },
  {
    id: "account-creation",
    number: "04",
    title: "Creating an Account",
    toc: "Accounts",
    body: (
      <>
        <P>Some features require an Account.</P>
        <P>When creating an Account, you agree to:</P>
        <Ul>
          <li>provide accurate and current information;</li>
          <li>provide a valid email address;</li>
          <li>keep your Account information updated;</li>
          <li>maintain the confidentiality of your credentials;</li>
          <li>use only your own Account;</li>
          <li>notify us if you believe your Account has been compromised;</li>
          <li>remain responsible for activity performed through your Account.</li>
        </Ul>
        <P>You must not:</P>
        <Ul>
          <li>create an Account using another person&rsquo;s identity;</li>
          <li>impersonate another person or organization;</li>
          <li>create Accounts for fraudulent purposes;</li>
          <li>create multiple Accounts to circumvent limits or promotions;</li>
          <li>share your Account credentials with another person;</li>
          <li>sell, transfer, or resell your Account.</li>
        </Ul>
        <P>
          We may require verification of information where reasonably necessary to protect the Service
          or its users.
        </P>
      </>
    ),
  },
  {
    id: "account-security",
    number: "05",
    title: "Account Security",
    toc: "Account Security",
    body: (
      <>
        <P>You are responsible for maintaining reasonable security of your Account credentials.</P>
        <P>
          JobQuest will implement reasonable technical and organizational measures appropriate to the
          Service, but no internet-based system can be guaranteed to be completely secure.
        </P>
        <P>
          If you suspect unauthorized access, immediately contact:{" "}
          <strong>{LEGAL.securityEmail}</strong>
        </P>
        <P>
          We may temporarily restrict access to an Account where reasonably necessary to protect the
          Account, Service, or other users.
        </P>
      </>
    ),
  },
  {
    id: "service",
    number: "06",
    title: "The JobQuest Service",
    toc: "Service",
    body: (
      <>
        <P>
          JobQuest may provide different features depending on your Account, subscription,
          promotional eligibility, or other applicable conditions.
        </P>
        <P>Features may include:</P>
        <Ul>
          <li>Dashboard;</li>
          <li>New Jobs;</li>
          <li>Preferences;</li>
          <li>job matching;</li>
          <li>job alerts;</li>
          <li>saved jobs;</li>
          <li>application tracking;</li>
          <li>billing management;</li>
          <li>Telegram notifications;</li>
          <li>other features introduced from time to time.</li>
        </Ul>
        <P>We may add, modify, replace, suspend, or remove features subject to these Terms and applicable law.</P>
      </>
    ),
  },
  {
    id: "matching",
    number: "07",
    title: "Automated Matching and Recommendations",
    toc: "Automated Matching",
    body: (
      <>
        <P>
          JobQuest may use automated rules, algorithms, ranking systems, machine-learning systems, or
          other technical processes to identify, filter, rank, or recommend Job Listings.
        </P>
        <P>Matching results may depend on:</P>
        <Ul>
          <li>your preferences;</li>
          <li>information you provide;</li>
          <li>information contained in Job Listings;</li>
          <li>available job sources;</li>
          <li>timing of data collection;</li>
          <li>technical limitations;</li>
          <li>matching algorithms.</li>
        </Ul>
        <P>Automated matching may produce:</P>
        <Ul>
          <li>irrelevant results;</li>
          <li>incomplete results;</li>
          <li>duplicate results;</li>
          <li>delayed results;</li>
          <li>incorrect matches;</li>
          <li>missed opportunities.</li>
        </Ul>
        <P>JobQuest does not guarantee that every job suitable for you will be identified or presented.</P>
        <P>
          You remain responsible for reviewing each listing and determining whether it is suitable for
          you.
        </P>
      </>
    ),
  },
  {
    id: "listings",
    number: "08",
    title: "Job Listings",
    toc: "Job Listings",
    body: (
      <>
        <P>
          Job Listings may be collected from publicly accessible employer career pages and other
          permitted sources.
        </P>
        <P>Listings are provided for informational and discovery purposes.</P>
        <P>We do not guarantee that a Job Listing is:</P>
        <Ul>
          <li>current;</li>
          <li>accurate;</li>
          <li>complete;</li>
          <li>available;</li>
          <li>authentic;</li>
          <li>free of errors;</li>
          <li>still accepting applications;</li>
          <li>suitable for you;</li>
          <li>offered by the employer identified;</li>
          <li>available at the salary, location, or conditions shown.</li>
        </Ul>
        <P>A Job Listing may change or disappear after JobQuest collects it.</P>
        <P>
          You should always verify important information on the Employer&rsquo;s official application
          page before applying.
        </P>
      </>
    ),
  },
  {
    id: "employer-independence",
    number: "09",
    title: "Employer Independence",
    toc: "Employers",
    body: (
      <>
        <P>
          The appearance of an Employer or Job Listing on JobQuest does not necessarily indicate:
        </P>
        <Ul>
          <li>endorsement;</li>
          <li>sponsorship;</li>
          <li>partnership;</li>
          <li>affiliation;</li>
          <li>recruitment relationship;</li>
          <li>employment relationship.</li>
        </Ul>
        <P>Unless explicitly stated, JobQuest does not represent any Employer.</P>
        <P>JobQuest does not make hiring decisions.</P>
        <P>Employers are solely responsible for their recruitment processes and employment decisions.</P>
      </>
    ),
  },
  {
    id: "no-guarantee",
    number: "10",
    title: "No Employment Guarantee",
    toc: "No Guarantee",
    body: (
      <>
        <P>Use of JobQuest does not guarantee:</P>
        <Ul>
          <li>employment;</li>
          <li>an interview;</li>
          <li>a recruiter response;</li>
          <li>an application review;</li>
          <li>a job offer;</li>
          <li>a particular salary;</li>
          <li>career advancement;</li>
          <li>successful employment in a particular country;</li>
          <li>any other employment outcome.</li>
        </Ul>
        <P>JobQuest is not responsible for an Employer&rsquo;s hiring decision.</P>
      </>
    ),
  },
  {
    id: "reporting",
    number: "11",
    title: "Reporting Incorrect Listings",
    toc: "Reporting",
    body: (
      <>
        <P>
          If you identify an inaccurate, duplicate, misleading, stale, or otherwise problematic Job
          Listing, you may report it to: <strong>{LEGAL.supportEmail}</strong>
        </P>
        <P>
          We may investigate reported listings and, where appropriate, correct, update, restrict, or
          remove them.
        </P>
        <P>We do not guarantee that every reported listing will be removed or corrected immediately.</P>
      </>
    ),
  },
  {
    id: "telegram",
    number: "12",
    title: "Telegram Integration",
    toc: "Telegram",
    body: (
      <>
        <P>JobQuest may optionally allow you to connect a Telegram account for receiving notifications.</P>
        <P>Connecting Telegram is optional unless explicitly required for a particular feature.</P>
        <P>If you connect Telegram:</P>
        <Ul>
          <li>you authorize JobQuest to use the information necessary to provide the integration;</li>
          <li>JobQuest may send JobQuest-related notifications to the connected Telegram account;</li>
          <li>you are responsible for ensuring that the connected Telegram account belongs to you;</li>
          <li>you may disconnect Telegram through the available JobQuest controls;</li>
          <li>Telegram&rsquo;s own terms and policies may also apply.</li>
        </Ul>
        <P>
          JobQuest is not responsible for outages, limitations, policy changes, or failures of the
          Telegram platform.
        </P>
        <P>
          Data associated with Telegram integration is handled according to our{" "}
          <Link href="/privacy">Privacy Policy</Link>.
        </P>
      </>
    ),
  },
  {
    id: "notifications",
    number: "13",
    title: "Notifications",
    toc: "Notifications",
    body: (
      <>
        <P>JobQuest may send notifications through channels such as:</P>
        <Ul>
          <li>email;</li>
          <li>Telegram;</li>
          <li>in-app notifications;</li>
          <li>other notification mechanisms introduced by the Service.</li>
        </Ul>
        <P>Notification delivery may be affected by:</P>
        <Ul>
          <li>provider outages;</li>
          <li>email filtering;</li>
          <li>Telegram restrictions;</li>
          <li>network failures;</li>
          <li>incorrect contact information;</li>
          <li>technical delays.</li>
        </Ul>
        <P>We do not guarantee that every notification will be delivered immediately or successfully.</P>
      </>
    ),
  },
  {
    id: "free",
    number: "14",
    title: "Free Features",
    toc: "Free Features",
    body: (
      <>
        <P>JobQuest may provide certain features without payment.</P>
        <P>Free access may be subject to:</P>
        <Ul>
          <li>usage limits;</li>
          <li>feature limitations;</li>
          <li>promotional conditions;</li>
          <li>availability;</li>
          <li>changes to the Service.</li>
        </Ul>
        <P>We may modify or discontinue Free Features subject to applicable law.</P>
      </>
    ),
  },
  {
    id: "subscriptions",
    number: "15",
    title: "Paid Subscriptions",
    toc: "Subscriptions",
    body: (
      <>
        <P>JobQuest may offer paid subscription plans.</P>
        <P>Before purchasing a Subscription, the applicable:</P>
        <Ul>
          <li>price;</li>
          <li>billing interval;</li>
          <li>applicable taxes;</li>
          <li>included features;</li>
          <li>promotional discounts;</li>
          <li>renewal conditions;</li>
        </Ul>
        <P>will be presented through the applicable purchase flow.</P>
        <P>Unless otherwise stated, Subscription fees are payable in advance.</P>
      </>
    ),
  },
  {
    id: "pricing-taxes",
    number: "16",
    title: "Pricing and Taxes",
    toc: "Pricing",
    body: (
      <>
        <P>Prices are displayed in the applicable currency shown at checkout.</P>
        <P>
          Where applicable, taxes such as GST may be included or separately identified in accordance
          with applicable law and the pricing information presented before payment.
        </P>
        <P>
          The amount you are charged should correspond to the applicable price and taxes disclosed
          during the purchase process.
        </P>
        <P>
          JobQuest may change pricing for future billing periods, subject to applicable law and any
          notice requirements.
        </P>
        <P>
          A price change will not retroactively change an already completed billing period unless
          otherwise required by law.
        </P>
      </>
    ),
  },
  {
    id: "renewal",
    number: "17",
    title: "Automatic Renewal",
    toc: "Renewal",
    body: (
      <>
        <P>
          Where a Subscription is configured as recurring, the Subscription may automatically renew at
          the end of each billing period unless cancelled before the applicable renewal date.
        </P>
        <P>
          The applicable renewal price and billing interval should be displayed during the purchase
          process.
        </P>
        <P>
          You authorize the applicable payment processor to process recurring payments according to
          the authorization and payment flow presented to you.
        </P>
        <P>
          Recurring payments may be subject to applicable payment-system requirements and
          payment-provider rules.
        </P>
        <P>
          For recurring payments in India, applicable RBI requirements concerning e-mandates and
          pre-debit notifications may apply to the payment method and transaction.
        </P>
      </>
    ),
  },
  {
    id: "payments",
    number: "18",
    title: "Payment Processing",
    toc: "Payments",
    body: (
      <>
        <P>Payments may be processed through third-party payment providers, including Razorpay.</P>
        <P>
          JobQuest does not ordinarily receive or store complete payment-card credentials processed
          by the payment provider unless explicitly stated otherwise.
        </P>
        <P>
          Your use of a third-party payment provider may also be subject to that provider&rsquo;s
          applicable terms and policies.
        </P>
        <P>Payment confirmation may be required before paid features are activated.</P>
      </>
    ),
  },
  {
    id: "failed-payments",
    number: "19",
    title: "Failed Payments",
    toc: "Failed Payments",
    body: (
      <>
        <P>If a payment fails, JobQuest may:</P>
        <Ul>
          <li>retry payment where supported;</li>
          <li>notify you of the failure;</li>
          <li>temporarily restrict paid features;</li>
          <li>suspend the applicable Subscription;</li>
          <li>cancel the Subscription after applicable payment failures.</li>
        </Ul>
        <P>The exact handling may depend on the payment provider and applicable payment method.</P>
      </>
    ),
  },
  {
    id: "cancellation",
    number: "20",
    title: "Cancellation",
    toc: "Cancellation",
    body: (
      <>
        <P>
          You may cancel your Subscription using the cancellation mechanism made available through
          JobQuest or by contacting: <strong>{LEGAL.billingEmail}</strong>
        </P>
        <P>
          Unless otherwise stated in the <Link href="/refund">Refund &amp; Cancellation Policy</Link>,
          cancelling a Subscription prevents future renewal but does not necessarily terminate access
          immediately.
        </P>
        <P>Where applicable, paid access may continue until the end of the already-paid billing period.</P>
      </>
    ),
  },
  {
    id: "refunds",
    number: "21",
    title: "Refunds",
    toc: "Refunds",
    body: (
      <>
        <P>
          Refund eligibility is governed by the JobQuest{" "}
          <Link href="/refund">Refund &amp; Cancellation Policy</Link>.
        </P>
        <P>
          The <Link href="/refund">Refund &amp; Cancellation Policy</Link> forms part of these Terms
          by reference.
        </P>
        <P>The policy should explain applicable rules for:</P>
        <Ul>
          <li>subscription cancellation;</li>
          <li>accidental payments;</li>
          <li>duplicate payments;</li>
          <li>service issues;</li>
          <li>promotional purchases;</li>
          <li>coupon-based access;</li>
          <li>failed payments;</li>
          <li>partial-period refunds;</li>
          <li>chargebacks.</li>
        </Ul>
        <P>
          Nothing in this section limits any mandatory rights available to consumers under applicable
          law.
        </P>
      </>
    ),
  },
  {
    id: "coupons",
    number: "22",
    title: "Coupons and Promotional Access",
    toc: "Coupons",
    body: (
      <>
        <P>Coupons may provide free or discounted access subject to their specific conditions.</P>
        <P>Unless otherwise stated:</P>
        <Ul>
          <li>coupons have no cash value;</li>
          <li>coupons are non-transferable;</li>
          <li>coupons cannot be sold;</li>
          <li>coupons cannot necessarily be combined;</li>
          <li>coupons may have expiration dates;</li>
          <li>coupons may be restricted to eligible Accounts;</li>
          <li>fraudulent or abusive use may result in cancellation of the benefit.</li>
        </Ul>
        <P>
          If a promotional period converts into a paid Subscription, the applicable conversion price
          and renewal terms should be disclosed before activation.
        </P>
      </>
    ),
  },
  {
    id: "referrals",
    number: "23",
    title: "Referral Program",
    toc: "Referrals",
    body: (
      <>
        <P>
          Where JobQuest operates a referral program, referral benefits are available only for genuine
          referrals.
        </P>
        <P>You must not:</P>
        <Ul>
          <li>create fake Accounts;</li>
          <li>refer yourself through duplicate Accounts;</li>
          <li>use bots;</li>
          <li>spam users;</li>
          <li>misrepresent JobQuest;</li>
          <li>purchase or sell referral links;</li>
          <li>manipulate referral tracking.</li>
        </Ul>
        <P>We may investigate and revoke referral benefits obtained through abuse or fraud.</P>
      </>
    ),
  },
  {
    id: "acceptable-use",
    number: "24",
    title: "Acceptable Use",
    toc: "Acceptable Use",
    body: (
      <>
        <P>You agree to use JobQuest lawfully and responsibly.</P>
        <P>You must not:</P>
        <Ol>
          <li>share or resell your Account;</li>
          <li>scrape JobQuest&rsquo;s website or databases without authorization;</li>
          <li>use automated bots to abuse the Service;</li>
          <li>bypass rate limits;</li>
          <li>bypass authentication or subscription controls;</li>
          <li>attempt unauthorized access;</li>
          <li>interfere with the Service;</li>
          <li>distribute malware;</li>
          <li>conduct denial-of-service attacks;</li>
          <li>probe production systems without authorization;</li>
          <li>impersonate another person;</li>
          <li>submit intentionally false information;</li>
          <li>use JobQuest for unlawful purposes;</li>
          <li>harass or threaten others;</li>
          <li>abuse referral or coupon systems;</li>
          <li>reverse engineer the Service except where applicable law expressly permits it;</li>
          <li>exploit vulnerabilities without authorization;</li>
          <li>use JobQuest to infringe third-party rights.</li>
        </Ol>
      </>
    ),
  },
  {
    id: "security-reporting",
    number: "25",
    title: "Security and Vulnerability Reporting",
    toc: "Security",
    body: (
      <>
        <P>
          If you discover a potential security vulnerability, please report it responsibly to:{" "}
          <strong>{LEGAL.securityEmail}</strong>
        </P>
        <P>
          You must not exploit, disclose, or publicly expose a vulnerability before providing JobQuest
          a reasonable opportunity to investigate and address it.
        </P>
        <P>Nothing in this section restricts rights that cannot lawfully be restricted.</P>
      </>
    ),
  },
  {
    id: "user-content",
    number: "26",
    title: "User Content",
    toc: "User Content",
    body: (
      <>
        <P>You may provide information such as:</P>
        <Ul>
          <li>your name;</li>
          <li>job preferences;</li>
          <li>saved jobs;</li>
          <li>feedback;</li>
          <li>profile information;</li>
          <li>notification settings;</li>
          <li>other information necessary to use the Service.</li>
        </Ul>
        <P>You retain ownership of content that you lawfully own.</P>
        <P>
          You grant JobQuest the limited rights necessary to host, process, display, transmit, and
          otherwise use that information to provide the Service.
        </P>
        <P>
          Processing of personal information is governed by the JobQuest{" "}
          <Link href="/privacy">Privacy Policy</Link>.
        </P>
      </>
    ),
  },
  {
    id: "feedback",
    number: "27",
    title: "Feedback",
    toc: "Feedback",
    body: (
      <>
        <P>
          If you provide suggestions, ideas, feature requests, or other feedback about JobQuest, you
          permit JobQuest to use that feedback to improve the Service without creating an obligation
          to compensate you.
        </P>
        <P>We will not treat confidential information as feedback merely because you provide it.</P>
      </>
    ),
  },
  {
    id: "ip",
    number: "28",
    title: "Intellectual Property",
    toc: "Intellectual Property",
    body: (
      <>
        <P>
          The JobQuest name, logo, branding, interface design, software, source code, databases,
          documentation, and other original JobQuest materials are owned by or licensed to the Service
          operator, subject to applicable third-party rights.
        </P>
        <P>Except as expressly permitted by these Terms, you may not:</P>
        <Ul>
          <li>copy;</li>
          <li>reproduce;</li>
          <li>modify;</li>
          <li>distribute;</li>
          <li>sell;</li>
          <li>sublicense;</li>
          <li>publicly display;</li>
          <li>reverse engineer;</li>
          <li>create derivative works from;</li>
        </Ul>
        <P>JobQuest proprietary materials.</P>
        <P>
          Job Listing content remains subject to the rights of the respective Employers, publishers,
          or other rights holders.
        </P>
      </>
    ),
  },
  {
    id: "third-party",
    number: "29",
    title: "Third-Party Services",
    toc: "Third-Party Services",
    body: (
      <>
        <P>JobQuest may rely on third-party services for functions including:</P>
        <Ul>
          <li>payment processing;</li>
          <li>hosting;</li>
          <li>email;</li>
          <li>messaging;</li>
          <li>analytics;</li>
          <li>authentication;</li>
          <li>infrastructure;</li>
          <li>notifications.</li>
        </Ul>
        <P>
          Third-party services may have their own terms, privacy policies, availability limitations,
          and technical restrictions.
        </P>
        <P>
          JobQuest is not responsible for failures that are solely caused by a third-party service,
          subject to applicable law.
        </P>
      </>
    ),
  },
  {
    id: "privacy-data",
    number: "30",
    title: "Privacy and Personal Data",
    toc: "Privacy",
    body: (
      <>
        <P>
          JobQuest processes personal information according to its{" "}
          <Link href="/privacy">Privacy Policy</Link>.
        </P>
        <P>
          The <Link href="/privacy">Privacy Policy</Link> explains:
        </P>
        <Ul>
          <li>information collected;</li>
          <li>purposes of processing;</li>
          <li>use of information;</li>
          <li>data sharing;</li>
          <li>service providers;</li>
          <li>retention;</li>
          <li>security;</li>
          <li>user rights;</li>
          <li>deletion;</li>
          <li>grievance handling;</li>
          <li>cookies and similar technologies;</li>
          <li>Telegram integration.</li>
        </Ul>
        <P>
          Where applicable, personal-data processing will be carried out in accordance with applicable
          Indian data-protection law.
        </P>
        <P>
          The Digital Personal Data Protection Act establishes requirements concerning processing of
          digital personal data, including obligations concerning notice, consent where applicable,
          security, children&rsquo;s data, and grievance mechanisms.
        </P>
      </>
    ),
  },
  {
    id: "career-decisions",
    number: "31",
    title: "Employment and Career Decisions",
    toc: "Employment",
    body: (
      <>
        <P>JobQuest provides information and discovery tools.</P>
        <P>You are responsible for:</P>
        <Ul>
          <li>verifying eligibility;</li>
          <li>reviewing job descriptions;</li>
          <li>verifying Employer identity;</li>
          <li>reviewing salary information;</li>
          <li>determining work authorization;</li>
          <li>determining visa requirements;</li>
          <li>reviewing application deadlines;</li>
          <li>deciding whether to apply.</li>
        </Ul>
        <P>
          JobQuest does not provide legal, immigration, financial, or employment-law advice unless
          expressly stated.
        </P>
      </>
    ),
  },
  {
    id: "international",
    number: "32",
    title: "International Jobs",
    toc: "International Jobs",
    body: (
      <>
        <P>JobQuest may display jobs located outside your country of residence.</P>
        <P>You are responsible for determining:</P>
        <Ul>
          <li>work authorization;</li>
          <li>visa eligibility;</li>
          <li>immigration requirements;</li>
          <li>tax obligations;</li>
          <li>employment eligibility;</li>
          <li>local employment requirements.</li>
        </Ul>
        <P>
          JobQuest does not guarantee that you are eligible to work in the jurisdiction associated
          with a Job Listing.
        </P>
      </>
    ),
  },
  {
    id: "availability",
    number: "33",
    title: "Availability",
    toc: "Availability",
    body: (
      <>
        <P>
          We aim to maintain reasonable availability of the Service but do not guarantee
          uninterrupted operation.
        </P>
        <P>The Service may occasionally be unavailable because of:</P>
        <Ul>
          <li>maintenance;</li>
          <li>upgrades;</li>
          <li>infrastructure failures;</li>
          <li>security incidents;</li>
          <li>third-party outages;</li>
          <li>network failures;</li>
          <li>governmental actions;</li>
          <li>events beyond our reasonable control.</li>
        </Ul>
        <P>Where reasonably practical, we may provide notice of planned maintenance.</P>
      </>
    ),
  },
  {
    id: "changes-service",
    number: "34",
    title: "Changes to the Service",
    toc: "Changes",
    body: (
      <>
        <P>We may modify or discontinue features.</P>
        <P>Changes may include:</P>
        <Ul>
          <li>adding features;</li>
          <li>removing features;</li>
          <li>changing matching behavior;</li>
          <li>changing notification mechanisms;</li>
          <li>changing usage limits;</li>
          <li>changing Free Features;</li>
          <li>changing Subscription features.</li>
        </Ul>
        <P>
          If a material change substantially affects a paid Service, we will provide notice where
          required by applicable law or these Terms.
        </P>
      </>
    ),
  },
  {
    id: "disclaimer",
    number: "35",
    title: "Disclaimer of Warranties",
    toc: "Disclaimers",
    body: (
      <>
        <P>
          To the maximum extent permitted by applicable law, JobQuest is provided on an
          &ldquo;as available&rdquo; and &ldquo;as is&rdquo; basis.
        </P>
        <P>We do not guarantee that:</P>
        <Ul>
          <li>the Service will always be available;</li>
          <li>the Service will be error-free;</li>
          <li>Job Listings will always be accurate;</li>
          <li>every suitable job will be identified;</li>
          <li>alerts will always be delivered;</li>
          <li>Employers will respond;</li>
          <li>an Employer will hire you;</li>
          <li>the Service will meet every individual expectation.</li>
        </Ul>
        <P>
          Nothing in these Terms excludes a warranty, guarantee, or consumer right that cannot
          lawfully be excluded.
        </P>
      </>
    ),
  },
  {
    id: "liability",
    number: "36",
    title: "Limitation of Liability",
    toc: "Liability",
    body: (
      <>
        <P>
          To the maximum extent permitted by applicable law, JobQuest will not be responsible for
          indirect, incidental, special, consequential, exemplary, or similar losses arising from your
          use of the Service where such limitation is legally permitted.
        </P>
        <P>This may include losses relating to:</P>
        <Ul>
          <li>employment outcomes;</li>
          <li>missed applications;</li>
          <li>Employer decisions;</li>
          <li>inaccurate Job Listings;</li>
          <li>third-party services;</li>
          <li>notification failures;</li>
          <li>temporary Service outages.</li>
        </Ul>
        <P>
          To the maximum extent permitted by applicable law, the aggregate liability of JobQuest for
          claims arising from the Service will not exceed the amount you paid to JobQuest for the
          Service during the twelve months preceding the event giving rise to the claim.
        </P>
        <P>
          Nothing in these Terms limits liability or consumer rights that applicable law does not
          permit us to limit.
        </P>
        <P>
          <strong>This section should be reviewed by qualified Indian legal counsel before publication.</strong>
        </P>
      </>
    ),
  },
  {
    id: "indemnification",
    number: "37",
    title: "Indemnification",
    toc: "Indemnification",
    body: (
      <>
        <P>
          To the extent permitted by applicable law, you agree to be responsible for claims, losses,
          liabilities, and reasonable costs arising from your:
        </P>
        <Ul>
          <li>violation of these Terms;</li>
          <li>unlawful use of the Service;</li>
          <li>misuse of your Account;</li>
          <li>infringement of third-party rights;</li>
          <li>fraudulent activity;</li>
          <li>intentional misuse of the Service.</li>
        </Ul>
        <P>Nothing in this section limits rights that cannot legally be limited.</P>
      </>
    ),
  },
  {
    id: "suspension",
    number: "38",
    title: "Suspension",
    toc: "Suspension",
    body: (
      <>
        <P>We may temporarily suspend an Account where reasonably necessary because of:</P>
        <Ul>
          <li>security concerns;</li>
          <li>suspected fraud;</li>
          <li>payment issues;</li>
          <li>abuse;</li>
          <li>violation of these Terms;</li>
          <li>unlawful activity;</li>
          <li>threats to the Service or other users.</li>
        </Ul>
        <P>Where practical, we may provide notice and an opportunity to resolve the issue.</P>
        <P>
          Immediate suspension may occur where reasonably necessary to protect the Service, users, or
          comply with law.
        </P>
      </>
    ),
  },
  {
    id: "termination-you",
    number: "39",
    title: "Termination by You",
    toc: "Termination",
    body: (
      <>
        <P>You may stop using JobQuest at any time.</P>
        <P>
          You may request Account deletion through the available Account controls or by contacting:{" "}
          <strong>{LEGAL.supportEmail}</strong>
        </P>
        <P>
          Subscription cancellation and Account deletion may have different effects and are governed
          by the applicable billing and refund rules.
        </P>
      </>
    ),
  },
  {
    id: "termination-jobquest",
    number: "40",
    title: "Termination by JobQuest",
    toc: "Termination by Us",
    body: (
      <>
        <P>We may terminate or restrict an Account where permitted by law if:</P>
        <Ul>
          <li>you materially violate these Terms;</li>
          <li>you engage in fraud;</li>
          <li>you abuse the Service;</li>
          <li>you threaten Service security;</li>
          <li>payment obligations remain unresolved;</li>
          <li>continued access creates legal or security risk.</li>
        </Ul>
        <P>Where appropriate, we may provide notice before termination.</P>
      </>
    ),
  },
  {
    id: "effect-termination",
    number: "41",
    title: "Effect of Termination",
    toc: "After Termination",
    body: (
      <>
        <P>After termination:</P>
        <Ul>
          <li>your right to access applicable paid features may end;</li>
          <li>subscription renewal may stop;</li>
          <li>Account access may be disabled;</li>
          <li>
            applicable data may be deleted or anonymized according to the{" "}
            <Link href="/privacy">Privacy Policy</Link>;
          </li>
          <li>information that we are legally required or permitted to retain may be retained.</li>
        </Ul>
        <P>
          Termination does not automatically create a right to a refund unless provided by the{" "}
          <Link href="/refund">Refund &amp; Cancellation Policy</Link> or applicable law.
        </P>
      </>
    ),
  },
  {
    id: "grievance",
    number: "42",
    title: "Grievance Redressal",
    toc: "Grievances",
    body: (
      <>
        <P>
          JobQuest will maintain a mechanism for receiving and addressing applicable user and consumer
          grievances.
        </P>
        <P>
          <strong>Grievance Officer:</strong> {LEGAL.grievanceName}
          <br />
          <strong>Designation:</strong> {LEGAL.grievanceDesignation}
          <br />
          <strong>Email:</strong> {LEGAL.grievanceEmail}
          <br />
          <strong>Address:</strong> {LEGAL.grievanceAddress}
        </P>
        <P>
          Please include sufficient information for us to understand and investigate your grievance.
        </P>
        <P>
          Applicable Indian consumer/e-commerce rules impose requirements concerning grievance
          mechanisms and disclosure of grievance-officer information for covered e-commerce entities.
          The applicable requirements should be verified against JobQuest&rsquo;s actual legal
          structure and business model.
        </P>
      </>
    ),
  },
  {
    id: "disputes",
    number: "43",
    title: "Dispute Resolution",
    toc: "Disputes",
    body: (
      <>
        <P>
          If you have a dispute concerning the Service, please first contact:{" "}
          <strong>{LEGAL.legalEmail}</strong>
        </P>
        <P>We will attempt to resolve the issue informally where reasonably possible.</P>
        <P>
          Nothing in this section prevents you from exercising any statutory consumer or other legal
          rights that cannot lawfully be waived.
        </P>
      </>
    ),
  },
  {
    id: "governing-law",
    number: "44",
    title: "Governing Law",
    toc: "Governing Law",
    body: (
      <>
        <P>
          These Terms will be governed by the laws of India, subject to applicable mandatory
          consumer-protection and other statutory rights.
        </P>
        <P>
          The appropriate courts/forum and jurisdiction should be specified after confirming the legal
          operator&rsquo;s registered location and obtaining appropriate legal advice.
        </P>
      </>
    ),
  },
  {
    id: "force-majeure",
    number: "45",
    title: "Force Majeure",
    toc: "Force Majeure",
    body: (
      <>
        <P>
          JobQuest will not be responsible for delay or failure caused by circumstances beyond its
          reasonable control, including where applicable:
        </P>
        <Ul>
          <li>natural disasters;</li>
          <li>war;</li>
          <li>civil unrest;</li>
          <li>governmental action;</li>
          <li>telecommunications failures;</li>
          <li>major internet outages;</li>
          <li>cloud infrastructure failures;</li>
          <li>payment-provider failures;</li>
          <li>third-party platform outages;</li>
          <li>widespread cybersecurity incidents.</li>
        </Ul>
        <P>This does not affect rights that applicable law does not permit us to exclude.</P>
      </>
    ),
  },
  {
    id: "severability",
    number: "46",
    title: "Severability",
    toc: "Severability",
    body: (
      <>
        <P>
          If any provision of these Terms is determined to be invalid, unlawful, or unenforceable,
          that provision will be interpreted or modified to the maximum extent permitted by law, and
          the remaining provisions will continue to apply.
        </P>
      </>
    ),
  },
  {
    id: "waiver",
    number: "47",
    title: "Waiver",
    toc: "Waiver",
    body: (
      <>
        <P>
          Failure to enforce a provision of these Terms does not constitute a waiver of our right to
          enforce that provision later.
        </P>
      </>
    ),
  },
  {
    id: "assignment",
    number: "48",
    title: "Assignment",
    toc: "Assignment",
    body: (
      <>
        <P>
          You may not transfer or assign your rights or obligations under these Terms without our
          prior written consent, except where such restriction is prohibited by applicable law.
        </P>
        <P>
          We may assign or transfer these Terms in connection with a merger, acquisition,
          restructuring, sale of substantially all relevant assets, or similar transaction, subject to
          applicable law.
        </P>
      </>
    ),
  },
  {
    id: "entire-agreement",
    number: "49",
    title: "Entire Agreement",
    toc: "Entire Agreement",
    body: (
      <>
        <P>
          These Terms, together with the <Link href="/privacy">Privacy Policy</Link>,{" "}
          <Link href="/refund">Refund &amp; Cancellation Policy</Link>, Cookie Policy, and any other
          policies expressly incorporated into these Terms, form the applicable agreement governing
          your use of the Service.
        </P>
        <P>
          If a specific product or promotional offer has additional terms, those terms will apply to
          that offer to the extent of any conflict.
        </P>
      </>
    ),
  },
  {
    id: "survival",
    number: "50",
    title: "Survival",
    toc: "Survival",
    body: (
      <>
        <P>
          Provisions which by their nature should survive termination will continue to apply after
          termination, including provisions concerning:
        </P>
        <Ul>
          <li>intellectual property;</li>
          <li>payment obligations;</li>
          <li>disclaimers;</li>
          <li>limitations of liability;</li>
          <li>indemnification;</li>
          <li>dispute resolution;</li>
          <li>governing law;</li>
          <li>other provisions intended to survive termination.</li>
        </Ul>
      </>
    ),
  },
  {
    id: "changes-terms",
    number: "51",
    title: "Changes to These Terms",
    toc: "Changes to Terms",
    body: (
      <>
        <P>We may update these Terms from time to time.</P>
        <P>
          For material changes, we may provide notice through one or more appropriate channels, such
          as:
        </P>
        <Ul>
          <li>email;</li>
          <li>in-app notification;</li>
          <li>website notice;</li>
          <li>dashboard notification.</li>
        </Ul>
        <P>The updated Terms will identify the applicable &ldquo;Last Updated&rdquo; date.</P>
        <P>
          Where applicable law requires affirmative acceptance of updated Terms, we will obtain such
          acceptance.
        </P>
      </>
    ),
  },
  {
    id: "contact",
    number: "52",
    title: "Contact",
    toc: "Contact",
    body: (
      <>
        <P>
          For general support: <strong>{LEGAL.supportEmail}</strong>
        </P>
        <P>
          For billing: <strong>{LEGAL.billingEmail}</strong>
        </P>
        <P>
          For privacy: <strong>{LEGAL.privacyEmail}</strong>
        </P>
        <P>
          For legal matters: <strong>{LEGAL.legalEmail}</strong>
        </P>
        <P>
          For security: <strong>{LEGAL.securityEmail}</strong>
        </P>
        <P>
          For grievances: <strong>{LEGAL.grievanceEmail}</strong>
        </P>
        <P>
          <strong>{LEGAL.operatorShort}</strong>
          <br />
          Operating JobQuest
          <br />
          <strong>{LEGAL.address}</strong>
        </P>
      </>
    ),
  },
];
