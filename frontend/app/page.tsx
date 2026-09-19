import { JobQuestLanding } from "@/components/landing/jobquest-landing";

export const metadata = {
  title: "JobQuest · Find Your Next Opportunity",
  description:
    "Discover the best jobs from top companies, tailored to your skills and goals. Jobs find you.",
};

export default function Home() {
  return <JobQuestLanding />;
}
