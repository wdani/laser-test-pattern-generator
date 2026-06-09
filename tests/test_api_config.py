import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def run_command(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(Path("makera_material_test_generator.py")), *args],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )


def parse_json_stdout(result: subprocess.CompletedProcess[str]) -> dict:
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    return json.loads(result.stdout)


def cleanup_output(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def test_api_preview_config_returns_valid_json():
    result = run_command("--api", "preview", "--config", "examples/api/preview_basic.json")
    data = parse_json_stdout(result)

    assert data["api_command"] == "preview"
    assert data["output_format"] == "NC"
    assert data["rows"] == 2
    assert data["cols"] == 3
    assert data["labels_enabled"] is False


def test_api_generate_config_creates_expected_output_file():
    output_path = REPO_ROOT / "tmp" / "api_generate_nc_basic.nc"
    cleanup_output(output_path)

    try:
        result = run_command(
            "--api",
            "generate",
            "--config",
            "examples/api/generate_nc_basic.json",
            "--overwrite",
        )
        data = parse_json_stdout(result)

        assert data["api_command"] == "generate"
        assert data["result"]["format"] == "NC"
        assert Path(data["result"]["output"]).resolve() == output_path.resolve()
        assert output_path.exists()
        assert output_path.stat().st_size > 0
    finally:
        cleanup_output(output_path)


def test_api_config_cli_arguments_override_config_values():
    result = run_command(
        "--api",
        "preview",
        "--config",
        "examples/api/preview_basic.json",
        "--rows",
        "4",
        "--format",
        "MKS",
        "--labels",
    )
    data = parse_json_stdout(result)

    assert data["rows"] == 4
    assert data["output_format"] == "MKS"
    assert data["labels_enabled"] is True


def test_api_invalid_config_returns_useful_error(tmp_path):
    config_path = tmp_path / "invalid.json"
    config_path.write_text('{"rows": 2,', encoding="utf-8")

    result = run_command("--api", "preview", "--config", str(config_path))

    assert result.returncode != 0
    assert result.stdout == ""
    assert "API config error" in result.stderr
    assert "not valid JSON" in result.stderr


def test_api_unknown_config_key_returns_useful_error(tmp_path):
    config_path = tmp_path / "unknown_key.json"
    config_path.write_text(json.dumps({"unknown_setting": 123}), encoding="utf-8")

    result = run_command("--api", "preview", "--config", str(config_path))

    assert result.returncode != 0
    assert result.stdout == ""
    assert "API config error" in result.stderr
    assert "unsupported config key 'unknown_setting'" in result.stderr


def test_api_invalid_config_value_type_returns_useful_error(tmp_path):
    config_path = tmp_path / "bad_type.json"
    config_path.write_text(json.dumps({"rows": True}), encoding="utf-8")

    result = run_command("--api", "preview", "--config", str(config_path))

    assert result.returncode != 0
    assert result.stdout == ""
    assert "API config error" in result.stderr
    assert "expected a string, number, or null value" in result.stderr


def test_existing_cli_only_api_preview_still_works():
    result = run_command("--api", "preview", "--rows", "1", "--cols", "1")
    data = parse_json_stdout(result)

    assert data["api_command"] == "preview"
    assert data["rows"] == 1
    assert data["cols"] == 1
