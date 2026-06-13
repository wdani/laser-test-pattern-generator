from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from .paths import config_dir
from .update_check import default_update_preferences


THEME_CHOICES = ("Light", "Dark")
DEFAULT_UI_THEME = "Light"


def normalize_theme_name(theme: object) -> str:
    text = str(theme or "").strip().title()
    return text if text in THEME_CHOICES else DEFAULT_UI_THEME


def default_ui_settings_path() -> Path:
    return config_dir() / "ui_settings.json"


def default_ui_settings() -> Dict[str, object]:
    settings = {"theme": DEFAULT_UI_THEME}
    settings.update(default_update_preferences())
    return settings


def normalize_ui_settings(data: object) -> Dict[str, object]:
    settings = default_ui_settings()
    if not isinstance(data, dict):
        return settings

    settings["theme"] = normalize_theme_name(data.get("theme"))
    settings["update_check_on_startup"] = data.get("update_check_on_startup") is True

    for key in ("update_last_checked", "update_snooze_until", "update_ignored_version"):
        value = data.get(key, "")
        settings[key] = str(value).strip() if value is not None else ""

    return settings


def load_ui_settings(path: Optional[Path] = None) -> Dict[str, object]:
    settings_path = Path(path) if path is not None else default_ui_settings_path()
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    except Exception:
        return default_ui_settings()

    return normalize_ui_settings(data)


def save_ui_settings(settings: Dict[str, object], path: Optional[Path] = None) -> Path:
    settings_path = Path(path) if path is not None else default_ui_settings_path()
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    existing = load_ui_settings(settings_path) if settings_path.exists() else default_ui_settings()
    existing.update(settings)
    data = normalize_ui_settings(existing)

    settings_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return settings_path
