"use client";

import styles from "./ink.module.css";

/** Atmospheric radar-tower night scene. Decorative; blends into the hero. */
export function HeroArt() {
  return (
    <svg className={styles.heroArt} viewBox="0 0 640 300" fill="none" aria-hidden>
      <defs>
        <radialGradient id="hq-sun" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#C4B5FD" stopOpacity="0.85" />
          <stop offset="45%" stopColor="#8B5CF6" stopOpacity="0.38" />
          <stop offset="100%" stopColor="#7C3AED" stopOpacity="0" />
        </radialGradient>
        <linearGradient id="hq-sky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#1E1E2E" stopOpacity="0" />
          <stop offset="100%" stopColor="#1A1A24" stopOpacity="0.55" />
        </linearGradient>
      </defs>

      <rect x="240" y="0" width="400" height="300" fill="url(#hq-sky)" opacity="0.7" />
      <ellipse cx="430" cy="105" rx="150" ry="90" fill="url(#hq-sun)" />
      <circle cx="430" cy="105" r="34" fill="#DDD6FE" />
      <circle cx="430" cy="105" r="34" fill="#8B5CF6" opacity="0.2" />

      {/* clouds */}
      <g fill="#181825" opacity="0.9">
        <ellipse cx="330" cy="80" rx="70" ry="14" />
        <ellipse cx="520" cy="60" rx="80" ry="13" />
        <ellipse cx="470" cy="140" rx="90" ry="12" opacity="0.7" />
      </g>
      <g fill="#8B5CF6" opacity="0.16">
        <ellipse cx="330" cy="86" rx="55" ry="7" />
        <ellipse cx="520" cy="66" rx="62" ry="6" />
      </g>

      {/* far mountains */}
      <path
        d="M180 235 280 130l45 60 55-85 60 95 40-50 60 85 50-45 50 45v80H180z"
        fill="#171724"
      />
      {/* snow caps */}
      <g fill="#E9E9F1" opacity="0.18">
        <path d="M380 115l14 22-8 5-8-6-9 5-7-4z" />
        <path d="M540 145l12 18-7 4-7-5-8 4-6-3z" />
      </g>
      {/* near ridge */}
      <path d="M120 260 230 175l60 70 70-60 90 75 90-55 100 55v40H120z" fill="#0F0F14" />

      {/* pines */}
      <g fill="#041014">
        <path d="M205 262l10-26 10 26h-7v10h-6v-10z" />
        <path d="M228 266l8-20 8 20h-5v8h-6v-8z" />
        <path d="M585 258l10-26 10 26h-7v10h-6v-10z" />
        <path d="M608 262l8-20 8 20h-5v8h-6v-8z" />
      </g>

      {/* watchtower */}
      <g stroke="#0A0A0F" strokeLinecap="round">
        <path d="M508 260 500 180M548 260l8-80" strokeWidth="7" />
        <path d="M502 220h52M504 200h48" strokeWidth="4" />
        <rect x="492" y="138" width="72" height="44" rx="3" fill="#0A0A0F" stroke="none" />
        <path d="M488 138 528 108l40 30" strokeWidth="6" />
        <path d="M500 138v-12h56v12" strokeWidth="4" />
        <rect x="519" y="150" width="18" height="14" rx="2" fill="#A78BFA" opacity="0.9" stroke="none" />
        <path d="M528 108V92" strokeWidth="4" />
        <circle cx="528" cy="86" r="4" fill="#A78BFA" stroke="none" opacity="0.95" />
      </g>

      {/* birds */}
      <g stroke="#0B2428" strokeWidth="2.5" strokeLinecap="round" fill="none">
        <path d="M300 70q7-7 14 0q7-7 14 0" />
        <path d="M345 52q5-5 10 0q5-5 10 0" />
      </g>

      {/* handwritten note */}
      <g className={styles.hand} fill="#A1A1AA" fontSize="24" transform="rotate(-4 90 90)">
        <text x="34" y="86">MORE</text>
        <text x="42" y="116">JOBS</text>
        <text x="26" y="146">BRIGHTER</text>
        <text x="38" y="176">PEOPLE</text>
      </g>
      <path
        d="M118 178c14 8 30 10 46 6"
        stroke="#A78BFA"
        strokeWidth="2.5"
        strokeLinecap="round"
        opacity="0.75"
      />
    </svg>
  );
}
