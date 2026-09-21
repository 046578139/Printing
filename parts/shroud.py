"""02 - Kill flash housing ("shroud").

Slips over the objective front bezel and carries the kill flash. The kill
flash loads from the REAR, seats against an integral front flange, and is
then trapped by the objective itself - no snap ring, no glue, and it still
comes apart for cleaning in two seconds.

Axial layout, Z=0 at the rear face, +Z forward:

    0.0 .............. objective bezel enters here
    GRIP_LEN ......... kill flash seats from here
    +KF_THICK ........ front retaining flange begins
    +FLANGE_T ........ cap register spigot begins
    +REG_HEIGHT ...... front face

Print orientation: FRONT FACE DOWN on the plate. Every overhang in the part
is then either a 45 degree chamfer or an upward-opening pocket, so it needs
no support anywhere.
"""

import params as P
from lib.solids import (profile_revolve, cyl, chamfer_outer, bore_lead_in,
                        union, rect2d, fillet2d, circle2d)
from lib.patterns import axial_flutes

Z_KF    = P.SHROUD_GRIP_LEN                       # kill flash seat face
Z_FLNG  = Z_KF + P.KF_THICK                       # flange rear face
Z_BODY  = Z_FLNG + P.SHROUD_FLANGE_T              # body front / register base
Z_TOP   = Z_BODY + P.REG_HEIGHT                   # front face
TOTAL   = Z_TOP


def build():
    ro   = P.SHROUD_OD / 2.0
    rreg = P.REG_OD / 2.0

    # --- outer profile -----------------------------------------------------
    # Square shoulder, not a cone: the cap has to land on a flat annulus or it
    # rocks. Printed front-face-down this leaves a 1.3 mm cantilever ledge,
    # which bridges cleanly without support.
    body = profile_revolve([
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
        # rear outside edge
        chamfer_outer(0.0, P.SHROUD_OD, 0.8, False),
        # front face edge of the register
        chamfer_outer(Z_TOP, P.REG_OD, P.REG_CHAMFER, True),
        # break the aperture edge so it does not shave the kill flash rim
        bore_lead_in(Z_FLNG, P.SHROUD_APERTURE, 0.5, False),
    ]
    part = part - union(cuts)

    # --- collet slots ------------------------------------------------------
    # Cut from the rear face forward, through the full wall, with a rounded
    # end so there is no square corner for a crack to start from.
    if P.SHROUD_SLOTS:
        slot2d = fillet2d(rect2d(P.SHROUD_OD + 6.0, P.SLOT_W), P.SLOT_END_R)
        blade = slot2d.extrude(P.SLOT_LEN + P.SLOT_END_R)
        # Keep only the outboard half so the slot does not cut clean across.
        half = rect2d(P.SHROUD_OD + 8.0, P.SLOT_W + 2.0) \
            .translate(((P.SHROUD_OD + 8.0) / 2.0, 0.0))
        blade = blade ^ half.extrude(P.SLOT_LEN + P.SLOT_END_R)
        blade = blade.translate([0, 0, -P.SLOT_END_R])
        part = part - union([blade.rotate([0, 0, 45.0 + 360.0 * i / P.SHROUD_SLOTS])
                             for i in range(P.SHROUD_SLOTS)])

    # --- grip --------------------------------------------------------------
    part = part - axial_flutes(P.KNURL_START, P.KNURL_LEN, P.SHROUD_OD,
                               P.KNURL_COUNT, P.KNURL_DEPTH)
    return part


META = dict(
    name="02_killflash_housing",
    desc="Shroud: presses onto the objective bezel, holds the kill flash, "
         "gives the cap a register to close on.",
    orient="FRONT FACE DOWN (register on the plate). No supports.",
)
