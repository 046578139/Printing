"""01g - Cinch collar. Held by a zip tie, not by the plastic.

Every other collar in this set asks PLA to be a spring, and PLA is bad at
being a spring: it holds on the day you fit it and stress-relaxes afterwards.
01f is a better ring than any of them and it still cannot beat that. This one
asks the plastic to do nothing but transmit load. A nylon zip tie around the
outside does the clamping.

Reduced to the same terms - an equivalent band tension, since a split ring
carries no hoop load and grips only by bending back toward its free shape:

    01f, PLA spring  : 6.1 N equivalent -> 0.21 Nm of twist resistance
    01g, 3.6 mm tie  : 40 N hand-tight  -> 1.39 Nm, and re-tensionable

0.21 Nm is a collar you can twist with your fingers, which is exactly the
reported behaviour - and PLA sheds a third of even that in the first week.
The tie is 6.6x better on the day and does not decay at all.

It is also gentle: 40 N spreads to 0.20 MPa (29 psi) over the bore, and
leaves the collar wall at 1.14 MPa, 44x under PLA's yield. Pulling the tie
to its full 178 N rating still leaves 10x.

The second thing it buys is that the seat diameter stops mattering. It has
never been gauged, only triangulated from the front bezel. A 6 mm gap closes
6/pi = 1.91 mm of diameter, so ONE part covers 37.20 down to 35.29 - wider
than the whole plausible spread. Nothing to sweep, nothing to get wrong.

The tie channel
---------------
Formed by standing the rest of the OD PROUD of the channel floor, not by
grooving into the wall. Grooving 1.50 mm into a 3.20 mm wall would leave
1.70 mm exactly where the band tension is trying to crush it; this way the
wall is full thickness everywhere and the rims are free material.

The upper rim arrives on a 45 degree ramp, which is self-supporting and also
stops the tie walking up out of the channel under tension. The lower shoulder
is a square step that faces up, so it needs no support either.

The ears sit entirely within the lower full-OD section, so nothing intrudes
into the channel and the tie runs clear all the way round.

Cord instead of a tie: 1/8 in shock cord sits in the same channel. It is the
better choice for a part that will live on the goggle, because the cord keeps
pulling as the plastic creeps, where a tie holds whatever length it was
ratcheted to. A tie is the better choice for tonight.

Print orientation: REAR FACE DOWN, plate face flat. No supports - the only
downward faces on the part are the 45 degree ramp and the bore lead-in.
"""

import math

import params as P
from lib.solids import (circle2d, cyl, poly, profile_revolve, round2d, union,
                        SEG)
from lib.patterns import cord_ear_2d
from lib.text3d import text_2d
from manifold3d import Manifold, CrossSection

R_CH = P.CINCH_BORE / 2.0 + P.COL_WALL              # channel floor radius
R_RIM = R_CH + P.CINCH_RIM                          # rim radius


def stack(height: float = None) -> tuple:
    """(lower section, channel, ramp, rim) for a given overall height.

    The channel width is defended first and the ears give up the height,
    because a cord anchor can afford to be thinner than a tie channel can
    afford to be narrower - a 3.6 mm tie in a 3.0 mm channel rides on the
    rims instead of in the groove, which is the one way this collar fails.
    """
    height = P.COL_HEIGHT if height is None else height
    ramp = P.CINCH_RIM                 # 45 deg: rise must equal the offset
    rim = 0.50
    chan = P.CINCH_CHAN_Z if height >= 10.0 else P.CINCH_SHORT_CHAN
    lower = height - chan - ramp - rim
    return lower, chan, ramp, rim


def clamp_range(bore: float = None, gap: float = None) -> tuple:
    """(largest, smallest) barrel this collar can grip. Closing the gap by g
    shortens the bore circumference by exactly g, so the diameter falls by
    g/pi. This is the whole argument for the design."""
    bore = P.CINCH_BORE if bore is None else bore
    gap = P.CINCH_GAP if gap is None else gap
    return bore, bore - gap / math.pi


def grip(bore: float = None, tension: float = 40.0, seat: float = None,
         ring_free: float = None, mu: float = 0.30, E: float = 2750.0) -> dict:
    """What actually holds the collar on, against what 01f manages.

    The two cannot be compared on stress, because a SPLIT ring carries no
    hoop tension at all - the gap sees to that. It grips only by trying to
    spring back toward its free curvature, which is a bending moment. So
    reduce both to the same thing: an equivalent band tension.

      tie   : T is the tension you ratchet in, directly.
      01f   : M = E*I*|1/r_seat - 1/r_free| at every section, and a moment M
              on radius r is worth a band tension M/r.

    From there the grip is the same for both. A band at tension T presses in
    with a line load T/r, which integrates to 2*pi*T of normal force over the
    circumference - so pull-off is mu*2*pi*T and the twisting torque that
    sets the cap's orientation is mu*2*pi*T*r.
    """
    bore = P.CINCH_BORE if bore is None else bore
    seat = P.OBJ_COLLAR_OD if seat is None else seat
    ring_free = P.LAP_BORE if ring_free is None else ring_free
    r = seat / 2.0

    # 01f, as an equivalent band tension.
    inertia = P.COL_HEIGHT * P.COL_WALL ** 3 / 12.0
    d_kappa = abs(1.0 / (seat / 2.0) - 1.0 / (ring_free / 2.0))
    t_ring = E * inertia * d_kappa / r

    def holding(t):
        n = 2.0 * math.pi * t
        return dict(band=t, normal=n, pulloff=mu * n, torque=mu * n * r / 1000.0)

    tie, ring = holding(tension), holding(t_ring)
    return dict(
        tie=tie, ring=ring, ratio=tension / t_ring,
        # And what that tension does to the parts it is squeezing.
        bore_pressure=tension / (r * P.COL_HEIGHT),
        collar_hoop=tension / (P.COL_WALL * P.COL_HEIGHT),
        yield_margin=50.0 / (tension / (P.COL_WALL * P.COL_HEIGHT)),
    )


def _sector(angle: float, r: float, start: float) -> CrossSection:
    n = max(4, int(SEG * angle / 360.0) + 1)
    pts = [(0.0, 0.0)]
    for i in range(n + 1):
        a = math.radians(start + angle * i / n)
        pts.append((r * math.cos(a), r * math.sin(a)))
    return poly(pts)


def _profile(bore: float, height: float = None) -> list:
    """The (radius, z) section, revolved to make the band.

    Authored bottom-outward-up-inward-down. The bottom face is dead flat:
    a chamfer there is what made every ring in the first printed round come
    out ragged for its first few layers.
    """
    h = P.COL_HEIGHT if height is None else height
    lower, chan, ramp, _rim = stack(h)
    r_b = bore / 2.0
    r_ch = r_b + P.COL_WALL
    r_rim = r_ch + P.CINCH_RIM
    z_lo = lower
    z_hi = z_lo + chan
    e = P.CINCH_EDGE
    return [
        (r_b, 0.0),
        (r_rim, 0.0),                      # flat plate face, full width
        (r_rim, z_lo),                     # lower section - the ears live here
        (r_ch, z_lo),                      # step in; faces UP, self-supporting
        (r_ch, z_hi),                      # channel floor
        (r_rim, z_hi + ramp),              # 45 deg ramp back out
        (r_rim, h - e),
        (r_rim - e, h),                    # top edge break
        (r_b + 0.8, h),                    # bore lead-in, fit it top-first
        (r_b, h - 0.8),
    ]


def _ear(angle: float, bore: float, thick: float,
         label: str = None) -> Manifold:
    """Cord ear, straight out from the band at full boss width.

    A slice of the band is folded into the profile before rounding so the
    root fillets into it rather than being welded on as a separate solid.
    """
    r_b = bore / 2.0
    r_rim = r_b + P.COL_WALL + P.CINCH_RIM
    prof = cord_ear_2d(r_rim, P.CORD_RADIUS, P.EAR_BOSS_D,
                       P.EAR_STEM_W, P.EAR_ROUND)
    band = (circle2d(2 * r_rim, SEG) - circle2d(2 * r_b, SEG)) \
        ^ _sector(60.0, 4 * r_rim, -30.0)
    ear = round2d(prof + band, P.CINCH_ROUND).extrude(thick)
    # NOTE: the cord hole is NOT cut here. See build().
    if label:
        txt = text_2d(label, 2.40)
        if not txt.is_empty():
            ear = ear - txt.rotate(90).extrude(0.8) \
                .translate([r_rim + 1.0, 0.0, thick - P.LAYER * 2])
    return ear.rotate([0, 0, angle])


def build(bore: float = None, gap: float = None, label: str = None,
          height: float = None):
    bore = P.CINCH_BORE if bore is None else bore
    gap = P.CINCH_GAP if gap is None else gap
    height = P.COL_HEIGHT if height is None else height
    lower = stack(height)[0]
    r_b = bore / 2.0
    r_rim = r_b + P.COL_WALL + P.CINCH_RIM

    # Ear thickness IS the lower section, so the ears can never intrude into
    # the tie channel however short the collar gets.
    part = union([profile_revolve(_profile(bore, height), SEG),
                  _ear(0.0, bore, lower, label),
                  _ear(180.0, bore, lower, label)])

    # The gap. Cut as a slot of constant WIDTH rather than a sector, because
    # what has to close is a width, not an angle - and the number that gets
    # quoted is 6 mm at the bore, not 18 degrees.
    span = r_rim + 8.0
    slot = poly([(-gap / 2.0, 0.0), (gap / 2.0, 0.0),
                 (gap / 2.0, span), (-gap / 2.0, span)]) \
        .extrude(height + 4.0).translate([0.0, 0.0, -2.0])
    part = part - slot.rotate([0, 0, P.CINCH_GAP_AT - 90.0])

    # Re-cut the bore AND the cord holes last. Both have to come after the
    # union, for the same reason: the band and the ears overlap each other,
    # so anything cut from one before they are joined is filled straight back
    # in by the other.
    #
    # The cord hole sits at a FIXED radius while the band's rim grows with
    # the bore. Cut inside _ear(), the hole measured 3.92 mm round at a 37.20
    # bore, 3.70 at 39.20 and 2.70 at 41.20 - the band ate the inner side of
    # it and left a D. Every one of those still passed topology, volume and
    # a probe down the hole's centre.
    cuts = [cyl(height + 4.0, bore, seg=SEG).translate([0, 0, -2.0])]
    for x in (P.CORD_RADIUS, -P.CORD_RADIUS):
        cuts.append(cyl(height + 4.0, P.CORD_HOLE, seg=48)
                    .translate([x, 0.0, -2.0]))
    return part - union(cuts)


META = dict(
    name="01g_collar_cinch",
    desc="Zip-tie cinch collar. One 3.6 mm tie in the channel, pulled tight. "
         "A 6 mm gap means it clamps anything from 37.20 down to 35.29, so "
         "the ungauged seat diameter does not matter.",
    orient="Rear face down - already oriented. No supports.",
    hardware="1x zip tie, 3.6 mm wide (40 lb), 150 mm or longer. Or 150 mm "
             "of 1/8 in shock cord knotted in the channel.",
)
