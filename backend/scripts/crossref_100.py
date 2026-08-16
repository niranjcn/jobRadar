"""Cross-reference the 100-company list against existing sources and probe
the missing companies' career sites to detect ATS type.
"""

import json
import re
from urllib.parse import urlparse

import httpx

from app.config import load_settings
from app.db import query

COMPANIES = [
    ("Google", "https://www.google.com/about/careers/applications/"),
    ("Apple", "https://www.apple.com/careers/"),
    ("Microsoft", "https://careers.microsoft.com/"),
    ("Amazon", "https://www.amazon.jobs/"),
    ("Meta", "https://www.metacareers.com/"),
    ("Netflix", "https://jobs.netflix.com/"),
    ("IBM", "https://www.ibm.com/careers/"),
    ("Intel", "https://www.intel.com/content/www/us/en/jobs/jobs-at-intel.html"),
    ("AMD", "https://careers.amd.com/"),
    ("Oracle", "https://www.oracle.com/careers/"),
    ("SAP", "https://jobs.sap.com/"),
    ("Cisco", "https://jobs.cisco.com/"),
    ("HP", "https://careers.hp.com/"),
    ("HPE", "https://careers.hpe.com/"),
    ("Dell Technologies", "https://jobs.dell.com/"),
    ("VMware", "https://careers.broadcom.com/"),
    ("Broadcom", "https://careers.broadcom.com/"),
    ("NVIDIA", "https://www.nvidia.com/en-us/about-nvidia/careers/"),
    ("Qualcomm", "https://www.qualcomm.com/company/careers"),
    ("Micron", "https://careers.micron.com/"),
    ("Salesforce", "https://careers.salesforce.com/"),
    ("ServiceNow", "https://careers.servicenow.com/"),
    ("Atlassian", "https://www.atlassian.com/company/careers"),
    ("Intuit", "https://www.intuit.com/careers/"),
    ("Autodesk", "https://www.autodesk.com/careers"),
    ("OpenText", "https://careers.opentext.com/"),
    ("Synopsys", "https://careers.synopsys.com/"),
    ("Cadence", "https://www.cadence.com/en_US/home/company/careers.html"),
    ("Siemens", "https://jobs.siemens.com/"),
    ("Red Hat", "https://www.redhat.com/en/jobs"),
    ("OpenAI", "https://openai.com/careers/"),
    ("Anthropic", "https://www.anthropic.com/careers"),
    ("Cohere", "https://cohere.com/careers"),
    ("Mistral AI", "https://mistral.ai/careers"),
    ("Perplexity AI", "https://www.perplexity.ai/careers"),
    ("Scale AI", "https://scale.com/careers"),
    ("Hugging Face", "https://huggingface.co/jobs"),
    ("Together AI", "https://www.together.ai/careers"),
    ("Cognition AI", "https://cognition.ai/careers"),
    ("Poolside", "https://poolside.ai/careers"),
    ("Stripe", "https://stripe.com/jobs"),
    ("PayPal", "https://www.paypal.com/careers"),
    ("Visa", "https://corporate.visa.com/en/careers.html"),
    ("Mastercard", "https://careers.mastercard.com/"),
    ("American Express", "https://www.americanexpress.com/careers/"),
    ("JPMorgan Chase", "https://careers.jpmorgan.com/"),
    ("Goldman Sachs", "https://www.goldmansachs.com/careers/"),
    ("Morgan Stanley", "https://www.morganstanley.com/careers"),
    ("Wells Fargo", "https://www.wellsfargojobs.com/"),
    ("Bank of America", "https://careers.bankofamerica.com/"),
    ("Palo Alto Networks", "https://jobs.paloaltonetworks.com/"),
    ("CrowdStrike", "https://www.crowdstrike.com/careers/"),
    ("Fortinet", "https://www.fortinet.com/corporate/careers"),
    ("Check Point", "https://careers.checkpoint.com/"),
    ("SentinelOne", "https://www.sentinelone.com/jobs/"),
    ("Rapid7", "https://careers.rapid7.com/"),
    ("Trellix", "https://careers.trellix.com/"),
    ("Sophos", "https://www.sophos.com/careers"),
    ("Cloudflare", "https://www.cloudflare.com/careers/"),
    ("Okta", "https://www.okta.com/company/careers/"),
    ("HashiCorp", "https://www.hashicorp.com/careers"),
    ("Datadog", "https://www.datadoghq.com/careers/"),
    ("Elastic", "https://www.elastic.co/careers"),
    ("Confluent", "https://careers.confluent.io/"),
    ("MongoDB", "https://www.mongodb.com/careers"),
    ("Snowflake", "https://careers.snowflake.com/"),
    ("Redis", "https://redis.com/company/careers/"),
    ("Grafana Labs", "https://grafana.com/about/careers/"),
    ("DigitalOcean", "https://www.digitalocean.com/careers"),
    ("Akamai", "https://www.akamai.com/careers"),
    ("Texas Instruments", "https://careers.ti.com/"),
    ("Applied Materials", "https://careers.appliedmaterials.com/"),
    ("Lam Research", "https://careers.lamresearch.com/"),
    ("KLA", "https://www.kla.com/careers"),
    ("ASML", "https://www.asml.com/en/careers"),
    ("Arm", "https://careers.arm.com/"),
    ("Western Digital", "https://careers.westerndigital.com/"),
    ("Seagate", "https://careers.seagate.com/"),
    ("Marvell", "https://www.marvell.com/company/careers.html"),
    ("Synaptics", "https://www.synaptics.com/company/careers"),
    ("Tesla", "https://www.tesla.com/careers"),
    ("SpaceX", "https://www.spacex.com/careers/"),
    ("Blue Origin", "https://www.blueorigin.com/careers"),
    ("Rivian", "https://careers.rivian.com/"),
    ("Lucid Motors", "https://lucidmotors.com/careers"),
    ("Boeing", "https://jobs.boeing.com/"),
    ("RTX", "https://careers.rtx.com/"),
    ("Lockheed Martin", "https://www.lockheedmartinjobs.com/"),
    ("Northrop Grumman", "https://www.northropgrumman.com/careers/"),
    ("General Motors", "https://careers.gm.com/"),
    ("Accenture", "https://www.accenture.com/careers"),
    ("Capgemini", "https://jobs.capgemini.com/"),
    ("Cognizant", "https://careers.cognizant.com/"),
    ("Infosys", "https://www.infosys.com/careers/"),
    ("TCS", "https://www.tcs.com/careers"),
    ("Wipro", "https://careers.wipro.com/"),
    ("HCLTech", "https://www.hcltech.com/careers"),
    ("Tech Mahindra", "https://careers.techmahindra.com/"),
    ("Persistent Systems", "https://careers.persistent.com/"),
    ("Iris Software", "https://www.irissoftware.com/careers/"),
]

GREENHOUSE = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
LEVER = "https://api.lever.co/v0/postings/{slug}?mode=json"
ASHBY = "https://api.ashbyhq.com/posting-api/job-board/{slug}"


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def detect_from_url(url: str) -> str | None:
    host = urlparse(url).hostname or ""
    if "myworkdayjobs.com" in host:
        return "workday"
    if "oraclecloud.com" in host or "oraclecloud.net" in host or "taleo.net" in host or host == "careers.oracle.com":
        return "oracle"
    return None


def main() -> None:
    s = load_settings()
    rows = query(s, "select company_name, ats_type, board_identifier, active from sources")
    existing = {r["company_name"].lower(): r for r in rows}

    existing_found = []
    missing = []
    for name, url in COMPANIES:
        key = name.lower()
        row = existing.get(key)
        if row:
            existing_found.append((name, row["ats_type"], row["board_identifier"]))
        else:
            missing.append((name, url))

    print("=== ALREADY EXIST ===")
    for name, ats, board in existing_found:
        print(f"{name} | {ats} | {board}")

    print("\n=== MISSING (to probe) ===")
    for name, url in missing:
        print(f"{name} | {url}")


if __name__ == "__main__":
    main()