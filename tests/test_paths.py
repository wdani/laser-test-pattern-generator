import os
import sys
import unittest
import uuid
from pathlib import Path

from laser_test_pattern_generator.paths import (
    config_dir,
    is_macos_app_bundle,
    package_dir,
    prepare_app_launch_environment,
    startup_log_path,
)
from run_gui import write_startup_diagnostics


class PathTests(unittest.TestCase):
    def test_package_dir_for_frozen_macos_app_uses_package_folder(self):
        original_executable = sys.executable
        had_frozen = hasattr(sys, "frozen")
        original_frozen = getattr(sys, "frozen", None)
        package_root = Path("build") / "Laser_Test_Pattern_Generator_macos"
        executable = package_root / "LaserTestPatternGenerator.app" / "Contents" / "MacOS" / "LaserTestPatternGenerator"

        try:
            sys.frozen = True
            sys.executable = str(executable)

            self.assertEqual(package_dir(), package_root.resolve())
        finally:
            sys.executable = original_executable
            if had_frozen:
                sys.frozen = original_frozen
            else:
                delattr(sys, "frozen")

    def test_frozen_macos_app_bundle_detection(self):
        original_executable = sys.executable
        had_frozen = hasattr(sys, "frozen")
        original_frozen = getattr(sys, "frozen", None)
        package_root = Path("build") / "Laser_Test_Pattern_Generator_macos"
        executable = package_root / "LaserTestPatternGenerator.app" / "Contents" / "MacOS" / "LaserTestPatternGenerator"

        try:
            sys.frozen = True
            sys.executable = str(executable)

            self.assertTrue(is_macos_app_bundle())
        finally:
            sys.executable = original_executable
            if had_frozen:
                sys.frozen = original_frozen
            else:
                delattr(sys, "frozen")

    def test_startup_log_path_for_frozen_macos_app_uses_user_library(self):
        home = Path("/Users/tester")

        self.assertEqual(
            startup_log_path(platform_name="darwin", frozen=True, home=home, package_root=Path("/Package")),
            home / "Library" / "Logs" / "Laser Test Pattern Generator" / "startup.log",
        )

    def test_config_dir_for_frozen_macos_app_uses_user_application_support(self):
        home = Path("/Users/tester")

        self.assertEqual(
            config_dir(platform_name="darwin", frozen=True, home=home, package_root=Path("/Package")),
            home / "Library" / "Application Support" / "Laser Test Pattern Generator" / "config",
        )

    def test_prepare_app_launch_environment_sets_cwd_for_frozen_app(self):
        original_executable = sys.executable
        had_frozen = hasattr(sys, "frozen")
        original_frozen = getattr(sys, "frozen", None)
        original_cwd = Path.cwd()
        package_root = original_cwd / "tmp" / "path_tests" / uuid.uuid4().hex / "Laser_Test_Pattern_Generator_macos"
        executable = package_root / "LaserTestPatternGenerator.app" / "Contents" / "MacOS" / "LaserTestPatternGenerator"
        executable.parent.mkdir(parents=True, exist_ok=True)

        try:
            sys.frozen = True
            sys.executable = str(executable)

            self.assertEqual(prepare_app_launch_environment(), package_root)
            self.assertEqual(Path.cwd(), package_root)
        finally:
            os.chdir(original_cwd)
            sys.executable = original_executable
            if had_frozen:
                sys.frozen = original_frozen
            else:
                delattr(sys, "frozen")

    def test_write_startup_diagnostics_creates_log_file(self):
        package_root = Path.cwd() / "tmp" / "path_tests" / uuid.uuid4().hex

        try:
            raise RuntimeError("startup boom")
        except RuntimeError as exc:
            log_path = write_startup_diagnostics(exc, package_root)

        self.assertEqual(log_path, package_root / "logs" / "startup.log")
        text = log_path.read_text(encoding="utf-8")
        self.assertIn("startup boom", text)
        self.assertIn("traceback:", text)
        self.assertIn("sys.executable:", text)


if __name__ == "__main__":
    unittest.main()
