import json
import shutil
import unittest
import uuid
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

from laser_test_pattern_generator import app
from laser_test_pattern_generator.material_log import (
    MaterialLogError,
    append_material_result,
    build_material_result_entry,
    read_material_result_log,
)
from laser_test_pattern_generator.settings import APP_VERSION


class MaterialLogTests(unittest.TestCase):
    def make_workspace_tmp(self) -> Path:
        root = Path(__file__).resolve().parents[1] / "tmp" / "material_log_tests" / uuid.uuid4().hex
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        return root

    def run_app(self, args: list[str]) -> tuple[int, str, str]:
        stdout = StringIO()
        stderr = StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = app.main(args)
        return exit_code, stdout.getvalue(), stderr.getvalue()

    def test_result_log_file_is_created(self):
        root = self.make_workspace_tmp()
        log_path = root / "material_test_results.jsonl"
        entry = build_material_result_entry(
            app_version=APP_VERSION,
            material_name="cork",
            result_rating="good",
            source="test",
            created_at="2026-06-11T00:00:00Z",
        )

        append_material_result(log_path, entry)

        self.assertTrue(log_path.exists())
        entries = read_material_result_log(log_path)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["schema_version"], 1)
        self.assertEqual(entries[0]["app_version"], APP_VERSION)
        self.assertEqual(entries[0]["created_at"], "2026-06-11T00:00:00Z")
        self.assertEqual(entries[0]["material_name"], "cork")
        self.assertEqual(entries[0]["source"], "test")
        self.assertEqual(entries[0]["result_rating"], "good")

    def test_multiple_appends_preserve_earlier_entries(self):
        root = self.make_workspace_tmp()
        log_path = root / "results.jsonl"

        append_material_result(
            log_path,
            build_material_result_entry(
                app_version=APP_VERSION,
                material_name="cork",
                result_rating="too_light",
                source="test",
                created_at="2026-06-11T00:00:00Z",
            ),
        )
        append_material_result(
            log_path,
            build_material_result_entry(
                app_version=APP_VERSION,
                material_name="wood",
                result_rating="good",
                source="test",
                created_at="2026-06-11T00:01:00Z",
            ),
        )

        entries = read_material_result_log(log_path)
        self.assertEqual([entry["material_name"] for entry in entries], ["cork", "wood"])
        self.assertEqual([entry["result_rating"] for entry in entries], ["too_light", "good"])

    def test_optional_manifest_photo_and_machine_fields_are_recorded(self):
        entry = build_material_result_entry(
            app_version=APP_VERSION,
            material_name="cork",
            result_rating="unclear",
            source="api",
            machine_name="Carvera Air",
            laser_module="10W diode",
            manifest_path=Path("jobs/cork.manifest.json"),
            generated_output_path=Path("jobs/cork.nc"),
            selected_speed=1800,
            selected_power=24,
            notes="Edges looked clean.",
            photo_path=Path("photos/cork-test.jpg"),
            created_at="2026-06-11T00:00:00Z",
        )

        self.assertEqual(entry["machine_name"], "Carvera Air")
        self.assertEqual(entry["laser_module"], "10W diode")
        self.assertEqual(entry["manifest_path"], str(Path("jobs/cork.manifest.json")))
        self.assertEqual(entry["generated_output_path"], str(Path("jobs/cork.nc")))
        self.assertEqual(entry["selected_speed"], 1800.0)
        self.assertEqual(entry["selected_power"], 24.0)
        self.assertEqual(entry["notes"], "Edges looked clean.")
        self.assertEqual(entry["photo_path"], str(Path("photos/cork-test.jpg")))

    def test_missing_required_rating_fails_cleanly(self):
        try:
            build_material_result_entry(
                app_version=APP_VERSION,
                material_name="cork",
                result_rating=None,
                source="test",
            )
        except MaterialLogError:
            return
        raise AssertionError("Expected MaterialLogError")

    def test_invalid_rating_fails_cleanly(self):
        try:
            build_material_result_entry(
                app_version=APP_VERSION,
                material_name="cork",
                result_rating="perfect",
                source="test",
            )
        except MaterialLogError:
            return
        raise AssertionError("Expected MaterialLogError")

    def test_api_log_result_appends_entry_and_returns_json(self):
        root = self.make_workspace_tmp()
        log_path = root / "api_results.jsonl"

        exit_code, stdout, stderr = self.run_app(
            [
                "--api",
                "log-result",
                "--result-log",
                str(log_path),
                "--material-name",
                "cork",
                "--result-rating",
                "good",
                "--manifest",
                str(root / "cork.manifest.json"),
                "--photo",
                str(root / "cork.jpg"),
                "--selected-speed",
                "1800",
                "--selected-power",
                "24",
                "--machine-name",
                "Carvera Air",
                "--laser-module",
                "10W diode",
                "--result-notes",
                "Clean result.",
            ]
        )

        self.assertEqual(exit_code, 0, stderr)
        self.assertEqual(stderr, "")
        data = json.loads(stdout)
        self.assertTrue(data["success"])
        self.assertEqual(data["api_command"], "log-result")
        self.assertEqual(data["log_path"], str(log_path))
        self.assertEqual(data["entry"]["source"], "api")
        self.assertEqual(data["entry"]["result_rating"], "good")
        self.assertEqual(len(read_material_result_log(log_path)), 1)

    def test_cli_log_result_appends_entry(self):
        root = self.make_workspace_tmp()
        log_path = root / "cli_results.jsonl"

        exit_code, stdout, stderr = self.run_app(
            [
                "--log-result",
                "--result-log",
                str(log_path),
                "--material-name",
                "cardboard",
                "--result-rating",
                "too_dark",
            ]
        )

        self.assertEqual(exit_code, 0, stderr)
        self.assertEqual(stderr, "")
        data = json.loads(stdout)
        self.assertEqual(data["entry"]["source"], "cli")
        self.assertEqual(read_material_result_log(log_path)[0]["material_name"], "cardboard")

    def test_api_log_result_missing_rating_returns_nonzero_without_stdout(self):
        root = self.make_workspace_tmp()
        log_path = root / "missing_rating.jsonl"

        exit_code, stdout, stderr = self.run_app(
            [
                "--api",
                "log-result",
                "--result-log",
                str(log_path),
                "--material-name",
                "cork",
            ]
        )

        self.assertEqual(exit_code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("Material log error", stderr)
        self.assertFalse(log_path.exists())

    def test_api_log_result_invalid_rating_returns_nonzero_without_stdout(self):
        root = self.make_workspace_tmp()
        log_path = root / "invalid_rating.jsonl"

        exit_code, stdout, stderr = self.run_app(
            [
                "--api",
                "log-result",
                "--result-log",
                str(log_path),
                "--material-name",
                "cork",
                "--result-rating",
                "perfect",
            ]
        )

        self.assertEqual(exit_code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("Material log error", stderr)
        self.assertFalse(log_path.exists())


if __name__ == "__main__":
    unittest.main()
