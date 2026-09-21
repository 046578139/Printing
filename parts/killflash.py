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
from lib.solids import chamfer_outer, cyl


def build(od: float = None, cell: float = None, thick: float = None,
          marks: int = 0):
    """`marks` puts that many small dimples in the rim's front face.

    Five test discs 0.15 mm apart are indistinguishable in the hand, and a
    sweep you cannot identify afterwards is a wasted print. The dimples are
    0.80 mm in a 1.10 mm rim and 0.40 mm deep in a 3.60 mm part, so they
    touch neither the press surface nor the optics - you just count them.
    """
    od = P.KF_OD if od is None else od
    cell = P.KF_CELL_AF if cell is None else cell
    thick = P.KF_THICK if thick is None else thick

    disc = honeycomb_disc(od, thick, cell, P.KF_WALL, P.KF_RIM, chamfer=0.0)
    if P.KF_CHAMFER > 0:
        disc = disc - chamfer_outer(thick, od, P.KF_CHAMFER, True)

    if marks:
        r = od / 2.0 - P.KF_RIM / 2.0
        span = 7.0 * (marks - 1)                     # mm of arc used
        for i in range(marks):
            a = math.radians(-span / 2.0 / r * 180.0 / math.pi
                             + (7.0 * i) / r * 180.0 / math.pi)
            dot = cyl(1.2, max(1.2, P.NOZZLE * 2), seg=20).translate(
                [r * math.cos(a), r * math.sin(a), thick - P.DETAIL_DEPTH])
            disc = disc - dot
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
