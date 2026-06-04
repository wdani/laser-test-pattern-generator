# Laser Test Pattern Generator

Generate laser material test patterns for **Makera Studio (`.mks`)** and
**generic NC/G-code (`.nc`)**.

> Unofficial tool. Not affiliated with Makera. Always preview generated files
> before running a laser.

## Current Release

The first clean public release baseline is **v1.0**.

This is a cross-platform Python/Tkinter tool. The included `.bat` file is only a
Windows convenience launcher; the generator itself runs from Python on Windows,
Linux, and macOS.

## Features

- Generate Makera Studio `.mks` project files.
- Generate generic `.nc` / G-code files.
- Output modes: `MKS`, `NC`, or `Both`.
- Configurable grid: rows, columns, tile size, gap, and stock size.
- Configurable test ranges: speed in mm/min and power in percent.
- Laser modes: Line, Fill, and Offset Fill.
- English GUI.
- Generated labels selectable between English and German.
- Preset manager with JSON presets.
- Auto filename generation and overwrite protection.
- Approximate preview tab.

## Quick Start

### Windows

Double-click:

```text
start_gui_windows.bat
```

### Linux/macOS

```bash
python3 makera_material_test_generator.py --gui
```

### Manual Python Start

```bash
python makera_material_test_generator.py --gui
```

Tkinter is part of the Python standard library on many installs. On some Linux
distributions it is packaged separately as `python3-tk`.

## Recommended First Test

1. Start the GUI.
2. Open the **Presets** tab.
3. Load `Cork broad 8x8`.
4. Go to **Preview** and click `Update Preview`.
5. Click `Generate`.
6. Open the generated `.mks` in Makera Studio.
7. Press **Recalculate**.
8. Check the Preview before exporting or running.

## Command Line Examples

Generate both `.mks` and `.nc`:

```bash
python makera_material_test_generator.py --format Both --auto-filename --material-name cork --rows 8 --cols 8 --speed-min 1800 --speed-max 2800 --power-min 20 --power-max 40
```

Generate only Makera Studio `.mks`:

```bash
python makera_material_test_generator.py --format MKS --output material_test.mks
```

Generate only generic `.nc`:

```bash
python makera_material_test_generator.py --format NC --output material_test.nc --nc-s-max 1000
```

Generate German labels:

```bash
python makera_material_test_generator.py --format MKS --language Deutsch --output material_test_de.mks
```

## Repository Layout

- `makera_material_test_generator.py` - main Python/Tkinter app and CLI.
- `start_gui_windows.bat` - Windows convenience launcher.
- `templates/` - Makera Studio template projects used by `.mks` generation.
- `presets/` - compatible JSON presets for the GUI.
- `docs/` - safety notes and roadmap.

Generated scratch outputs should stay outside the repository or in ignored output
folders.

## Generic NC Warning

Generic `.nc` output is controller-dependent. Different controllers use
different laser power scales, for example:

```text
S1
S255
S1000
S10000
```

The tool default is:

```text
NC S max = 1000
20% power = S200
40% power = S400
100% power = S1000
```

Always verify the `S` scale for your machine.

## Safety

Read [docs/SAFETY.md](docs/SAFETY.md).

## Roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md).

## License

MIT License. See [LICENSE.txt](LICENSE.txt).
