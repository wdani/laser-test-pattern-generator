from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping, Sequence

from .paths import make_unique_output_path
from .settings import APP_VERSION, GeneratorSettings


JOB_MANIFEST_SCHEMA_VERSION = 1
JOB_MANIFEST_TYPE = "laser_test_pattern_generator.job_manifest"


def manifest_path_for_output(output_path: Path) -> Path:
    return output_path.with_name(f"{output_path.stem}.manifest.json")


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def portable_path(path: Path, base_dir: Path) -> str:
    try:
        return str(path.resolve().relative_to(base_dir.resolve()))
    except Exception:
        return str(path)


def output_format_from_info(info: Mapping[str, object], output_path: Path) -> str:
    explicit_format = str(info.get("format", "")).strip()
    if explicit_format:
        return explicit_format

    suffix = output_path.suffix.lower()
    if suffix == ".mks":
        return "MKS"
    if suffix == ".nc":
        return "NC"
    return ""


def generated_output_entries(infos: Sequence[Mapping[str, object]], manifest_dir: Path) -> list:
    entries = []
    for info in infos:
        output = Path(str(info["output"]))
        entries.append(
            {
                "format": output_format_from_info(info, output),
                "path": portable_path(output, manifest_dir),
            }
        )
    return entries


def job_manifest_data(
    settings: GeneratorSettings,
    infos: Sequence[Mapping[str, object]],
    source: str,
    manifest_path: Path,
    created_at: str | None = None,
) -> dict:
    manifest_dir = manifest_path.parent
    return {
        "schema_version": JOB_MANIFEST_SCHEMA_VERSION,
        "manifest_type": JOB_MANIFEST_TYPE,
        "app_name": "Laser Test Pattern Generator",
        "app_version": APP_VERSION,
        "created_at": created_at or utc_timestamp(),
        "source": source,
        "output_format": settings.output_format,
        "generated_outputs": generated_output_entries(infos, manifest_dir),
        "settings": {
            "material_name": settings.material_name,
            "rows": int(settings.rows),
            "cols": int(settings.cols),
            "tile_size": settings.tile_size,
            "gap": settings.gap,
            "stock_x": settings.stock_x,
            "stock_y": settings.stock_y,
            "stock_z": settings.stock_z,
            "speed_min": settings.speed_min,
            "speed_max": settings.speed_max,
            "power_min": settings.power_min,
            "power_max": settings.power_max,
            "laser_mode": settings.tile_mode_name,
            "line_interval": settings.line_interval,
            "passes": int(settings.passes),
            "bidirectional": bool(settings.bidirectional),
            "scan_angle": settings.scan_angle,
            "labels_enabled": bool(settings.labels_enabled),
            "language": settings.language,
            "nc_power_profile": settings.nc_power_profile,
            "nc_s_max": settings.nc_s_max,
            "nc_units": settings.nc_units,
            "nc_include_labels": bool(settings.nc_include_labels),
        },
    }


def write_job_manifest(settings: GeneratorSettings, infos: Sequence[Mapping[str, object]], source: str) -> dict:
    if not infos:
        raise ValueError("cannot write job manifest without generated outputs")

    first_output = Path(str(infos[0]["output"]))
    manifest_path = manifest_path_for_output(first_output)
    if not settings.overwrite_existing:
        manifest_path = make_unique_output_path(manifest_path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    data = job_manifest_data(settings, infos, source=source, manifest_path=manifest_path)
    manifest_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "output": str(manifest_path),
        "format": "manifest",
        "schema_version": JOB_MANIFEST_SCHEMA_VERSION,
    }
