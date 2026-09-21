"""Repeating textures: honeycomb, axial flutes, grip panels, centre mark."""

import math
import numpy as np
import manifold3d as m3d
from manifold3d import Manifold, CrossSection, JoinType

from .solids import (poly, circle2d, rect2d, hexagon2d, fillet2d, round2d,
                     cyl, box, union, extrude, SEG)


def hex_centres(af: float, wall: float, extent: float, keep):
    """Centres of a hex lattice covering +/-extent, filtered by `keep(x, y)`.

    Pitch is af + wall in all six directions, so every wall between cells is
    the same thickness. Only WHOLE cells are emitted - partial cells clipped
    by a boundary leave slivers thinner than one extrusion, which the slicer
    either drops or prints as stringy rubbish.
    """
    p = af + wall
    dx = p * math.sqrt(3.0) / 2.0
    ncol = int(extent / dx) + 2
    nrow = int(extent / p) + 2
    out = []
    for i in range(-ncol, ncol + 1):
        cx = i * dx
        yoff = (p / 2.0) if (i % 2) else 0.0
        for j in range(-nrow, nrow + 1):
            cy = j * p + yoff
            if keep(cx, cy):
                out.append((cx, cy))
    return out


def _hex_union(centres, af: float) -> CrossSection:
    if not centres:
        return CrossSection()
    cell = hexagon2d(af)
    return CrossSection.batch_boolean(
        [cell.translate(c) for c in centres], m3d.OpType.Add)


def honeycomb_disc(od: float, thickness: float, across_flats: float,
                   wall: float, rim: float, chamfer: float = 0.0) -> Manifold:
    """Solid-rimmed honeycomb disc, axis on Z, sitting on Z=0.

    Cells whose centre falls inside the open aperture are kept and clipped
    to it. A cell clipped at its own centre still leaves half a hexagon, so
    this costs no printability but buys back the ~18 percent of open area
    that a whole-cells-only rule throws away - and open area is transmitted
    light, which is the whole point of the device this bolts onto.
    """
    r_open = od / 2.0 - rim
    centres = hex_centres(across_flats, wall, r_open + across_flats,
                          lambda x, y: math.hypot(x, y) <= r_open)
    holes = _hex_union(centres, across_flats) ^ circle2d(2 * r_open)
    disc = (circle2d(od) - holes).extrude(thickness)

    if chamfer > 0:
        from .solids import chamfer_outer
        disc = disc - chamfer_outer(thickness, od, chamfer, True)
        disc = disc - chamfer_outer(0.0, od, chamfer, False)
    return disc


def axial_flutes(z0: float, length: float, d: float, count: int,
                 depth: float) -> Manifold:
    """Cutter: `count` semicircular grooves running along Z on diameter d."""
    r = d / 2.0
    groove_d = max(1.0, math.pi * d / count * 0.78)
    tool = cyl(length, groove_d, seg=20).translate([r, 0, z0])
    return union([tool.rotate([0, 0, 360.0 * i / count]) for i in range(count)])


def grip_panel(width: float, height: float, depth: float, cell: float,
               wall: float, corner_r: float = 1.4) -> Manifold:
    """A rounded-rect patch of hex texture, sitting on Z=0, `depth` tall.

    Returns the WALL LATTICE. Subtract it from a face and the hex cells are
    left standing proud of the grooves - which is the way round that prints
    cleanly when the decorated face goes down on the plate.
    """
    cr = cell / math.sqrt(3.0)
    hx, hy = width / 2.0 - wall, height / 2.0 - wall

    def inside(x, y):
        # Whole cells only, and stay clear of the rounded corners.
        if abs(x) + cr > hx or abs(y) + cr > hy:
            return False
        ox, oy = abs(x) - (hx - corner_r), abs(y) - (hy - corner_r)
        if ox > 0 and oy > 0:
            return math.hypot(ox, oy) + cr <= corner_r
        return True

    outline = fillet2d(rect2d(width, height), corner_r)
    centres = hex_centres(cell, wall, max(width, height), inside)
    return (outline - _hex_union(centres, cell)).extrude(depth)


def chevron_mark(width: float, depth: float) -> Manifold:
    """Generic mountain mark: a solid peak with a notch cut out of its base.

    Deliberately NOT anyone's trademark - it is a plain geometric mountain.
    Swap the polygon below, or set MARK_ENABLE = False in params.py, to put
    your own mark here.
    """
    w = width / 2.0
    h = width * 0.60
    y0 = -h / 2.0

    peak = poly([(-w, y0), (w, y0), (0.0, y0 + h)])
    # Notch: a smaller inverted peak taken out of the base, which reads as a
    # mountain rather than a plain triangle and gives the deboss two edges.
    nw, nh = w * 0.38, h * 0.44
    notch = poly([(-nw, y0 - 0.1), (nw, y0 - 0.1), (0.0, y0 + nh)])
    # Rounded generously: at 0.6 mm deep the deboss floor is only a few
    # layers, and sharp internal corners there leave an unclosed seam.
    return round2d(peak - notch, 0.75).extrude(depth)


def cord_ear_2d(r_out: float, cord_radius: float, boss_d: float,
                stem_w: float, round_r: float) -> CrossSection:
    """Cord anchor profile: a circular boss on a tapered stem, blended.

    Shared by the collars and the cap so every cord anchor in the set is the
    same shape. The collars used to carry square slabs, which sat next to a
    cap full of round bosses and read as parts from two different designs.

    `stem_w` should equal `boss_d`: the ear then runs straight out from the
    band at constant width and the load path from the cord into the band
    never narrows. A stem thinner than the boss looks neater and puts the
    smallest section in the part directly under the highest load.
    """
    boss = circle2d(boss_d).translate((cord_radius, 0.0))
    stem = rect2d(cord_radius - r_out + 8.0, stem_w) \
        .translate(((r_out - 4.0 + cord_radius) / 2.0, 0.0))
    return round2d(boss + stem, round_r)


def pinch_tab_2d(r_out: float, proj: float, w: float, head_d: float,
                 round_r: float) -> CrossSection:
    """Finger tab profile: a narrow stem with a rounded head.

    The head is what a fingertip pulls against. Narrow at the root so two of
    them can sit either side of a 20 degree gap without touching, and round
    everywhere because these are the most snag-prone features on the part.
    """
    stem = rect2d(proj + 3.0, w).translate((r_out + proj / 2.0 - 1.5, 0.0))
    head = circle2d(head_d).translate((r_out + proj, 0.0))
    return round2d(stem + head, round_r)
