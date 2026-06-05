import unittest
from pathlib import Path

import makera_material_test_generator as generator


def generate_nc_text(profile: str) -> str:
    temp_root = Path(__file__).resolve().parents[1] / "tmp"
    temp_root.mkdir(exist_ok=True)
    output = temp_root / f"{generator.sanitize_filename_part(profile)}_power_profile_test.nc"
    settings = generator.GeneratorSettings(
        output_path=output,
        output_format="NC",
        overwrite_existing=True,
        rows=1,
        cols=2,
        speed_min=1000,
        speed_max=1000,
        power_min=20,
        power_max=40,
        tile_size=1,
        gap=0,
        grid_x=0,
        grid_y=0,
        auto_position=False,
        labels_enabled=False,
        nc_power_profile=profile,
        nc_s_max=9999,
    )
    generator.generate_generic_nc(settings)
    return output.read_text(encoding="utf-8")


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


if __name__ == "__main__":
    unittest.main()
