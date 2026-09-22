#!/usr/bin/env python3
"""Trace a bitmap into a polygon set for the cap's centre mark.

Run once when the artwork changes; it writes lib/mark_data.py, which the
build imports. The build must not depend on an image file or on PIL.

    python3 tools/trace_mark.py <image.png> --height 16.0
    python3 tools/trace_mark.py --text FUCK --width 34 --out mark_fuck

Why an opening pass is not optional
-----------------------------------
Blackletter is full of hairline flourishes. On the supplied P, 18 % of the
glyph's area sits in strokes under one extrusion width at any size that fits
the cap - and a debossed groove narrower than the nozzle is not a fine
groove, it is no groove at all. The slicer silently omits it, exactly as it
omitted the first kill flash's cell walls.

So the mask is morphologically OPENED at the minimum printable stroke first.
That deletes what could never have printed and leaves the bold strokes at
their true width, which is an honest representation of what will come off
the plate rather than a drawing that only looks right on screen.
"""

import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage


def render_text(s, font_path, px=400):
    """Render text to a mask at high resolution.

    Reusing the image path rather than pulling glyph outlines out of the
    font: the opening pass below is the thing that actually matters, and it
    wants a raster anyway. A 400 px cap height is ~30 px per printed 0.1 mm
    at the sizes used here, so nothing is lost to the raster.
    """
    from PIL import ImageFont, ImageDraw
    f = ImageFont.truetype(font_path, px)
    tmp = Image.new("L", (10, 10))
    box = ImageDraw.Draw(tmp).textbbox((0, 0), s, font=f)
    w, h = box[2] - box[0] + 2 * px // 5, box[3] - box[1] + 2 * px // 5
    img = Image.new("L", (w, h), 0)
    ImageDraw.Draw(img).text((px // 5 - box[0], px // 5 - box[1]), s,
                             font=f, fill=255)
    return img


def load_mask(path):
    a = np.asarray(Image.open(path).convert("L"))
    m = a > 128
    if m.mean() > 0.5:                      # dark glyph on light ground
        m = ~m
    ys, xs = np.nonzero(m)
    return m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def disc(r):
    n = int(np.ceil(r))
    y, x = np.mgrid[-n:n + 1, -n:n + 1]
    return (x * x + y * y) <= r * r


def open_to(mask, px_per_mm, min_stroke):
    """Drop every stroke thinner than `min_stroke` mm, keep the rest at size."""
    r = max(1.0, min_stroke / 2.0 * px_per_mm)
    k = disc(r)
    out = ndimage.binary_dilation(ndimage.binary_erosion(mask, k), k)
    # Opening can leave crumbs; drop anything under a printable blob.
    lab, n = ndimage.label(out)
    if n:
        area = ndimage.sum(out, lab, range(1, n + 1))
        keep = np.isin(lab, 1 + np.nonzero(area >= (r * r * 4.0))[0])
        out = keep
    return out


def runs(mask):
    """Run-length rectangles, one per horizontal run. Fed to a single
    CrossSection with a positive fill rule, they union for free - far
    cheaper and far more robust than chaining thousands of booleans."""
    out = []
    h, w = mask.shape
    for y in range(h):
        row = mask[y]
        d = np.diff(np.concatenate(([0], row.view(np.int8), [0])))
        for x0, x1 in zip(np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]):
            out.append((int(x0), int(y), int(x1), int(y + 1)))
    return out


FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def main(argv):
    def opt(name, default=None, cast=float):
        return cast(argv[argv.index(name) + 1]) if name in argv else default

    text = opt("--text", None, str)
    src = text if text else argv[1]
    height = opt("--height")
    width = opt("--width")
    min_stroke = opt("--min", 0.55)
    out_name = opt("--out", "mark_data", str)
    font = opt("--font", FONT, str)

    if text:
        img = render_text(text, font)
        a = np.asarray(img)
        m = a > 128
        ys, xs = np.nonzero(m)
        mask = m[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    else:
        mask = load_mask(src)
    h, w = mask.shape
    # Text is wide, not tall, so it is normally sized by WIDTH; the traced
    # artwork is tall and narrow and is sized by height. Whichever is given.
    if width is not None:
        px_per_mm = w / width
        height = h / px_per_mm
    else:
        height = height if height is not None else 16.0
        px_per_mm = h / height
    before = mask.sum()
    mask = open_to(mask, px_per_mm, min_stroke)
    ys, xs = np.nonzero(mask)
    mask = mask[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h2, w2 = mask.shape

    print("source      %d x %d px" % (w, h))
    print("target      %.2f mm tall  ->  %.1f px/mm" % (height, px_per_mm))
    print("opened at   %.2f mm minimum stroke" % min_stroke)
    print("            %.1f %% of the glyph area removed as unprintable"
          % (100.0 * (1.0 - mask.sum() / before)))
    print("result      %.2f x %.2f mm" % (w2 / px_per_mm, h2 / px_per_mm))

    r = runs(mask)
    print("            %d run rectangles" % len(r))

    # Emit in mm, centred, y flipped (image rows run downward).
    cx, cy = w2 / 2.0, h2 / 2.0
    rects = [(round((x0 - cx) / px_per_mm, 4), round((cy - y1) / px_per_mm, 4),
              round((x1 - cx) / px_per_mm, 4), round((cy - y0) / px_per_mm, 4))
             for x0, y0, x1, y1 in r]

    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(here, "lib", out_name + ".py")
    with open(out, "w") as f:
        f.write('"""Traced centre mark - GENERATED by tools/trace_mark.py.\n\n'
                'Do not edit by hand. Re-run the tracer if the artwork or the\n'
                'mark size changes.\n\n'
                '    source     %s\n'
                '    height     %.2f mm\n'
                '    width      %.2f mm\n'
                '    opened at  %.2f mm minimum stroke\n'
                '"""\n\n' % (os.path.basename(src), height,
                             w2 / px_per_mm, min_stroke))
        f.write("MARK_HEIGHT = %.4f\nMARK_WIDTH = %.4f\nMIN_STROKE = %.4f\n\n"
                % (height, w2 / px_per_mm, min_stroke))
        f.write("# (x0, y0, x1, y1) horizontal runs, millimetres, centred on the origin\n")
        f.write("RUNS = [\n")
        for t in rects:
            f.write("    (%.4f, %.4f, %.4f, %.4f),\n" % t)
        f.write("]\n")
    print("wrote       %s" % os.path.relpath(out, here))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
