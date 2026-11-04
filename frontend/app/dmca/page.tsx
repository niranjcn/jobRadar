import { LEGAL, LegalH, LegalList, LegalP, LegalShell } from "@/components/legal-shell";

export const metadata = {
  title: "JobQuest · Copyright & DMCA",
  description: "How to report copyright infringement on JobQuest and how counter-notices work.",
};

const SECTIONS = [
  { id: "policy", title: "Copyright policy" },
  { id: "notice", title: "Filing a takedown notice" },
  { id: "counter", title: "Counter-notices" },
  { id: "repeat", title: "Repeat infringers" },
  { id: "agent", title: "Designated agent" },
];

export default function DmcaPage() {
  return (
    <LegalShell
      eyebrow="Legal"
      title="Copyright & DMCA"
      intro="How to report content on JobQuest that you believe infringes your copyright, and what happens next."
      sections={SECTIONS}
    >
      <LegalH id="policy" index={1}>Copyright policy</LegalH>
      <LegalP>
        JobQuest respects the intellectual property of others. Job listings shown on JobQuest
        come from employers&rsquo; own public career pages — the listing text, logos, and images
        remain the property of the respective employer or rights holder. User accounts hold only
        preferences and settings; JobQuest does not host user-uploaded images or files.
      </LegalP>
      <LegalP>
        If you believe content displayed on JobQuest infringes your copyright, you may request
        its removal by sending a notice that meets the requirements below. We review valid
        notices promptly and remove or disable access to the identified material.
      </LegalP>

      <LegalH id="notice" index={2}>Filing a takedown notice</LegalH>
      <LegalP>
        Email your notice to {LEGAL.dmcaEmail} with the subject line
        &ldquo;DMCA Takedown Notice&rdquo;. Your notice must include:
      </LegalP>
      <LegalList>
        <li>identification of the copyrighted work you claim is infringed (title, URL, or registration number);</li>
        <li>the exact JobQuest URL(s) where the infringing material appears;</li>
        <li>your full name, mailing address, phone number, and email address;</li>
        <li>
          a statement that you have a good-faith belief the use is not authorized by the
          copyright owner, its agent, or the law;
        </li>
        <li>
          a statement, under penalty of perjury, that the information in your notice is accurate
          and that you are the copyright owner or authorized to act on the owner&rsquo;s behalf;
        </li>
        <li>your physical or electronic signature.</li>
      </LegalList>
      <LegalP>
        Incomplete notices cannot be acted on — we will reply asking for the missing pieces.
        Knowingly false claims carry liability, so please verify ownership before filing.
      </LegalP>

      <LegalH id="counter" index={3}>Counter-notices</LegalH>
      <LegalP>
        If your material was removed following a notice and you believe the removal was a
        mistake or misidentification, email {LEGAL.dmcaEmail} with the subject line
        &ldquo;DMCA Counter-Notice&rdquo;, including the removed URL(s), your contact details,
        a consent-to-jurisdiction statement, and your signature under penalty of perjury. We
        forward valid counter-notices to the original complainant; unless they confirm court
        action within 10–14 business days, the material may be restored.
      </LegalP>

      <LegalH id="repeat" index={4}>Repeat infringers</LegalH>
      <LegalP>
        Accounts that repeatedly trigger valid infringement notices may be suspended or
        terminated under the Terms of Service.
      </LegalP>

      <LegalH id="agent" index={5}>Designated agent</LegalH>
      <LegalP>
        Copyright agent: {LEGAL.dmcaEmail}
        <br />
        {LEGAL.entity} · {LEGAL.address}
      </LegalP>
      <LegalP>
        Note: the agent contact above is a placeholder until a formal designation is filed
        with the U.S. Copyright Office (required for DMCA safe harbor on user content).
        Employer listing corrections (stale or wrong job data, not copyright claims) go to{" "}
        {LEGAL.email} — see Contact.
      </LegalP>
    </LegalShell>
  );
}
