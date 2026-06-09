from __future__ import annotations

import argparse
import copy
import json
from dataclasses import fields
from pathlib import Path
from typing import Optional, Sequence

from .generator_mks import generate_mks
from .generator_nc import generate_generic_nc, resolve_nc_s_max
from .geometry import computed_layout, linspace, validate_layout
from .gui import GeneratorGui
from .settings import (
    APP_VERSION,
    DEFAULT_NC_POWER_PROFILE,
    GeneratorSettings,
    LASER_MODES,
    NC_POWER_PROFILES,
)

API_SCHEMA_VERSION = 1
APP_NAME = "Laser Test Pattern Generator"
AVAILABLE_API_COMMANDS = ["app-info", "default-settings", "preview"]
PLANNED_API_COMMANDS = ["generate"]


def positive_int(value: str) -> int:
    i = int(value)
    if i <= 0:
        raise argparse.ArgumentTypeError("must be > 0")
    return i


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate Makera Studio .mks material-test projects.")
    p.add_argument("--gui", action="store_true", help="Open the Tkinter GUI")
    p.add_argument("--output", type=Path, default=Path("makera_material_test_generated.mks"))
    p.add_argument("--overwrite", action="store_true", help="Overwrite the output file if it already exists")
    p.add_argument("--auto-filename", action="store_true", help="Generate filename from material and test settings")
    p.add_argument("--material-name", default="material", help="Material name used for auto filenames")
    p.add_argument("--format", choices=["MKS", "NC", "Both"], default="MKS", help="Output format")
    p.add_argument("--rows", type=positive_int, default=6)
    p.add_argument("--cols", type=positive_int, default=6)
    p.add_argument("--speed-min", type=float, default=2200)
    p.add_argument("--speed-max", type=float, default=2800)
    p.add_argument("--power-min", type=float, default=20)
    p.add_argument("--power-max", type=float, default=40)
    p.add_argument("--tile-size", type=float, default=8.0)
    p.add_argument("--gap", type=float, default=2.0)
    p.add_argument("--grid-x", type=float, default=18.0)
    p.add_argument("--grid-y", type=float, default=8.0)
    p.add_argument("--no-auto-position", action="store_true", help="Use manual Grid X/Y instead of automatic stock placement")
    p.add_argument("--mode", choices=list(LASER_MODES), default="Offset Fill")
    p.add_argument("--line-interval", type=float, default=0.10)
    p.add_argument("--passes", type=positive_int, default=1)
    p.add_argument("--scan-angle", type=float, default=0.0)
    p.add_argument("--no-bidirectional", action="store_true")
    p.add_argument("--language", choices=["English", "Deutsch"], default="English")
    p.add_argument("--no-labels", action="store_true")
    p.add_argument("--label-speed", type=float, default=2500)
    p.add_argument("--label-power", type=float, default=25)
    p.add_argument("--label-mode", choices=list(LASER_MODES), default="Line")
    p.add_argument("--label-thickness", type=float, default=0.06)
    p.add_argument("--stock-x", type=float, default=100)
    p.add_argument("--stock-y", type=float, default=100)
    p.add_argument("--stock-z", type=float, default=20)
    p.add_argument("--no-round-speed", action="store_true", help="Do not round generated speed values")
    p.add_argument("--no-round-power", action="store_true", help="Do not round generated power values")
    p.add_argument("--nc-power-profile", choices=list(NC_POWER_PROFILES), default=DEFAULT_NC_POWER_PROFILE, help="Generic NC laser power scale profile")
    p.add_argument("--nc-s-max", type=float, default=1.0, help="Custom NC S-value for 100 percent power; used when --nc-power-profile Custom")
    p.add_argument("--template-dir", type=Path, default=None)
    p.add_argument("--api", choices=AVAILABLE_API_COMMANDS, help="API commands")
    return p.parse_args(argv)


def settings_from_args(args: argparse.Namespace) -> GeneratorSettings:
    return GeneratorSettings(
        output_path=args.output,
        output_format=args.format,
        overwrite_existing=args.overwrite,
        auto_filename=args.auto_filename,
        material_name=args.material_name,
        rows=args.rows,
        cols=args.cols,
        speed_min=args.speed_min,
        speed_max=args.speed_max,
        power_min=args.power_min,
        power_max=args.power_max,
        tile_size=args.tile_size,
        gap=args.gap,
        grid_x=args.grid_x,
        grid_y=args.grid_y,
        auto_position=not args.no_auto_position,
        tile_mode_name=args.mode,
        line_interval=args.line_interval,
        passes=args.passes,
        bidirectional=not args.no_bidirectional,
        scan_angle=args.scan_angle,
        labels_enabled=not args.no_labels,
        language=args.language,
        label_speed=args.label_speed,
        label_power=args.label_power,
        label_mode_name=args.label_mode,
        label_thickness=args.label_thickness,
        stock_x=args.stock_x,
        stock_y=args.stock_y,
        stock_z=args.stock_z,
        round_speed_values=not args.no_round_speed,
        round_power_values=not args.no_round_power,
        template_dir=args.template_dir,
        nc_power_profile=args.nc_power_profile,
        nc_s_max=resolve_nc_s_max(args.nc_power_profile, args.nc_s_max),
    )


def api_json_value(value):
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, tuple):
        return [api_json_value(item) for item in value]
    if isinstance(value, list):
        return [api_json_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): api_json_value(item) for key, item in value.items()}
    return value


def app_info_response() -> dict:
    return {
        "schema_version": API_SCHEMA_VERSION,
        "app_name": APP_NAME,
        "app_version": APP_VERSION,
        "backend": "Python",
        "supported_output_formats": ["MKS", "NC", "Both"],
        "available_api_commands": AVAILABLE_API_COMMANDS,
        "planned_api_commands": PLANNED_API_COMMANDS,
    }


def settings_to_api_defaults(settings: GeneratorSettings) -> dict:
    data = {
        "schema_version": API_SCHEMA_VERSION,
        "api_command": "default-settings",
        "app_name": APP_NAME,
        "app_version": APP_VERSION,
    }

    for field_info in fields(GeneratorSettings):
        data[field_info.name] = api_json_value(getattr(settings, field_info.name))

    return data


def rounded_axis_values(start: float, end: float, count: int, should_round: bool) -> list:
    values = linspace(start, end, count)
    if should_round:
        return [int(round(value)) for value in values]
    return [round(value, 6) for value in values]


def preview_response(settings: GeneratorSettings) -> dict:
    preview_settings = copy.deepcopy(settings)
    rows = int(preview_settings.rows)
    cols = int(preview_settings.cols)

    speeds = rounded_axis_values(
        preview_settings.speed_min,
        preview_settings.speed_max,
        rows,
        preview_settings.round_speed_values,
    )
    powers = rounded_axis_values(
        preview_settings.power_min,
        preview_settings.power_max,
        cols,
        preview_settings.round_power_values,
    )

    layout = computed_layout(preview_settings)

    return {
        "schema_version": API_SCHEMA_VERSION,
        "api_command": "preview",
        "app_name": APP_NAME,
        "app_version": APP_VERSION,
        "output_format": preview_settings.output_format,
        "rows": rows,
        "cols": cols,
        "tile_count": rows * cols,
        "tile_size": preview_settings.tile_size,
        "gap": preview_settings.gap,
        "grid_x": preview_settings.grid_x,
        "grid_y": preview_settings.grid_y,
        "auto_position": preview_settings.auto_position,
        "grid_width": layout["grid_w"],
        "grid_height": layout["grid_h"],
        "stock_x": preview_settings.stock_x,
        "stock_y": preview_settings.stock_y,
        "stock_z": preview_settings.stock_z,
        "labels_enabled": preview_settings.labels_enabled,
        "language": preview_settings.language,
        "tile_mode_name": preview_settings.tile_mode_name,
        "line_interval": preview_settings.line_interval,
        "passes": preview_settings.passes,
        "bidirectional": preview_settings.bidirectional,
        "scan_angle": preview_settings.scan_angle,
        "speeds_visual_top_to_bottom": list(reversed(speeds)),
        "powers_left_to_right": powers,
        "approx_bounds": {
            "min_x": layout["layout_min_x"],
            "max_x": layout["layout_max_x"],
            "min_y": layout["layout_min_y"],
            "max_y": layout["layout_max_y"],
        },
        "warnings": validate_layout(preview_settings),
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    if args.gui:
        gui = GeneratorGui()
        gui.run()
        return 0

    if args.api == "app-info":
        print(json.dumps(app_info_response(), indent=2))
        return 0

    if args.api == "default-settings":
        settings = settings_from_args(parse_args([]))
        print(json.dumps(settings_to_api_defaults(settings), indent=2))
        return 0

    if args.api == "preview":
        settings = settings_from_args(args)
        print(json.dumps(preview_response(settings), indent=2))
        return 0

    settings = settings_from_args(args)
    infos = []
    if settings.output_format in ("MKS", "Both"):
        infos.append(generate_mks(copy.deepcopy(settings)))
    if settings.output_format in ("NC", "Both"):
        infos.append(generate_generic_nc(copy.deepcopy(settings)))

    print(json.dumps(infos if len(infos) > 1 else infos[0], indent=2, ensure_ascii=False))
    print("\nFor MKS: open in Makera Studio, click Recalculate, inspect Preview, then export.")
    print("For NC: verify your laser controller's S-value scale and preview in your sender/CAM before use.")
    return 0
