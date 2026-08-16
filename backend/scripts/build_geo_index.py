"""Build a compact geo index from the dr5hn/countries-states-cities-database.

Downloads the prebuilt JSON snapshots from GitHub and writes
backend/app/data/geo_index.json containing:

  {
    "countries": { "<lower name>": "<iso2>", ... },
    "states":    { "<lower name>": "<iso2>", ... },
    "cities":    { "<lower name>": "<iso2>", ... },
  }

City names are matched globally; because city names collide across countries
(Paris, Portland, Hyderabad...) the first country that appears for a name wins.
This is intentionally a rough heuristic - the runtime mapper prefers explicit
country/state hints and only falls back to city matching.

Run from backend/:
    python scripts/build_geo_index.py
"""

import json
import urllib.request
from pathlib import Path

BASE = "https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/json/"
OUT = Path(__file__).resolve().parent.parent / "app" / "data" / "geo_index.json"


def _download(name: str) -> list[dict]:
    url = BASE + name
    print(f"downloading {name} ...")
    with urllib.request.urlopen(url, timeout=180) as res:
        return json.loads(res.read())


def main() -> None:
    countries_meta = _download("countries.json")
    countries_cities = _download("countries+cities.json")
    states = _download("states.json")

    iso2_by_name: dict[str, str] = {
        c["name"].lower(): c["iso2"] for c in countries_meta
    }

    countries: dict[str, str] = {}
    for lower, iso2 in iso2_by_name.items():
        countries[lower] = iso2

    states_out: dict[str, str] = {}
    for s in states:
        iso2 = s["country_code"]
        states_out[s["name"].lower()] = iso2

    # cities live inside each country blob (plain strings)
    cities: dict[str, str] = {}
    for c in countries_cities:
        iso2 = iso2_by_name.get(c["name"].lower())
        if not iso2:
            continue
        for city in c.get("cities", []):
            key = city.lower()
            if key and key not in cities:
                cities[key] = iso2

    payload = {
        "countries": countries,
        "states": states_out,
        "cities": cities,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    print(
        f"wrote {OUT}  "
        f"({len(countries)} countries, {len(states_out)} states, {len(cities)} cities)"
    )


if __name__ == "__main__":
    main()
