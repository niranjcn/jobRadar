"""Verify final board identifiers for batch-1 adds before inserting."""

import httpx

GREENHOUSE = "https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
LEVER = "https://api.lever.co/v0/postings/{slug}?mode=json"
ASHBY = "https://api.ashbyhq.com/posting-api/job-board/{slug}"

CHECKS = [
    ("greenhouse-rapid7", GREENHOUSE.format(slug="rapid7")),
    ("greenhouse-rapid7-2", GREENHOUSE.format(slug="rapidseven")),
    ("lever-redis", LEVER.format(slug="redis")),
    ("lever-redislabs", LEVER.format(slug="redislabs")),
    ("workday-redhat", "https://redhat.wd3.myworkdayjobs.com/en-US/RedHat"),
    ("workday-redhat2", "https://redhat.wd1.myworkdayjobs.com/RedHat"),
    ("workday-mastercard", "https://mastercard.wd1.myworkdayjobs.com/en-US/Careers"),
    ("workday-mastercard2", "https://careers.mastercard.com/us/en"),
    ("workday-boa", "https://bankofamerica.wd1.myworkdayjobs.com/en-US/BankofAmerica"),
    ("workday-boa2", "https://careers.bankofamerica.com/en-us"),
    ("workday-panw", "https://paloaltonetworks.wd1.myworkdayjobs.com/en-US/External"),
    ("workday-panw2", "https://jobs.paloaltonetworks.com/en"),
    ("oracle-amex", "https://careers.americanexpress.com/en/sites/CX_1"),
    ("ashby-snowflake", ASHBY.format(slug="snowflake")),
    ("ashby-perplexity", ASHBY.format(slug="perplexity")),
    ("ashby-cognition", ASHBY.format(slug="cognition")),
    ("ashby-mistral", ASHBY.format(slug="mistral.ai")),
    ("gh-mongodb", GREENHOUSE.format(slug="mongodb")),
    ("gh-spacex", GREENHOUSE.format(slug="spacex")),
    ("gh-lucid", GREENHOUSE.format(slug="lucidmotors")),
    ("gh-tcs", GREENHOUSE.format(slug="tcs")),
    ("lever-sophos", LEVER.format(slug="sophos")),
]

with httpx.Client(timeout=15.0, follow_redirects=True) as c:
    for name, url in CHECKS:
        try:
            r = c.get(url)
            body = r.text[:200].replace("\n", " ")
            print(f"{name}: status={r.status_code} host={r.url.host}")
        except httpx.HTTPError as e:
            print(f"{name}: {type(e).__name__}")