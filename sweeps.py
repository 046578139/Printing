#!/usr/bin/env python3
"""Generate labelled test sweeps into stl/sweep/.

A sweep settles one unknown in a single plate instead of over three
print-and-measure cycles. Every variant carries its own identity - the kill
flashes by a countable dimple, the collars by their bore size moulded into
the cord ear - because a sweep you cannot identify once it is off the plate
tells you nothing.

    python3 sweeps.py                # everything
    python3 sweeps.py snap-bore      # one set
    python3 sweeps.py --list
"""

import os
import sys

import numpy as np
import trimesh

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import params as P
from parts import killflash, snapcollar

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl", "sweep")


def frange(lo, hi, step):
    n = int(round((hi - lo) / step)) + 1
    return [round(lo + i * step, 3) for i in range(n)]


SETS = {
    # The press into the housing's front recess. An FDM hole runs undersize
    # and an FDM boss runs oversize, and both errors land on the same
    # 0.30 mm clearance - so this is measured, not calculated.
    "killflash-fit": dict(
        what="kill flash OD, press into the front recess",
        how="Count the dimples. Largest that seats with thumb pressure and "
            "does not drop out inverted wins -> put it in KF_OD.",
        values=frange(32.3, 33.1, 0.2),
        name=lambda v, i: "kf_od_%05.2f" % v,
        build=lambda v, i: killflash.build(od=v, marks=i + 1),
    ),
    # Cell size trades transmission against cutoff angle. Only an eye can
    # settle this one.
    "killflash-optics": dict(
        what="kill flash cell size, at the nominal OD",
        how="Hold each up and look through it. Bigger cells pass more light "
            "and suppress less. Under ~3.5 they start cutting the 40 deg "
            "field of view.",
        values=[3.4, 4.2, 5.0],
        name=lambda v, i: "kf_cell_%04.1f" % v,
        build=lambda v, i: killflash.build(cell=v, marks=i + 1),
    ),
    "snap-bore": dict(
        what="01c push-on collar free bore",
        how="Wants firm thumb pressure to go on and no rotation once there. "
            "The bore is moulded into both cord ears.",
        values=frange(35.2, 36.8, 0.4),
        name=lambda v, i: "snap_%05.2f" % v,
        build=lambda v, i: snapcollar.build(bore=v, label="%.1f" % v),
    ),
    "lever-bore": dict(
        what="01d lever collar free bore",
        how="Pinch the paddles, spread, slide on axially, release.",
        values=frange(35.6, 36.4, 0.4),
        name=lambda v, i: "lever_%05.2f" % v,
        build=lambda v, i: snapcollar.build_lever(bore=v, label="%.1f" % v),
    ),
}


def export(man, path):
    m = man.to_mesh()
    tm = trimesh.Trimesh(vertices=np.asarray(m.vert_properties[:, :3]),
                         faces=np.asarray(m.tri_verts), process=False)
    bad = []
    if len(man.decompose()) != 1:
        bad.append("%d shells" % len(man.decompose()))
    if not tm.is_watertight:
        bad.append("not watertight")
    if abs(man.bounding_box()[2]) > 1e-6:
        bad.append("does not start at Z=0")
    if not bad:
        tm.export(path)
    return bad, man.volume()


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    if "--list" in argv:
        for k, s in SETS.items():
            print("  %-18s %s" % (k, s["what"]))
        return 0

    os.makedirs(OUT, exist_ok=True)
    want = args or list(SETS)
    total = 0.0
    for key in want:
        if key not in SETS:
            print("unknown set %r (try --list)" % key)
            return 1
        s = SETS[key]
        print("\n%s  --  %s" % (key, s["what"]))
        print("  %s" % s["how"])
        for i, v in enumerate(s["values"]):
            man = s["build"](v, i)
            fn = s["name"](v, i) + ".stl"
            bad, vol = export(man, os.path.join(OUT, fn))
            total += vol
            tag = ("FAIL: " + ", ".join(bad)) if bad else "ok"
            print("    %-22s %8.1f mm3   %s" % (fn, vol, tag))

    print("\n%d files in %s, %.1f cm3 solid (~%.0f g in PLA at 100%%, less "
          "with infill)" % (len(os.listdir(OUT)), os.path.relpath(OUT),
                            total / 1000.0, total / 1000.0 * 1.24))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
