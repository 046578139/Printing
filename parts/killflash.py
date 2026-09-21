"""03 - Kill flash insert.

Presses into the housing's FRONT recess - the SHROUD_APERTURE counterbore
between the internal flange and the front face - and sits just under flush.
The cap covers it.

It does NOT go in a rear pocket. The objective fills the entire 36.90 bore
and bottoms against the back of the flange, so there is no rear pocket to go
into. The first version was built 36.65 x 5.00 for exactly that non-existent
pocket, which is why it would not fit anywhere.

Cell walls are 0.80 mm, i.e. two full 0.40 extrusions. The first version
used 0.45 mm single-extrusion walls and the slicer discarded all of them -
the part came off the plate as a bare rim with stubs. Thin-wall detection is
not something to stake a print on.

Print orientation: FLAT. The chamfer is on the TOP face only, so the plate
face stays full width; insert it chamfer-first.
"""

import math

import params as P
from lib.patterns import honeycomb_disc
from lib.solids import chamfer_outer


def build():
    disc = honeycomb_disc(P.KF_OD, P.KF_THICK, P.KF_CELL_AF,
                          P.KF_WALL, P.KF_RIM, chamfer=0.0)
    if P.KF_CHAMFER > 0:
        disc = disc - chamfer_outer(P.KF_THICK, P.KF_OD, P.KF_CHAMFER, True)
    return disc


def optics():
    open_frac = (P.KF_CELL_AF / (P.KF_CELL_AF + P.KF_WALL)) ** 2
    cutoff = math.degrees(math.atan2(P.KF_CELL_AF, P.KF_THICK))
    return open_frac, cutoff


META = dict(
    name="03_killflash_insert",
    desc="Honeycomb flash suppressor. Presses into the housing's front "
         "recess, chamfered edge leading, and sits 0.20 mm under flush.",
    orient="FLAT on the plate, chamfer UP. No supports.",
)
