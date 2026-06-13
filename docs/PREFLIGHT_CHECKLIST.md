# Laser Safety Preflight Checklist

This checklist is a reminder for basic setup and safety checks before using
generated laser files. It is not a guarantee of safety and does not replace the
manuals, training, material data sheets, or procedures for your machine,
material, enclosure, exhaust system, or controller.

The checklist is available as a read-only JSON API command:

```bash
python makera_material_test_generator.py --api preflight-checklist
```

The command does not write `.mks`, `.nc`, log, manifest, or other output files.
It returns stable checklist item IDs that future GUI/frontend work can display
without duplicating the checklist by hand.

## Material Warnings

- Only process materials that are known to be laser-safe for your machine.
- Do not laser PVC, vinyl, or unknown chlorinated plastics.
- Be careful with unknown coatings, adhesives, laminates, foams, and composite
  materials.
- Start conservatively and supervise the machine area whenever testing a new
  material.

## File Verification

For Makera Studio `.mks` files:

1. Open the generated project in Makera Studio.
2. Click **Recalculate**.
3. Inspect the Makera Studio Preview before running or exporting.

For generic `.nc` files:

1. Verify the selected NC power profile and S-value scale for the target
   controller.
2. Preview the path in the sender/CAM software.
3. Confirm travel moves, work zero, origin, and bounds before running.

## Practical Preflight Areas

The checklist covers:

- Material safety.
- PVC/vinyl/chlorinated material avoidance.
- Flat and secured workpiece.
- Focus or laser height.
- Exhaust and ventilation.
- Air assist when required.
- Fire risk and suitable fire response.
- Supervision.
- Correct file, preview, origin, and controller checks.

This is a small foundation for future UI integration, not a complex wizard or
blocking workflow.
