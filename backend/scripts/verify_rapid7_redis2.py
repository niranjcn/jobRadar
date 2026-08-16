import httpx

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125"}

with httpx.Client(timeout=20.0, headers=headers, follow_redirects=True) as c:
    print("=== Rapid7 careers.rapid7.com ===")
    r = c.get("https://careers.rapid7.com/")
    txt = r.text
    print(f"status={r.status_code} len={len(txt)}")
    # look for job listing URLs or API references
    import re

    urls = re.findall(r'https?://[^"\'<> ]+', txt)
    jobish = [u for u in urls if any(k in u.lower() for k in ["job", "position", "career", "api", "posting", "board"])]
    print("job-ish urls:", jobish[:15])
    for kw in ["greenhouse", "lever", "ashby", "icims", "workday", "smartrecruiters", "oracle", "taleo", "greenhouse.io"]:
        if kw in txt.lower():
            print(f"  contains: {kw}")

    print("\n=== Redis redis.io/careers ===")
    r = c.get("https://redis.io/careers/")
    txt = r.text
    print(f"status={r.status_code} len={len(txt)}")
    urls = re.findall(r'https?://[^"\'<> ]+', txt)
    jobish = [u for u in urls if any(k in u.lower() for k in ["job", "position", "career", "api", "posting", "board"])]
    print("job-ish urls:", jobish[:15])
    for kw in ["greenhouse", "lever", "ashby", "icims", "workday", "smartrecruiters", "oracle", "taleo", "lever.co", "greenhouse.io"]:
        if kw in txt.lower():
            print(f"  contains: {kw}")