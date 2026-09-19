"use client";

import styles from "@/components/ink/ink.module.css";
import {
  AnalyticsRail,
  MetricsRow,
  OpportunityFeed,
  SystemStatusWide,
  useOverviewData,
} from "@/components/ink/overview";

export default function DashboardPage() {
  const d = useOverviewData(30);

  return (
    <div className={styles.content}>
      {d.loading ? (
        <p className={styles.emptyNote}>Loading your radar…</p>
      ) : d.error ? (
        <p className={styles.emptyNote}>{d.error}</p>
      ) : (
        <>
          <MetricsRow stats={d.stats} daily={d.daily} sourcesActive={d.sourcesActive} />
          <div className={styles.grid2}>
            <OpportunityFeed jobs={d.feed} total={d.stats?.jobs_total ?? 0} saved={d.saved} onToggleSave={d.toggleSave} />
            <AnalyticsRail
              daily={d.daily}
              companies={d.companies}
              sourcesActive={d.sourcesActive}
              sourcesTotal={d.sourcesTotal}
              lastRunAt={d.lastRunAt}
              lastRunOk={d.lastRunOk}
              notifSent={d.notifSent}
              dbMs={d.dbMs}
            />
          </div>
          <SystemStatusWide
            sourcesActive={d.sourcesActive}
            sourcesTotal={d.sourcesTotal}
            lastRunAt={d.lastRunAt}
            lastRunOk={d.lastRunOk}
            notifSent={d.notifSent}
            dbMs={d.dbMs}
          />
        </>
      )}
    </div>
  );
}
