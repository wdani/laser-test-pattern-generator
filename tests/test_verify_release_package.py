import shutil
import subprocess
import sys
import unittest
import uuid
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "verify_release_package.py"

REQUIRED_FILES = [
    "LaserTestPatternGenerator.exe",
    "README.md",
    "LICENSE.txt",
    "CHANGELOG.md",
    "RELEASE_NOTES.txt",
    "docs/INSTALLATION.md",
    "docs/WINDOWS_EXE.md",
    "docs/RELEASE_CHECKLIST.md",
    "docs/SAFETY.md",
    "docs/PREFLIGHT_CHECKLIST.md",
    "docs/MATERIAL_RESULTS.md",
]

REQUIRED_DIRS = ["_internal", "templates", "presets", "docs"]


class VerifyReleasePackageTests(unittest.TestCase):
    def make_workspace_tmp(self) -> Path:
        root = REPO_ROOT / "tmp" / "verify_release_package_tests" / uuid.uuid4().hex
        root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        return root

    def make_valid_package(self, root: Path, missing_files: set[str] | None = None) -> Path:
        missing_files = missing_files or set()
        package_dir = root / "Laser_Test_Pattern_Generator_windows"
        package_dir.mkdir()

        for rel_dir in REQUIRED_DIRS:
            (package_dir / rel_dir).mkdir(parents=True, exist_ok=True)

        for rel_file in REQUIRED_FILES:
            if rel_file in missing_files:
                continue
            path = package_dir / rel_file
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("test\n", encoding="utf-8")

        return package_dir

    def run_verifier(self, package_path: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(package_path)],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def write_package_zip(self, package_dir: Path, zip_path: Path) -> None:
        with zipfile.ZipFile(zip_path, "w") as archive:
            for path in sorted(package_dir.rglob("*")):
                rel_path = path.relative_to(package_dir)
                archive_name = Path(package_dir.name) / rel_path
                if path.is_dir():
                    archive.writestr(archive_name.as_posix().rstrip("/") + "/", "")
                else:
                    archive.write(path, archive_name.as_posix())

    def test_valid_package_directory_passes(self):
        root = self.make_workspace_tmp()
        package_dir = self.make_valid_package(root)

        result = self.run_verifier(package_dir)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("RESULT: PASS", result.stdout)

    def test_missing_required_file_fails(self):
        root = self.make_workspace_tmp()
        package_dir = self.make_valid_package(root, missing_files={"LICENSE.txt"})

        result = self.run_verifier(package_dir)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing required path: LICENSE.txt", result.stdout)
        self.assertIn("RESULT: FAIL", result.stdout)

    def test_top_level_scratch_output_fails(self):
        root = self.make_workspace_tmp()
        package_dir = self.make_valid_package(root)
        (package_dir / "api_generate_smoke.nc").write_text("scratch\n", encoding="utf-8")

        result = self.run_verifier(package_dir)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unexpected scratch output at package root: api_generate_smoke.nc", result.stdout)

    def test_valid_package_zip_passes(self):
        root = self.make_workspace_tmp()
        package_dir = self.make_valid_package(root)
        zip_path = root / "Laser_Test_Pattern_Generator_Windows_v1.0.0.zip"
        self.write_package_zip(package_dir, zip_path)

        result = self.run_verifier(zip_path)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("ZIP contains top-level package folder", result.stdout)
        self.assertIn("RESULT: PASS", result.stdout)

    def test_zip_inside_zip_fails(self):
        root = self.make_workspace_tmp()
        package_dir = self.make_valid_package(root)
        nested_zip = package_dir / "old_artifact.zip"
        with zipfile.ZipFile(nested_zip, "w") as archive:
            archive.writestr("placeholder.txt", "nested")
        zip_path = root / "bad_nested.zip"
        self.write_package_zip(package_dir, zip_path)

        result = self.run_verifier(zip_path)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unexpected nested ZIP file in package: old_artifact.zip", result.stdout)

    def test_zip_without_top_level_package_folder_fails(self):
        root = self.make_workspace_tmp()
        package_dir = self.make_valid_package(root)
        zip_path = root / "flat_package.zip"
        with zipfile.ZipFile(zip_path, "w") as archive:
            for path in sorted(package_dir.rglob("*")):
                if path.is_file():
                    archive.write(path, path.relative_to(package_dir).as_posix())

        result = self.run_verifier(zip_path)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ZIP should contain one top-level package folder", result.stdout)


if __name__ == "__main__":
    unittest.main()
