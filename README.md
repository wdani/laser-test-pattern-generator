# Laser Test Pattern Generator

Generate laser material test patterns for **Makera Studio (`.mks`)** and
**generic NC/G-code (`.nc`)**.

> Unofficial tool. Not affiliated with Makera. Always preview generated files
> before running a laser.

## Current Release

The current release is **v1.3**.

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
- Generic NC power profiles for Makera, GRBL, 8-bit, and custom S-value scales.
- Metadata comments in generated generic `.nc` files for easier verification.
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

## Screenshots

### Grid and stock setup

![Grid and stock setup](docs/screenshots/01-grid-stock-setup.png?v=clean-v1-2)

### Laser and NC settings

![Laser and NC settings](docs/screenshots/02-laser-nc-settings.png?v=clean-v1-2)

### Built-in layout preview

![Built-in layout preview](docs/screenshots/03-layout-preview.png?v=clean-v1-2)

### Makera Studio preview after Recalculate

![Makera Studio preview after Recalculate](docs/screenshots/04-makera-studio-preview.png?v=clean-v1-2)

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
python makera_material_test_generator.py --format NC --output material_test.nc
```

Generate generic `.nc` for a GRBL-style controller:

```bash
python makera_material_test_generator.py --format NC --nc-power-profile "GRBL (0-1000)" --output material_test_grbl.nc
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

## Generic NC Power Scale

Generic `.nc` output is controller-dependent. Different controllers use
different laser power scales.

Generated `.nc` files include metadata comments at the top with the selected
NC power profile, S max, grid settings, speed and power ranges, and a reminder
to verify the S-value scale before running the file.

Since v1.1, the default generic NC profile is **Makera (0-1)**:

- `0%` power maps to `S0.0`
- `20%` power maps to `S0.2`
- `40%` power maps to `S0.4`
- `100%` power maps to `S1.0`

GRBL-style controllers often use **0-1000** instead:

- `20%` power maps to `S200`
- `40%` power maps to `S400`
- `100%` power maps to `S1000`

Available profiles:

- `Makera (0-1)`
- `GRBL (0-1000)`
- `8-bit (0-255)`
- `Custom`

Use `--nc-power-profile Custom --nc-s-max VALUE` for another controller scale.
Always verify the `S` scale for your machine.

## Safety

Read [docs/SAFETY.md](docs/SAFETY.md).

## Roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md).

## License

MIT License. See [LICENSE.txt](LICENSE.txt).
