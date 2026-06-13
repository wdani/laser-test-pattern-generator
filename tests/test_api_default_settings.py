import json
import subprocess
import sys
from dataclasses import fields
from pathlib import Path

from laser_test_pattern_generator import app
from laser_test_pattern_generator.settings import APP_VERSION, GeneratorSettings, NC_POWER_PROFILES


REPO_ROOT = Path(__file__).resolve().parent.parent
METADATA_KEYS = {"schema_version", "api_command", "app_name", "app_version"}


def run_default_settings_cli() -> dict:
    result = subprocess.run(
        [
            sys.executable,
            str(Path("makera_material_test_generator.py")),
            "--api",
            "default-settings",
        ],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip(), "Output should not be empty"
    return json.loads(result.stdout)


def serializable_value(value):
    if isinstance(value, Path):
        return str(value)
    return value


def default_settings() -> GeneratorSettings:
    return app.settings_from_args(app.parse_args([]))


def test_settings_to_api_defaults_includes_metadata():
    data = app.settings_to_api_defaults(default_settings())

    assert data["schema_version"] == 1
    assert data["api_command"] == "default-settings"
    assert data["app_name"] == "Laser Test Pattern Generator"
    assert data["app_version"] == APP_VERSION


def test_settings_to_api_defaults_includes_every_generator_setting():
    settings = default_settings()
    data = app.settings_to_api_defaults(settings)

    setting_keys = {field_info.name for field_info in fields(GeneratorSettings)}
    missing_keys = setting_keys - set(data)
    unexpected_keys = set(data) - setting_keys - METADATA_KEYS

    assert not missing_keys, f"Missing GeneratorSettings fields: {sorted(missing_keys)}"
    assert not unexpected_keys, f"Unexpected default-settings keys: {sorted(unexpected_keys)}"

    for field_info in fields(GeneratorSettings):
        expected = serializable_value(getattr(settings, field_info.name))
        assert data[field_info.name] == expected


def test_default_settings_cli_returns_valid_json_from_real_defaults():
    settings = default_settings()
    data = run_default_settings_cli()

    for field_info in fields(GeneratorSettings):
        expected = serializable_value(getattr(settings, field_info.name))
        assert data[field_info.name] == expected


def test_default_settings_contains_generation_relevant_fields():
    data = run_default_settings_cli()

    expected_keys = {
        "output_path",
        "output_format",
        "overwrite_existing",
        "auto_filename",
        "material_name",
        "rows",
        "cols",
        "speed_min",
        "speed_max",
        "power_min",
        "power_max",
        "tile_size",
        "gap",
        "grid_x",
        "grid_y",
        "auto_position",
        "tile_mode_name",
        "line_interval",
        "passes",
        "bidirectional",
        "scan_angle",
        "labels_enabled",
        "language",
        "label_speed",
        "label_power",
        "label_mode_name",
        "label_thickness",
        "stock_x",
        "stock_y",
        "stock_z",
        "round_speed_values",
        "round_power_values",
        "template_dir",
        "nc_flavor",
        "nc_power_profile",
        "nc_s_max",
        "nc_units",
        "nc_include_labels",
        "write_manifest",
        "z_offset",
        "indent_distance",
    }

    missing_keys = expected_keys - set(data)
    assert not missing_keys, f"Missing generation defaults: {sorted(missing_keys)}"


def test_default_settings_serializes_path_values_for_json():
    data = run_default_settings_cli()

    assert isinstance(data["output_path"], str)
    assert data["output_path"] == "makera_material_test_generated.mks"
    assert data["template_dir"] is None


def test_default_settings_uses_known_nc_power_profile():
    data = run_default_settings_cli()

    assert data["nc_power_profile"] in NC_POWER_PROFILES
    assert isinstance(data["nc_s_max"], (int, float))


def test_app_info_includes_default_settings():
    result = subprocess.run(
        [
            sys.executable,
            str(Path("makera_material_test_generator.py")),
            "--api",
            "app-info",
        ],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    assert result.returncode == 0, result.stderr

    data = json.loads(result.stdout)
    assert "default-settings" in data["available_api_commands"]
