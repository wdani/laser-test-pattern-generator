from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from .paths import package_dir


THEME_CHOICES = ("Light", "Dark")
DEFAULT_UI_THEME = "Light"


def normalize_theme_name(theme: object) -> str:
    text = str(theme or "").strip().title()
    return text if text in THEME_CHOICES else DEFAULT_UI_THEME


def default_ui_settings_path() -> Path:
    return package_dir() / "config" / "ui_settings.json"


def load_ui_settings(path: Optional[Path] = None) -> Dict[str, str]:
    settings_path = Path(path) if path is not None else default_ui_settings_path()
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    except Exception:
        return {"theme": DEFAULT_UI_THEME}

    if not isinstance(data, dict):
        return {"theme": DEFAULT_UI_THEME}
    return {"theme": normalize_theme_name(data.get("theme"))}


def save_ui_settings(settings: Dict[str, object], path: Optional[Path] = None) -> Path:
    settings_path = Path(path) if path is not None else default_ui_settings_path()
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    data = {"theme": normalize_theme_name(settings.get("theme"))}
    settings_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return settings_path
