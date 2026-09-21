"""01c - Snap-fit retention collar (no tools).

An alternative to the screw-clamp collar: a split C-ring that flexes out of
round, passes over the barrel, and springs back around it. Same cord ears in
the same places, so it is a drop-in swap for testing.

The trade against the screw clamp is not about strength, it is about creep.
A screw clamp holds by a preload you can re-tighten; a snap ring holds by a
sustained elastic strain, and every polymer here stress-relaxes. It will be
tightest on the day you fit it.

Mechanics
---------
Installation: the narrowest point the barrel must pass is the CHORD between
the two tips, so the tips have to spread by (barrel - chord). Peak bending
strain is at the crown, opposite the gap. Both are computed below rather
than guessed, because "it felt about right in PLA" does not transfer to a
carbon-filled resin with a third of the elongation.

Print orientation: REAR FACE DOWN, same as the screw collar. The band then
bends WITHIN its layers rather than across them, so installation loads X-Y
strength and never tests layer adhesion - which is the whole reason this
part is printable at all.
"""

import math

import numpy as np

import params as P
from lib.solids import (tube, cyl, poly, rect2d, fillet2d, union, SEG,
                        bore_lead_in, chamfer_outer)
from manifold3d import Manifold, CrossSection


def mechanics(barrel: float = None, wall: float = None, wrap: float = None,
              interference: float = None) -> dict:
    """Curved-beam model of the ring. Returns spreads and peak strains.

    Each arm is treated as a curved cantilever built in at the crown and
    loaded at the tip (Castigliano). `install` is the transient strain while
    the ring passes over the barrel; `seated` is the sustained strain that
    actually provides grip - and the one that creeps.
    """
    barrel = P.OBJ_COLLAR_OD if barrel is None else barrel
    wall = P.COL_WALL if wall is None else wall
    wrap = P.SNAP_WRAP if wrap is None else wrap
    interference = P.SNAP_INTERF if interference is None else interference

    d_free = barrel - interference
    g = math.radians((360.0 - wrap) / 2.0)
    chord = d_free * math.sin(g)
    spread = barrel - chord

    beta = math.radians(wrap / 2.0)
    r_mean = (d_free + wall) / 2.0
    phi = np.linspace(0.0, beta, 4000)
    J = float(np.trapezoid((np.cos(phi) - math.cos(beta)) ** 2, phi))

    install = (spread / 2) * wall * (1 - math.cos(beta)) / (2 * r_mean ** 2 * J)

    # Seated: the bore is forced from d_free out to the barrel, so the band's
    # curvature changes. eps = (t/2) * |1/Rf - 1/Rb|
    rf, rb = d_free / 2.0, barrel / 2.0
    seated = (wall / 2.0) * abs(1 / rf - 1 / rb)

    return dict(barrel=barrel, free_bore=d_free, chord=chord, spread=spread,
                install=install, seated=seated, J=J, r_mean=r_mean)


def _sector(angle: float, r: float, start: float) -> CrossSection:
    """Pie sector CrossSection, `angle` degrees wide, beginning at `start`."""
    n = max(4, int(SEG * angle / 360.0) + 1)
    pts = [(0.0, 0.0)]
    for i in range(n + 1):
        a = math.radians(start + angle * i / n)
        pts.append((r * math.cos(a), r * math.sin(a)))
    return poly(pts)


def _ear(angle: float, r_out: float, ear_proj: float) -> Manifold:
    x0, x1 = r_out - 2.5, r_out + ear_proj
    prof = fillet2d(rect2d(x1 - x0, P.EAR_W)
                    .translate(((x0 + x1) / 2.0, 0.0)), P.EAR_FILLET)
    hole = cyl(P.EAR_T + 2.0, P.CORD_HOLE, seg=48) \
        .translate([P.CORD_RADIUS, 0.0, -1.0])
    return (prof.extrude(P.EAR_T) - hole).rotate([0, 0, angle])


def build():
    bore = P.SNAP_BORE
    r_out = bore / 2.0 + P.COL_WALL
    od = 2 * r_out
    ear_proj = P.CORD_RADIUS + P.CORD_HOLE / 2 + P.CORD_EDGE_WALL - r_out

    band = tube(P.COL_HEIGHT, od, bore)
    part = union([band, _ear(0.0, r_out, ear_proj),
                  _ear(180.0, r_out, ear_proj)])

    big = od + 20.0
    gap_deg = 360.0 - P.SNAP_WRAP

    # Gap, centred at 6 o'clock so the collar pushes on the same way the
    # screw version does.
    gap = _sector(gap_deg, big, 270.0 - gap_deg / 2.0) \
        .extrude(P.COL_HEIGHT + 4.0).translate([0, 0, -2.0])

    # Cam ramp: widen the gap only over the innermost SNAP_LEADIN_D of wall,
    # so the tips present a flare to the barrel instead of a square corner
    # and the ring is pushed open rather than jammed.
    lead_deg = gap_deg + 2 * P.SNAP_LEADIN
    lead = _sector(lead_deg, big, 270.0 - lead_deg / 2.0) \
        .extrude(P.COL_HEIGHT + 4.0).translate([0, 0, -2.0])
    ring = tube(P.COL_HEIGHT + 4.0, bore + 2 * P.SNAP_LEADIN_D, bore - 2.0) \
        .translate([0, 0, -2.0])
    part = part - union([gap, lead ^ ring])

    # Re-cut the bore: the ears overlap into it.
    part = part - cyl(P.COL_HEIGHT + 4.0, bore, seg=SEG).translate([0, 0, -2.0])

    part = part - union([
        bore_lead_in(P.COL_HEIGHT, bore, 1.0, True),
        bore_lead_in(0.0, bore, 0.6, False),
        chamfer_outer(P.COL_HEIGHT, od, 0.8, True),
        chamfer_outer(0.0, od, 0.6, False),
    ])
    return part


META = dict(
    name="01c_collar_snap",
    desc="No-tools split C-ring collar. Flexes out of round over the barrel "
         "and springs back. Same cord ears as the screw version.",
    orient="REAR FACE DOWN. No supports. Band bends in-plane, never across "
           "layers.",
    hardware="None.",
)
