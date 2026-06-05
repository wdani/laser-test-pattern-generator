# Changelog

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
