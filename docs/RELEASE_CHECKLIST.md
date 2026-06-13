# Release Checklist

Use this checklist before publishing a Laser Test Pattern Generator release.
It is meant to be practical and beginner-friendly.

## Before Release

- Confirm the version number is updated in `laser_test_pattern_generator/settings.py`.
- Confirm `CHANGELOG.md` has an entry for the release.
- Confirm `RELEASE_NOTES.txt` matches the release version.
- Check the current release text in `README.md`.
- Run the test suite.
- Run JSON API smoke checks:
  - `python makera_material_test_generator.py --api app-info`
  - `python makera_material_test_generator.py --api default-settings`
  - `python makera_material_test_generator.py --api preview`
  - `python makera_material_test_generator.py --api generate --format NC --output api_generate_smoke.nc --overwrite`
- Delete any smoke output files after testing.

## Windows Package Check

- Download and extract the Windows ZIP package.
- From a repository checkout, run the package verifier against the extracted
  package folder:
  - `python scripts/verify_release_package.py path/to/Laser_Test_Pattern_Generator_windows`
- Confirm `LaserTestPatternGenerator.exe` starts the GUI.
- Confirm `_internal/`, `templates/`, and `presets/` are present.
- Confirm preset loading works from the GUI.
- Generate a small sample output file.
- Expect a Windows SmartScreen or unsigned-build warning because the
  experimental executable is not code-signed.

## macOS App Package Check

- Download and extract the macOS app artifact.
- Extract the contained `.tar.gz` package archive. It is used to preserve
  executable permissions inside the `.app` bundle.
- Confirm `LaserTestPatternGenerator.app` is present.
- Confirm `templates/`, `presets/`, and `docs/` are present next to the `.app`.
- Confirm README, license, changelog, and release notes are included.
- Open the `.app` if macOS allows it.
- Expect a Gatekeeper or unidentified-developer warning because the
  experimental `.app` is unsigned and not notarized.
- If macOS blocks the `.app`, confirm the Python/source fallback still works:
  - `python3 run_gui.py`
  - `python3 makera_material_test_generator.py --gui`

## Source Package Check

- Confirm `python run_gui.py` starts the GUI.
- Confirm `python makera_material_test_generator.py --gui` starts the GUI.
- Confirm CLI help works:
  - `python makera_material_test_generator.py --help`
- Confirm source users can find `docs/INSTALLATION.md`.

## Generated File Check

- Generate a sample `.mks` file.
- Generate a sample `.nc` file.
- If useful, generate with `--write-manifest` and inspect the
  `.manifest.json` file.
- Preview generated `.mks` files in Makera Studio after **Recalculate** before
  real use.
- Preview generated `.nc` files in an NC sender/viewer before real use.
- Verify the generic NC S-value scale for the target controller.

## Release Asset Check

- Confirm the correct files are attached to the GitHub Release.
- Confirm no scratch/generated test output is accidentally included.
- Confirm `scripts/verify_release_package.py` passes for the Windows package or
  release ZIP.
- Confirm release notes match the published version.
- Confirm release asset naming is clear and consistent.
- Confirm Windows ZIP assets, if present, are not ZIP-inside-ZIP workflow
  artifacts.
- Confirm macOS app artifacts, if present, are clearly marked experimental.

## After Release

- Confirm the GitHub Release is visible.
- Confirm the GUI update check sees the latest release.
- Confirm README and release metadata still point to the correct version.
- Confirm linked documentation opens correctly from the repository.
