from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .paths import resource_dir, sanitize_filename_part


PRESET_METADATA_FIELDS = (
    "name",
    "material",
    "machine",
    "laser_module",
    "notes",
    "safety_note",
    "reference_image",
)
LEGACY_PRESET_NAME_FIELD = "_preset_name"


def preset_dir() -> Path:
    d = resource_dir("presets")
    d.mkdir(exist_ok=True)
    return d


def preset_path(name: str, directory: Optional[Path] = None) -> Path:
    safe = sanitize_filename_part(name)
    return (directory or preset_dir()) / f"{safe}.json"


def read_preset_file(path: Path) -> Dict[str, object]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Preset JSON must contain an object")
    return data


def preset_display_name(data: Dict[str, object], path: Optional[Path] = None) -> str:
    for key in ("name", LEGACY_PRESET_NAME_FIELD):
        value = str(data.get(key) or "").strip()
        if value:
            return value
    return path.stem if path is not None else "Untitled preset"


def normalize_preset_data(data: Dict[str, object], name: Optional[str] = None) -> Dict[str, object]:
    normalized = dict(data)
    display_name = (name or preset_display_name(normalized)).strip()
    if display_name:
        normalized["name"] = display_name
        normalized[LEGACY_PRESET_NAME_FIELD] = display_name
    return normalized


def list_presets(directory: Optional[Path] = None) -> List[Tuple[str, Path]]:
    root = directory or preset_dir()
    result: List[Tuple[str, Path]] = []
    for path in sorted(root.glob("*.json")):
        try:
            data = read_preset_file(path)
            result.append((preset_display_name(data, path), path))
        except Exception:
            result.append((path.stem, path))
    return result


def find_preset_path(name: str, directory: Optional[Path] = None) -> Path:
    root = directory or preset_dir()
    direct = preset_path(name, root)
    if direct.exists():
        return direct

    for display_name, path in list_presets(root):
        if display_name == name:
            return path
    return direct


def write_preset_file(path: Path, data: Dict[str, object], name: Optional[str] = None) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    normalized = normalize_preset_data(data, name)
    out.write_text(json.dumps(normalized, indent=2), encoding="utf-8")
    return out


def save_preset_data(
    name: str,
    data: Dict[str, object],
    directory: Optional[Path] = None,
    overwrite: bool = True,
) -> Path:
    root = directory or preset_dir()
    root.mkdir(parents=True, exist_ok=True)
    path = find_preset_path(name, root)
    if path.exists() and not overwrite:
        raise FileExistsError(f"Preset already exists: {path}")
    return write_preset_file(path, data, name)


def import_preset_file(
    source: Path,
    directory: Optional[Path] = None,
    name: Optional[str] = None,
    overwrite: bool = True,
) -> Path:
    data = read_preset_file(source)
    return save_preset_data(name or preset_display_name(data, Path(source)), data, directory, overwrite=overwrite)


def export_preset_file(name: str, destination: Path, directory: Optional[Path] = None) -> Path:
    source = find_preset_path(name, directory)
    if not source.exists():
        raise FileNotFoundError(f"Preset not found: {name}")

    out = Path(destination)
    if out.suffix.lower() != ".json":
        out = out.with_suffix(".json")
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, out)
    return out


def metadata_subset(data: Dict[str, object]) -> Dict[str, object]:
    return {key: data.get(key, "") for key in PRESET_METADATA_FIELDS}
