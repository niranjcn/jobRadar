import httpx
import re

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125"}
c = httpx.Client(timeout=20.0, headers=headers, follow_redirects=True)

print("=== Rapid7 ===")
for url in ["https://careers.rapid7.com/", "https://rapid7.com/company/careers/"]:
    try:
        r = c.get(url)
        txt = r.text
        for pat, label in [
            (r"boards-api\.greenhouse\.io/v1/boards/([a-zA-Z0-9\-]+)", "greenhouse"),
            (r"jobs\.lever\.co/([a-zA-Z0-9\-]+)", "lever"),
            (r"api\.ashbyhq\.com/posting-api/job-board/([a-zA-Z0-9\-\.]+)", "ashby"),
            (r"myworkdayjobs\.com", "workday"),
            (r"icims\.com", "icims"),
            (r"oraclecloud|taleo", "oracle"),
            (r"smartrecruiters", "smartrecruiters"),
            (r"jobs\.greenhouse\.io", "greenhouse-jobs"),
        ]:
            m = re.findall(pat, txt, re.I)
            if m:
                print(f"  {label}: {m[:3]}")
        print(f"  status={r.status_code} host={r.url.host}")
    except httpx.HTTPError as e:
        print(f"  {type(e).__name__}")

print("=== Redis ===")
for url in ["https://redis.com/company/careers/", "https://redis.io/careers/"]:
    try:
        r = c.get(url)
        txt = r.text
        print(f"  status={r.status_code} host={r.url.host}")
        for pat, label in [
            (r"boards-api\.greenhouse\.io/v1/boards/([a-zA-Z0-9\-]+)", "greenhouse"),
            (r"jobs\.lever\.co/([a-zA-Z0-9\-]+)", "lever"),
            (r"api\.ashbyhq\.com/posting-api/job-board/([a-zA-Z0-9\-\.]+)", "ashby"),
            (r"myworkdayjobs\.com", "workday"),
            (r"icims\.com", "icims"),
            (r"jobs\.greenhouse\.io", "greenhouse-jobs"),
            (r"apply\.workable|workable\.com", "workable"),
        ]:
            m = re.findall(pat, txt, re.I)
            if m:
                print(f"  {label}: {m[:3]}")
    except httpx.HTTPError as e:
        print(f"  {type(e).__name__}")