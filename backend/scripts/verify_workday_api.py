import httpx

headers = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}

workday_boards = [
    ("redhat", "https://redhat.wd5.myworkdayjobs.com/en-US/jobs"),
    ("mastercard", "https://mastercard.wd1.myworkdayjobs.com/CorporateCareers"),
    ("boa", "https://ghr.wd1.myworkdayjobs.com/en-US/lateral-us"),
    ("panw", "https://paloaltonetworks.wd5.myworkdayjobs.com/en-US/panwexternalcareers"),
]


def parse_board(bi):
    from urllib.parse import urlparse
    import re

    parsed = urlparse(bi)
    host = parsed.hostname or ""
    parts = host.split(".")
    tenant, shard = parts[0], parts[1]
    segments = [s for s in (parsed.path or "/").strip("/").split("/")]
    while segments and re.match(r"^[a-z]{2}(-[A-Z]{2})?$", segments[0]):
        segments.pop(0)
    site = segments[0] if segments else "External"
    return tenant, shard, site


with httpx.Client(timeout=20.0, headers=headers) as c:
    for name, board in workday_boards:
        tenant, shard, site = parse_board(board)
        api = f"https://{tenant}.{shard}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs"
        try:
            r = c.post(api, json={"appliedFacets": {}, "limit": 1, "offset": 0, "searchText": ""})
            j = r.json()
            total = j.get("total", "?")
            print(f"{name}: {api} -> status={r.status_code} total={total}")
        except Exception as e:
            print(f"{name}: {api} -> {type(e).__name__} {e}")

    # Rapid7 and Redis real ATS
    for name, url in [("rapid7", "https://careers.rapid7.com/"), ("redis", "https://redis.com/company/careers/")]:
        try:
            r = c.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125"})
            txt = r.text
            import re

            gh = re.findall(r"boards-api\.greenhouse\.io/v1/boards/([a-zA-Z0-9\-]+)", txt)
            lv = re.findall(r"jobs\.lever\.co/([a-zA-Z0-9\-]+)", txt)
            print(f"{name}: status={r.status_code} gh_slug={gh[:2]} lever_slug={lv[:2]}")
        except httpx.HTTPError as e:
            print(f"{name}: {type(e).__name__}")