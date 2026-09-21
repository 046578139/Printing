#!/usr/bin/env python3
"""Offscreen preview renderer - orthographic z-buffer rasteriser in numpy.

No GL, no display, no extra dependencies: the environment that builds these
parts also has to be able to show them, and a headless container has neither
a GPU nor a window server.

    python3 render.py                 # one PNG per STL, into preview/
    python3 render.py 04_flip_cap     # just one
"""

import os
import sys
import zlib
import struct

import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
STL = os.path.join(HERE, "stl")
OUT = os.path.join(HERE, "preview")

BG = np.array([22, 24, 28], dtype=np.float64)
BASE = np.array([196, 202, 208], dtype=np.float64)
KEY = np.array([-0.45, -0.75, 0.90])     # main light
FILL = np.array([0.80, 0.30, 0.35])      # fill from the other side


def write_png(path, rgb):
    """Minimal PNG writer (RGB8, no filtering)."""
    h, w, _ = rgb.shape
    raw = b"".join(b"\x00" + rgb[y].astype(np.uint8).tobytes() for y in range(h))

    def chunk(tag, data):
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c))

    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 6))
           + chunk(b"IEND", b""))
    open(path, "wb").write(png)


def look_at(elev_deg, azim_deg):
    """Orthonormal camera basis (right, up, forward)."""
    e, a = np.radians(elev_deg), np.radians(azim_deg)
    fwd = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
    fwd /= np.linalg.norm(fwd)
    up0 = np.array([0.0, 0.0, 1.0])
    right = np.cross(up0, fwd)
    if np.linalg.norm(right) < 1e-6:
        right = np.array([1.0, 0.0, 0.0])
    right /= np.linalg.norm(right)
    up = np.cross(fwd, right)
    return right, up, fwd


def render(mesh, size=760, elev=26.0, azim=-58.0, margin=0.10):
    right, up, fwd = look_at(elev, azim)
    v = mesh.vertices - mesh.vertices.mean(axis=0)
    sx, sy, sz = v @ right, v @ up, v @ fwd

    span = max(sx.max() - sx.min(), sy.max() - sy.min()) * (1 + 2 * margin)
    scale = size / span
    px = (sx - (sx.max() + sx.min()) / 2) * scale + size / 2
    py = size / 2 - (sy - (sy.max() + sy.min()) / 2) * scale

    tris = mesh.faces
    n = mesh.face_normals
    # Two-light Lambert with a wrap term so the shadow side stays readable.
    lk = np.clip(n @ (KEY / np.linalg.norm(KEY)), 0, 1)
    lf = np.clip(n @ (FILL / np.linalg.norm(FILL)), 0, 1)
    shade = 0.16 + 0.68 * lk + 0.26 * lf
    rim = np.clip(1.0 - np.abs(n @ fwd), 0, 1) ** 3
    shade = np.clip(shade + 0.30 * rim, 0, 1.35)

    img = np.tile(BG, (size, size, 1))
    zbuf = np.full((size, size), -np.inf)

    a, b, c = tris[:, 0], tris[:, 1], tris[:, 2]
    # Back-face cull in screen space.
    area2 = ((px[b] - px[a]) * (py[c] - py[a]) - (px[c] - px[a]) * (py[b] - py[a]))
    keep = np.where(area2 < -1e-9)[0]

    for t in keep:
        i, j, k = tris[t]
        x0, x1, x2 = px[i], px[j], px[k]
        y0, y1, y2 = py[i], py[j], py[k]
        z0, z1, z2 = sz[i], sz[j], sz[k]

        xlo = max(int(np.floor(min(x0, x1, x2))), 0)
        xhi = min(int(np.ceil(max(x0, x1, x2))) + 1, size)
        ylo = max(int(np.floor(min(y0, y1, y2))), 0)
        yhi = min(int(np.ceil(max(y0, y1, y2))) + 1, size)
        if xlo >= xhi or ylo >= yhi:
            continue

        xs = np.arange(xlo, xhi) + 0.5
        ys = np.arange(ylo, yhi) + 0.5
        gx, gy = np.meshgrid(xs, ys)

        d = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if abs(d) < 1e-12:
            continue
        w0 = ((y1 - y2) * (gx - x2) + (x2 - x1) * (gy - y2)) / d
        w1 = ((y2 - y0) * (gx - x2) + (x0 - x2) * (gy - y2)) / d
        w2 = 1.0 - w0 - w1
        inside = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
        if not inside.any():
            continue

        z = w0 * z0 + w1 * z1 + w2 * z2
        sub = zbuf[ylo:yhi, xlo:xhi]
        win = inside & (z > sub)
        if not win.any():
            continue
        sub[win] = z[win]
        img[ylo:yhi, xlo:xhi][win] = np.clip(BASE * shade[t], 0, 255)

    return img


def main(argv):
    os.makedirs(OUT, exist_ok=True)
    want = argv[1:]
    files = sorted(f for f in os.listdir(STL) if f.endswith(".stl"))
    if want:
        files = [f for f in files if any(w in f for w in want)]

    for f in files:
        m = trimesh.load(os.path.join(STL, f), process=False)
        # Gauges read better straight on; parts read better isometric.
        iso = "gauge" not in f
        img = render(m, elev=28 if iso else 62, azim=-55 if iso else -90)
        out = os.path.join(OUT, f.replace(".stl", ".png"))
        write_png(out, img)
        print("  %-28s -> %s" % (f, os.path.relpath(out, HERE)))


if __name__ == "__main__":
    main(sys.argv)
