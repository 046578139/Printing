#!/usr/bin/env python3
"""Top view of a build plate, as an SVG. Look before you print.

    python3 tools/plate_preview.py plate_pair

A plate that validates can still be laid out badly - a part hanging off an
edge, or two footprints that clear by a hair. This draws the real
silhouettes (manifold's own top projection, not bounding boxes) on the bed
outline, so the layout can be checked by eye in a second.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import build as bm
from parts import plate

BED = 256.0
PAD = 12.0
COLORS = ["#4c72b0", "#dd8452", "#55a868", "#c44e52", "#8172b3",
          "#937860", "#da8bc3", "#8c8c8c"]


def svg(key, path=None):
    m = bm.PARTS[key][0]()
    shells = m.decompose()
    w = h = BED + 2 * PAD

    def tx(x, y):                       # bed centre to SVG, y flipped
        return (x + BED / 2.0 + PAD, BED / 2.0 - y + PAD)

    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%g" height="%g" '
           'viewBox="0 0 %g %g">' % (w, h, w, h),
           '<rect width="%g" height="%g" fill="#111"/>' % (w, h),
           '<rect x="%g" y="%g" width="%g" height="%g" fill="#1b1b1b" '
           'stroke="#555" stroke-dasharray="4 3"/>' % (PAD, PAD, BED, BED)]

    for i, sh in enumerate(shells):
        col = COLORS[i % len(COLORS)]
        d = []
        for ring in sh.project().to_polygons():
            pts = " ".join("%.2f,%.2f" % tx(p[0], p[1]) for p in ring)
            d.append('<polygon points="%s"/>' % pts)
        out.append('<g fill="%s" fill-opacity="0.55" stroke="%s" '
                   'stroke-width="0.6" fill-rule="evenodd">%s</g>'
                   % (col, col, "".join(d)))
        b = sh.bounding_box()
        cx, cy = tx((b[0] + b[3]) / 2.0, (b[1] + b[4]) / 2.0)
        out.append('<text x="%.1f" y="%.1f" fill="#fff" font-size="7" '
                   'font-family="monospace" text-anchor="middle">%d</text>'
                   % (cx, cy, i + 1))

    bb = m.bounding_box()
    out.append('<text x="%g" y="%g" fill="#888" font-size="8" '
               'font-family="monospace">%s  -  %d parts  -  %.1f x %.1f mm '
               'on a %.0f mm bed</text>'
               % (PAD, h - 3, bm.FILENAME[key], len(shells),
                  bb[3] - bb[0], bb[4] - bb[1], BED))
    out.append("</svg>")

    path = path or os.path.join(os.path.dirname(bm.OUT), "stl",
                                bm.FILENAME[key] + ".svg")
    open(path, "w").write("\n".join(out))
    return path, len(shells)


if __name__ == "__main__":
    keys = sys.argv[1:] or [k for k in bm.PARTS if k.startswith("plate")]
    for k in keys:
        p, n = svg(k)
        print("  %-24s %d parts  ->  %s" % (k, n, p))
