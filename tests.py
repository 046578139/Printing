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
from parts import collar, shroud, killflash, cap

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
        check(P.SLOT_LEN < P.SHROUD_GRIP_LEN,
              "collet slots (%.1f) run past the grip section (%.1f) and would "
              "open the kill flash seat" % (P.SLOT_LEN, P.SHROUD_GRIP_LEN))
        import math as _m
        r_mid = (P.SHROUD_BORE / 2 + P.SHROUD_OD / 2) / 2
        for i in range(P.SHROUD_SLOTS):
            a = _m.radians(45.0 + 360.0 * i / P.SHROUD_SLOTS)
            probe(m, "shroud slot %d open" % i,
                  (r_mid * _m.cos(a), r_mid * _m.sin(a), P.SLOT_LEN / 2), False)
            probe(m, "shroud seat solid above slot %d" % i,
                  (r_mid * _m.cos(a), r_mid * _m.sin(a), shroud.Z_KF + 2.5), True)
        # Between slots there must still be real wall.
        a = _m.radians(45.0 + 180.0 / P.SHROUD_SLOTS)
        probe(m, "shroud wall between slots",
              (r_mid * _m.cos(a), r_mid * _m.sin(a), P.SLOT_LEN / 2), True)
        removed = P.SHROUD_SLOTS * P.SLOT_W / (_m.pi * P.SHROUD_OD)
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
    for fn in (test_interfaces, test_collar, test_shroud, test_killflash, test_cap):
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
