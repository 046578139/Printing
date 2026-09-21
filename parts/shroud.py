"""02 - Kill flash housing ("shroud").

Slips over the objective front bezel. The objective goes all the way in and
bottoms against the internal flange, which is the depth stop. The kill flash
presses into the counterbore on the FRONT of that flange and is covered by
the cap.

Axial layout, Z=0 at the rear face, +Z forward:

    0.0 ................ objective bezel enters here
    SHROUD_BORE_LEN .... objective BOTTOMS OUT against the flange
    +FLANGE_T .......... cap register spigot begins
    +REG_HEIGHT ........ front face

The kill flash does NOT live in this bore - the objective fills all of it.
It goes into the FRONT recess, the SHROUD_APERTURE-diameter counterbore
between the flange and the front face.

Print orientation: FRONT FACE DOWN on the plate. Every overhang in the part
is then either a 45 degree chamfer or an upward-opening pocket, so it needs
no support anywhere. The front face itself is left perfectly flat - see the
plate-face rule in params.py.
"""

import math

import params as P
from lib.solids import (profile_revolve, cyl, chamfer_outer, bore_lead_in,
                        union, rect2d)
from lib.patterns import axial_flutes

Z_KF    = P.SHROUD_BORE_LEN                       # (kept as an alias)
Z_FLNG  = P.SHROUD_BORE_LEN                       # flange rear face / seat
Z_BODY  = Z_FLNG + P.SHROUD_FLANGE_T              # body front / register base
Z_TOP   = Z_BODY + P.REG_HEIGHT                   # front face
TOTAL   = Z_TOP


def build(slots: int = None):
    slots = P.SHROUD_SLOTS if slots is None else slots
    ro   = P.SHROUD_OD / 2.0
    rreg = P.REG_OD / 2.0

    # --- outer profile -----------------------------------------------------
    # The OD is relieved over the collet so the fingers are thin enough to
    # actually flex (see COLLET_WALL in params.py), then blended back out on a
    # 45 degree cone. Square shoulder at the front, not a cone: the cap has to
    # land on a flat annulus or it rocks. Printed front-face-down the shoulder
    # leaves a 1.3 mm cantilever ledge, which bridges cleanly without support.
    rcol = P.COLLET_OD / 2.0
    body = profile_revolve([
        (0.0,  0.0),
        (rcol, 0.0),
        (rcol, P.COLLET_LEN),
        (ro,   P.COLLET_LEN + P.COLLET_TAPER),
        (ro,   Z_BODY),
        (rreg, Z_BODY),
        (rreg, Z_TOP),
        (0.0,  Z_TOP),
    ] if slots else [
        (0.0,  0.0),
        (ro,   0.0),
        (ro,   Z_BODY),
        (rreg, Z_BODY),
        (rreg, Z_TOP),
        (0.0,  Z_TOP),
    ])

    # --- bores -------------------------------------------------------------
    # One straight bore for the bezel and the kill flash, then the aperture.
    bore = profile_revolve([
        (0.0,                   -1.0),
        (P.SHROUD_BORE / 2.0,   -1.0),
        (P.SHROUD_BORE / 2.0,   Z_FLNG),
        (P.SHROUD_APERTURE / 2.0, Z_FLNG),
        (P.SHROUD_APERTURE / 2.0, Z_TOP + 1.0),
        (0.0,                   Z_TOP + 1.0),
    ])
    part = body - bore

    # --- edge breaks -------------------------------------------------------
    cuts = [
        # rear lead-in so the shroud starts onto the bezel square, not cocked
        bore_lead_in(0.0, P.SHROUD_BORE, P.SHROUD_LEAD_IN, False),
        # rear outside edge - kept small, it shares the rear face with the
        # bore lead-in above and that face is only COLLET_WALL wide
        chamfer_outer(0.0, P.COLLET_OD if slots else P.SHROUD_OD,
                      P.SHROUD_REAR_CH, False),
        # NOTE: no chamfer on the front register. That face goes DOWN on the
        # plate, and chamfering it narrowed the first layer so the part
        # started ragged and only cleaned up once it reached full width.
        # break the aperture edge so it does not shave the kill flash rim
        bore_lead_in(Z_FLNG, P.SHROUD_APERTURE, 0.5, False),
    ]
    part = part - union(cuts)

    # --- collet slots ------------------------------------------------------
    if slots:
        span = P.SHROUD_OD + 8.0
        rb = P.SHROUD_BORE / 2.0

        # The slot itself: a radial cut from the rear face forward.
        blade = rect2d(span, P.SLOT_W).translate((span / 2.0, 0.0)) \
            .extrude(P.SLOT_LEN + 1.0).translate([0, 0, -1.0])

        # Round crack-arrestor at the root. A slot ending in a flat face has
        # two square corners at exactly the point of highest bending stress;
        # a keyhole 1.5x the slot width spreads it.
        keyhole = cyl(span, P.SLOT_KEYHOLE_D, seg=48).rotate([0, 90, 0]) \
            .translate([0.0, 0.0, P.SLOT_LEN])

        # Break the two axial edges each slot leaves in the BORE. Left square,
        # these are eight sharp edges that scrape the full grip length of the
        # objective bezel on every install - on a coated optic that is the one
        # piece of damage this design could actually do.
        th = math.asin(min(1.0, (P.SLOT_W / 2.0) / rb))
        breaks = [cyl(P.SLOT_LEN + 1.0, P.SLOT_EDGE_BREAK, seg=32)
                  .translate([rb * math.cos(sgn * th), rb * math.sin(sgn * th), -1.0])
                  for sgn in (1.0, -1.0)]

        cutter = union([blade, keyhole] + breaks)
        part = part - union([cutter.rotate([0, 0, 45.0 + 360.0 * i / slots])
                             for i in range(slots)])

    # --- grip --------------------------------------------------------------
    part = part - axial_flutes(P.KNURL_START, P.KNURL_LEN, P.SHROUD_OD,
                               P.KNURL_COUNT, P.KNURL_DEPTH)
    return part


META = dict(
    name="02_killflash_housing",
    desc="Shroud: presses onto the objective bezel, holds the kill flash, "
         "gives the cap a register to close on.",
    orient="Front face down - ALREADY ORIENTED. No supports.",
)


META_SOLID = dict(
    name="02b_killflash_housing_solid",
    desc="ALTERNATIVE: the same housing with the collet slots deleted and the "
         "OD relief filled in. Cleaner, stiffer - and a press fit roughly "
         "1.7x tighter than 02, because the collet was carrying about a "
         "tenth of the grip on a third of the length. Try it before you "
         "commit; it is also 1.7x harder to get back OFF.",
    orient="Front face down - ALREADY ORIENTED. No supports.",
    hardware="None.",
)
