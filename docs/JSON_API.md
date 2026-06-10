# JSON CLI API

The JSON CLI API is the backend contract for future UI/frontend work around the
Laser Test Pattern Generator. The v1.x application remains the stable
Python/Tkinter version, and the Python core remains the source of truth for
settings, preview calculations, and file generation.

All API commands are invoked through the existing Python entry point:

```bash
python makera_material_test_generator.py --api COMMAND
```

API commands print valid JSON to stdout. They are intended for frontends,
automation, companion tools, and future Tauri v2.0 UI work. Frontends should
call these commands instead of duplicating Python defaults or generation logic.

Generated MKS and generic NC toolpath behavior is unchanged by the API wrapper.
The API calls the same Python settings and generator functions used by the
normal command-line workflow.

## Command Summary

| Command | Writes Files | Purpose |
| --- | --- | --- |
| `app-info` | No | Discover application/API metadata. |
| `default-settings` | No | Get the complete default `GeneratorSettings` values. |
| `preview` | No | Calculate a read-only layout preview from CLI settings. |
| `generate` | Yes | Generate MKS/NC output files and return machine-readable results. |

## JSON Config Files

`preview` and `generate` can load settings from a JSON config file:

```bash
python makera_material_test_generator.py --api preview --config examples/api/preview_basic.json
```

```bash
python makera_material_test_generator.py --api generate --config examples/api/generate_nc_basic.json --overwrite
```

Config files use snake_case keys matching the `default-settings` response where
possible, for example `output_format`, `output_path`, `rows`, `cols`,
`speed_min`, `power_max`, `labels_enabled`, `tile_mode_name`, and
`nc_power_profile`.

Precedence is:

1. Built-in Python defaults.
2. JSON config values.
3. Explicit CLI arguments.

That means a frontend or script can keep common settings in JSON and override a
single value on the command line:

```bash
python makera_material_test_generator.py --api preview --config examples/api/preview_basic.json --rows 4
```

Boolean config keys use the positive setting names, such as
`labels_enabled: false`, `auto_position: true`, `round_speed_values: false`, or
`overwrite_existing: true`.

Use `write_manifest: true` to make `generate` write an optional
`.manifest.json` file next to the generated output. The manifest records the app
version, selected settings, and generated output paths for reproducibility.

Invalid config files return a non-zero exit code, write a useful error to
stderr, and do not print partial JSON to stdout.

Included examples:

- `examples/api/preview_basic.json`
- `examples/api/generate_nc_basic.json`
- `examples/api/generate_both_basic.json`

## app-info

Example:

```bash
python makera_material_test_generator.py --api app-info
```

Writes files: No.

Purpose:

Returns stable metadata that a frontend can use during startup or capability
discovery.

Important JSON fields:

- `schema_version`
- `app_name`
- `app_version`
- `backend`
- `supported_output_formats`
- `available_api_commands`
- `planned_api_commands`

Intended frontend usage:

- Detect that the backend is available.
- Show or log the Python backend version.
- Discover available API commands.
- Confirm supported output formats: `MKS`, `NC`, and `Both`.

`planned_api_commands` is currently empty when all known API commands are
available.

## default-settings

Example:

```bash
python makera_material_test_generator.py --api default-settings
```

Writes files: No.

Purpose:

Returns the complete default settings object used by generation. The response is
derived from `settings_from_args(parse_args([]))`, so it reflects the real
Python defaults.

Important JSON fields:

- Metadata: `schema_version`, `api_command`, `app_name`, `app_version`
- Output defaults: `output_path`, `output_format`, `overwrite_existing`,
  `auto_filename`
- Grid/test defaults: `rows`, `cols`, `speed_min`, `speed_max`, `power_min`,
  `power_max`, `tile_size`, `gap`, `grid_x`, `grid_y`, `auto_position`
- Laser defaults: `tile_mode_name`, `line_interval`, `passes`,
  `bidirectional`, `scan_angle`
- Label defaults: `labels_enabled`, `language`, `label_speed`, `label_power`,
  `label_mode_name`, `label_thickness`
- Stock defaults: `stock_x`, `stock_y`, `stock_z`
- Rounding defaults: `round_speed_values`, `round_power_values`
- NC defaults: `nc_power_profile`, `nc_s_max`, `nc_units`,
  `nc_include_labels`
- Template default: `template_dir`

Path values are serialized as strings or `null`.

Intended frontend usage:

- Initialize form controls from the backend.
- Avoid duplicating Python-side defaults in a frontend.
- Keep future UI defaults synchronized with generator behavior.

## preview

Example:

```bash
python makera_material_test_generator.py --api preview --rows 2 --cols 3 --speed-min 1000 --speed-max 2000 --power-min 10 --power-max 30
```

Example with config:

```bash
python makera_material_test_generator.py --api preview --config examples/api/preview_basic.json
```

Writes files: No.

Purpose:

Returns a read-only layout preview for the same CLI settings that generation
would use. This command does not require Makera template files and does not
create or overwrite output files.

The preview applies the same speed/power rounding behavior and auto-positioning
logic used by generation.

Important JSON fields:

- Metadata: `schema_version`, `api_command`, `app_name`, `app_version`
- Layout summary: `output_format`, `rows`, `cols`, `tile_count`, `tile_size`,
  `gap`, `grid_x`, `grid_y`, `auto_position`, `grid_width`, `grid_height`
- Stock: `stock_x`, `stock_y`, `stock_z`
- Laser settings: `tile_mode_name`, `line_interval`, `passes`,
  `bidirectional`, `scan_angle`
- Labels: `labels_enabled`, `language`
- Generated axes: `speeds_visual_top_to_bottom`, `powers_left_to_right`
- Bounds: `approx_bounds.min_x`, `approx_bounds.max_x`,
  `approx_bounds.min_y`, `approx_bounds.max_y`
- Validation: `warnings`

Intended frontend usage:

- Show a safe layout preview before writing any files.
- Display generated speed/power axis values after rounding.
- Show stock/layout warnings before generation.
- Let users adjust settings without touching the filesystem.

## generate

Example for NC:

```bash
python makera_material_test_generator.py --api generate --format NC --output material_test.nc --overwrite
```

Example for MKS:

```bash
python makera_material_test_generator.py --api generate --format MKS --output material_test.mks --overwrite
```

Example for both outputs:

```bash
python makera_material_test_generator.py --api generate --format Both --output material_test.mks --overwrite
```

Example with config:

```bash
python makera_material_test_generator.py --api generate --config examples/api/generate_nc_basic.json --overwrite
```

Writes files: Yes.

Purpose:

Generates output files using the same `generate_mks()` and
`generate_generic_nc()` functions as normal CLI generation, then returns a clean
JSON result. Unlike normal CLI generation, API generation does not print the
human guidance text after the JSON.

Overwrite behavior:

- With `--overwrite`, the requested output path may be overwritten.
- Without `--overwrite`, existing output paths are not overwritten; the existing
  output path resolver chooses a unique filename.
- `--format Both` runs the existing MKS and NC generators, and each generated
  file uses its existing independent output path resolution.
- Do not assume that `--format Both` always creates matching `.mks` and `.nc`
  filename stems. When `--overwrite` is not used and filename collisions exist,
  each generator may resolve to a different unique output path.
- The returned JSON `output` values are authoritative. Frontends must read the
  actual generated paths from `result.output` or each entry in the `results`
  array instead of deriving companion paths.
- With `--write-manifest`, the response includes a `manifest` object with the
  written manifest path.

JSON shape for one output format:

```json
{
  "schema_version": 1,
  "api_command": "generate",
  "app_name": "Laser Test Pattern Generator",
  "app_version": "...",
  "result": {
    "output": "material_test.nc"
  }
}
```

JSON shape for `--format Both`:

```json
{
  "schema_version": 1,
  "api_command": "generate",
  "app_name": "Laser Test Pattern Generator",
  "app_version": "...",
  "results": [
    {
      "output": "material_test.mks"
    },
    {
      "output": "material_test.nc"
    }
  ]
}
```

Important result fields:

- MKS results may include `output`, `paths`, `shapes`, `label_shapes`,
  `tile_shapes`, `speeds_visual_top_to_bottom`, `powers_left_to_right`,
  `grid_width`, `grid_height`, and `warnings`.
- NC results may include `output`, `format`, `lines`, `tiles`,
  `speeds_visual_top_to_bottom`, `powers_left_to_right`, `power_profile`, and
  `s_max`.

Intended frontend usage:

- Trigger generation only after the user confirms settings.
- Treat this command as the only JSON API command that writes files.
- Surface generated output paths and warnings to the user.
- Read generated paths from the returned `result` or `results` data. Do not
  infer an NC path from an MKS path, or an MKS path from an NC path.
- Preserve backend overwrite behavior instead of implementing a separate
  frontend overwrite policy.

## Frontend Architecture Guidance

- The Python backend and JSON CLI API are the source of truth.
- Future Tauri v2.0 or companion frontends should call the JSON CLI API.
- Frontends should initialize controls from `default-settings`.
- Frontends should use `preview` for safe, read-only layout feedback.
- Frontends should call `generate` only when the user intentionally wants files
  written.
- Frontends should not duplicate MKS/NC toolpath generation logic.
- Frontends should not duplicate default settings manually.
- Any generated `.mks` or `.nc` file must still be previewed and verified before
  running on a real laser.
