// Central legal configuration — public contact placeholders only, no secrets.
// Bracket tokens render visibly until real values are configured.
export const LEGAL = {
  // No registered legal entity: independent-operator wording (owner instruction).
  operatorShort: "the JobQuest operator",
  operatorNote:
    "JobQuest is an independently operated software service, currently operated by its individual developer.",
  address: "[FULL_ADDRESS]",
  supportEmail: "[SUPPORT_EMAIL]",
  billingEmail: "[BILLING_EMAIL]",
  privacyEmail: "[PRIVACY_EMAIL]",
  legalEmail: "[LEGAL_EMAIL]",
  securityEmail: "[SECURITY_EMAIL]",
  grievanceName: "[NAME]",
  grievanceDesignation: "[DESIGNATION]",
  grievanceEmail: "[GRIEVANCE_EMAIL]",
  grievanceAddress: "[ADDRESS]",
  lastUpdated: "September 2026",
  version: "2.0",
  // No effective date configured — intentionally omitted from the page.
  effectiveDate: null as string | null,
};
