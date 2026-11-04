import Link from "next/link";
import { PRIVACY_SECTIONS } from "./privacy-content";
import styles from "./privacy.module.css";

export const metadata = {
  title: "Privacy Policy | JobQuest",
  description:
    "How JobQuest collects, uses, shares, retains, and deletes your information — based on what the software actually does.",
};

export default function PrivacyPage() {
  return (
    <div className={styles.page}>
      <a href="#privacy-content" className={styles.skip}>
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

      <main id="privacy-content">
        <div className={styles.hero}>
          <p className={styles.eyebrow}>Legal</p>
          <h1 className={styles.heroTitle}>Privacy Policy</h1>
          <p className={styles.heroSub}>
            What JobQuest collects, why it collects it, who receives it, how long it is kept,
            and what choices you have — written against what the software actually does.
          </p>
          <p className={styles.heroMeta}>
            Last updated: September 2026 · Operated by the JobQuest operator, an independent
            software service run by its individual developer. No registered company exists yet —
            identity and contact details below are marked placeholders, not facts.
          </p>
        </div>

        <div className={styles.doc}>
          <nav aria-label="Table of contents" className={styles.toc}>
            <p className={styles.tocTitle}>Contents</p>
            <ol className={styles.tocList}>
              {PRIVACY_SECTIONS.map((s) => (
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
                {PRIVACY_SECTIONS.map((s) => (
                  <li key={s.id}>
                    <a href={`#${s.id}`}>{s.title}</a>
                  </li>
                ))}
              </ol>
            </details>

            {PRIVACY_SECTIONS.map((s) => (
              <section key={s.id} id={s.id} aria-labelledby={`${s.id}-heading`} className={styles.section}>
                <div className={styles.sectionHead}>
                  <span className={styles.sectionNum}>{s.number}</span>
                  <h2 id={`${s.id}-heading`}>{s.title}</h2>
                </div>
                {s.body}
              </section>
            ))}

            <div className={styles.support}>
              <h2>Questions about your information?</h2>
              <p>
                If you have questions about this policy or your information, contact support. For
                account access issues, include your account email.
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
                  <Link href="/refund">Refund &amp; Cancellation Policy</Link>
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
                <Link href="/dmca">DMCA</Link>
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
