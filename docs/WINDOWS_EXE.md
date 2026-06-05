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

The uploaded artifact is a ZIP package containing the Windows executable plus
the project files needed beside it:

- `LaserTestPatternGenerator.exe`
- `run_gui.py`
- `makera_material_test_generator.py`
- `templates/`
- `presets/`
- `docs/`
- `README.md`
- `LICENSE.txt`
- `CHANGELOG.md`
- `RELEASE_NOTES.txt`

To test a build, download the workflow artifact, extract the ZIP, and run the
executable from the extracted folder. Windows may show a warning because the
experimental executable is not code-signed.

Always preview generated `.mks` files in Makera Studio after Recalculate, and
always verify generic `.nc` files against the target controller before running a
laser.
