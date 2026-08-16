import httpx
import re

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/125"}

with httpx.Client(timeout=20.0, headers=headers, follow_redirects=True) as c:
    r = c.get("https://careers.rapid7.com/")
    txt = r.text
    idxs = [m.start() for m in re.finditer(r"greenhouse", txt, re.I)]
    print("greenhouse occurrences:", len(idxs))
    for i in idxs[:5]:
        print("  ...", txt[max(0, i - 120): i + 150].replace("\n", " "))

    # check known rapid7 board possibilities
    print("\npossible greenhouse slugs:")
    for slug in ["rapid7", "rapid-7", "rapid7careers"]:
        try:
            rr = c.get(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs")
            print(f"  {slug}: {rr.status_code}")
        except Exception:
            pass

    # check if the job search is elsewhere
    print("\njob links on page:")
    for m in re.findall(r'href="([^"]*job[^"]*)"', txt, re.I)[:10]:
        print("  ", m)