import shutil
import unittest
import uuid
from pathlib import Path

from laser_test_pattern_generator.ui_settings import (
    DEFAULT_UI_THEME,
    load_ui_settings,
    normalize_theme_name,
    save_ui_settings,
)


class UiSettingsTests(unittest.TestCase):
    def make_workspace_tmp(self) -> Path:
        root = Path(__file__).resolve().parents[1] / "tmp" / "ui_settings_tests" / uuid.uuid4().hex
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        return root

    def test_missing_settings_file_uses_default_theme(self):
        path = self.make_workspace_tmp() / "missing.json"

        self.assertEqual(load_ui_settings(path)["theme"], DEFAULT_UI_THEME)

    def test_invalid_settings_file_uses_default_theme(self):
        path = self.make_workspace_tmp() / "broken.json"
        path.write_text("{not json", encoding="utf-8")

        self.assertEqual(load_ui_settings(path)["theme"], DEFAULT_UI_THEME)

    def test_theme_name_is_normalized(self):
        self.assertEqual(normalize_theme_name("dark"), "Dark")
        self.assertEqual(normalize_theme_name("unknown"), DEFAULT_UI_THEME)

    def test_save_and_load_theme_setting(self):
        path = self.make_workspace_tmp() / "config" / "ui_settings.json"

        save_ui_settings({"theme": "Dark"}, path)

        self.assertEqual(load_ui_settings(path)["theme"], "Dark")


if __name__ == "__main__":
    unittest.main()
