"""Location -> country mapping.

Maps a raw job location string (e.g. "Remote - Germany", "Bengaluru, India",
"SF, NYC, SEA, CHI") to a list of ISO2 country codes plus a remote flag.

Precedence (high to low):
    1. custom aliases configured in the app settings
    2. explicit country name / ISO code mention
    3. state name
    4. city name (curated overrides first, then the dr5hn index)

The bundled index is generated from
https://github.com/dr5hn/countries-states-cities-database via
backend/scripts/build_geo_index.py
"""

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

INDEX_PATH = Path(__file__).resolve().parent / "data" / "geo_index.json"

# Region/ambiguous words that should never resolve to a country by city match.
REGION_WORDS = {"amer", "emea", "apac", "latam", "mena"}

# Major US cities that beat the noisy raw index. The dr5hn database maps loose
# matches like "portland"/"phoenix" to an obscure parish/island elsewhere (JM/KI),
# but in job postings these overwhelmingly mean the US city.
TOP_US_CITIES = {
    "albany",
    "albuquerque",
    "anaheim",
    "anchorage",
    "arlington",
    "atlanta",
    "austin",
    "bakersfield",
    "baltimore",
    "baton rouge",
    "birmingham",
    "boston",
    "buffalo",
    "chandler",
    "charlotte",
    "chicago",
    "cincinnati",
    "cleveland",
    "colorado springs",
    "columbus",
    "corpus christi",
    "dallas",
    "denver",
    "detroit",
    "el paso",
    "fort worth",
    "fresno",
    "honolulu",
    "houston",
    "indianapolis",
    "jacksonville",
    "kansas city",
    "las vegas",
    "long beach",
    "los angeles",
    "louisville",
    "memphis",
    "mesa",
    "miami",
    "milwaukee",
    "minneapolis",
    "nashville",
    "new orleans",
    "new york",
    "newark",
    "oakland",
    "oklahoma city",
    "omaha",
    "orlando",
    "philadelphia",
    "phoenix",
    "pittsburgh",
    "portland",
    "raleigh",
    "riverside",
    "sacramento",
    "salt lake city",
    "san antonio",
    "san diego",
    "san francisco",
    "san jose",
    "seattle",
    "st. louis",
    "st paul",
    "stockton",
    "tampa",
    "tucson",
    "tulsa",
    "virginia beach",
    "washington",
    "wichita",
}

# US state/territory abbreviations collide with ISO2 country codes ("CA" is
# California OR Canada, "IN" is Indiana OR India). Job listings overwhelmingly
# use these as US states, so we never treat them as country codes and instead
# let city/state matching resolve them to the US.
US_STATE_CODES = {
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "DC",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
}

REMOTE_WORDS = (
    "remote",
    "anywhere",
    "worldwide",
    "global",
    "work from home",
    "wfh",
    "virtual",
    "home office",
    "100% remote",
    "fully remote",
)

# Curated fixes for the raw index: city names that collide with other countries
# or that are English aliases. Value is the ISO2 the city belongs to.
CITY_OVERRIDES: dict[str, str] = {
    "toronto": "CA",
    "paris": "FR",
    "london": "GB",
    "dublin": "IE",
    "cairo": "EG",
    "us": "US",
    "uk": "GB",
    "san francisco": "US",
    "san jose": "US",
    "los angeles": "US",
    "san diego": "US",
    "salt lake city": "US",
    "las vegas": "US",
    "new york": "US",
    "boston": "US",
    "portland": "US",
    "miami": "US",
    "phoenix": "US",
    "dallas": "US",
    "cleveland": "US",
    "sacramento": "US",
    "charlotte": "US",
    "philadelphia": "US",
    "houston": "US",
    "united states": "US",
    "bangalore": "IN",
    "bengaluru": "IN",
    "blr": "IN",
    "bombay": "IN",
    "mumbai": "IN",
    "hyderabad": "IN",
    "hyd": "IN",
    "calcutta": "IN",
    "kolkata": "IN",
    "lucknow": "IN",
    "goa": "IN",
    "salem": "IN",
    "kochi": "IN",
    "cochin": "IN",
    "mangalore": "IN",
    "mysore": "IN",
    "gurgaon": "IN",
    "gurugram": "IN",
    "ncr": "IN",
    "new delhi": "IN",
    "delhi": "IN",
    "pune": "IN",
    "chennai": "IN",
    "madras": "IN",
    "ahmedabad": "IN",
    "chandigarh": "IN",
    "indore": "IN",
    "jaipur": "IN",
    "thiruvananthapuram": "IN",
    "trivandrum": "IN",
    "surat": "IN",
    "nagpur": "IN",
    "kanpur": "IN",
    "patna": "IN",
    "bhopal": "IN",
    "vadodara": "IN",
    "agra": "IN",
    "varanasi": "IN",
    "visakhapatnam": "IN",
    "vijayawada": "IN",
    "jamshedpur": "IN",
    "ranchi": "IN",
    "bhubaneswar": "IN",
    "guwahati": "IN",
    "panaji": "IN",
    "dehradun": "IN",
    "shimla": "IN",
    "coimbatore": "IN",
    "madurai": "IN",
    "erode": "IN",
    "tiruchirappalli": "IN",
    "puducherry": "IN",
    "noida": "IN",
    "greater noida": "IN",
    "bengaluru, india": "IN",
    "hyderabad, india": "IN",
    "delhi, india": "IN",
    "pune, india": "IN",
}

# Common metro short codes -> country. India first, then common global hubs.
SHORT_FORMS: dict[str, str] = {
    "blr": "IN",
    "hyd": "IN",
    "bom": "IN",
    "mum": "IN",
    "del": "IN",
    "ccu": "IN",
    "kol": "IN",
    "maa": "IN",
    "chn": "IN",
    "mds": "IN",
    "pnq": "IN",
    "pun": "IN",
    "ggn": "IN",
    "noi": "IN",
    "amd": "IN",
    "idr": "IN",
    "jai": "IN",
    "lko": "IN",
    "bho": "IN",
    "pat": "IN",
    "nag": "IN",
    "vns": "IN",
    "agr": "IN",
    "cmb": "IN",
    "coi": "IN",
    "goi": "IN",
    "trv": "IN",
    "cok": "IN",
    "vsk": "IN",
    "vtm": "IN",
    "nyc": "US",
    "ny": "US",
    "sf": "US",
    "sfo": "US",
    "la": "US",
    "lax": "US",
    "chi": "US",
    "sea": "US",
    "atx": "US",
    "bos": "US",
    "dal": "US",
    "hou": "US",
    "phx": "US",
    "den": "US",
    "mia": "US",
    "atl": "US",
    "dc": "US",
    "lon": "GB",
    "lhr": "GB",
    "dub": "AE",
    "dxb": "AE",
    "auh": "AE",
    "sg": "SG",
    "hk": "HK",
    "hkg": "HK",
    "tokyo": "JP",
    "tyo": "JP",
    "syd": "AU",
    "mel": "AU",
    "blr/hyd": "IN",
    "blr,hyd": "IN",
}

DEFAULT_SETTINGS: dict[str, Any] = {
    "enabled": True,
    "remote_to": ["IN"],
    "custom_aliases": {},
}

SETTINGS_KEY = "location_mapping"


@lru_cache(maxsize=1)
def load_geo_index() -> dict[str, dict[str, str]]:
    if not INDEX_PATH.exists():
        return {"countries": {}, "states": {}, "cities": {}}
    with open(INDEX_PATH, encoding="utf-8") as f:
        return json.load(f)


def country_stored_variants(values: list[str]) -> list[str]:
    """Every stored spelling a selected country value can take.

    The jobs table mixes ISO codes ("IN") and full names ("India"), so any
    country comparison must accept both forms. Unknown values pass through
    uppercased. Pure.
    """
    try:
        names = load_geo_index().get("countries") or {}
    except Exception:
        names = {}
    code_to_name = {str(code).upper(): str(name) for name, code in names.items()}
    variants: list[str] = []
    for raw in values:
        text = (raw or "").strip()
        if not text:
            continue
        candidates = {text.upper(), text.title()}
        code = names.get(text.lower())
        if code:
            candidates.add(str(code).upper())
        full_name = code_to_name.get(text.upper())
        if full_name:
            candidates.add(str(full_name).title())
        for candidate in candidates:
            if candidate not in variants:
                variants.append(candidate)
    return variants


def _country_hints(index: dict[str, dict[str, str]], settings: dict[str, Any]) -> tuple[dict, dict]:
    custom = {
        str(k).lower(): str(v).upper() for k, v in (settings.get("custom_aliases") or {}).items()
    }
    return custom, {}


def _tokenize(text: str) -> list[str]:
    return [t.lower() for t in re.split(r"[,\-/|()&\s]+", text) if t]


def _raw_tokens(text: str) -> list[str]:
    return [t for t in re.split(r"[,\-/|()&\s]+", text) if t]


def _compile(names: list[str]) -> re.Pattern:
    names = sorted(names, key=len, reverse=True)
    return re.compile(r"\b(" + "|".join(re.escape(n) for n in names) + r")\b")


@lru_cache(maxsize=1)
def _patterns() -> dict[str, re.Pattern]:
    """Compiled alternation regexes so each job does ~3 regex scans instead of
    130k+ dict iterations (countries 250, states 5106)."""
    idx = load_geo_index()
    return {
        "countries": _compile(list(idx["countries"])),
        "states": _compile(list(idx["states"])),
    }


def _best_matches(
    normalized: str, pattern: re.Pattern, name_to_code: dict[str, str]
) -> dict[str, str]:
    """Return name->code pairs that match, dropping names that are substrings
    of a longer matching name (e.g. "york" inside "new york", "ireland"
    inside "northern ireland")."""
    found = set(pattern.findall(normalized))
    matched = {name: name_to_code[name] for name in found}
    keep = {}
    for name, code in matched.items():
        if any(len(other) > len(name) and name in other for other in matched):
            continue
        keep[name] = code
    return keep


@lru_cache(maxsize=1)
def _city_phrases() -> dict[str, str]:
    """Multi-word city names plus curated overrides, with overrides winning on
    collisions (e.g. the raw index maps "san francisco" to a smaller AR city,
    but we want the US one)."""
    multi = {k: v for k, v in load_geo_index()["cities"].items() if " " in k}
    return {**multi, **CITY_OVERRIDES}


@lru_cache(maxsize=1)
def _city_phrase_map() -> dict[str, list[str]]:
    """Index of multi-word city names by their first token, so phrase matching
    is O(candidates) per token instead of scanning all 42k names."""
    by_first: dict[str, list[str]] = {}
    for name in _city_phrases():
        by_first.setdefault(name.split()[0], []).append(name)
    for names in by_first.values():
        names.sort(key=len, reverse=True)
    return by_first


def map_location(location: str | None, settings: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return {"countries": [iso2...], "is_remote": bool, "matched": [...], "source": "..."}."""
    settings = {**DEFAULT_SETTINGS, **(settings or {})}
    if not settings.get("enabled", True) or not location:
        return {"countries": [], "is_remote": False, "matched": [], "source": "none"}

    index = load_geo_index()
    normalized = location.lower().strip()
    tokens = _tokenize(normalized)
    raw_tokens = _raw_tokens(location.strip())

    is_remote = any(word in normalized for word in REMOTE_WORDS)

    matched: list[str] = []
    countries: list[str] = []

    def _add(code: str, what: str) -> None:
        code = code.upper()
        if code not in countries:
            countries.append(code)
        if what not in matched:
            matched.append(what)

    # 1. custom aliases
    for alias, code in (settings.get("custom_aliases") or {}).items():
        if alias.lower() in normalized:
            _add(code, f"alias:{alias}")
    if countries:
        return {
            "countries": countries,
            "is_remote": is_remote,
            "matched": matched,
            "source": "alias",
        }

    # 2. explicit country name mention. A US state code (uppercase "GA") next to
    # a country name disambiguates name collisions like "Georgia" (state vs the
    # country); the state scan below resolves those to the US.
    patterns = _patterns()
    raw_codes = {t.upper() for t in raw_tokens}
    has_us_state_code = bool(raw_codes & US_STATE_CODES)
    us_hint = has_us_state_code or bool(raw_codes & {"US", "USA"})
    for name, code in _best_matches(normalized, patterns["countries"], index["countries"]).items():
        if us_hint and code in ("GE",):
            continue
        _add(code, name)
    # 2b. ISO2/ISO3 codes written in all caps (US, AE, GBR...). US state
    # abbreviations are excluded so "CA" in "San Francisco, CA" resolves to the
    # US via the city/state below, not to Canada.
    iso_set = set(index["countries"].values())
    for token in raw_tokens:
        upper = token.upper()
        if token == upper and 2 <= len(token) <= 3 and upper in iso_set:
            if upper in US_STATE_CODES:
                continue
            _add(upper, token)
    if countries:
        return {
            "countries": countries,
            "is_remote": is_remote,
            "matched": matched,
            "source": "country",
        }

    # 3. state name. Skip non-US "state" matches that name a major US city: the
    # dr5hn states table contains parishes/islands ("portland" -> JM, "phoenix"
    # -> KI) that are almost certainly the US city in a job posting. Real
    # provinces (Maharashtra, Bavaria, Ontario) are unaffected.
    for name, code in _best_matches(normalized, patterns["states"], index["states"]).items():
        if code != "US" and name in TOP_US_CITIES:
            continue
        _add(code, f"state:{name}")
    if countries:
        return {
            "countries": countries,
            "is_remote": is_remote,
            "matched": matched,
            "source": "state",
        }

    # 4. city name / short forms. Precedence inside this step:
    #      multi-word names  ->  curated overrides/short forms  ->  US state code  ->  raw index
    #    A US state code ("MA" in "Boston, MA") wins over the raw index, which
    #    maps "boston" to the Philippines. But curated overrides win over the
    #    state code, so "Toronto, CA" resolves to Canada, not the US.
    phrase_map = _city_phrase_map()
    for token in tokens:
        if token in REGION_WORDS:
            continue
        for phrase in phrase_map.get(token, ()):
            if phrase in normalized:
                _add(_city_phrases()[phrase], f"city:{phrase}")
                break
        if countries:
            break
    for token in tokens:
        if token in REGION_WORDS:
            continue
        override = CITY_OVERRIDES.get(token) or SHORT_FORMS.get(token)
        if override:
            _add(override, f"city:{token}")
            continue
        if token in TOP_US_CITIES:
            _add("US", f"city:{token}")
    if countries:
        return {
            "countries": countries,
            "is_remote": is_remote,
            "matched": matched,
            "source": "city",
        }
    state_codes = {t.upper() for t in raw_tokens if t.isupper() and t.upper() in US_STATE_CODES}
    if state_codes:
        _add("US", f"state:{sorted(state_codes)}")
        return {
            "countries": countries,
            "is_remote": is_remote,
            "matched": matched,
            "source": "state",
        }
    for token in tokens:
        if token in REGION_WORDS:
            continue
        if token in TOP_US_CITIES:
            _add("US", f"city:{token}")
            break
        code = index["cities"].get(token)
        if code:
            _add(code, f"city:{token}")
            break

    # 5. remote-only fallback
    if is_remote and not countries and settings.get("remote_to"):
        for code in settings["remote_to"]:
            _add(code, "remote")
        return {"countries": countries, "is_remote": True, "matched": matched, "source": "remote"}

    return {
        "countries": countries,
        "is_remote": is_remote,
        "matched": matched,
        "source": "city" if countries else "none",
    }


def resolve_preference_location(
    location: str, settings: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Resolve a preference location entry the same way jobs are mapped."""
    return map_location(location, settings)


def location_matches_preference(
    job_countries: list[str], job_is_remote: bool, pref: str, settings: dict[str, Any] | None = None
) -> bool:
    """Country-aware matching used by the matcher (see matcher.py)."""
    p = pref.strip().lower()
    if p in ("remote", "work from home", "wfh", "anywhere", "worldwide", "global"):
        return bool(job_is_remote)
    mapped = map_location(pref, settings)
    codes = mapped["countries"]
    if not codes:
        return False
    return bool(set(codes) & set(job_countries))


def map_job_locations(
    location_name: str | None,
    office_names: list[str],
    settings: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Map the combined location + offices of a job detail into countries.

    Office names on Greenhouse/Lever/Ashby details are usually more precise
    ("Paris, France", "US", "Remote - Germany"); combining them with the list
    location string gives a better country snapshot than the list alone, which
    helps remove false positives when a detail is fetched later.
    """
    countries: list[str] = []
    is_remote = False
    combined = " ".join([location_name or "", *(office_names or [])])
    by_office = map_location(" ".join(office_names), settings) if office_names else {}
    by_location = map_location(location_name, settings) if location_name else {}
    for part in (by_office, by_location):
        for code in part.get("countries", []):
            if code not in countries:
                countries.append(code)
        if part.get("is_remote"):
            is_remote = True
    if not countries and is_remote and settings:
        countries = list(settings.get("remote_to") or [])
    return {"countries": countries, "is_remote": is_remote, "raw": combined}
