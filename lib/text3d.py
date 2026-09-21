"""Minimal seven-segment numerals for moulded-in gauge labels.

Only digits and '.' are needed; a seven-segment face stays legible when
debossed 0.6 mm into PETG and survives the move to carbon-filled filament,
where a fine outline font would fill in.
"""

import manifold3d as m3d
from manifold3d import CrossSection, Manifold

from .solids import rect2d, fillet2d, union

# A B C D E F G  ->  top, upper-right, lower-right, bottom, lower-left,
#                    upper-left, middle
_SEGS = {
    "0": "ABCDEF", "1": "BC",     "2": "ABGED",  "3": "ABGCD",  "4": "FGBC",
    "5": "AFGCD",  "6": "AFGECD", "7": "ABC",    "8": "ABCDEFG", "9": "ABCDFG",
}


def _glyph(ch: str, h: float, t: float) -> CrossSection:
    w = h * 0.58
    if ch == ".":
        return fillet2d(rect2d(t, t).translate((t / 2, t / 2)), t * 0.3)
    if ch == "-":
        return fillet2d(rect2d(w - t, t).translate((w / 2, h / 2)), t * 0.3)
    if ch == " ":
        return CrossSection()

    half = h / 2.0
    hz = w - t          # length of horizontal bars
    vt = half - t       # length of vertical bars
    place = {
        "A": (rect2d(hz, t), (w / 2, h - t / 2)),
        "G": (rect2d(hz, t), (w / 2, half)),
        "D": (rect2d(hz, t), (w / 2, t / 2)),
        "F": (rect2d(t, vt), (t / 2, half + vt / 2 + t / 2 - t / 2)),
        "B": (rect2d(t, vt), (w - t / 2, half + vt / 2 + t / 2 - t / 2)),
        "E": (rect2d(t, vt), (t / 2, t / 2 + vt / 2)),
        "C": (rect2d(t, vt), (w - t / 2, t / 2 + vt / 2)),
    }
    on = _SEGS.get(ch.upper())
    if on is None:
        return CrossSection()
    bars = [place[s][0].translate(place[s][1]) for s in on]
    return fillet2d(CrossSection.batch_boolean(bars, m3d.OpType.Add), t * 0.22)


def text_2d(s: str, h: float, t: float = None, center: bool = True) -> CrossSection:
    """Lay out `s` at cap-height `h`. Returns a CrossSection on the XY plane."""
    t = t if t else h * 0.20
    w = h * 0.58
    adv = {".": t * 1.9, " ": w * 0.6}
    x = 0.0
    out, total = [], 0.0
    for ch in s:
        g = _glyph(ch, h, t)
        if not g.is_empty():
            out.append(g.translate((x, 0.0)))
        step = adv.get(ch, w) + t * 0.85
        x += step
    total = x - t * 0.85
    res = CrossSection.batch_boolean(out, m3d.OpType.Add) if out else CrossSection()
    if center and not res.is_empty():
        res = res.translate((-total / 2.0, -h / 2.0))
    return res


def text_3d(s: str, h: float, depth: float, t: float = None) -> Manifold:
    cs = text_2d(s, h, t)
    return cs.extrude(depth) if not cs.is_empty() else Manifold()
