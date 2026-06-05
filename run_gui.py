#!/usr/bin/env python3
"""GUI-only launcher for Python and Windows PyInstaller builds."""

from laser_test_pattern_generator.gui import GeneratorGui


def main() -> int:
    gui = GeneratorGui()
    gui.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
