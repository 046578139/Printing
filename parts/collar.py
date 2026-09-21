"""01 - Retention collar.

A split band clamp that anchors the shock cord to the objective barrel. An
M3 pinch screw closes a gap at 6 o'clock; two ears at 3 and 9 o'clock carry
the cord.

Why a screw clamp and not a snap band: the collar is the ONLY thing setting
the rotational orientation of the flip cap. If it creeps around the barrel
the thumb tab ends up somewhere useless. A clamped band cannot creep.

IMPORTANT FITMENT NOTE: clamp this onto a section of barrel that does NOT
rotate when you focus. On a PVS-14-pattern objective the focus ring turns;
clamping the collar to it will bind the focus.

Print orientation: REAR FACE DOWN (cord ears and clamp lugs on the plate).
The nut pocket is rotated vertex-up so it is self-supporting.
"""

import math
import params as P
from lib.solids import (tube, box, cyl, poly, rect2d, fillet2d, hexagon2d,
                        union, extrude, chamfer_outer, bore_lead_in, SEG)
import manifold3d as m3d
from manifold3d import Manifold, JoinType

R_OUT  = P.COL_OD / 2.0
R_BORE = P.COL_BORE / 2.0
Y_LUG  = -(R_OUT + P.LUG_PROJ)          # outer face of the clamp lugs
Y_SCR  = -(R_OUT + P.LUG_PROJ * 0.55)   # screw axis
Z_SCR  = P.LUG_H / 2.0
X_LUG  = P.COL_GAP / 2.0 + P.LUG_W      # outer face of each lug in X


def _ear(angle: float) -> Manifold:
    """Cord ear: a flat tab on the rear face with a fore/aft cord hole."""
    x0 = R_OUT - 2.5                     # overlap into the band
    x1 = R_OUT + P.EAR_PROJ
    prof = rect2d(x1 - x0, P.EAR_W).translate(((x0 + x1) / 2.0, 0.0))
    prof = fillet2d(prof, P.EAR_FILLET)
    ear = prof.extrude(P.EAR_T)
    hole = cyl(P.EAR_T + 2.0, P.CORD_HOLE, seg=48) \
        .translate([P.CORD_RADIUS, 0.0, -1.0])
    return (ear - hole).rotate([0, 0, angle])


def _clamp_lugs() -> Manifold:
    """Two blocks flanking the pinch gap, plus the screw and nut features."""
    depth = abs(Y_LUG)
    lug = box(P.LUG_W, depth, P.LUG_H, center=False)
    right = lug.translate([P.COL_GAP / 2.0, Y_LUG, 0.0])
    left  = lug.translate([-X_LUG,           Y_LUG, 0.0])
    lugs = union([right, left])

    # Round the outboard corners so the lugs do not snag on kit.
    keep = fillet2d(rect2d(2 * X_LUG, 2 * depth), 2.2).extrude(P.LUG_H)
    lugs = lugs ^ keep.translate([0, 0, 0])

    cuts = []
    # M3 clearance right through both lugs
    cuts.append(cyl(4 * X_LUG, P.M3_CLEAR, seg=48)
                .rotate([0, 90, 0]).translate([-2 * X_LUG, Y_SCR, Z_SCR]))
    # Socket head counterbore on the +X lug
    cuts.append(cyl(P.M3_HEAD_DEPTH + 1.0, P.M3_HEAD_D, seg=48)
                .rotate([0, -90, 0])
                .translate([X_LUG + 1.0, Y_SCR, Z_SCR]))
    # Hex nut trap on the -X lug, rotated so a VERTEX points up: a flat-topped
    # hex pocket would need support, a pointed one bridges itself.
    nut = hexagon2d(P.M3_NUT_AF).extrude(P.M3_NUT_DEPTH + 1.0)
    cuts.append(nut.rotate([0, 90, 0])
                   .translate([-X_LUG - 1.0, Y_SCR, Z_SCR]))
    return lugs - union(cuts)


def build():
    band = tube(P.COL_HEIGHT, P.COL_OD, P.COL_BORE)
    part = union([band, _clamp_lugs(), _ear(0.0), _ear(180.0)])

    # Pinch gap, cut after the lugs exist so it splits them too.
    span = R_OUT + P.LUG_PROJ + 6.0
    gap = box(P.COL_GAP, span, P.COL_HEIGHT + 4.0, center=False) \
        .translate([-P.COL_GAP / 2.0, -span, -2.0])

    # Re-cut the bore last: the lugs and ears both overlap into it.
    bore = cyl(P.COL_HEIGHT + 4.0, P.COL_BORE, seg=SEG).translate([0, 0, -2.0])

    part = part - union([gap, bore])

    # Edge breaks. Lead-in at the top of the bore so it starts onto the
    # barrel square; chamfers top and bottom outside.
    part = part - union([
        bore_lead_in(P.COL_HEIGHT, P.COL_BORE, 1.0, True),
        bore_lead_in(0.0, P.COL_BORE, 0.6, False),
        chamfer_outer(P.COL_HEIGHT, P.COL_OD, 0.8, True),
        chamfer_outer(0.0, P.COL_OD, 0.6, False),
    ])
    return part


META = dict(
    name="01_collar",
    desc="Split band clamp with M3 pinch screw. Anchors the shock cord.",
    orient="REAR FACE DOWN (ears and lugs on the plate). No supports.",
    hardware="1x M3 socket head cap screw, 16 mm + 1x M3 hex nut, per eye.",
)
