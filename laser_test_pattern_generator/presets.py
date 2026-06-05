from __future__ import annotations

from pathlib import Path

from .paths import package_dir, sanitize_filename_part


def preset_dir() -> Path:
    d = package_dir() / "presets"
    d.mkdir(exist_ok=True)
    return d


def preset_path(name: str) -> Path:
    safe = sanitize_filename_part(name)
    return preset_dir() / f"{safe}.json"
