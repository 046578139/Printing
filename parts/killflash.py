"""03 - Kill flash insert.

A printed honeycomb disc. Open-area fraction is (AF/(AF+wall))^2 and the
off-axis cutoff is atan(AF/thickness), so the two numbers to play with are
KF_CELL_AF and KF_THICK in params.py.

Cell walls are a single 0.45 mm extrusion - see docs/PRINTING.md for the
slicer settings that keep them single-wall instead of being dropped.
"""

import math
import params as P
from lib.patterns import honeycomb_disc


def build():
    return honeycomb_disc(P.KF_OD, P.KF_THICK, P.KF_CELL_AF,
                          P.KF_WALL, P.KF_RIM, P.KF_CHAMFER)


def optics():
    open_frac = (P.KF_CELL_AF / (P.KF_CELL_AF + P.KF_WALL)) ** 2
    cutoff = math.degrees(math.atan2(P.KF_CELL_AF, P.KF_THICK))
    return open_frac, cutoff


META = dict(
    name="03_killflash_insert",
    desc="Honeycomb flash suppressor. Drops into the shroud from the rear.",
    orient="FLAT on the plate. No supports. Thin-wall detection ON.",
)
