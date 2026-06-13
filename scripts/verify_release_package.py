from __future__ import annotations

import argparse
import fnmatch
import sys
import zipfile
from pathlib import Path

REQUIRED_PATHS = [
    ("file", "LaserTestPatternGenerator.exe"),
    ("dir", "_internal"),
    ("dir", "templates"),
    ("dir", "presets"),
    ("dir", "docs"),
    ("file", "README.md"),
    ("file", "LICENSE.txt"),
    ("file", "CHANGELOG.md"),
    ("file", "RELEASE_NOTES.txt"),
    ("file", "docs/INSTALLATION.md"),
    ("file", "docs/WINDOWS_EXE.md"),
    ("file", "docs/RELEASE_CHECKLIST.md"),
    ("file", "docs/SAFETY.md"),
    ("file", "docs/PREFLIGHT_CHECKLIST.md"),
    ("file", "docs/MATERIAL_RESULTS.md"),
]

SCRATCH_EXACT_NAMES = {
    ".pytest_cache",
    "api_generate_smoke.nc",
    "material_test_results.jsonl",
    "tmp",
}
SCRATCH_PATTERNS = ["*.manifest.json"]


class Report:
    def __init__(self) -> None:
        self.lines: list[str] = []
        self.failure_count = 0

    @property
    def ok(self) -> bool:
        return self.failure_count == 0

    def pass_(self, message: str) -> None:
        self.lines.append(f"PASS: {message}")

    def fail(self, message: str) -> None:
        self.failure_count += 1
        self.lines.append(f"FAIL: {message}")


def is_scratch_name(name: str) -> bool:
    if name in SCRATCH_EXACT_NAMES:
        return True
    return any(fnmatch.fnmatchcase(name, pattern) for pattern in SCRATCH_PATTERNS)


def normalize_zip_name(name: str) -> str:
    return "/".join(part for part in name.replace("\\", "/").strip("/").split("/") if part)


def verify_required_path(report: Report, exists: bool, rel_path: str) -> None:
    if exists:
        report.pass_(f"found {rel_path}")
    else:
        report.fail(f"missing required path: {rel_path}")


def verify_directory(package_path: Path, report: Report) -> None:
    report.pass_(f"package directory exists: {package_path}")

    for kind, rel_path in REQUIRED_PATHS:
        path = package_path / Path(rel_path)
        exists = path.is_file() if kind == "file" else path.is_dir()
        verify_required_path(report, exists, rel_path)

    scratch_names = sorted(child.name for child in package_path.iterdir() if is_scratch_name(child.name))
    if scratch_names:
        for name in scratch_names:
            report.fail(f"unexpected scratch output at package root: {name}")
    else:
        report.pass_("no obvious scratch outputs at package root")


def zip_path_exists(names: set[str], rel_path: str, kind: str) -> bool:
    rel_path = rel_path.strip("/")
    if kind == "file":
        return rel_path in names
    return rel_path in names or any(name.startswith(f"{rel_path}/") for name in names)


def verify_zip(package_path: Path, report: Report) -> None:
    report.pass_(f"package ZIP exists: {package_path}")

    with zipfile.ZipFile(package_path) as archive:
        names = [normalize_zip_name(name) for name in archive.namelist()]

    names = [name for name in names if name]
    if not names:
        report.fail("ZIP archive is empty")
        return

    top_level_names = {name.split("/", 1)[0] for name in names}
    if len(top_level_names) != 1:
        found = ", ".join(sorted(top_level_names))
        report.fail(f"ZIP should contain one top-level package folder; found: {found}")
        return

    package_root = next(iter(top_level_names))
    report.pass_(f"ZIP contains top-level package folder: {package_root}")

    rel_names = {
        name[len(package_root) + 1 :]
        for name in names
        if name != package_root and name.startswith(f"{package_root}/")
    }

    if not rel_names:
        report.fail("ZIP top-level package folder is empty")
        return

    nested_zips = sorted(name for name in rel_names if Path(name).name.lower().endswith(".zip"))
    if nested_zips:
        for name in nested_zips:
            report.fail(f"unexpected nested ZIP file in package: {name}")
    else:
        report.pass_("no nested ZIP files found")

    for kind, rel_path in REQUIRED_PATHS:
        verify_required_path(report, zip_path_exists(rel_names, rel_path, kind), rel_path)

    top_level_rel_names = {name.split("/", 1)[0] for name in rel_names}
    scratch_names = sorted(name for name in top_level_rel_names if is_scratch_name(name))
    if scratch_names:
        for name in scratch_names:
            report.fail(f"unexpected scratch output at package root: {name}")
    else:
        report.pass_("no obvious scratch outputs at package root")


def verify_package(package_path: Path) -> Report:
    report = Report()
    report.lines.append("Release package verification")
    report.lines.append(f"Path: {package_path}")

    if not package_path.exists():
        report.fail("package path does not exist")
        return report

    if package_path.is_dir():
        verify_directory(package_path, report)
        return report

    if package_path.is_file() and zipfile.is_zipfile(package_path):
        verify_zip(package_path, report)
        return report

    report.fail("package path must be an extracted directory or a ZIP file")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify a Laser Test Pattern Generator release package.")
    parser.add_argument("package_path", type=Path, help="Extracted package directory or release ZIP path")
    args = parser.parse_args(argv)

    report = verify_package(args.package_path)
    for line in report.lines:
        print(line)

    if report.ok:
        print("RESULT: PASS")
        return 0

    print(f"RESULT: FAIL ({report.failure_count} issue(s))")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
