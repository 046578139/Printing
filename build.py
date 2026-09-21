#!/usr/bin/env python3
"""Build every part and write one STL per part into stl/.

Each part is validated before it is written: a mesh that is not a single
watertight shell will not slice correctly, and a silently-fragmented part is
the kind of thing you only notice after a two-hour print.

    python3 build.py                      # build everything
    python3 build.py cap collar           # build a subset
    python3 build.py gauge --step 0.1     # fine sweep once you are close
    python3 build.py gauge --nominal 39.2 --step 0.1 --count 7
    python3 build.py gauge:shroud --step 0.1 --count 7   # one ladder only
    python3 build.py gauge:shroud --tag nylon --step 0.05 --count 7
    python3 build.py cap --nozzle 0.4 --layer 0.2 --tag fine
"""

import os
import sys
import time

import numpy as np
import trimesh

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import params as P
from parts import (collar, snapcollar, pinchcollar, lapcollar, shroud,
                   killflash, cap, gauge)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl")

# name -> (builder, expected genus, description, print orientation)
PARTS = {
    "collar": (collar.build, 4, collar.META),
    "collar_proto": (collar.build_proto, 4, collar.META_PROTO),
    "collar_snap": (snapcollar.build, 2, snapcollar.META),
    "collar_lever": (snapcollar.build_lever, 2, snapcollar.META_LEVER),
    "collar_pinch": (pinchcollar.build, 2, pinchcollar.META),
    "collar_lap": (lapcollar.build, 3, lapcollar.META),
    "shroud": (shroud.build, 1, shroud.META),
    "killflash": (killflash.build, None, killflash.META),
    "cap": (cap.build, 2, cap.META),
}

FILENAME = {
    "collar": "01_collar",
    "collar_proto": "01b_collar_proto",
    "collar_snap": "01c_collar_snap",
    "collar_lever": "01d_collar_lever",
    "collar_pinch": "01e_collar_pinch",
    "collar_lap": "01f_collar_lap",
    "shroud": "02_killflash_housing",
    "killflash": "03_killflash_insert",
    "cap": "04_flip_cap",
}


# Parts whose PRINT orientation is not the orientation they are modelled in.
# Exporting a part that then has to be flipped by hand is how the housing got
# printed upside down and strung the whole way up: the documentation said one
# thing and the file said another. The file now says the same thing.
def _flip(man, height):
    return man.rotate([180, 0, 0]).translate([0, 0, height])


def orient(name, man):
    """Put a part into the orientation its META describes, so it can be
    dropped straight onto the plate."""
    if name == "cap":
        return _flip(man, P.CAP_T)            # decorated face down
    if name == "shroud":
        return _flip(man, shroud.TOTAL)       # front register down
    return man                                 # already plate-side-down


def to_trimesh(man):
    m = man.to_mesh()
    return trimesh.Trimesh(vertices=np.asarray(m.vert_properties[:, :3]),
                           faces=np.asarray(m.tri_verts), process=False)


def validate(name, man, expect_genus):
    errs, warns = [], []
    ncomp = len(man.decompose())
    if ncomp != 1:
        errs.append("%d disconnected shells (must be 1)" % ncomp)
    if man.volume() <= 0:
        errs.append("non-positive volume")
    if expect_genus is not None and man.genus() != expect_genus:
        warns.append("genus %d, expected %d" % (man.genus(), expect_genus))

    tm = to_trimesh(man)
    if not tm.is_watertight:
        errs.append("not watertight")
    if not tm.is_winding_consistent:
        errs.append("inconsistent winding")

    bb = man.bounding_box()
    dx, dy, dz = bb[3] - bb[0], bb[4] - bb[1], bb[5] - bb[2]
    if max(dx, dy) > 250 or dz > 250:
        errs.append("exceeds 256 mm build volume")
    return errs, warns, tm, (dx, dy, dz)


def build_one(name, man, expect_genus, meta, fname):
    errs, warns, tm, dims = validate(name, man, expect_genus)
    path = os.path.join(OUT, fname + ".stl")
    status = "FAIL" if errs else ("warn" if warns else "ok")
    if not errs:
        tm.export(path)
    return dict(name=name, file=fname + ".stl", status=status, errs=errs,
                warns=warns, vol=man.volume(), tris=len(tm.faces), dims=dims,
                meta=meta)


# Flags that carry text rather than a number.
TEXT_OPTS = ("tag",)


def parse(argv):
    """Pull --key value flags out of argv, return (names, opts)."""
    names, opts, i = [], {}, 1
    while i < len(argv):
        a = argv[i]
        if a.startswith("--"):
            k, v = a[2:], argv[i + 1]
            opts[k] = v if k in TEXT_OPTS else float(v)
            i += 2
        else:
            names.append(a.lower()); i += 1
    return names, opts


def main(argv):
    os.makedirs(OUT, exist_ok=True)
    want, opts = parse(argv)
    if "nozzle" in opts:
        P.set_nozzle(opts["nozzle"], opts.get("layer"))
        print("  rebuilding for a %.2f nozzle / %.2f layer"
              % (P.NOZZLE, P.LAYER))
    want = want or list(PARTS) + ["gauge"]
    rows = []
    t0 = time.time()

    for name in list(PARTS):
        if name not in want:
            continue
        fn, g, meta = PARTS[name]
        out = FILENAME[name] + ("_" + opts["tag"] if "tag" in opts else "")
        rows.append(build_one(name, orient(name, fn()), g, meta, out))

    GAUGES = (
        ("shroud", "shroud bore", P.OBJ_FRONT_OD, P.FIT_PRESS, "05_gauge_shroud"),
        ("collar", "collar bore", P.OBJ_COLLAR_OD, P.FIT_SLIP, "06_gauge_collar"),
    )
    for key, tag, nom, fit, fname in GAUGES:
        if "gauge" not in want and ("gauge:" + key) not in want:
            continue
        if "gauge:" in " ".join(want) and ("gauge:" + key) not in want:
            continue
        if True:
            nom = opts.get("nominal", nom)
            m = dict(gauge.META)
            m["desc"] = "Ring ladder centred on the %s (%.2f nominal)." % (tag, nom + fit)
            g = gauge.build(nom, fit,
                            count=int(opts["count"]) if "count" in opts else None,
                            step=opts.get("step"))
            out = fname + ("_" + opts["tag"] if "tag" in opts else "")
            rows.append(build_one("gauge:" + tag, g, None, m, out))

    if "gauge" in want or "gauge:killflash" in want:
        m = dict(gauge.META)
        m["desc"] = "Plug ladder for the kill flash press into the front recess."
        m["orient"] = "FLAT on the plate. No supports."
        rows.append(build_one("gauge:killflash",
                              gauge.plug_gauge(P.KF_RECESS_D, P.KF_FIT,
                                               count=5, step=0.15),
                              None, m, "07_gauge_killflash"))

    w = max(len(r["file"]) for r in rows)
    print("\nNVG objective cap set  --  %s\n" % time.strftime("%Y-%m-%d %H:%M"))
    print(P.summary())
    print("\n%-*s  %6s  %9s  %8s  %-22s  %s" %
          (w, "FILE", "STATUS", "VOL mm3", "TRIS", "SIZE mm", "ORIENTATION"))
    print("-" * (w + 78))
    bad = 0
    for r in rows:
        dx, dy, dz = r["dims"]
        print("%-*s  %6s  %9.1f  %8d  %-22s  %s" %
              (w, r["file"], r["status"], r["vol"], r["tris"],
               "%.1f x %.1f x %.1f" % (dx, dy, dz),
               r["meta"].get("orient", "")))
        for e in r["errs"]:
            print("      ERROR: %s" % e); bad += 1
        for e in r["warns"]:
            print("      warn:  %s" % e)

    print("\nwrote %d STL to %s  (%.1fs)" %
          (sum(1 for r in rows if r["status"] != "FAIL"), OUT, time.time() - t0))
    if bad:
        print("!! %d validation error(s) - those files were NOT written" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
