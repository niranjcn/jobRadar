"""Reconcile failed companies: probe candidate board tokens across ATS platforms.

For each company whose configured source failed, derive candidate slugs from the
name/domain and probe greenhouse/ashby/lever/workable endpoints (single request
each, no pagination). Reports the first provider+token that returns 200 with jobs.
"""

import asyncio
import json
import re
from pathlib import Path

import httpx

SOURCES_FILE = Path(__file__).resolve().parent / "sources.json"
ENDPOINTS = {
    "greenhouse": "https://boards-api.greenhouse.io/v1/boards/{t}/jobs",
    "ashby": "https://api.ashbyhq.com/posting-api/job-board/{t}",
    "workable": "https://apply.workable.com/api/v1/widget/accounts/{t}?details=true",
    "lever": "https://api.lever.co/v0/postings/{t}?mode=json",
}

FAILED = [
    "OpenAI","HashiCorp","Ramp","Plaid","Canva","Notion","Rippling","Hugging Face",
    "Weights & Biases","Confluent","Circle","Miro","Grammarly","Zapier","GitHub",
    "Netflix","Lyft","DoorDash","Faire","Flexport","Lattice","Webflow","Sourcegraph",
    "Mux","PlanetScale","Snyk","Remote","Oura","Anduril","Patreon","Intercom",
    "Fivetran","dbt Labs","LaunchDarkly","Cohere","Grubhub","Airtable","CircleCI",
    "Loom","Drift","Replicate","Together AI","Mistral AI","Anysphere","Retool",
    "Glean","Tailscale",
]


def candidate_tokens(name: str) -> list[str]:
    base = name.lower().replace("&", "").replace("+", "").replace(",", "").replace("-", "").replace(" ", "")
    base = re.sub(r"[^a-z0-9]", "", base)
    tokens = {base}
    known = {
        "openai": ["openai"],
        "ramp": ["ramp"],
        "notion": ["makenotion", "notion"],
        "canva": ["canva"],
        "plaid": ["plaid"],
        "rippling": ["rippling"],
        "zapier": ["zapier"],
        "github": ["github"],
        "miro": ["miro"],
        "grammarly": ["grammarly"],
        "confluent": ["confluent"],
        "circle": ["circle"],
        "hashicorp": ["hashicorp", "hc"],
        "webflow": ["webflow"],
        "remote": ["remotecom"],
        "dbtlabs": ["dbtlabs", "dbt-labs"],
        "netflix": ["netflix"],
        "lyft": ["lyft"],
        "doordash": ["doordash"],
        "intercom": ["intercom"],
        "airtable": ["airtable"],
        "fivetran": ["fivetran"],
    }
    tokens.update(known.get(base, []))
    return sorted(tokens)


async def probe(client: httpx.AsyncClient, provider: str, token: str) -> int:
    url = ENDPOINTS[provider].format(t=token)
    r = await client.get(url)
    if r.status_code != 200:
        return 0
    try:
        data = r.json()
    except Exception:
        return 0
    if provider == "greenhouse" and isinstance(data, dict):
        return len(data.get("jobs") or [])
    if provider == "lever" and isinstance(data, list):
        return len(data)
    if provider == "ashby" and isinstance(data, dict):
        return len(data.get("jobs") or [])
    if provider == "workable" and isinstance(data, dict):
        n = len(((data.get("jobs") or []) + (data.get("applyJobs") or [])))
        return n
    return 0


async def main() -> None:
    async with httpx.AsyncClient(timeout=15.0) as client:
        for name in FAILED:
            found = None
            for token in candidate_tokens(name):
                for provider in ("greenhouse", "ashby", "workable", "lever"):
                    try:
                        n = await probe(client, provider, token)
                    except Exception:
                        continue
                    if n and n > 0:
                        found = (provider, token, n)
                        break
                if found:
                    break
            if found:
                print(f"{name:<20} -> {found[0]}:{found[1]} ({found[2]} jobs)")
            else:
                print(f"{name:<20} -> NO MATCH across candidates")


if __name__ == "__main__":
    asyncio.run(main())