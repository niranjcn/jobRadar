"use client";

import { useState } from "react";
import styles from "./ink.module.css";
import { InkHeader } from "./InkHeader";
import { InkSidebar } from "./InkSidebar";

export function InkShell({ children }: { children: React.ReactNode }) {
  const [drawer, setDrawer] = useState(false);

  return (
    <div className={styles.ink}>
      <div className={styles.shell}>
        <InkSidebar open={drawer} onClose={() => setDrawer(false)} />
        <div className={styles.main}>
          <InkHeader onMenu={() => setDrawer(true)} />
          <main>{children}</main>
        </div>
      </div>
    </div>
  );
}
