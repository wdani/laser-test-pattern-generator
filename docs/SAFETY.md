# Safety Notes

This project generates laser test patterns. Always verify generated files before
running a laser.

## For Makera Studio `.mks`

1. Open the generated `.mks`.
2. Press **Recalculate**.
3. Check the Preview.
4. Export or run only after verifying the toolpaths.

## For generic `.nc`

Generic NC/G-code is controller-dependent. Different controllers use different
laser power scales:

- `S1`
- `S255`
- `S1000`
- `S10000`

Set **NC S max** correctly and always preview the file in your sender/CAM before use.

## General Laser Safety

- Start with conservative power and speed settings for unknown materials.
- Use proper ventilation and fire-safe fixturing.
- Never leave a laser unattended.
- Keep an appropriate fire extinguisher nearby.
- Follow the safety manual for your machine, material, and controller.
