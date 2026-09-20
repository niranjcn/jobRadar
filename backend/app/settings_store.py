"""Read/write JSON settings in the app_settings table."""

import json
from datetime import UTC, datetime
from typing import Any

from supabase import Client

from app.geo import DEFAULT_SETTINGS, SETTINGS_KEY


def load_app_settings(supabase: Client, key: str) -> dict[str, Any] | None:
    response = supabase.table("app_settings").select("value").eq("key", key).execute()
    if not response.data:
        return None
    return response.data[0]["value"]


def save_app_settings(supabase: Client, key: str, value: dict[str, Any]) -> None:
    supabase.table("app_settings").upsert(
        {"key": key, "value": value, "updated_at": datetime.now(UTC).isoformat()},
        on_conflict="key",
    ).execute()


def load_location_mapping(supabase: Client) -> dict[str, Any]:
    row = load_app_settings(supabase, SETTINGS_KEY)
    merged = {**DEFAULT_SETTINGS}
    if row:
        merged.update(row)
    return merged


def save_location_mapping(supabase: Client, value: dict[str, Any]) -> None:
    # Every save mints a new mapping generation: jobs stamped with older
    # versions (see jobs.geo_version) are identifiable as stale without
    # re-reading history. Placed last so callers can never inject it.
    existing = load_app_settings(supabase, SETTINGS_KEY) or {}
    try:
        generation = int(existing.get("version") or 0) + 1
    except (TypeError, ValueError):
        generation = 1
    merged = {**DEFAULT_SETTINGS, **value, "version": generation}
    save_app_settings(supabase, SETTINGS_KEY, merged)


def as_json(value: dict[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False)
