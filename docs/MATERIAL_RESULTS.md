# Material Result Logging

Material result logging is a small local foundation for recording real-world
test observations after a pattern has been generated and tested.

It is not a full material database, not a cloud service, and not a replacement
for careful machine-specific verification. It writes a simple JSONL file: one
JSON object per line.

## Basic CLI Usage

Append one result entry:

```bash
python makera_material_test_generator.py --log-result --material-name cork --result-rating good --result-notes "Clean cut at selected tile"
```

Choose a log path:

```bash
python makera_material_test_generator.py --log-result --result-log material_test_results.jsonl --material-name cork --result-rating unclear
```

Common optional fields:

```bash
python makera_material_test_generator.py --log-result ^
  --result-log material_test_results.jsonl ^
  --material-name cork ^
  --machine-name "Carvera Air" ^
  --laser-module "10W diode" ^
  --manifest cork_test.manifest.json ^
  --generated-output cork_test.nc ^
  --selected-speed 1800 ^
  --selected-power 24 ^
  --result-rating good ^
  --result-notes "Best tile was clean with light edge darkening" ^
  --photo photos/cork_test.jpg
```

On macOS/Linux, use backslashes or a single line according to your shell.

## JSON API Usage

The JSON CLI API can append a result entry without generating files:

```bash
python makera_material_test_generator.py --api log-result --result-log material_test_results.jsonl --material-name cork --result-rating good
```

The response includes:

- `schema_version`
- `api_command`
- `success`
- `log_path`
- `entry`

## Ratings

The first version uses a small fixed set of result ratings:

- `good`
- `too_light`
- `too_dark`
- `burned`
- `unclear`

Use `notes` for details that do not fit the rating.

## Using Job Manifests

Job manifests describe the generated test pattern and output files. Material
result log entries can reference a manifest with `--manifest`, which makes it
easier to connect a real-world observation back to the generated settings.

This is intentionally only a foundation. A future GUI can build on the JSONL
log and job manifests to offer a more complete material result workflow.
