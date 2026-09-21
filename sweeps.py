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
from parts import (killflash, snapcollar, pinchcollar, lapcollar,
                   cinchcollar)

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
            "does not drop out inverted wins -> put it in KF_OD. Centred on "
            "32.90 because 32.70 went in but was slightly loose, so the "
            "answer is above it: 33.00 is nominal zero clearance and the "
            "last two are real interference presses.",
        values=frange(32.8, 33.2, 0.1),
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
    # The pinch collar's grip. OBJ_COLLAR_OD (36.90) is TRIANGULATED, not
    # gauged - the 36.85 ring was read on the front bezel, not on the collar
    # seat behind it. This ladder settles the seat diameter and the grip in
    # one plate, which no gauge ring can do because the ring cannot tell you
    # how much interference the ring wants.
    "pinch-bore": dict(
        what="01e pinch collar free bore",
        how="Spread the two tabs, slide it down over the bare bezel, "
            "release. Want the largest bore that still cannot be twisted by "
            "hand once seated - that is the one with the least install "
            "strain that still holds the cap's orientation. The bore size is "
            "moulded into both cord ears. Fit these BEFORE the housing.",
        values=frange(35.6, 36.8, 0.3),
        name=lambda v, i: "pinch_%05.2f" % v,
        build=lambda v, i: pinchcollar.build(bore=v, label="%.1f" % v),
    ),
    # 01g, and the only sweep here that is not a fit hunt. Each rung closes
    # 6/pi = 1.91 mm of diameter, so three of them cover 35.29 -> 41.20 with
    # no gaps - which spans EVERY seat on the unit: the front bezel (36.70),
    # the collar seat behind it, the fat ring further back, and the kill
    # flash housing's own collet (40.60-41.00). Print all three, fit whichever
    # lands on the seat you want to use.
    "cinch-bore": dict(
        what="01g cinch collar - three rungs covering every seat on the unit",
        how="Slide it on, run a 3.6 mm zip tie round the channel, pull it "
            "tight. Take the rung whose bore just clears your seat; the tie "
            "takes up whatever is left. Bore is moulded into both cord ears.",
        values=[37.2, 39.2, 41.2],
        name=lambda v, i: "cinch_%05.2f" % v,
        build=lambda v, i: cinchcollar.build(bore=v, label="%.1f" % v),
    ),
    # Same three bores, short. The locking collar is a narrow band and its
    # width has never been measured; if it is under 11 mm the standard collar
    # rides up onto the focus ring, which is the exact binding the seat was
    # moved to avoid. Print whichever height matches the band.
    "cinch-short": dict(
        what="01g cinch collar, 9.00 tall - for a narrow locking collar",
        how="Same three bores. Use these if the locking collar band is under "
            "11 mm wide. Channel still takes a 3.6 mm tie; the ears give up "
            "the height instead.",
        values=[37.2, 39.2, 41.2],
        name=lambda v, i: "cinchS_%05.2f" % v,
        build=lambda v, i: cinchcollar.build(bore=v, label="%.1f" % v,
                                             height=P.CINCH_SHORT_Z),
    ),
    "lap-bore": dict(
        what="01f lapped collar free bore",
        how="SQUEEZE the two tabs together - they are at different heights "
            "so they lap past each other - slide it down over the bare "
            "bezel, release. Want the largest bore that still cannot be "
            "twisted by hand once seated. Bore size is moulded into both "
            "cord ears. Fits BEFORE the housing.",
        values=frange(35.6, 36.8, 0.3),
        name=lambda v, i: "lap_%05.2f" % v,
        build=lambda v, i: lapcollar.build(bore=v, label="%.1f" % v),
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

    # Clear the directory first. Retuning a range leaves the old values
    # sitting there looking exactly as legitimate as the new ones, and a
    # stale variant on the plate is a measurement you cannot trust and will
    # not know not to trust. Only do it on a full run - a single-set run has
    # no business deleting another set's files.
    if not args:
        stale = [f for f in os.listdir(OUT) if f.endswith(".stl")]
        for f in stale:
            os.remove(os.path.join(OUT, f))
        if stale:
            print("cleared %d previous sweep file(s)" % len(stale))

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
