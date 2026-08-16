import httpx
import re

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125"}

with httpx.Client(timeout=20.0, headers=headers, follow_redirects=True) as c:
    print("=== Rapid7 greenhouse references ===")
    r = c.get("https://careers.rapid7.com/")
    txt = r.text
    for m in re.finditer(r".{80}greenhouse.{120}", txt, re.I):
        s = m.group(0).replace("\n", " ")
        print("  ...", s[:200])

    print("\n=== Redis lever references ===")
    r = c.get("https://redis.io/company/careers/")
    txt = r.text
    for m in re.finditer(r".{80}lever.{120}", txt, re.I):
        s = m.group(0).replace("\n", " ")
        print("  ...", s[:200])