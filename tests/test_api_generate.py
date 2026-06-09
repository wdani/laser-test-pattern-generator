import json
import subprocess
import sys
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
GUIDANCE_TEXT = "For MKS: open in Makera Studio"


def run_command(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(Path("makera_material_test_generator.py")), *args],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )


def run_api_generate(*args: str) -> tuple[dict, str]:
    result = run_command("--api", "generate", *args)

    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    text = result.stdout.strip()
    assert text.startswith("{")
    assert text.endswith("}")
    assert GUIDANCE_TEXT not in text
    return json.loads(text), text


def test_api_generate_returns_valid_json(tmp_path):
    output_path = tmp_path / "api_valid.nc"

    data, _stdout = run_api_generate(
        "--format",
        "NC",
        "--output",
        str(output_path),
        "--overwrite",
        "--rows",
        "1",
        "--cols",
        "1",
        "--no-labels",
    )

    assert data["schema_version"] == 1
    assert data["api_command"] == "generate"
    assert data["app_name"] == "Laser Test Pattern Generator"
    assert "app_version" in data
    assert "result" in data


def test_api_generate_nc_creates_output_file(tmp_path):
    output_path = tmp_path / "api_generate.nc"

    data, _stdout = run_api_generate(
        "--format",
        "NC",
        "--output",
        str(output_path),
        "--overwrite",
        "--rows",
        "1",
        "--cols",
        "1",
        "--no-labels",
    )

    assert output_path.exists()
    assert output_path.stat().st_size > 0
    assert data["result"]["format"] == "NC"
    assert data["result"]["output"] == str(output_path)
    assert data["result"]["tiles"] == 1


def test_api_generate_mks_creates_output_file(tmp_path):
    output_path = tmp_path / "api_generate.mks"

    data, _stdout = run_api_generate(
        "--format",
        "MKS",
        "--output",
        str(output_path),
        "--overwrite",
        "--rows",
        "1",
        "--cols",
        "1",
        "--no-labels",
    )

    assert output_path.exists()
    assert output_path.stat().st_size > 0
    assert zipfile.is_zipfile(output_path)
    assert data["result"]["output"] == str(output_path)
    assert data["result"]["tile_shapes"] == 1


def test_api_generate_both_creates_both_output_files(tmp_path):
    output_path = tmp_path / "api_generate_both.mks"

    data, _stdout = run_api_generate(
        "--format",
        "Both",
        "--output",
        str(output_path),
        "--overwrite",
        "--rows",
        "1",
        "--cols",
        "1",
        "--no-labels",
    )

    mks_path = tmp_path / "api_generate_both.mks"
    nc_path = tmp_path / "api_generate_both.nc"

    assert mks_path.exists()
    assert nc_path.exists()
    assert "results" in data
    assert len(data["results"]) == 2
    assert {entry["output"] for entry in data["results"]} == {str(mks_path), str(nc_path)}


def test_api_generate_output_is_json_only(tmp_path):
    output_path = tmp_path / "json_only.nc"

    _data, stdout = run_api_generate(
        "--format",
        "NC",
        "--output",
        str(output_path),
        "--overwrite",
        "--rows",
        "1",
        "--cols",
        "1",
        "--no-labels",
    )

    assert GUIDANCE_TEXT not in stdout
    assert "For NC: verify your laser controller" not in stdout
    json.loads(stdout)


def test_api_generate_respects_existing_overwrite_protection(tmp_path):
    output_path = tmp_path / "existing.nc"
    output_path.write_text("original", encoding="utf-8")

    data, _stdout = run_api_generate(
        "--format",
        "NC",
        "--output",
        str(output_path),
        "--rows",
        "1",
        "--cols",
        "1",
        "--no-labels",
    )

    generated_path = Path(data["result"]["output"])
    assert output_path.read_text(encoding="utf-8") == "original"
    assert generated_path != output_path
    assert generated_path.exists()


def test_normal_cli_generation_keeps_guidance_text(tmp_path):
    output_path = tmp_path / "normal_cli.nc"

    result = run_command(
        "--format",
        "NC",
        "--output",
        str(output_path),
        "--overwrite",
        "--rows",
        "1",
        "--cols",
        "1",
        "--no-labels",
    )

    assert result.returncode == 0, result.stderr
    assert output_path.exists()
    assert GUIDANCE_TEXT in result.stdout
    assert "For NC: verify your laser controller" in result.stdout
