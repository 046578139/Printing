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


def _mark_2d(mark: str = None, mark_h: float = None):
    """The centre mark's outline, or None when marks are off.

    MARK_H sizes the PROJECT mark, which is tall and narrow and so is
    constrained by its height. A custom mark keeps whatever size it was
    traced at unless told otherwise - scaling a 36 x 9 word to a 22 mm
    "height" makes it 85 mm wide and off the part entirely.
    """
    if not (P.MARK_ENABLE and P.MARK_TRACED):
        return None
    h = mark_h if mark_h is not None else (None if mark else P.MARK_H)
    return traced_mark_2d(h, data=mark or P.MARK_DATA)


def _hex_field(prof, mark2d, depth: float):
    """The dimple field as a solid standing on z=0, `depth` tall.

    build() takes it with an overcut and hex_inlay() takes it flush, but
    both take it from HERE. A field cut at one cell size or keep-out and
    filled at another would still be watertight, still validate, and still
    come off the plate as a cap with plugs in the wrong holes.
    """
    field = hex_dimple_disc(P.TEX_FIELD_R, depth, P.TEX_CELL, P.TEX_WALL,
                            keepout=mark2d, keepout_clear=P.TEX_MARK_CLEAR)
    # Clipped 2 mm in from the outline so no cell can break the rim.
    return field ^ prof.offset(-2.0).extrude(P.CAP_T + 2.0)


def build(mark: str = None, mark_h: float = None):
    """`mark` names a traced-mark module in lib/ (see tools/trace_mark.py).
    Default is the project mark; pass another to get a custom face. Nothing
    else about the cap changes - same bore, same register, same everything
    that has to fit."""
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
    mark2d = _mark_2d(mark, mark_h)
    if P.MARK_ENABLE:
        if mark2d is not None:
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
    cuts.append(_hex_field(prof, mark2d, P.TEX_DEPTH + 0.2)
                .translate([0.0, 0.0, P.CAP_T - P.TEX_DEPTH]))

    return part - union(cuts)


META = dict(
    name="04_flip_cap",
    desc="Bungee flip cap. Cord bosses at 3/9, thumb tab at 6, hex grip, "
         "register pocket that drops over the shroud.",
    orient="Decorated face down - ALREADY ORIENTED. No supports.",
)


def _variant(word, name):
    m = dict(META)
    m["name"] = name
    m["desc"] = ('Custom face: "%s" in place of the centre mark. Dimensionally '
                 'identical to 04 - same register, same cord radius, same '
                 'skirt. Only the debossed face differs.' % word)
    return m


META_FUCK = _variant("FUCK", "04b_flip_cap_FUCK")
META_YOU = _variant("YOU", "04c_flip_cap_YOU")


def inlay(mark: str = None, mark_h: float = None):
    """The LETTERING as a separate solid, exactly filling the recess that
    build() cuts. Load it as a second part of the same object and give it
    another filament.

    It fills the recess FLUSH rather than part way. Two reasons, and the
    second is the interesting one:

      * a partial fill would leave the inlay floating over the void beneath
        it, since the decorated face prints downward.
      * flush is better anyway. In one colour, every letter's floor is a
        ceiling bridged over air. Filled with a second filament there is no
        void left to bridge - the letters build off the plate like the rest
        of the first layer. The multicolour version is the EASIER print.

    Same origin and orientation as build(), so the two line up with nothing
    to position in the slicer.
    """
    return _mark_2d(mark, mark_h).extrude(P.MARK_DEPTH) \
        .translate([0.0, 0.0, P.CAP_T - P.MARK_DEPTH])


def hex_inlay(mark: str = None, mark_h: float = None):
    """The DIMPLE FIELD as a separate solid - the other half of a two-tone
    face. One plug per cell, each filling its dimple flush.

    The plugs are islands, but never orphaned ones: the body's own first
    layer prints around every plug in the same pass, so each is fenced in
    on all six sides before the nozzle leaves it. Same argument as the
    lettering - filled, there is no dimple floor left to bridge.

    It has to be given the SAME mark as the cap it fills. The keep-out
    around the lettering is what decides which cells exist at all, so a
    FUCK cap filled with a YOU field would have plugs standing where the
    letters are and holes where the field should be.

    The cost is swaps. The lettering is one compact region inside a five
    layer band; the field is 30-40 cells spread over the whole face, so
    every one of those layers wants a tool change and a purge either way.
    Budget for it, or print the lettering alone.
    """
    return _hex_field(outline(), _mark_2d(mark, mark_h), P.TEX_DEPTH) \
        .translate([0.0, 0.0, P.CAP_T - P.TEX_DEPTH])


def _inlay_meta(name, what, cap_file):
    return dict(
        name=name,
        desc="EXTRA FILAMENT, optional. %s Load %s first, then Add Part -> "
             "Load this, and assign it another colour. It shares an origin "
             "with the cap - do not move it." % (what, cap_file),
        orient="Arrives aligned to the cap. Do NOT reposition or reorient.",
        hardware="None. Needs a multi-material printer (AMS/H2C).",
    )


def _inlay_pair(mark_name, hex_name, cap_file, what):
    """(lettering meta, hex field meta) for one cap. The names match the
    FILENAME map in build.py; a meta that says one thing while the file is
    called another is how a part gets loaded onto the wrong cap."""
    return (
        _inlay_meta(mark_name, what + " lettering alone.", cap_file),
        _inlay_meta(hex_name,
                    "The hex dimple field alone: 30-40 plugs, one per "
                    "dimple. Costs more purge than the lettering does.",
                    cap_file),
    )


META_INLAY, META_INLAY_HEX = _inlay_pair(
    "04_inlay_mark", "04_inlay_hex", "04_flip_cap", "The centre mark")
META_INLAY_FUCK, META_INLAY_HEX_FUCK = _inlay_pair(
    "04b_inlay_FUCK", "04b_inlay_hex_FUCK", "04b_flip_cap_FUCK", 'The "FUCK"')
META_INLAY_YOU, META_INLAY_HEX_YOU = _inlay_pair(
    "04c_inlay_YOU", "04c_inlay_hex_YOU", "04c_flip_cap_YOU", 'The "YOU"')
