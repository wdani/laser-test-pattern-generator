# NC Output Flavors

Laser Test Pattern Generator supports two `.nc` output flavors:

- `generic`
- `makera-studio`

The default is `generic`. Existing generic NC output behavior remains the
default and is intended to be controller-neutral.

## Generic NC

Generic NC/G-code is the existing output style. It uses a controller-selected
S-value scale through the NC power profile settings:

- `Makera (0-1)`
- `GRBL (0-1000)`
- `8-bit (0-255)`
- `Custom`

Always verify the S-value scale and preview the file in your sender/CAM before
running a laser.

## Experimental Makera Studio NC

The `makera-studio` flavor is experimental. It is based on observed exports from
the current Makera Studio `.nc` output style.

Use it from the CLI with:

```bash
python makera_material_test_generator.py --format NC --nc-flavor makera-studio --output material_test_makera_studio.nc
```

This flavor targets the new Makera Studio-style `.nc` export. It does not
support or recreate legacy Makera CAM `.mkc`, and it does not support old Makera
CAM `.nc` behavior.

Makera Studio-style NC output:

- Uses Makera metadata comments such as `;@MKR|BEGIN`.
- Uses one startup `M3` near the beginning.
- Puts `S` and `F` on cutting `G1` moves.
- Uses `G1 S0` after strokes, scanlines, or contour paths.
- Supports Line, Fill, and Offset Fill tile modes.
- Supports labels using deterministic built-in stroke/bar geometry.

It is still machine-control output. Preview and verify the generated file before
running it on real hardware.

## Z Offset

`z_offset` is exposed as a setting for future Makera Studio Laser Vector parity
and is recorded in settings/defaults/manifests.

Observed Makera Studio direct NC exports still emit:

```gcode
G0 Z0
```

even when a Z Offset is present in the Studio settings. For parity with the
observed direct NC export, the experimental Makera Studio NC flavor also keeps
`G0 Z0` for now and does not emit arbitrary `G0 Z<z_offset>`.

## Indent Distance

`indent_distance` is exposed for Makera Studio-style Fill and Offset Fill
geometry. It shrinks the effective fill/offset rectangle inward. If the indent
is too large for the tile size, generation fails clearly instead of silently
creating invalid geometry.

## Limitations

- Thumbnail/base64 embedding is not implemented yet.
- Per-tile editing is not implemented. The current generator uses global tile
  settings.
- This is not a replacement for previewing/recalculating/verifying generated
  machine files.
- Local reference `.nc` files used during development live under ignored temp
  folders and are not part of the repository.
