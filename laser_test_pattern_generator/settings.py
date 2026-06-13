from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional


LASER_MODES = {
    "Line": 0,
    "Fill": 1,
    "Offset Fill": 2,
}

APP_VERSION = "v1.6.3"

NC_POWER_PROFILES: Dict[str, Optional[float]] = {
    "Makera (0-1)": 1.0,
    "GRBL (0-1000)": 1000.0,
    "8-bit (0-255)": 255.0,
    "Custom": None,
}
DEFAULT_NC_POWER_PROFILE = "Makera (0-1)"

NC_FLAVORS = {
    "generic": "Generic",
    "makera-studio": "Makera Studio",
}
DEFAULT_NC_FLAVOR = "generic"


@dataclass
class GeneratorSettings:
    output_path: Path
    output_format: str = "MKS"
    overwrite_existing: bool = False
    auto_filename: bool = False
    material_name: str = "material"
    rows: int = 6
    cols: int = 6
    speed_min: float = 2200
    speed_max: float = 2800
    power_min: float = 20
    power_max: float = 40
    tile_size: float = 8.0
    gap: float = 2.0
    grid_x: float = 18.0
    grid_y: float = 8.0
    auto_position: bool = True
    tile_mode_name: str = "Offset Fill"
    line_interval: float = 0.10
    passes: int = 1
    bidirectional: bool = True
    scan_angle: float = 0.0
    labels_enabled: bool = True
    label_speed: float = 2500
    label_power: float = 25
    label_mode_name: str = "Line"
    label_thickness: float = 0.06
    stock_x: float = 100
    stock_y: float = 100
    stock_z: float = 20
    round_speed_values: bool = True
    round_power_values: bool = True
    language: str = "English"
    axis_power_label: str = "POWER (%)"
    axis_speed_label: str = "SPEED (MM/MIN)"
    power_axis_text_height: float = 3.0
    power_number_text_height: float = 2.6
    speed_axis_text_height: float = 2.2
    speed_number_text_height: float = 2.4
    template_dir: Optional[Path] = None
    nc_flavor: str = DEFAULT_NC_FLAVOR
    nc_power_profile: str = DEFAULT_NC_POWER_PROFILE
    nc_s_max: float = 1.0
    nc_units: str = "mm"
    nc_include_labels: bool = True
    write_manifest: bool = False
    z_offset: float = 0.0
    indent_distance: float = 0.0

