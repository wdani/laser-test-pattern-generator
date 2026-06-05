# Windows Executable Builds

Windows executable builds are experimental. The primary supported way to run the
Laser Test Pattern Generator is still the cross-platform Python/Tkinter source
version.

The executable package is built with PyInstaller through the manual GitHub
Actions workflow `Build Windows Executable`. The workflow uses
`workflow_dispatch`, so it only runs when started manually and is not part of
the normal push or pull request test workflow.

Double-clicking `LaserTestPatternGenerator.exe` opens the GUI directly. CLI
users should continue to use the Python script:

```bash
python makera_material_test_generator.py --help
```

The uploaded workflow artifact is the package folder. GitHub downloads workflow
artifacts as archives automatically, so the workflow does not create a second
ZIP inside the artifact.

The extracted package uses this layout:

- `LaserTestPatternGenerator.exe`
- `README.md`
- `LICENSE.txt`
- `CHANGELOG.md`
- `RELEASE_NOTES.txt`
- `docs/`
- `templates/`
- `presets/`
- `_internal/`

The `_internal/` folder contains required PyInstaller runtime files such as
Python DLLs, `.pyd` files, `base_library.zip`, and Tcl/Tk runtime data. Do not
delete or move it.

Keep `templates/` and `presets/` next to `LaserTestPatternGenerator.exe`.
Makera Studio `.mks` generation needs the template files, and the GUI preset
manager reads and writes presets from that visible package folder.

To test a build, download the workflow artifact, extract the ZIP, and run the
executable from the extracted folder. Windows may show a warning because the
experimental executable is not code-signed.

Always preview generated `.mks` files in Makera Studio after Recalculate, and
always verify generic `.nc` files against the target controller before running a
laser.
