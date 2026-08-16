import httpx
import re

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125"}
TARGETS = [
    ("redhat", "https://www.redhat.com/en/jobs"),
    ("mastercard", "https://careers.mastercard.com/us/en"),
    ("boa", "https://careers.bankofamerica.com/en-us"),
    ("panw", "https://jobs.paloaltonetworks.com/en"),
    ("rapid7", "https://careers.rapid7.com/"),
    ("redis", "https://redis.com/company/careers/"),
]

with httpx.Client(timeout=20.0, headers=headers, follow_redirects=True) as c:
    for name, url in TARGETS:
        try:
            r = c.get(url)
            txt = r.text
            wd = set(re.findall(r"[a-zA-Z0-9\-\.]*myworkdayjobs\.com[^\"')\s]*", txt))
            if wd:
                print(f"{name}: workday URLs -> {sorted(wd)[:3]}")
            else:
                print(f"{name}: no workday URL in page (status={r.status_code}, host={r.url.host})")
        except httpx.HTTPError as e:
            print(f"{name}: {type(e).__name__}")