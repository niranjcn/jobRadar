"""Preference presets: reusable bundles admins apply to users.

Applying a preset copies its arrays into the target user's preferences row
through a normal upsert (same shape as PUT /api/preferences). The preset
itself is never mutated. The seeded "Admin Preference" preset is a copy of
the original operator configuration.
"""

from datetime import UTC, datetime
from typing import Any

from supabase import Client

from app.config import Settings
from app.db import query

PRESET_FIELDS = (
    "roles",
    "keywords",
    "locations",
    "seniority",
    "excluded_companies",
    "excluded_roles",
)


def preset_fields(row: dict[str, Any]) -> dict[str, list[str]]:
    """Pure mapper: preset row -> preference columns (unit-tested offline)."""
    return {field: row.get(field) or [] for field in PRESET_FIELDS}


def list_presets(settings: Settings, *, include_admin_only: bool = False) -> list[dict[str, Any]]:
    where = "" if include_admin_only else "where not is_admin_only"
    return query(
        settings,
        f"""
        select id, name, description, roles, keywords, locations, seniority,
               excluded_companies, excluded_roles, is_admin_only, created_at
        from preference_presets
        {where}
        order by is_admin_only desc, name
        """,
    )


def get_preset(settings: Settings, preset_id: str) -> dict[str, Any] | None:
    rows = query(
        settings,
        """
        select id, name, description, roles, keywords, locations, seniority,
               excluded_companies, excluded_roles, is_admin_only
        from preference_presets where id = %s::uuid
        """,
        (preset_id,),
    )
    return rows[0] if rows else None


def create_preset(
    settings: Settings,
    *,
    created_by: str,
    name: str,
    description: str = "",
    fields: dict[str, list[str]] | None = None,
    is_admin_only: bool = False,
) -> dict[str, Any]:
    values = preset_fields(fields or {})
    existing = query(settings, "select id from preference_presets where name = %s", (name,))
    if existing:
        raise ValueError(f"a preset named '{name}' already exists")
    rows = query(
        settings,
        """
        insert into preference_presets (
            name, description, roles, keywords, locations, seniority,
            excluded_companies, excluded_roles, is_admin_only, created_by
        )
        values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::uuid)
        returning id, name
        """,
        (
            name,
            description,
            values["roles"],
            values["keywords"],
            values["locations"],
            values["seniority"],
            values["excluded_companies"],
            values["excluded_roles"],
            is_admin_only,
            created_by,
        ),
    )
    return rows[0]


def snapshot_user_preferences(
    settings: Settings,
    supabase: Client,
    *,
    source_user_id: str,
    name: str,
    description: str = "",
    is_admin_only: bool = True,
) -> dict[str, Any]:
    """Create a preset by copying a user's CURRENT preferences (used to seed
    'Admin Preference' and for the admin's snapshot button)."""
    response = supabase.table("preferences").select("*").eq("user_id", source_user_id).execute()
    if not response.data:
        raise LookupError("source user has no preferences row")
    source = response.data[0]
    return create_preset(
        settings,
        created_by=source_user_id,
        name=name,
        description=description,
        fields=preset_fields(source),
        is_admin_only=is_admin_only,
    )


def update_preset(settings: Settings, preset_id: str, update: dict[str, Any]) -> None:
    field_map = {k: v for k, v in update.items() if k in PRESET_FIELDS}
    extra = {k: v for k, v in update.items() if k in ("name", "description", "is_admin_only")}
    if not field_map and not extra:
        raise ValueError("nothing to update")
    sets = ["updated_at = now()"]
    params: list[Any] = []
    for key, value in {**field_map, **extra}.items():
        sets.append(f"{key} = %s")
        params.append(value)
    params.append(preset_id)
    query(
        settings,
        f"update preference_presets set {', '.join(sets)} where id = %s::uuid",
        tuple(params),
    )


def delete_preset(settings: Settings, preset_id: str) -> bool:
    rows = query(
        settings,
        "delete from preference_presets where id = %s::uuid returning id",
        (preset_id,),
    )
    return bool(rows)


def apply_preset_to_user(
    settings: Settings,
    supabase: Client,
    *,
    preset_id: str,
    user_id: str,
) -> dict[str, Any]:
    """Overwrite the user's preference ARRAYS with the preset's. Notification
    flags (channels/scopes/frequency) are intentionally left untouched."""
    preset = get_preset(settings, preset_id)
    if not preset:
        raise LookupError("preset not found")
    values = preset_fields(preset)
    supabase.table("preferences").upsert(
        [
            {
                "user_id": user_id,
                **values,
                "updated_at": datetime.now(UTC).isoformat(),
            }
        ],
        on_conflict="user_id",
    ).execute()
    return {"preset": preset["name"], "applied_to": user_id, **values}
