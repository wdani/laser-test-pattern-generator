# v2 Concept Comparison Prototype

This folder contains a static bilingual v2 design comparison for the Laser Test Pattern Generator and a possible future CNC/Laser Companion interface.

## Start

Open the central launcher:

- `index.html`

Collect structured feedback:

- `feedback.html`

The concepts can also be opened directly:

- `concept_a_program_shell/index.html`
- `concept_b_workshop_companion/index.html`

## Language

The launcher, feedback form, Concept A, and Concept B support German and English.

- First load follows the browser language: German for `de*`, otherwise English.
- The selected language is remembered in `localStorage`.
- All pages include the same DE/EN switch and a `Local in browser` / `Lokal im Browser` status badge.

## Concepts

- Concept A: Desktop Program Shell
  - A classic desktop app with modules, left submenu navigation, central workflow, and right preview/status rail.
- Concept B: Workshop Companion Command Center
  - A job-oriented workshop interface where active jobs are supported by helpers, material, machine, and safety context.

## Active Workflows

Both concepts include two active workflow ideas:

- Laser Test Pattern Generator
- Parametric Design / Nameplate Generator

Passive helpers such as Safety Checklist, V-bit Calculator, Cost Calculator, SVG Detail Checker, and Material Journal remain supporting surfaces.

## Feedback

`feedback.html` collects structured comparison notes locally in the browser.

- Nothing is saved automatically.
- Nothing is uploaded.
- There is no backend.
- Users can generate, copy, or download feedback.
- Button labels avoid `.md`; helper text explains that the downloaded file is Markdown.
- A Markdown file is created only if the tester clicks the download button.

## Teaser Assets

The launcher intro uses local images:

- `assets/locked_loading_soon.png` as the open teaser reference.
- `assets/locked_loading_soon_closed.png` as the closed-shutter start frame.

If the closed image cannot load, the prototype remains usable and falls back to the dark CSS laser/shutter background.

## Scope

Everything in this folder is static HTML/CSS/JS.

- No backend.
- No upload.
- No network connection.
- No real machine file generation.
- No machine files.
- No machine output.
- No change to the stable v1.x Python/Tkinter generator.
- No Tauri implementation yet.
