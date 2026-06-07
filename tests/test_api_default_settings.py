import json
import subprocess
import sys
from pathlib import Path

def test_default_settings_returns_valid_json():
    """Test that --api default-settings returns valid JSON with expected structure."""
    # Run the command
    result = subprocess.run([
        sys.executable,
        str(Path("makera_material_test_generator.py")),
        "--api", "default-settings"
    ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)

    assert result.returncode == 0, f"Command failed with return code {result.returncode}"
    assert result.stdout.strip(), "Output should not be empty"

    # Parse the JSON
    data = json.loads(result.stdout)

    # Check required fields
    assert data["schema_version"] == 1
    assert data["api_command"] == "default-settings"
    assert data["app_name"] == "Laser Test Pattern Generator"

    # Check that all expected keys are present
    expected_keys = [
        "output_format", "rows", "cols", "speed_min", "speed_max",
        "power_min", "power_max", "tile_size", "gap", "labels",
        "nc_power_profile", "nc_s_max"
    ]

    for key in expected_keys:
        assert key in data, f"Missing key: {key}"

    # Check specific value types
    assert data["output_format"] in ["MKS", "NC", "Both"]
    assert isinstance(data["rows"], int)
    assert isinstance(data["cols"], int)
    assert isinstance(data["speed_min"], (int, float))
    assert isinstance(data["speed_max"], (int, float))
    assert isinstance(data["power_min"], (int, float))
    assert isinstance(data["power_max"], (int, float))
    assert isinstance(data["tile_size"], (int, float))
    assert isinstance(data["gap"], (int, float))
    assert isinstance(data["labels"], bool)
    assert data["nc_power_profile"] in ["Makera (0-1)", "GRBL (0-1000)", "Custom"]
    assert isinstance(data["nc_s_max"], (int, float))

def test_app_info_includes_default_settings():
    """Test that app-info API includes default-settings as an available command."""
    result = subprocess.run([
        sys.executable,
        str(Path("makera_material_test_generator.py")),
        "--api", "app-info"
    ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)

    assert result.returncode == 0

    data = json.loads(result.stdout)
    assert "default-settings" in data["available_api_commands"]
