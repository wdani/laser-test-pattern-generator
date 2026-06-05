# Changelog

## v1.5.0 - 2026-06-05

UI/UX upgrade release.

### Added

- Added a right-side quick preview on wide GUI windows using the same layout
  preview drawing as the Preview tab.
- Added automatic preview refresh after successful generation.
- Added lightweight GUI tooltips and clearer inline hints for output, grid,
  parameter, laser/NC, label, and preset workflows.
- Added a small non-intrusive Safety / Verify reminder in the GUI.
- Added tests for GUI output suffix sync helper behavior.

### Changed

- Improved GUI spacing, grouping, and status/log messages.
- Improved the Preview tab summary formatting and warning visibility.
- The GUI output path now updates known generated suffixes `.mks` and `.nc`
  when switching output format, while leaving custom suffixes unchanged.
- Bumped visible version text to v1.5.0.

## v1.4.0 - 2026-06-05

Preset and material workflow release.

### Added

- Added preset metadata support for optional `name`, `material`, `machine`,
  `laser_module`, `notes`, `safety_note`, and `reference_image` fields.
- Added GUI support for creating a new preset by typing a new preset name and
  clicking **Save preset**.
- Improved preset import/export so JSON files can be copied into and out of the
  local `presets/` folder.
- Added overwrite confirmation when saving or importing over an existing preset.
- Added optional `reference_image` preset metadata for result/reference photos.
- Added preset helper tests covering metadata, old-format compatibility,
  reference images, overwrite protection, and import/export behavior.
- Added [docs/PRESETS.md](docs/PRESETS.md) with preset sharing and safety notes.
- Added conservative preset starting points for cork, wood, cardboard, and
  Makera-style generic NC tests.

### Changed

- Bumped visible version text to v1.4.0.
- Updated included presets with optional material workflow metadata.

## v1.3 - 2026-06-05

Small generic NC polish release.

### Changed

- Expanded generated generic `.nc` header comments with generator version,
  selected NC power profile, NC S max, speed and power ranges, grid size, tile
  size, gap, laser mode, line interval, and an S-value scale reminder.
- Bumped visible version text to v1.3.

### Tests

- Added checks that generated `.nc` headers contain the selected NC power
  profile and resolved NC S max.

## v1.2 - 2026-06-05

Documentation and preview polish release.

### Fixed

- Fixed the Preview tab summary text so line breaks render as real new lines
  instead of literal `\n` text.

### Added

- Added README screenshots for grid setup, Laser / NC settings, built-in layout
  preview, and Makera Studio preview after Recalculate.

## v1.1 - 2026-06-04

Small generic NC power scale fix.

### Changed

- Changed the default generic NC profile to Makera-style `S0.0` to `S1.0`.
- Added NC power profiles for Makera, GRBL, 8-bit, and Custom S-value scales.
- Added a GUI `NC power profile` dropdown in the Laser / NC tab.
- Added CLI option `--nc-power-profile`.
- Kept `--nc-s-max` for the Custom/manual profile.
- Updated included presets to store the Makera NC power profile explicitly.

### Tests

- Added checks for Makera `S0.2` / `S0.4` output.
- Added checks for GRBL `S200` / `S400` output.

## v1.0 - 2026-06-04

First clean public release baseline.

### Added

- Single-file Python/Tkinter generator and GUI.
- Makera Studio `.mks` output.
- Generic `.nc` / G-code output.
- `MKS`, `NC`, and `Both` output modes.
- Preset manager with included JSON presets.
- Makera Studio template project files.
- Auto filename generation.
- Overwrite protection.
- Auto positioning inside stock.
- Approximate preview tab.
- English GUI.
- English/German generated label language option.
- Windows convenience launcher.
- Public release documentation, safety notes, roadmap, and ignore rules.

### Notes

This version should be treated as a first stable prototype. Generated files must
still be previewed before use.
