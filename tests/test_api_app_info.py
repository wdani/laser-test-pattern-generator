import json
from contextlib import redirect_stdout
from io import StringIO

from laser_test_pattern_generator import app
from laser_test_pattern_generator.settings import APP_VERSION


def run_app_info() -> dict:
    output = StringIO()

    with redirect_stdout(output):
        exit_code = app.main(["--api", "app-info"])

    assert exit_code == 0
    return json.loads(output.getvalue())


def test_app_info_returns_expected_metadata():
    data = run_app_info()

    assert data["schema_version"] == 1
    assert data["app_name"] == "Laser Test Pattern Generator"
    assert data["app_version"] == APP_VERSION
    assert data["backend"] == "Python"


def test_app_info_helper_matches_main_response():
    assert run_app_info() == app.app_info_response()


def test_app_info_lists_supported_output_formats():
    data = run_app_info()

    assert "MKS" in data["supported_output_formats"]
    assert "NC" in data["supported_output_formats"]
    assert "Both" in data["supported_output_formats"]


def test_app_info_lists_available_and_planned_api_commands():
    data = run_app_info()

    assert "app-info" in data["available_api_commands"]

    assert "default-settings" in data["available_api_commands"]
    assert "preview" in data["available_api_commands"]
    assert "preview" not in data["planned_api_commands"]
    assert "generate" in data["planned_api_commands"]
