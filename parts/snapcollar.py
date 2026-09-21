"""01c - Snap-fit retention collar (no tools).

An alternative to the screw-clamp collar: a split C-ring that flexes out of
round, passes over the barrel, and springs back around it. Same cord ears in
the same places, so it is a drop-in swap for testing.

The trade against the screw clamp is not about strength, it is about creep.
A screw clamp holds by a preload you can re-tighten; a snap ring holds by a
sustained elastic strain, and every polymer here stress-relaxes. It will be
tightest on the day you fit it.

Mechanics
---------
Installation: the narrowest point the barrel must pass is the CHORD between
the two tips, so the tips have to spread by (barrel - chord). Peak bending
strain is at the crown, opposite the gap. Both are computed below rather
than guessed, because "it felt about right in PLA" does not transfer to a
carbon-filled resin with a third of the elongation.

Print orientation: REAR FACE DOWN, same as the screw collar. The band then
bends WITHIN its layers rather than across them, so installation loads X-Y
strength and never tests layer adhesion - which is the whole reason this
part is printable at all.
"""

import math

import numpy as np

import params as P
from lib.solids import (tube, cyl, poly, rect2d, fillet2d, round2d, union,
                        SEG, bore_lead_in, chamfer_outer)
from lib.text3d import text_2d
from manifold3d import Manifold, CrossSection


def mechanics(barrel: float = None, wall: float = None, wrap: float = None,
              interference: float = None, mode: str = "radial",
              clear: float = None, height: float = None,
              E: float = 2750.0) -> dict:
    """Curved-beam model of the ring. Returns spreads, strains and tip force.

    Each arm is treated as a curved cantilever built in at the crown and
    loaded at the tip (Castigliano). `install` is the transient strain while
    the ring is fitted; `seated` is the sustained strain that provides grip -
    and the one that creeps.

    Two install modes, and the difference between them is the whole design:

      "radial"  pushed straight on, the BARREL forces the gap open. The
                barrel has to pass the chord between the tips, so the spread
                needed explodes past about 240 degrees of wrap.
      "axial"   expanded by hand and slid on, circlip fashion. The gap only
                has to open by pi x expansion, which is nearly independent of
                wrap - so the ring can wrap much further for LESS strain.
    """
    barrel = P.OBJ_COLLAR_OD if barrel is None else barrel
    wall = P.COL_WALL if wall is None else wall
    wrap = P.SNAP_WRAP if wrap is None else wrap
    interference = P.SNAP_INTERF if interference is None else interference
    clear = P.SNAP_LEVER_CLEAR if clear is None else clear
    height = P.COL_HEIGHT if height is None else height

    d_free = barrel - interference
    g = math.radians((360.0 - wrap) / 2.0)
    chord = d_free * math.sin(g)

    if mode == "axial":
        # Arc length is fixed, so expanding the bore by X opens the gap by
        # pi * X. Expand past the barrel by `clear` so it will slide.
        spread = math.pi * (interference + clear)
    else:
        spread = barrel - chord

    beta = math.radians(wrap / 2.0)
    r_mean = (d_free + wall) / 2.0
    phi = np.linspace(0.0, beta, 4000)
    J = float(np.trapezoid((np.cos(phi) - math.cos(beta)) ** 2, phi))

    install = (spread / 2) * wall * (1 - math.cos(beta)) / (2 * r_mean ** 2 * J)
    inertia = height * wall ** 3 / 12.0
    tip_force = (spread / 2) * E * inertia / (r_mean ** 3 * J)

    # Seated: the bore is forced from d_free out to the barrel, so the band's
    # curvature changes. eps = (t/2) * |1/Rf - 1/Rb|
    rf, rb = d_free / 2.0, barrel / 2.0
    seated = (wall / 2.0) * abs(1 / rf - 1 / rb)

    return dict(barrel=barrel, free_bore=d_free, chord=chord, spread=spread,
                install=install, seated=seated, tip_force=tip_force,
                mode=mode, wrap=wrap, J=J, r_mean=r_mean)


def _sector(angle: float, r: float, start: float) -> CrossSection:
    """Pie sector CrossSection, `angle` degrees wide, beginning at `start`."""
    n = max(4, int(SEG * angle / 360.0) + 1)
    pts = [(0.0, 0.0)]
    for i in range(n + 1):
        a = math.radians(start + angle * i / n)
        pts.append((r * math.cos(a), r * math.sin(a)))
    return poly(pts)


def _ear(angle: float, r_out: float, ear_proj: float,
         label: str = None) -> Manifold:
    x0, x1 = r_out - 2.5, r_out + ear_proj
    prof = fillet2d(rect2d(x1 - x0, P.EAR_W)
                    .translate(((x0 + x1) / 2.0, 0.0)), P.EAR_FILLET)
    ear = prof.extrude(P.EAR_T)
    hole = cyl(P.EAR_T + 2.0, P.CORD_HOLE, seg=48) \
        .translate([P.CORD_RADIUS, 0.0, -1.0])
    ear = ear - hole

    # A sweep of five rings 0.4 mm apart is unidentifiable once it is off
    # the plate, so each one carries its own bore size.
    if label:
        txt = text_2d(label, 2.60)
        if not txt.is_empty():
            ear = ear - txt.rotate(90).extrude(0.8) \
                .translate([x0 + (x1 - x0) * 0.33, 0.0, P.EAR_T - 0.5])
    return ear.rotate([0, 0, angle])


def _paddle(r_out):
    """Finger paddle: a radial stem with a wider head your fingertip sits on.

    Built at angle 0 and rotated to a tip; the head is what makes the ring
    openable by hand at all, since a bare band this size gives a fingertip
    nothing to pull against.
    """
    stem = rect2d(P.LEVER_PROJ + 2.0, P.LEVER_W) \
        .translate((r_out + P.LEVER_PROJ / 2.0 - 1.0, 0.0))
    head = rect2d(P.LEVER_PAD_T, P.LEVER_PAD_W) \
        .translate((r_out + P.LEVER_PROJ - P.LEVER_PAD_T / 2.0, 0.0))
    return round2d(stem + head, P.LEVER_ROUND)


def build_lever(bore: float = None, label: str = None):
    """01d - circlip-style collar, expanded by hand and slid on axially.

    Wraps SNAP_LEVER_WRAP, far past what could ever be pushed on radially.
    Because the barrel never has to force the gap, the ring can capture much
    more of the circumference and still take LESS strain to fit than the
    push-on version.
    """
    bore = P.SNAP_LEVER_BORE if bore is None else bore
    r_out = bore / 2.0 + P.COL_WALL
    od = 2 * r_out
    ear_proj = P.CORD_RADIUS + P.CORD_HOLE / 2 + P.CORD_EDGE_WALL - r_out
    gap_deg = 360.0 - P.SNAP_LEVER_WRAP

    band = tube(P.COL_HEIGHT, od, bore)

    # Cut the gap BEFORE the paddles go on, so the paddles are not clipped.
    big = od + 2 * P.LEVER_PROJ + 20.0
    gap = _sector(gap_deg, big, 270.0 - gap_deg / 2.0) \
        .extrude(P.COL_HEIGHT + 4.0).translate([0, 0, -2.0])
    band = band - gap

    # Sit each paddle just inside its tip so it has a full-width root.
    off = math.degrees((P.LEVER_W / 2.0) / r_out)
    pad = _paddle(r_out).extrude(P.COL_HEIGHT)
    paddles = [pad.rotate([0, 0, 270.0 - gap_deg / 2.0 - off]),
               pad.rotate([0, 0, 270.0 + gap_deg / 2.0 + off])]

    part = union([band] + paddles
                 + [_ear(0.0, r_out, ear_proj, label),
                    _ear(180.0, r_out, ear_proj, label)])

    part = part - cyl(P.COL_HEIGHT + 4.0, bore, seg=SEG).translate([0, 0, -2.0])
    # Top edge breaks only - the bottom is the plate face. See params.py.
    part = part - union([
        bore_lead_in(P.COL_HEIGHT, bore, 1.0, True),
        chamfer_outer(P.COL_HEIGHT, od, 0.8, True),
    ])
    return part


def build(bore: float = None, label: str = None):
    bore = P.SNAP_BORE if bore is None else bore
    r_out = bore / 2.0 + P.COL_WALL
    od = 2 * r_out
    ear_proj = P.CORD_RADIUS + P.CORD_HOLE / 2 + P.CORD_EDGE_WALL - r_out

    band = tube(P.COL_HEIGHT, od, bore)
    part = union([band, _ear(0.0, r_out, ear_proj, label),
                  _ear(180.0, r_out, ear_proj, label)])

    big = od + 20.0
    gap_deg = 360.0 - P.SNAP_WRAP

    # Gap, centred at 6 o'clock so the collar pushes on the same way the
    # screw version does.
    gap = _sector(gap_deg, big, 270.0 - gap_deg / 2.0) \
        .extrude(P.COL_HEIGHT + 4.0).translate([0, 0, -2.0])

    # Cam ramp: widen the gap only over the innermost SNAP_LEADIN_D of wall,
    # so the tips present a flare to the barrel instead of a square corner
    # and the ring is pushed open rather than jammed.
    lead_deg = gap_deg + 2 * P.SNAP_LEADIN
    lead = _sector(lead_deg, big, 270.0 - lead_deg / 2.0) \
        .extrude(P.COL_HEIGHT + 4.0).translate([0, 0, -2.0])
    ring = tube(P.COL_HEIGHT + 4.0, bore + 2 * P.SNAP_LEADIN_D, bore - 2.0) \
        .translate([0, 0, -2.0])
    part = part - union([gap, lead ^ ring])

    # Re-cut the bore: the ears overlap into it.
    part = part - cyl(P.COL_HEIGHT + 4.0, bore, seg=SEG).translate([0, 0, -2.0])

    # Top edge breaks only - the bottom is the plate face. See params.py.
    part = part - union([
        bore_lead_in(P.COL_HEIGHT, bore, 1.0, True),
        chamfer_outer(P.COL_HEIGHT, od, 0.8, True),
    ])
    return part


META_LEVER = dict(
    name="01d_collar_lever",
    desc="Circlip-style collar. Pinch the two paddles to expand it, slide it "
         "on axially, release. 290 deg of wrap - far more capture than the "
         "push-on version, for less install strain.",
    orient="REAR FACE DOWN. No supports. Band bends in-plane.",
    hardware="None.",
)

META = dict(
    name="01c_collar_snap",
    desc="No-tools split C-ring collar. Flexes out of round over the barrel "
         "and springs back. Same cord ears as the screw version.",
    orient="REAR FACE DOWN. No supports. Band bends in-plane, never across "
           "layers.",
    hardware="None.",
)
