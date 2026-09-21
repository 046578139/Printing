"""04 - Flip cap.

Bungee-retained cover. Two cords run straight forward from the collar ears
to the bosses at 3 and 9 o'clock, so the cord line IS the hinge axis: push
up on the thumb tab at 6 o'clock and the cap swings up and over the top,
where cord tension and friction hold it clear of the objective.

Because the cap's orientation is set by the two cords rather than by the
register, the shroud is free to sit at any rotation - which is why nothing
in this design needs an anti-rotation key.

Axial layout, Z=0 at the rear (facing the shroud), +Z forward:
    0.0 .................. rear face, lands on the shroud shoulder
    CAP_SKIRT_DEPTH ...... ceiling of the register pocket
    CAP_T ................ front face

Print orientation: FRONT FACE DOWN. The register pocket, the thumb scoop
and the cord holes then all open upward, so it prints without support and
the decorated face gets the plate finish.
"""

import params as P
from lib.solids import (circle2d, rect2d, fillet2d, round2d, poly, cyl, box,
                        union, prism_chamfered, bore_lead_in, SEG)
from lib.patterns import (grip_panel, grip_dimples, hex_dimple_disc,
                          chevron_mark, traced_mark, traced_mark_2d)

TAB_Y_OUT = -(P.CAP_OD / 2.0 + P.TAB_PROJ)
TAB_Y_IN  = -(P.CAP_OD / 2.0 - 5.0)
PANEL_Y   = 15.0
PANEL_W   = 21.0
PANEL_H   = 11.0
SCOOP_R   = 3.0


def outline():
    """The cap's 2D profile: a circle with four 45 degree flats, plus the
    two cord bosses and the thumb tab, all blended together."""
    prof = circle2d(P.CAP_OD, SEG)

    # Four flats at the diagonals give the rounded-square look and keep the
    # cap from fouling the neighbouring pod at narrow IPD.
    d = P.CAP_OD / 2.0 - P.CAP_FLAT_INSET
    knife = rect2d(90.0, 90.0).translate((d + 45.0, 0.0))
    for a in (45.0, 135.0, 225.0, 315.0):
        prof = prof - knife.rotate(a)
    prof = fillet2d(prof, P.CAP_EDGE_R)

    boss = circle2d(P.CAP_BOSS_D, 48).translate((P.CORD_RADIUS, 0.0))
    # Tapered rather than square: a straight slab reads as an afterthought
    # and catches on kit, a trapezoid sheds it.
    hw = P.TAB_W / 2.0
    tab = fillet2d(poly([(-hw, TAB_Y_IN), (hw, TAB_Y_IN),
                         (hw * 0.70, TAB_Y_OUT), (-hw * 0.70, TAB_Y_OUT)]), 2.0)

    prof = prof + boss + boss.rotate(180.0) + tab
    return round2d(prof, 0.9)          # blend the joins, inside and out


def build():
    prof = outline()
    part = prism_chamfered(prof, P.CAP_T, c_bot=0.5, c_top=0.7, steps=6)

    cuts = []

    # Register pocket. Bottoms 0.4 mm shy of the register top so the cap
    # lands on the shroud's flat shoulder, not on the register face.
    cuts.append(cyl(P.CAP_SKIRT_DEPTH + 1.0, P.CAP_SKIRT_BORE, seg=SEG)
                .translate([0, 0, -1.0]))
    cuts.append(bore_lead_in(0.0, P.CAP_SKIRT_BORE, 0.8, False))

    # Cord holes, fore/aft, on the shared cord radius.
    for x in (P.CORD_RADIUS, -P.CORD_RADIUS):
        cuts.append(cyl(P.CAP_T + 2.0, P.CORD_HOLE, seg=48)
                    .translate([x, 0.0, -1.0]))

    # Thumb scoop: a radiused groove across the rear of the tab. More
    # comfortable against a gloved thumb than a flat chamfer, and it opens
    # upward when printed front-face-down.
    scoop = cyl(P.TAB_W + 12.0, SCOOP_R * 2.0, seg=48).rotate([0, 90, 0])
    cuts.append(scoop.translate([-(P.TAB_W + 12.0) / 2.0,
                                 TAB_Y_OUT + 2.5,
                                 P.TAB_UNDERCUT - SCOOP_R]))

    # Centre mark first: the hex field has to know where to leave space.
    #
    # DEBOSSED, and printed front-face-down that means its floor is a ceiling
    # bridged over air. That is fine for a glyph and was not fine for the
    # chevron it replaced: a glyph is a set of 1.5-3 mm strokes, so every span
    # is short, where an 18 mm solid triangle was one long sagging bridge.
    mark2d = None
    if P.MARK_ENABLE:
        if P.MARK_TRACED:
            mark2d = traced_mark_2d(P.MARK_H)
            cuts.append(mark2d.extrude(P.MARK_DEPTH + 0.2)
                        .translate([0.0, 0.0, P.CAP_T - P.MARK_DEPTH]))
        else:
            cuts.append(chevron_mark(P.MARK_W, P.MARK_DEPTH + 0.2)
                        .translate([0.0, 0.0, P.CAP_T - P.MARK_DEPTH]))

    # Grip texture: ONE hex field across the whole face, at the kill flash's
    # cell size, rather than two rectangular panels. DIMPLES, not pips - the
    # first printed cap came off with squashed cells and ropey bridge lines
    # across both panel floors, because a raised cell is an isolated
    # first-layer island when the face prints downward and the floor around
    # it is one long bridge. Dimples have neither.
    clip = prof.offset(-2.0)
    field = hex_dimple_disc(P.TEX_FIELD_R, P.TEX_DEPTH + 0.2,
                            P.TEX_CELL, P.TEX_WALL,
                            keepout=mark2d, keepout_clear=P.TEX_MARK_CLEAR)
    field = field ^ clip.extrude(P.CAP_T + 2.0)
    cuts.append(field.translate([0.0, 0.0, P.CAP_T - P.TEX_DEPTH]))

    return part - union(cuts)


META = dict(
    name="04_flip_cap",
    desc="Bungee flip cap. Cord bosses at 3/9, thumb tab at 6, hex grip, "
         "register pocket that drops over the shroud.",
    orient="Decorated face down - ALREADY ORIENTED. No supports.",
)
