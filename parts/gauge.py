"""05/06 - Fit gauges.

A ladder of short rings stepping through a range of bore diameters, each
with its size moulded onto a flag. Print one, find the ring that slides on
with light thumb pressure and does not fall off when inverted, and type that
number into params.py.

This exists because the two hardware diameters in this design are the only
things standing between a good set of caps and a pile of scrap, and a
15-minute gauge print beats guessing at a 45-minute shroud.
"""

import params as P
from lib.solids import (tube, box, cyl, rect2d, fillet2d, union,
                        bore_lead_in, chamfer_outer, SEG)
from lib.text3d import text_2d

FLAG_T     = 2.20
RAIL_W     = 4.50
TEXT_PAD   = 11.0


def build(nominal: float, fit: float = 0.0, count: int = None,
          step: float = None, plate: float = 240.0):
    """Ladder centred on `nominal` + `fit`, stepping by `step`.

    `fit` lets the ladder be centred on the *design* bore (nominal plus the
    intended clearance) rather than on the raw measurement. Rings wrap onto
    as many rows as it takes to stay inside `plate`.
    """
    count = count or P.GAUGE_COUNT
    step = step or P.GAUGE_STEP
    centre = nominal + fit
    mid = (count - 1) / 2.0

    bores = [centre + (i - mid) * step for i in range(count)]
    max_od = max(bores) + 2 * P.GAUGE_WALL
    pitch = max_od + P.GAUGE_PITCH_PAD
    y_out = max_od / 2.0 + TEXT_PAD
    row_pitch = y_out + RAIL_W / 2.0 + max_od / 2.0 + 4.0
    per_row = max(1, int(plate // pitch))

    solids = []
    rows = {}
    for i, b in enumerate(bores):
        row, col = divmod(i, per_row)
        x, y = col * pitch, -row * row_pitch
        rows.setdefault(row, []).append(col)

        od = b + 2 * P.GAUGE_WALL
        r = tube(P.GAUGE_RING_H, od, b, seg=SEG)
        r = r - union([
            bore_lead_in(P.GAUGE_RING_H, b, 0.8, True),
            chamfer_outer(P.GAUGE_RING_H, od, 0.6, True),
            chamfer_outer(0.0, od, 0.5, False),
        ])
        solids.append(r.translate([x, y, 0]))

        # Flag carrying the label, reaching out to that row's rail.
        y_in = od / 2.0 - 1.5
        fl = fillet2d(rect2d(pitch - 1.5, y_out - y_in)
                      .translate((0.0, (y_out + y_in) / 2.0)), 1.5)
        flag = fl.extrude(FLAG_T)

        label = "%.2f" % b if round(b * 100) % 10 else "%.1f" % b
        txt = text_2d(label, P.GAUGE_TEXT_H)
        if not txt.is_empty():
            cut = txt.extrude(P.GAUGE_TEXT_D + 0.2) \
                     .translate([0.0, y_out - P.GAUGE_TEXT_H / 2.0 - 2.2,
                                 FLAG_T - P.GAUGE_TEXT_D])
            flag = flag - cut
        solids.append(flag.translate([x, y, 0]))

    for row, cols in rows.items():
        span = (max(cols) - min(cols)) * pitch + pitch
        solids.append(
            box(span, RAIL_W, FLAG_T, center=False)
            .translate([min(cols) * pitch - pitch / 2.0,
                        -row * row_pitch + y_out - RAIL_W / 2.0, 0.0]))

    # Tie the rows together down the left-hand margin, clear of every ring,
    # so the whole ladder lifts off the plate as one piece instead of as a
    # handful of loose rings that immediately get mixed up.
    for row in range(1, max(rows) + 1):
        solids.append(
            box(RAIL_W, row_pitch, FLAG_T, center=False)
            .translate([min(rows[row]) * pitch - pitch / 2.0,
                        -row * row_pitch + y_out - RAIL_W / 2.0, 0.0]))

    return union(solids)


META = dict(
    name="fit_gauge",
    desc="Ring ladder for dialling in the two hardware bores.",
    orient="FLAT on the plate as generated. No supports.",
)
