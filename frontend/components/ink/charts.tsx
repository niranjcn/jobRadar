"use client";

import styles from "./ink.module.css";

/** Tiny sparkline bars for metric cards. */
export function Spark({ values, blue = false }: { values: number[]; blue?: boolean }) {
  const max = Math.max(1, ...values);
  return (
    <span className={`${styles.spark} ${blue ? styles.blue : ""}`} aria-hidden>
      {values.map((v, i) => (
        <span key={i} style={{ height: `${Math.max(12, Math.round((v / max) * 100))}%` }} />
      ))}
    </span>
  );
}
