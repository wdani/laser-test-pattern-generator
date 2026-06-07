from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Optional, Sequence

from .generator_mks import generate_mks
from .generator_nc import generate_generic_nc, resolve_nc_s_max
from .gui import GeneratorGui
from .settings import (
    DEFAULT_NC_POWER_PROFILE,
    GeneratorSettings,
    LASER_MODES,
    NC_POWER_PROFILES,
)


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
    p.add_argument("--api", choices=["app-info"], help="API commands")
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


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    if args.gui:
        gui = GeneratorGui()
        gui.run()
        return 0

    if args.api == "app-info":
        app_info = {
            "schema_version": 1,
            "app_name": "Laser Test Pattern Generator",
            "app_version": "v1.6.0",
            "backend": "Python",
            "supported_output_formats": ["MKS", "NC", "Both"],
            "available_api_commands": ["app-info"],
            "planned_api_commands": ["default-settings", "preview", "generate"]
        }
        print(json.dumps(app_info, indent=2))
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
