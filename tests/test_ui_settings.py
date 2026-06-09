import shutil
import unittest
import uuid
from pathlib import Path

from laser_test_pattern_generator.ui_settings import (
    DEFAULT_UI_THEME,
    default_ui_settings,
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
        self.assertFalse(load_ui_settings(path)["update_check_on_startup"])

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

    def test_default_settings_disable_startup_update_check(self):
        self.assertFalse(default_ui_settings()["update_check_on_startup"])

    def test_save_and_load_update_check_settings(self):
        path = self.make_workspace_tmp() / "config" / "ui_settings.json"

        save_ui_settings(
            {
                "theme": "Dark",
                "update_check_on_startup": True,
                "update_last_checked": "2026-06-09",
                "update_snooze_until": "2026-06-19",
                "update_ignored_version": "v1.6.3",
            },
            path,
        )
        data = load_ui_settings(path)

        self.assertEqual(data["theme"], "Dark")
        self.assertTrue(data["update_check_on_startup"])
        self.assertEqual(data["update_last_checked"], "2026-06-09")
        self.assertEqual(data["update_snooze_until"], "2026-06-19")
        self.assertEqual(data["update_ignored_version"], "v1.6.3")

    def test_saving_theme_preserves_update_check_settings(self):
        path = self.make_workspace_tmp() / "config" / "ui_settings.json"

        save_ui_settings({"update_check_on_startup": True, "update_ignored_version": "v1.6.3"}, path)
        save_ui_settings({"theme": "Dark"}, path)
        data = load_ui_settings(path)

        self.assertEqual(data["theme"], "Dark")
        self.assertTrue(data["update_check_on_startup"])
        self.assertEqual(data["update_ignored_version"], "v1.6.3")

    def test_startup_update_check_requires_boolean_true(self):
        path = self.make_workspace_tmp() / "config" / "ui_settings.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('{"update_check_on_startup": "true"}', encoding="utf-8")

        self.assertFalse(load_ui_settings(path)["update_check_on_startup"])


if __name__ == "__main__":
    unittest.main()
