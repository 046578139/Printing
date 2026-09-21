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
no way through. So the outer arm stops at 6.5 mm and the inner arm carries a
full-width flange above it, from which its tab projects.

That leaves the upper tab starting half way up the band with nothing at all
underneath it outboard of the OD - a fin hanging 6.8 mm in the air, which a
slicer flags as a floating cantilever and is right to. Outboard of the band
nothing is in the way, so the tab carries straight down to the plate there,
clear of the outer arm by the same 0.40 mm the arms use.

Which is why the lap is 50 degrees. Tabs at different heights could lap past
each other; tabs that both reach the bed cannot, so they have to stay apart.
And a tab may not sit ON its arm's free end - it hangs half its width past it
and welds that arm to the body. So each is inset 7 deg, which costs another
14 deg of separation. What is left keeps the heads 3.7 mm apart even fully
squeezed. Insetting does not change the mechanism: the arms are rigid, so a
tab turns with its arm by the same angle wherever it sits on it.

    lap 50 deg at rest = 17.1 mm of arc
    squeeze consumes 11.9 deg = 4.1 mm -> bore grows 1.30 mm
    38 deg = 13.0 mm still lapped at full expansion
    2.9 N at the tabs, 0.66 % peak strain (2.3x margin in PLA)

Three ways this part can be built welded solid, all of which still give one
watertight shell with the correct bore:

  * a tab stem reaching 3 mm inside the OD crosses the 0.40 mm slide gap
  * a tab centred on a free end overhangs it into the body
  * an arm root that merely BUTTS the body on a coplanar radial face never
    welds to it at all - the part held together only through the two
    fusions above, and fixing them is what exposed it

Each of those is caught by sweeping a probe along the whole feature. None is
caught by probing one point, or by any dimension, volume or topology check.

Print orientation: REAR FACE DOWN, plate face flat. Every feature either
stands on the plate or bridges the 0.30 mm sliding gap above the outer arm -
a print-in-place clearance, not an overhang. No supports, no floating
cantilevers.
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
# Tabs sit INSIDE their own arm, not centred on its tip. A tab centred on the
# free end hangs half its width past it and welds that arm to the body.
A_TAB_OUT = A_OUT_TIP + P.LAP_TAB_INSET
A_TAB_IN = A_IN_TIP - P.LAP_TAB_INSET


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


def _tab(r_out: float, angle: float, z0: float, z1: float,
         root_r: float = None, column_r: float = None) -> Manifold:
    """Finger tab at `angle`. Rounded everywhere - these are the most
    snag-prone features on the part and the only ones you handle.

    `column_r` carries the tab down to the plate outboard of that radius.
    The upper tab's root has to start above the outer arm to get out past
    it, and outboard of the band there is nothing underneath at all - so
    without this the tab is a fin hanging 6.8 mm in the air, which the
    slicer flags as a floating cantilever and is right to. Outboard of
    column_r nothing is in the way, so the tab simply stands on the bed and
    is a stiffer thing to push on for it.
    """
    prof = pinch_tab_2d(r_out, P.LAP_TAB_PROJ, P.LAP_TAB_W,
                        P.LAP_TAB_HEAD, P.LAP_ROUND)
    # CLIP THE ROOT. The stem reaches 3 mm inside the band OD so a tab on a
    # plain ring has something to root into - but on a lapped ring that 3 mm
    # crosses the 0.40 mm slide gap and welds the two arms together. Each tab
    # may only reach as far in as its OWN arm goes.
    if root_r:
        prof = prof - circle2d(2.0 * root_r, SEG)
    prof = prof.rotate(angle)
    tab = prof.extrude(z1 - z0).translate([0.0, 0.0, z0])
    if column_r is not None and z0 > 0.0:
        # Overlap into the tab above; a coplanar butt does not weld.
        col = (prof - circle2d(2.0 * column_r, SEG)).extrude(z0 + 1.0)
        tab = union([tab, col])
    return tab


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
    parts.append(_arc(r_b, r_i1, -P.LAP_WELD, A_IN_TIP, 0.0, h))
    parts.append(_arc(r_i1, r_o, -P.LAP_WELD, A_IN_TIP,
                      zs + P.LAP_SLIDE_Z, h))

    # Outer arm: rooted at LAP_DEG, free at A_OUT_TIP. Lower half only, so
    # the inner arm's flange can ride over it.
    parts.append(_arc(r_o1, r_o, A_OUT_TIP, P.LAP_DEG + P.LAP_WELD,
                      0.0, zs))

    # Tabs, one on each free end, at the two different heights.
    parts.append(_tab(r_o, A_TAB_OUT, 0.0, zs, root_r=r_o1))
    # Clear of the outer arm by the same slide gap the arms use, so the
    # column can pass it without fusing.
    parts.append(_tab(r_o, A_TAB_IN, zs + P.LAP_SLIDE_Z, h,
                      column_r=r_o + P.LAP_SLIDE))
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
