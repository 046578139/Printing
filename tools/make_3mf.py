#!/usr/bin/env python3
"""Write a Bambu Studio project (.3mf) with per-part filament assignment.

An STL is a bag of triangles. It has no notion of a part, a colour or a
filament, so "combine the cap and its lettering into one STL" can only ever
produce one grey object - which is exactly what it produced. 3MF is the
format that carries the rest: objects, the parts inside them, and which
extruder each part is printed with.

Each object here is built as a 3MF <components> assembly: one child object
per part, plus Metadata/model_settings.config naming the parts and giving
each an extruder. That is Bambu Studio's own layout, so the project opens
with the filaments already assigned and nothing to position.

    python3 tools/make_3mf.py

Bed centring is baked into the build item transform - Bambu's origin is the
front-left corner of the plate, not the middle, so geometry authored around
zero lands off the bed without it.
"""

import os
import sys
import uuid
import zipfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

import build as bm
from parts import cap

BED = 256.0

CT = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
</Types>
"""

RELS = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Target="/3D/3dmodel.model" Id="rel-1" \
Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>
"""


def _mesh_xml(man, out):
    """Append one <mesh> for a Manifold. Written straight into the output
    list rather than built as a string - a cap is 99k triangles and the
    intermediate copies cost more than the file does."""
    m = man.to_mesh()
    verts = np.asarray(m.vert_properties[:, :3], dtype=np.float64)
    tris = np.asarray(m.tri_verts)
    out.append("<mesh><vertices>")
    for x, y, z in verts:
        out.append('<vertex x="%.4f" y="%.4f" z="%.4f"/>' % (x, y, z))
    out.append("</vertices><triangles>")
    for a, b, c in tris:
        out.append('<triangle v1="%d" v2="%d" v3="%d"/>' % (a, b, c))
    out.append("</triangles></mesh>")


def write(path, objects, bed=BED):
    """objects: [(object name, [(part name, Manifold, extruder), ...]), ...]

    Objects are laid out left to right across the bed with the same 8 mm
    gap the STL plates use, and every part of an object moves with it.
    """
    model = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<model unit="millimeter" xml:lang="en-US" '
             'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
             'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06">',
             '<resources>']
    cfg = ['<?xml version="1.0" encoding="UTF-8"?>', '<config>']
    items = []

    # Lay the objects out before writing anything, so the transforms are
    # known when the build items go in.
    spans = []
    for _name, parts in objects:
        bb = [p[1].bounding_box() for p in parts]
        spans.append((min(b[0] for b in bb), max(b[3] for b in bb),
                      min(b[1] for b in bb), max(b[4] for b in bb)))
    total = sum(hi - lo for lo, hi, _a, _b in spans) + 8.0 * (len(objects) - 1)
    cursor = bed / 2.0 - total / 2.0

    nid = 1
    for (name, parts), (lo, hi, ylo, yhi) in zip(objects, spans):
        part_ids = []
        for pname, man, _ext in parts:
            model.append('<object id="%d" p:UUID="%s" type="model">'
                         % (nid, uuid.uuid4()))
            _mesh_xml(man, model)
            model.append('</object>')
            part_ids.append(nid)
            nid += 1

        oid = nid
        nid += 1
        model.append('<object id="%d" p:UUID="%s" type="model"><components>'
                     % (oid, uuid.uuid4()))
        for pid in part_ids:
            model.append('<component p:UUID="%s" objectid="%d" '
                         'transform="1 0 0 0 1 0 0 0 1 0 0 0"/>'
                         % (uuid.uuid4(), pid))
        model.append('</components></object>')

        # Bambu's origin is the front-left plate corner, not the centre.
        # Centre the BOUNDING BOX, not the modelling origin: the cap's thumb
        # tab hangs off one side, so the two are 2.7 mm apart.
        dx = cursor - lo
        dy = bed / 2.0 - (ylo + yhi) / 2.0
        cursor += (hi - lo) + 8.0
        items.append('<item objectid="%d" p:UUID="%s" '
                     'transform="1 0 0 0 1 0 0 0 1 %.4f %.4f 0" printable="1"/>'
                     % (oid, uuid.uuid4(), dx, dy))

        cfg.append('<object id="%d">' % oid)
        cfg.append('<metadata key="name" value="%s"/>' % name)
        for pid, (pname, _man, ext) in zip(part_ids, parts):
            cfg.append('<part id="%d" subtype="normal_part">' % pid)
            cfg.append('<metadata key="name" value="%s"/>' % pname)
            cfg.append('<metadata key="extruder" value="%d"/>' % ext)
            cfg.append('<mesh_stat edges_fixed="0" degenerate_facets="0" '
                       'facets_removed="0" facets_reversed="0" '
                       'backwards_edges="0"/>')
            cfg.append('</part>')
        cfg.append('</object>')

    model.append('</resources><build>')
    model.extend(items)
    model.append('</build></model>')
    cfg.append('</config>')

    z = zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=6)
    z.writestr("[Content_Types].xml", CT)
    z.writestr("_rels/.rels", RELS)
    z.writestr("3D/3dmodel.model", "".join(model))
    z.writestr("Metadata/model_settings.config", "".join(cfg))
    z.close()
    return path


GREY, TEAL = 1, 2       # AMS slot 1 and slot 2


def cap_object(word, data=None, name=None):
    """A cap as three parts: the body, the lettering and the hex field.

    Lettering and hex both go to slot 2, so the whole decorated face reads
    as one colour against the body. They stay SEPARATE parts rather than
    one merged solid, which costs nothing and means either can be clicked
    back to slot 1 without a rebuild.
    """
    return (name or ("%s cap" % word), [
        ("body (grey)", bm.orient("cap", cap.build(mark=data)), GREY),
        ("lettering %s (teal)" % word,
         bm.orient("cap_inlay", cap.inlay(mark=data)), TEAL),
        ("hex field (teal)",
         bm.orient("cap_inlay", cap.hex_inlay(mark=data)), TEAL),
    ])


if __name__ == "__main__":
    out = bm.OUT
    jobs = [
        ("20_cap_FUCK_2color.3mf", [cap_object("FUCK", "mark_fuck")]),
        ("21_cap_YOU_2color.3mf", [cap_object("YOU", "mark_you")]),
        ("22_caps_FUCK_YOU_2color.3mf",
         [cap_object("FUCK", "mark_fuck"), cap_object("YOU", "mark_you")]),
        ("23_cap_2color.3mf", [cap_object(None, None, "flip cap")]),
    ]
    for fname, objs in jobs:
        p = write(os.path.join(out, fname), objs)
        n = sum(len(o[1]) for o in objs)
        slots = sorted({e for _n, parts in objs for _p, _m, e in parts})
        print("  %-28s %d cap(s), %d parts on %d filament(s) %s  %.1f MB"
              % (fname, len(objs), n, len(slots), slots,
                 os.path.getsize(p) / 1e6))
