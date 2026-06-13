# v2 Concept Comparison Prototype

This folder contains two tracked, static v2 UI concepts for comparing future directions of the Laser Test Pattern Generator and a broader CNC/Laser companion app.

Open the central launcher in a browser:

- `index.html`

Or open either concept directly:

- `concept_a_program_shell/index.html`
- `concept_b_workshop_companion/index.html`

The prototypes are HTML/CSS/JavaScript only. They do not call the Python backend, write files, generate machine-control output, or change v1.x behavior.

## Included Concepts

- Concept A: Desktop Program Shell
  - Tests a conventional desktop application with modules, a contextual left submenu, central workflow panels, and a right preview/status rail.
- Concept B: Workshop Companion Command Center
  - Tests a job-oriented workshop dashboard where active jobs are supported by contextual helpers.

## Active Workflows

Both concepts include two active workflow ideas:

- Laser Test Pattern Generator
- Parametric Design / Nameplate Generator

Passive helpers such as safety checklists, V-bit calculators, cost calculators, and journals are shown as supporting surfaces only.

## Scope

This is a static comparison prototype. It is intentionally not a Tauri implementation and not a new generator backend. The stable v1.x Python/Tkinter app and JSON CLI/API remain the source of truth.

