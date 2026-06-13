import json
import subprocess
import unittest
import uuid
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

from laser_test_pattern_generator import app
from laser_test_pattern_generator.job_manifest import manifest_path_for_output


class MakeraStudioNcTests(unittest.TestCase):
    def run_app_result(self, args: list[str]) -> tuple[int, str, str]:
        stdout = StringIO()
        stderr = StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = app.main(args)
        return exit_code, stdout.getvalue(), stderr.getvalue()

    def run_app(self, args: list[str]) -> str:
        exit_code, stdout, stderr = self.run_app_result(args)
        self.assertEqual(exit_code, 0, stdout + stderr)
        return stdout

    def unique_root(self) -> Path:
        root = Path(__file__).resolve().parents[1] / "tmp" / "makera_studio_nc_tests" / uuid.uuid4().hex
        root.mkdir(parents=True, exist_ok=True)
        return root

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
        root = self.unique_root()
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
        root = self.unique_root()
        text = self.generate_text(root, "--no-labels")

        self.assertNotRegex(text, r"(?m)^M3 S")
        self.assertRegex(text, r"(?m)^G1 X\S+ Y\S+ S0\.2 F2200")
        self.assertIn("G1 S0", text)

    def test_labels_are_present_when_enabled(self):
        root = self.unique_root()
        text = self.generate_text(root)

        self.assertIn(";@MKR|TOOLPATH_START|toolpath_number=1", text)
        self.assertIn("; Tile row=1 col=1", text)
        self.assertIn(";@MKR|TOOLPATH_START|toolpath_number=2", text)
        self.assertIn("S0.25 F2500", text)

    def test_labels_absent_starts_first_tile_at_toolpath_one_when_disabled(self):
        root = self.unique_root()
        text = self.generate_text(root, "--no-labels")

        self.assertIn("; Tile row=1 col=1", text)
        self.assertEqual(text.count(";@MKR|TOOLPATH_START|toolpath_number="), 1)
        self.assertIn(";@MKR|TOOLPATH_START|toolpath_number=1", text)
        self.assertNotIn("S0.25 F2500", text)

    def test_line_mode_emits_connected_outline_path(self):
        root = self.unique_root()
        text = self.generate_text(root, "--no-labels", "--mode", "Line")

        self.assertIn("G0 X10 Y20", text)
        self.assertIn("G1 X14 Y20 S0.2 F2200", text)
        self.assertIn("G1 X14 Y24", text)
        self.assertIn("G1 X10 Y24", text)
        self.assertIn("G1 X10 Y20", text)

    def test_fill_mode_emits_scanlines_plus_outline(self):
        root = self.unique_root()
        text = self.generate_text(root, "--no-labels", "--mode", "Fill", "--line-interval", "2")

        self.assertIn("G0 X10 Y21", text)
        self.assertIn("G1 X14 Y21 S0.2 F2200", text)
        self.assertIn("G0 X14 Y23", text)
        self.assertIn("G1 X10 Y23 S0.2 F2200", text)
        self.assertIn("G0 X10 Y20", text)
        self.assertEqual(text.count("G1 X14 Y20 S0.2 F2200"), 1)
        self.assertIn("G1 X14 Y24", text)

    def test_fill_scanlines_do_not_duplicate_outline_boundary(self):
        root = self.unique_root()
        text = self.generate_text(root, "--no-labels", "--mode", "Fill", "--line-interval", "2")

        self.assertNotIn("G0 X10 Y24\nG1 X14 Y24 S0.2 F2200", text)
        self.assertEqual(text.count("G1 X14 Y20 S0.2 F2200"), 1)
        self.assertEqual(text.count("G1 X14 Y21 S0.2 F2200"), 1)
        self.assertEqual(text.count("G1 X10 Y23 S0.2 F2200"), 1)

    def test_fill_mode_respects_no_bidirectional(self):
        root = self.unique_root()
        text = self.generate_text(root, "--no-labels", "--mode", "Fill", "--line-interval", "2", "--no-bidirectional")

        self.assertIn("G0 X10 Y21", text)
        self.assertIn("G0 X10 Y23", text)
        self.assertNotIn("G0 X10 Y24\nG1 X14 Y24 S0.2 F2200", text)

    def test_fill_mode_respects_nonzero_scan_angle(self):
        root = self.unique_root()
        text = self.generate_text(root, "--no-labels", "--mode", "Fill", "--line-interval", "2", "--scan-angle", "45")

        self.assertRegex(text, r"G0 X1[0-4](?:\.\d+)? Y2[0-4](?:\.\d+)?")
        self.assertRegex(text, r"G1 X1[0-4](?:\.\d+)? Y2[0-4](?:\.\d+)? S0\.2 F2200")
        self.assertEqual(text.count("G1 X14 Y20 S0.2 F2200"), 1)

    def test_fill_mode_respects_indent_distance(self):
        root = self.unique_root()
        text = self.generate_text(root, "--no-labels", "--mode", "Fill", "--line-interval", "2", "--indent-distance", "1")

        self.assertIn("G0 X11 Y22", text)
        self.assertIn("G1 X13 Y22 S0.2 F2200", text)
        self.assertIn("G0 X11 Y21", text)
        self.assertEqual(text.count("G1 X13 Y21 S0.2 F2200"), 1)
        self.assertIn("G1 X13 Y23", text)
        self.assertNotIn("G0 X10 Y20", text)

    def test_offset_fill_emits_one_connected_contour_path_per_pass(self):
        root = self.unique_root()
        text = self.generate_text(root, "--no-labels", "--mode", "Offset Fill", "--tile-size", "8", "--line-interval", "1", "--indent-distance", "1")

        xy_rapids = [line for line in text.splitlines() if line.startswith("G0 X")]
        laser_offs = [line for line in text.splitlines() if line == "G1 S0"]
        self.assertEqual(len(xy_rapids), 1)
        self.assertEqual(len(laser_offs), 1)
        self.assertIn("G0 X16 Y22", text)
        self.assertIn("G1 X16 Y26 S0.2 F2200", text)
        self.assertIn("G1 X15 Y23", text)
        self.assertNotIn("G0 X10 Y20", text)

    def test_offset_fill_repeats_one_connected_path_per_pass(self):
        root = self.unique_root()
        text = self.generate_text(root, "--no-labels", "--mode", "Offset Fill", "--tile-size", "8", "--line-interval", "1", "--indent-distance", "1", "--passes", "2")

        xy_rapids = [line for line in text.splitlines() if line.startswith("G0 X")]
        laser_offs = [line for line in text.splitlines() if line == "G1 S0"]
        self.assertEqual(len(xy_rapids), 2)
        self.assertEqual(len(laser_offs), 2)

    def test_passes_repeat_geometry_deterministically(self):
        root = self.unique_root()
        one_pass = self.generate_text(root, "--no-labels", "--mode", "Line", "--passes", "1")
        two_passes = self.generate_text(root, "--no-labels", "--mode", "Line", "--passes", "2")

        self.assertEqual(two_passes.count("G1 X14 Y20 S0.2 F2200"), one_pass.count("G1 X14 Y20 S0.2 F2200") * 2)

        one_fill = self.generate_text(root, "--no-labels", "--mode", "Fill", "--line-interval", "2", "--passes", "1")
        two_fill = self.generate_text(root, "--no-labels", "--mode", "Fill", "--line-interval", "2", "--passes", "2")
        self.assertEqual(two_fill.count("G1 X14 Y20 S0.2 F2200"), one_fill.count("G1 X14 Y20 S0.2 F2200") * 2)

    def test_z_offset_setting_does_not_change_makera_studio_nc_g0_z0(self):
        root = self.unique_root()
        text = self.generate_text(root, "--no-labels", "--z-offset", "2")

        self.assertIn("G0 Z0", text)
        self.assertNotIn("G0 Z2", text)

    def test_api_generate_returns_makera_studio_flavor_metadata(self):
        root = self.unique_root()
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
        root = self.unique_root()
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

    def test_cli_invalid_indent_fails_cleanly_and_writes_no_file(self):
        root = self.unique_root()
        output_path = root / "invalid_indent.nc"
        exit_code, stdout, stderr = self.run_app_result(
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
                "--indent-distance",
                "3",
                "--no-labels",
            ]
        )

        self.assertEqual(exit_code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("Makera Studio NC generation error: Indent distance is too large for the tile size.", stderr)
        self.assertFalse(output_path.exists())

    def test_api_invalid_indent_fails_cleanly_and_writes_no_file(self):
        root = self.unique_root()
        output_path = root / "api_invalid_indent.nc"
        exit_code, stdout, stderr = self.run_app_result(
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
                "--tile-size",
                "4",
                "--indent-distance",
                "3",
                "--no-labels",
            ]
        )

        self.assertEqual(exit_code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("Makera Studio NC generation error: Indent distance is too large for the tile size.", stderr)
        self.assertFalse(output_path.exists())

    def test_temp_reference_folder_is_ignored_and_not_tracked(self):
        repo_root = Path(__file__).resolve().parents[1]
        gitignore = (repo_root / ".gitignore").read_text(encoding="utf-8")
        self.assertRegex(gitignore, r"(?m)^temp/$")

        result = subprocess.run(
            ["git", "ls-files", "temp"],
            cwd=repo_root,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            self.skipTest("git ls-files is not available in this test environment")
        self.assertEqual(result.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
