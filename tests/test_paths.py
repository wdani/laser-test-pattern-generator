import sys
import unittest
from pathlib import Path

from laser_test_pattern_generator.paths import package_dir


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


if __name__ == "__main__":
    unittest.main()
