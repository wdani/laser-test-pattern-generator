from __future__ import annotations

import math
from typing import Dict, List, Sequence, Tuple

from .font import text_segments
from .generator_nc import fmt_num, fmt_s_value, power_to_s_value, resolve_nc_s_max
from .geometry import apply_auto_position, linspace
from .paths import resolve_output_path
from .settings import APP_VERSION, GeneratorSettings, LASER_MODES

Point = Tuple[float, float]


def rounded_axis_values(start: float, end: float, count: int, should_round: bool) -> list:
    values = linspace(start, end, count)
    if should_round:
        return [int(round(value)) for value in values]
    return [round(value, 6) for value in values]


def makera_header(settings: GeneratorSettings) -> List[str]:
    return [
        ";@MKR|BEGIN",
        ";@MKR|SCHEMA|v=1.0.0",
        ";@MKR|MACHINE|id=C1|name=Carvera",
        f";@MKR|MATERIAL|id=|name={settings.material_name}",
        (
            f";@MKR|STOCK|id=cuboid|length={fmt_num(settings.stock_x)}|"
            f"width={fmt_num(settings.stock_y)}|height={fmt_num(settings.stock_z)}|diameter=50"
        ),
        f";@MKR|CAM|id=laser-test-pattern-generator|name=Laser Test Pattern Generator|v={APP_VERSION}",
        ";@MKR|TIME|seconds=0",
        ";@MKR|END",
        "",
        "G90 G21",
    ]


def makera_footer() -> List[str]:
    return [
        "M05",
        "M322",
        "M05",
        "G28",
        "M02",
    ]


def add_toolpath_start(lines: List[str], number: int, include_start_sequence: bool = False) -> None:
    lines.append(f";@MKR|TOOLPATH_START|toolpath_number={number}")
    if include_start_sequence:
        lines.extend(["M321", "G0 Z0", "M3"])


def add_polyline(lines: List[str], points: Sequence[Point], speed: float, power: float, s_max: float) -> int:
    pts = list(points)
    if len(pts) < 2:
        return 0

    s_value = fmt_s_value(power_to_s_value(power, s_max), s_max)
    lines.append(f"G0 X{fmt_num(pts[0][0])} Y{fmt_num(pts[0][1])}")
    lines.append(f"G1 X{fmt_num(pts[1][0])} Y{fmt_num(pts[1][1])} S{s_value} F{fmt_num(speed, 1)}")
    for x, y in pts[2:]:
        lines.append(f"G1 X{fmt_num(x)} Y{fmt_num(y)}")
    lines.append("G1 S0")
    return 1


def effective_rect(x: float, y: float, w: float, h: float, indent: float) -> tuple[float, float, float, float]:
    indent = max(0.0, float(indent))
    ex = x + indent
    ey = y + indent
    ew = w - 2 * indent
    eh = h - 2 * indent
    if ew <= 0.01 or eh <= 0.01:
        raise ValueError("Indent distance is too large for the tile size.")
    return ex, ey, ew, eh


def rectangle_points(x: float, y: float, w: float, h: float) -> list[Point]:
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)]


def add_rectangle_outline(lines: List[str], x: float, y: float, w: float, h: float, speed: float, power: float, s_max: float) -> int:
    return add_polyline(lines, rectangle_points(x, y, w, h), speed, power, s_max)


def bar_points_for_segment(p1: Point, p2: Point, thickness: float) -> list[Point]:
    x1, y1 = p1
    x2, y2 = p2
    dx = x2 - x1
    dy = y2 - y1
    length = math.hypot(dx, dy)
    if length < 0.001:
        return []

    half = max(0.001, float(thickness) / 2.0)
    nx = -dy / length * half
    ny = dx / length * half
    return [
        (x1 + nx, y1 + ny),
        (x2 + nx, y2 + ny),
        (x2 - nx, y2 - ny),
        (x1 - nx, y1 - ny),
        (x1 + nx, y1 + ny),
    ]


def add_text_bars(
    lines: List[str],
    label: str,
    x: float,
    y: float,
    height: float,
    speed: float,
    power: float,
    s_max: float,
    thickness: float,
    angle: float = 0.0,
    anchor: str = "start",
) -> int:
    count = 0
    if not label:
        return count
    for p1, p2 in text_segments(label, x, y, height=height, angle_deg=angle, anchor=anchor):
        points = bar_points_for_segment(p1, p2, thickness)
        count += add_polyline(lines, points, speed, power, s_max)
    return count


def add_labels(lines: List[str], settings: GeneratorSettings, speeds: Sequence[float], powers: Sequence[float], grid_w: float, grid_h: float) -> int:
    if settings.language == "Deutsch":
        power_label = "LEISTUNG (%)"
        speed_label = "GESCHWINDIGKEIT (MM/MIN)"
    else:
        power_label = "POWER (%)"
        speed_label = "SPEED (MM/MIN)"

    gx = settings.grid_x
    gy = settings.grid_y
    count = 0
    count += add_text_bars(
        lines,
        power_label,
        gx + grid_w / 2,
        gy + grid_h + 9.5,
        settings.power_axis_text_height,
        settings.label_speed,
        settings.label_power,
        settings.nc_s_max,
        settings.label_thickness,
        anchor="middle",
    )
    count += add_text_bars(
        lines,
        speed_label,
        max(2.5, gx - 16.5),
        gy + grid_h / 2,
        settings.speed_axis_text_height,
        settings.label_speed,
        settings.label_power,
        settings.nc_s_max,
        settings.label_thickness,
        angle=-90,
        anchor="middle",
    )

    for c, power in enumerate(powers):
        cx = gx + c * (settings.tile_size + settings.gap) + settings.tile_size / 2
        label = str(int(power)) if isinstance(power, int) or float(power).is_integer() else f"{power:g}"
        count += add_text_bars(
            lines,
            label,
            cx,
            gy + grid_h + 3.4,
            settings.power_number_text_height,
            settings.label_speed,
            settings.label_power,
            settings.nc_s_max,
            settings.label_thickness,
            anchor="middle",
        )

    for r, speed in enumerate(speeds):
        cy = gy + r * (settings.tile_size + settings.gap) + settings.tile_size / 2 - 1.0
        label = str(int(speed)) if isinstance(speed, int) or float(speed).is_integer() else f"{speed:g}"
        count += add_text_bars(
            lines,
            label,
            gx - 5.0,
            cy + settings.speed_number_text_height / 2,
            settings.speed_number_text_height,
            settings.label_speed,
            settings.label_power,
            settings.nc_s_max,
            settings.label_thickness,
            anchor="end",
        )

    return count


def clip_scanline_to_rect(x: float, y: float, w: float, h: float, direction: Point, normal_value: float) -> list[Point]:
    dx, dy = direction
    nx, ny = -dy, dx
    corners = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    edges = list(zip(corners, corners[1:] + corners[:1]))
    points: list[Point] = []

    for (x1, y1), (x2, y2) in edges:
        v1 = nx * x1 + ny * y1 - normal_value
        v2 = nx * x2 + ny * y2 - normal_value
        if abs(v1) <= 1e-9 and (x1, y1) not in points:
            points.append((x1, y1))
        if v1 * v2 < -1e-9:
            t = v1 / (v1 - v2)
            px = x1 + (x2 - x1) * t
            py = y1 + (y2 - y1) * t
            candidate = (round(px, 10), round(py, 10))
            if candidate not in [(round(px0, 10), round(py0, 10)) for px0, py0 in points]:
                points.append((px, py))
        if abs(v2) <= 1e-9 and (x2, y2) not in points:
            points.append((x2, y2))

    if len(points) < 2:
        return []

    points.sort(key=lambda pt: dx * pt[0] + dy * pt[1])
    return [points[0], points[-1]]


def scanline_segments(x: float, y: float, w: float, h: float, interval: float, angle_deg: float, bidirectional: bool) -> list[tuple[Point, Point]]:
    interval = max(0.01, float(interval))
    angle = math.radians(float(angle_deg))
    direction = (math.cos(angle), math.sin(angle))
    normal = (-direction[1], direction[0])
    corners = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    projections = [normal[0] * cx + normal[1] * cy for cx, cy in corners]
    start = min(projections)
    end = max(projections)
    count = max(1, int(math.floor((end - start) / interval)) + 1)
    values = [start + i * interval for i in range(count)]
    if values[-1] < end - 1e-6:
        values.append(end)

    segments: list[tuple[Point, Point]] = []
    for i, value in enumerate(values):
        pts = clip_scanline_to_rect(x, y, w, h, direction, value)
        if len(pts) != 2:
            continue
        p1, p2 = pts
        if bidirectional and i % 2 == 1:
            p1, p2 = p2, p1
        segments.append((p1, p2))
    return segments


def add_fill(
    lines: List[str],
    x: float,
    y: float,
    w: float,
    h: float,
    speed: float,
    power: float,
    s_max: float,
    interval: float,
    bidirectional: bool,
    scan_angle: float,
    indent: float,
    passes: int,
) -> int:
    ex, ey, ew, eh = effective_rect(x, y, w, h, indent)
    count = 0
    for _pass in range(int(passes)):
        for p1, p2 in scanline_segments(ex, ey, ew, eh, interval, scan_angle, bidirectional):
            count += add_polyline(lines, [p1, p2], speed, power, s_max)
        count += add_rectangle_outline(lines, ex, ey, ew, eh, speed, power, s_max)
    return count


def add_offset_fill(
    lines: List[str],
    x: float,
    y: float,
    w: float,
    h: float,
    speed: float,
    power: float,
    s_max: float,
    interval: float,
    indent: float,
    passes: int,
) -> int:
    ex, ey, ew, eh = effective_rect(x, y, w, h, indent)
    interval = max(0.01, float(interval))
    count = 0
    for _pass in range(int(passes)):
        inset = interval
        while ew - 2 * inset > 0.01 and eh - 2 * inset > 0.01:
            count += add_rectangle_outline(lines, ex + inset, ey + inset, ew - 2 * inset, eh - 2 * inset, speed, power, s_max)
            inset += interval
    return count


def generate_makera_studio_nc(settings: GeneratorSettings) -> Dict[str, object]:
    """Generate experimental Makera Studio-style NC output.

    This emitter follows observed new Makera Studio NC export structure and keeps
    the observed direct-NC start sequence at G0 Z0 even when z_offset is set.
    """
    settings.nc_s_max = resolve_nc_s_max(settings.nc_power_profile, settings.nc_s_max)
    rows = int(settings.rows)
    cols = int(settings.cols)

    speeds = rounded_axis_values(settings.speed_min, settings.speed_max, rows, settings.round_speed_values)
    powers = rounded_axis_values(settings.power_min, settings.power_max, cols, settings.round_power_values)

    tile_mode = LASER_MODES[settings.tile_mode_name]
    grid_w = cols * settings.tile_size + (cols - 1) * settings.gap
    grid_h = rows * settings.tile_size + (rows - 1) * settings.gap
    apply_auto_position(settings, grid_w, grid_h)

    lines = makera_header(settings)
    warnings = [
        "Makera Studio NC flavor is experimental; preview and verify in Makera Studio or an NC viewer before running.",
        "Observed Makera Studio direct NC exports use G0 Z0; z_offset is stored in settings but not emitted yet.",
    ]

    toolpath_number = 1
    shape_count = 0
    start_sequence_written = False

    if settings.labels_enabled and settings.nc_include_labels:
        add_toolpath_start(lines, toolpath_number, include_start_sequence=True)
        start_sequence_written = True
        label_count = add_labels(lines, settings, speeds, powers, grid_w, grid_h)
        if label_count:
            shape_count += label_count
            toolpath_number += 1
        else:
            toolpath_number = 1

    for r, speed in enumerate(speeds):
        for c, power in enumerate(powers):
            x = settings.grid_x + c * (settings.tile_size + settings.gap)
            y = settings.grid_y + r * (settings.tile_size + settings.gap)
            lines.append(f"; Tile row={r + 1} col={c + 1} speed={speed} power={power}")
            add_toolpath_start(lines, toolpath_number, include_start_sequence=not start_sequence_written)
            start_sequence_written = True
            if tile_mode == 0:
                for _pass in range(int(settings.passes)):
                    shape_count += add_rectangle_outline(lines, x, y, settings.tile_size, settings.tile_size, speed, power, settings.nc_s_max)
            elif tile_mode == 1:
                shape_count += add_fill(
                    lines,
                    x,
                    y,
                    settings.tile_size,
                    settings.tile_size,
                    speed,
                    power,
                    settings.nc_s_max,
                    settings.line_interval,
                    settings.bidirectional,
                    settings.scan_angle,
                    settings.indent_distance,
                    settings.passes,
                )
            else:
                shape_count += add_offset_fill(
                    lines,
                    x,
                    y,
                    settings.tile_size,
                    settings.tile_size,
                    speed,
                    power,
                    settings.nc_s_max,
                    settings.line_interval,
                    settings.indent_distance,
                    settings.passes,
                )
            toolpath_number += 1

    lines.extend(makera_footer())

    out = resolve_output_path(settings.output_path, settings.overwrite_existing, suffix=".nc", settings=settings)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return {
        "output": str(out),
        "format": "NC",
        "nc_flavor": "makera-studio",
        "lines": len(lines),
        "tiles": rows * cols,
        "toolpaths": toolpath_number - 1,
        "shapes": shape_count,
        "speeds_visual_top_to_bottom": list(reversed(speeds)),
        "powers_left_to_right": powers,
        "power_profile": settings.nc_power_profile,
        "s_max": settings.nc_s_max,
        "warnings": warnings,
    }
