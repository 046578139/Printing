"""01e - Pinch collar. The one modelled on the recorder mount.

A nearly-closed ring with two small tabs flanking a narrow gap. Pull the
tabs apart, the ring expands, slide it down over the objective bezel, let
go. The bore does the gripping; the tabs are handles, not springs.

Why it can sit at 340 degrees when the push-on ring was capped at 230:
a push-on ring has to let the barrel through the CHORD between its tips,
which collapses as the wrap grows. Opened by hand and fitted axially, the
gap only has to open by pi x expansion - which is independent of wrap. So
more wrap costs nothing and buys a ring that looks and behaves closed.

    340 deg, expand 1.30 -> gap opens 4.08 mm, 0.37 % strain, ~5 N at the tabs
    230 deg, push-on     -> gap opens 5.65 mm, 0.75 % strain, ~13 N

ASSEMBLY ORDER IS FIXED. At this wrap the ring cannot pass over the 43.7 mm
housing, so it goes on FIRST, over the bare bezel. Removing it means pulling
the housing.

Print orientation: REAR FACE DOWN, plate face flat. The band then flexes
within its layers and never tests layer adhesion.
"""

import math

import params as P
from lib.solids import (circle2d, cyl, poly, round2d, union,
                        prism_chamfered, SEG)
from lib.patterns import cord_ear_2d, pinch_tab_2d
from lib.text3d import text_2d
from manifold3d import Manifold, CrossSection

R_OUT = P.PINCH_BORE / 2.0 + P.COL_WALL
GAP_DEG = 360.0 - P.PINCH_WRAP


def mechanics(bore: float = None, wrap: float = None,
              expansion: float = None, E: float = 2750.0) -> dict:
    """Curved-beam model. Arc length is fixed, so growing the bore by X
    opens the gap by pi*X regardless of wrap."""
    import numpy as np
    bore = P.PINCH_BORE if bore is None else bore
    wrap = P.PINCH_WRAP if wrap is None else wrap
    if expansion is None:
        expansion = P.PINCH_INTERF + P.PINCH_CLEAR

    spread = math.pi * expansion
    beta = math.radians(wrap / 2.0)
    r_mean = (bore + P.COL_WALL) / 2.0
    phi = np.linspace(0.0, beta, 6000)
    J = float(np.trapezoid((np.cos(phi) - math.cos(beta)) ** 2, phi))

    strain = (spread / 2) * P.COL_WALL * (1 - math.cos(beta)) / (2 * r_mean ** 2 * J)
    inertia = P.COL_HEIGHT * P.COL_WALL ** 3 / 12.0
    force = (spread / 2) * E * inertia / (r_mean ** 3 * J)
    gap_arc = math.radians(360.0 - wrap) * r_mean
    return dict(spread=spread, strain=strain, force=force,
                gap_closed=gap_arc, gap_open=gap_arc + spread)


def _sector(angle: float, r: float, start: float) -> CrossSection:
    n = max(4, int(SEG * angle / 360.0) + 1)
    pts = [(0.0, 0.0)]
    for i in range(n + 1):
        a = math.radians(start + angle * i / n)
        pts.append((r * math.cos(a), r * math.sin(a)))
    return poly(pts)


def _ear(angle: float, r_out: float = None, label: str = None) -> Manifold:
    r_out = R_OUT if r_out is None else r_out
    prof = cord_ear_2d(r_out, P.CORD_RADIUS, P.EAR_BOSS_D,
                       P.EAR_STEM_W, P.EAR_ROUND)
    ear = prism_chamfered(prof, P.EAR_T, c_bot=0.0, c_top=P.PINCH_EDGE)
    ear = ear - cyl(P.EAR_T + 2.0, P.CORD_HOLE, seg=48) \
        .translate([P.CORD_RADIUS, 0.0, -1.0])
    if label:
        txt = text_2d(label, 2.40)
        if not txt.is_empty():
            ear = ear - txt.rotate(90).extrude(0.8) \
                .translate([r_out + 1.0, 0.0, P.EAR_T - P.LAYER * 2])
    return ear.rotate([0, 0, angle])


def band_2d(bore: float = None) -> CrossSection:
    """Band, gap and both tabs as ONE 2D profile.

    Built together rather than welded together so the whole thing can be
    round2d-ed in a single pass. That is not cosmetic: unioning a tab onto
    the band as a separate solid leaves a sharp internal corner at the root,
    and every newton you put into a tab enters the band through that corner.
    A sharp notch on a part designed to be flexed is where it cracks. The
    same pass rounds the two ends of the gap, which are the other place a
    spread ring concentrates stress.
    """
    bore = P.PINCH_BORE if bore is None else bore
    r_out = bore / 2.0 + P.COL_WALL
    od = 2 * r_out

    ring = circle2d(od, SEG) - circle2d(bore, SEG)

    # Narrow gap, cut before the tabs so they are not clipped.
    big = od + 2 * P.PINCH_TAB_PROJ + 24.0
    ring = ring - _sector(GAP_DEG, big, P.PINCH_GAP_AT - GAP_DEG / 2.0)

    # Tabs sit just inside each tip so they have a full-width root.
    off = math.degrees((P.PINCH_TAB_W / 2.0) / r_out)
    tab = pinch_tab_2d(r_out, P.PINCH_TAB_PROJ, P.PINCH_TAB_W,
                       P.PINCH_TAB_HEAD, P.PINCH_ROUND)
    prof = (ring
            + tab.rotate(P.PINCH_GAP_AT - GAP_DEG / 2.0 - off)
            + tab.rotate(P.PINCH_GAP_AT + GAP_DEG / 2.0 + off))
    return round2d(prof, P.PINCH_ROOT_R)


def build(bore: float = None, label: str = None):
    bore = P.PINCH_BORE if bore is None else bore

    # c_bot stays 0: the bottom is the plate face and a chamfer there is what
    # made every ring in the first round print ragged for its first layers.
    # c_top breaks the band, the bore and the tab tops in one operation.
    part = prism_chamfered(band_2d(bore), P.COL_HEIGHT,
                           c_bot=0.0, c_top=P.PINCH_EDGE)
    r_out = bore / 2.0 + P.COL_WALL
    part = union([part, _ear(0.0, r_out, label),
                  _ear(180.0, r_out, label)])

    # Re-cut the bore last: the ears overlap into it, and the bore is the one
    # dimension on this part that has to come out exactly as designed.
    part = part - cyl(P.COL_HEIGHT + 4.0, bore, seg=SEG).translate([0, 0, -2.0])
    return part


META = dict(
    name="01e_collar_pinch",
    desc="Nearly-closed ring, 340 deg. Pull the two tabs apart, slide it "
         "over the bezel, release. No hardware, no tools.",
    orient="Rear face down - already oriented. No supports.",
    hardware="None. Fits BEFORE the housing.",
)
