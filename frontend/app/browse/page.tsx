import { Suspense } from "react";
import { BrowseJobs } from "./browse-jobs";
import { RadarLoading } from "@/components/radar-loading";

export const metadata = {
  title: "Browse Jobs · JobQuest",
  description: "Browse every tracked job posting. No login required.",
};

export default function BrowsePage() {
  return (
    <Suspense fallback={<RadarLoading label="Loading jobs…" />}>
      <BrowseJobs />
    </Suspense>
  );
}
