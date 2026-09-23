import Link from "next/link";
import { REFUND_SECTIONS } from "./refund-content";
import styles from "../terms/terms.module.css";

export const metadata = {
  title: "Refund & Cancellation Policy | JobQuest",
  description:
    "Learn how JobQuest subscriptions, cancellations, refunds, billing issues, and promotional access are handled.",
};

export default function RefundPage() {
  return (
    <div className={styles.page}>
      <a href="#refund-content" className={styles.skip}>
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

      <main id="refund-content">
        <div className={styles.hero}>
          <p className={styles.eyebrow}>Legal</p>
          <h1 className={styles.heroTitle}>Refund &amp; Cancellation Policy</h1>
          <p className={styles.heroSub}>
            How JobQuest subscriptions are charged, how cancellation works, when refunds apply,
            and where to get help with billing.
          </p>
          <p className={styles.heroMeta}>
            Last updated: September 2026 · Operated by the JobQuest operator, an independent
            software service run by its individual developer.
          </p>
        </div>

        <div className={styles.doc}>
          <nav aria-label="Table of contents" className={styles.toc}>
            <p className={styles.tocTitle}>Contents</p>
            <ol className={styles.tocList}>
              {REFUND_SECTIONS.map((s) => (
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
                {REFUND_SECTIONS.map((s) => (
                  <li key={s.id}>
                    <a href={`#${s.id}`}>{s.title}</a>
                  </li>
                ))}
              </ol>
            </details>

            {REFUND_SECTIONS.map((s) => (
              <section key={s.id} id={s.id} aria-labelledby={`${s.id}-heading`} className={styles.section}>
                <div className={styles.sectionHead}>
                  <span className={styles.sectionNum}>{s.number}</span>
                  <h2 id={`${s.id}-heading`}>{s.title}</h2>
                </div>
                {s.body}
              </section>
            ))}

            <div className={styles.support}>
              <h2>Billing problem?</h2>
              <p>
                Include your account email and Razorpay payment ID so the charge can be traced.
              </p>
              <Link href="/contact" className={styles.cta}>
                Contact support &rarr;
              </Link>
            </div>

            <div className={styles.related}>
              <h2>Related documents</h2>
              <ul>
                <li>
                  <Link href="/terms">Terms of Service</Link>
                </li>
                <li>
                  <Link href="/privacy">Privacy Policy</Link>
                </li>
                <li>
                  <Link href="/contact">Contact</Link>
                </li>
              </ul>
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
