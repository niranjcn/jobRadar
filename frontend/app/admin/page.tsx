"use client";

import styles from "@/components/ink/ink.module.css";
import {
  AnalyticsRail,
  Greeting,
  MetricsRow,
  OpportunityFeed,
  timeGreeting,
  useOverviewData,
} from "@/components/ink/overview";

export default function AdminOverviewPage() {
  const d = useOverviewData(30);

  return (
    <div>
      <Greeting kick={`${timeGreeting()},`} name="Admin" sub="System overview and health." />
      {d.loading ? (
        <p className={styles.emptyNote}>Loading overview…</p>
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
        </>
      )}
    </div>
  );
}
