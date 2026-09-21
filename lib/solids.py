"""Primitive and helper solids built on manifold3d.

Coordinate convention used throughout this project
--------------------------------------------------
  +Z  = forward along the optical axis (out of the objective, toward target)
  Z=0 = rear face of whichever part is being built
  +X  = outboard/inboard (left-right across the face of the NVG)
  +Y  = up

Everything is in millimetres.
"""

import math
import numpy as np
import manifold3d as m3d
from manifold3d import Manifold, CrossSection, JoinType, FillRule

# Global tessellation. 128 segments on a ~45 mm part gives ~1.1 mm facets,
# well below what a 0.4 mm nozzle can resolve.
SEG = 128
m3d.set_circular_segments(SEG)


# --------------------------------------------------------------------------
# 2D helpers (CrossSection)
# --------------------------------------------------------------------------

def poly(points) -> CrossSection:
    """CrossSection from a single closed polygon given as [(x, y), ...]."""
    return CrossSection([np.asarray(points, dtype=float)], FillRule.NonZero)


def circle2d(d: float, seg: int = 0) -> CrossSection:
    return CrossSection.circle(d / 2.0, seg)


def rect2d(w: float, h: float, center: bool = True) -> CrossSection:
    cs = CrossSection.square((w, h), center)
    return cs


def fillet2d(cs: CrossSection, r: float, seg: int = 0) -> CrossSection:
    """Round outside corners by r (offset out then back in)."""
    if r <= 0:
        return cs
    return cs.offset(r, JoinType.Round, 2.0, seg).offset(-r, JoinType.Round, 2.0, seg)


def round2d(cs: CrossSection, r: float, seg: int = 0) -> CrossSection:
    """Round both convex and concave corners by r."""
    if r <= 0:
        return cs
    return (cs.offset(r, JoinType.Round, 2.0, seg)
              .offset(-2.0 * r, JoinType.Round, 2.0, seg)
              .offset(r, JoinType.Round, 2.0, seg))


def hexagon2d(across_flats: float) -> CrossSection:
    """Regular hexagon with a flat at top and bottom (pointy left/right)."""
    r = across_flats / math.sqrt(3.0)          # circumradius
    pts = [(r * math.cos(math.radians(60 * i)),
            r * math.sin(math.radians(60 * i))) for i in range(6)]
    return poly(pts)


# --------------------------------------------------------------------------
# 3D primitives
# --------------------------------------------------------------------------

def cyl(h: float, d: float, d_top: float = None, center: bool = False,
        seg: int = 0) -> Manifold:
    """Cylinder / cone by diameter, sitting on Z=0 unless center=True."""
    rt = d / 2.0 if d_top is None else d_top / 2.0
    return Manifold.cylinder(h, d / 2.0, rt, seg, center)


def tube(h: float, od: float, id_: float, seg: int = 0) -> Manifold:
    """Hollow cylinder on Z=0. Cutter is over-long so the boolean is clean."""
    return cyl(h, od, seg=seg) - cyl(h + 2.0, id_, seg=seg).translate([0, 0, -1.0])


def box(x: float, y: float, z: float, center: bool = True) -> Manifold:
    b = Manifold.cube((x, y, z), False)
    if center:
        b = b.translate([-x / 2.0, -y / 2.0, -z / 2.0])
    return b


def profile_revolve(points, seg: int = 0, degrees: float = 360.0) -> Manifold:
    """Revolve a closed (radius, z) profile about the Z axis.

    manifold3d revolves a CrossSection about *its* Y axis, so the profile is
    authored as (x=radius, y=z) and comes back already oriented with Z up.
    """
    return poly(points).revolve(seg, degrees)


def extrude(cs: CrossSection, h: float, center: bool = False) -> Manifold:
    m = cs.extrude(h)
    return m.translate([0, 0, -h / 2.0]) if center else m


# --------------------------------------------------------------------------
# Feature helpers
# --------------------------------------------------------------------------

def chamfer_outer(z: float, d: float, size: float, up: bool,
                  seg: int = 0) -> Manifold:
    """Ring cutter that puts a 45 degree chamfer on an OUTSIDE edge sitting
    at height z on diameter d. up=True chamfers a top edge, False a bottom
    edge. The cutter runs well past the part so the boolean is unambiguous."""
    big = d / 2.0 + 4 * size + 4
    if up:
        zf = z + size + 2                       # far side, past the part
        pts = [(d / 2, z - size),
               (big, z - size),
               (big, zf),
               (d / 2 - size - (zf - z), zf)]
    else:
        zf = z - size - 2
        pts = [(d / 2, z + size),
               (big, z + size),
               (big, zf),
               (d / 2 - size - (z - zf), zf)]
    return profile_revolve(pts, seg)


def bore_lead_in(z: float, d: float, size: float, up: bool,
                 seg: int = 0) -> Manifold:
    """Cutter putting a 45 degree lead-in on a bore of diameter d whose mouth
    is at height z. up=True means the bore opens toward +Z."""
    if up:
        zf = z + 2
        pts = [(0, z - size),
               (d / 2, z - size),
               (d / 2 + size + 2, zf),
               (0, zf)]
    else:
        zf = z - 2
        pts = [(0, z + size),
               (d / 2, z + size),
               (d / 2 + size + 2, zf),
               (0, zf)]
    return profile_revolve(pts, seg)


def polar(obj: Manifold, n: int, start: float = 0.0) -> Manifold:
    """Union of n copies of obj rotated about Z."""
    out = []
    for i in range(n):
        out.append(obj.rotate([0, 0, start + 360.0 * i / n]))
    return Manifold.batch_boolean(out, m3d.OpType.Add)


def union(parts) -> Manifold:
    parts = [p for p in parts if p is not None]
    if not parts:
        return Manifold()
    return Manifold.batch_boolean(parts, m3d.OpType.Add)


def difference(base: Manifold, cutters) -> Manifold:
    cutters = [c for c in cutters if c is not None]
    if not cutters:
        return base
    return base - union(cutters)


def prism_chamfered(cs: CrossSection, h: float, c_bot: float = 0.0,
                    c_top: float = 0.0, steps: int = 6) -> Manifold:
    """Extrude an arbitrary (possibly non-convex) 2D profile with edge breaks
    on the top and/or bottom face.

    Done as a short stack of progressively inset slices rather than a true
    conic loft: manifold3d has no offset-loft, and a hull would fill in the
    concave joins where the cord bosses meet the cap rim. At 0.1 mm steps the
    staircase is half a layer high, i.e. invisible once printed.

    Each slice is extruded to twice its step so that consecutive slices
    interpenetrate. Butt-jointing them on coplanar faces does NOT merge them
    into one shell - the result looks right but decomposes into loose shards,
    which slices as a pile of separate objects.
    """
    parts = []
    z0, z1 = c_bot, h - c_top
    if z1 > z0:
        parts.append(cs.extrude(z1 - z0).translate([0, 0, z0]))
    for c, base, up in ((c_bot, 0.0, True), (c_top, h, False)):
        if c <= 0:
            continue
        st = c / steps
        for i in range(steps):
            layer = cs.offset(-(c - i * st), JoinType.Round)
            if layer.is_empty():
                continue
            zz = base + i * st if up else base - (i + 2) * st
            parts.append(layer.extrude(st * 2.0).translate([0, 0, zz]))
    return union(parts)
