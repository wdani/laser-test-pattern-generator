# Laser Test Pattern Generator

Generate laser material test patterns for **Makera Studio (`.mks`)** and **generic NC/G-code (`.nc`)**.

> Unofficial tool. Not affiliated with Makera. Always preview generated files before running a laser.

## Features

- Generate Makera Studio `.mks` project files.
- Generate generic `.nc` / G-code files.
- Output modes: `MKS`, `NC`, or `Both`.
- Configurable grid: rows, columns, tile size, gap and stock size.
- Configurable test ranges: speed in mm/min and power in percent.
- Laser modes: Line, Fill and Offset Fill.
- Labels in English or German.
- Preset manager.
- Auto filename generation.
- Overwrite protection.
- Approximate preview tab.

## Current release

The current first packaged version is **v1.0**.

The release ZIP contains:

- `makera_material_test_generator.py`
- `start_gui_windows.bat`
- `generate_example_cli_windows.bat`
- `templates/`
- `presets/`
- `examples/`
- documentation and license files

## Quick start

### Windows

1. Download the v1.0 release ZIP.
2. Extract it.
3. Double-click:

```text
start_gui_windows.bat
```

### Manual start

```bash
python makera_material_test_generator.py --gui
```

## Recommended first test

1. Start the GUI.
2. Open the **Presets** tab.
3. Load `Cork broad 8x8`.
4. Go to **Preview** and click `Update Preview`.
5. Click `Generate`.
6. Open the generated `.mks` in Makera Studio.
7. Press **Recalculate**.
8. Check the Preview before exporting or running.

## Command line example

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

## Generic NC warning

Generic `.nc` output is controller-dependent. Different controllers use different laser power scales, for example:

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
