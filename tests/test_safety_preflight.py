import json
import shutil
import unittest
import uuid
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

from laser_test_pattern_generator import app
from laser_test_pattern_generator.safety_preflight import (
    CHECKLIST_NAME,
    CHECKLIST_VERSION,
    safety_preflight_items,
)


class SafetyPreflightTests(unittest.TestCase):
    def make_workspace_tmp(self) -> Path:
        root = Path(__file__).resolve().parents[1] / "tmp" / "safety_preflight_tests" / uuid.uuid4().hex
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        return root

    def run_app(self, args: list[str]) -> tuple[int, str, str]:
        stdout = StringIO()
        stderr = StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = app.main(args)
        return exit_code, stdout.getvalue(), stderr.getvalue()

    def test_app_info_lists_preflight_checklist_api(self):
        exit_code, stdout, stderr = self.run_app(["--api", "app-info"])

        self.assertEqual(exit_code, 0, stderr)
        data = json.loads(stdout)
        self.assertIn("preflight-checklist", data["available_api_commands"])
        self.assertEqual(data["planned_api_commands"], [])

    def test_preflight_checklist_api_returns_stable_data(self):
        exit_code, stdout, stderr = self.run_app(["--api", "preflight-checklist"])

        self.assertEqual(exit_code, 0, stderr)
        data = json.loads(stdout)
        self.assertEqual(data["schema_version"], 1)
        self.assertEqual(data["api_command"], "preflight-checklist")
        self.assertEqual(data["checklist_name"], CHECKLIST_NAME)
        self.assertEqual(data["checklist_version"], CHECKLIST_VERSION)
        self.assertGreaterEqual(len(data["items"]), 10)

        for item in data["items"]:
            self.assertIsInstance(item["id"], str)
            self.assertIsInstance(item["label"], str)
            self.assertIsInstance(item["description"], str)
            self.assertIsInstance(item["category"], str)
            self.assertIsInstance(item["required"], bool)
            self.assertIsInstance(item["applies_to"], list)

    def test_checklist_contains_required_safety_items(self):
        item_ids = {item["id"] for item in safety_preflight_items()}

        self.assertIn("material_laser_safe", item_ids)
        self.assertIn("no_pvc_vinyl_chlorinated_material", item_ids)
        self.assertIn("ventilation_running", item_ids)
        self.assertIn("fire_response_nearby", item_ids)
        self.assertIn("machine_supervised", item_ids)
        self.assertIn("mks_recalculated_previewed", item_ids)
        self.assertIn("nc_s_value_scale_verified", item_ids)
        self.assertIn("movement_path_preview_checked", item_ids)
        self.assertIn("origin_work_zero_checked", item_ids)

    def test_preflight_checklist_api_does_not_write_files(self):
        root = self.make_workspace_tmp()
        output_path = root / "should_not_exist.nc"

        exit_code, stdout, stderr = self.run_app(
            ["--api", "preflight-checklist", "--output", str(output_path)]
        )

        self.assertEqual(exit_code, 0, stderr)
        self.assertEqual(json.loads(stdout)["api_command"], "preflight-checklist")
        self.assertFalse(output_path.exists())
        self.assertEqual(list(root.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
