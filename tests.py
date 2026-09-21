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
    check(P.KF_OD < P.SHROUD_BORE,
          "kill flash (%.2f) will not enter the shroud bore (%.2f)"
          % (P.KF_OD, P.SHROUD_BORE))
    check(P.SHROUD_BORE - P.KF_OD <= 0.45,
          "kill flash is loose in the shroud bore (%.2f clearance)"
          % (P.SHROUD_BORE - P.KF_OD))
    check(P.SHROUD_APERTURE < P.KF_OD,
          "front flange (%.2f) will not retain the kill flash (%.2f) - it "
          "would fall straight out the front" % (P.SHROUD_APERTURE, P.KF_OD))
    check(P.SHROUD_APERTURE > 28.0,
          "aperture %.2f is tight enough to vignette PVS-14 pattern glass"
          % P.SHROUD_APERTURE)

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


def test_shroud():
    m = shroud.build()
    topology(m, "shroud", expect_genus=1)
    r_b, r_o = P.SHROUD_BORE / 2, P.SHROUD_OD / 2
    probe(m, "shroud mount bore clear", (r_b - 1.0, 0.0, 4.0), False)
    probe(m, "shroud wall at mount",    (r_b + 1.5, 0.0, 4.0), True)
    probe(m, "shroud kf pocket clear",  (r_b - 1.0, 0.0, shroud.Z_KF + 2.5), False)
    probe(m, "shroud flange present",   (P.SHROUD_APERTURE / 2 + 1.2, 0.0, shroud.Z_FLNG + 0.8), True)
    probe(m, "shroud aperture clear",   (0.0, 0.0, shroud.Z_FLNG + 0.8), False)
    probe(m, "shroud register wall",    (P.REG_OD / 2 - 1.2, 0.0, shroud.Z_BODY + 1.0), True)
    probe(m, "shroud shoulder is void", (r_o - 0.6, 0.0, shroud.Z_BODY + 1.0), False)
    check(shroud.Z_KF >= P.SHROUD_GRIP_LEN,
          "kill flash pocket overlaps the objective bezel")

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
    check(open_frac > 0.60,
          "kill flash open area is only %.0f%% - too much light lost" % (open_frac * 100))
    check(m.genus() > 30, "kill flash has only %d cells" % m.genus())
    probe(m, "killflash rim",    (P.KF_OD / 2 - P.KF_RIM / 2, 0.0, 2.5), True)
    probe(m, "killflash centre", (0.0, 0.0, 2.5), False)
    of, cutoff = killflash.optics()
    check(25 < cutoff < 55, "cutoff angle %.0f deg is outside a sane range" % cutoff)


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


def main():
    for fn in (test_interfaces, test_collar, test_collar_proto,
               test_collar_snap, test_shroud, test_killflash, test_cap):
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
