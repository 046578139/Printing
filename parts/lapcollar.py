"""01f - Lapped collar. The recorder mount's actual mechanism.

The band wraps past 360 degrees so its two ends lap over each other, stepped
in thickness: the inner arm passes inside the outer one. Each end carries a
finger tab. Squeeze the two tabs together, the lap shortens, and a band of
fixed arc length with less lap is a bigger circle. Slide it on, release.

Why squeezing expands it, when squeezing 01e would have shrunk it
--------------------------------------------------------------
On 01e the tabs sit on the band either side of a gap. Expanding that ring
opens the gap, so the tabs move APART and it has to be spread.

Lap the ends past each other and each tab rides a free END. The ends have
CROSSED - the outer arm's tip has gone past the inner arm's root - so the
angle between the tips IS the lap. Expanding the ring shortens the lap,
which brings the tips, and the tabs on them, together. The motion reverses.

What the thickness step forces
------------------------------
The inner arm's tab has to get out past the outer arm, and radially there is
no way through. So the outer arm stops half way up the band and the inner
arm carries a full-width flange above it, from which its tab projects. The
two tabs end up at different heights - which is not a workaround, it is what
lets them lap past each other instead of butting heads. At full squeeze they
are only a few millimetres apart in plan and would collide if they shared a
height.

    lap 30 deg at rest = 10.3 mm of arc
    squeeze consumes 11.9 deg = 4.1 mm -> bore grows 1.30 mm
    18 deg = 6.2 mm still lapped at full expansion

Print orientation: REAR FACE DOWN, plate face flat. Everything is a
vertical-walled extrusion except the upper flange, which bridges the
0.30 mm sliding gap above the outer arm - a print-in-place clearance, not
an overhang.
"""

import math

import params as P
from lib.solids import circle2d, cyl, poly, round2d, union, SEG
from lib.patterns import cord_ear_2d, pinch_tab_2d
from lib.text3d import text_2d
from manifold3d import Manifold, CrossSection

R_OUT = P.LAP_BORE / 2.0 + P.COL_WALL

# Spatial angles, before the whole band is rotated so the lap sits at LAP_AT.
# The lap zone is [0, LAP_DEG]. The body covers the rest.
#   outer arm : root at LAP_DEG, free end (and its tab) at END_CLEAR
#   inner arm : root at 0,       free end (and its tab) at LAP_DEG - END_CLEAR
A_OUT_TIP = P.LAP_END_CLEAR
A_IN_TIP = P.LAP_DEG - P.LAP_END_CLEAR


def mechanics(bore: float = None, expansion: float = None,
              E: float = 2750.0) -> dict:
    """Curved-beam model of the ring, in two sections in series.

    The body is a full-thickness near-ring; the lap is two thin arms nested
    inside each other. The arms are an order of magnitude more compliant
    (I goes as t^3, and 1.60 against 3.20 is a factor of eight), so most of
    the deflection happens in the lap and that is where the strain has to be
    checked. Treating the whole ring as one thick band would understate it
    badly.
    """
    import numpy as np
    bore = P.LAP_BORE if bore is None else bore
    if expansion is None:
        expansion = P.LAP_INTERF + P.LAP_CLEAR

    r_mean = (bore + P.COL_WALL) / 2.0
    spread = math.pi * expansion            # arc the tabs must travel
    lap_arc = math.radians(P.LAP_DEG) * r_mean

    # Body: near-closed curved cantilever, full wall.
    beta = math.radians((360.0 - P.LAP_DEG) / 2.0)
    phi = np.linspace(0.0, beta, 6000)
    J = float(np.trapezoid((np.cos(phi) - math.cos(beta)) ** 2, phi))
    i_body = P.COL_HEIGHT * P.COL_WALL ** 3 / 12.0

    # Lap arms: each a curved cantilever of the arm section over LAP_DEG.
    # The upper flange restores full wall above the split, so take the
    # inner arm at the full section over the flange's height and the arm
    # section below it; the outer arm is thin over its whole height.
    i_outer = P.LAP_SPLIT_Z * P.LAP_ARM_OUT ** 3 / 12.0
    i_inner = (P.LAP_SPLIT_Z * P.LAP_ARM_IN ** 3 / 12.0
               + (P.COL_HEIGHT - P.LAP_SPLIT_Z) * P.COL_WALL ** 3 / 12.0)

    # Compliance in series: body plus the two arms. The arms are short, so
    # their contribution is a straight cantilever of length lap_arc.
    c_body = (r_mean ** 3 * J) / (E * i_body)
    c_arms = lap_arc ** 3 / (3.0 * E * i_outer) + lap_arc ** 3 / (3.0 * E * i_inner)
    force = (spread / 2.0) / (c_body + c_arms)

    # Peak strain: body crown, and the root of the weaker (outer) arm.
    m_body = force * r_mean
    m_arm = force * lap_arc
    eps_body = m_body * (P.COL_WALL / 2.0) / (E * i_body)
    eps_outer = m_arm * (P.LAP_ARM_OUT / 2.0) / (E * i_outer)
    eps_inner = m_arm * (P.COL_WALL / 2.0) / (E * i_inner)

    # Seated: the bore is forced from the free bore out to the seat.
    rf, rb = bore / 2.0, (bore + P.LAP_INTERF) / 2.0
    seated = (P.COL_WALL / 2.0) * abs(1 / rf - 1 / rb)

    return dict(spread=spread, force=force, lap_arc=lap_arc,
                strain_body=eps_body, strain_arm=eps_outer,
                strain_inner=eps_inner,
                strain=max(eps_body, eps_outer, eps_inner),
                seated=seated,
                lap_rest=P.LAP_DEG,
                lap_open=P.LAP_DEG - math.degrees(spread / r_mean))


def _sector(angle: float, r: float, start: float) -> CrossSection:
    n = max(4, int(SEG * angle / 360.0) + 1)
    pts = [(0.0, 0.0)]
    for i in range(n + 1):
        a = math.radians(start + angle * i / n)
        pts.append((r * math.cos(a), r * math.sin(a)))
    return poly(pts)


def _arc(r_in: float, r_out: float, a0: float, a1: float,
         z0: float, z1: float) -> Manifold:
    """Annular sector solid, r_in..r_out, a0..a1 degrees, z0..z1."""
    ring = circle2d(2 * r_out, SEG) - circle2d(2 * r_in, SEG)
    return (ring ^ _sector(a1 - a0, 4 * r_out, a0)) \
        .extrude(z1 - z0).translate([0.0, 0.0, z0])


def _tab(r_out: float, angle: float, z0: float, z1: float) -> Manifold:
    """Finger tab at `angle`, occupying only z0..z1 so it can lap past the
    other one. Rooted at `angle` and rounded everywhere - these are the most
    snag-prone features on the part and the only ones you handle."""
    prof = pinch_tab_2d(r_out, P.LAP_TAB_PROJ, P.LAP_TAB_W,
                        P.LAP_TAB_HEAD, P.LAP_ROUND).rotate(angle)
    return prof.extrude(z1 - z0).translate([0.0, 0.0, z0])


def _ear(angle: float, r_out: float, label: str = None) -> Manifold:
    """Cord ear: straight out from the band at full boss width, no waist."""
    prof = cord_ear_2d(r_out, P.CORD_RADIUS, P.EAR_BOSS_D,
                       P.EAR_STEM_W, P.EAR_ROUND)
    ear = prof.extrude(P.EAR_T)
    ear = ear - cyl(P.EAR_T + 2.0, P.CORD_HOLE, seg=48) \
        .translate([P.CORD_RADIUS, 0.0, -1.0])
    if label:
        txt = text_2d(label, 2.40)
        if not txt.is_empty():
            ear = ear - txt.rotate(90).extrude(0.8) \
                .translate([r_out + 1.0, 0.0, P.EAR_T - P.LAYER * 2])
    return ear.rotate([0, 0, angle])


def band(bore: float = None) -> Manifold:
    """The lapped band alone, lap zone at angles [0, LAP_DEG]."""
    bore = P.LAP_BORE if bore is None else bore
    r_b = bore / 2.0
    r_o = r_b + P.COL_WALL
    r_i1 = r_b + P.LAP_ARM_IN                # outside of the inner arm
    r_o1 = r_i1 + P.LAP_SLIDE                # inside of the outer arm
    h = P.COL_HEIGHT
    zs = P.LAP_SPLIT_Z

    # Body: full wall, full height, everything outside the lap zone.
    parts = [_arc(r_b, r_o, P.LAP_DEG, 360.0, 0.0, h)]

    # Inner arm: rooted at 0, free at A_IN_TIP. Thin and full height, with a
    # full-width flange above the sliding gap - that flange is what carries
    # its tab out past the outer arm.
    parts.append(_arc(r_b, r_i1, 0.0, A_IN_TIP, 0.0, h))
    parts.append(_arc(r_i1, r_o, 0.0, A_IN_TIP, zs + P.LAP_SLIDE_Z, h))

    # Outer arm: rooted at LAP_DEG, free at A_OUT_TIP. Lower half only, so
    # the inner arm's flange can ride over it.
    parts.append(_arc(r_o1, r_o, A_OUT_TIP, P.LAP_DEG, 0.0, zs))

    # Tabs, one on each free end, at the two different heights.
    parts.append(_tab(r_o, A_OUT_TIP, 0.0, zs))
    parts.append(_tab(r_o, A_IN_TIP, zs + P.LAP_SLIDE_Z, h))
    return union(parts)


def build(bore: float = None, label: str = None):
    bore = P.LAP_BORE if bore is None else bore
    r_out = bore / 2.0 + P.COL_WALL

    # Put the lap at the top so the cord ears keep 3 and 9 o'clock.
    part = band(bore).rotate([0, 0, P.LAP_AT - P.LAP_DEG / 2.0])
    part = union([part, _ear(0.0, r_out, label), _ear(180.0, r_out, label)])

    # Re-cut the bore last: the ears overlap into it, and the bore is the one
    # dimension on this part that has to come out exactly as designed.
    part = part - cyl(P.COL_HEIGHT + 4.0, bore, seg=SEG).translate([0, 0, -2.0])
    return part


META = dict(
    name="01f_collar_lap",
    desc="Lapped ring, 390 deg. The ends cross, so SQUEEZING the two tabs "
         "together expands it. Slide it over the bezel and release.",
    orient="Rear face down - already oriented. No supports.",
    hardware="None. Fits BEFORE the housing.",
)
