# Windows Executable Builds

Windows executable builds are experimental. The primary supported way to run the
Laser Test Pattern Generator is still the cross-platform Python/Tkinter source
version.

The `.exe` package and `.bat` launcher are Windows-only convenience options.
macOS and Linux users should run from source with Python/Tkinter instead:

```bash
python3 run_gui.py
```

or:

```bash
python3 makera_material_test_generator.py --gui
```

Tkinter is required. On some Linux distributions it may need to be installed as
`python3-tk` or the distribution's equivalent package.

The executable package is built with PyInstaller through the manual GitHub
Actions workflow `Build Windows Executable`. The workflow uses
`workflow_dispatch` for manual test builds and also runs for version tags such
as `v1.3.1` or `v1.4.0`.

Double-clicking `LaserTestPatternGenerator.exe` opens the GUI directly. CLI
users should continue to use the Python script:

```bash
python makera_material_test_generator.py --help
```

Manual workflow runs upload the package folder as a workflow artifact. GitHub
downloads workflow artifacts as archives automatically, so manual builds do not
create a second ZIP inside the artifact.

Tag builds create a release asset ZIP named like
`Laser_Test_Pattern_Generator_Windows_v1.3.1.zip` and attach it to the matching
GitHub Release. The Windows ZIP is still experimental, but it is easier for
non-Python users to download and try.

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
