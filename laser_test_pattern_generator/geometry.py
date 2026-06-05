from __future__ import annotations

import copy as _copy
import math
import uuid
from typing import Dict, List, Tuple

from .settings import GeneratorSettings

Point = Tuple[float, float]
Segment = Tuple[Point, Point]


def make_uuid() -> str:
    return str(uuid.uuid4())


def linspace(a: float, b: float, n: int) -> List[float]:
    if n <= 0:
        raise ValueError("count must be > 0")
    if n == 1:
        return [float(a)]
    return [float(a) + (float(b) - float(a)) * i / (n - 1) for i in range(n)]

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

