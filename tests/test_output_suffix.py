import unittest

from laser_test_pattern_generator.paths import sync_output_suffix_for_format


class OutputSuffixTests(unittest.TestCase):
    def test_mks_suffix_changes_to_nc(self):
        self.assertEqual(sync_output_suffix_for_format("material_test.mks", "NC"), "material_test.nc")

    def test_nc_suffix_changes_to_mks(self):
        self.assertEqual(sync_output_suffix_for_format("material_test.nc", "MKS"), "material_test.mks")

    def test_no_suffix_gets_expected_suffix(self):
        self.assertEqual(sync_output_suffix_for_format("material_test", "NC"), "material_test.nc")

    def test_custom_suffix_is_left_unchanged(self):
        self.assertEqual(sync_output_suffix_for_format("material_test.gcode", "NC"), "material_test.gcode")


if __name__ == "__main__":
    unittest.main()
