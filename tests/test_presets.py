import json
import shutil
import unittest
import uuid
from pathlib import Path

from laser_test_pattern_generator import presets


class PresetHelperTests(unittest.TestCase):
    def make_workspace_tmp(self) -> Path:
        root = Path(__file__).resolve().parents[1] / "tmp" / "preset_tests" / uuid.uuid4().hex
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        return root

    def test_old_preset_format_uses_legacy_name(self):
        root = self.make_workspace_tmp()
        path = root / "legacy.json"
        path.write_text(json.dumps({"_preset_name": "Legacy Cork", "rows": "6"}), encoding="utf-8")

        data = presets.read_preset_file(path)

        self.assertEqual(presets.preset_display_name(data, path), "Legacy Cork")
        self.assertEqual(presets.metadata_subset(data)["material"], "")

    def test_preset_metadata_is_preserved_when_saving(self):
        root = self.make_workspace_tmp()
        path = presets.save_preset_data(
            "Cardboard low power",
            {
                "material": "cardboard",
                "machine": "Makera Carvera Air",
                "laser_module": "10 W diode",
                "notes": "Start low and verify.",
                "safety_note": "Check fumes and fire risk.",
                "reference_image": "photos/cardboard-test.png",
                "unknown_field": "kept but ignored by the GUI",
                "rows": "4",
            },
            root,
        )

        data = presets.read_preset_file(path)

        self.assertEqual(data["name"], "Cardboard low power")
        self.assertEqual(data["_preset_name"], "Cardboard low power")
        self.assertEqual(data["material"], "cardboard")
        self.assertEqual(data["reference_image"], "photos/cardboard-test.png")
        self.assertEqual(data["unknown_field"], "kept but ignored by the GUI")

    def test_image_metadata_is_optional_and_safe_to_read(self):
        root = self.make_workspace_tmp()
        with_image = root / "with_image.json"
        with_image.write_text(
            json.dumps({"name": "With image", "reference_image": "result.webp", "rows": "3"}),
            encoding="utf-8",
        )
        without_image = root / "without_image.json"
        without_image.write_text(json.dumps({"name": "Without image", "rows": "3"}), encoding="utf-8")

        self.assertEqual(presets.metadata_subset(presets.read_preset_file(with_image))["reference_image"], "result.webp")
        self.assertEqual(presets.metadata_subset(presets.read_preset_file(without_image))["reference_image"], "")

    def test_import_and_export_copy_preset_json(self):
        source_root = self.make_workspace_tmp()
        target_root = self.make_workspace_tmp()
        source = source_root / "shared.json"
        source.write_text(json.dumps({"name": "Shared wood", "material": "wood", "rows": "3"}), encoding="utf-8")

        imported = presets.import_preset_file(source, target_root)
        exported = presets.export_preset_file("Shared wood", source_root / "exported.json", target_root)

        self.assertEqual(imported.name, "shared_wood.json")
        self.assertEqual(json.loads(exported.read_text(encoding="utf-8"))["material"], "wood")

    def test_save_without_overwrite_refuses_existing_preset(self):
        root = self.make_workspace_tmp()
        presets.save_preset_data("Existing preset", {"rows": "1"}, root)

        with self.assertRaises(FileExistsError):
            presets.save_preset_data("Existing preset", {"rows": "2"}, root, overwrite=False)

        data = presets.read_preset_file(root / "existing_preset.json")
        self.assertEqual(data["rows"], "1")

    def test_import_without_overwrite_refuses_existing_preset(self):
        source_root = self.make_workspace_tmp()
        target_root = self.make_workspace_tmp()
        source = source_root / "shared.json"
        source.write_text(json.dumps({"name": "Shared cork", "rows": "3"}), encoding="utf-8")
        presets.import_preset_file(source, target_root)

        source.write_text(json.dumps({"name": "Shared cork", "rows": "4"}), encoding="utf-8")
        with self.assertRaises(FileExistsError):
            presets.import_preset_file(source, target_root, overwrite=False)

        data = presets.read_preset_file(target_root / "shared_cork.json")
        self.assertEqual(data["rows"], "3")


if __name__ == "__main__":
    unittest.main()
