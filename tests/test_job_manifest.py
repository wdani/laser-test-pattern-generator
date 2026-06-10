import json
import shutil
import unittest
import uuid
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from laser_test_pattern_generator import app
from laser_test_pattern_generator.job_manifest import generated_output_entries, manifest_path_for_output
from laser_test_pattern_generator.settings import APP_VERSION


class JobManifestTests(unittest.TestCase):
    def make_workspace_tmp(self) -> Path:
        root = Path(__file__).resolve().parents[1] / "tmp" / "job_manifest_tests" / uuid.uuid4().hex
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        return root

    def run_app(self, args: list[str]) -> str:
        output = StringIO()
        with redirect_stdout(output):
            exit_code = app.main(args)
        self.assertEqual(exit_code, 0)
        return output.getvalue()

    def test_manifest_is_not_written_by_default(self):
        root = self.make_workspace_tmp()
        output_path = root / "default.nc"

        self.run_app(
            [
                "--format",
                "NC",
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

        self.assertTrue(output_path.exists())
        self.assertFalse(manifest_path_for_output(output_path).exists())

    def test_manifest_is_written_when_enabled(self):
        root = self.make_workspace_tmp()
        output_path = root / "with_manifest.nc"

        self.run_app(
            [
                "--format",
                "NC",
                "--output",
                str(output_path),
                "--overwrite",
                "--write-manifest",
                "--material-name",
                "cork",
                "--rows",
                "2",
                "--cols",
                "3",
                "--speed-min",
                "1000",
                "--speed-max",
                "1200",
                "--power-min",
                "10",
                "--power-max",
                "30",
                "--tile-size",
                "5",
                "--gap",
                "1",
                "--stock-x",
                "80",
                "--stock-y",
                "60",
                "--mode",
                "Line",
                "--language",
                "Deutsch",
                "--nc-power-profile",
                "GRBL (0-1000)",
                "--no-labels",
            ]
        )

        manifest_path = manifest_path_for_output(output_path)
        self.assertTrue(manifest_path.exists())

        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(data["schema_version"], 1)
        self.assertEqual(data["manifest_type"], "laser_test_pattern_generator.job_manifest")
        self.assertEqual(data["app_version"], APP_VERSION)
        self.assertEqual(data["source"], "cli")
        self.assertEqual(data["output_format"], "NC")
        self.assertEqual(data["generated_outputs"], [{"format": "NC", "path": "with_manifest.nc"}])

        settings = data["settings"]
        self.assertEqual(settings["material_name"], "cork")
        self.assertEqual(settings["rows"], 2)
        self.assertEqual(settings["cols"], 3)
        self.assertEqual(settings["tile_size"], 5.0)
        self.assertEqual(settings["gap"], 1.0)
        self.assertEqual(settings["stock_x"], 80.0)
        self.assertEqual(settings["stock_y"], 60.0)
        self.assertEqual(settings["speed_min"], 1000.0)
        self.assertEqual(settings["speed_max"], 1200.0)
        self.assertEqual(settings["power_min"], 10.0)
        self.assertEqual(settings["power_max"], 30.0)
        self.assertEqual(settings["laser_mode"], "Line")
        self.assertEqual(settings["language"], "Deutsch")
        self.assertEqual(settings["nc_power_profile"], "GRBL (0-1000)")
        self.assertEqual(settings["nc_s_max"], 1000.0)

    def test_api_generate_reports_manifest_path(self):
        root = self.make_workspace_tmp()
        output_path = root / "api_manifest.nc"
        manifest_path = manifest_path_for_output(output_path)

        stdout = self.run_app(
            [
                "--api",
                "generate",
                "--format",
                "NC",
                "--output",
                str(output_path),
                "--overwrite",
                "--write-manifest",
                "--rows",
                "1",
                "--cols",
                "1",
                "--no-labels",
            ]
        )

        data = json.loads(stdout)
        self.assertEqual(data["manifest"]["output"], str(manifest_path))
        self.assertEqual(data["manifest"]["format"], "manifest")
        self.assertTrue(manifest_path.exists())

    def test_api_config_can_enable_manifest(self):
        root = self.make_workspace_tmp()
        output_path = root / "config_manifest.nc"
        config_path = root / "generate_with_manifest.json"
        config_path.write_text(
            json.dumps(
                {
                    "output_format": "NC",
                    "output_path": str(output_path),
                    "write_manifest": True,
                    "rows": 1,
                    "cols": 1,
                    "labels_enabled": False,
                }
            ),
            encoding="utf-8",
        )

        stdout = self.run_app(["--api", "generate", "--config", str(config_path), "--overwrite"])

        data = json.loads(stdout)
        manifest_path = manifest_path_for_output(output_path)
        self.assertEqual(data["manifest"]["output"], str(manifest_path))
        self.assertTrue(manifest_path.exists())

    def test_manifest_format_fallback_uses_output_suffix(self):
        root = self.make_workspace_tmp()

        entries = generated_output_entries(
            [
                {"output": str(root / "legacy.mks")},
                {"output": str(root / "legacy.nc")},
            ],
            root,
        )

        self.assertEqual(entries, [{"format": "MKS", "path": "legacy.mks"}, {"format": "NC", "path": "legacy.nc"}])

    def test_mks_manifest_entry_has_mks_format(self):
        root = self.make_workspace_tmp()
        output_path = root / "mks_manifest.mks"

        self.run_app(
            [
                "--format",
                "MKS",
                "--output",
                str(output_path),
                "--overwrite",
                "--write-manifest",
                "--rows",
                "1",
                "--cols",
                "1",
                "--no-labels",
            ]
        )

        manifest_path = manifest_path_for_output(output_path)
        data = json.loads(manifest_path.read_text(encoding="utf-8"))

        self.assertEqual(data["generated_outputs"], [{"format": "MKS", "path": "mks_manifest.mks"}])

    def test_both_manifest_entries_have_clear_formats(self):
        root = self.make_workspace_tmp()
        output_path = root / "both_manifest.mks"

        self.run_app(
            [
                "--format",
                "Both",
                "--output",
                str(output_path),
                "--overwrite",
                "--write-manifest",
                "--rows",
                "1",
                "--cols",
                "1",
                "--no-labels",
            ]
        )

        manifest_path = manifest_path_for_output(output_path)
        data = json.loads(manifest_path.read_text(encoding="utf-8"))

        self.assertEqual(
            data["generated_outputs"],
            [
                {"format": "MKS", "path": "both_manifest.mks"},
                {"format": "NC", "path": "both_manifest.nc"},
            ],
        )


if __name__ == "__main__":
    unittest.main()
