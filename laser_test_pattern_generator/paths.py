from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Optional

from .settings import GeneratorSettings

GENERATED_OUTPUT_SUFFIXES = {".mks", ".nc"}


def package_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


def resource_dir(name: str) -> Path:
    external = package_dir() / name
    if external.exists():
        return external

    bundled_root = getattr(sys, "_MEIPASS", None)
    if bundled_root:
        bundled = Path(bundled_root).resolve() / name
        if bundled.exists():
            return bundled

    return external


def default_template_dir() -> Path:
    return resource_dir("templates")


def make_unique_output_path(path: Path) -> Path:
    """Return path if free; otherwise append _001, _002, ... before the suffix."""
    if not path.exists():
        return path

    parent = path.parent
    stem = path.stem
    suffix = path.suffix or ".mks"

    for i in range(1, 10000):
        candidate = parent / f"{stem}_{i:03d}{suffix}"
        if not candidate.exists():
            return candidate

    raise FileExistsError(f"Could not find a free filename for {path}")



def sanitize_filename_part(text: str) -> str:
    """Make a short safe filename part."""
    text = str(text).strip().lower()
    text = re.sub(r"[^a-z0-9._-]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "material"


def fmt_filename_number(value: float) -> str:
    """Format numbers for filenames without ugly decimals."""
    try:
        f = float(value)
        if f.is_integer():
            return str(int(f))
        return f"{f:g}".replace(".", "p")
    except Exception:
        return sanitize_filename_part(str(value))


def build_auto_filename(settings: GeneratorSettings, suffix: str) -> str:
    material = sanitize_filename_part(settings.material_name)
    mode = sanitize_filename_part(settings.tile_mode_name.replace(" ", "-"))
    parts = [
        material,
        f"{int(settings.rows)}x{int(settings.cols)}",
        f"s{fmt_filename_number(settings.speed_min)}-{fmt_filename_number(settings.speed_max)}",
        f"p{fmt_filename_number(settings.power_min)}-{fmt_filename_number(settings.power_max)}",
        mode,
    ]
    return "_".join(parts) + suffix


def expected_output_suffix_for_format(output_format: str) -> str:
    """Return the visible GUI output suffix for a selected format."""
    return ".nc" if output_format == "NC" else ".mks"


def sync_output_suffix_for_format(path_text: str, output_format: str) -> str:
    """Adjust known generated output suffixes while leaving custom suffixes alone."""
    text = str(path_text).strip()
    if not text:
        return text

    expected_suffix = expected_output_suffix_for_format(output_format)
    path = Path(text)
    suffix = path.suffix.lower()

    if suffix in GENERATED_OUTPUT_SUFFIXES or not suffix:
        return str(path.with_suffix(expected_suffix))
    return text


def resolve_output_path(path: Path, overwrite_existing: bool, suffix: Optional[str] = None, settings: Optional[GeneratorSettings] = None) -> Path:
    """Resolve output path, optionally auto-generating a filename and avoiding overwrite."""
    out = path

    if settings is not None and settings.auto_filename:
        base_dir = out if out.suffix == "" else out.parent
        out = base_dir / build_auto_filename(settings, suffix or ".mks")
    elif suffix:
        out = out.with_suffix(suffix)

    if not overwrite_existing:
        out = make_unique_output_path(out)

    out.parent.mkdir(parents=True, exist_ok=True)
    return out


