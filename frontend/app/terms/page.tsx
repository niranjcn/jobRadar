import Link from "next/link";
import { LEGAL } from "./legal";
import { TERMS_SECTIONS } from "./terms-content";
import styles from "./terms.module.css";

export const metadata = {
  title: "Terms of Service | JobQuest",
  description:
    "Read the JobQuest Terms of Service governing use of the JobQuest job discovery and alerting platform.",
};

export default function TermsPage() {
  return (
    <div className={styles.page}>
      <a href="#terms-content" className={styles.skip}>
        Skip to content
      </a>

      <header className={styles.nav}>
        <div className={styles.navInner}>
          <Link href="/" className={styles.brand}>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="/logo.png" alt="JobQuest" width={30} height={30} style={{ borderRadius: 8 }} />
            JobQuest
          </Link>
          <nav aria-label="Primary" className={styles.navLinks}>
            <Link href="/">Home</Link>
            <Link href="/pricing">Pricing</Link>
            <Link href="/contact">Contact</Link>
          </nav>
          <Link href="/login" className={styles.signIn}>
            Sign in
          </Link>
          <Link href="/register" className={styles.getStarted}>
            Get started
          </Link>
        </div>
      </header>

      <main id="terms-content">
        <div className={styles.hero}>
          <p className={styles.eyebrow}>Legal</p>
          <h1 className={styles.heroTitle}>Terms of Service</h1>
          <p className={styles.heroSub}>
            The terms governing your use of JobQuest. Clear, transparent, and designed to protect
            both you and the service.
          </p>
          <p className={styles.heroMeta}>Last updated: {LEGAL.lastUpdated}</p>
        </div>

        <div className={styles.doc}>
          <nav aria-label="Table of contents" className={styles.toc}>
            <p className={styles.tocTitle}>Contents</p>
            <ol className={styles.tocList}>
              {TERMS_SECTIONS.map((s) => (
                <li key={s.id}>
                  <a href={`#${s.id}`}>
                    <span className={styles.tocNum}>{s.number}</span> {s.toc}
                  </a>
                </li>
              ))}
            </ol>
          </nav>

          <article className={styles.article}>
            <details className={styles.tocMobile}>
              <summary>Contents</summary>
              <ol>
                {TERMS_SECTIONS.map((s) => (
                  <li key={s.id}>
                    <a href={`#${s.id}`}>{s.title}</a>
                  </li>
                ))}
              </ol>
            </details>

            <div className={styles.preamble}>
              <p>
                These Terms of Service (&ldquo;Terms&rdquo;) govern your access to and use of
                JobQuest, including the JobQuest website, dashboard, job discovery services, job
                alerts, matching features, notifications, Telegram integration, subscriptions, and
                related services (collectively, the &ldquo;Service&rdquo;).
              </p>
              <div className={styles.operatorBox}>
                <p>
                  <strong>The Service is operated by {LEGAL.operatorShort}.</strong>
                </p>
                <p>{LEGAL.operatorNote}</p>
                <p>
                  <strong>Registered/Business Address:</strong> {LEGAL.address}
                  <br />
                  <strong>Email:</strong> {LEGAL.supportEmail}
                  <br />
                  <strong>Legal/Grievance Email:</strong> {LEGAL.grievanceEmail}
                </p>
              </div>
              <p>
                In these Terms, &ldquo;{LEGAL.operatorShort}&rdquo;, &ldquo;JobQuest&rdquo;,
                &ldquo;we&rdquo;, &ldquo;us&rdquo;, and &ldquo;our&rdquo; refer to the operator of
                the Service, and &ldquo;you&rdquo;, &ldquo;your&rdquo;, or &ldquo;User&rdquo; refers
                to the person accessing or using the Service.
              </p>
              <p>
                By creating an account, purchasing a subscription, clicking an acceptance checkbox,
                or otherwise using the Service where acceptance is required, you acknowledge that you
                have read and agree to these Terms.
              </p>
              <p>
                If you do not agree to these Terms, do not create an account or use the Service.
              </p>
            </div>

            {TERMS_SECTIONS.map((s) => (
              <section key={s.id} id={s.id} aria-labelledby={`${s.id}-heading`} className={styles.section}>
                <div className={styles.sectionHead}>
                  <span className={styles.sectionNum}>{s.number}</span>
                  <h2 id={`${s.id}-heading`}>{s.title}</h2>
                </div>
                {s.body}
              </section>
            ))}

            <div className={styles.support}>
              <h2>Questions about these Terms?</h2>
              <p>
                If you have questions about JobQuest or these Terms, contact our support team.
              </p>
              <Link href="/contact" className={styles.cta}>
                Contact support &rarr;
              </Link>
            </div>

            <div className={styles.related}>
              <h2>Related policies</h2>
              <ul>
                <li>
                  <Link href="/privacy">Privacy Policy</Link>
                </li>
                <li>
                  <Link href="/refund">Refund &amp; Cancellation Policy</Link>
                </li>
                <li>
                  <Link href="/contact">Contact</Link>
                </li>
              </ul>
            </div>

            <div className={styles.docFooter}>
              <p>
                <strong>Product:</strong> JobQuest &nbsp;·&nbsp; <strong>Document:</strong> Terms of
                Service &nbsp;·&nbsp; <strong>Version:</strong> {LEGAL.version} &nbsp;·&nbsp;{" "}
                <strong>Last Updated:</strong> {LEGAL.lastUpdated}
              </p>
            </div>
          </article>
        </div>
      </main>

      <footer className={styles.footer}>
        <div className={styles.footerInner}>
          <div className={styles.footerBrand}>
            <Link href="/" className={styles.brand}>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src="/logo.png" alt="JobQuest" width={28} height={28} style={{ borderRadius: 8 }} />
              JobQuest
            </Link>
            <p>
              Better Opportunities.
              <br />
              Brighter Tomorrow.
            </p>
          </div>
          <div className={styles.footerCol}>
            <h3>Product</h3>
            <ul>
              <li>
                <Link href="/">Home</Link>
              </li>
              <li>
                <Link href="/pricing">Pricing</Link>
              </li>
              <li>
                <Link href="/contact">Contact</Link>
              </li>
            </ul>
          </div>
          <div className={styles.footerCol}>
            <h3>Legal</h3>
            <ul>
              <li>
                <Link href="/privacy">Privacy</Link>
              </li>
              <li>
                <Link href="/terms">Terms</Link>
              </li>
              <li>
                <Link href="/refund">Refunds</Link>
              </li>
              <li>
                <Link href="/contact">Contact</Link>
              </li>
            </ul>
          </div>
        </div>
        <p className={styles.copyright}>© 2026 JobQuest. All rights reserved.</p>
      </footer>
    </div>
  );
}
