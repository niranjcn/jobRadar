export type ReferralJob = {
  company: string;
  title: string;
  external_job_id: string;
};

export function referralMessage(job: ReferralJob): string {
  return [
    "Hi [Name],",
    "",
    "I hope you're doing well. I've been following your journey at " +
      job.company +
      " and really admire your experience there.",
    "",
    "I'm a recent Computer Science graduate currently exploring Software Engineering opportunities, " +
      "and I came across the " +
      job.title +
      " (Job ID: " +
      job.external_job_id +
      ") role. My background in Python, Java, SQL, Data Structures & Algorithms, " +
      "and backend development aligns well with the role.",
    "",
    "If you're open to it, I'd really appreciate a quick conversation. I'd also be grateful if you " +
      "could consider referring me for this position.",
    "",
    "I've attached my resume for your reference.",
    "",
    "Thank you for your time, and I look forward to hearing from you.",
    "",
    "Best regards,",
    "Niranj C N",
  ].join("\n");
}

export async function copyReferral(job: ReferralJob): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(referralMessage(job));
    return true;
  } catch {
    return false;
  }
}
