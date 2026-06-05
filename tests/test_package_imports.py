import unittest


class PackageImportTests(unittest.TestCase):
    def test_package_modules_import(self):
        import laser_test_pattern_generator
        import laser_test_pattern_generator.generator_mks
        import laser_test_pattern_generator.generator_nc

        self.assertTrue(hasattr(laser_test_pattern_generator, "GeneratorSettings"))
        self.assertTrue(hasattr(laser_test_pattern_generator.generator_mks, "generate_mks"))
        self.assertTrue(hasattr(laser_test_pattern_generator.generator_nc, "generate_generic_nc"))


if __name__ == "__main__":
    unittest.main()
