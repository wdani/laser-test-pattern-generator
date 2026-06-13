# macOS App Builds

macOS app builds are experimental. The primary supported way to run the Laser
Test Pattern Generator is still the cross-platform Python/Tkinter source
version.

The experimental macOS app package is built with PyInstaller through the manual
GitHub Actions workflow `Build macOS App`. It is intended as a convenience
artifact for testing the stable v1.x Python/Tkinter app, not as a signed or
notarized installer.

## Package Contents

The macOS artifact contains a folder with:

- `LaserTestPatternGenerator.app`
- `README.md`
- `LICENSE.txt`
- `CHANGELOG.md`
- `RELEASE_NOTES.txt`
- `docs/`
- `templates/`
- `presets/`

Keep `templates/` and `presets/` next to the `.app`. Makera Studio `.mks`
generation needs the template files, and the GUI preset manager reads and
writes presets from the visible package folder.

## Download and Start

1. Open the manual `Build macOS App` workflow run in GitHub Actions.
2. Download the macOS artifact.
3. Extract the artifact first. Do not run the app from inside a compressed ZIP
   viewer.
4. Open the extracted folder.
5. Double-click `LaserTestPatternGenerator.app`.

## Gatekeeper Notes

The experimental `.app` is unsigned and not notarized. macOS Gatekeeper may warn
that the app is from an unidentified developer or may block it.

Only run artifacts that you downloaded from the official repository workflow or
release. If macOS blocks the `.app`, use the Python/source startup path instead:

```bash
python3 run_gui.py
```

or:

```bash
python3 makera_material_test_generator.py --gui
```

## Source Fallback

Python/source startup remains supported on macOS. It is the recommended fallback
if the app bundle is blocked, if the experimental package does not work on your
macOS version, or if you want to use the CLI/API commands directly.

Tkinter is required. It is included with many Python installations, but exact
availability can vary depending on how Python was installed.

## Safety

Always preview generated `.mks` files in Makera Studio after Recalculate, and
always verify generic `.nc` files against the target controller before running a
laser.
