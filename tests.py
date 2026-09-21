#!/usr/bin/env python3
"""Geometry and interface tests.

Two kinds of check:

  * SOLID/EMPTY probes - a small cube is intersected with the part to ask
    "is there material here?". This catches features that got built in the
    wrong place, which a volume or bounding-box check happily sails past.
    (The nut trap was cut into the middle of the clamp lug rather than its
    outer face, and only a probe found it.)

  * INTERFACE assertions - the arithmetic that has to hold between parts for
    the set to actually go together. These are the ones that matter when
    somebody edits params.py six months from now.

    python3 tests.py
"""

import math
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import params as P
from lib.solids import box
from parts import collar, snapcollar, shroud, killflash, cap

FAILS = []
CHECKS = [0]


def check(cond, msg):
    CHECKS[0] += 1
    if not cond:
        FAILS.append(msg)
    return cond


def solid_at(m, p, s=0.4):
    return (m ^ box(s, s, s, center=True).translate(list(p))).volume() > (s ** 3) * 0.5


def probe(m, name, p, want_solid):
    got = solid_at(m, p)
    check(got == want_solid,
          "%s: wanted %s at %s, got %s" %
          (name, "solid" if want_solid else "empty",
           tuple(round(v, 2) for v in p), "solid" if got else "empty"))


def topology(m, name, expect_genus=None):
    import numpy as np, trimesh
    check(len(m.decompose()) == 1, "%s: not a single connected shell" % name)
    check(m.volume() > 0, "%s: non-positive volume" % name)
    mm = m.to_mesh()
    tm = trimesh.Trimesh(vertices=np.asarray(mm.vert_properties[:, :3]),
                         faces=np.asarray(mm.tri_verts), process=False)
    check(tm.is_watertight, "%s: not watertight" % name)
    check(tm.is_winding_consistent, "%s: inconsistent winding" % name)
    if expect_genus is not None:
        check(m.genus() == expect_genus,
              "%s: genus %d, expected %d" % (name, m.genus(), expect_genus))
    bb = m.bounding_box()
    check(max(bb[3] - bb[0], bb[4] - bb[1]) <= 250 and bb[5] - bb[2] <= 250,
          "%s: does not fit the build volume" % name)


# ---------------------------------------------------------------- interfaces
def test_interfaces():
    # The kill flash lives in the housing's FRONT recess. The objective
    # fills the whole bore and bottoms on the flange, so there is no rear
    # pocket - asserting otherwise is what let the first insert ship at a
    # size that fitted nowhere.
    check(P.KF_OD < P.KF_RECESS_D,
          "kill flash (%.2f) will not enter the front recess (%.2f)"
          % (P.KF_OD, P.KF_RECESS_D))
    check(P.KF_RECESS_D - P.KF_OD <= 0.50,
          "kill flash is loose in the front recess (%.2f clearance)"
          % (P.KF_RECESS_D - P.KF_OD))
    check(P.KF_THICK < P.KF_RECESS_LEN,
          "kill flash (%.2f) is deeper than the recess (%.2f) and would "
          "stand proud, blocking the cap" % (P.KF_THICK, P.KF_RECESS_LEN))
    check(P.KF_RECESS_LEN - P.KF_THICK >= 0.10,
          "only %.2f mm of sink - too close to proud"
          % (P.KF_RECESS_LEN - P.KF_THICK))
    # MINIMUM FEATURE AUDIT. Every thin feature against the nozzle. A wall
    # under ~1.1x nozzle cannot be extruded at all and the slicer silently
    # omits it - which is exactly how the first kill flash came off the
    # plate as a bare rim: 0.45 mm cells on a 0.60 nozzle, 75 % of nozzle
    # diameter. This is the single most useful test in the file.
    FEATURES = (
        ("collet finger",  P.COLLET_WALL),
        ("kill flash rim", P.KF_RIM),
        ("kill flash cell wall", P.KF_WALL),
        ("cap skirt wall", P.CAP_SKIRT_WALL),
        ("cap face",       P.CAP_FACE_T),
        ("collar band",    P.COL_WALL),
        ("shroud wall",    P.SHROUD_WALL),
        ("collet slot",    P.SLOT_W),
        ("slot keyhole",   P.SLOT_KEYHOLE_D),
        ("slot edge break", P.SLOT_EDGE_BREAK),
        ("texture groove", P.TEX_WALL),
        ("cord hole",      P.CORD_HOLE),
        ("ear thickness",  P.EAR_T),
    )
    for name, v in FEATURES:
        check(v >= P.NOZZLE * 1.1,
              "%s is %.2f mm, only %.1fx a %.2f nozzle - the slicer will "
              "drop it" % (name, v, v / P.NOZZLE, P.NOZZLE))

    # Debossed detail needs real layers behind it, not one or two.
    for name, d in (("texture", P.TEX_DEPTH), ("centre mark", P.MARK_DEPTH),
                    ("gauge text", P.GAUGE_TEXT_D)):
        check(d >= P.LAYER * 2.5,
              "%s is %.2f mm deep, under 3 layers at %.2f - it will not read"
              % (name, d, P.LAYER))
    check(P.SHROUD_APERTURE > 28.0,
          "aperture %.2f is tight enough to vignette PVS-14 pattern glass"
          % P.SHROUD_APERTURE)

    # No chamfer may sit on a plate face. This is the defect that made every
    # ring in the first round print ragged for its first few layers.
    check(abs(P.PLATE_FACE_CHAMFER) < 1e-9,
          "PLATE_FACE_CHAMFER must stay zero")

    check(P.CAP_SKIRT_BORE > P.REG_OD,
          "cap pocket (%.2f) will not fit over the register (%.2f)"
          % (P.CAP_SKIRT_BORE, P.REG_OD))
    check(P.CAP_SKIRT_DEPTH > P.REG_HEIGHT,
          "cap would bottom out on the register face instead of seating on "
          "the shroud shoulder")
    check(P.CAP_OD / 2 > P.SHROUD_OD / 2,
          "cap does not overhang the shroud")

    # The cord has to run straight, or the cap pulls crooked when it closes.
    ear_hole_r = P.CORD_RADIUS
    boss_hole_r = P.CORD_RADIUS
    check(abs(ear_hole_r - boss_hole_r) < 1e-9,
          "collar ear and cap boss are not on the same cord radius")
    check(P.CORD_RADIUS > P.SHROUD_OD / 2,
          "cord line (r=%.2f) fouls the shroud (r=%.2f)"
          % (P.CORD_RADIUS, P.SHROUD_OD / 2))
    check(P.CORD_HOLE > P.CORD_DIA,
          "cord hole %.2f will not pass %.2f mm shock cord"
          % (P.CORD_HOLE, P.CORD_DIA))
    check(P.CORD_HOLE < P.CORD_KNOT_D,
          "cord hole is big enough for the knot to pull through")

    # Ear and boss need real meat outboard of the hole - this is what the
    # shock cord pulls against for the life of the part.
    ear_wall = (P.COL_OD / 2 + P.EAR_PROJ) - (P.CORD_RADIUS + P.CORD_HOLE / 2)
    boss_wall = (P.CAP_OD / 2 + P.CAP_BOSS_PROJ) - (P.CORD_RADIUS + P.CORD_HOLE / 2)
    check(ear_wall >= 2.0, "collar ear wall outboard of the cord hole is only %.2f" % ear_wall)
    check(boss_wall >= 2.0, "cap boss wall outboard of the cord hole is only %.2f" % boss_wall)

    check(P.SHROUD_GRIP_LEN <= P.OBJ_FRONT_LEN,
          "shroud grips %.1f mm but only %.1f mm of bezel is available"
          % (P.SHROUD_GRIP_LEN, P.OBJ_FRONT_LEN))
    check(P.COL_HEIGHT <= P.OBJ_COLLAR_LEN,
          "collar is taller than the barrel section it clamps")

    # Walls thick enough to be structural at 0.4 mm nozzle.
    for name, w in (("shroud", P.SHROUD_WALL), ("collar", P.COL_WALL),
                    ("cap face", P.CAP_FACE_T), ("cap skirt", P.CAP_SKIRT_WALL)):
        check(w >= 3 * P.NOZZLE * 0.95,
              "%s wall %.2f is under three perimeters" % (name, w))

    # Material provenance must stay self-consistent: a calibration is only
    # valid in the material it was read in.
    check(P.CAL_MATERIAL in P.BORE_SHIFT,
          "CAL_MATERIAL %r is not in BORE_SHIFT" % P.CAL_MATERIAL)
    check(P.PRINT_MATERIAL in P.BORE_SHIFT,
          "PRINT_MATERIAL %r is not in BORE_SHIFT" % P.PRINT_MATERIAL)
    expect = (P.BORE_SHIFT[P.PRINT_MATERIAL] - P.BORE_SHIFT[P.CAL_MATERIAL]
              + P.BORE_TRIM)
    check(abs(P.BORE_BIAS - expect) < 1e-9,
          "BORE_BIAS %.3f does not match the material table (%.3f)"
          % (P.BORE_BIAS, expect))
    check(abs(P.BORE_SHIFT["PLA"]) < 1e-9,
          "PLA is the reference row and must be 0.00")
    check(abs(P.BORE_BIAS) < 0.40,
          "BORE_BIAS of %+.2f is larger than any real material delta - "
          "check CAL_MATERIAL / PRINT_MATERIAL" % P.BORE_BIAS)

    check(0.10 <= P.KF_FIT <= 0.45,
          "KF_FIT %.2f is outside a workable press into the shroud bore"
          % P.KF_FIT)

    check(P.GAUGE_STEP <= P.FIT_PRESS * 2,
          "gauge step %.2f cannot resolve a %.2f press fit"
          % (P.GAUGE_STEP, P.FIT_PRESS))
    check((P.GAUGE_COUNT - 1) / 2 * P.GAUGE_STEP >= 1.0,
          "gauge ladder only spans +/-%.2f - too narrow to bracket an "
          "unverified nominal" % ((P.GAUGE_COUNT - 1) / 2 * P.GAUGE_STEP))

    # Texture and mark must not cut through the cap face.
    check(P.TEX_DEPTH < P.CAP_FACE_T * 0.5, "grip texture is too deep")
    check(P.MARK_DEPTH < P.CAP_FACE_T * 0.5, "centre mark is too deep")


# ---------------------------------------------------------------- per part
def test_collar():
    m = collar.build()
    topology(m, "collar", expect_genus=4)
    X = collar.X_LUG
    probe(m, "collar screw axis",       (0.0, collar.Y_SCR, collar.Z_SCR), False)
    probe(m, "collar counterbore",      (X - 1.0, collar.Y_SCR + 2.2, collar.Z_SCR), False)
    probe(m, "collar past counterbore", (X - P.M3_HEAD_DEPTH - 0.9, collar.Y_SCR + 2.2, collar.Z_SCR), True)
    probe(m, "collar nut trap",         (-X + 1.0, collar.Y_SCR + 2.2, collar.Z_SCR), False)
    probe(m, "collar past nut trap",    (-X + P.M3_NUT_DEPTH + 0.9, collar.Y_SCR + 2.2, collar.Z_SCR), True)
    probe(m, "collar lug body",         (X - 2.0, collar.Y_SCR + 6.0, collar.Z_SCR), True)
    probe(m, "collar ear hole +X",      (P.CORD_RADIUS, 0.0, 2.0), False)
    probe(m, "collar ear hole -X",      (-P.CORD_RADIUS, 0.0, 2.0), False)
    probe(m, "collar ear meat",         (P.CORD_RADIUS + 3.2, 0.0, 2.0), True)
    probe(m, "collar band at 12",       (0.0, P.COL_OD / 2 - 1.6, 5.5), True)
    probe(m, "collar bore clear",       (0.0, P.COL_BORE / 2 - 1.5, 5.5), False)
    probe(m, "collar pinch gap",        (0.0, -(P.COL_OD / 2 - 1.0), 5.0), False)


def test_collar_proto():
    import math as _m
    g = collar.geom(P.COL_PROTO_BORE, P.COL_PROTO_GAP)
    hi, lo = collar.clamp_range(g)
    check(hi - lo > 2.5,
          "prototype collar only spans %.2f mm - not enough to be worth "
          "printing before the barrel is gauged" % (hi - lo))
    check(lo < P.COL_BORE < hi or lo < P.OBJ_COLLAR_OD < hi,
          "prototype collar range %.2f-%.2f does not cover the current "
          "nominal" % (lo, hi))
    check(g["gap"] < _m.pi * g["bore"] * 0.12,
          "pinch gap is %.0f%% of the circumference - the band would no "
          "longer wrap enough to grip"
          % (100 * g["gap"] / (_m.pi * g["bore"])))
    # Screw has to physically span both lugs plus the open gap.
    need = 2 * g["x_lug"]
    check(need < 32.0,
          "prototype collar needs a %.0f mm screw - longer than M3 stock"
          % need)
    m = collar.build_proto()
    topology(m, "collar_proto", expect_genus=4)
    probe(m, "proto ear hole +X", (P.CORD_RADIUS, 0.0, 2.0), False)
    probe(m, "proto ear hole -X", (-P.CORD_RADIUS, 0.0, 2.0), False)
    probe(m, "proto bore clear", (0.0, P.COL_PROTO_BORE / 2 - 1.5, 5.5), False)


def test_collar_snap():
    m = snapcollar.build()
    topology(m, "collar_snap", expect_genus=2)

    check(P.SNAP_WRAP > 180.0,
          "snap collar wraps %.0f deg - under 180 it cannot capture the "
          "barrel at all" % P.SNAP_WRAP)
    check(P.SNAP_WRAP < 250.0,
          "snap collar wraps %.0f deg - past ~240 the spread needed to get "
          "over the barrel grows very fast" % P.SNAP_WRAP)
    check(P.SNAP_LEADIN_D < P.COL_WALL * 0.6,
          "cam ramp %.2f eats too much of a %.2f wall"
          % (P.SNAP_LEADIN_D, P.COL_WALL))

    # Installation strain must have real margin in the weakest material the
    # part will ever be printed in, at the LARGEST barrel it might see.
    worst = P.SNAP_BORE + P.SNAP_INTERF + 1.2
    r = snapcollar.mechanics(barrel=worst, interference=worst - P.SNAP_BORE)
    check(r["install"] < 0.015,
          "install strain %.2f%% at a %.2f barrel exceeds PLA's ~1.5%% limit"
          % (r["install"] * 100, worst))
    check(r["install"] < 0.015 / 1.5,
          "install strain %.2f%% leaves under 1.5x margin in PLA"
          % (r["install"] * 100))

    # And it has to actually grip at the SMALLEST barrel, or it is jewellery.
    best = P.SNAP_BORE + 0.2
    rb = snapcollar.mechanics(barrel=best, interference=0.2)
    check(rb["seated"] > 0.0002,
          "seated strain %.3f%% at a %.2f barrel is too low to grip"
          % (rb["seated"] * 100, best))

    # Seated strain is sustained, and sustained strain creeps.
    nom = snapcollar.mechanics()
    check(nom["seated"] < 0.010,
          "seated strain %.2f%% is high for a permanently loaded part - it "
          "will relax" % (nom["seated"] * 100))
    check(nom["spread"] > 0.5,
          "spread of %.2f mm means the ring barely has to flex - check the "
          "wrap angle" % nom["spread"])

    probe(m, "snap ear hole +X", (P.CORD_RADIUS, 0.0, 2.0), False)
    probe(m, "snap ear hole -X", (-P.CORD_RADIUS, 0.0, 2.0), False)
    probe(m, "snap gap open at 6", (0.0, -(P.SNAP_BORE / 2 + 1.5), 5.5), False)
    probe(m, "snap crown solid at 12",
          (0.0, P.SNAP_BORE / 2 + 1.5, 5.5), True)


def test_collar_lever():
    import math as _m
    m = snapcollar.build_lever()
    topology(m, "collar_lever", expect_genus=2)

    check(P.SNAP_LEVER_WRAP > P.SNAP_WRAP,
          "the lever collar's whole point is more wrap than the push-on "
          "version (%.0f vs %.0f)" % (P.SNAP_LEVER_WRAP, P.SNAP_WRAP))
    check(P.SNAP_LEVER_WRAP < 330.0,
          "%.0f deg leaves too little gap to get a finger in"
          % P.SNAP_LEVER_WRAP)

    ax = snapcollar.mechanics(mode="axial", wrap=P.SNAP_LEVER_WRAP,
                              interference=P.SNAP_LEVER_INTERF)
    rad = snapcollar.mechanics(mode="radial")

    # The reason this design exists: opening it by hand beats letting the
    # barrel force it, on strain AND on force, despite far more wrap.
    check(ax["install"] <= rad["install"],
          "lever install strain %.2f%% is worse than the push-on's %.2f%% - "
          "the extra wrap is not paying for itself"
          % (ax["install"] * 100, rad["install"] * 100))
    check(ax["install"] < 0.015,
          "lever install strain %.2f%% exceeds PLA's ~1.5%% limit"
          % (ax["install"] * 100))

    # It has to be openable by hand but not floppy.
    check(5.0 < ax["tip_force"] < 45.0,
          "%.0f N at the paddles is outside what fingers do comfortably"
          % ax["tip_force"])

    # At this wrap it CANNOT be pushed on radially - make sure nobody
    # quietly changes the wrap and reintroduces that assumption.
    r_at_wrap = snapcollar.mechanics(mode="radial", wrap=P.SNAP_LEVER_WRAP,
                                     interference=P.SNAP_LEVER_INTERF)
    check(r_at_wrap["install"] > ax["install"] * 1.5,
          "radial and axial install are too close at %.0f deg - the axial "
          "story no longer holds" % P.SNAP_LEVER_WRAP)

    # Paddles must not foul each other, or the ring cannot close.
    r_out = P.SNAP_LEVER_BORE / 2 + P.COL_WALL
    gap = 360.0 - P.SNAP_LEVER_WRAP
    off = _m.degrees((P.LEVER_W / 2.0) / r_out)
    sep = _m.radians(gap - 2 * off)
    r_head = r_out + P.LEVER_PROJ - P.LEVER_PAD_T / 2
    clear = 2 * r_head * _m.sin(sep / 2) - P.LEVER_PAD_W
    check(clear > 4.0,
          "only %.1f mm between the paddle heads - they will collide" % clear)

    probe(m, "lever ear hole +X", (P.CORD_RADIUS, 0.0, 2.0), False)
    probe(m, "lever ear hole -X", (-P.CORD_RADIUS, 0.0, 2.0), False)
    probe(m, "lever crown solid",
          (0.0, P.SNAP_LEVER_BORE / 2 + 1.5, 5.5), True)
    probe(m, "lever gap open at 6",
          (0.0, -(P.SNAP_LEVER_BORE / 2 + 1.5), 5.5), False)


def test_shroud():
    m = shroud.build()
    topology(m, "shroud", expect_genus=1)
    r_b, r_o = P.SHROUD_BORE / 2, P.SHROUD_OD / 2
    r_ap = P.KF_RECESS_D / 2
    z_mid = (shroud.Z_FLNG + shroud.Z_TOP) / 2      # inside the front recess

    # The objective's bore, all the way to the flange it bottoms on.
    probe(m, "shroud bore clear (rear)",  (r_b - 1.0, 0.0, 3.0), False)
    probe(m, "shroud bore clear (front)", (r_b - 1.0, 0.0, shroud.Z_FLNG - 1.0), False)
    probe(m, "shroud wall at bore",       (r_b + 1.5, 0.0, 3.0), True)

    # The flange the objective seats against - material must appear at the
    # aperture radius right where the bore ends.
    probe(m, "shroud flange present", (r_ap + 1.2, 0.0, shroud.Z_FLNG + 0.8), True)

    # The FRONT recess the kill flash presses into.
    probe(m, "shroud front recess clear", (r_ap - 2.0, 0.0, z_mid), False)
    probe(m, "shroud recess wall",        (r_ap + 1.2, 0.0, z_mid), True)
    probe(m, "shroud aperture open",      (0.0, 0.0, z_mid), False)

    probe(m, "shroud register wall",    (P.REG_OD / 2 - 1.2, 0.0, shroud.Z_BODY + 1.0), True)
    probe(m, "shroud shoulder is void", (r_o - 0.6, 0.0, shroud.Z_BODY + 1.0), False)

    # And the recess has to be clear over the kill flash's full footprint,
    # for its full thickness - the whole point of this rebuild.
    import math as _m2
    for a in (0, 90, 180, 270):
        rr = P.KF_OD / 2 - 0.6
        probe(m, "shroud recess clear at %d deg" % a,
              (rr * _m2.cos(_m2.radians(a)), rr * _m2.sin(_m2.radians(a)),
               shroud.Z_FLNG + P.KF_THICK - 0.3), False)
    # The rear bore lead-in and the rear outer chamfer bite into the SAME
    # annular face from opposite sides. If they sum past the wall they erase
    # it, the fingers feather to a knife edge, and the part no longer starts
    # at Z=0 - which is exactly what shipped in the first round.
    rear_wall = P.COLLET_WALL if P.SHROUD_SLOTS else P.SHROUD_WALL
    left = rear_wall - P.SHROUD_LEAD_IN - P.SHROUD_REAR_CH
    check(left >= 0.4,
          "rear face is only %.2f mm wide after a %.2f lead-in and a %.2f "
          "chamfer on a %.2f wall" % (left, P.SHROUD_LEAD_IN,
                                      P.SHROUD_REAR_CH, rear_wall))
    bb = m.bounding_box()
    check(abs(bb[2]) < 1e-6,
          "shroud does not start at Z=0 (starts at %.3f) - something has "
          "eaten the rear face" % bb[2])
    check(abs(bb[5] - shroud.Z_TOP) < 1e-6,
          "shroud top is %.3f, expected %.3f" % (bb[5], shroud.Z_TOP))

    # The objective seats against the flange, so that depth is hardware-
    # confirmed and must not drift when the kill flash is resized.
    check(abs(shroud.Z_FLNG - P.SHROUD_BORE_LEN) < 1e-9,
          "flange seat has moved off SHROUD_BORE_LEN")
    check(abs((shroud.Z_TOP - shroud.Z_FLNG) - P.KF_RECESS_LEN) < 1e-9,
          "front recess depth no longer matches KF_RECESS_LEN")

    if P.SHROUD_SLOTS:
        import math as _m
        check(P.SLOT_LEN < P.COLLET_LEN < P.SHROUD_GRIP_LEN,
              "slot %.1f / collet %.1f / grip %.1f are out of order - the "
              "collet would open the kill flash seat"
              % (P.SLOT_LEN, P.COLLET_LEN, P.SHROUD_GRIP_LEN))
        check(P.SLOT_LEN + P.SLOT_KEYHOLE_D / 2 <= P.COLLET_LEN + 1e-9,
              "keyhole reaches Z=%.2f, past the collet section at %.2f"
              % (P.SLOT_LEN + P.SLOT_KEYHOLE_D / 2, P.COLLET_LEN))
        check(P.SLOT_KEYHOLE_D > P.SLOT_W,
              "keyhole is not larger than the slot, so it arrests nothing")

        # The finger has to be a spring. Compliance goes as t^3/L^3; below
        # about L/t = 3 it behaves as a short plate and the collet buys
        # nothing over a solid ring.
        lt = P.SLOT_LEN / P.COLLET_WALL
        check(lt >= 3.0,
              "collet finger L/t is %.2f - too stubby to flex; thin "
              "COLLET_WALL or lengthen SLOT_LEN" % lt)
        check(P.COLLET_WALL >= 3 * P.NOZZLE * 0.95,
              "collet finger wall %.2f is under three perimeters" % P.COLLET_WALL)
        check(P.COLLET_OD < P.SHROUD_OD,
              "collet OD is not relieved below the full wall")

        r_mid = (P.SHROUD_BORE / 2 + P.COLLET_OD / 2) / 2
        for i in range(P.SHROUD_SLOTS):
            a = _m.radians(45.0 + 360.0 * i / P.SHROUD_SLOTS)
            probe(m, "shroud slot %d open" % i,
                  (r_mid * _m.cos(a), r_mid * _m.sin(a), P.SLOT_LEN / 2), False)
            probe(m, "shroud keyhole %d" % i,
                  (r_mid * _m.cos(a), r_mid * _m.sin(a), P.SLOT_LEN), False)
            probe(m, "shroud solid above collet %d" % i,
                  (r_mid * _m.cos(a), r_mid * _m.sin(a), P.COLLET_LEN + 0.4), True)
        # Finger material must survive between slots.
        a = _m.radians(45.0 + 180.0 / P.SHROUD_SLOTS)
        probe(m, "shroud finger between slots",
              (r_mid * _m.cos(a), r_mid * _m.sin(a), P.SLOT_LEN / 2), True)

        # The eight axial edges the slots leave in the bore must be broken -
        # square ones scrape the objective bezel on every install.
        rb = P.SHROUD_BORE / 2
        th = _m.asin((P.SLOT_W / 2) / rb)
        for i in range(P.SHROUD_SLOTS):
            a = _m.radians(45.0 + 360.0 * i / P.SHROUD_SLOTS)
            for sgn in (1, -1):
                e = a + sgn * th
                probe(m, "shroud bore edge %d%+d broken" % (i, sgn),
                      ((rb + 0.35) * _m.cos(e), (rb + 0.35) * _m.sin(e),
                       P.SLOT_LEN / 2), False)

        removed = P.SHROUD_SLOTS * P.SLOT_W / (_m.pi * P.COLLET_OD)
        check(removed < 0.20,
              "collet slots remove %.0f%% of the grip circumference" % (removed * 100))


def test_killflash():
    m = killflash.build()
    topology(m, "killflash")
    solid = math.pi * (P.KF_OD / 2) ** 2 * P.KF_THICK
    open_frac = 1 - m.volume() / solid
    check(open_frac > 0.55,
          "kill flash open area is only %.0f%% - too much light lost" % (open_frac * 100))
    check(m.genus() > 25, "kill flash has only %d cells" % m.genus())
    probe(m, "killflash rim",    (P.KF_OD / 2 - P.KF_RIM / 2, 0.0, 1.5), True)
    probe(m, "killflash centre", (0.0, 0.0, 1.5), False)
    bb = m.bounding_box()
    check(abs(bb[2]) < 1e-6,
          "kill flash does not start at Z=0 - the plate face has been "
          "chamfered")
    of, cutoff = killflash.optics()
    check(cutoff > 45.0,
          "cutoff %.0f deg is inside the ~40 deg field of view - the flash "
          "would vignette the image" % cutoff)
    check(cutoff < 60.0,
          "cutoff %.0f deg is so wide it suppresses almost nothing" % cutoff)


def test_cap():
    m = cap.build()
    topology(m, "cap", expect_genus=2)
    probe(m, "cap pocket clear",     (0.0, 0.0, 1.0), False)
    probe(m, "cap face present",     (0.0, 0.0, P.CAP_T - 1.0), True)
    probe(m, "cap pocket wall",      (P.CAP_SKIRT_BORE / 2 + 1.0, 0.0, 1.0), True)
    probe(m, "cap cord hole +X",     (P.CORD_RADIUS, 0.0, P.CAP_T / 2), False)
    probe(m, "cap cord hole -X",     (-P.CORD_RADIUS, 0.0, P.CAP_T / 2), False)
    probe(m, "cap boss meat",        (P.CORD_RADIUS + 3.0, 0.0, P.CAP_T / 2), True)
    probe(m, "cap thumb tab",        (0.0, cap.TAB_Y_OUT + 2.0, P.CAP_T - 1.0), True)
    probe(m, "cap thumb scoop",      (0.0, cap.TAB_Y_OUT + 2.5, 0.3), False)


def test_assembly():
    """Virtual assembly. Parts that pass every dimension check individually
    can still refuse to go together - which is exactly what happened to the
    first kill flash."""
    sh = shroud.build()
    kf = killflash.build().translate([0, 0, shroud.Z_FLNG])

    clash = (sh ^ kf).volume()
    check(clash < 1e-6,
          "kill flash fouls the housing by %.3f mm3 when seated" % clash)

    top = shroud.Z_FLNG + P.KF_THICK
    check(top <= shroud.Z_TOP,
          "kill flash stands %.2f mm proud of the front face and would hold "
          "the cap off" % (top - shroud.Z_TOP))

    # The cap has to close over whatever is in the recess.
    check(P.CAP_SKIRT_DEPTH > P.REG_HEIGHT,
          "cap bottoms on the register instead of the shoulder")
    check(P.CAP_SKIRT_BORE > P.REG_OD,
          "cap will not go over the register")

    # Every part must sit flat on the plate. A chamfered plate face is the
    # defect that made the first round print ragged for its first layers.
    for name, m in (("collar", collar.build()),
                    ("collar_proto", collar.build_proto()),
                    ("collar_snap", snapcollar.build()),
                    ("collar_lever", snapcollar.build_lever()),
                    ("killflash", killflash.build()),
                    ("shroud", sh)):
        check(abs(m.bounding_box()[2]) < 1e-6,
              "%s does not start at Z=0 - its plate face is chamfered" % name)


def test_export_orientation():
    """The exported file must already be in the orientation the docs claim.

    A file that has to be flipped by hand before slicing is a file that will
    eventually be sliced unflipped - which is exactly how the housing got
    printed upside down and strung the whole way up its bore.
    """
    import build

    c = build.orient("cap", cap.build())
    z0, z1 = c.bounding_box()[2], c.bounding_box()[5]
    check(abs(z0) < 1e-6, "oriented cap does not sit on Z=0")
    # r=15 is outside the centre mark but inside the register pocket, so it
    # tells the two faces apart. Face plate solid, pocket not.
    check(solid_at(c, (15.0, 0.0, z0 + 0.8)),
          "cap: no material just above the plate at r=15 - it is upside down")
    check(not solid_at(c, (15.0, 0.0, z1 - 0.8)),
          "cap: solid at r=15 near the top - the pocket is facing down")

    s = build.orient("shroud", shroud.build())
    z0, z1 = s.bounding_box()[2], s.bounding_box()[5]
    check(abs(z0) < 1e-6, "oriented shroud does not sit on Z=0")
    # r=17.8 sits between the 33.00 front recess and the 36.90 rear bore.
    check(solid_at(s, (17.8, 0.0, z0 + 1.5)),
          "shroud: no material at r=17.8 near the plate - front is not down")
    check(not solid_at(s, (17.8, 0.0, z1 - 1.5)),
          "shroud: solid at r=17.8 near the top - it is upside down")

    # Parts modelled plate-side-down must be left alone.
    for name, fn in (("collar", collar.build),
                     ("collar_snap", snapcollar.build),
                     ("killflash", killflash.build)):
        m = fn()
        check(abs(build.orient(name, m).volume() - m.volume()) < 1e-6,
              "%s should not be reoriented on export" % name)


def main():
    for fn in (test_interfaces, test_collar, test_collar_proto,
               test_collar_snap, test_collar_lever, test_shroud,
               test_killflash, test_cap, test_assembly,
               test_export_orientation):
        name = fn.__name__.replace("test_", "")
        before = len(FAILS)
        fn()
        n = len(FAILS) - before
        print("  %-12s %s" % (name, "ok" if n == 0 else "%d FAILED" % n))

    print("\n%d checks, %d failures" % (CHECKS[0], len(FAILS)))
    for f in FAILS:
        print("  FAIL: %s" % f)
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
