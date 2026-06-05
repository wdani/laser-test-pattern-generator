import re
import unittest
from pathlib import Path

import makera_material_test_generator as generator


def generate_nc_text(profile: str, **overrides) -> str:
    temp_root = Path(__file__).resolve().parents[1] / "tmp"
    temp_root.mkdir(exist_ok=True)
    output = temp_root / f"{generator.sanitize_filename_part(profile)}_power_profile_test.nc"
    settings_data = {
        "output_path": output,
        "output_format": "NC",
        "overwrite_existing": True,
        "rows": 1,
        "cols": 2,
        "speed_min": 1000,
        "speed_max": 1000,
        "power_min": 20,
        "power_max": 40,
        "tile_size": 1,
        "gap": 0,
        "grid_x": 0,
        "grid_y": 0,
        "auto_position": False,
        "labels_enabled": False,
        "nc_power_profile": profile,
        "nc_s_max": 9999,
    }
    settings_data.update(overrides)
    settings = generator.GeneratorSettings(**settings_data)
    generator.generate_generic_nc(settings)
    return output.read_text(encoding="utf-8")


def header_range(text: str, prefix: str, line_suffix: str = "", value_suffix: str = "") -> tuple[str, str]:
    for line in text.splitlines():
        if line.startswith(prefix):
            body = line.removeprefix(prefix).removesuffix(line_suffix)
            left, right = body.split(" - ")
            if value_suffix:
                left = left.removesuffix(value_suffix)
                right = right.removesuffix(value_suffix)
            return left, right
    raise AssertionError(f"Missing header line: {prefix}")


def tile_comment_ranges(text: str) -> tuple[tuple[str, str], tuple[str, str]]:
    matches = re.findall(r"; Tile row=\d+ col=\d+ speed=(\S+) power=(\S+)", text)
    if not matches:
        raise AssertionError("Missing tile comments")

    speeds = [speed for speed, _power in matches]
    powers = [power for _speed, power in matches]
    speed_range = (min(speeds, key=float), max(speeds, key=float))
    power_range = (min(powers, key=float), max(powers, key=float))
    return speed_range, power_range


class NcPowerProfileTests(unittest.TestCase):
    def test_makera_profile_uses_fractional_s_values(self):
        text = generate_nc_text("Makera (0-1)")

        self.assertIn("M3 S0.2", text)
        self.assertIn("M3 S0.4", text)

    def test_grbl_profile_uses_1000_scale_s_values(self):
        text = generate_nc_text("GRBL (0-1000)")

        self.assertIn("M3 S200", text)
        self.assertIn("M3 S400", text)

    def test_header_includes_selected_power_profile(self):
        text = generate_nc_text("GRBL (0-1000)")

        self.assertIn("; NC power profile: GRBL (0-1000)", text)

    def test_header_includes_resolved_nc_s_max(self):
        text = generate_nc_text("GRBL (0-1000)")

        self.assertIn("; NC S max: 1000", text)

    def test_header_uses_rounded_ranges_when_rounding_enabled(self):
        text = generate_nc_text(
            "Makera (0-1)",
            rows=2,
            cols=2,
            speed_min=1000.4,
            speed_max=1002.4,
            power_min=20.4,
            power_max=40.4,
        )

        self.assertIn("; Power range: 20% - 40%", text)
        self.assertIn("; Speed range: 1000 - 1002 mm/min", text)
        self.assertIn("; Tile row=1 col=1 speed=1000 power=20", text)
        self.assertIn("; Tile row=2 col=2 speed=1002 power=40", text)

    def test_header_ranges_match_generated_tile_values(self):
        text = generate_nc_text(
            "Makera (0-1)",
            rows=2,
            cols=2,
            speed_min=1000.4,
            speed_max=1002.4,
            power_min=20.4,
            power_max=40.4,
            round_speed_values=False,
            round_power_values=False,
        )
        tile_speed_range, tile_power_range = tile_comment_ranges(text)

        self.assertEqual(tile_power_range, header_range(text, "; Power range: ", value_suffix="%"))
        self.assertEqual(tile_speed_range, header_range(text, "; Speed range: ", line_suffix=" mm/min"))


if __name__ == "__main__":
    unittest.main()
