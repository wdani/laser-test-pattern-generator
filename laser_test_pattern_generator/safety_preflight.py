from __future__ import annotations

import copy

CHECKLIST_NAME = "Laser Safety Preflight Checklist"
CHECKLIST_VERSION = "1.0"

_CHECKLIST_ITEMS = [
    {
        "id": "material_laser_safe",
        "label": "Material is laser-safe",
        "description": "Confirm the material is known to be safe for laser processing on your machine.",
        "category": "material",
        "required": True,
        "applies_to": ["all"],
    },
    {
        "id": "no_pvc_vinyl_chlorinated_material",
        "label": "No PVC, vinyl, or chlorinated material",
        "description": "Do not laser PVC, vinyl, or unknown chlorinated plastics.",
        "category": "material",
        "required": True,
        "applies_to": ["all"],
    },
    {
        "id": "workpiece_flat_secured",
        "label": "Workpiece is flat and secured",
        "description": "Make sure the stock cannot lift, shift, or catch during the job.",
        "category": "machine_setup",
        "required": True,
        "applies_to": ["all"],
    },
    {
        "id": "focus_height_checked",
        "label": "Correct focus / laser height checked",
        "description": "Verify focus or laser height for the selected stock thickness.",
        "category": "machine_setup",
        "required": True,
        "applies_to": ["all"],
    },
    {
        "id": "ventilation_running",
        "label": "Exhaust / ventilation is running",
        "description": "Confirm exhaust and ventilation are active before firing the laser.",
        "category": "environment",
        "required": True,
        "applies_to": ["all"],
    },
    {
        "id": "air_assist_checked",
        "label": "Air assist is enabled if required",
        "description": "Use air assist when the material, lens, or job setup requires it.",
        "category": "machine_setup",
        "required": True,
        "applies_to": ["all"],
    },
    {
        "id": "fire_risk_checked",
        "label": "Fire risk checked",
        "description": "Remove flammable debris and confirm the job can be supervised safely.",
        "category": "fire_safety",
        "required": True,
        "applies_to": ["all"],
    },
    {
        "id": "fire_response_nearby",
        "label": "Fire extinguisher or suitable fire response nearby",
        "description": "Keep an appropriate fire response available for the machine and material.",
        "category": "fire_safety",
        "required": True,
        "applies_to": ["all"],
    },
    {
        "id": "machine_supervised",
        "label": "Machine area is supervised",
        "description": "Never leave a running laser unattended.",
        "category": "fire_safety",
        "required": True,
        "applies_to": ["all"],
    },
    {
        "id": "correct_file_loaded",
        "label": "Correct file loaded",
        "description": "Check that the loaded file matches the intended material test.",
        "category": "file_verification",
        "required": True,
        "applies_to": ["all"],
    },
    {
        "id": "mks_recalculated_previewed",
        "label": "MKS files are recalculated and previewed in Makera Studio",
        "description": "For Makera Studio projects, click Recalculate and inspect Preview before running or exporting.",
        "category": "file_verification",
        "required": True,
        "applies_to": ["MKS", "Both"],
    },
    {
        "id": "nc_s_value_scale_verified",
        "label": "Generic NC S-value scale is verified for the target controller",
        "description": "Confirm the selected NC power profile and S max match the controller before running G-code.",
        "category": "controller",
        "required": True,
        "applies_to": ["NC", "Both"],
    },
    {
        "id": "movement_path_preview_checked",
        "label": "Movement/path preview checked",
        "description": "Preview travel, bounds, and laser-on moves in Makera Studio or the target sender/CAM.",
        "category": "file_verification",
        "required": True,
        "applies_to": ["all"],
    },
    {
        "id": "origin_work_zero_checked",
        "label": "Correct origin/work zero checked",
        "description": "Verify the machine origin or work zero matches the generated layout.",
        "category": "machine_setup",
        "required": True,
        "applies_to": ["all"],
    },
]


def safety_preflight_items() -> list[dict]:
    return copy.deepcopy(_CHECKLIST_ITEMS)
