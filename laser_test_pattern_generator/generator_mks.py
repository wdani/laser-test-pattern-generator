from __future__ import annotations

import copy
import json
import math
import struct
import uuid
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .font import text_segments
from .geometry import Point, apply_auto_position, linspace, make_uuid
from .paths import default_template_dir, resolve_output_path
from .settings import GeneratorSettings, LASER_MODES


def read_zip_entry(path: Path, name: str) -> bytes:
    with zipfile.ZipFile(path) as z:
        return z.read(name)

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
        "format": "MKS",
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

