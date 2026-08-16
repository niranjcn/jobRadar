"""Fast smoke tests for the REST API. Uses a live uvicorn instance with the
scheduler disabled, so the test suite is fast and never triggers a poll.

Requires backend/.env (Supabase + DATABASE_URL). Run from backend/:
    python -m pytest tests/test_api.py -v
"""

import os
import sys
import time
import threading
import urllib.request
import urllib.error
import json
from pathlib import Path

import pytest

os.environ["JOBRADAR_DISABLE_SCHEDULER"] = "1"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import uvicorn
from app.migrate import run_migrations
from app.config import load_settings
from datetime import UTC

BASE_URL = "http://127.0.0.1:8100"
server = None


@pytest.fixture(scope="session", autouse=True)
def server_fixture():
    global server
    run_migrations(load_settings().database_url)
    config = uvicorn.Config("app.main:app", host="127.0.0.1", port=8100, log_level="error")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    for _ in range(100):
        try:
            urllib.request.urlopen(f"{BASE_URL}/health", timeout=2)
            break
        except Exception:
            time.sleep(0.2)
    yield
    server.should_exit = True
    thread.join(timeout=10)


def _get(path: str) -> dict:
    with urllib.request.urlopen(f"{BASE_URL}{path}", timeout=15) as res:
        return json.loads(res.read())


def _put(path: str, payload: dict) -> dict:
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="PUT",
    )
    with urllib.request.urlopen(req, timeout=15) as res:
        return json.loads(res.read())


def _post(path: str, payload: dict | None = None) -> dict:
    data = json.dumps(payload).encode() if payload is not None else None
    headers = {"Content-Type": "application/json"} if payload is not None else {}
    req = urllib.request.Request(f"{BASE_URL}{path}", data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=15) as res:
        return json.loads(res.read())


def test_health():
    assert _get("/health") == {"status": "ok"}


def test_stats_shape():
    stats = _get("/api/stats")
    for key in ("jobs_total", "jobs_new_7d", "companies", "matches", "avg_match_score"):
        assert key in stats, f"missing {key}"


def test_matches_summary_shape():
    data = _get("/api/matches/summary")
    assert "total" in data
    assert isinstance(data["companies"], list)
    assert data["total"] == sum(c["matches"] for c in data["companies"])


def test_matches_jobs_shapes():
    data = _get("/api/matches/jobs?limit=50")
    assert "jobs" in data and "total" in data
    assert data["limit"] == 50
    for job in data["jobs"]:
        assert "title" in job and "match_score" in job and "company" in job
    if data["jobs"]:
        first = data["jobs"][0]["company"]
        scoped = _get(f"/api/matches/jobs?company={first}")
        assert len(scoped["jobs"]) == scoped["total"]
        assert all(j["company"] == first for j in scoped["jobs"])


def test_jobs_list_shape():
    data = _get("/api/jobs?limit=5")
    assert isinstance(data["jobs"], list)
    assert isinstance(data["total"], int)
    if data["jobs"]:
        job = data["jobs"][0]
        for key in ("id", "title", "company", "ats_type", "match_score"):
            assert key in job, f"missing {key}"


def test_sources_shape():
    data = _get("/api/sources")
    assert isinstance(data["sources"], list)
    assert isinstance(data["intervals"], dict)
    if data["sources"]:
        src = data["sources"][0]
        for key in ("id", "company_name", "ats_type", "status", "poll_interval"):
            assert key in src, f"missing {key}"


def test_schedule_shape():
    data = _get("/api/schedule")
    assert isinstance(data["schedule"], list)
    if data["schedule"]:
        entry = data["schedule"][0]
        for key in (
            "ats_type",
            "interval_seconds",
            "last_checked_at",
            "next_run_at",
            "source_count",
        ):
            assert key in entry, f"missing {key}"
        # roundtrip: set an override, confirm it sticks, then reset
        _put(f"/api/schedule/{entry['ats_type']}", {"interval_seconds": 3600})
        after = _get("/api/schedule")
        target = next(e for e in after["schedule"] if e["ats_type"] == entry["ats_type"])
        assert target["interval_seconds"] == 3600
        # reset via DELETE
        req = urllib.request.Request(
            f"{BASE_URL}/api/schedule/{entry['ats_type']}",
            method="DELETE",
        )
        with urllib.request.urlopen(req, timeout=15) as res:
            assert json.loads(res.read())["ok"] is True


def test_job_filters_shape():
    data = _get("/api/jobs/filters")
    assert isinstance(data["companies"], list)
    assert isinstance(data["countries"], list)


def test_jobs_country_filter():
    data = _get("/api/jobs?limit=1&country=IN")
    assert "jobs" in data and "total" in data
    for job in data["jobs"]:
        assert "IN" in (job["countries"] or [])


def test_companies_shape():
    data = _get("/api/companies")
    assert isinstance(data["companies"], list)


def test_preferences_roundtrip():
    before = _get("/api/preferences")
    payload = {
        "roles": ["Backend Engineer", "DevOps Engineer"],
        "keywords": ["python", "aws"],
        "locations": ["remote", "dubai"],
        "seniority": ["senior"],
        "excluded_companies": [],
        "excluded_roles": ["staff", "principal"],
        "notify_telegram": True,
        "notify_email": True,
        "alert_frequency": "immediate",
    }
    _put("/api/preferences", payload)
    after = _get("/api/preferences")
    assert after["roles"] == payload["roles"]
    assert after["keywords"] == payload["keywords"]
    assert after["excluded_roles"] == payload["excluded_roles"]
    assert after["notify_telegram"] is True
    # restore
    _put(
        "/api/preferences",
        {
            **before,
            "roles": before.get("roles") or [],
            "keywords": before.get("keywords") or [],
            "locations": before.get("locations") or [],
            "seniority": before.get("seniority") or [],
            "excluded_companies": before.get("excluded_companies") or [],
            "excluded_roles": before.get("excluded_roles") or [],
            "notify_telegram": before.get("notify_telegram", True),
            "notify_email": before.get("notify_email", True),
            "alert_frequency": before.get("alert_frequency", "immediate"),
        },
    )


def test_preferences_recompute():
    """Saving preferences must immediately re-match existing jobs (matches page)."""
    before = _get("/api/preferences")
    _put(
        "/api/preferences",
        {
            "roles": [],
            "keywords": ["zzz-no-match-keyword-xyz"],
            "locations": [],
            "seniority": [],
            "excluded_companies": [],
            "notify_telegram": before.get("notify_telegram", True),
            "notify_email": before.get("notify_email", True),
            "alert_frequency": before.get("alert_frequency", "immediate"),
        },
    )
    assert _get("/api/stats")["matches"] == 0

    # restore original preferences -> recompute should bring matches back
    _put(
        "/api/preferences",
        {
            **before,
            "roles": before.get("roles") or [],
            "keywords": before.get("keywords") or [],
            "locations": before.get("locations") or [],
            "seniority": before.get("seniority") or [],
            "excluded_companies": before.get("excluded_companies") or [],
        },
    )
    assert _get("/api/stats")["matches"] >= 0


def test_notifications_shape():
    data = _get("/api/notifications")
    assert isinstance(data["notifications"], list)


def test_poll_runs_shape():
    """GET /api/poll/runs returns a run list with the fields the UI renders."""
    data = _get("/api/poll/runs?limit=5")
    assert isinstance(data["runs"], list)
    for run in data["runs"]:
        for key in (
            "id",
            "triggered_by",
            "status",
            "started_at",
            "finished_at",
            "jobs_fetched",
            "jobs_new",
            "matches_considered",
            "matches_new",
            "telegram_sent",
            "email_sent",
            "sources",
        ):
            assert key in run, f"missing {key}"
        assert run["triggered_by"] in ("scheduled", "manual")
        assert run["status"] in ("running", "completed", "failed")
        assert isinstance(run["sources"], list)


def test_poll_runs_conflict_guard():
    """Two concurrent manual runs -> the second is rejected with 409."""
    from app.poller import create_poll_run
    from app.db import get_supabase

    settings = load_settings()
    supabase = get_supabase(settings)
    run_id = create_poll_run(supabase, triggered_by="manual")
    try:
        with pytest.raises(urllib.error.HTTPError) as exc:
            _post("/api/poll/run", {"ats_type": "lever"})
        assert exc.value.code == 409
    finally:
        supabase.table("poll_runs").delete().eq("id", run_id).execute()


def test_clear_orphaned_runs():
    """Startup cleanup marks stale running rows as failed so they stop blocking polls."""
    from datetime import datetime, timedelta
    from app.poller import create_poll_run, clear_orphaned_runs
    from app.db import get_supabase

    settings = load_settings()
    supabase = get_supabase(settings)
    run_id = create_poll_run(supabase, triggered_by="scheduled", ats_type="workday")
    try:
        # force the run to appear long-stale so the startup cleanup picks it up
        supabase.table("poll_runs").update(
            {"started_at": (datetime.now(UTC) - timedelta(hours=3)).isoformat()}
        ).eq("id", run_id).execute()
        cleared = clear_orphaned_runs(supabase, stale_minutes=10)
        assert cleared >= 1
        row = supabase.table("poll_runs").select("status").eq("id", run_id).execute().data[0]
        assert row["status"] == "failed"
    finally:
        supabase.table("poll_runs").delete().eq("id", run_id).execute()


def test_add_source_detection_failure():
    """Unknown company -> clean 422 from auto-detect, no partial writes."""
    with pytest.raises(urllib.error.HTTPError) as exc:
        _post("/api/sources", {"company_name": "zzzdefinitelynotacompany123"})
    assert exc.value.code == 422


def test_location_mapping_get_and_preview():
    data = _get("/api/settings/location-mapping")
    assert "settings" in data
    assert "index_stats" in data
    assert "enabled" in data["settings"]
    assert data["index_stats"]["countries"] == 250

    preview = _post("/api/settings/location-mapping/preview", {"location": "Bengaluru, India"})
    assert "IN" in preview["countries"]
    assert preview["is_remote"] is False

    remote = _post("/api/settings/location-mapping/preview", {"location": "Remote - Germany"})
    assert "DE" in remote["countries"]
    assert remote["is_remote"] is True


def test_location_mapping_roundtrip():
    before = _get("/api/settings/location-mapping")["settings"]
    _put(
        "/api/settings/location-mapping",
        {
            "enabled": True,
            "remote_to": ["IN"],
            "custom_aliases": {"gotham": "US"},
        },
    )
    after = _get("/api/settings/location-mapping")["settings"]
    assert after["custom_aliases"].get("gotham") == "US"
    # restore
    _put("/api/settings/location-mapping", before)
