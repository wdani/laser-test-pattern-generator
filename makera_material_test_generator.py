#!/usr/bin/env python3
"""
Makera Material Test Generator v1.3

Creates Makera Studio .mks project files with a generated material-test grid:
- real SvgShape geometry in makera.bin
- one Laser Vector path per tile
- optional labels generated as real geometry
- no manual creation inside Makera Studio needed

Reverse-engineered from user-provided Makera Studio project files.
Tested conceptually with Makera Studio after Recalculate.

Important:
This is experimental. Always open the generated .mks in Makera Studio,
click Recalculate, inspect Preview, and only then export/laser.
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import os
import re
import struct
import sys
import uuid
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
except Exception:
    tk = None
    ttk = None
    filedialog = None
    messagebox = None

Point = Tuple[float, float]
Segment = Tuple[Point, Point]


LASER_MODES = {
    "Line": 0,
    "Fill": 1,
    "Offset Fill": 2,
}

APP_VERSION = "v1.3"

NC_POWER_PROFILES: Dict[str, Optional[float]] = {
    "Makera (0-1)": 1.0,
    "GRBL (0-1000)": 1000.0,
    "8-bit (0-255)": 255.0,
    "Custom": None,
}
DEFAULT_NC_POWER_PROFILE = "Makera (0-1)"


# Simple single-stroke font. Labels are generated from thin rectangle "bar" geometry.
# This avoids relying on Makera Studio SVG text import.
FONT: Dict[str, List[List[Point]]] = {
    "0": [[(0,0),(5,0),(5,7),(0,7),(0,0)]],
    "1": [[(2.5,0),(2.5,7)],[(1.2,7),(3.8,7)]],
    "2": [[(0,1),(1,0),(4,0),(5,1),(5,3),(0,7),(5,7)]],
    "3": [[(0,0),(5,0),(3,3.5),(5,7),(0,7)],[(2,3.5),(5,3.5)]],
    "4": [[(5,0),(5,7)],[(0,0),(0,3.5),(5,3.5)]],
    "5": [[(5,0),(0,0),(0,3.5),(4,3.5),(5,4.5),(5,6),(4,7),(0,7)]],
    "6": [[(5,0),(1,0),(0,1),(0,6),(1,7),(4,7),(5,6),(5,4.5),(4,3.5),(0,3.5)]],
    "7": [[(0,0),(5,0),(2,7)]],
    "8": [[(1,0),(4,0),(5,1),(5,2.5),(4,3.5),(1,3.5),(0,2.5),(0,1),(1,0)],
          [(1,3.5),(4,3.5),(5,4.5),(5,6),(4,7),(1,7),(0,6),(0,4.5),(1,3.5)]],
    "9": [[(5,3.5),(1,3.5),(0,2.5),(0,1),(1,0),(4,0),(5,1),(5,6),(4,7),(0,7)]],
    "/": [[(5,0),(0,7)]],
    "%": [[(0,7),(5,0)],[(1,0),(2,0),(2,1),(1,1),(1,0)],[(3,6),(4,6),(4,7),(3,7),(3,6)]],
    "(": [[(4,0),(2,1),(1,3.5),(2,6),(4,7)]],
    ")": [[(1,0),(3,1),(4,3.5),(3,6),(1,7)]],
    "-": [[(0.5,3.5),(4.5,3.5)]],
    ".": [[(2.1,6.5),(2.9,6.5),(2.9,7.0),(2.1,7.0),(2.1,6.5)]],
    " ": [],
    "A": [[(0,7),(2.5,0),(5,7)],[(1,4),(4,4)]],
    "B": [[(0,0),(0,7)],[(0,0),(4,0),(5,1),(5,2.5),(4,3.5),(0,3.5)],[(0,3.5),(4,3.5),(5,4.5),(5,6),(4,7),(0,7)]],
    "C": [[(5,1),(4,0),(1,0),(0,1),(0,6),(1,7),(4,7),(5,6)]],
    "D": [[(0,0),(0,7)],[(0,0),(3.5,0),(5,1.5),(5,5.5),(3.5,7),(0,7)]],
    "E": [[(5,0),(0,0),(0,7),(5,7)],[(0,3.5),(4,3.5)]],
    "F": [[(0,0),(0,7)],[(0,0),(5,0)],[(0,3.5),(4,3.5)]],
    "G": [[(5,1),(4,0),(1,0),(0,1),(0,6),(1,7),(4,7),(5,6),(5,4),(3,4)]],
    "H": [[(0,0),(0,7)],[(5,0),(5,7)],[(0,3.5),(5,3.5)]],
    "I": [[(0,0),(5,0)],[(2.5,0),(2.5,7)],[(0,7),(5,7)]],
    "K": [[(0,0),(0,7)],[(5,0),(0,3.5),(5,7)]],
    "L": [[(0,0),(0,7),(5,7)]],
    "M": [[(0,7),(0,0),(2.5,3.5),(5,0),(5,7)]],
    "N": [[(0,7),(0,0),(5,7),(5,0)]],
    "O": [[(0,0),(5,0),(5,7),(0,7),(0,0)]],
    "P": [[(0,7),(0,0),(4,0),(5,1),(5,2.5),(4,3.5),(0,3.5)]],
    "R": [[(0,7),(0,0),(4,0),(5,1),(5,2.5),(4,3.5),(0,3.5)],[(2.5,3.5),(5,7)]],
    "S": [[(5,1),(4,0),(1,0),(0,1),(0,3),(1,3.5),(4,3.5),(5,4),(5,6),(4,7),(1,7),(0,6)]],
    "T": [[(0,0),(5,0)],[(2.5,0),(2.5,7)]],
    "U": [[(0,0),(0,6),(1,7),(4,7),(5,6),(5,0)]],
    "W": [[(0,0),(0.8,7),(2.5,4),(4.2,7),(5,0)]],
    "Y": [[(0,0),(2.5,3.5),(5,0)],[(2.5,3.5),(2.5,7)]],
}


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
    nc_power_profile: str = DEFAULT_NC_POWER_PROFILE
    nc_s_max: float = 1.0
    nc_units: str = "mm"
    nc_include_labels: bool = True


def package_dir() -> Path:
    return Path(__file__).resolve().parent


def default_template_dir() -> Path:
    return package_dir() / "templates"


def read_zip_entry(path: Path, name: str) -> bytes:
    with zipfile.ZipFile(path) as z:
        return z.read(name)


def make_uuid() -> str:
    return str(uuid.uuid4())


def linspace(a: float, b: float, n: int) -> List[float]:
    if n <= 0:
        raise ValueError("count must be > 0")
    if n == 1:
        return [float(a)]
    return [float(a) + (float(b) - float(a)) * i / (n - 1) for i in range(n)]


def find_single_shape_sections(base_bin: bytes) -> Tuple[bytes, bytearray, bytes, bytearray]:
    """Split a one-rectangle makera.bin into prefix, SvgShape block, material block, footer.

    This is based on observed Makera Studio binary structure.
    """
    shape_start = base_bin.find((8).to_bytes(4, "little") + b"SvgShape")
    if shape_start < 0:
        raise RuntimeError("Could not find SvgShape record in base makera.bin")

    mesh_mat_pos = base_bin.find(b"MeshBasicMaterial", shape_start)
    if mesh_mat_pos < 0:
        raise RuntimeError("Could not find MeshBasicMaterial after SvgShape")

    material_start = mesh_mat_pos - 3
    group_start = base_bin.find((5).to_bytes(4, "little") + b"group", material_start)
    if group_start < 0:
        raise RuntimeError("Could not find group footer after material block")

    return (
        bytes(base_bin[:shape_start]),
        bytearray(base_bin[shape_start:material_start]),
        bytes(base_bin[material_start:group_start]),
        bytearray(base_bin[group_start:]),
    )


def patch_svg_file_child_count(bin_data: bytes, child_count: int) -> bytes:
    """Patch object count under the 'svg file' object.

    Without this, Makera Studio can crash because the number of child SvgShape blocks
    does not match the parent count.
    """
    b = bytearray(bin_data)
    svg_start = b.find((8).to_bytes(4, "little") + b"svg file")
    if svg_start < 0:
        raise RuntimeError("Could not find svg file object")
    struct.pack_into("<I", b, svg_start + 120, int(child_count))
    return bytes(b)


def raw_points_from_shape_block(block: bytes) -> List[Tuple[float, float, float]]:
    """Read the raw rectangle points from a SvgShape block."""
    pos = 52 + 64 + 30
    _flag = struct.unpack_from("<I", block, pos)[0]
    pos += 4
    vbytes = struct.unpack_from("<I", block, pos)[0]
    pos += 4
    vals = struct.unpack_from("<" + "f"*(vbytes//4), block, pos)
    return [vals[i:i+3] for i in range(0, len(vals), 3)]


def update_shape_block_rect(
    block: bytes,
    mesh_uuid: str,
    center_x: float,
    center_y: float,
    width: float,
    height: float,
    raw_cx: float,
    raw_cy: float,
    raw_w: float,
    raw_h: float,
    angle_deg: float = 0.0,
) -> bytes:
    """Duplicate a rectangle SvgShape and transform it to an arbitrary rotated rectangle."""
    b = bytearray(block)
    uuid_bytes = mesh_uuid.encode("ascii")
    if len(uuid_bytes) != 36:
        raise ValueError("mesh_uuid must be 36 ASCII characters")

    # UUID inside the SvgShape block.
    b[16:52] = uuid_bytes

    sx = float(width) / raw_w
    sy = float(height) / raw_h
    a = math.radians(angle_deg)
    ca = math.cos(a)
    sa = math.sin(a)

    # Observed Three.js-like column-major matrix:
    # x' = m0*x + m4*y + m12
    # y' = m1*x + m5*y + m13
    m0 = ca * sx
    m1 = sa * sx
    m4 = -sa * sy
    m5 = ca * sy
    tx = center_x - m0 * raw_cx - m4 * raw_cy
    ty = center_y - m1 * raw_cx - m5 * raw_cy

    matrix = [
        m0, m1, 0, 0,
        m4, m5, 0, 0,
        0,  0,  1, 0,
        tx, ty, 0, 1,
    ]
    struct.pack_into("<16f", b, 52, *matrix)
    return bytes(b)


def text_width_units(text: str) -> float:
    return sum(6 if ch != " " else 3 for ch in text.upper())


def text_segments(
    text: str,
    x: float,
    y: float,
    height: float = 3.0,
    angle_deg: float = 0.0,
    anchor: str = "start",
) -> List[Segment]:
    """Return line segments for the single-stroke font."""
    text = text.upper()
    scale = height / 7.0
    total_w = text_width_units(text) * scale
    if anchor == "middle":
        start_x = -total_w / 2
    elif anchor == "end":
        start_x = -total_w
    else:
        start_x = 0.0

    a = math.radians(angle_deg)
    ca = math.cos(a)
    sa = math.sin(a)

    def transform(px: float, py: float) -> Point:
        lx = start_x + px * scale

        # Makera's display coordinate system uses +Y upward.
        # The stroke font above is defined in screen/font coordinates where +Y goes downward.
        # Therefore py must be flipped here, otherwise all digits/letters appear mirrored.
        ly = -py * scale

        return (x + ca*lx - sa*ly, y + sa*lx + ca*ly)

    segs: List[Segment] = []
    cursor = 0.0
    for ch in text:
        if ch == " ":
            cursor += 3
            continue
        for poly in FONT.get(ch, []):
            pts = [transform(cursor + px, py) for px, py in poly]
            for a_pt, b_pt in zip(pts, pts[1:]):
                segs.append((a_pt, b_pt))
        cursor += 6
    return segs


def add_bar_for_segment(
    shapes: List[Tuple[str, bytes]],
    p1: Point,
    p2: Point,
    thickness: float,
    raw: Dict[str, object],
) -> Optional[str]:
    """Add a thin rotated rectangle for a stroke-font segment."""
    (x1, y1), (x2, y2) = p1, p2
    dx = x2 - x1
    dy = y2 - y1
    length = math.hypot(dx, dy)
    if length < 0.001:
        return None

    angle = math.degrees(math.atan2(dy, dx))
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    mesh_id = make_uuid()

    block = update_shape_block_rect(
        raw["shape_template"], mesh_id,
        cx, cy,
        length + thickness * 0.6, thickness,
        raw["cx"], raw["cy"], raw["w"], raw["h"],
        angle,
    )
    shapes.append((mesh_id, block))
    return mesh_id


def path_from_template(
    template: Dict,
    mesh_ids: List[str],
    speed: float,
    power: float,
    mode: int,
    line_interval: float = 0.1,
    passes: int = 1,
    bidirectional: bool = True,
    scan_angle: float = 0.0,
) -> Dict:
    """Create a Makera laser path from an observed template path."""
    p = copy.deepcopy(template)
    p["id"] = "{" + str(uuid.uuid4()) + "}"
    p["selectedmeshes"] = list(mesh_ids)
    p["nSelectObjCount"] = len(mesh_ids)
    p["gcodemeshuuidmap"] = {}
    p["speed"] = round(float(speed), 6)
    p["laserpower"] = round(float(power), 6)
    p["lasermode"] = int(mode)
    p["lineinterval"] = float(line_interval)
    p["linesperinch"] = round(25.4 / float(line_interval)) if line_interval else 254
    p["bidirecttional"] = bool(bidirectional)
    p["scanangle"] = float(scan_angle)
    p["passesnum"] = int(passes)
    p["indentdisatance"] = 0
    p["zoffset"] = 0
    p["dPathAngle"] = -1
    return p


def scheme_for_path(mesh_ids: List[str], speed: float, power: float, mode: int) -> Dict:
    return {
        "autoSelectObj": False,
        "laserMode": int(mode),
        "lstSelectMashID": list(mesh_ids),
        "lstTools": [],
        "nSelectObjCount": len(mesh_ids),
        "power": round(float(power), 6),
        "speed": round(float(speed), 6),
    }


def set_stock_size(prj: Dict, length: float, width: float, height: float) -> None:
    try:
        stock = prj["project"]["stStockInfo"]
        stock["length"] = float(length)
        stock["width"] = float(width)
        stock["height"] = float(height)
    except Exception:
        pass


def get_template_paths(template_dir: Path) -> Dict[str, Path]:
    return {
        "base": template_dir / "base_rectangle_10x10.mks",
        "line": template_dir / "template_line.mks",
        "fill": template_dir / "template_fill.mks",
        "offset": template_dir / "template_offset_fill.mks",
    }


def require_template_files(template_dir: Path) -> Dict[str, Path]:
    paths = get_template_paths(template_dir)
    missing = [str(p) for p in paths.values() if not p.exists()]
    if missing:
        raise FileNotFoundError("Missing template files:\n" + "\n".join(missing))
    return paths



def make_unique_output_path(path: Path) -> Path:
    """Return path if free; otherwise append _001, _002, ... before the suffix."""
    if not path.exists():
        return path

    parent = path.parent
    stem = path.stem
    suffix = path.suffix or ".mks"

    for i in range(1, 10000):
        candidate = parent / f"{stem}_{i:03d}{suffix}"
        if not candidate.exists():
            return candidate

    raise FileExistsError(f"Could not find a free filename for {path}")



def sanitize_filename_part(text: str) -> str:
    """Make a short safe filename part."""
    text = str(text).strip().lower()
    text = re.sub(r"[^a-z0-9._-]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "material"


def fmt_filename_number(value: float) -> str:
    """Format numbers for filenames without ugly decimals."""
    try:
        f = float(value)
        if f.is_integer():
            return str(int(f))
        return f"{f:g}".replace(".", "p")
    except Exception:
        return sanitize_filename_part(str(value))


def build_auto_filename(settings: GeneratorSettings, suffix: str) -> str:
    material = sanitize_filename_part(settings.material_name)
    mode = sanitize_filename_part(settings.tile_mode_name.replace(" ", "-"))
    parts = [
        material,
        f"{int(settings.rows)}x{int(settings.cols)}",
        f"s{fmt_filename_number(settings.speed_min)}-{fmt_filename_number(settings.speed_max)}",
        f"p{fmt_filename_number(settings.power_min)}-{fmt_filename_number(settings.power_max)}",
        mode,
    ]
    return "_".join(parts) + suffix


def resolve_output_path(path: Path, overwrite_existing: bool, suffix: Optional[str] = None, settings: Optional[GeneratorSettings] = None) -> Path:
    """Resolve output path, optionally auto-generating a filename and avoiding overwrite."""
    out = path

    if settings is not None and settings.auto_filename:
        base_dir = out if out.suffix == "" else out.parent
        out = base_dir / build_auto_filename(settings, suffix or ".mks")
    elif suffix:
        out = out.with_suffix(suffix)

    if not overwrite_existing:
        out = make_unique_output_path(out)

    out.parent.mkdir(parents=True, exist_ok=True)
    return out


def apply_auto_position(settings: GeneratorSettings, grid_w: float, grid_h: float) -> None:
    """Auto-place the grid inside stock while leaving room for labels."""
    if not settings.auto_position:
        return

    if settings.labels_enabled:
        left = 18.0
        right = 3.0
        bottom = 8.0
        top = 14.0
    else:
        left = 5.0
        right = 5.0
        bottom = 5.0
        top = 5.0

    total_w = left + grid_w + right
    total_h = bottom + grid_h + top

    settings.grid_x = left + max(0.0, (settings.stock_x - total_w) / 2.0)
    settings.grid_y = bottom + max(0.0, (settings.stock_y - total_h) / 2.0)

def power_to_s_value(power_percent: float, s_max: float) -> float:
    """Convert percent power to generic G-code S value."""
    return max(0.0, min(float(s_max), float(power_percent) / 100.0 * float(s_max)))


def resolve_nc_s_max(profile: str, custom_s_max: float) -> float:
    """Return the NC S max for a named profile, or the custom value."""
    profile_s_max = NC_POWER_PROFILES.get(profile)
    if profile_s_max is not None:
        return float(profile_s_max)
    return float(custom_s_max)


def profile_for_nc_s_max(s_max: float) -> str:
    """Infer the closest built-in profile for legacy presets that only store S max."""
    try:
        value = float(s_max)
    except Exception:
        return "Custom"

    for profile, profile_s_max in NC_POWER_PROFILES.items():
        if profile_s_max is not None and math.isclose(value, profile_s_max, rel_tol=0, abs_tol=1e-9):
            return profile
    return "Custom"


def fmt_num(value: float, digits: int = 4) -> str:
    """Compact numeric formatting for G-code."""
    text = f"{float(value):.{digits}f}".rstrip("0").rstrip(".")
    return text if text else "0"


def fmt_s_value(value: float, s_max: float) -> str:
    """Format S values, preserving Makera-style 0.0/1.0 endpoints."""
    if float(s_max) <= 1.0:
        text = fmt_num(value, 3)
        return text if "." in text else text + ".0"
    return fmt_num(value, 3)


def nc_header(settings: GeneratorSettings) -> List[str]:
    return [
        f"; Generated by Laser Test Pattern Generator {APP_VERSION}",
        "; Generic NC/G-code output. Verify your controller's laser S-value scale before use.",
        f"; NC power profile: {settings.nc_power_profile}",
        f"; NC S max: {fmt_num(settings.nc_s_max, 3)}",
        f"; Power range: {fmt_num(settings.power_min, 3)}% - {fmt_num(settings.power_max, 3)}%",
        f"; Speed range: {fmt_num(settings.speed_min, 1)} - {fmt_num(settings.speed_max, 1)} mm/min",
        f"; Grid: {int(settings.rows)} x {int(settings.cols)}",
        f"; Tile size: {fmt_num(settings.tile_size, 3)} mm",
        f"; Gap: {fmt_num(settings.gap, 3)} mm",
        f"; Mode: {settings.tile_mode_name}",
        f"; Line interval: {fmt_num(settings.line_interval, 3)} mm",
        "G21 ; millimeters",
        "G90 ; absolute coordinates",
        "M5",
    ]


def nc_footer() -> List[str]:
    return [
        "M5",
        "G0 X0 Y0",
        "M2",
    ]


def nc_laser_line(lines: List[str], x1: float, y1: float, x2: float, y2: float, speed: float, power: float, s_max: float) -> None:
    s_value = power_to_s_value(power, s_max)
    lines.append(f"G0 X{fmt_num(x1)} Y{fmt_num(y1)}")
    lines.append(f"M3 S{fmt_s_value(s_value, s_max)}")
    lines.append(f"G1 X{fmt_num(x2)} Y{fmt_num(y2)} F{fmt_num(speed, 1)}")
    lines.append("M5")


def nc_rectangle_outline(lines: List[str], x: float, y: float, w: float, h: float, speed: float, power: float, s_max: float) -> None:
    s_value = power_to_s_value(power, s_max)
    pts = [(x, y), (x+w, y), (x+w, y+h), (x, y+h), (x, y)]
    lines.append(f"G0 X{fmt_num(pts[0][0])} Y{fmt_num(pts[0][1])}")
    lines.append(f"M3 S{fmt_s_value(s_value, s_max)}")
    for px, py in pts[1:]:
        lines.append(f"G1 X{fmt_num(px)} Y{fmt_num(py)} F{fmt_num(speed, 1)}")
    lines.append("M5")


def nc_rectangle_fill(lines: List[str], x: float, y: float, w: float, h: float, speed: float, power: float, s_max: float, interval: float) -> None:
    interval = max(0.01, float(interval))
    count = int(math.floor(h / interval)) + 1
    s_value = power_to_s_value(power, s_max)
    direction = 1
    for i in range(count):
        yy = min(y + i * interval, y + h)
        x_start, x_end = (x, x+w) if direction > 0 else (x+w, x)
        lines.append(f"G0 X{fmt_num(x_start)} Y{fmt_num(yy)}")
        lines.append(f"M3 S{fmt_s_value(s_value, s_max)}")
        lines.append(f"G1 X{fmt_num(x_end)} Y{fmt_num(yy)} F{fmt_num(speed, 1)}")
        lines.append("M5")
        direction *= -1


def nc_rectangle_offset_fill(lines: List[str], x: float, y: float, w: float, h: float, speed: float, power: float, s_max: float, interval: float) -> None:
    interval = max(0.01, float(interval))
    inset = 0.0
    while w - 2*inset > 0.01 and h - 2*inset > 0.01:
        nc_rectangle_outline(lines, x+inset, y+inset, w-2*inset, h-2*inset, speed, power, s_max)
        inset += interval



def computed_layout(settings: GeneratorSettings) -> Dict[str, float]:
    """Return grid dimensions and approximate labeled layout bounds."""
    rows = int(settings.rows)
    cols = int(settings.cols)
    grid_w = cols * settings.tile_size + (cols - 1) * settings.gap
    grid_h = rows * settings.tile_size + (rows - 1) * settings.gap

    # Work on a shallow copy-like object by mutating only after caller accepts.
    apply_auto_position(settings, grid_w, grid_h)

    label_left = 18.0 if settings.labels_enabled else 0.0
    label_top = 14.0 if settings.labels_enabled else 0.0
    label_right = 2.0
    label_bottom = 0.0

    return {
        "rows": rows,
        "cols": cols,
        "grid_w": grid_w,
        "grid_h": grid_h,
        "grid_x": settings.grid_x,
        "grid_y": settings.grid_y,
        "layout_min_x": settings.grid_x - label_left,
        "layout_max_x": settings.grid_x + grid_w + label_right,
        "layout_min_y": settings.grid_y - label_bottom,
        "layout_max_y": settings.grid_y + grid_h + label_top,
        "stock_x": settings.stock_x,
        "stock_y": settings.stock_y,
    }


def validate_layout(settings: GeneratorSettings) -> List[str]:
    """Return human-readable layout warnings."""
    import copy as _copy
    tmp = _copy.deepcopy(settings)
    layout = computed_layout(tmp)
    warnings: List[str] = []

    if layout["layout_min_x"] < 0 or layout["layout_max_x"] > settings.stock_x or layout["layout_min_y"] < 0 or layout["layout_max_y"] > settings.stock_y:
        warnings.append(
            f"Layout may exceed stock: approx X {layout['layout_min_x']:.1f}..{layout['layout_max_x']:.1f}, "
            f"Y {layout['layout_min_y']:.1f}..{layout['layout_max_y']:.1f}; stock is {settings.stock_x:g}x{settings.stock_y:g}."
        )

    if settings.tile_size <= 0:
        warnings.append("Tile size must be greater than 0.")
    if settings.gap < 0:
        warnings.append("Gap should not be negative.")
    if settings.line_interval <= 0:
        warnings.append("Line interval must be greater than 0.")
    if settings.power_max > 100:
        warnings.append("Power max is above 100%; this may not be valid for all controllers.")
    if settings.rows * settings.cols > 100:
        warnings.append("Large grids can create very large MKS/NC files and slow recalculation.")

    return warnings


def generate_generic_nc(settings: GeneratorSettings) -> Dict[str, object]:
    """Generate a generic NC/G-code material test file.

    This is controller-neutral and uses S in range 0..nc_s_max.
    Many laser controllers use different S scales, so users must verify.
    """
    settings.nc_s_max = resolve_nc_s_max(settings.nc_power_profile, settings.nc_s_max)
    rows = int(settings.rows)
    cols = int(settings.cols)

    speeds_raw = linspace(settings.speed_min, settings.speed_max, rows)
    powers_raw = linspace(settings.power_min, settings.power_max, cols)

    speeds = [int(round(v)) for v in speeds_raw] if settings.round_speed_values else [round(v, 6) for v in speeds_raw]
    powers = [int(round(v)) for v in powers_raw] if settings.round_power_values else [round(v, 6) for v in powers_raw]

    if settings.language == "Deutsch":
        power_label = "LEISTUNG (%)"
        speed_label = "GESCHWINDIGKEIT (MM/MIN)"
    else:
        power_label = "POWER (%)"
        speed_label = "SPEED (MM/MIN)"

    tile_mode = LASER_MODES[settings.tile_mode_name]
    grid_w = cols * settings.tile_size + (cols - 1) * settings.gap
    grid_h = rows * settings.tile_size + (rows - 1) * settings.gap
    apply_auto_position(settings, grid_w, grid_h)

    lines = nc_header(settings)

    # Optional labels: simple stroke lines, not filled bars.
    if settings.labels_enabled and settings.nc_include_labels:
        gx = settings.grid_x
        gy = settings.grid_y

        def add_text_nc(label: str, x: float, y: float, h: float, angle: float = 0.0, anchor: str = "start") -> None:
            for p1, p2 in text_segments(label, x, y, height=h, angle_deg=angle, anchor=anchor):
                nc_laser_line(lines, p1[0], p1[1], p2[0], p2[1], settings.label_speed, settings.label_power, settings.nc_s_max)

        add_text_nc(power_label, gx + grid_w/2, gy + grid_h + 9.5, settings.power_axis_text_height, anchor="middle")
        add_text_nc(speed_label, max(2.5, gx - 16.5), gy + grid_h/2, settings.speed_axis_text_height, angle=-90, anchor="middle")

        for c, power in enumerate(powers):
            cx = gx + c*(settings.tile_size + settings.gap) + settings.tile_size/2
            label = str(int(power)) if isinstance(power, int) or float(power).is_integer() else f"{power:g}"
            add_text_nc(label, cx, gy + grid_h + 3.4, settings.power_number_text_height, anchor="middle")

        for r, speed in enumerate(speeds):
            cy = gy + r*(settings.tile_size + settings.gap) + settings.tile_size/2 - 1.0
            label = str(int(speed)) if isinstance(speed, int) or float(speed).is_integer() else f"{speed:g}"
            add_text_nc(label, gx - 5.0, cy + settings.speed_number_text_height / 2, settings.speed_number_text_height, anchor="end")

    # Tiles
    for r, speed in enumerate(speeds):
        for c, power in enumerate(powers):
            x = settings.grid_x + c*(settings.tile_size + settings.gap)
            y = settings.grid_y + r*(settings.tile_size + settings.gap)
            lines.append(f"; Tile row={r+1} col={c+1} speed={speed} power={power}")
            if tile_mode == 0:
                nc_rectangle_outline(lines, x, y, settings.tile_size, settings.tile_size, speed, power, settings.nc_s_max)
            elif tile_mode == 1:
                nc_rectangle_fill(lines, x, y, settings.tile_size, settings.tile_size, speed, power, settings.nc_s_max, settings.line_interval)
            else:
                nc_rectangle_offset_fill(lines, x, y, settings.tile_size, settings.tile_size, speed, power, settings.nc_s_max, settings.line_interval)

    lines.extend(nc_footer())

    out = resolve_output_path(settings.output_path, settings.overwrite_existing, suffix=".nc", settings=settings)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return {
        "output": str(out),
        "format": "NC",
        "lines": len(lines),
        "tiles": rows * cols,
        "speeds_visual_top_to_bottom": list(reversed(speeds)),
        "powers_left_to_right": powers,
        "power_profile": settings.nc_power_profile,
        "s_max": settings.nc_s_max,
    }

def generate_mks(settings: GeneratorSettings) -> Dict[str, object]:
    """Generate a Makera Studio .mks material test project."""
    template_dir = settings.template_dir or default_template_dir()
    tpaths = require_template_files(template_dir)

    base_bin = read_zip_entry(tpaths["base"], "makera.bin")
    base_prj = json.loads(read_zip_entry(tpaths["base"], "makera.prj").decode("utf-8"))
    line_prj = json.loads(read_zip_entry(tpaths["line"], "makera.prj").decode("utf-8"))
    fill_prj = json.loads(read_zip_entry(tpaths["fill"], "makera.prj").decode("utf-8"))
    offset_prj = json.loads(read_zip_entry(tpaths["offset"], "makera.prj").decode("utf-8"))

    mode_templates = {
        0: line_prj["project"]["lstCoordinate"]["0"]["path"][0],
        1: fill_prj["project"]["lstCoordinate"]["0"]["path"][0],
        2: offset_prj["project"]["lstCoordinate"]["0"]["path"][0],
    }

    tile_mode = LASER_MODES[settings.tile_mode_name]
    label_mode = LASER_MODES[settings.label_mode_name]

    tile_template = mode_templates[tile_mode]
    label_template = mode_templates[label_mode]

    prefix, shape_template, material_block, group_block = find_single_shape_sections(base_bin)
    pts = raw_points_from_shape_block(shape_template)
    raw_xmin, raw_xmax = min(p[0] for p in pts), max(p[0] for p in pts)
    raw_ymin, raw_ymax = min(p[1] for p in pts), max(p[1] for p in pts)

    raw = {
        "shape_template": shape_template,
        "cx": (raw_xmin + raw_xmax) / 2,
        "cy": (raw_ymin + raw_ymax) / 2,
        "w": raw_xmax - raw_xmin,
        "h": raw_ymax - raw_ymin,
    }

    rows = int(settings.rows)
    cols = int(settings.cols)
    speeds_raw = linspace(settings.speed_min, settings.speed_max, rows)
    powers_raw = linspace(settings.power_min, settings.power_max, cols)

    if settings.round_speed_values:
        speeds = [int(round(v)) for v in speeds_raw]
    else:
        speeds = [round(v, 6) for v in speeds_raw]

    if settings.round_power_values:
        powers = [int(round(v)) for v in powers_raw]
    else:
        powers = [round(v, 6) for v in powers_raw]

    # Resolve UI language labels. Custom dataclass labels still win if set manually.
    if settings.language == "Deutsch":
        settings.axis_power_label = "LEISTUNG (%)"
        settings.axis_speed_label = "GESCHWINDIGKEIT (MM/MIN)"
    else:
        settings.axis_power_label = "POWER (%)"
        settings.axis_speed_label = "SPEED (MM/MIN)"

    grid_w = cols * settings.tile_size + (cols - 1) * settings.gap
    grid_h = rows * settings.tile_size + (rows - 1) * settings.gap
    apply_auto_position(settings, grid_w, grid_h)

    shapes: List[Tuple[str, bytes]] = []
    label_mesh_ids: List[str] = []

    def add_text(label: str, x: float, y: float, h: float, angle: float = 0.0, anchor: str = "start") -> None:
        if not label:
            return
        for p1, p2 in text_segments(label, x, y, height=h, angle_deg=angle, anchor=anchor):
            mesh_id = add_bar_for_segment(shapes, p1, p2, settings.label_thickness, raw)
            if mesh_id:
                label_mesh_ids.append(mesh_id)

    # Labels are positioned for Makera's coordinate display: X to the right, Y upwards.
    if settings.labels_enabled:
        gx = settings.grid_x
        gy = settings.grid_y

        # Makera display uses +Y upwards. grid_y is the bottom of the raster.
        # Therefore labels above the raster must use grid_y + grid_h + ...
        # Compact label layout intended to fit 8x8 on 100x100 stock.
        add_text(settings.axis_power_label, gx + grid_w/2, gy + grid_h + 9.5,
                 h=settings.power_axis_text_height, anchor="middle")
        add_text(settings.axis_speed_label, max(2.5, gx - 16.5), gy + grid_h/2,
                 h=settings.speed_axis_text_height, angle=-90, anchor="middle")

        for c, power in enumerate(powers):
            cx = gx + c*(settings.tile_size + settings.gap) + settings.tile_size/2
            label = str(int(power)) if isinstance(power, int) or float(power).is_integer() else f"{power:g}"
            add_text(label, cx, gy + grid_h + 3.4,
                     h=settings.power_number_text_height, anchor="middle")

        # Bottom row = speed_min, top row = speed_max.
        for r, speed in enumerate(speeds):
            cy = gy + r*(settings.tile_size + settings.gap) + settings.tile_size/2 - 1.0
            label = str(int(speed)) if isinstance(speed, int) or float(speed).is_integer() else f"{speed:g}"
            add_text(label, gx - 5.0, cy + settings.speed_number_text_height / 2,
                     h=settings.speed_number_text_height, anchor="end")

    # Tile rectangles. Visually top row is max speed; bottom row min speed,
    # matching common material-test layout and the user's Makera preview.
    tile_mesh_ids_2d: List[List[str]] = []
    for r in range(rows):
        row: List[str] = []
        for c in range(cols):
            mesh_id = make_uuid()
            row.append(mesh_id)
            cx = settings.grid_x + c*(settings.tile_size + settings.gap) + settings.tile_size/2
            cy = settings.grid_y + r*(settings.tile_size + settings.gap) + settings.tile_size/2
            block = update_shape_block_rect(
                shape_template, mesh_id,
                cx, cy,
                settings.tile_size, settings.tile_size,
                raw["cx"], raw["cy"], raw["w"], raw["h"],
                0,
            )
            shapes.append((mesh_id, block))
        tile_mesh_ids_2d.append(row)

    # Build new makera.bin with all geometry.
    blocks: List[bytes] = [prefix]
    for _mesh_id, block in shapes:
        blocks.append(block)
        blocks.append(material_block)
    blocks.append(bytes(group_block))
    new_bin = patch_svg_file_child_count(b"".join(blocks), len(shapes))

    # Build project json.
    prj = copy.deepcopy(base_prj)
    proj = prj["project"]
    proj["strProjectName"] = "Makera Material Test Generated"
    proj["nSchemePageIndex"] = 2
    proj["bCurSchemeWidget"] = False
    proj["nGraphihcessMaxNum"] = len(shapes)
    set_stock_size(prj, settings.stock_x, settings.stock_y, settings.stock_z)

    coord = proj["lstCoordinate"]["0"]
    coord["graphicsshow"] = True
    coord["pathsshow"] = False

    paths: List[Dict] = []
    schemes: List[Dict] = []

    # Path 0: labels, if enabled and geometry exists.
    if settings.labels_enabled and label_mesh_ids:
        paths.append(path_from_template(
            label_template, label_mesh_ids,
            settings.label_speed, settings.label_power, label_mode,
            line_interval=0.1, passes=1, bidirectional=True, scan_angle=0,
        ))
        schemes.append(scheme_for_path(label_mesh_ids, settings.label_speed, settings.label_power, label_mode))

    # Tile paths.
    # Coordinate system: bottom row = speed_min, top row = speed_max.
    for r, speed in enumerate(speeds):
        for c, power in enumerate(powers):
            mesh_id = tile_mesh_ids_2d[r][c]
            paths.append(path_from_template(
                tile_template, [mesh_id],
                speed, power, tile_mode,
                line_interval=settings.line_interval,
                passes=settings.passes,
                bidirectional=settings.bidirectional,
                scan_angle=settings.scan_angle,
            ))
            schemes.append(scheme_for_path([mesh_id], speed, power, tile_mode))

    coord["path"] = paths
    proj["SchemeInfo"]["SchemeInfo2DLaser"]["lstLaserVectorScheme"] = schemes
    proj["SchemeInfo"]["SchemeInfo2DLaser"]["lstLaserImageScheme"] = []

    try:
        prj_img = read_zip_entry(tpaths["base"], "prjImg.png")
    except Exception:
        prj_img = b""

    output_path = resolve_output_path(settings.output_path, settings.overwrite_existing, suffix=".mks", settings=settings)
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("makera", b"")
        z.writestr("makera.bin", new_bin)
        z.writestr("makera.prj", json.dumps(prj, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
        z.writestr("prjImg.png", prj_img)

    warnings = []
    approx_min_x = settings.grid_x - (18.0 if settings.labels_enabled else 0.0)
    approx_max_x = settings.grid_x + grid_w + 2.0
    approx_min_y = settings.grid_y
    approx_max_y = settings.grid_y + grid_h + (14.0 if settings.labels_enabled else 0.0)
    if approx_min_x < 0 or approx_max_x > settings.stock_x or approx_min_y < 0 or approx_max_y > settings.stock_y:
        warnings.append(
            f"Layout may exceed stock: approx X {approx_min_x:.1f}..{approx_max_x:.1f}, "
            f"Y {approx_min_y:.1f}..{approx_max_y:.1f} within stock {settings.stock_x:g}x{settings.stock_y:g}."
        )

    return {
        "output": str(output_path),
        "paths": len(paths),
        "shapes": len(shapes),
        "label_shapes": len(label_mesh_ids),
        "tile_shapes": rows * cols,
        "speeds_visual_top_to_bottom": list(reversed(speeds)),
        "powers_left_to_right": powers,
        "grid_width": grid_w,
        "grid_height": grid_h,
        "warnings": warnings,
    }


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



class GeneratorGui:
    def __init__(self) -> None:
        if tk is None:
            raise RuntimeError("Tkinter is not available")

        self.root = tk.Tk()
        self.root.title(f"Makera Material Test Generator {APP_VERSION}")
        self.root.geometry("900x720")
        self.vars: Dict[str, tk.Variable] = {}
        self.preset_names_var = tk.StringVar(value="")
        self._build()
        self._refresh_presets()

    def _var(self, name: str, default, cls=tk.StringVar):
        v = cls(value=default)
        self.vars[name] = v
        return v

    def _entry(self, parent, label: str, varname: str, default, row: int, col: int = 0, width: int = 12):
        ttk.Label(parent, text=label).grid(row=row, column=col, sticky="w", padx=6, pady=4)
        ent = ttk.Entry(parent, textvariable=self._var(varname, default), width=width)
        ent.grid(row=row, column=col+1, sticky="w", padx=6, pady=4)
        return ent

    def _build(self):
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill="both", expand=True)

        output = ttk.LabelFrame(main, text="Output")
        output.pack(fill="x", pady=(0, 8))

        self._var("output", str(Path.cwd() / "makera_material_test_generated.mks"))
        ttk.Entry(output, textvariable=self.vars["output"], width=78).grid(row=0, column=0, columnspan=5, padx=6, pady=6, sticky="we")
        ttk.Button(output, text="Browse", command=self._browse_output).grid(row=0, column=5, padx=6, pady=6)

        self.vars["output_format"] = tk.StringVar(value="MKS")
        ttk.Label(output, text="Format").grid(row=1, column=0, sticky="w", padx=6, pady=3)
        ttk.Combobox(output, textvariable=self.vars["output_format"], values=["MKS", "NC", "Both"], state="readonly", width=10).grid(row=1, column=1, sticky="w", padx=6, pady=3)

        self.vars["overwrite_existing"] = tk.BooleanVar(value=False)
        ttk.Checkbutton(output, text="Overwrite existing file", variable=self.vars["overwrite_existing"]).grid(row=1, column=2, sticky="w", padx=6, pady=3)

        self.vars["auto_filename"] = tk.BooleanVar(value=True)
        ttk.Checkbutton(output, text="Auto filename", variable=self.vars["auto_filename"]).grid(row=1, column=3, sticky="w", padx=6, pady=3)
        ttk.Label(output, text="Material").grid(row=1, column=4, sticky="e", padx=6, pady=3)
        ttk.Entry(output, textvariable=self._var("material_name", "material"), width=16).grid(row=1, column=5, sticky="w", padx=6, pady=3)
        output.columnconfigure(0, weight=1)

        tabs = ttk.Notebook(main)
        tabs.pack(fill="both", expand=True)

        self.tab_grid = ttk.Frame(tabs, padding=10)
        self.tab_params = ttk.Frame(tabs, padding=10)
        self.tab_laser = ttk.Frame(tabs, padding=10)
        self.tab_labels = ttk.Frame(tabs, padding=10)
        self.tab_preview = ttk.Frame(tabs, padding=10)
        self.tab_presets = ttk.Frame(tabs, padding=10)

        tabs.add(self.tab_grid, text="Grid / Stock")
        tabs.add(self.tab_params, text="Parameters")
        tabs.add(self.tab_laser, text="Laser / NC")
        tabs.add(self.tab_labels, text="Labels")
        tabs.add(self.tab_preview, text="Preview")
        tabs.add(self.tab_presets, text="Presets")

        self._build_grid_tab()
        self._build_params_tab()
        self._build_laser_tab()
        self._build_labels_tab()
        self._build_preview_tab()
        self._build_presets_tab()

        buttons = ttk.Frame(main)
        buttons.pack(fill="x", pady=8)
        ttk.Button(buttons, text="Generate", command=self._generate).pack(side="left", padx=6)
        ttk.Button(buttons, text="Close", command=self.root.destroy).pack(side="left", padx=6)

        self.status = tk.Text(main, height=9)
        self.status.pack(fill="both", expand=False)
        self._log("Ready. Generate files, then verify them in Makera Studio or your NC viewer/sender.")

    def _build_grid_tab(self):
        f = self.tab_grid
        self._entry(f, "Rows", "rows", "6", 0, 0)
        self._entry(f, "Columns", "cols", "6", 0, 2)
        self._entry(f, "Tile size (mm)", "tile_size", "8.0", 1, 0)
        self._entry(f, "Gap (mm)", "gap", "2.0", 1, 2)

        self.vars["auto_position"] = tk.BooleanVar(value=True)
        ttk.Checkbutton(f, text="Auto position inside stock", variable=self.vars["auto_position"]).grid(row=2, column=0, columnspan=2, sticky="w", padx=6, pady=4)
        self._entry(f, "Grid X manual", "grid_x", "18.0", 3, 0)
        self._entry(f, "Grid Y manual", "grid_y", "8.0", 3, 2)

        sep = ttk.Separator(f, orient="horizontal")
        sep.grid(row=4, column=0, columnspan=4, sticky="we", pady=12)

        self._entry(f, "Stock X (mm)", "stock_x", "100", 5, 0)
        self._entry(f, "Stock Y (mm)", "stock_y", "100", 5, 2)
        self._entry(f, "Stock Z (mm)", "stock_z", "20", 6, 0)

        note = ttk.Label(f, text="Auto position keeps room for labels and centers the whole test layout inside the stock.", foreground="#555")
        note.grid(row=7, column=0, columnspan=4, sticky="w", padx=6, pady=10)

    def _build_params_tab(self):
        f = self.tab_params
        self._entry(f, "Speed min (mm/min)", "speed_min", "2200", 0, 0)
        self._entry(f, "Speed max (mm/min)", "speed_max", "2800", 0, 2)
        self._entry(f, "Power min (%)", "power_min", "20", 1, 0)
        self._entry(f, "Power max (%)", "power_max", "40", 1, 2)

        self.vars["round_speed_values"] = tk.BooleanVar(value=True)
        self.vars["round_power_values"] = tk.BooleanVar(value=True)
        ttk.Checkbutton(f, text="Round speed labels/values to integers", variable=self.vars["round_speed_values"]).grid(row=2, column=0, columnspan=2, sticky="w", padx=6, pady=4)
        ttk.Checkbutton(f, text="Round power labels/values to integers", variable=self.vars["round_power_values"]).grid(row=2, column=2, columnspan=2, sticky="w", padx=6, pady=4)

        note = ttk.Label(f, text="Tip: integer rounding avoids long labels like 1942.857.", foreground="#555")
        note.grid(row=3, column=0, columnspan=4, sticky="w", padx=6, pady=10)

    def _build_laser_tab(self):
        f = self.tab_laser
        ttk.Label(f, text="Tile mode").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.vars["mode"] = tk.StringVar(value="Offset Fill")
        ttk.Combobox(f, textvariable=self.vars["mode"], values=list(LASER_MODES), state="readonly", width=18).grid(row=0, column=1, sticky="w", padx=6, pady=4)

        self._entry(f, "Line interval (mm)", "line_interval", "0.10", 0, 2)
        self._entry(f, "Passes", "passes", "1", 1, 0)
        self._entry(f, "Scan angle", "scan_angle", "0", 1, 2)

        self.vars["bidirectional"] = tk.BooleanVar(value=True)
        ttk.Checkbutton(f, text="Bi-directional Fill", variable=self.vars["bidirectional"]).grid(row=2, column=0, columnspan=2, sticky="w", padx=6, pady=4)

        sep = ttk.Separator(f, orient="horizontal")
        sep.grid(row=3, column=0, columnspan=4, sticky="we", pady=12)

        ttk.Label(f, text="NC power profile").grid(row=4, column=0, sticky="w", padx=6, pady=4)
        self.vars["nc_power_profile"] = tk.StringVar(value=DEFAULT_NC_POWER_PROFILE)
        profile_combo = ttk.Combobox(f, textvariable=self.vars["nc_power_profile"], values=list(NC_POWER_PROFILES), state="readonly", width=18)
        profile_combo.grid(row=4, column=1, sticky="w", padx=6, pady=4)
        profile_combo.bind("<<ComboboxSelected>>", lambda _event: self._sync_nc_s_max_from_profile())

        self._entry(f, "NC S max", "nc_s_max", "1", 5, 0)
        note = ttk.Label(f, text="Generic NC only: Makera uses S0.0-S1.0; GRBL often uses S0-S1000; 8-bit uses S0-S255.", foreground="#555")
        note.grid(row=6, column=0, columnspan=4, sticky="w", padx=6, pady=10)

    def _build_labels_tab(self):
        f = self.tab_labels
        self.vars["labels_enabled"] = tk.BooleanVar(value=True)
        ttk.Checkbutton(f, text="Enable labels", variable=self.vars["labels_enabled"]).grid(row=0, column=0, columnspan=2, sticky="w", padx=6, pady=4)

        ttk.Label(f, text="Language").grid(row=0, column=2, sticky="w", padx=6, pady=4)
        self.vars["language"] = tk.StringVar(value="English")
        ttk.Combobox(f, textvariable=self.vars["language"], values=["English", "Deutsch"], state="readonly", width=12).grid(row=0, column=3, sticky="w", padx=6, pady=4)

        self._entry(f, "Label speed", "label_speed", "2500", 1, 0)
        self._entry(f, "Label power (%)", "label_power", "25", 1, 2)

        ttk.Label(f, text="Label mode").grid(row=2, column=0, sticky="w", padx=6, pady=4)
        self.vars["label_mode"] = tk.StringVar(value="Line")
        ttk.Combobox(f, textvariable=self.vars["label_mode"], values=list(LASER_MODES), state="readonly", width=18).grid(row=2, column=1, sticky="w", padx=6, pady=4)
        self._entry(f, "Label thickness", "label_thickness", "0.06", 2, 2)


    def _build_preview_tab(self):
        f = self.tab_preview

        top = ttk.Frame(f)
        top.pack(fill="x", pady=(0, 8))
        ttk.Button(top, text="Update Preview", command=self._update_preview).pack(side="left", padx=6)
        ttk.Label(top, text="Approximate 2D layout preview. The real laser paths are calculated by Makera Studio / your controller.", foreground="#555").pack(side="left", padx=12)

        body = ttk.Frame(f)
        body.pack(fill="both", expand=True)

        self.preview_canvas = tk.Canvas(body, width=560, height=460, bg="white", highlightthickness=1, highlightbackground="#aaa")
        self.preview_canvas.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.preview_text = tk.Text(body, width=36, height=22)
        self.preview_text.pack(side="right", fill="y")

    def _update_preview(self):
        try:
            import copy as _copy
            settings = self._settings()
            layout_settings = _copy.deepcopy(settings)
            layout = computed_layout(layout_settings)
            warnings = validate_layout(settings)

            c = self.preview_canvas
            c.delete("all")
            cw = int(c.winfo_width() or 560)
            ch = int(c.winfo_height() or 460)
            pad = 30

            sx = layout["stock_x"]
            sy = layout["stock_y"]
            scale = min((cw - 2 * pad) / max(sx, 1), (ch - 2 * pad) / max(sy, 1))

            def px(x):
                return pad + x * scale

            def py(y):
                # Display Y upwards
                return ch - pad - y * scale

            # Stock outline
            c.create_rectangle(px(0), py(sy), px(sx), py(0), outline="#222", width=2)
            c.create_text(px(sx/2), py(sy) - 12, text=f"Stock {sx:g} × {sy:g} mm", fill="#222")

            gx = layout["grid_x"]
            gy = layout["grid_y"]
            tile = settings.tile_size
            gap = settings.gap
            rows = int(settings.rows)
            cols = int(settings.cols)

            # Approx label zones
            if settings.labels_enabled:
                c.create_text(px(gx + layout["grid_w"]/2), py(gy + layout["grid_h"] + 9.5), text="POWER (%)", fill="#555")
                c.create_text(px(max(2.5, gx - 16.5)), py(gy + layout["grid_h"]/2), text="SPEED", fill="#555", angle=90)

            # Tiles
            for r in range(rows):
                for col in range(cols):
                    x = gx + col * (tile + gap)
                    y = gy + r * (tile + gap)
                    c.create_rectangle(px(x), py(y + tile), px(x + tile), py(y), outline="#1f77b4", width=1)

            # Overall approx layout bounds
            c.create_rectangle(px(layout["layout_min_x"]), py(layout["layout_max_y"]), px(layout["layout_max_x"]), py(layout["layout_min_y"]), outline="#cc7a00", dash=(4, 2))

            # Value summary
            speeds_raw = linspace(settings.speed_min, settings.speed_max, rows)
            powers_raw = linspace(settings.power_min, settings.power_max, cols)
            speeds = [int(round(v)) for v in speeds_raw] if settings.round_speed_values else [round(v, 6) for v in speeds_raw]
            powers = [int(round(v)) for v in powers_raw] if settings.round_power_values else [round(v, 6) for v in powers_raw]

            self.preview_text.delete("1.0", "end")
            self.preview_text.insert("end", "Layout summary\n")
            self.preview_text.insert("end", "--------------\n")
            self.preview_text.insert("end", f"Grid: {rows} × {cols}\n")
            self.preview_text.insert("end", f"Tiles: {rows * cols}\n")
            self.preview_text.insert("end", f"Grid size: {layout['grid_w']:.1f} × {layout['grid_h']:.1f} mm\n")
            self.preview_text.insert("end", f"Grid origin: X{layout['grid_x']:.1f} Y{layout['grid_y']:.1f}\n")
            self.preview_text.insert("end", f"Approx bounds: X{layout['layout_min_x']:.1f}..{layout['layout_max_x']:.1f}, Y{layout['layout_min_y']:.1f}..{layout['layout_max_y']:.1f}\n\n")
            self.preview_text.insert("end", "Speed top → bottom:\n")
            self.preview_text.insert("end", ", ".join(str(v) for v in reversed(speeds)) + "\n\n")
            self.preview_text.insert("end", "Power left → right:\n")
            self.preview_text.insert("end", ", ".join(str(v) for v in powers) + "\n\n")

            if warnings:
                self.preview_text.insert("end", "Warnings:\n")
                for w in warnings:
                    self.preview_text.insert("end", "- " + w + "\n")
            else:
                self.preview_text.insert("end", "No layout warnings.\n")

            self._log("Preview updated.")
        except Exception as e:
            self._log("ERROR: " + str(e))
            messagebox.showerror("Error", str(e))



    def _build_presets_tab(self):
        f = self.tab_presets

        ttk.Label(f, text="Preset").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.vars["preset_name"] = tk.StringVar(value="")
        self.preset_combo = ttk.Combobox(f, textvariable=self.vars["preset_name"], values=[], width=42)
        self.preset_combo.grid(row=0, column=1, columnspan=3, sticky="we", padx=6, pady=4)

        ttk.Button(f, text="Load selected", command=self._load_selected_preset).grid(row=1, column=0, padx=6, pady=6, sticky="w")
        ttk.Button(f, text="Save as selected/new", command=self._save_named_preset).grid(row=1, column=1, padx=6, pady=6, sticky="w")
        ttk.Button(f, text="Delete selected", command=self._delete_selected_preset).grid(row=1, column=2, padx=6, pady=6, sticky="w")
        ttk.Button(f, text="Refresh", command=self._refresh_presets).grid(row=1, column=3, padx=6, pady=6, sticky="w")

        sep = ttk.Separator(f, orient="horizontal")
        sep.grid(row=2, column=0, columnspan=4, sticky="we", pady=12)

        ttk.Button(f, text="Export preset to file", command=self._save_preset_file).grid(row=3, column=0, padx=6, pady=6, sticky="w")
        ttk.Button(f, text="Import preset from file", command=self._load_preset_file).grid(row=3, column=1, padx=6, pady=6, sticky="w")

        note = ttk.Label(f, text="Built-in/local presets are stored in the package's presets folder.", foreground="#555")
        note.grid(row=4, column=0, columnspan=4, sticky="w", padx=6, pady=10)
        f.columnconfigure(1, weight=1)

    def _browse_output(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".mks",
            filetypes=[("Makera Studio Project", "*.mks"), ("NC/G-code", "*.nc"), ("All files", "*.*")]
        )
        if path:
            self.vars["output"].set(path)

    def _log(self, text: str):
        self.status.insert("end", text + "\n")
        self.status.see("end")

    def _preset_dir(self) -> Path:
        d = package_dir() / "presets"
        d.mkdir(exist_ok=True)
        return d

    def _preset_path(self, name: str) -> Path:
        safe = sanitize_filename_part(name)
        return self._preset_dir() / f"{safe}.json"

    def _refresh_presets(self):
        names = []
        for path in sorted(self._preset_dir().glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                names.append(str(data.get("_preset_name") or path.stem))
            except Exception:
                names.append(path.stem)
        self.preset_combo["values"] = names
        if names and not self.vars.get("preset_name", tk.StringVar()).get():
            self.vars["preset_name"].set(names[0])

    def _collect_preset_data(self) -> Dict[str, object]:
        data: Dict[str, object] = {}
        for key, var in self.vars.items():
            if key == "preset_name":
                continue
            try:
                data[key] = var.get()
            except Exception:
                pass
        return data

    def _apply_preset_data(self, data: Dict[str, object]) -> None:
        for key, value in data.items():
            if key.startswith("_"):
                continue
            if key in self.vars:
                try:
                    self.vars[key].set(value)
                except Exception:
                    pass
        if "nc_power_profile" not in data and "nc_s_max" in data and "nc_power_profile" in self.vars:
            self.vars["nc_power_profile"].set(profile_for_nc_s_max(data["nc_s_max"]))
        self._sync_nc_s_max_from_profile()

    def _sync_nc_s_max_from_profile(self) -> None:
        if "nc_power_profile" not in self.vars or "nc_s_max" not in self.vars:
            return
        profile = self.vars["nc_power_profile"].get()
        profile_s_max = NC_POWER_PROFILES.get(profile)
        if profile_s_max is not None:
            self.vars["nc_s_max"].set(fmt_num(profile_s_max, 3))

    def _save_named_preset(self):
        name = self.vars["preset_name"].get().strip()
        if not name:
            messagebox.showwarning("Preset name missing", "Enter a preset name first.")
            return
        data = self._collect_preset_data()
        data["_preset_name"] = name
        path = self._preset_path(name)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        self._log("Preset saved: " + str(path))
        self._refresh_presets()

    def _load_selected_preset(self):
        name = self.vars["preset_name"].get().strip()
        if not name:
            return
        path = self._preset_path(name)
        if not path.exists():
            # fall back to exact existing filename stem lookup
            candidates = list(self._preset_dir().glob("*.json"))
            for candidate in candidates:
                try:
                    data = json.loads(candidate.read_text(encoding="utf-8"))
                    if str(data.get("_preset_name") or candidate.stem) == name:
                        path = candidate
                        break
                except Exception:
                    pass
        if not path.exists():
            messagebox.showerror("Error", "Preset not found.")
            return
        data = json.loads(path.read_text(encoding="utf-8"))
        self._apply_preset_data(data)
        self._log("Preset loaded: " + str(path))

    def _delete_selected_preset(self):
        name = self.vars["preset_name"].get().strip()
        if not name:
            return
        path = self._preset_path(name)
        if path.exists():
            path.unlink()
            self._log("Preset deleted: " + str(path))
        self.vars["preset_name"].set("")
        self._refresh_presets()

    def _save_preset_file(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Preset JSON", "*.json"), ("All files", "*.*")]
        )
        if not path:
            return
        data = self._collect_preset_data()
        data["_preset_name"] = Path(path).stem
        Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")
        self._log("Preset exported: " + path)

    def _load_preset_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("Preset JSON", "*.json"), ("All files", "*.*")]
        )
        if not path:
            return
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        self._apply_preset_data(data)
        self._log("Preset imported: " + path)

    def _settings(self) -> GeneratorSettings:
        def f(name): return float(self.vars[name].get())
        def i(name): return int(float(self.vars[name].get()))
        return GeneratorSettings(
            output_path=Path(self.vars["output"].get()),
            output_format=self.vars["output_format"].get(),
            overwrite_existing=bool(self.vars["overwrite_existing"].get()),
            auto_filename=bool(self.vars["auto_filename"].get()),
            material_name=self.vars["material_name"].get(),
            rows=i("rows"),
            cols=i("cols"),
            speed_min=f("speed_min"),
            speed_max=f("speed_max"),
            power_min=f("power_min"),
            power_max=f("power_max"),
            tile_size=f("tile_size"),
            gap=f("gap"),
            grid_x=f("grid_x"),
            grid_y=f("grid_y"),
            auto_position=bool(self.vars["auto_position"].get()),
            tile_mode_name=self.vars["mode"].get(),
            line_interval=f("line_interval"),
            passes=i("passes"),
            bidirectional=bool(self.vars["bidirectional"].get()),
            scan_angle=f("scan_angle"),
            labels_enabled=bool(self.vars["labels_enabled"].get()),
            language=self.vars["language"].get(),
            label_speed=f("label_speed"),
            label_power=f("label_power"),
            label_mode_name=self.vars["label_mode"].get(),
            label_thickness=f("label_thickness"),
            stock_x=f("stock_x"),
            stock_y=f("stock_y"),
            stock_z=f("stock_z"),
            round_speed_values=bool(self.vars["round_speed_values"].get()),
            round_power_values=bool(self.vars["round_power_values"].get()),
            nc_power_profile=self.vars["nc_power_profile"].get(),
            nc_s_max=f("nc_s_max"),
        )

    def _generate(self):
        try:
            settings = self._settings()
            pre_warnings = validate_layout(settings)
            for warning in pre_warnings:
                self._log("WARNING: " + warning)
            infos = []
            if settings.output_format in ("MKS", "Both"):
                infos.append(generate_mks(copy.deepcopy(settings)))
            if settings.output_format in ("NC", "Both"):
                infos.append(generate_generic_nc(copy.deepcopy(settings)))

            for info in infos:
                self._log("Created: " + info["output"])
                if info.get("format") == "NC":
                    self._log(f"NC lines: {info['lines']} | Tiles: {info['tiles']} | Profile: {info['power_profile']} | S max: {info['s_max']}")
                else:
                    self._log(f"Paths: {info['paths']} | Shapes: {info['shapes']} | Labels: {info['label_shapes']} | Tiles: {info['tile_shapes']}")
                self._log("Speed top→bottom: " + ", ".join(str(int(x) if isinstance(x, int) or float(x).is_integer() else x) for x in info["speeds_visual_top_to_bottom"]))
                self._log("Power left→right: " + ", ".join(str(int(x) if isinstance(x, int) or float(x).is_integer() else x) for x in info["powers_left_to_right"]))
                for warning in info.get("warnings", []):
                    self._log("WARNING: " + warning)

            messagebox.showinfo("Done", "File(s) created.\n\nFor MKS: open in Makera Studio → Recalculate → inspect Preview.\nFor NC: verify S-value scale and preview before use.")
        except Exception as e:
            self._log("ERROR: " + str(e))
            messagebox.showerror("Error", str(e))

    def run(self):
        self.root.mainloop()


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    if args.gui:
        gui = GeneratorGui()
        gui.run()
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


if __name__ == "__main__":
    raise SystemExit(main())
