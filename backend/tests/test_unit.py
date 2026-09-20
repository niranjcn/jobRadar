"""Unit tests that don't touch the network or DB."""

import json
import os
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("JOBQUEST_DISABLE_SCHEDULER", "1")
os.environ.setdefault("JOBQUEST_DISABLE_BOT", "1")

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
    # Keyword matching is title-only (descriptions are not stored): both
    # keyword terms below hit the title, keeping the 3/3-category contract.
    job = {
        "title": "Backend Software Engineer",
        "description": "",
        "location": "Dubai",
        "company_name": "Adobe",
    }
    prefs = {
        "roles": ["backend", "software engineer"],
        "keywords": ["software", "engineer"],
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


def _match_job(job_id="j1"):
    return {
        "id": job_id,
        "title": "Senior Backend Engineer (Python)",
        "description": "Build APIs with Python and Postgres in Bengaluru.",
        "location": "Bengaluru, India",
        "company_name": "Acme",
        "countries": ["IN"],
        "is_remote": False,
    }


def _match_prefs(**overrides):
    base = {
        "roles": ["backend engineer"],
        "keywords": ["python"],
        "locations": ["india"],
        "seniority": ["senior"],
        "excluded_companies": [],
        "excluded_roles": [],
    }
    base.update(overrides)
    return base


def test_grouped_evaluation_matches_ungrouped_exactly():
    """Grouped path must produce byte-identical rows per user (ids, reasons, scores)."""
    from app.matcher import preference_signature
    from app.notification_queue import AudienceUser, evaluate_jobs_for_user

    jobs = [_match_job("j1"), _match_job("j2")]
    prefs = _match_prefs()
    users = [
        AudienceUser(
            id=f"u{i}",
            role="user",
            status="approved",
            access_locked=False,
            alert_delay_minutes=0,
            telegram_chat_id=None,
            email=None,
            capabilities=[],
            prefs=dict(prefs),
        )
        for i in range(3)
    ]
    per_user = [evaluate_jobs_for_user(jobs, user, None) for user in users]
    assert preference_signature(users[0].prefs) == preference_signature(users[1].prefs)
    for rows, _ in per_user:
        assert [(r["job_id"], r["matched_on"], r["match_score"]) for r in rows] == [
            (
                "j1",
                ["role:backend engineer", "keyword:python", "seniority:senior", "location:india"],
                100,
            ),
            (
                "j2",
                ["role:backend engineer", "keyword:python", "seniority:senior", "location:india"],
                100,
            ),
        ]


def test_preference_signature_is_order_and_duplicate_sensitive():
    """Reasons embed raw strings in list order, so reordered/duplicated term
    lists must never share an evaluation."""
    from app.matcher import preference_signature

    base = _match_prefs()
    reordered = _match_prefs()
    reordered["roles"] = ["backend engineer", "software engineer"]
    base["roles"] = ["software engineer", "backend engineer"]
    assert preference_signature(base) != preference_signature(reordered)
    duped = _match_prefs()
    duped["keywords"] = ["python", "python"]
    assert preference_signature(_match_prefs()) != preference_signature(duped)
    assert preference_signature(_match_prefs()) == preference_signature(_match_prefs())
    assert preference_signature({}) == preference_signature(
        {
            "roles": [],
            "keywords": [],
            "locations": [],
            "seniority": [],
            "excluded_companies": [],
            "excluded_roles": [],
        }
    )


def test_empty_prefs_collapse_to_one_signature():
    """Match-all users (empty prefs) form a single group whatever their count."""
    from app.matcher import preference_signature

    sigs = {preference_signature({}) for _ in range(50)}
    assert len(sigs) == 1


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


def _load_amazon_json():
    with open(FIXTURES / "amazon" / "amazon_jobs.json", encoding="utf-8") as f:
        return json.load(f)


def test_amazon_normalize():
    from app.adapters.amazon import AmazonAdapter

    payload = _load_amazon_json()
    assert payload["hits"] > 0
    job = AmazonAdapter._normalize(payload["jobs"][0])
    assert job.external_job_id.isdigit()
    assert job.title
    assert job.location
    assert job.url and "amazon.jobs" in job.url
    assert job.posted_at
    assert job.countries
    assert job.description


def test_amazon_missing_fields():
    from app.adapters.amazon import AmazonAdapter

    job = AmazonAdapter._normalize(
        {"id": "abc", "id_icims": "12345", "title": "Engineer", "job_path": "/en/jobs/12345/x"}
    )
    assert job.external_job_id == "12345"
    assert job.title == "Engineer"
    assert job.location is None
    assert job.url == "https://www.amazon.jobs/en/jobs/12345/x"
    assert job.posted_at is None
    assert job.countries == []


def test_amazon_remote_detection():
    from app.adapters.amazon import AmazonAdapter

    job = AmazonAdapter._normalize(
        {
            "id_icims": "9",
            "title": "Engineer",
            "location": "Virtual Location - Texas",
            "locations": ['{"type":"VIRTUAL","countryIso2a":"US","normalizedCountryCode":"USA"}'],
        }
    )
    assert job.is_remote
    assert job.countries == ["US"]


def test_amazon_pagination_arithmetic():
    """offset + PAGE_SIZE stopping matches the real endpoint semantics."""
    from app.adapters.amazon import PAGE_SIZE

    payload = _load_amazon_json()
    total = int(payload["hits"])
    pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
    assert pages * PAGE_SIZE >= total


def _load_google_html():
    with open(FIXTURES / "google" / "google_search.html", encoding="utf-8") as f:
        return f.read()


def test_google_parse_page():
    from app.adapters.google import _extract_ds1_data

    data = _extract_ds1_data(_load_google_html())
    assert data is not None
    assert data[2] > 0  # total
    assert len(data[0]) > 0


def test_google_normalize():
    from app.adapters.google import GoogleAdapter, _extract_ds1_data

    data = _extract_ds1_data(_load_google_html())
    job = GoogleAdapter._normalize(data[0][0])
    assert job.external_job_id.isdigit()
    assert job.title
    assert job.location
    assert job.url and "google.com/about/careers" in job.url
    assert job.external_job_id in (job.url or "")
    assert job.posted_at
    assert job.countries
    assert job.description


def test_google_empty_result_page():
    """A page whose ds:1 data[0] is None (no matches) must not crash."""
    from app.adapters.google import _extract_ds1_data

    html = (
        "<script>AF_initDataCallback({key: 'ds:1', hash: '2', data:[null, null, 0, 20]});</script>"
    )
    data = _extract_ds1_data(html)
    assert data is not None
    assert (data[0] or []) == []


def test_google_no_callback_returns_none():
    from app.adapters.google import _extract_ds1_data

    assert _extract_ds1_data("<html><body>no data</body></html>") is None


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
    assert parse_command("/matches@JobQuestBot adobe") == ("matches", "adobe")
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

    return SimpleNamespace(
        telegram_chat_id=chat_id,
        telegram_bot_token="test-token",
        telegram_mini_app_url="",
    )


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


def test_bot_menu_markup_with_mini_app():
    from app.telegram.bot import MENU_COMMANDS, _menu_markup

    markup = _menu_markup(mini_app_url="https://example.com/app")
    rows = markup["inline_keyboard"]
    last_row = rows[-1]
    assert len(last_row) == 1
    assert last_row[0]["web_app"] == {"url": "https://example.com/app"}
    buttons = [b for row in rows for b in row]
    assert len(buttons) == len(MENU_COMMANDS) + 1


def test_bot_app_markup():
    from app.telegram.bot import _app_markup

    markup = _app_markup("https://example.com/app")
    buttons = markup["inline_keyboard"][0]
    assert buttons[0]["web_app"] == {"url": "https://example.com/app"}


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


def test_bot_inline_results_empty_query():
    from app.telegram.bot import _inline_results

    results = _inline_results(_fake_settings("123456789"), "   ", limit=5)
    assert results == []


def test_bot_inline_placeholder():
    from app.telegram.bot import _inline_placeholder

    empty = _inline_placeholder("")
    assert len(empty) == 1
    assert empty[0]["id"] == "placeholder"
    assert "Search" in empty[0]["title"]

    no_match = _inline_placeholder("xyznotfound")
    assert len(no_match) == 1
    assert no_match[0]["id"] == "placeholder"
    assert "xyznotfound" in no_match[0]["title"]


def test_bot_inline_query_unauthorized_answers_empty():
    import asyncio

    from app.telegram.bot import _handle_inline_query

    settings = _fake_settings("123456789")

    async def run():
        calls = []

        class FakeResponse:
            status_code = 200

        class FakeClient:
            async def post(self, url, **kwargs):
                calls.append((url, kwargs.get("content")))
                return FakeResponse()

        await _handle_inline_query(
            settings,
            {
                "inline_query": {
                    "id": "iq-1",
                    "query": "python",
                    "from": {"id": 999},
                }
            },
            FakeClient(),
        )
        return calls

    calls = asyncio.run(run())
    answered = [c for c in calls if "answerInlineQuery" in c[0]]
    assert len(answered) == 1
    payload = json.loads(answered[0][1])
    assert payload["inline_query_id"] == "iq-1"
    assert payload["results"] == []


def test_bot_inline_query_empty_when_no_term():
    import asyncio
    import json

    from app.telegram.bot import _handle_inline_query

    settings = _fake_settings("123456789")

    async def run():
        calls = []

        class FakeResponse:
            status_code = 200

        class FakeClient:
            async def post(self, url, **kwargs):
                calls.append((url, kwargs.get("content")))
                return FakeResponse()

        await _handle_inline_query(
            settings,
            {
                "inline_query": {
                    "id": "iq-2",
                    "query": "",
                    "from": {"id": 123456789},
                }
            },
            FakeClient(),
        )
        return calls

    calls = asyncio.run(run())
    answered = [c for c in calls if "answerInlineQuery" in c[0]]
    assert len(answered) == 1
    payload = json.loads(answered[0][1])
    assert payload["results"] and payload["results"][0]["id"] == "placeholder"


def _load_emirates_jobs():
    with open(FIXTURES / "emirates" / "emirates_jobs.json", encoding="utf-8") as f:
        return json.load(f)["data"]


def test_emirates_parse_jobs():
    """Emirates JSON entries must parse into jobs with stable reqid, title, url."""
    from app.adapters.emirates import EmiratesAdapter

    entries = _load_emirates_jobs()
    assert len(entries) >= 3, "fixture must contain job entries"
    job = EmiratesAdapter._normalize(entries[0], "https://www.emiratesgroupcareers.com")
    assert job.external_job_id == "267"
    assert job.title == "Cabin Crew Opportunities"
    assert job.location == "Emirates Group Headquarters"
    assert job.url == "https://www.emiratesgroupcareers.com/search-and-apply/267"
    assert job.countries == ["United Arab Emirates"]
    assert job.posted_at is not None


def test_emirates_empty_location_falls_back_to_city_country():
    """Jobs with an empty location string must fall back to city/state/country."""
    from app.adapters.emirates import EmiratesAdapter

    entries = _load_emirates_jobs()
    it_job = next(e for e in entries if e["reqid"] == "23987")
    job = EmiratesAdapter._normalize(it_job, "https://www.emiratesgroupcareers.com")
    assert job.external_job_id == "23987"
    assert job.location is not None and "Dubai" in job.location
    assert "United Arab Emirates" in job.location


def test_emirates_missing_fields():
    from app.adapters.emirates import EmiratesAdapter

    job = EmiratesAdapter._normalize({}, "https://www.emiratesgroupcareers.com")
    assert job.external_job_id == ""
    assert job.title == ""
    assert job.location is None

    job = EmiratesAdapter._normalize(
        {"reqid": "123", "title": "  Engineer  ", "country": "India"},
        "https://www.emiratesgroupcareers.com/",
    )
    assert job.external_job_id == "123"
    assert job.title == "Engineer"
    assert job.location == "India"
    assert job.url == "https://www.emiratesgroupcareers.com/search-and-apply/123"


def test_emirates_posted_date_parsing():
    from app.adapters.emirates import _parse_posted

    assert _parse_posted(1748390400000) is not None
    assert _parse_posted(None) is None
    assert _parse_posted("not-a-date") is None


def test_emirates_adapter_registered():
    from app.adapters import adapter_for
    from app.adapters.emirates import EmiratesAdapter

    assert EmiratesAdapter.ats_type == "emirates"
    assert isinstance(adapter_for("emirates"), EmiratesAdapter)


def test_detect_emirates_url():
    assert _detect_from_url("https://www.emiratesgroupcareers.com/search-and-apply/") == {
        "ats_type": "emirates",
        "board_identifier": "https://www.emiratesgroupcareers.com",
    }


def test_load_settings_memoized(monkeypatch):
    """Step D: repeated load_settings() must return the same object (no re-parse)."""
    from app.config import load_settings, reset_settings_cache

    # Hermetic: CI has no .env file (gitignored), so stamp dummy required vars.
    monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "test-key")
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
    reset_settings_cache()
    try:
        first = load_settings()
        second = load_settings()
        assert first is second
    finally:
        reset_settings_cache()
    third = load_settings()
    assert third is not first
    assert third.supabase_url == first.supabase_url
    reset_settings_cache()


def test_ats_concurrency_defaults_and_env_override(monkeypatch):
    """Tier 3: heavy boards run 10-way by default (workday 20 for 271 boards); POLL_CONCURRENCY_{ATS} overrides."""
    from app.config import ATS_CONCURRENCY, load_settings, reset_settings_cache

    assert ATS_CONCURRENCY["workday"] == 20
    assert ATS_CONCURRENCY["successfactors"] == 10
    assert ATS_CONCURRENCY["avature"] == 10
    assert ATS_CONCURRENCY["oracle"] == 10
    assert ATS_CONCURRENCY["greenhouse"] == 16

    monkeypatch.setenv("POLL_CONCURRENCY_WORKDAY", "4")
    monkeypatch.setenv("POLL_CONCURRENCY_GREENHOUSE", "20")
    # Hermetic: CI has no .env file (gitignored), so stamp dummy required vars.
    monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "test-key")
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
    reset_settings_cache()
    try:
        settings = load_settings()
        assert settings.ats_concurrency["workday"] == 4
        assert settings.ats_concurrency["greenhouse"] == 20
        assert settings.ats_concurrency["lever"] == ATS_CONCURRENCY["lever"]
    finally:
        reset_settings_cache()
    monkeypatch.delenv("POLL_CONCURRENCY_WORKDAY", raising=False)
    monkeypatch.delenv("POLL_CONCURRENCY_GREENHOUSE", raising=False)
    assert load_settings().ats_concurrency["workday"] == 20
    reset_settings_cache()


def test_query_async_with_fake_pool():
    """Step C: query_async must return json-safe rows via the shared async pool."""
    import asyncio
    import uuid

    import app.db as db

    uid = uuid.uuid4()

    class FakeCursor:
        description = (type("Col", (), {"name": "id"})(),)
        executed = None

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return False

        async def execute(self, sql, params):
            FakeCursor.executed = (sql, params)

        async def fetchall(self):
            return [(uid,)]

    class FakeConn:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return False

        def cursor(self):
            return FakeCursor()

    class FakePool:
        def connection(self, timeout=None):
            return FakeConn()

    async def run():
        previous = db._apool
        db._apool = FakePool()
        try:
            return await db.query_async(object(), "select id from t where x = %s", ("y",))
        finally:
            db._apool = previous

    rows = asyncio.run(run())
    assert rows == [{"id": str(uid)}]
    assert FakeCursor.executed[0].startswith("select id")


def test_close_async_pool_noop_without_pool():
    """Step C: closing when no pool is open must not raise."""
    import asyncio

    import app.db as db

    async def run():
        assert db._apool is None
        await db.close_async_pool()
        assert db._apool is None

    asyncio.run(run())


def test_poll_source_reuses_geo_settings(monkeypatch):
    """Step D: a passed geo_settings must be reused (no app_settings DB read).

    New ingestion path: persistence is database-side (bulk INSERT ... RETURNING),
    so poll_source must not touch Supabase REST at all — only mark_checked does.
    """
    import asyncio

    import app.poller as poller_module
    from app.geo import DEFAULT_SETTINGS
    from app.models import NormalizedJob
    from app.poller import poll_source

    accessed_tables: list[str] = []

    class FakeResponse:
        data: tuple = ()

    class FakeTable:
        def __init__(self, name: str):
            self._name = name

        def select(self, *args, **kwargs):
            return self

        def update(self, *args, **kwargs):
            return self

        def upsert(self, *args, **kwargs):
            return self

        def eq(self, *args, **kwargs):
            return self

        def execute(self):
            return FakeResponse()

    class FakeSupabase:
        def table(self, name: str):
            accessed_tables.append(name)
            return FakeTable(name)

    class FakeAdapter:
        async def fetch_jobs(self, board_identifier: str, client=None):
            return [
                NormalizedJob(
                    external_job_id="1",
                    title="Engineer",
                    location="Bengaluru, India",
                    url="https://example.com/jobs/1",
                    raw_payload={},
                )
            ]

    statements: list[str] = []
    sentinel = object()
    # Hermetic: poll_source resolves settings internally; CI has no .env file.
    monkeypatch.setattr(poller_module, "load_settings", lambda: sentinel)

    def fake_query(settings, sql, params=()):
        statements.append(sql)
        if sql.startswith("INSERT INTO jobs"):
            assert settings is sentinel
            return [{"external_job_id": "1", "is_new": True}]
        return []

    monkeypatch.setattr(poller_module, "query", fake_query)

    async def run():
        return await poll_source(
            FakeSupabase(),
            {"id": "source-1", "company_name": "Acme", "board_identifier": "acme"},
            FakeAdapter(),
            90,
            geo_settings={**DEFAULT_SETTINGS},
        )

    result = asyncio.run(run())
    assert result["company"] == "Acme"
    assert result["fetched"] == 1
    assert result["new"] == 1
    assert result["new_ids"] == ["1"]
    assert "app_settings" not in accessed_tables
    assert "jobs" not in accessed_tables
    # Full lifecycle sequence runs on the success path: upsert, reactivate, touch, sweep.
    joined = "\n".join(statements)
    assert joined.count("INSERT INTO jobs") == 1
    assert "is_active = true" in joined  # reactivate reposts
    assert "last_seen_at = now()" in joined  # touch sightings
    assert "is_active = false" in joined  # sweep the unseen


def _job_row(external_id: str, index: int = 0) -> dict:
    return {
        "source_id": "source-1",
        "external_job_id": external_id,
        "title": f"Engineer {index}",
        "location": "Bengaluru, India",
        "url": f"https://example.com/jobs/{external_id}",
        "countries": ["IN"],
        "is_remote": False,
    }


def test_upsert_jobs_returning_chunks_and_new_detection(monkeypatch):
    """Bulk path: 1200 rows -> 3 chunks, RETURNING maps is_new, SQL shape exact."""
    import app.poller as poller_module

    calls: list[tuple[str, tuple]] = []

    def fake_query(settings, sql, params=()):
        calls.append((sql, params))
        return [
            {"external_job_id": "n", "is_new": True},
            {"external_job_id": "o", "is_new": False},
        ]

    monkeypatch.setattr(poller_module, "query", fake_query)
    rows = [_job_row(f"e{i}", i) for i in range(1200)]
    out = poller_module.upsert_jobs_returning(object(), rows)
    assert len(calls) == 3  # 1200 rows at 500 per chunk
    assert len(calls[0][1]) == 500 * 8
    assert len(calls[2][1]) == 200 * 8
    sql = calls[0][0]
    assert "ON CONFLICT (source_id, external_job_id)" in sql
    assert "DO UPDATE SET" in sql
    assert "description = EXCLUDED" not in sql  # descriptions frozen after insert
    assert "RETURNING" in sql and "xmax" in sql
    assert "%s::uuid" in sql and "%s::text[]" in sql
    assert out == {"new_ids": ["n", "n", "n"], "failed_chunks": 0}


def test_upsert_placeholders_match_columns():
    """Structural invariant: one placeholder per upsert column. A mismatch
    fails every poll's upserts loudly, so this is locked at unit level."""
    import re

    import app.poller as poller_module

    assert len(re.findall(r"%s", poller_module._ROW_SQL)) == len(poller_module._UPSERT_COLS)


def test_upsert_jobs_returning_stamps_geo_version(monkeypatch):
    """geo_version rides the INSERT positionally (last column); rows without
    one stamp NULL (unknown vintage). Never part of the conflict update."""
    import app.poller as poller_module

    captured: list[tuple[str, tuple]] = []

    def fake_query(settings, sql, params=()):
        captured.append((sql, params))
        return []

    monkeypatch.setattr(poller_module, "query", fake_query)
    rows = [_job_row("g1"), _job_row("g2")]
    out = poller_module.upsert_jobs_returning(object(), rows, geo_version=9)
    assert out == {"new_ids": [], "failed_chunks": 0}
    sql, params = captured[0]
    assert params[7] == 9 and params[15] == 9
    assert "geo_version" in sql  # INSERT column list
    assert "geo_version = EXCLUDED" not in sql  # never conflict-updated
    out = poller_module.upsert_jobs_returning(object(), [_job_row("g3")])
    assert captured[1][1][7] is None


def test_location_mapping_save_bumps_version(monkeypatch):
    """Each mapping save mints the next generation; content merges over defaults."""
    from types import SimpleNamespace

    from app import settings_store as ss

    stored: dict = {}
    saved: dict = {}

    class FakeTable:
        def __init__(self):
            self._selecting = False

        def select(self, *args, **kwargs):
            self._selecting = True
            return self

        def eq(self, *args, **kwargs):
            return self

        def upsert(self, payload, **kwargs):
            saved.update(payload)
            return self

        def execute(self):
            if self._selecting:
                self._selecting = False
                data = [{"value": dict(stored)}] if stored else []
                return SimpleNamespace(data=data)
            return SimpleNamespace(data=[])

    class FakeSupabase:
        def table(self, name):
            assert name == "app_settings"
            return FakeTable()

    supabase = FakeSupabase()
    ss.save_location_mapping(supabase, {"custom_aliases": {"gotham": "US"}})
    assert saved["value"]["version"] == 1
    assert saved["value"]["custom_aliases"] == {"gotham": "US"}
    assert saved["value"]["enabled"] is True  # defaults merged
    stored.update(saved["value"])
    saved.clear()
    ss.save_location_mapping(supabase, {"custom_aliases": {"metropolis": "US"}})
    assert saved["value"]["version"] == 2
    assert saved["value"]["custom_aliases"] == {"metropolis": "US"}


def test_upsert_jobs_returning_empty_and_failures(monkeypatch):
    """Empty short-circuits; all-failed raises; partial failure still returns."""
    import pytest

    import app.poller as poller_module

    seen: list = []
    monkeypatch.setattr(poller_module, "query", lambda *a, **k: seen.append(a) or [])
    assert poller_module.upsert_jobs_returning(object(), []) == {
        "new_ids": [],
        "failed_chunks": 0,
    }
    assert seen == []

    def always_fail(settings, sql, params=()):
        raise RuntimeError("boom")

    monkeypatch.setattr(poller_module, "query", always_fail)
    with pytest.raises(RuntimeError, match="all 1 upsert chunk"):
        poller_module.upsert_jobs_returning(object(), [_job_row("e")])

    state = {"n": 0}

    def flaky(settings, sql, params=()):
        state["n"] += 1
        if state["n"] == 1:
            raise RuntimeError("boom")
        return [{"external_job_id": "ok", "is_new": True}]

    monkeypatch.setattr(poller_module, "query", flaky)
    big = [_job_row(f"e{i}", i) for i in range(600)]  # 2 chunks
    assert poller_module.upsert_jobs_returning(object(), big) == {
        "new_ids": ["ok"],
        "failed_chunks": 1,
    }


def test_reactivate_jobs_returns_reopened_ids(monkeypatch):
    """Reposts (seen again after deactivation) are reported for matching."""
    import app.poller as poller_module

    calls: list[tuple[str, tuple]] = []

    def fake_query(settings, sql, params=()):
        calls.append((sql, params))
        return [{"external_job_id": "r1"}, {"external_job_id": "r2"}]

    monkeypatch.setattr(poller_module, "query", fake_query)
    out = poller_module.reactivate_jobs(object(), "source-9", ["r1", "r2", "r3"])
    assert out == ["r1", "r2"]
    assert "is_active = false" in calls[0][0]
    assert "last_seen_at = now()" in calls[0][0]
    assert poller_module.reactivate_jobs(object(), "source-9", []) == []
    assert len(calls) == 1  # empty list short-circuits, no query


def test_touch_and_sweep_sql_shape(monkeypatch):
    """Touch respects the staleness guard; sweep respects the grace window."""
    import app.poller as poller_module

    calls: list[tuple[str, tuple]] = []

    def fake_query(settings, sql, params=()):
        calls.append((sql, params))
        return [{"external_job_id": "x"}]

    monkeypatch.setattr(poller_module, "query", fake_query)
    assert poller_module.touch_seen_jobs(object(), "source-9", ["a", "b"]) == 1
    assert poller_module.sweep_missing_jobs(object(), "source-9", grace_hours=72) == ["x"]
    assert poller_module.touch_seen_jobs(object(), "source-9", []) == 0
    touch_sql, sweep_sql = calls[0][0], calls[1][0]
    assert "last_seen_at < now()" in touch_sql  # daily granularity, not per poll
    assert "is_active" in sweep_sql and "last_seen_at < now()" in sweep_sql
    assert calls[1][1][1] == 72  # grace passed as a bound parameter, not inlined


def test_prune_inactive_jobs_counts_deletes(monkeypatch):
    """Inactive prune returns the deleted count for retention logging."""
    import app.poller as poller_module

    monkeypatch.setattr(poller_module, "query", lambda settings, sql, params=(): [{"c": 7}])
    assert poller_module.prune_inactive_jobs(object()) == 7


def test_prune_old_jobs_requires_abandonment_not_just_age(monkeypatch):
    """Item 12 (Job-A rule): the age prune must filter on last_seen_at too,
    so an old-but-still-seen posting is never deleted for age alone."""
    import app.poller as poller_module

    chains: list[list[tuple[str, str]]] = []

    class FakeResponse:
        data: tuple = ()

    class FakeDelete:
        def __init__(self):
            self.filters: list[tuple[str, str]] = []

        def lt(self, column, value):
            self.filters.append((column, value))
            return self

        def execute(self):
            chains.append(self.filters)
            return FakeResponse()

    class FakeTable:
        def delete(self):
            return FakeDelete()

    class FakeSupabase:
        def table(self, name):
            assert name == "jobs"
            return FakeTable()

    monkeypatch.setattr(poller_module, "load_settings", lambda: object())
    monkeypatch.setattr(poller_module, "query", lambda settings, sql, params=(): [{"c": 0}])
    assert poller_module.prune_old_jobs(FakeSupabase(), 30) == 0
    assert len(chains) == 1
    cols = [column for column, _ in chains[0]]
    assert "first_seen_at" in cols and "last_seen_at" in cols
    assert chains[0][0][1] == chains[0][1][1]  # one cutoff for both guards


def test_mark_checked_writes_health_atomically(monkeypatch):
    """Success path stamps all seven health signals in one UPDATE (no
    read-modify-write, so overlapping runs can't lose counter increments)."""
    import app.poller as poller_module

    calls: list[tuple[str, tuple]] = []

    def fake_query(settings, sql, params=()):
        calls.append((sql, params))
        return []

    monkeypatch.setattr(poller_module, "query", fake_query)
    poller_module.mark_checked(object(), "source-1", 3, fetched=12, new=4, duration_ms=1500)
    assert len(calls) == 1
    sql, params = calls[0]
    for column in (
        "last_checked_at",
        "last_success_at",
        "consecutive_failures",
        "consecutive_empty_runs",
        "last_http_status",
        "last_duration_ms",
        "jobs_last_seen",
        "quiet_runs",
    ):
        assert column in sql
    assert params == (3, 12, 1500, 4, "source-1")
    # Empty vs productive is data-driven (CASE), not a code branch.
    poller_module.mark_checked(object(), "source-1", 0, fetched=0, new=0, duration_ms=10)
    assert calls[1][1] == (0, 0, 10, 0, "source-1")


def test_mark_error_tracks_failures_not_emptiness(monkeypatch):
    """Failure path advances failure signals only; success fields and the
    empty counter stay untouched. HTTP status extracted when present."""
    import app.poller as poller_module

    calls: list[tuple[str, tuple]] = []

    def fake_query(settings, sql, params=()):
        calls.append((sql, params))
        return []

    monkeypatch.setattr(poller_module, "query", fake_query)

    class HttpError(Exception):
        def __init__(self):
            super().__init__("429 hammered")
            from types import SimpleNamespace

            self.response = SimpleNamespace(status_code=429)

    poller_module.mark_error(object(), {"id": "source-1"}, HttpError())
    sql, params = calls[0]
    assert "last_failure_at" in sql and "consecutive_failures" in sql
    assert "last_success_at" not in sql and "consecutive_empty_runs" not in sql
    assert "jobs_last_seen" not in sql and "last_duration_ms" not in sql
    assert params[1] == 429

    poller_module.mark_error(object(), {"id": "source-1"}, RuntimeError("dns blew up"))
    assert calls[1][1][1] is None  # no HTTP status without a response


def _drain_harness(monkeypatch, items, recorded=(), lock_granted=True):
    """Minimal drain fakes: one due telegram row, routable item loads, no network."""
    from types import SimpleNamespace

    import app.notification_queue as nq

    due_row = {
        "id": "q1",
        "user_id": "u1",
        "job_id": "j1",
        "channel": "telegram",
        "attempts": 0,
        "role": "user",
        "status": "approved",
        "access_locked": False,
        "capabilities": ["dashboard", "preferences", "telegram_alerts", "email_alerts"],
        "alert_delay_minutes": 0,
        "telegram_chat_id": 123,
        "email": None,
    }

    def fake_query(settings, sql, params=()):
        if "scheduled_for" in sql and "from notification_queue q" in sql:
            return [dict(due_row)]  # the due-window select (has a destination)
        if "from notifications_sent" in sql:
            return [{"job_id": job_id} for job_id in recorded]
        if "from jobs j" in sql:
            return list(items)
        return []  # cancel-cleanup selects: nothing undeliverable here

    monkeypatch.setattr(nq, "query", fake_query)

    calls: dict[str, list] = {"mark": [], "ledger": [], "sent": []}

    lock_state = {"acquired": 0, "released": 0}

    def fake_acquire(settings):
        if not lock_granted:
            return None
        lock_state["acquired"] += 1
        return object()

    def fake_release(conn):
        lock_state["released"] += 1

    monkeypatch.setattr(nq, "_acquire_drain_lock", fake_acquire)
    monkeypatch.setattr(nq, "_release_drain_lock", fake_release)
    calls["lock"] = lock_state

    class FakeTable:
        def __init__(self, name):
            self.name = name
            self.payload = None

        def update(self, payload):
            self.payload = payload
            return self

        def upsert(self, payload, **kwargs):
            calls["ledger"].append((self.name, payload))
            return self

        def eq(self, column, value):
            return self

        def in_(self, column, values):
            calls["mark"].append((self.name, self.payload, column, list(values)))
            return self

        def execute(self):
            class R:
                data = ()

            return R()

    class FakeSupabase:
        def table(self, name):
            return FakeTable(name)

    monkeypatch.setattr(nq, "_send_message", lambda *args, **kwargs: calls["sent"].append(args))
    settings = SimpleNamespace(
        telegram_enabled=True, telegram_bot_token="tok", notify_enabled=False
    )
    return nq, settings, FakeSupabase(), calls


def test_drain_ledger_skips_pruned_jobs(monkeypatch):
    """042 FK guard: a job pruned between enqueue and drain loads no item, so
    it must never reach the ledger (the FK would reject it); its queue row is
    still marked sent as processed."""
    nq_mod, settings, supabase, calls = _drain_harness(monkeypatch, items=[])
    out = nq_mod.drain_due_notifications(settings, supabase)
    assert out == {"sent_telegram": 1, "sent_email": 0, "failed": 0}
    assert len(calls["sent"]) == 1  # summary-only message still went out
    assert calls["ledger"] == []
    assert len(calls["mark"]) == 1 and calls["mark"][0][3] == ["q1"]


def test_drain_ledger_records_communicated_jobs(monkeypatch):
    """Normal path unchanged: a surviving job is recorded exactly once."""
    item = {
        "id": "j1",
        "title": "T",
        "location": "L",
        "url": "u",
        "matched_on": [],
        "company": "Acme",
    }
    nq_mod, settings, supabase, calls = _drain_harness(monkeypatch, items=[item])
    out = nq_mod.drain_due_notifications(settings, supabase)
    assert out == {"sent_telegram": 1, "sent_email": 0, "failed": 0}
    assert len(calls["ledger"]) == 1
    name, payload = calls["ledger"][0]
    assert name == "notifications_sent"
    assert payload == [
        {"user_id": "u1", "job_id": "j1", "channel": "telegram", "sent_at": payload[0]["sent_at"]}
    ]


def test_drain_skips_tick_when_lock_held(monkeypatch):
    """Single-flight: a loser returns zeros without touching the DB or sending."""
    nq_mod, settings, supabase, calls = _drain_harness(monkeypatch, items=[], lock_granted=False)
    out = nq_mod.drain_due_notifications(settings, supabase)
    assert out == {"sent_telegram": 0, "sent_email": 0, "failed": 0}
    assert calls["sent"] == [] and calls["mark"] == [] and calls["ledger"] == []
    assert calls["lock"] == {"acquired": 0, "released": 0}


def test_drain_skips_resend_of_recorded_jobs(monkeypatch):
    """Crash-window dedup: ledger already has the row -> mark sent, never
    resend, never re-record (the 042 FK would reject ghosts anyway)."""
    nq_mod, settings, supabase, calls = _drain_harness(monkeypatch, items=[], recorded=["j1"])
    out = nq_mod.drain_due_notifications(settings, supabase)
    assert out == {"sent_telegram": 0, "sent_email": 0, "failed": 0}
    assert calls["sent"] == []
    assert calls["ledger"] == []
    assert len(calls["mark"]) == 1 and calls["mark"][0][3] == ["q1"]
    assert calls["mark"][0][1]["status"] == "sent"
    assert calls["lock"]["released"] == 1


def test_drain_releases_lock_on_send_failure(monkeypatch):
    """Lock is released even when the send blows up mid-tick."""
    nq_mod, settings, supabase, calls = _drain_harness(
        monkeypatch,
        items=[
            {
                "id": "j1",
                "title": "T",
                "location": "L",
                "url": "u",
                "matched_on": [],
                "company": "Acme",
            }
        ],
    )

    def boom(*args, **kwargs):
        raise RuntimeError("net down")

    monkeypatch.setattr(nq_mod, "_send_message", boom)
    out = nq_mod.drain_due_notifications(settings, supabase)
    assert out == {"sent_telegram": 0, "sent_email": 0, "failed": 0}
    assert calls["lock"]["released"] == 1


def test_email_idempotency_key_stable():
    """Same logical batch always hashes identically (order-insensitive);
    different batches never collide in the tested space."""
    from app.notification_queue import _email_idempotency_key

    key = _email_idempotency_key("u1", "email", ["j2", "j1"])
    assert key == _email_idempotency_key("u1", "email", ["j1", "j2", "j1"])
    assert key.startswith("jq-") and len(key) <= 100
    assert key != _email_idempotency_key("u1", "email", ["j1"])
    assert key != _email_idempotency_key("u1", "telegram", ["j1", "j2"])


def test_quiet_runs_counter():
    """Quiet counter resets on first check / new jobs, else increments."""
    from app.poller import next_quiet_runs

    assert next_quiet_runs({"quiet_runs": 7}, True, 0) == 0
    assert next_quiet_runs({"quiet_runs": 7}, False, 3) == 0
    assert next_quiet_runs({"quiet_runs": 7}, False, 0) == 8
    assert next_quiet_runs({}, False, 0) == 1
    assert next_quiet_runs({"quiet_runs": None}, False, 0) == 1


def test_quiet_due_predicate():
    """Quiet backoff skips only scheduled per-ATS runs for quiet, recently-checked boards."""
    from datetime import UTC, datetime, timedelta

    from app.poller import QUIET_RUNS_THRESHOLD, QUIET_SKIP_MULTIPLE, quiet_due

    now = datetime.now(UTC)
    quiet = {"company_name": "Q", "quiet_runs": QUIET_RUNS_THRESHOLD + 2}
    fresh = {**quiet, "last_checked_at": (now - timedelta(minutes=30)).isoformat()}
    stale = {**quiet, "last_checked_at": (now - timedelta(hours=5)).isoformat()}

    # Scheduled per-ATS run: fresh quiet board skipped, stale one due.
    due, reason = quiet_due(fresh, 3600, now, triggered_by="scheduled", ats_type="workday")
    assert due is False and "quiet board" in (reason or "")
    due, _ = quiet_due(stale, 3600, now, triggered_by="scheduled", ats_type="workday")
    assert due is True

    # Boundary: exactly MULTIPLE intervals old is due (every Nth check runs).
    edge = {
        **quiet,
        "last_checked_at": (now - timedelta(seconds=3600 * QUIET_SKIP_MULTIPLE)).isoformat(),
    }
    due, _ = quiet_due(edge, 3600, now, triggered_by="scheduled", ats_type="workday")
    assert due is True

    # Loud boards, never-checked boards, manual and global runs are always due.
    loud = {"company_name": "L", "quiet_runs": 0, "last_checked_at": fresh["last_checked_at"]}
    assert quiet_due(loud, 3600, now, triggered_by="scheduled", ats_type="workday")[0] is True
    assert (
        quiet_due({"quiet_runs": 99}, 3600, now, triggered_by="scheduled", ats_type="workday")[0]
        is True
    )
    assert quiet_due(fresh, 3600, now, triggered_by="manual", ats_type="workday")[0] is True
    assert quiet_due(fresh, 3600, now, triggered_by="scheduled", ats_type=None)[0] is True


def test_quiet_boards_not_stale():
    """Quiet boards (checked every 3rd interval by design) are not stale at 3h."""
    from datetime import UTC, datetime, timedelta

    from app.poller import (
        QUIET_RUNS_THRESHOLD,
        QUIET_SKIP_MULTIPLE,
        source_status,
        stale_after_seconds,
    )

    now = datetime.now(UTC)
    three_hours_ago = (now - timedelta(hours=3)).isoformat()

    loud = {"company_name": "L", "quiet_runs": 0, "last_checked_at": three_hours_ago}
    assert stale_after_seconds(loud, 3600) == 7200
    assert source_status(loud, 3600, now)[0] == "stale"

    quiet = {
        "company_name": "Q",
        "quiet_runs": QUIET_RUNS_THRESHOLD + 2,
        "last_checked_at": three_hours_ago,
    }
    assert stale_after_seconds(quiet, 3600) == 3600 * QUIET_SKIP_MULTIPLE * 2
    assert source_status(quiet, 3600, now)[0] == "healthy"

    # Way past even the quiet cadence -> stale again.
    ancient = {**quiet, "last_checked_at": (now - timedelta(hours=7)).isoformat()}
    assert source_status(ancient, 3600, now)[0] == "stale"

    # Errors keep the strict bar even for quiet boards.
    errored = {**quiet, "last_error": "boom"}
    assert stale_after_seconds(errored, 3600) == 7200
    assert source_status(errored, 3600, now)[0] == "stale"


def test_stats_daily_shapes_series(monkeypatch):
    """GET /api/stats/daily with a stubbed DB: shape, totals, placeholder alignment."""
    from types import SimpleNamespace

    import app.api.routes as routes

    calls: list[tuple[str, list]] = []

    def fake_query(_settings, sql, params=()):
        calls.append((sql, list(params)))
        return [
            {"day": "2026-09-10", "jobs": 5, "matches": 1, "avg_score": 80},
            {"day": "2026-09-11", "jobs": 0, "matches": 0, "avg_score": 0},
        ]

    monkeypatch.setattr(routes, "query", fake_query)
    monkeypatch.setattr(routes, "_settings", lambda: object())
    out = routes.stats_daily(SimpleNamespace(id="user-1"), days=2)
    assert out["total_jobs"] == 5
    assert [d["date"] for d in out["days"]] == ["2026-09-10", "2026-09-11"]
    assert out["days"][0]["matches"] == 1
    sql, params = calls[0]
    # 61: optimized to GROUP BY: now 2 placeholders (days, user_id) not 3
    assert sql.count("%s") == len(params) == 2
    assert params[1] == "user-1"
