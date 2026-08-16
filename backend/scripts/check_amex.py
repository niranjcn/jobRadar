import httpx
import re

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125"}
c = httpx.Client(timeout=20.0, headers=headers, follow_redirects=True)
r = c.get("https://careers.americanexpress.com/en/sites/CX_1")
print("status", r.status_code, "final", r.url)
text = r.text
print("apibase:", re.search(r'data-apibaseurl="([^"]+)"', text))
print("sitenum:", re.search(r'data-sitenumber="([^"]+)"', text))
print("hcmUI in text:", "/hcmUI/" in text)
print("oraclecloud in text:", "oraclecloud" in text.lower())