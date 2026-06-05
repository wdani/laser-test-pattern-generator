# Presets

Presets are JSON files that store GUI settings for repeatable material-test
grids. They are starting points, not guaranteed safe laser settings.

## Storage

Built-in and locally saved presets are stored in the repository or package
folder:

```text
presets/
```

In the experimental Windows executable package, keep `presets/` next to
`LaserTestPatternGenerator.exe`.

## Import, Export, And Sharing

Use the GUI **Presets** tab to:

- Load an existing preset.
- Save changes to the selected preset.
- Type a new preset name in the top preset field and click **Save preset** to
  create a new preset.
- Use **Import preset...** to copy a shared JSON preset into your local
  `presets/` folder.
- Use **Export preset...** to copy the selected preset JSON to another location
  for sharing or backup.

The preset field at the top is the only editable preset name. Preset JSON files
may still contain `name` or `_preset_name` for compatibility, but the GUI does
not show a second editable name field.

Saving or importing over an existing preset asks for confirmation first. If you
cancel, the existing preset is left unchanged.

Preset files can include optional metadata:

- `name`
- `material`
- `machine`
- `laser_module`
- `notes`
- `safety_note`
- `reference_image`

Older presets without metadata still load. Unknown JSON fields are ignored by
the GUI, so shared presets can carry extra notes without breaking generation.

`reference_image` is an optional helper path to a photo or result image for the
preset. It is metadata only for now: the app stores the path but does not manage
image files or provide a full material journal.

## Safety

Material behavior depends on the exact material, coating, glue, thickness,
machine, laser module, air assist, focus, and ventilation. Unknown materials
should be tested carefully with low-risk settings, active supervision, and
proper fire safety equipment.

Never treat a preset as a verified safe setting for your machine. Always preview
generated `.mks` files in Makera Studio after Recalculate, and always verify
generic `.nc` files against the target controller before running a laser.
