from __future__ import annotations

import math
from typing import Dict, List

from .geometry import Point, Segment


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

