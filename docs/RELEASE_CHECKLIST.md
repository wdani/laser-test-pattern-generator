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
- Confirm `LaserTestPatternGenerator.exe` starts the GUI.
- Confirm `_internal/`, `templates/`, and `presets/` are present.
- Confirm preset loading works from the GUI.
- Generate a small sample output file.
- Expect a Windows SmartScreen or unsigned-build warning because the
  experimental executable is not code-signed.

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
- Confirm release notes match the published version.
- Confirm release asset naming is clear and consistent.
- Confirm Windows ZIP assets, if present, are not ZIP-inside-ZIP workflow
  artifacts.

## After Release

- Confirm the GitHub Release is visible.
- Confirm the GUI update check sees the latest release.
- Confirm README and release metadata still point to the correct version.
- Confirm linked documentation opens correctly from the repository.
