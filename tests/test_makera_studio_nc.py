import json
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from laser_test_pattern_generator import app
from laser_test_pattern_generator.job_manifest import manifest_path_for_output


class MakeraStudioNcTests(unittest.TestCase):
    def run_app(self, args: list[str]) -> str:
        output = StringIO()
        with redirect_stdout(output):
            exit_code = app.main(args)
        self.assertEqual(exit_code, 0, output.getvalue())
        return output.getvalue()

    def generate_text(self, tmp_path: Path, *extra_args: str) -> str:
        output_path = tmp_path / "makera_studio.nc"
        self.run_app(
            [
                "--format",
                "NC",
                "--nc-flavor",
                "makera-studio",
                "--output",
                str(output_path),
                "--overwrite",
                "--rows",
                "1",
                "--cols",
                "1",
                "--tile-size",
                "4",
                "--gap",
                "0",
                "--no-auto-position",
                "--grid-x",
                "10",
                "--grid-y",
                "20",
                *extra_args,
            ]
        )
        return output_path.read_text(encoding="utf-8")

    def test_makera_studio_nc_header_footer_and_start_sequence(self):
        root = Path(__file__).resolve().parents[1] / "tmp" / "makera_studio_nc_tests"
        root.mkdir(parents=True, exist_ok=True)
        text = self.generate_text(root, "--no-labels")

        for expected in [
            ";@MKR|BEGIN",
            ";@MKR|SCHEMA|v=1.0.0",
            ";@MKR|MACHINE|id=C1|name=Carvera",
            ";@MKR|MATERIAL|",
            ";@MKR|STOCK|",
            ";@MKR|CAM|id=laser-test-pattern-generator",
            "G90 G21",
            ";@MKR|TOOLPATH_START|toolpath_number=1",
            "M321",
            "G0 Z0",
            "M3",
            "M322",
            "G28",
            "M02",
        ]:
            self.assertIn(expected, text)

    def test_makera_studio_nc_uses_makera_cutting_style_not_generic_m3_s_segments(self):
        root = Path(__file__).resolve().parents[1] / "tmp" / "makera_studio_nc_tests"
        root.mkdir(parents=True, exist_ok=True)
        text = self.generate_text(root, "--no-labels")

        self.assertNotRegex(text, r"(?m)^M3 S")
        self.assertRegex(text, r"(?m)^G1 X\S+ Y\S+ S0\.2 F2200")
        self.assertIn("G1 S0", text)

    def test_labels_are_present_when_enabled(self):
        root = Path(__file__).resolve().parents[1] / "tmp" / "makera_studio_nc_tests"
        root.mkdir(parents=True, exist_ok=True)
        text = self.generate_text(root)

        self.assertIn(";@MKR|TOOLPATH_START|toolpath_number=1", text)
        self.assertIn("; Tile row=1 col=1", text)
        self.assertIn(";@MKR|TOOLPATH_START|toolpath_number=2", text)
        self.assertIn("S0.25 F2500", text)

    def test_labels_absent_starts_first_tile_at_toolpath_one_when_disabled(self):
        root = Path(__file__).resolve().parents[1] / "tmp" / "makera_studio_nc_tests"
        root.mkdir(parents=True, exist_ok=True)
        text = self.generate_text(root, "--no-labels")

        self.assertIn("; Tile row=1 col=1", text)
        self.assertEqual(text.count(";@MKR|TOOLPATH_START|toolpath_number="), 1)
        self.assertIn(";@MKR|TOOLPATH_START|toolpath_number=1", text)
        self.assertNotIn("S0.25 F2500", text)

    def test_line_mode_emits_connected_outline_path(self):
        root = Path(__file__).resolve().parents[1] / "tmp" / "makera_studio_nc_tests"
        root.mkdir(parents=True, exist_ok=True)
        text = self.generate_text(root, "--no-labels", "--mode", "Line")

        self.assertIn("G0 X10 Y20", text)
        self.assertIn("G1 X14 Y20 S0.2 F2200", text)
        self.assertIn("G1 X14 Y24", text)
        self.assertIn("G1 X10 Y24", text)
        self.assertIn("G1 X10 Y20", text)

    def test_fill_mode_emits_scanlines_plus_outline(self):
        root = Path(__file__).resolve().parents[1] / "tmp" / "makera_studio_nc_tests"
        root.mkdir(parents=True, exist_ok=True)
        text = self.generate_text(root, "--no-labels", "--mode", "Fill", "--line-interval", "2")

        self.assertIn("G0 X10 Y20", text)
        self.assertIn("G1 X14 Y20 S0.2 F2200", text)
        self.assertIn("G0 X14 Y22", text)
        self.assertIn("G1 X10 Y22 S0.2 F2200", text)
        self.assertIn("G1 X14 Y24", text)

    def test_fill_mode_respects_no_bidirectional(self):
        root = Path(__file__).resolve().parents[1] / "tmp" / "makera_studio_nc_tests"
        root.mkdir(parents=True, exist_ok=True)
        text = self.generate_text(root, "--no-labels", "--mode", "Fill", "--line-interval", "2", "--no-bidirectional")

        self.assertIn("G0 X10 Y20", text)
        self.assertIn("G0 X10 Y22", text)
        self.assertIn("G0 X10 Y24", text)

    def test_fill_mode_respects_nonzero_scan_angle(self):
        root = Path(__file__).resolve().parents[1] / "tmp" / "makera_studio_nc_tests"
        root.mkdir(parents=True, exist_ok=True)
        text = self.generate_text(root, "--no-labels", "--mode", "Fill", "--line-interval", "2", "--scan-angle", "45")

        self.assertIn("G0 X14 Y22.8284", text)
        self.assertIn("G1 X11.1716 Y20 S0.2 F2200", text)

    def test_fill_mode_respects_indent_distance(self):
        root = Path(__file__).resolve().parents[1] / "tmp" / "makera_studio_nc_tests"
        root.mkdir(parents=True, exist_ok=True)
        text = self.generate_text(root, "--no-labels", "--mode", "Fill", "--line-interval", "2", "--indent-distance", "1")

        self.assertIn("G0 X11 Y21", text)
        self.assertIn("G1 X13 Y21 S0.2 F2200", text)
        self.assertIn("G1 X13 Y23", text)
        self.assertNotIn("G0 X10 Y20", text)

    def test_offset_fill_emits_nested_contours_and_respects_indent(self):
        root = Path(__file__).resolve().parents[1] / "tmp" / "makera_studio_nc_tests"
        root.mkdir(parents=True, exist_ok=True)
        text = self.generate_text(root, "--no-labels", "--mode", "Offset Fill", "--tile-size", "6", "--line-interval", "1", "--indent-distance", "1")

        self.assertIn("G0 X12 Y22", text)
        self.assertIn("G1 X14 Y22 S0.2 F2200", text)
        self.assertNotIn("G0 X10 Y20", text)

    def test_passes_repeat_geometry_deterministically(self):
        root = Path(__file__).resolve().parents[1] / "tmp" / "makera_studio_nc_tests"
        root.mkdir(parents=True, exist_ok=True)
        one_pass = self.generate_text(root, "--no-labels", "--mode", "Line", "--passes", "1")
        two_passes = self.generate_text(root, "--no-labels", "--mode", "Line", "--passes", "2")

        self.assertEqual(two_passes.count("G1 X14 Y20 S0.2 F2200"), one_pass.count("G1 X14 Y20 S0.2 F2200") * 2)

        one_fill = self.generate_text(root, "--no-labels", "--mode", "Fill", "--line-interval", "2", "--passes", "1")
        two_fill = self.generate_text(root, "--no-labels", "--mode", "Fill", "--line-interval", "2", "--passes", "2")
        self.assertEqual(two_fill.count("G1 X14 Y20 S0.2 F2200"), one_fill.count("G1 X14 Y20 S0.2 F2200") * 2)

    def test_z_offset_setting_does_not_change_makera_studio_nc_g0_z0(self):
        root = Path(__file__).resolve().parents[1] / "tmp" / "makera_studio_nc_tests"
        root.mkdir(parents=True, exist_ok=True)
        text = self.generate_text(root, "--no-labels", "--z-offset", "2")

        self.assertIn("G0 Z0", text)
        self.assertNotIn("G0 Z2", text)

    def test_api_generate_returns_makera_studio_flavor_metadata(self):
        root = Path(__file__).resolve().parents[1] / "tmp" / "makera_studio_nc_tests"
        root.mkdir(parents=True, exist_ok=True)
        output_path = root / "api_makera.nc"
        stdout = self.run_app(
            [
                "--api",
                "generate",
                "--format",
                "NC",
                "--nc-flavor",
                "makera-studio",
                "--output",
                str(output_path),
                "--overwrite",
                "--rows",
                "1",
                "--cols",
                "1",
                "--no-labels",
            ]
        )

        data = json.loads(stdout)
        self.assertEqual(data["result"]["format"], "NC")
        self.assertEqual(data["result"]["nc_flavor"], "makera-studio")

    def test_job_manifest_includes_makera_studio_nc_settings(self):
        root = Path(__file__).resolve().parents[1] / "tmp" / "makera_studio_nc_tests"
        root.mkdir(parents=True, exist_ok=True)
        output_path = root / "manifest_makera.nc"
        self.run_app(
            [
                "--format",
                "NC",
                "--nc-flavor",
                "makera-studio",
                "--output",
                str(output_path),
                "--overwrite",
                "--write-manifest",
                "--z-offset",
                "2",
                "--indent-distance",
                "1",
                "--rows",
                "1",
                "--cols",
                "1",
                "--no-labels",
            ]
        )

        data = json.loads(manifest_path_for_output(output_path).read_text(encoding="utf-8"))
        self.assertEqual(data["settings"]["nc_flavor"], "makera-studio")
        self.assertEqual(data["settings"]["z_offset"], 2.0)
        self.assertEqual(data["settings"]["indent_distance"], 1.0)


if __name__ == "__main__":
    unittest.main()
