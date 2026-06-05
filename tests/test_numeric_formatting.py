import unittest

from laser_test_pattern_generator.gui import GeneratorGui


class NumericFormattingTests(unittest.TestCase):
    def test_integer_increment_formats_as_integer(self):
        self.assertEqual(GeneratorGui._format_numeric_value(None, 7.0, 1), "7")

    def test_decimal_increment_trims_float_artifacts(self):
        self.assertEqual(GeneratorGui._format_numeric_value(None, 0.30000000000000004, 0.1), "0.3")

    def test_explicit_format_preserves_useful_decimals(self):
        self.assertEqual(GeneratorGui._format_numeric_value(None, 0.1, 0.01, "%.2f"), "0.10")


if __name__ == "__main__":
    unittest.main()
