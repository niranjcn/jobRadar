"""Offline unit tests for app.public_filters (no DB, no network)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.public_filters import (
    csv_ilike_condition,
    escape_like,
    keyword_group_condition,
    parse_lpa,
    salary_condition,
    split_csv,
)


def test_split_csv():
    assert split_csv("") == []
    assert split_csv(None) == []
    assert split_csv("a, b,,A ,c") == ["a", "b", "c"]


def test_escape_like():
    assert escape_like("100%_x\\y") == "100\\%\\_x\\\\y"


def test_keyword_group_unknown_keys_ignored():
    cond, params = keyword_group_condition("types", ["nope", ""])
    assert cond == "" and params == []


def test_keyword_group_unknown_group():
    cond, params = keyword_group_condition("nope", ["full-time"])
    assert cond == "" and params == []


def test_keyword_group_builds_or_condition():
    cond, params = keyword_group_condition("types", ["internship"])
    assert "intern" in params[0]
    assert cond.count("ilike") == len(params) >= 2
    assert cond.startswith("(") and cond.endswith(")")


def test_keyword_group_multi_select():
    _cond, params = keyword_group_condition("exp", ["fresher", "bogus"])
    assert params, "known key must still produce keywords"
    assert "bogus" not in " ".join(params)


def test_csv_condition_empty():
    assert csv_ilike_condition("j.location", []) == ("", [])


def test_csv_condition_escapes_wildcards():
    cond, params = csv_ilike_condition("j.location", ["100%"])
    assert params == ["%100\\%%"]
    assert "escape" in cond


def test_parse_lpa():
    assert parse_lpa("12") == 12.0
    assert parse_lpa(" 8.5 ") == 8.5
    assert parse_lpa("") is None
    assert parse_lpa(None) is None
    assert parse_lpa("abc") is None
    assert parse_lpa("-3") is None
    assert parse_lpa("0") is None


def test_salary_condition_none():
    assert salary_condition("", "") == ("", [])
    assert salary_condition("abc", "-1") == ("", [])


def test_salary_condition_bounds():
    cond, params = salary_condition("6", "20")
    assert ">=" in cond and "<=" in cond
    assert params == [6.0, 20.0]


def _call_endpoint(monkeypatch, **kwargs):
    import app.api.public_routes as pr

    calls: list[tuple[str, list]] = []

    def fake_query(_settings, sql, params=()):
        calls.append((sql, list(params)))
        return [{"c": 0}] if "count(*)" in sql else []

    monkeypatch.setattr(pr, "query", fake_query)
    monkeypatch.setattr(pr, "_settings", lambda: object())
    result = pr.public_list_jobs(**kwargs)
    assert result["jobs"] == [] and result["total"] == 0
    assert len(calls) == 2, "listing + count queries expected"
    return calls


def test_endpoint_placeholders_match_params(monkeypatch):
    calls = _call_endpoint(
        monkeypatch,
        q="a%b_c",
        companies="Google,Zoho",
        sources="greenhouse,lever",
        countries="IN,US",
        locs="Bengaluru,Hyderabad",
        types="full-time,internship",
        exp="fresher",
        skills="Python",
        cats="software",
        min_salary="6",
        max_salary="20",
        country="IN",
        remote_only=True,
        mode="hybrid",
        since="2026-01-01T00:00:00+00:00",
        sort="oldest",
        limit=6,
        offset=0,
    )
    for sql, params in calls:
        assert sql.count("%s") == len(params), (sql, params)
    _, count_params = calls[1]
    assert "%a\\%b\\_c%" in count_params, "LIKE wildcards must be escaped"


def test_multi_term_search_is_union(monkeypatch):
    calls = _call_endpoint(monkeypatch, q="python,remote")
    sql, params = calls[0]
    assert sql.count("%s") == len(params)
    assert "%python%" in params and "%remote%" in params
    # The two per-term groups are joined by OR (union), not AND.
    assert ") or (lower(s.company_name) ilike lower(" in sql


def test_spaces_do_not_split_terms(monkeypatch):
    calls = _call_endpoint(monkeypatch, q="software engineer")
    sql, params = calls[0]
    assert sql.count("%s") == len(params)
    assert sql.count("lower(s.company_name) ilike lower(") == 1
    assert "%software engineer%" in params


def test_empty_search_has_no_text_clause(monkeypatch):
    calls = _call_endpoint(monkeypatch, q="   ")
    sql, params = calls[0]
    assert sql.count("%s") == len(params)
    assert "company_name) ilike" not in sql


def test_country_variants_cover_both_stored_spellings():
    from app.geo import country_stored_variants

    assert set(country_stored_variants(["IN"])) >= {"IN", "India"}
    assert set(country_stored_variants(["India"])) >= {"IN", "India"}
    assert set(country_stored_variants(["in"])) >= {"IN", "India"}
    assert country_stored_variants([""]) == []
    assert "XX" in country_stored_variants(["XX"])


def test_mixed_storage_matches_either_spelling():
    from app.geo import country_stored_variants, location_matches_preference

    # Stored full name matches a name preference and vice versa for codes.
    assert location_matches_preference(country_stored_variants(["India"]), False, "India", None)
    assert location_matches_preference(country_stored_variants(["IN"]), False, "India", None)
    # Without expansion the old exact-match behavior misses.
    assert not location_matches_preference(["INDIA"], False, "India", None)


def test_endpoint_country_filter_matches_variants(monkeypatch):
    calls = _call_endpoint(monkeypatch, countries="IN")
    _, count_params = calls[1]
    assert "IN" in count_params and "India" in count_params


def test_endpoint_defaults_align(monkeypatch):
    for sql, params in _call_endpoint(monkeypatch):
        assert sql.count("%s") == len(params)
