from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


MATERIAL_RESULT_SCHEMA_VERSION = 1
DEFAULT_RESULT_LOG_PATH = Path("material_test_results.jsonl")
RESULT_RATINGS = ("good", "too_light", "too_dark", "burned", "unclear")


class MaterialLogError(ValueError):
    pass


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def clean_optional_text(value: object) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def clean_required_text(value: object, field_name: str) -> str:
    text = clean_optional_text(value)
    if text is None:
        raise MaterialLogError(f"{field_name} is required")
    return text


def clean_optional_number(value: object) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise MaterialLogError(f"expected a number, got {value!r}") from exc


def clean_optional_path(value: object) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def build_material_result_entry(
    *,
    app_version: str,
    material_name: object,
    result_rating: object,
    source: str,
    machine_name: object = None,
    laser_module: object = None,
    manifest_path: object = None,
    generated_output_path: object = None,
    selected_speed: object = None,
    selected_power: object = None,
    notes: object = None,
    photo_path: object = None,
    created_at: Optional[str] = None,
) -> dict:
    material = clean_required_text(material_name, "material_name")
    rating = clean_required_text(result_rating, "result_rating")
    if rating not in RESULT_RATINGS:
        raise MaterialLogError(f"result_rating must be one of: {', '.join(RESULT_RATINGS)}")

    entry = {
        "schema_version": MATERIAL_RESULT_SCHEMA_VERSION,
        "app_version": app_version,
        "created_at": created_at or utc_timestamp(),
        "material_name": material,
        "source": clean_required_text(source, "source"),
        "result_rating": rating,
    }

    optional_fields = {
        "machine_name": clean_optional_text(machine_name),
        "laser_module": clean_optional_text(laser_module),
        "manifest_path": clean_optional_path(manifest_path),
        "generated_output_path": clean_optional_path(generated_output_path),
        "selected_speed": clean_optional_number(selected_speed),
        "selected_power": clean_optional_number(selected_power),
        "notes": clean_optional_text(notes),
        "photo_path": clean_optional_path(photo_path),
    }

    for key, value in optional_fields.items():
        if value is not None:
            entry[key] = value

    return entry


def append_material_result(log_path: Path, entry: dict) -> Path:
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
    return path


def read_material_result_log(log_path: Path) -> list:
    path = Path(log_path)
    if not path.exists():
        return []

    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            entries.append(json.loads(line))
    return entries
