from __future__ import annotations

import argparse
import copy
import json
import sys
from dataclasses import fields
from pathlib import Path
from typing import Optional, Sequence

from .generator_mks import generate_mks
from .generator_nc import generate_generic_nc, resolve_nc_s_max
from .generator_nc_makera import MakeraStudioNcGenerationError, generate_makera_studio_nc
from .geometry import computed_layout, linspace, validate_layout
from .gui import GeneratorGui
from .job_manifest import write_job_manifest
from .material_log import (
    DEFAULT_RESULT_LOG_PATH,
    RESULT_RATINGS,
    MaterialLogError,
    append_material_result,
    build_material_result_entry,
)
from .safety_preflight import CHECKLIST_NAME, CHECKLIST_VERSION, safety_preflight_items
from .settings import (
    APP_VERSION,
    DEFAULT_NC_POWER_PROFILE,
    GeneratorSettings,
    LASER_MODES,
    NC_FLAVORS,
    NC_POWER_PROFILES,
)

API_SCHEMA_VERSION = 1
APP_NAME = "Laser Test Pattern Generator"
AVAILABLE_API_COMMANDS = [
    "app-info",
    "default-settings",
    "preview",
    "generate",
    "log-result",
    "preflight-checklist",
]
PLANNED_API_COMMANDS = []
CONFIG_API_COMMANDS = {"preview", "generate"}

CONFIG_SCALAR_OPTIONS = {
    "output_path": "--output",
    "output": "--output",
    "output_format": "--format",
    "format": "--format",
    "material_name": "--material-name",
    "rows": "--rows",
    "cols": "--cols",
    "speed_min": "--speed-min",
    "speed_max": "--speed-max",
    "power_min": "--power-min",
    "power_max": "--power-max",
    "tile_size": "--tile-size",
    "gap": "--gap",
    "grid_x": "--grid-x",
    "grid_y": "--grid-y",
    "tile_mode_name": "--mode",
    "mode": "--mode",
    "line_interval": "--line-interval",
    "passes": "--passes",
    "scan_angle": "--scan-angle",
    "language": "--language",
    "label_speed": "--label-speed",
    "label_power": "--label-power",
    "label_mode_name": "--label-mode",
    "label_mode": "--label-mode",
    "label_thickness": "--label-thickness",
    "stock_x": "--stock-x",
    "stock_y": "--stock-y",
    "stock_z": "--stock-z",
    "nc_power_profile": "--nc-power-profile",
    "nc_s_max": "--nc-s-max",
    "nc_flavor": "--nc-flavor",
    "z_offset": "--z-offset",
    "indent_distance": "--indent-distance",
    "template_dir": "--template-dir",
}

CONFIG_BOOLEAN_OPTIONS = {
    "overwrite_existing": ("--overwrite", "--no-overwrite"),
    "overwrite": ("--overwrite", "--no-overwrite"),
    "auto_filename": ("--auto-filename", "--no-auto-filename"),
    "auto_position": ("--auto-position", "--no-auto-position"),
    "bidirectional": ("--bidirectional", "--no-bidirectional"),
    "labels_enabled": ("--labels", "--no-labels"),
    "labels": ("--labels", "--no-labels"),
    "round_speed_values": ("--round-speed", "--no-round-speed"),
    "round_power_values": ("--round-power", "--no-round-power"),
    "nc_include_labels": ("--nc-include-labels", "--no-nc-include-labels"),
    "write_manifest": ("--write-manifest", "--no-write-manifest"),
}


class ConfigError(ValueError):
    pass


def positive_int(value: str) -> int:
    i = int(value)
    if i <= 0:
        raise argparse.ArgumentTypeError("must be > 0")
    return i


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate Makera Studio .mks material-test projects.")
    p.add_argument("--gui", action="store_true", help="Open the Tkinter GUI")
    p.add_argument("--output", type=Path, default=Path("makera_material_test_generated.mks"))
    p.add_argument("--overwrite", dest="overwrite", action="store_true", help="Overwrite the output file if it already exists")
    p.add_argument("--no-overwrite", dest="overwrite", action="store_false", help=argparse.SUPPRESS)
    p.add_argument("--auto-filename", dest="auto_filename", action="store_true", help="Generate filename from material and test settings")
    p.add_argument("--no-auto-filename", dest="auto_filename", action="store_false", help=argparse.SUPPRESS)
    p.add_argument("--material-name", default=None, help="Material name used for auto filenames")
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
    p.add_argument("--auto-position", dest="no_auto_position", action="store_false", help=argparse.SUPPRESS)
    p.add_argument("--no-auto-position", dest="no_auto_position", action="store_true", help="Use manual Grid X/Y instead of automatic stock placement")
    p.add_argument("--mode", choices=list(LASER_MODES), default="Offset Fill")
    p.add_argument("--line-interval", type=float, default=0.10)
    p.add_argument("--passes", type=positive_int, default=1)
    p.add_argument("--scan-angle", type=float, default=0.0)
    p.add_argument("--bidirectional", dest="no_bidirectional", action="store_false", help=argparse.SUPPRESS)
    p.add_argument("--no-bidirectional", dest="no_bidirectional", action="store_true")
    p.add_argument("--language", choices=["English", "Deutsch"], default="English")
    p.add_argument("--labels", dest="no_labels", action="store_false", help=argparse.SUPPRESS)
    p.add_argument("--no-labels", dest="no_labels", action="store_true")
    p.add_argument("--label-speed", type=float, default=2500)
    p.add_argument("--label-power", type=float, default=25)
    p.add_argument("--label-mode", choices=list(LASER_MODES), default="Line")
    p.add_argument("--label-thickness", type=float, default=0.06)
    p.add_argument("--stock-x", type=float, default=100)
    p.add_argument("--stock-y", type=float, default=100)
    p.add_argument("--stock-z", type=float, default=20)
    p.add_argument("--round-speed", dest="no_round_speed", action="store_false", help=argparse.SUPPRESS)
    p.add_argument("--no-round-speed", dest="no_round_speed", action="store_true", help="Do not round generated speed values")
    p.add_argument("--round-power", dest="no_round_power", action="store_false", help=argparse.SUPPRESS)
    p.add_argument("--no-round-power", dest="no_round_power", action="store_true", help="Do not round generated power values")
    p.add_argument("--nc-flavor", choices=list(NC_FLAVORS), default="generic", help="NC output flavor: generic or experimental Makera Studio-style")
    p.add_argument("--nc-power-profile", choices=list(NC_POWER_PROFILES), default=DEFAULT_NC_POWER_PROFILE, help="Generic NC laser power scale profile")
    p.add_argument("--nc-s-max", type=float, default=1.0, help="Custom NC S-value for 100 percent power; used when --nc-power-profile Custom")
    p.add_argument("--nc-include-labels", dest="nc_include_labels", action="store_true", help=argparse.SUPPRESS)
    p.add_argument("--no-nc-include-labels", dest="nc_include_labels", action="store_false", help=argparse.SUPPRESS)
    p.add_argument("--z-offset", type=float, default=0.0, help="Laser Z offset setting metadata; Makera Studio NC currently still emits G0 Z0")
    p.add_argument("--indent-distance", type=float, default=0.0, help="Inset distance for Makera Studio-style Fill and Offset Fill geometry")
    p.add_argument("--template-dir", type=Path, default=None)
    p.add_argument("--write-manifest", dest="write_manifest", action="store_true", help="Write an optional JSON job manifest next to generated output")
    p.add_argument("--no-write-manifest", dest="write_manifest", action="store_false", help=argparse.SUPPRESS)
    p.add_argument("--log-result", action="store_true", help="Append one material test result entry to a local JSONL log")
    p.add_argument("--result-log", type=Path, default=DEFAULT_RESULT_LOG_PATH, help="Material result JSONL log path")
    p.add_argument("--result-rating", default=None, help=f"Observed result rating ({', '.join(RESULT_RATINGS)})")
    p.add_argument("--result-notes", default=None, help="Notes for a material test result log entry")
    p.add_argument("--manifest", dest="manifest_path", type=Path, default=None, help="Related job manifest path for result logging")
    p.add_argument("--generated-output", dest="generated_output_path", type=Path, default=None, help="Related generated output path for result logging")
    p.add_argument("--photo", dest="photo_path", type=Path, default=None, help="Related result photo path for result logging")
    p.add_argument("--machine-name", default=None, help="Machine name for result logging")
    p.add_argument("--laser-module", default=None, help="Laser module name for result logging")
    p.add_argument("--selected-speed", type=float, default=None, help="Observed best/selected speed for result logging")
    p.add_argument("--selected-power", type=float, default=None, help="Observed best/selected power for result logging")
    p.add_argument("--api", choices=AVAILABLE_API_COMMANDS, help="API commands")
    p.add_argument("--config", type=Path, default=None, help="JSON config file for API preview/generate")
    p.set_defaults(
        overwrite=False,
        auto_filename=False,
        no_auto_position=False,
        no_bidirectional=False,
        no_labels=False,
        no_round_speed=False,
        no_round_power=False,
        nc_include_labels=True,
        write_manifest=False,
    )
    return p.parse_args(argv)


def settings_from_args(args: argparse.Namespace) -> GeneratorSettings:
    return GeneratorSettings(
        output_path=args.output,
        output_format=args.format,
        overwrite_existing=args.overwrite,
        auto_filename=args.auto_filename,
        material_name=args.material_name or "material",
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
        nc_flavor=args.nc_flavor,
        nc_power_profile=args.nc_power_profile,
        nc_s_max=resolve_nc_s_max(args.nc_power_profile, args.nc_s_max),
        nc_include_labels=args.nc_include_labels,
        write_manifest=args.write_manifest,
        z_offset=args.z_offset,
        indent_distance=args.indent_distance,
    )


def load_config_data(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise ConfigError(f"could not read {path}: {exc}") from exc

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ConfigError(f"{path} is not valid JSON: {exc.msg} at line {exc.lineno}, column {exc.colno}") from exc

    if not isinstance(data, dict):
        raise ConfigError(f"{path} must contain a JSON object")

    return data


def config_value_to_arg(value) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, bool):
        raise ConfigError("expected a string, number, or null value, got boolean")
    if isinstance(value, (str, int, float)):
        return str(value)
    raise ConfigError(f"expected a string, number, or null value, got {type(value).__name__}")


def config_data_to_argv(data: dict) -> list:
    argv = []

    for raw_key, value in data.items():
        key = str(raw_key).replace("-", "_")

        if key in CONFIG_BOOLEAN_OPTIONS:
            if not isinstance(value, bool):
                raise ConfigError(f"config key '{raw_key}' must be true or false")
            true_option, false_option = CONFIG_BOOLEAN_OPTIONS[key]
            argv.append(true_option if value else false_option)
            continue

        if key in CONFIG_SCALAR_OPTIONS:
            arg_value = config_value_to_arg(value)
            if arg_value is None:
                continue
            argv.extend([CONFIG_SCALAR_OPTIONS[key], arg_value])
            continue

        raise ConfigError(f"unsupported config key '{raw_key}'")

    return argv


def parse_args_with_api_config(raw_argv: Sequence[str]) -> argparse.Namespace:
    args = parse_args(raw_argv)
    if args.api not in CONFIG_API_COMMANDS or args.config is None:
        return args

    config_argv = config_data_to_argv(load_config_data(args.config))
    return parse_args(config_argv + list(raw_argv))


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


def preflight_checklist_response() -> dict:
    return {
        "schema_version": API_SCHEMA_VERSION,
        "api_command": "preflight-checklist",
        "app_name": APP_NAME,
        "app_version": APP_VERSION,
        "checklist_name": CHECKLIST_NAME,
        "checklist_version": CHECKLIST_VERSION,
        "items": api_json_value(safety_preflight_items()),
    }


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


def generate_output_infos(settings: GeneratorSettings) -> list:
    infos = []
    if settings.output_format in ("MKS", "Both"):
        infos.append(generate_mks(copy.deepcopy(settings)))
    if settings.output_format in ("NC", "Both"):
        if settings.nc_flavor == "makera-studio":
            infos.append(generate_makera_studio_nc(copy.deepcopy(settings)))
        else:
            infos.append(generate_generic_nc(copy.deepcopy(settings)))
    return infos


def maybe_write_job_manifest(settings: GeneratorSettings, infos: list, source: str) -> Optional[dict]:
    if not settings.write_manifest:
        return None
    return write_job_manifest(settings, infos, source=source)


def generate_response(settings: GeneratorSettings) -> dict:
    infos = generate_output_infos(settings)
    manifest_info = maybe_write_job_manifest(settings, infos, source="api")
    data = {
        "schema_version": API_SCHEMA_VERSION,
        "api_command": "generate",
        "app_name": APP_NAME,
        "app_version": APP_VERSION,
    }

    if len(infos) == 1:
        data["result"] = api_json_value(infos[0])
    else:
        data["results"] = api_json_value(infos)

    if manifest_info is not None:
        data["manifest"] = api_json_value(manifest_info)

    return data


def material_result_response(args: argparse.Namespace, source: str) -> dict:
    entry = build_material_result_entry(
        app_version=APP_VERSION,
        material_name=args.material_name,
        result_rating=args.result_rating,
        source=source,
        machine_name=args.machine_name,
        laser_module=args.laser_module,
        manifest_path=args.manifest_path,
        generated_output_path=args.generated_output_path,
        selected_speed=args.selected_speed,
        selected_power=args.selected_power,
        notes=args.result_notes,
        photo_path=args.photo_path,
    )
    log_path = append_material_result(args.result_log, entry)
    return {
        "schema_version": API_SCHEMA_VERSION,
        "api_command": "log-result",
        "success": True,
        "log_path": str(log_path),
        "entry": api_json_value(entry),
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    raw_argv = list(argv) if argv is not None else sys.argv[1:]
    try:
        args = parse_args_with_api_config(raw_argv)
    except ConfigError as exc:
        print(f"API config error: {exc}", file=sys.stderr)
        return 2

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

    if args.api == "preflight-checklist":
        print(json.dumps(preflight_checklist_response(), indent=2))
        return 0

    if args.api == "preview":
        settings = settings_from_args(args)
        print(json.dumps(preview_response(settings), indent=2))
        return 0

    if args.api == "generate":
        settings = settings_from_args(args)
        try:
            print(json.dumps(generate_response(settings), indent=2, ensure_ascii=False))
        except MakeraStudioNcGenerationError as exc:
            print(f"Makera Studio NC generation error: {exc}", file=sys.stderr)
            return 2
        return 0

    if args.api == "log-result":
        try:
            print(json.dumps(material_result_response(args, source="api"), indent=2, ensure_ascii=False))
        except MaterialLogError as exc:
            print(f"Material log error: {exc}", file=sys.stderr)
            return 2
        return 0

    if args.log_result:
        try:
            print(json.dumps(material_result_response(args, source="cli"), indent=2, ensure_ascii=False))
        except MaterialLogError as exc:
            print(f"Material log error: {exc}", file=sys.stderr)
            return 2
        return 0

    settings = settings_from_args(args)
    try:
        infos = generate_output_infos(settings)
        manifest_info = maybe_write_job_manifest(settings, infos, source="cli")
    except MakeraStudioNcGenerationError as exc:
        print(f"Makera Studio NC generation error: {exc}", file=sys.stderr)
        return 2

    output_data = infos if len(infos) > 1 else infos[0]
    if manifest_info is not None:
        output_data = {
            "results": infos,
            "manifest": manifest_info,
        } if len(infos) > 1 else {
            "result": infos[0],
            "manifest": manifest_info,
        }

    print(json.dumps(output_data, indent=2, ensure_ascii=False))
    print("\nFor MKS: open in Makera Studio, click Recalculate, inspect Preview, then export.")
    print("For NC: verify your laser controller's S-value scale and preview in your sender/CAM before use.")
    return 0
