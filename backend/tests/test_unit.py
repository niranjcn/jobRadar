"""Unit tests that don't touch the network or DB."""

import os
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("JOBRADAR_DISABLE_SCHEDULER", "1")
os.environ.setdefault("JOBRADAR_DISABLE_BOT", "1")

from app.main import _interval_seconds_to_cron
from app.matcher import compute_match_score, job_matches_preferences
from app.geo import map_location, location_matches_preference, map_job_locations
from app.telegram.messages import build_html, build_text, build_text_sections, build_text_summary
from app.adapters.oracle import OracleAdapter, _is_fusion
from app.adapters.icims import IcimsAdapter
from app.api.detect import _detect_from_url
from app.poller import dedupe_rows

FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.mark.parametrize(
    "seconds,expected",
    [
        (3600, "0 */1 * * *"),
        (7200, "0 */2 * * *"),
        (1800, "*/30 * * * *"),
        (900, "*/15 * * * *"),
        (45, "* * * * *"),
    ],
)
def test_cron_conversion(seconds, expected):
    assert _interval_seconds_to_cron(seconds) == expected


def test_match_preferences_and_score():
    job = {
        "title": "Backend Software Engineer",
        "description": "Python AWS PostgreSQL",
        "location": "Dubai",
        "company_name": "Adobe",
    }
    prefs = {
        "roles": ["backend", "software engineer"],
        "keywords": ["python", "aws"],
        "locations": ["dubai"],
        "seniority": [],
        "excluded_companies": [],
    }
    matched, reasons = job_matches_preferences(job, prefs)
    assert matched is True
    assert any("role:" in r for r in reasons)
    assert any("keyword:" in r for r in reasons)
    assert any("location:" in r for r in reasons)
    score = compute_match_score(job, prefs)
    assert score == 100  # 3/3 categories hit


def test_excluded_company_never_matches():
    job = {"title": "Engineer", "description": "", "location": "", "company_name": "Stripe"}
    prefs = {
        "roles": [],
        "keywords": [],
        "locations": [],
        "seniority": [],
        "excluded_companies": ["Stripe"],
    }
    matched, reasons = job_matches_preferences(job, prefs)
    assert matched is False
    assert reasons == []


def test_empty_prefs_score_100():
    job = {"title": "Anything", "description": "", "location": "", "company_name": "X"}
    prefs = {
        "roles": [],
        "keywords": [],
        "locations": [],
        "seniority": [],
        "excluded_companies": [],
    }
    assert compute_match_score(job, prefs) == 100
    matched, _ = job_matches_preferences(job, prefs)
    assert matched is True


def test_partial_score():
    job = {
        "title": "Data Engineer",
        "description": "nothing",
        "location": "London",
        "company_name": "X",
    }
    prefs = {
        "roles": ["backend"],
        "keywords": ["python"],
        "locations": ["dubai", "remote"],
        "seniority": [],
        "excluded_companies": [],
    }
    matched, _ = job_matches_preferences(job, prefs)
    assert matched is False  # no roles, no keywords, no location
    score = compute_match_score(job, prefs)
    assert score == 0


def test_location_alone_does_not_match_without_content_term():
    # A job hits only the location preference -> NOT a match under the new
    # semantics: location is a hard filter, but roles/keywords/seniority still
    # need to hit when configured.
    job = {
        "title": "Accountant",
        "description": "",
        "location": "Mumbai",
        "company_name": "X",
        "countries": ["IN"],
        "is_remote": False,
    }
    prefs = {
        "roles": ["software engineer"],
        "keywords": ["kubernetes"],
        "locations": ["india", "remote"],
        "seniority": ["senior"],
        "excluded_companies": [],
    }
    matched, reasons = job_matches_preferences(job, prefs)
    assert matched is False
    assert reasons == []


def test_location_must_match_when_content_hits():
    # Location India is the hard filter; within it, a role hit makes it match.
    job = {
        "title": "Backend Software Engineer",
        "description": "",
        "location": "Mumbai",
        "company_name": "X",
        "countries": ["IN"],
        "is_remote": False,
    }
    prefs = {
        "roles": ["software engineer"],
        "keywords": ["kubernetes"],
        "locations": ["india", "remote"],
        "seniority": ["senior"],
        "excluded_companies": [],
    }
    matched, reasons = job_matches_preferences(job, prefs)
    assert matched is True
    assert any("role:" in r for r in reasons)
    assert any("location:" in r for r in reasons)


def test_seniority_only_match_with_matching_location():
    # A job hits the seniority preference and the location -> match.
    job = {
        "title": "Marketing Intern",
        "description": "",
        "location": "India",
        "company_name": "X",
        "countries": ["IN"],
        "is_remote": False,
    }
    prefs = {
        "roles": ["backend"],
        "keywords": ["python"],
        "locations": ["india"],
        "seniority": ["intern"],
        "excluded_companies": [],
    }
    matched, reasons = job_matches_preferences(job, prefs)
    assert matched is True
    assert any("seniority:" in r for r in reasons)
    assert any("location:" in r for r in reasons)


def test_no_term_hit_still_rejected():
    # No category hits anything -> no match even though a category is set.
    job = {
        "title": "Sales Manager",
        "description": "",
        "location": "London",
        "company_name": "X",
        "countries": ["GB"],
        "is_remote": False,
    }
    prefs = {
        "roles": ["backend"],
        "keywords": ["python"],
        "locations": ["india"],
        "seniority": ["intern"],
        "excluded_companies": [],
    }
    matched, reasons = job_matches_preferences(job, prefs)
    assert matched is False
    assert reasons == []


# ---------- geo mapping ----------


@pytest.mark.parametrize(
    "location,expected",
    [
        ("Remote - Germany", "DE"),
        ("Bengaluru, India", "IN"),
        ("Paris, France", "FR"),
        ("Remote India", "IN"),
        ("US", "US"),
        ("Remote", "IN"),  # remote_to default -> India
        ("London", "GB"),
        ("AMER", None),
        ("Hybrid", None),
        ("In-Office", None),
    ],
)
def test_geo_map_location(location, expected):
    result = map_location(location)
    if expected is None:
        assert result["countries"] == [], location
    else:
        assert expected in result["countries"], (location, result)


@pytest.mark.parametrize(
    "loc,is_remote",
    [
        ("Remote - Germany", True),
        ("Remote India", True),
        ("Remote", True),
        ("Berlin, Germany", False),
        ("US", False),
    ],
)
def test_geo_remote_flag(loc, is_remote):
    assert map_location(loc)["is_remote"] is is_remote, loc


def test_geo_india_short_forms():
    for loc in ("BLR", "HYD", "Mumbai", "Bangalore", "Noida", "Hyderabad"):
        assert "IN" in map_location(loc)["countries"], loc


def test_geo_india_states_and_cities():
    for loc in (
        "Maharashtra",
        "Karnataka",
        "Tamil Nadu",
        "Telangana",
        "Gujarat",
        "Delhi",
        "West Bengal",
        "Uttar Pradesh",
        "Pune, Maharashtra",
        "Bengaluru",
        "Chennai",
        "Kolkata",
        "Ahmedabad",
        "Gurgaon, Haryana",
    ):
        assert "IN" in map_location(loc)["countries"], loc


def test_geo_us_states_and_cities():
    for loc in (
        "California",
        "Texas",
        "New York",
        "Washington",
        "Illinois",
        "Massachusetts",
        "San Francisco, CA",
        "Austin, TX",
        "New York, NY",
        "Seattle, WA",
        "Chicago, IL",
        "Atlanta, GA",
        "Mountain View, CA",
        "Boston, MA",
        "Boston",
        "CA",
        "MA",
        "Portland",
        "Phoenix",
        "Portland, OR",
    ):
        assert "US" in map_location(loc)["countries"], loc


def test_geo_world_states_and_cities():
    for loc, code in (
        ("Ontario", "CA"),
        ("Bavaria", "DE"),
        ("Dubai", "AE"),
        ("London", "GB"),
        ("Paris", "FR"),
        ("Singapore", "SG"),
        ("Berlin", "DE"),
        ("Sydney", "AU"),
        ("Toronto", "CA"),
        ("Dublin", "IE"),
        ("Tokyo", "JP"),
        ("Melbourne", "AU"),
    ):
        assert code in map_location(loc)["countries"], (loc, code)


def test_geo_us_state_code_wins_over_noisy_index_city():
    # raw index maps "boston" to the Philippines, but "Boston, MA" is the US
    assert map_location("Boston, MA")["countries"] == ["US"]


def test_geo_override_wins_over_state_code():
    # "Toronto, CA" is Canada, not California
    assert map_location("Toronto, CA")["countries"] == ["CA"]


def test_geo_lowercase_state_words_ignored():
    # "In-Office" is not Indiana; only uppercase codes count as state codes
    assert map_location("In-Office")["countries"] == []


def test_geo_custom_alias():
    settings = {"enabled": True, "remote_to": [], "custom_aliases": {"gotham": "US"}}
    result = map_location("Gotham City", settings)
    assert result["countries"] == ["US"]


def test_geo_remote_maps_to_countries():
    settings = {"enabled": True, "remote_to": ["IN"], "custom_aliases": {}}
    result = map_location("Remote", settings)
    assert result["countries"] == ["IN"]
    assert result["is_remote"] is True


def test_geo_disabled():
    settings = {"enabled": False, "remote_to": [], "custom_aliases": {}}
    result = map_location("Bengaluru, India", settings)
    assert result["countries"] == []
    assert result["is_remote"] is False


def test_location_matches_preference_country():
    assert location_matches_preference(["IN"], False, "India") is True
    assert location_matches_preference(["DE"], True, "India") is False
    assert location_matches_preference([], True, "Remote") is True
    assert location_matches_preference(["US"], False, "Remote") is False


def test_map_job_locations_offices():
    result = map_job_locations("SF, NYC, SEA, CHI", ["US", "Canada Locations"])
    assert "US" in result["countries"]
    assert "CA" in result["countries"]


def test_match_preferences_country_aware():
    job = {
        "title": "Backend Engineer",
        "description": "Python",
        "location": "Bengaluru",
        "company_name": "Stripe",
        "countries": ["IN"],
        "is_remote": False,
    }
    prefs = {
        "roles": ["backend"],
        "keywords": ["python"],
        "locations": ["india"],
        "seniority": [],
        "excluded_companies": [],
    }
    matched, reasons = job_matches_preferences(job, prefs)
    assert matched is True
    assert any("location:" in r for r in reasons)


def test_roles_are_or_not_and():
    # Selecting multiple roles must match jobs hitting ANY single one, not all.
    roles = ["software engineer", "devops", "mts"]
    prefs = {
        "roles": roles,
        "keywords": [],
        "locations": [],
        "seniority": [],
        "excluded_companies": [],
    }

    devops_job = {
        "title": "DevOps Engineer",
        "description": "",
        "location": "",
        "company_name": "X",
    }
    mts_job = {"title": "MTS", "description": "", "location": "", "company_name": "X"}
    swe_job = {
        "title": "Senior Software Engineer",
        "description": "",
        "location": "",
        "company_name": "X",
    }
    unrelated = {
        "title": "Marketing Manager",
        "description": "",
        "location": "",
        "company_name": "X",
    }

    assert job_matches_preferences(devops_job, prefs)[0] is True
    assert job_matches_preferences(mts_job, prefs)[0] is True
    assert job_matches_preferences(swe_job, prefs)[0] is True
    assert job_matches_preferences(unrelated, prefs)[0] is False


def test_location_is_hard_filter_with_other_terms():
    # Location India is a hard filter: job must be in India AND hit a role/keyword.
    prefs = {
        "roles": ["backend"],
        "keywords": ["python"],
        "locations": ["india"],
        "seniority": [],
        "excluded_companies": [],
    }
    india_hit = {
        "title": "Backend Engineer",
        "description": "Python",
        "location": "Bengaluru, India",
        "company_name": "X",
        "countries": ["IN"],
        "is_remote": False,
    }
    india_miss = {
        "title": "Backend Engineer",
        "description": "Python",
        "location": "London",
        "company_name": "X",
        "countries": ["GB"],
        "is_remote": False,
    }
    assert job_matches_preferences(india_hit, prefs)[0] is True
    assert job_matches_preferences(india_miss, prefs)[0] is False


def test_excluded_roles_block_otherwise_matching_job():
    # "software engineer" would match "Staff Software Engineer"; excluding
    # "staff" must disqualify it while normal SWE jobs still match.
    prefs = {
        "roles": ["software engineer"],
        "keywords": [],
        "locations": [],
        "seniority": [],
        "excluded_companies": [],
        "excluded_roles": ["staff", "principal", "lead"],
    }
    staff_job = {
        "title": "Staff Software Engineer",
        "description": "",
        "location": "",
        "company_name": "X",
    }
    normal_job = {
        "title": "Software Engineer",
        "description": "",
        "location": "",
        "company_name": "X",
    }
    assert job_matches_preferences(staff_job, prefs)[0] is False
    assert job_matches_preferences(normal_job, prefs)[0] is True


def test_excluded_roles_require_nonempty_roles():
    # Excluded roles without any positive role/keyword/seniority: still honored.
    prefs = {
        "roles": [],
        "keywords": [],
        "locations": [],
        "seniority": [],
        "excluded_companies": [],
        "excluded_roles": ["intern"],
    }
    job = {
        "title": "Software Engineer Intern",
        "description": "",
        "location": "",
        "company_name": "X",
    }
    assert job_matches_preferences(job, prefs)[0] is False


# ---------- message builder ----------


def test_build_text_structured():
    jobs = [
        {
            "title": "Software Engineer",
            "company": "Adobe",
            "location": "Bengaluru, India",
            "url": "https://careers.adobe.com/1",
        },
        {
            "title": "DevOps Engineer",
            "company": "Adobe",
            "location": "Bengaluru, India",
            "url": "https://careers.adobe.com/2",
        },
        {
            "title": "Backend Engineer",
            "company": "Google",
            "location": "Remote",
            "url": "https://careers.google.com/x",
        },
    ]
    text = build_text(jobs)

    assert "3 jobs found" in text
    assert "Adobe — 2 new role(s)" in text
    assert "Google — 1 new role(s)" in text

    for job in jobs:
        assert job["title"] in text
        assert f"🏢 {job['company']}" in text
        assert f"📍 {job['location']}" in text
        assert "Apply" in text
        assert job["url"] in text


def test_build_text_sections_split_jobs():
    jobs = [
        {"title": "One", "company": "A", "location": "X", "url": "u1"},
        {"title": "Two", "company": "B", "location": "Y", "url": "u2"},
    ]
    sections = build_text_sections(jobs)
    assert sections[0].endswith("jobs found")
    assert "A — 1 new role(s)" in sections
    # every job block is its own section, never merged with another job
    assert any(s == "One\n\n🏢 A\n\n📍 X\n\nApply\n\nu1" for s in sections)
    assert any(s == "Two\n\n🏢 B\n\n📍 Y\n\nApply\n\nu2" for s in sections)


def test_build_html_escapes():
    jobs = [
        {
            "title": "<script>alert(1)</script>",
            "company": "A&B",
            "location": "X",
            "url": "https://example.com/?a=1&b=2",
        },
    ]
    html = build_html(jobs)
    assert "&lt;script&gt;" in html
    assert "A&amp;B" in html
    assert "&amp;b=2" in html


def test_build_text_summary():
    s = build_text_summary(0, 0)
    assert "New job(s) found: 0" in s
    assert "New matching job(s) found: 0" in s


def test_build_text_summary_with_counts():
    s = build_text_summary(5, 2)
    assert "New job(s) found: 5" in s
    assert "New matching job(s) found: 2" in s


def test_build_html_summary_even_when_empty():
    """A run summary email is emitted even with zero new/matched jobs."""
    html = build_html([], new_jobs=0, new_matches=0)
    assert "New job(s) found: 0" in html
    assert "New matching job(s) found: 0" in html


def test_build_html_summary_with_matches():
    jobs = [
        {"title": "Engineer", "company": "Acme", "location": "Remote", "url": "https://a.example/x"}
    ]
    html = build_html(jobs, new_jobs=5, new_matches=1)
    assert "New job(s) found: 5" in html
    assert "New matching job(s) found: 1" in html
    assert "Engineer" in html
    assert "Acme" in html


def test_oracle_fusion_detection():
    assert _is_fusion(
        "https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1002/jobs"
    )
    assert _is_fusion("https://careers.oracle.com/")
    assert _is_fusion("https://careers.americanexpress.com/en/sites/CX_1")
    assert not _is_fusion("https://valero.taleo.net/careersection/2")


def test_oracle_fusion_site_root():
    assert (
        OracleAdapter._fusion_site_root(
            "https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1002/jobs"
        )
        == "https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1002"
    )
    assert (
        OracleAdapter._fusion_site_root(
            "https://hdpc.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CampusHiring/jobs"
        )
        == "https://hdpc.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CampusHiring"
    )
    assert OracleAdapter._fusion_site_root("https://careers.oracle.com/") == (
        "https://careers.oracle.com/en/sites/jobsearch"
    )
    assert OracleAdapter._fusion_site_root("https://careers.americanexpress.com/en/sites/CX_1") == (
        "https://careers.americanexpress.com/en/sites/CX_1"
    )


def test_oracle_fusion_normalize():
    job = OracleAdapter._normalize_fusion(
        "https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1002",
        "CX_1002",
        {
            "id": "12345",
            "title": "Software Engineer",
            "primaryLocation": "Bengaluru, Karnataka, India",
            "postedDate": "2026-08-13",
            "shortDescriptionStr": "Build cool things",
        },
    )
    assert job.external_job_id == "12345"
    assert job.title == "Software Engineer"
    assert job.location == "Bengaluru, Karnataka, India"
    assert job.url == (
        "https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1002/job/12345"
    )
    assert job.posted_at == "2026-08-13"
    assert job.description == "Build cool things"


def test_poller_dedupe_rows():
    rows = [
        {"external_job_id": "a", "title": "A1"},
        {"external_job_id": "a", "title": "A2"},
        {"external_job_id": "b", "title": "B"},
    ]
    result = dedupe_rows(rows)
    assert [r["external_job_id"] for r in result] == ["a", "b"]
    assert result[0]["title"] == "A1"


def test_detect_fusion_url():
    detected = _detect_from_url(
        "https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1002/jobs"
    )
    assert detected == {
        "ats_type": "oracle",
        "board_identifier": "https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1002/jobs",
    }
    detected_vanity = _detect_from_url("https://careers.oracle.com/")
    assert detected_vanity["ats_type"] == "oracle"


def _load_icims_json():
    import json

    with open(FIXTURES / "icims" / "amd_jobs.json", encoding="utf-8") as f:
        return json.load(f)


def _load_arm_html():
    with open(FIXTURES / "icims" / "arm_search_page.html", encoding="utf-8") as f:
        return f.read()


def test_icims_json_normalize():
    payload = _load_icims_json()
    assert payload["totalCount"] > 0
    job = IcimsAdapter._normalize_json(payload["jobs"][0])
    assert job.external_job_id
    assert job.title
    assert job.location
    assert job.url
    assert job.posted_at


def test_icims_json_pagination_stop():
    """page * PAGE_SIZE >= totalCount terminates pagination."""
    from app.adapters.icims import PAGE_SIZE

    payload = _load_icims_json()
    total = int(payload["totalCount"])
    last_page = (total + PAGE_SIZE - 1) // PAGE_SIZE
    assert last_page * PAGE_SIZE >= total


def test_icims_html_normalize():
    html_page = _load_arm_html()
    cards = re.findall(r"<li class=\"job-card.*?</li>", html_page, re.DOTALL)
    assert cards, "fixture must contain job cards"
    job = IcimsAdapter._normalize_html(cards[0], "https://careers.arm.com/search-jobs?k=&l=&p=1")
    assert job.external_job_id.isdigit()
    assert job.title
    assert job.location
    assert job.url and "arm.com" in job.url


def _load_wipro_json():
    import json

    with open(FIXTURES / "successfactors" / "wipro_jobs.json", encoding="utf-8") as f:
        return json.load(f)


def _load_sap_html():
    with open(FIXTURES / "successfactors" / "sap_results.html", encoding="utf-8") as f:
        return f.read()


def test_successfactors_api_normalize():
    from app.adapters.successfactors import SuccessFactorsAdapter

    payload = _load_wipro_json()
    assert payload["totalJobs"] > 0
    job = SuccessFactorsAdapter._normalize_api(
        payload["jobSearchResult"][0]["response"], "https://careers.wipro.com"
    )
    assert job.external_job_id.isdigit()
    assert job.title
    assert job.location
    assert job.url and "careers.wipro.com" in job.url
    assert "job/" in job.url
    assert job.posted_at
    assert job.countries


def test_successfactors_api_missing_location_fields():
    """HCLTech responses lack jobLocationShort; custprimecity is used."""
    from app.adapters.successfactors import SuccessFactorsAdapter

    resp = {
        "id": "71970",
        "unifiedStandardTitle": "Hunter",
        "custprimecity": "Paris",
        "custCountryRegion": ["France"],
        "urlTitle": "Hunter",
    }
    job = SuccessFactorsAdapter._normalize_api(resp, "https://careers.hcltech.com")
    assert job.external_job_id == "71970"
    assert job.title == "Hunter"
    assert job.location == "Paris"
    assert job.countries == ["France"]
    assert job.url == "https://careers.hcltech.com/job/Hunter/71970/"


def test_successfactors_api_location_has_br_stripped():
    from app.adapters.successfactors import SuccessFactorsAdapter

    resp = {
        "id": "142130",
        "unifiedStandardTitle": "TECHNO FUNCTIONAL CONSULTANT L1",
        "jobLocationShort": ["Tampa, USA-FL, USA, 33634<br/>"],
        "jobLocationCountry": ["United States"],
        "urlTitle": "TECHNO-FUNCTIONAL-CONSULTANT-L1",
    }
    job = SuccessFactorsAdapter._normalize_api(resp, "https://careers.wipro.com")
    assert "<" not in job.location
    assert job.location == "Tampa, USA-FL, USA, 33634"


def test_successfactors_html_normalize():
    from app.adapters.successfactors import SuccessFactorsAdapter

    html_page = _load_sap_html()
    table = re.search(r'<table id="searchresults".*?</table>', html_page, re.DOTALL)
    assert table, "fixture must contain the results table"
    rows = re.findall(r'<tr class="data-row">(.*?)</tr>', table.group(0), re.DOTALL)
    assert rows, "fixture must contain data rows"
    job = SuccessFactorsAdapter._normalize_html(rows[0], "https://jobs.sap.com")
    assert job.external_job_id.isdigit()
    assert job.title
    assert job.location
    assert job.url and "jobs.sap.com/job/" in job.url


def test_successfactors_api_pagination_stop():
    """(pageNumber + 1) * API_PAGE_SIZE >= totalJobs terminates pagination."""
    from app.adapters.successfactors import API_PAGE_SIZE

    payload = _load_wipro_json()
    total = int(payload["totalJobs"])
    last_page = (total + API_PAGE_SIZE - 1) // API_PAGE_SIZE
    assert last_page * API_PAGE_SIZE >= total


def _load_opentext_html():
    with open(FIXTURES / "phenom" / "opentext_search.html", encoding="utf-8") as f:
        return f.read()


def test_phenom_parse_page():
    from app.adapters.phenom import PhenomAdapter

    jobs, total = PhenomAdapter._parse_page(_load_opentext_html())
    assert total and total > 0
    assert len(jobs) > 0
    assert jobs[0]["reqId"]


def test_phenom_normalize():
    from app.adapters.phenom import PhenomAdapter

    jobs, _ = PhenomAdapter._parse_page(_load_opentext_html())
    job = PhenomAdapter._normalize(jobs[0], "https://careers.opentext.com")
    assert job.external_job_id.isdigit()
    assert job.title
    assert job.location
    assert job.url and "careers.opentext.com" in job.url
    assert "job/" in job.url
    assert job.posted_at
    assert job.countries


def test_phenom_missing_location_falls_back():
    from app.adapters.phenom import PhenomAdapter

    job = PhenomAdapter._normalize(
        {"reqId": "123", "title": "Engineer", "cityStateCountry": "Tokyo, JPN"},
        "https://careers.opentext.com",
    )
    assert job.location == "Tokyo, JPN"
    assert job.external_job_id == "123"


def test_phenom_remote_detection():
    from app.adapters.phenom import PhenomAdapter

    job = PhenomAdapter._normalize(
        {"reqId": "456", "title": "Sales", "location": "Virtual, USA", "country": "USA"},
        "https://careers.opentext.com",
    )
    assert job.is_remote
    assert job.countries == ["USA"]


def _load_siemens_html():
    with open(FIXTURES / "avature" / "siemens_search.html", encoding="utf-8") as f:
        return f.read()


def test_avature_parse_rows():
    from app.adapters.avature import AvatureAdapter

    html_page = _load_siemens_html()
    rows = __import__("re").findall(r"<article.*?</article>", html_page, re.DOTALL)
    assert rows, "fixture must contain job rows"
    job = AvatureAdapter._normalize(rows[0])
    assert job.external_job_id.isdigit()
    assert job.title
    assert "&amp;" not in job.title
    assert job.location
    assert job.url and "JobDetail/" in job.url and job.external_job_id in job.url


def test_avature_missing_fields():
    from app.adapters.avature import AvatureAdapter

    job = AvatureAdapter._normalize(
        '<article><a href="https://jobs.siemens.com/en_US/externaljobs/JobDetail/99">'
        "Engineer</a></article>"
    )
    assert job.external_job_id == "99"
    assert job.title == "Engineer"
    assert job.location is None
    assert job.url.endswith("/JobDetail/99")


def test_avature_pagination_step():
    """Pagination param detection must match the portal's pager links."""
    from app.adapters.avature import AvatureAdapter, _detect_pagination_params

    assert AvatureAdapter.fetch_jobs.__name__ == "fetch_jobs"
    assert AvatureAdapter.ats_type == "avature"
    assert _detect_pagination_params(
        '<a href="SearchJobs/?jobRecordsPerPage=6&amp;jobOffset=6">2</a>'
    ) == ("jobOffset", "jobRecordsPerPage")
    assert _detect_pagination_params(
        '<a href="SearchJobs/?folderRecordsPerPage=6&amp;folderOffset=6">2</a>'
    ) == ("folderOffset", "folderRecordsPerPage")
    assert _detect_pagination_params("<html><body>no pager</body></html>") == (None, None)


def _load_synopsys_html():
    with open(FIXTURES / "avature" / "synopsys_search.html", encoding="utf-8") as f:
        return f.read()


def test_avature_slug_url_format():
    """Boards that use JobDetail/{slug}-{id}/{id} URLs must still extract the id."""
    from app.adapters.avature import AvatureAdapter

    html_page = _load_synopsys_html()
    rows = __import__("re").findall(r"<article.*?</article>", html_page, re.DOTALL)
    assert rows, "fixture must contain job rows"
    job = AvatureAdapter._normalize(rows[0])
    assert job.external_job_id.isdigit()
    assert job.external_job_id in job.url
    assert job.title
    assert job.location is None
    assert job.posted_at is not None
    assert job.url.startswith("https://synopsys.avature.net/careers/JobDetail/")


def test_avature_detail_parse_fields():
    """fetch_job_detail must parse structured field/value blocks into a detail dict."""
    from app.adapters.avature import AvatureAdapter

    detail_html = (
        '<div class="content__view__field__label">City</div>'
        '<div class="article__content__view__field__value">Exton</div>'
        '<div class="content__view__field__label">State/Province</div>'
        '<div class="article__content__view__field__value">Pennsylvania</div>'
        '<div class="content__view__field__label">Remote Eligible</div>'
        '<div class="article__content__view__field__value">No</div>'
        '<div class="content__view__field__label">Job Description and Requirements</div>'
        '<div class="article__content__view__field__value">'
        "<p>Some description text</p>"
        "</div>"
    )

    async def fake_fetch(url):
        return type("Resp", (), {"text": detail_html, "status_code": 200})()

    detail = AvatureAdapter._parse_detail_html(detail_html)
    assert detail["location"] == "Exton, Pennsylvania"
    assert detail["remote"] == "No"
    assert "<p>" in detail["content"]


def _load_iris_tiles_html():
    with open(FIXTURES / "custom" / "iris_tiles.html", encoding="utf-8") as f:
        return f.read()


def _load_iris_detail_html():
    with open(FIXTURES / "custom" / "iris_detail.html", encoding="utf-8") as f:
        return f.read()


def test_custom_parse_tiles():
    """J2W tile rows must parse into jobs with id, title, location, url, posted_at."""
    from app.adapters.custom import CustomAdapter

    html_page = _load_iris_tiles_html()
    tiles = re.findall(r'<li[^>]*class="[^"]*job-tile[^"]*".*?</li>', html_page, re.DOTALL)
    assert len(tiles) >= 10, "fixture must contain job tiles"
    job = CustomAdapter._normalize(tiles[0], "https://careers.irissoftware.com")
    assert job.external_job_id.isdigit()
    assert job.external_job_id in (job.url or "")
    assert job.title
    assert job.location
    assert job.url and "/job/" in job.url
    assert job.url.startswith("https://careers.irissoftware.com/")
    assert job.posted_at is not None


def test_custom_parse_missing_fields():
    """A tile missing optional fields must still produce a job without crashing."""
    from app.adapters.custom import CustomAdapter

    job = CustomAdapter._normalize(
        '<li class="job-tile" data-url="/job/Foo-Engineer/123456/">'
        '<a class="jobTitle-link" href="/job/Foo-Engineer/123456/">'
        "Engineer</a></li>"
    )
    assert job.external_job_id == "123456"
    assert job.title == "Engineer"
    assert job.location is None
    assert job.url.endswith("/job/Foo-Engineer/123456/")
    assert job.posted_at is None

    absolute = CustomAdapter._normalize(
        '<li class="job-tile" data-url="/job/Foo/987/">'
        '<a class="jobTitle-link" href="/job/Foo/987/">Foo</a></li>',
        "https://careers.irissoftware.com",
    )
    assert absolute.url == "https://careers.irissoftware.com/job/Foo/987/"


def test_custom_parse_posted_date():
    from app.adapters.custom import _parse_posted

    assert _parse_posted("14 Aug 2026") == "2026-08-14T00:00:00+00:00"
    assert _parse_posted("garbage") is None
    assert _parse_posted(None) is None


def test_custom_extract_job_id():
    from app.adapters.custom import _extract_job_id

    assert _extract_job_id("/job/Noida-Mulesoft-Senior-Engineer-UP/57926844/") == "57926844"
    assert _extract_job_id("https://careers.irissoftware.com/job/Foo/12345/") == "12345"
    assert _extract_job_id("https://careers.irissoftware.com/job/Foo/12345") == "12345"
    assert _extract_job_id("/job/noid/") == ""
    assert _extract_job_id("") == ""


def test_custom_detail_not_supported():
    """J2W detail URLs need the slug, so enrichment returns None (list data is complete)."""
    from app.adapters.custom import CustomAdapter

    assert CustomAdapter().fetch_job_detail.__name__ == "fetch_job_detail"
    assert CustomAdapter.ats_type == "custom"


def test_retrying_client_retries_transient_errors():
    """A dropped connection (e.g. Server disconnected) is retried, then succeeds."""
    import asyncio
    import httpx

    from app.adapters.http import RetryingClient

    attempts = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise httpx.RemoteProtocolError("Server disconnected without sending a response.")
        return httpx.Response(200, json={"jobs": [{"id": "1", "title": "Engineer"}]})

    transport = httpx.MockTransport(handler)

    async def run():
        async with RetryingClient(transport=transport, timeout=30.0) as client:
            return await client.get("https://example.com/jobs")

    response = asyncio.run(run())
    assert response.status_code == 200
    assert response.json()["jobs"][0]["title"] == "Engineer"
    assert attempts == 2


def test_retrying_client_retries_429_then_succeeds():
    import asyncio
    import httpx

    from app.adapters.http import RetryingClient

    attempts = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return httpx.Response(429, request=request)
        return httpx.Response(200, json={})

    transport = httpx.MockTransport(handler)

    async def run():
        async with RetryingClient(transport=transport, timeout=30.0) as client:
            return await client.get("https://example.com/jobs")

    response = asyncio.run(run())
    assert response.status_code == 200
    assert attempts == 2


def test_retrying_client_does_not_retry_404():
    import asyncio
    import httpx

    from app.adapters.http import RetryingClient

    attempts = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        return httpx.Response(404, request=request)

    transport = httpx.MockTransport(handler)

    async def run():
        async with RetryingClient(transport=transport, timeout=30.0) as client:
            return await client.get("https://example.com/jobs")

    response = asyncio.run(run())
    assert response.status_code == 404
    assert attempts == 1


# ---------- telegram bot ----------


def test_bot_parse_command():
    from app.telegram.bot import parse_command

    assert parse_command("/start") == ("start", "")
    assert parse_command("/jobs python") == ("jobs", "python")
    assert parse_command("/jobs  python aws ") == ("jobs", "python aws")
    assert parse_command("/matches@JobRadarBot adobe") == ("matches", "adobe")
    assert parse_command("/HELP") == ("help", "")
    assert parse_command("not a command") == ("", "")
    assert parse_command("") == ("", "")


def test_bot_authorized():
    from app.telegram.bot import authorized

    assert authorized(123456789, _fake_settings(chat_id="123456789")) is True
    assert authorized("123456789", _fake_settings(chat_id="123456789")) is True
    assert authorized(111, _fake_settings(chat_id="123456789")) is False


def _fake_settings(chat_id: str):
    from types import SimpleNamespace

    return SimpleNamespace(telegram_chat_id=chat_id, telegram_bot_token="test-token")


def test_bot_chunk_text_single():
    from app.telegram.bot import _chunk_text

    assert _chunk_text("short message") == ["short message"]
    assert _chunk_text("") == [""]


def test_bot_chunk_text_long():
    from app.telegram.bot import _chunk_text

    text = "\n\n".join(f"section {i}" + ("x" * 100) for i in range(100))
    chunks = _chunk_text(text, max_len=500)
    assert len(chunks) > 1
    assert all(len(c) <= 500 for c in chunks)
    assert "section 0" in chunks[0]
    assert "section 99" in chunks[-1]
    assert "\n\n".join(chunks) == text


def test_bot_format_job_block():
    from app.telegram.bot import format_job_block

    text = format_job_block(
        {
            "title": "Software Engineer",
            "company_name": "Adobe",
            "location": "Bengaluru",
            "url": "https://x",
        }
    )
    assert "Software Engineer" in text
    assert "Adobe" in text
    assert "Bengaluru" in text
    assert "https://x" in text

    no_extra = format_job_block({"title": "Engineer", "company_name": "Acme"})
    assert "location" not in no_extra.lower()


def test_bot_format_job_block_score():
    from app.telegram.bot import format_job_block

    text = format_job_block(
        {"title": "Backend Engineer", "company_name": "Acme", "match_score": 92}
    )
    assert "92%" in text


def test_bot_dispatch_unknown_command():
    from app.telegram.bot import dispatch_command

    reply = dispatch_command(_fake_settings("123456789"), None, "nosuchcmd", "")
    assert "Unknown command" in reply


def test_bot_menu_markup():
    from app.telegram.bot import MENU_COMMANDS, _menu_markup

    markup = _menu_markup()
    rows = markup["inline_keyboard"]
    assert len(rows) >= 1
    buttons = [b for row in rows for b in row]
    assert len(buttons) == len(MENU_COMMANDS)
    for row in rows:
        assert len(row) <= 2
    for button in buttons:
        assert button["callback_data"].startswith("menu:")
        command = button["callback_data"].split(":", 1)[1]
        assert command in MENU_COMMANDS
        assert button["text"]


def test_bot_menu_callback_unauthorized():
    import asyncio

    from app.telegram.bot import _handle_callback

    settings = _fake_settings("123456789")

    async def run():
        calls = []

        class FakeResponse:
            status_code = 200

        class FakeClient:
            async def post(self, url, **kwargs):
                calls.append((url, kwargs.get("content")))
                return FakeResponse()

        await _handle_callback(
            settings,
            {
                "callback_query": {
                    "id": "cb-1",
                    "data": "menu:stats",
                    "message": {"chat": {"id": 999}},
                }
            },
            FakeClient(),
        )
        return calls

    calls = asyncio.run(run())
    sent = [c for c in calls if "sendMessage" in c[0]]
    assert len(sent) == 1
    assert "Not authorized." in sent[0][1]


def test_bot_menu_callback_ignores_unknown_data():
    import asyncio

    from app.telegram.bot import _handle_callback

    settings = _fake_settings("123456789")

    async def run():
        calls = []

        class FakeResponse:
            status_code = 200

        class FakeClient:
            async def post(self, url, **kwargs):
                calls.append((url, kwargs.get("content")))
                return FakeResponse()

        await _handle_callback(
            settings,
            {
                "callback_query": {
                    "id": "cb-1",
                    "data": "other:stuff",
                    "message": {"chat": {"id": 123456789}},
                }
            },
            FakeClient(),
        )
        return calls

    calls = asyncio.run(run())
    assert calls == []
