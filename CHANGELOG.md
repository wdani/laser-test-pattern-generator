# Changelog

## v1.6.3 - 2026-06-09

JSON API config workflow and privacy-friendly update check release.

### Added

- Added JSON config-file support for `--api preview` and `--api generate` so
  automation, future frontends, and companion tools can share generation
  settings without duplicating long command lines.
- Added example API config files under `examples/api/` for preview, generic NC
  generation, and combined MKS/NC generation.
- Added a manual GUI update check via **Help -> Check for updates** that
  compares the current app version with the latest GitHub Release.
- Added optional startup update checks, disabled by default, with at-most-once
  per day checking when enabled.
- Added update notification actions for remind tomorrow, remind in 10 days,
  remind in 30 days, ignore this version, and disable update checks.

### Changed

- Improved JSON API documentation for config-file usage, CLI override
  precedence, and result-path handling.
- Bumped visible version text to v1.6.3.

### Notes

- The update check only contacts GitHub Releases when run manually or when
  startup checks are explicitly enabled.
- The update check displays current/latest versions and links to the latest
  GitHub Release, but does not auto-download or auto-install anything.
- v1.x remains the stable Python/Tkinter line.
- This release does not include a major Tkinter UI rewrite.
- No generated MKS or generic NC toolpath behavior changed.

## v1.6.2 - 2026-06-09

JSON CLI API backend contract release.

### Added

- Completed the JSON CLI API command set for future UI/frontend work:
  `--api app-info`, `--api default-settings`, `--api preview`, and
  `--api generate`.
- Added read-only `preview` API output for planned layout metadata without
  writing generated files.
- Added `generate` API output for writing MKS/NC files while returning clean
  JSON without the normal human CLI guidance text.
- Added developer API documentation in [docs/JSON_API.md](docs/JSON_API.md).

### Changed

- `app-info` now reports all JSON API commands as available and no planned API
  commands remain.
- Bumped visible version text to v1.6.2.

### Notes

- v1.x remains the stable Python/Tkinter line.
- Future larger UI work is still planned for Tauri v2.0.
- This release does not include a major Tkinter UI rewrite.
- No generated MKS or generic NC toolpath behavior changed.

## v1.6.1 - 2026-06-09

Backend/API groundwork and test hardening release.

### Added

- Added JSON CLI API groundwork for future UI/frontend work:
  `--api app-info` and `--api default-settings`.
- Added API tests for `app-info` and `default-settings`.
- Added stronger generated output validation tests for MKS, NC, and combined
  output generation.

### Changed

- `app-info` now reports the application version from the shared Python
  settings source.
- `default-settings` now derives its response from the real default
  `GeneratorSettings` object so Python core defaults remain the source of
  truth.
- Bumped visible version text to v1.6.1.

### Notes

- v1.x remains the stable Python/Tkinter version.
- This release does not include a major Tkinter UI rewrite.
- No MKS or generic NC generation behavior changed.

## v1.6.0 - 2026-06-05

Modern UI theme release.

### Added

- Added Light and Dark GUI themes using built-in Tkinter/ttk styling.
- Added local UI theme preference persistence in `config/ui_settings.json`
  with safe defaults if the settings file is missing or invalid.
- Added improved numeric controls for common grid, stock, speed, power, laser,
  and label settings while preserving manual text entry.
- Added tests for UI theme settings load/save fallback behavior.

### Changed

- Modernized GUI spacing, button hierarchy, labelframe styling, status/log
  styling, and preview colors for both Light and Dark themes.
- Styled Generate, Load preset, and Save preset as more prominent actions while
  keeping destructive/developer actions less prominent.
- Bumped visible version text to v1.6.0.

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
- Removed manual preview update buttons because the GUI preview now refreshes
  automatically after generation, preset loads, tab changes, and key layout
  edits.
- Hidden the right-side quick preview while the detailed Preview tab is active
  so the detailed preview can use the full width.
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
