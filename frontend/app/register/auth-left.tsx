import { BarChart3Icon, SendIcon, TargetIcon, ZapIcon } from "./icons";
import styles from "./auth.module.css";

const FEATURES = [
  { icon: ZapIcon, title: "Real-time job alerts", desc: "Be the first to know." },
  { icon: TargetIcon, title: "Smart matches", desc: "Jobs that fit you." },
  { icon: BarChart3Icon, title: "Track your progress", desc: "Stay organized, always." },
  { icon: SendIcon, title: "Telegram notifications", desc: "Opportunities, wherever you are." },
];

export function AuthLeft() {
  return (
    <div className={styles.left}>
      <div className={styles.leftContent}>
        <div className={styles.brand}>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/logo.png" alt="JobQuest" width={44} height={44} style={{ borderRadius: 12 }} />
          <span className={styles.brandName}>JobQuest</span>
        </div>

        <p className={styles.eyebrow}>More than a job search</p>
        <h1 className={styles.headline}>
          Your next
          <br />
          <span className={styles.headlineAccent}>opportunity</span>
          <br />
          starts here.
        </h1>
        <p className={styles.sub}>
          JobQuest helps you find, track and land your dream job with smarter alerts and personalized matches.
        </p>

        <ul className={styles.features}>
          {FEATURES.map((f) => (
            <li key={f.title} className={styles.feature}>
              <span className={styles.featureIcon}>
                <f.icon size={26} strokeWidth={1.8} />
              </span>
              <span>
                <p className={styles.featureTitle}>{f.title}</p>
                <p className={styles.featureDesc}>{f.desc}</p>
              </span>
            </li>
          ))}
        </ul>

        <div className={styles.bottomDeco}>
          <div className={styles.bottomLine} />
          <p className={styles.bottomText}>Build a brighter tomorrow</p>
        </div>
      </div>

      <div className={styles.cineWrap} aria-hidden>
        <div className={styles.cineFloat}>
          <div className={styles.cine}>
            <div className={styles.cineSky} />
            <div className={styles.cineBeam} />
            <div className={styles.cineGlow} />
            <div className={styles.cineFog} />
            <div className={styles.cineFloor}>
              <div className={styles.cineFloorLine} />
            </div>
            <div className={styles.cineShade} />
            <div className={styles.cineText}>Better Jobs Brighter Tomorrow</div>
          </div>
        </div>
      </div>
    </div>
  );
}
