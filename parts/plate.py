"""10 - Build plates. A whole set arranged on the bed, as one STL.

One file, one drag onto the plate, everything laid out and oriented. The
parts are separate shells inside it, not welded together - manifold's union
of disjoint solids keeps them disjoint - so the slicer sees the same
geometry it would have seen from the individual files.

Two things a combined plate CANNOT do, and both matter here:

  * Colour. An STL carries geometry and nothing else. The cap inlays are
    separate files precisely so the slicer can hand each one a different
    filament; merged into a plate they are just more plastic. Multicolour
    stays on the individual files.

  * Per-part settings, unless you load it as multiple parts. The kill flash
    wants 1 wall loop, 0 top/bottom and thin-wall detection ON, and the rest
    of the set very much does not. Answer YES to "multi-part object detected,
    load as a single object with multiple parts?" and you can right-click the
    insert and set them; answer no and the whole plate gets one set of
    settings and the insert comes out a disc full of holes.

Spacing is 8 mm, which is a brim's worth. The cap needs one - it is a 52 mm
flat plate with a thin edge chamfer and it will lift at a corner otherwise.
"""

import params as P
from lib.solids import union

GAP = 8.0        # a brim's worth between footprints
WIDTH = 210.0    # usable bed width to pack into; the H2C plate is 256


def pack(boxes, gap: float = GAP, width: float = WIDTH) -> list:
    """Shelf-pack (w, d) footprints. Returns one (dx, dy) per box, in the
    order given, with the whole arrangement centred on the origin.

    Rows are filled deepest-first so each shelf comes out level and the
    wasted strip above it is as thin as it can be. Eight parts is not a
    problem that wants a real bin packer.
    """
    order = sorted(range(len(boxes)), key=lambda i: -boxes[i][1])
    place = [None] * len(boxes)
    x = y = row_d = 0.0
    for i in order:
        w, d = boxes[i]
        if x > 0.0 and x + w > width:        # wrap to a new shelf
            y += row_d + gap
            x, row_d = 0.0, 0.0
        place[i] = (x, y)
        x += w + gap
        row_d = max(row_d, d)

    span_x = max(place[i][0] + boxes[i][0] for i in range(len(boxes)))
    span_y = y + row_d
    return [(px - span_x / 2.0, py - span_y / 2.0) for px, py in place]


def build(items: list, gap: float = GAP, width: float = WIDTH):
    """items: [(oriented Manifold, count)]. Every part keeps the orientation
    it was built in - a plate that has to be rearranged by hand is worse
    than no plate at all."""
    flat = [m for m, n in items for _ in range(n)]
    bbs = [m.bounding_box() for m in flat]
    boxes = [(b[3] - b[0], b[4] - b[1]) for b in bbs]
    out = []
    for m, b, (dx, dy) in zip(flat, bbs, pack(boxes, gap, width)):
        # Corner to the shelf origin, and z untouched: every part was
        # already sitting on z=0 and has to stay there.
        out.append(m.translate([dx - b[0], dy - b[1], 0.0]))
    return union(out)


def _meta(name, what, note=""):
    return dict(
        name=name,
        desc="ONE FILE, whole plate. %s Parts are separate shells, laid out "
             "and oriented; drop it on the bed and slice. %s" % (what, note),
        orient="Everything is already oriented. Do NOT rotate the plate.",
        hardware="Brim on. Answer YES to the slicer's multi-part prompt if "
                 "you want per-part settings.",
    )


META_SET = _meta(
    "10_plate_set", "One complete pod: cinch collar, housing, kill flash, cap.",
    "The kill flash needs thin-wall settings the others do not - see "
    "docs/PRINTING.md.")
META_PAIR = _meta(
    "11_plate_pair", "A full binocular set: two of each of the four parts.",
    "The kill flash needs thin-wall settings the others do not - see "
    "docs/PRINTING.md.")
META_CAPS = _meta(
    "12_plate_caps_FUCK_YOU", 'Both custom caps, "FUCK" and "YOU".',
    "Single colour. For the two-tone face use 04b/04c and their inlays.")
