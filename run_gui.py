#!/usr/bin/env python3
"""GUI-only launcher for the Windows PyInstaller build."""

from makera_material_test_generator import GeneratorGui


def main() -> int:
    gui = GeneratorGui()
    gui.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
