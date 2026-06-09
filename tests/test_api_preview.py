import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def run_preview_cli(*args: str) -> dict:
    result = subprocess.run(
        [
            sys.executable,
            str(Path("makera_material_test_generator.py")),
            "--api",
            "preview",
            *args,
        ],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    text = result.stdout.strip()
    assert text.startswith("{")
    assert text.endswith("}")
    return json.loads(text)


def test_preview_returns_valid_json():
    data = run_preview_cli()

    assert data["schema_version"] == 1
    assert data["api_command"] == "preview"
    assert data["app_name"] == "Laser Test Pattern Generator"
    assert "app_version" in data


def test_preview_uses_cli_arguments():
    data = run_preview_cli(
        "--rows",
        "2",
        "--cols",
        "3",
        "--speed-min",
        "1000",
        "--speed-max",
        "2000",
        "--power-min",
        "10",
        "--power-max",
        "30",
        "--format",
        "NC",
    )

    assert data["output_format"] == "NC"
    assert data["rows"] == 2
    assert data["cols"] == 3
    assert data["tile_count"] == 6
    assert data["speeds_visual_top_to_bottom"] == [2000, 1000]
    assert data["powers_left_to_right"] == [10, 20, 30]


def test_preview_applies_generation_rounding_rules():
    rounded = run_preview_cli(
        "--rows",
        "2",
        "--cols",
        "3",
        "--speed-min",
        "1000.4",
        "--speed-max",
        "2000.4",
        "--power-min",
        "10.4",
        "--power-max",
        "30.4",
    )

    unrounded = run_preview_cli(
        "--rows",
        "2",
        "--cols",
        "3",
        "--speed-min",
        "1000.4",
        "--speed-max",
        "2000.4",
        "--power-min",
        "10.4",
        "--power-max",
        "30.4",
        "--no-round-speed",
        "--no-round-power",
    )

    assert rounded["speeds_visual_top_to_bottom"] == [2000, 1000]
    assert rounded["powers_left_to_right"] == [10, 20, 30]
    assert unrounded["speeds_visual_top_to_bottom"] == [2000.4, 1000.4]
    assert unrounded["powers_left_to_right"] == [10.4, 20.4, 30.4]


def test_preview_includes_axis_values():
    data = run_preview_cli("--rows", "2", "--cols", "2")

    assert "speeds_visual_top_to_bottom" in data
    assert "powers_left_to_right" in data
    assert len(data["speeds_visual_top_to_bottom"]) == 2
    assert len(data["powers_left_to_right"]) == 2


def test_preview_does_not_create_requested_output_file(tmp_path):
    output_path = tmp_path / "preview_should_not_exist.mks"
    missing_templates = tmp_path / "missing_templates"

    data = run_preview_cli(
        "--output",
        str(output_path),
        "--format",
        "Both",
        "--template-dir",
        str(missing_templates),
    )

    assert data["output_format"] == "Both"
    assert not output_path.exists()
    assert not output_path.with_suffix(".nc").exists()


def test_preview_reports_layout_dimensions_and_tile_count():
    data = run_preview_cli(
        "--rows",
        "2",
        "--cols",
        "3",
        "--tile-size",
        "5",
        "--gap",
        "1",
    )

    assert data["tile_count"] == 6
    assert data["grid_width"] == 17
    assert data["grid_height"] == 11
    assert data["approx_bounds"]["min_x"] < data["approx_bounds"]["max_x"]
    assert data["approx_bounds"]["min_y"] < data["approx_bounds"]["max_y"]


def test_preview_applies_auto_positioning():
    data = run_preview_cli(
        "--rows",
        "2",
        "--cols",
        "3",
        "--tile-size",
        "5",
        "--gap",
        "1",
        "--grid-x",
        "1",
        "--grid-y",
        "2",
        "--stock-x",
        "200",
        "--stock-y",
        "200",
    )

    assert data["auto_position"] is True
    assert data["grid_x"] != 1
    assert data["grid_y"] != 2


def test_preview_returns_warnings_when_layout_exceeds_stock():
    data = run_preview_cli(
        "--rows",
        "4",
        "--cols",
        "4",
        "--tile-size",
        "20",
        "--gap",
        "5",
        "--stock-x",
        "30",
        "--stock-y",
        "30",
    )

    assert data["warnings"]
    assert any("Layout may exceed stock" in warning for warning in data["warnings"])
