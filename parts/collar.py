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
from lib.patterns import cord_ear_2d
import manifold3d as m3d
from manifold3d import Manifold, JoinType

def geom(bore: float = None, gap: float = None) -> dict:
    """Derive the collar's layout from a bore and a pinch gap.

    Kept as a function so a wider-gap prototype collar can be generated from
    the same code. The cord ear always reaches out to CORD_RADIUS, whatever
    the bore, so the bungee still runs parallel to the optical axis.
    """
    bore = P.COL_BORE if bore is None else bore
    gap = P.COL_GAP if gap is None else gap
    r_out = bore / 2.0 + P.COL_WALL
    return dict(
        bore=bore, gap=gap, r_out=r_out,
        ear_proj=P.CORD_RADIUS + P.CORD_HOLE / 2 + P.CORD_EDGE_WALL - r_out,
        y_lug=-(r_out + P.LUG_PROJ),          # outer face of the clamp lugs
        y_scr=-(r_out + P.LUG_PROJ * 0.55),   # screw axis
        z_scr=P.LUG_H / 2.0,
        x_lug=gap / 2.0 + P.LUG_W,            # outer face of each lug in X
    )


# Module-level defaults for the standard collar.
_G     = geom()
R_OUT  = _G["r_out"]
R_BORE = P.COL_BORE / 2.0
Y_LUG  = _G["y_lug"]
Y_SCR  = _G["y_scr"]
Z_SCR  = _G["z_scr"]
X_LUG  = _G["x_lug"]


def clamp_range(g: dict) -> tuple:
    """(largest, smallest) barrel this collar can actually grip. Closing the
    pinch gap by g shortens the bore circumference by exactly g."""
    return g["bore"], g["bore"] - g["gap"] / math.pi


def _ear(angle: float, g: dict) -> Manifold:
    """Cord ear: a round boss on a blended stem, with a fore/aft cord hole.

    Same profile the cap and the pinch collar use - see cord_ear_2d. The old
    square slab read as a part from a different design sitting next to a cap
    made entirely of rounds.
    """
    prof = cord_ear_2d(g["r_out"], P.CORD_RADIUS, P.EAR_BOSS_D,
                       P.EAR_STEM_W, P.EAR_ROUND)
    ear = prof.extrude(P.EAR_T)
    hole = cyl(P.EAR_T + 2.0, P.CORD_HOLE, seg=48) \
        .translate([P.CORD_RADIUS, 0.0, -1.0])
    return (ear - hole).rotate([0, 0, angle])


def _clamp_lugs(g: dict) -> Manifold:
    """Two blocks flanking the pinch gap, plus the screw and nut features."""
    Y_LUG, Y_SCR, Z_SCR, X_LUG = g["y_lug"], g["y_scr"], g["z_scr"], g["x_lug"]
    depth = abs(Y_LUG)
    lug = box(P.LUG_W, depth, P.LUG_H, center=False)
    right = lug.translate([g["gap"] / 2.0, Y_LUG, 0.0])
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


def build(bore: float = None, gap: float = None):
    g = geom(bore, gap)
    od = 2 * g["r_out"]

    band = tube(P.COL_HEIGHT, od, g["bore"])
    part = union([band, _clamp_lugs(g), _ear(0.0, g), _ear(180.0, g)])

    # Pinch gap, cut after the lugs exist so it splits them too.
    span = g["r_out"] + P.LUG_PROJ + 6.0
    slot = box(g["gap"], span, P.COL_HEIGHT + 4.0, center=False) \
        .translate([-g["gap"] / 2.0, -span, -2.0])

    # Re-cut the bore last: the lugs and ears both overlap into it.
    bore_cut = cyl(P.COL_HEIGHT + 4.0, g["bore"], seg=SEG).translate([0, 0, -2.0])

    part = part - union([slot, bore_cut])

    # Edge breaks on the TOP only. The bottom face is the plate face and
    # stays dead flat: chamfering it left a 2.0 mm first layer on a 3.2 mm
    # band, which printed ragged for several layers before widening out.
    # Fit the collar top-first - the lead-in is up there.
    part = part - union([
        bore_lead_in(P.COL_HEIGHT, g["bore"], 1.0, True),
        chamfer_outer(P.COL_HEIGHT, od, 0.8, True),
    ])
    return part


def build_proto():
    """Wide-gap prototype collar.

    The production collar has a 2.6 mm pinch gap, which is only 0.83 mm of
    diameter range - fine once OBJ_COLLAR_OD is known, useless before. This
    one opens the gap far enough to clamp anywhere across the plausible
    spread, so cord routing and the flip action can be shaken down before
    the barrel has been gauged.

    It does not sit as round when clamped on a small barrel, and it needs a
    longer screw. Not for the final set.
    """
    return build(P.COL_PROTO_BORE, P.COL_PROTO_GAP)


META = dict(
    name="01_collar",
    desc="Split band clamp with M3 pinch screw. Anchors the shock cord.",
    orient="REAR FACE DOWN (ears and lugs on the plate). No supports.",
    hardware="1x M3 socket head cap screw, 16 mm + 1x M3 hex nut, per eye.",
)

META_PROTO = dict(
    name="01b_collar_proto",
    desc="PROTOTYPE ONLY: wide-gap collar that clamps across a range of "
         "barrel diameters, for use before OBJ_COLLAR_OD has been gauged.",
    orient="REAR FACE DOWN (ears and lugs on the plate). No supports.",
    hardware="1x M3 socket head cap screw, 30 mm + 1x M3 hex nut, per eye.",
)
