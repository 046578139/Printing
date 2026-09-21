"""
Single source of truth for every dimension in the NVG objective cap set.

Target hardware : NOCTIS mil-spec objective glass in Nocturn Industries
                  Raptor housings (AN/PVS-14 pattern objective interface).
Retention       : 1/8 in (3.175 mm) shock cord.
Prototype       : Bambu Lab H2C, PLA Basic (NOT PETG - see docs/PRINTING.md).
Production      : PAHT-CF for the parts that grip the optic, ASA for the
                  kill flash and cap. See docs/PRINTING.md for why.

HOW TO USE THIS FILE
--------------------
Only the numbers in the "MEASURED" block should ever need to change.
Everything else derives from them. Print `05_gauge_shroud.stl` and
`06_gauge_collar.stl` first, find the rings that fit, and type those two
numbers into OBJ_FRONT_OD / OBJ_COLLAR_OD below. Then rebuild.

All units are millimetres, all angles degrees.
"""

# ==========================================================================
# MEASURED  --  the only numbers tied to physical hardware
# ==========================================================================
# !! THESE TWO ARE NOMINAL AN/PVS-14-PATTERN VALUES, NOT MEASURED OFF YOUR
# !! HARDWARE. Confirm them with the printed gauges before committing to a
# !! full set. See docs/MEASUREMENTS.md.

OBJ_FRONT_OD    = 36.65   # [GAUGED] PETG, 0.40 nozzle, 0.12 layer. The 36.80
                          # ring is very tight but goes on; 36.90 is loose
                          # enough to slide off. Bracketed, not bounded.
                          #
                          # This is NOT a caliper reading of the bezel and is
                          # not meant to be. It is (bezel diameter + whatever
                          # this material, nozzle and layer do to a hole), and
                          # holding it that way is the whole point: every part
                          # downstream is printed on the same setup, so the
                          # process offset cancels instead of being estimated.
                          # It stays true only while CAL_MATERIAL, CAL_NOZZLE
                          # and CAL_LAYER match what is in the machine.
                          #
                          # PLA at 0.20 read 36.85 on the same criterion, so
                          # this setup delivers 0.05 larger for the same
                          # modelled bore. Material and layer moved together,
                          # so that 0.05 is the pair of them, not either alone.
OBJ_FRONT_LEN   = 13.00   # [CONFIRMED] the bezel inserts the full bore depth
# WHICH SEAT. The collar goes on the LOCKING COLLAR - the fixed band
# immediately behind the focus ring - and NOT on the front bezel the housing
# grips. Two reasons, and the second one is the stronger:
#
#  1. The bezel turns to focus and has a little wobble in it. Hanging the
#     collar, the cord tension and the cap's weight off a part that has to
#     rotate is asking for a stiff focus and a worn thread.
#
#  2. The cap's register on the housing is CIRCULAR, so nothing about it sets
#     rotation. The cap's orientation is held entirely by the two cords, and
#     the cords anchor to this collar. On the fixed locking collar, focusing
#     just spins the housing underneath the cap and the thumb tab stays where
#     you left it. On the bezel, every focus adjustment drags the cap's
#     orientation round with it.
#
# The housing still presses on the bezel and so still turns with focus. That
# is fine - it becomes the focus grip - but it is why the collar must not.
OBJ_COLLAR_OD   = 36.90   # [TRIANGULATED, not yet gauged] Two oversized test
                          # prints agree: the 39.00 snap ring read ~2 mm loose
                          # and the 42.20 bolt-on ~5 mm loose, which both land
                          # on a ~37.0 seat. This was read as a barrel section;
                          # now that the seat is known to be the locking collar
                          # it may well be FATTER. 01g's cinch ladder brackets
                          # 35.29-41.20 and settles it without a gauge.
OBJ_COLLAR_LEN  = 12.00   # [VERIFY - and now the number that matters most]
                          # The locking collar is a narrow band. If it is under
                          # COL_HEIGHT the collar rides up onto the focus ring
                          # and reintroduces exactly the binding it was moved
                          # to avoid. 01g ships in two heights for this reason.

# --------------------------------------------------------------------------
# Bore calibration and material provenance
# --------------------------------------------------------------------------
# OBJ_FRONT_OD above was read off a gauge printed in ONE specific material.
# That number is only valid in that material: a bore delivered by FDM is the
# net of shrinkage, die swell and hole undersize, all of which are material
# and process properties, not geometry.
#
# So record what you calibrated in, and declare what you are printing now.
# The bias is then just the difference between the two, and setting it
# wrongly is no longer possible by forgetting.
CAL_MATERIAL    = "PETG"      # material of the gauge that set OBJ_FRONT_OD
PRINT_MATERIAL  = "PETG"      # material you are printing the parts in NOW

# ...and the hotend it was gauged on. A delivered bore is as much a property
# of the nozzle as of the material: a 0.60 nozzle undersizes a hole by
# roughly 0.20-0.35 mm, a 0.40 by roughly 0.10-0.20. Moving between them
# shifts every fit by more than the whole design clearance, so a calibration
# taken on one hotend is simply not valid on the other.
CAL_NOZZLE      = 0.40       # 36.80 ring read on the 0.40 nozzle
CAL_LAYER       = 0.12
# Set these to NOZZLE / LAYER once the fine ladder has been re-read on the
# new hotend, and BORE_BIAS goes back to being exactly zero.


def calibration_is_stale() -> bool:
    """True when the fit numbers were taken on a setup that would deliver a
    different BORE.

    Nozzle and material only. Every fit in this set is a vertical bore, and a
    vertical bore's delivered diameter is set by the extrusion width and how
    the slicer plans the perimeter around a curve - both functions of the
    nozzle. Layer height changes how many of those perimeters are stacked,
    not where any of them goes.

    That is not the same as "layer height does not matter": see
    calibration_note(). It just is not worth throwing away a hard-won
    measurement over, and crying wolf is how a staleness flag gets ignored.
    """
    return (abs(CAL_NOZZLE - NOZZLE) > 1e-9
            or CAL_MATERIAL != PRINT_MATERIAL)


def calibration_note() -> str:
    """Second-order caveats on an otherwise valid calibration."""
    if abs(CAL_LAYER - LAYER) < 1e-9:
        return ""
    return ("gauged at %.2f layers, printing at %.2f - second order for a "
            "vertical bore, but re-check the press if it feels different"
            % (CAL_LAYER, LAYER))

# How much must be ADDED to a modelled bore to land the same DELIVERED bore
# as PLA Basic. More shrinkage -> smaller delivered bore -> positive number.
#
# There is no single "carbon filled" value: chopped fibre SUPPRESSES matrix
# shrinkage, so the direction follows the matrix. Amorphous PET-CF lands on
# top of PLA; the semi-crystalline nylons do not.
#
# Only the PLA row is measured. Everything else is an estimate, and a fine
# gauge printed in the production filament beats every one of them - see
# docs/MEASUREMENTS.md. Re-gauging costs 15 g and 20 minutes.
BORE_SHIFT = {
    "PLA":     0.00,   # reference
    "PLA-CF":  0.00,
    "PETG":   -0.05,   # MEASURED - and the sign was wrong before.
                       # PETG delivers a LARGER hole than PLA for
                       # the same modelled bore, so it needs less
                       # added, not more. The table said +0.05.
    "ASA":    +0.10,   # estimate
    "PET-CF":  0.00,   # estimate; amorphous, CF-suppressed shrink
    "PAHT-CF":+0.10,   # estimate; semi-crystalline
    "PPA-CF": +0.10,   # estimate; semi-crystalline
}

for _m in (CAL_MATERIAL, PRINT_MATERIAL):
    if _m not in BORE_SHIFT:
        raise ValueError("unknown material %r - add it to BORE_SHIFT" % _m)

# Extra manual trim on top, if a part still comes out tight or loose:
#   too tight -> +0.10 ... too loose -> -0.10
BORE_TRIM       = 0.00

BORE_BIAS = BORE_SHIFT[PRINT_MATERIAL] - BORE_SHIFT[CAL_MATERIAL] + BORE_TRIM


# ==========================================================================
# RETENTION CORD
# ==========================================================================
CORD_DIA        = 3.175   # 1/8 in shock cord, nominal
CORD_HOLE       = 3.90    # free-running clearance hole (cord must slide)
CORD_KNOT_D     = 8.50    # overhand knot in 1/8 in cord, for clearance pockets

# One boss diameter for every cord anchor in the set. The collar's ears used
# to be square slabs sitting next to a cap with round bosses, which read as
# two parts from two different designs. They are now the same profile.
CORD_BOSS_D     = 8.20


# ==========================================================================
# FIT CLASSES  --  diametral allowance added to a bore
# ==========================================================================
# Note what these actually are: FIT_PRESS is ADDED, so the modelled bore is
# 0.15 mm LARGER than the bezel. The real interference comes from FDM hole
# undersize, which is process- and material-determined, not from the CAD.
# That is fine, because the gauge measures the DELIVERED bore rather than the
# nominal - but it is exactly why no fit number ever transfers between
# materials, and why you re-gauge for every production filament.
FIT_PRESS       = 0.15    # shroud onto objective: hand-press, stays put
FIT_SLIP        = 0.40    # collar onto objective: slides, then screw-clamped
FIT_LOCATE      = 0.35    # cap over shroud register: drops on, self-centres
FIT_CLEAR       = 0.60    # general non-critical clearance

# Optional sacrificial liner in the collar bore. Carbon fibre against a
# coated objective barrel was NOT cleared: the polymer is the grit-embedding
# member in mud, and carbon/aluminium is a galvanic couple in salt and rain.
# 0.13 mm self-adhesive PTFE or UHMW tape is non-conductive, slippery, inert
# and sacrificial. Set this to the tape thickness and the bore opens to suit.
# Do NOT use TPU for this: abrasive embeds in the softer member and laps the
# harder one, which turns the liner into a grit-charged lap against the barrel.
LINER_T         = 0.00


# ==========================================================================
# PRINT PROCESS  --  0.4 mm nozzle, 0.2 mm layer
# ==========================================================================
# THE NOZZLE IS A DESIGN INPUT, not a slicer setting. Every thin feature in
# this project is sized off it, so changing nozzle and rebuilding is the
# supported way to move between machines - editing feature sizes by hand is
# not.
NOZZLE          = 0.40
LAYER           = 0.12

# What actually limits a thin feature is the EXTRUSION WIDTH, not the nozzle
# bore. Bambu defaults a 0.40 nozzle to 0.42 and a 0.60 to about 0.62, so
# sizing off the nozzle alone is slightly optimistic. Read this off the
# slicer's "Default" line width and keep it honest.
LINE_WIDTH      = 0.42

# A single-extrusion wall has to be at least ~1.1x the nozzle or the slicer
# refuses it and the feature silently disappears. The first kill flash used
# 0.45 mm cells on a 0.60 nozzle - 75% of nozzle diameter - and every cell
# wall was dropped. The part came off the plate as a bare rim.
THIN_WALL       = round(LINE_WIDTH * 1.20, 2)  # reliable single pass
WALL_MIN        = round(NOZZLE * 3, 2)      # 3 perimeters, load-bearing
WALL_STD        = round(NOZZLE * 6, 2)      # 6 perimeters, structural
# A deboss or emboss needs 3 layers to read cleanly, not 2.
# How deep a debossed feature is cut. NOT derived from the layer height.
#
# It used to be LAYER * 3, which has the dependency backwards: finer layers
# would give SHALLOWER detail, so dropping to 0.12 would have quietly taken
# the hex dimples and the P from 0.60 deep to 0.36 and washed the cap out.
# Depth is a design intent - how pronounced should it look - and the layer
# height is a CONSTRAINT on it, not its source. The constraint is enforced in
# tests.py: at least three layers, or the feature does not read.
DETAIL_DEPTH    = 0.60
FIRST_LAYER_SQUISH = 0.00 # set to ~0.05 if your first layer elephant-foots

# THE PLATE-FACE RULE. Never chamfer the face that goes down on the plate.
# A 0.6 mm chamfer on the bottom of a 3.2 mm band leaves a 2.0 mm first layer
# that then widens over the next few layers - which prints ragged for three
# or four layers and only cleans up once it reaches full width. Every part
# here now leaves its plate face perfectly flat and takes its edge break on
# the top instead. Costs nothing; it was the single worst print defect in
# the first round.
PLATE_FACE_CHAMFER = 0.00


# ==========================================================================
# 02  KILL FLASH HOUSING (shroud)
# ==========================================================================
SHROUD_BORE     = OBJ_FRONT_OD + FIT_PRESS + BORE_BIAS
SHROUD_WALL     = 3.40
SHROUD_OD       = SHROUD_BORE + 2 * SHROUD_WALL      # ~44.9
# Depth of the 36.90 bore, i.e. how far the objective goes in before it
# bottoms on the back of the internal flange. CONFIRMED CORRECT on hardware:
# "very tight fit, fully bottoms out where it should". Do not touch it.
#
# This used to be derived as SHROUD_GRIP_LEN + KF_THICK, on the assumption
# that the kill flash lived in a rear pocket. It does not - the objective
# fills the entire bore, which is exactly why the first insert had nowhere
# to go. The bore depth is now its own number so that resizing the kill
# flash can never move the face the objective seats against.
SHROUD_BORE_LEN = 13.00
SHROUD_GRIP_LEN = SHROUD_BORE_LEN
SHROUD_LEAD_IN  = 1.00    # rear bore lead-in, so it starts onto the lens square
SHROUD_REAR_CH  = 0.30    # rear OUTER edge break
# These two eat into the same rear face from opposite sides, and that face is
# only COLLET_WALL wide. At 1.20 + 0.80 on a 1.90 wall they overlapped and
# deleted the rear face outright - the collet fingers feathered to a knife
# edge and the part's first solid layer sat 0.05 mm up. tests.py now checks
# the sum against the wall.

# Collet slots through the grip section. A solid 3.4 mm ring pressed at
# +0.15 onto an objective barrel has a narrow acceptance window and dumps
# real hoop stress into an expensive optic: 0.1 mm too big and it splits or
# scores the barrel, 0.1 mm too small and it falls off. Four axial slots
# turn the grip into a four-finger collet, which spreads the same grip over
# a much wider diameter band at a fraction of the peak stress.
# Set SHROUD_SLOTS = 0 for a solid ring if you would rather have the
# stiffness and can hit the diameter exactly.
# The finger has to be a SPRING, not a stubby plate. Radial compliance goes
# as t^3/L^3, so at the original 3.4 mm wall over a 6.4 mm slot (L/t = 1.88)
# the fingers barely moved and the collet bought almost nothing. There is not
# enough bezel to lengthen the slot, so the OD is relieved over the collet
# instead: 1.90 mm fingers at L/t = 3.16 are 4.7x more compliant, at no cost
# in axial length.
SHROUD_SLOTS    = 4
COLLET_WALL     = 1.90
COLLET_LEN      = 7.20    # < SHROUD_GRIP_LEN
COLLET_OD       = SHROUD_BORE + 2 * COLLET_WALL
COLLET_TAPER    = 0.80    # 45 deg blend back out to full wall
SLOT_W          = 1.60
SLOT_LEN        = 6.00    # < COLLET_LEN, so the kill flash seat stays a full ring
SLOT_KEYHOLE_D  = 2.40    # round crack-arrestor at the slot root, 1.5x slot width
SLOT_EDGE_BREAK = 1.30    # breaks the 8 axial edges the slots leave in the bore

# Front retaining flange: the kill flash loads from the REAR and seats here,
# then the objective traps it. No snap ring, no glue, fully serviceable.
SHROUD_APERTURE = 33.00   # clear aperture; PVS-14 glass is ~26 mm, no vignette
SHROUD_FLANGE_T = 1.60

# Cap register: a short spigot the flip cap drops over so it self-centres.
REG_HEIGHT      = 2.20
REG_OD          = SHROUD_OD - 2.60
REG_CHAMFER     = 0.60

# The bungee runs straight forward from the collar ear to the cap boss, well
# outboard of the shroud, so both cord holes sit on ONE radius. Change this
# and both parts follow.
CORD_RADIUS     = SHROUD_OD / 2 + 4.20
CORD_EDGE_WALL  = 2.55   # material left outboard of the cord hole

# Knurl band for grip with gloves.
KNURL_START     = 8.60
KNURL_LEN       = 4.00
KNURL_DEPTH     = 0.55
KNURL_COUNT     = 40
KNURL_ANGLE     = 32.0


# ==========================================================================
# 03  KILL FLASH INSERT
# ==========================================================================
# It goes into the housing's FRONT recess, not into a rear pocket. The
# objective bottoms against the back of the internal flange and fills the
# whole 36.90 bore, so there is no rear pocket to put it in - which is why
# the first one would not fit. It slides into the front, presses, and sits
# just under flush; the cap covers it.
KF_RECESS_D     = SHROUD_APERTURE                  # the front bore, 33.00
KF_RECESS_LEN   = SHROUD_FLANGE_T + REG_HEIGHT     # depth of that recess
KF_FIT          = 0.10                             # diametral. Was 0.30 and
                                                   # read slightly loose on hardware.
KF_SINK         = 0.20                             # sits this far below flush
KF_OD           = KF_RECESS_D - KF_FIT
KF_THICK        = KF_RECESS_LEN - KF_SINK

# 0.80 mm is exactly two 0.40 extrusions. The first insert used 0.45 mm
# single-extrusion walls and the slicer dropped every one of them - the part
# came off the plate as a bare rim. Two full perimeters is the smallest wall
# that is not at the mercy of thin-wall detection.
KF_WALL         = THIN_WALL
KF_CELL_AF      = 4.20   # [CONFIRMED] also the cap's hex, so the two match
KF_RIM          = round(NOZZLE * 2, 2)
KF_CHAMFER      = 0.50    # TOP edge only - insert chamfer-first (see docs)
# Open-area fraction ~= (AF/(AF+wall))^2 ~= 0.68
# Cutoff angle      ~= atan(AF/THICK)     ~= 47 deg off-axis


# ==========================================================================
# 01  RETENTION COLLAR
# ==========================================================================
COL_BORE        = OBJ_COLLAR_OD + FIT_SLIP + BORE_BIAS + 2 * LINER_T
COL_WALL        = 3.20
COL_OD          = COL_BORE + 2 * COL_WALL
COL_HEIGHT      = 11.00
COL_GAP         = 2.60    # pinch gap at 6 o'clock, closes under screw load

# Pinch lugs either side of the gap. M3 socket head cap screw.
LUG_W           = 7.00    # along the circumference, each side of the gap
LUG_H           = 9.00    # in Z
LUG_PROJ        = 8.50    # radially outboard of COL_OD
M3_CLEAR        = 3.40
M3_HEAD_D       = 6.20
M3_HEAD_DEPTH   = 3.40
M3_NUT_AF       = 5.60    # DIN 934 M3 hex nut across flats + clearance
M3_NUT_DEPTH    = 2.80

# --------------------------------------------------------------------------
# 01c  SNAP COLLAR  -- no-tools alternative
# --------------------------------------------------------------------------
# A split C-ring that flexes out of round over the barrel and springs back.
# Wrap must be > 180 deg to capture; past about 240 the spread needed to get
# it over the barrel grows fast, because the chord between the tips is what
# the barrel has to pass through.
SNAP_WRAP       = 230.00  # degrees of band
SNAP_LEADIN     = 8.00    # extra gap degrees at the bore only: a cam ramp so
                          # the barrel pushes the tips open instead of jamming
SNAP_LEADIN_D   = 1.20    # radial depth of that ramp

# Free bore sits this far under the barrel; the interference IS the grip.
# Expressed as a FRACTION of diameter, not a fixed millimetre value: a flat
# 2.00 mm was 4.9 % of a 41 bore but 5.9 % of a 37 one, so it quietly
# demanded more strain as the barrel estimate came down.
SNAP_INTERF_PCT = 0.024
SNAP_INTERF     = OBJ_COLLAR_OD * SNAP_INTERF_PCT
SNAP_BORE       = OBJ_COLLAR_OD - SNAP_INTERF + BORE_BIAS

# --------------------------------------------------------------------------
# 01d  LEVER COLLAR  -- circlip-style, opened by hand
# --------------------------------------------------------------------------
# The push-on ring above is limited to ~230 deg of wrap because the BARREL
# has to force the gap open, and the barrel must pass the chord between the
# tips. Opening the ring by hand removes that limit entirely: expand it,
# slide it on axially, release. The gap then only has to open by
# pi x expansion, which barely changes with wrap - so the ring can wrap much
# further, capture much better, and still take LESS strain to fit.
#
#   290 deg, axial:  gap opens 7.85 mm, 0.70 % install strain,  ~9 N at the tips
#   230 deg, radial: gap opens 5.65 mm, 0.75 % install strain, ~13 N
#
# The catch: at this wrap it CANNOT be pushed on radially. There has to be a
# clear axial path onto the barrel. Coming from the front that means over the
# objective bezel, which is the smaller diameter, so it should be fine - but
# it means the shroud comes off before the collar does.
SNAP_LEVER_WRAP   = 290.00
SNAP_LEVER_INTERF = OBJ_COLLAR_OD * SNAP_INTERF_PCT
SNAP_LEVER_CLEAR  = 0.50   # extra expansion so it slides past the step
SNAP_LEVER_BORE   = OBJ_COLLAR_OD - SNAP_LEVER_INTERF + BORE_BIAS

# Finger paddles at the two tips. Pinch and spread to expand the ring.
LEVER_PROJ      = 9.00    # how far the paddle reaches past the band OD
LEVER_W         = 5.00    # stem width, tangential
LEVER_PAD_W     = 9.50    # head width - this is what your fingertip sits on
LEVER_PAD_T     = 3.50    # head thickness, radial
LEVER_ROUND     = 1.60

# --------------------------------------------------------------------------
# 01e  PINCH COLLAR  -- the one modelled on the recorder mount
# --------------------------------------------------------------------------
# A nearly-closed ring with two small tabs flanking a narrow gap. Pull the
# tabs apart, the ring expands, slide it down over the objective bezel, let
# go. It grips on its own bore; the tabs are handles, not springs.
#
# Arc length is fixed, so growing the bore by X opens the gap by pi*X -
# independent of wrap angle. That is why this can sit at 340 degrees and
# still be easier to open than the 230 degree push-on ring:
#
#   340 deg, expand 1.30 -> gap opens 4.08 mm, 0.37 % strain, ~5 N at the tabs
#   230 deg, push-on     -> gap opens 5.65 mm, 0.75 % strain, ~13 N
#
# It cannot go on radially at this wrap, so it installs COLLAR FIRST, over
# the bare bezel, before the housing.
PINCH_WRAP      = 340.00
PINCH_INTERF    = 0.90    # free bore this far under the seat; this is the grip
PINCH_CLEAR     = 0.40    # extra expansion so it slides rather than scrapes
PINCH_BORE      = OBJ_COLLAR_OD - PINCH_INTERF + BORE_BIAS
PINCH_GAP_AT    = 90.0    # o'clock position of the gap; 90 = top

# 4.00, not 7.00. At 7 the head stood off on a long stem, which is a lever
# arm nobody needs - the squeeze is 3 N - and the most snag-prone thing on
# the part. At 4 the head's inner edge sits 0.70 mm off the band, so it reads
# as a circle stemming straight off the ring, and the whole tab pulls 3 mm
# back inside the cord ears. It costs 12 % more squeeze force and, on 01f,
# 4 degrees of lap to keep the two heads from meeting.
PINCH_TAB_PROJ  = 4.00    # how far a tab reaches past the band OD
PINCH_TAB_W     = 4.20    # stem width
PINCH_TAB_HEAD  = 6.60    # rounded head - this is what your fingertip pulls on
PINCH_ROUND     = 1.40
# Fillet where a tab meets the band. The tabs are handles, but the load you
# put into them all enters the band through this corner, and a sharp internal
# corner on a part whose entire job is to flex is a crack waiting for the
# tenth install. Applied to the whole band+tab profile in one pass, so the
# ends of the gap get rounded too.
PINCH_ROOT_R    = 1.50
PINCH_EDGE      = 0.80    # top edge break; bottom is the plate face, stays flat


# --------------------------------------------------------------------------
# 01f - LAPPED collar. The recorder mount's actual mechanism.
#
# The band wraps PAST 360 so the two ends lap over each other, stepped in
# thickness: the inner arm passes inside the outer one. Each end carries a
# finger tab, and because the ends have CROSSED, squeezing the two tabs
# together shortens the lap - and a band of fixed arc length with less lap
# is a bigger circle. Squeeze to expand.
#
# That is the difference from 01e and it is not a detail. On 01e the tabs sit
# on the band either side of a gap, and expanding the ring moves them APART,
# so it has to be spread. Put each tab on a crossed free END instead and the
# motion reverses.
#
# The step forces one thing: the INNER arm's tab has to get out past the
# outer arm. So the outer arm stops half way up the band and the inner arm's
# tab rides over the top of it. The two tabs end up at different heights,
# which is exactly why they can lap past each other rather than collide.
# 50, and every degree of that is paid for. A tab has to sit INSIDE its own
# arm - a tab centred on the free end hangs half its width past it and welds
# the arm to the body, which locks the ring solid while still passing every
# topology and bore check. So each tab is inset 7 deg from its tip, which
# costs 14 deg of separation; the free ends need 1.5 deg each so they are not
# butted at rest; and the squeeze itself eats 11.9 deg. What is left has to
# keep the two tab heads apart, because they both reach the plate and cannot
# pass. 54 leaves 4.4 mm at full squeeze. Insetting does NOT change the
# mechanism - the arms are rigid, so both tabs turn with their arm by the
# same angle wherever they sit on it.
LAP_DEG         = 54.00   # how far the ends lap at rest
LAP_TAB_INSET   = 7.00    # deg each tab sits inboard of its own free end
LAP_END_CLEAR   = 1.50    # deg between a free end and the step it retreats
                          # from, so nothing is butted solid at rest
LAP_SLIDE       = 0.40    # radial gap between the nested arms
# NOT an even split. The outer arm is a bare strip over its whole height,
# while the inner one gets a full-wall flange back above the sliding gap - so
# an even split leaves the outer arm carrying the squeeze on a third of the
# section and taking 0.81 % where the rest of the ring sees 0.14 %. Moving
# 0.20 mm of wall outward and the divide up to 6.5 drops the worst strain to
# 0.57 % and costs nothing. The inner arm stays above the 1.14 mm that three
# perimeters need at a 0.40 nozzle - do not thin it further to chase this.
LAP_ARM_IN      = 1.20    # inner arm: thin only below the split
LAP_ARM_OUT     = COL_WALL - LAP_SLIDE - LAP_ARM_IN
LAP_SPLIT_Z     = 6.50    # top of the outer arm
LAP_SLIDE_Z     = 0.30    # vertical gap the upper flange bridges
# Each arm is built to overlap its root INTO the body by this much. An arm
# that merely butts the body on a coplanar radial face does not weld to it -
# manifold leaves them as separate shells, exactly as noted in
# prism_chamfered. The part passed as one shell only while the tabs were
# still overhanging their free ends and accidentally welding the arms to the
# body; fixing that fusion is what exposed the butt joints underneath.
LAP_WELD        = 3.00    # deg each arm runs past its root into the body

LAP_AT          = 90.0    # o'clock position of the lap; 90 = top
LAP_INTERF      = 0.90    # free bore this far under the seat; this is the grip
LAP_CLEAR       = 0.40    # extra expansion so it slides rather than scrapes
LAP_BORE        = OBJ_COLLAR_OD - LAP_INTERF + BORE_BIAS

LAP_TAB_PROJ    = PINCH_TAB_PROJ
LAP_TAB_W       = 3.60    # narrower than 01e's: every mm of stem width
                          # costs two degrees of tab inset
LAP_TAB_HEAD    = PINCH_TAB_HEAD
LAP_ROUND       = PINCH_ROUND
LAP_ROOT_R      = PINCH_ROOT_R
LAP_EDGE        = PINCH_EDGE


# --------------------------------------------------------------------------
# 01g - CINCH collar. Held by a zip tie or a loop of cord, not by the plastic.
#
# Every ring above asks PLA to be a spring, and PLA is bad at being a spring:
# it holds on the day you fit it and stress-relaxes afterwards. This one asks
# the plastic to do nothing but transmit load. A band around the outside does
# the clamping, and a nylon zip tie pulled to ~40 N applies an order of
# magnitude more than the 0.22 % seated strain a PLA ring can muster - and,
# unlike the ring, you can re-tension it.
#
# The second thing it buys is that OBJ_COLLAR_OD stops mattering. The seat has
# never been gauged, only triangulated. A 6 mm gap closes 6/pi = 1.91 mm of
# diameter, so ONE part covers 37.20 down to 35.29 - wider than the whole
# plausible spread. There is nothing to get wrong and nothing to sweep.
# CONFIRMED on hardware. Three rungs went on - 37.20, 39.20, 41.20 - and the
# 37.20 is the one that fits the locking collar; the other two were scrapped.
# That brackets the seat at 35.29-37.20 without ever having gauged it, which
# is exactly what the 6 mm gap was for.
CINCH_SLIP      = 0.30    # bore runs OVER the seat; the tie takes up the rest
CINCH_BORE      = OBJ_COLLAR_OD + CINCH_SLIP + BORE_BIAS
CINCH_GAP       = 6.00    # closes 6/pi = 1.91 mm of diameter
CINCH_GAP_AT    = 90.0    # o'clock position of the gap; 90 = top, opposite
                          # nothing, and away from both cord ears

# Tie channel. The wall stays full thickness and the channel is formed by
# standing the rest of the OD PROUD of it, rather than by grooving into a
# 3.20 mm wall and leaving 1.70. Takes a 3.6 mm (40 lb) zip tie flush, a
# 4.8 mm one slightly proud, or 1/8 in shock cord.
CINCH_RIM       = 1.50    # how far the rims stand out past the channel floor
CINCH_CHAN_Z    = 4.50    # channel width. The ramp back out is always equal
                          # to CINCH_RIM so it sits at 45 deg - self-supporting,
                          # and it stops the tie walking up off the channel.
                          # Everything else in the stack, including the ear
                          # thickness, falls out of the height: see
                          # cinchcollar.stack(). The ears ARE the lower
                          # section, so they can never intrude on the channel.
CINCH_ROUND     = 1.80
CINCH_EDGE      = 0.40
# Short variant, for when the locking collar turns out to be a narrow band.
# The channel stays wide enough for a 3.6 mm tie and the ears give up the
# height instead - a cord anchor can afford to be thinner than a tie channel
# can afford to be narrower.
CINCH_SHORT_Z   = 9.00
CINCH_SHORT_CHAN = 3.60

# Cord ears, on every collar, are now circular bosses blended into the band
# with a tapered stem - the same profile as the cap's, instead of the square
# slabs that read as a different part from a different design.
EAR_BOSS_D      = CORD_BOSS_D
# Full boss width, NOT a narrowed neck. A stem thinner than the boss puts a
# waist between the cord hole and the band - which is the smallest section in
# the whole load path, sitting exactly where the shock cord pulls hardest.
# The ear now runs straight out from the band at constant width.
EAR_STEM_W      = CORD_BOSS_D
EAR_ROUND       = 1.80

# Prototype-only wide-gap collar. The production gap of 2.60 mm is worth
# only 0.83 mm of diameter range, which is fine once OBJ_COLLAR_OD is known
# and useless before it. These numbers clamp anywhere from 42.20 down to
# ~38.06, covering the whole plausible spread for this barrel, so the cord
# and flip action can be prototyped before the collar has been gauged.
# Needs an M3 x 30 screw rather than x 16.
COL_PROTO_BORE  = 38.60
COL_PROTO_GAP   = 11.00

# Cord ears at 3 and 9 o'clock. Hole runs fore/aft so the cord exits forward.
EAR_W           = 10.00
EAR_T           = 5.20    # radial thickness
EAR_PROJ        = CORD_RADIUS + CORD_HOLE / 2 + CORD_EDGE_WALL - COL_OD / 2
EAR_FILLET      = 2.60


# ==========================================================================
# 04  FLIP CAP
# ==========================================================================
CAP_FACE_T      = 3.00
CAP_OD          = SHROUD_OD + 7.00        # ~51.9
CAP_FLAT_INSET  = 2.00                    # depth of the four 45 deg flats
CAP_EDGE_R      = 2.40                    # profile corner rounding

CAP_SKIRT_BORE  = REG_OD + FIT_LOCATE
CAP_SKIRT_DEPTH = REG_HEIGHT + 0.40
CAP_SKIRT_WALL  = 2.20

# Cord bosses at 3 and 9 o'clock, hole fore/aft, knot sits proud on the front.
CAP_BOSS_D      = CORD_BOSS_D
CAP_BOSS_PROJ   = CORD_RADIUS + CAP_BOSS_D / 2 - CAP_OD / 2
CAP_T           = CAP_FACE_T + CAP_SKIRT_DEPTH   # total cap thickness

# Thumb tab on the lower edge - hook a gloved thumb under it and flip up.
TAB_W           = 17.00
TAB_PROJ        = 5.40
TAB_T           = 4.60
TAB_UNDERCUT    = 1.80

# Grip texture panels at 12 and 6 o'clock.
# True: hex DIMPLES cut into a flat face. False: a recessed panel with the
# cells left standing proud. Dimples, because the face prints downward - a
# raised cell is an isolated first-layer island and the floor around it is a
# long bridge, which is exactly what the first printed cap showed.
TEX_DIMPLE      = True
# The cap's hex matches the KILL FLASH's cell, not a size of its own. Matching
# the cell is what makes the two read as one object; the land between them is
# free to differ, because the kill flash's is a structural wall carrying the
# grid and the cap's is just a surface ridge between two shallow pockets.
TEX_CELL        = KF_CELL_AF
TEX_FIELD_R     = CAP_OD / 2 - 3.20   # hex field radius; stays clear of the
                                      # cord bosses and the thumb tab
TEX_MARK_CLEAR  = 2.20                # clean space kept around the mark
TEX_DEPTH       = DETAIL_DEPTH
TEX_WALL        = round(NOZZLE * 1.6, 2)

# Centre mark. Generic chevron/mountain deboss - swap or disable freely.
MARK_ENABLE     = True
MARK_TRACED     = True    # use the traced artwork in lib/mark_data.py
MARK_H          = 22.00   # sized by HEIGHT - the glyph is tall and narrow,
                          # and what constrains it is the 19 mm clear band
                          # between the two grip panels, not the cap width
MARK_W          = 18.00   # only used by the fallback chevron
MARK_DEPTH      = DETAIL_DEPTH


# ==========================================================================
# 05/06  FIT GAUGES
# ==========================================================================
GAUGE_RING_H    = 7.00
GAUGE_WALL      = 2.60
# GAUGE_STEP must resolve FIT_PRESS, or the ladder cannot measure the thing
# it exists to measure. At the old 0.50 the step was 3.3x the press fit.
GAUGE_STEP      = 0.25
GAUGE_COUNT     = 11      # odd, so the nominal lands in the middle
GAUGE_SPINE_W   = 4.00
GAUGE_SPINE_T   = 2.00
GAUGE_TEXT_H    = 4.20
GAUGE_TEXT_D    = DETAIL_DEPTH
GAUGE_PITCH_PAD = 3.00


def set_nozzle(nozzle: float, layer: float = None) -> None:
    """Re-derive every nozzle-dependent feature for a different hotend.

    The thin features are computed at import time, so changing NOZZLE alone
    does nothing. Call this instead, then rebuild.

    Changing the nozzle CHANGES THE DELIVERED BORES, which means the fit
    calibration does not carry across - re-gauge afterwards. That is the
    real cost of switching, and it is why it is worth batching with the move
    to production material rather than paying it twice.
    """
    g = globals()
    g["NOZZLE"] = nozzle
    if layer is not None:
        g["LAYER"] = layer
    g["LINE_WIDTH"] = round(nozzle * 1.05, 2)
    g["THIN_WALL"] = round(g["LINE_WIDTH"] * 1.20, 2)
    g["WALL_MIN"] = round(nozzle * 3, 2)
    g["WALL_STD"] = round(nozzle * 6, 2)
    g["KF_WALL"] = g["THIN_WALL"]
    g["KF_RIM"] = round(nozzle * 2, 2)
    g["TEX_DEPTH"] = g["DETAIL_DEPTH"]
    g["TEX_WALL"] = round(nozzle * 1.6, 2)
    g["TEX_CELL"] = g["KF_CELL_AF"]
    g["MARK_DEPTH"] = g["DETAIL_DEPTH"]
    g["GAUGE_TEXT_D"] = g["DETAIL_DEPTH"]


def summary() -> str:
    return "\n".join([x for x in [
        "  objective front OD (verify) : %6.2f" % OBJ_FRONT_OD,
        "  objective collar OD (verify): %6.2f" % OBJ_COLLAR_OD,
        "  calibrated on / printing on : %s %.2f/%.2f  ->  %s %.2f/%.2f%s" % (
            CAL_MATERIAL, CAL_NOZZLE, CAL_LAYER,
            PRINT_MATERIAL, NOZZLE, LAYER,
            "   *** CALIBRATION STALE - RE-GAUGE ***"
            if calibration_is_stale() else ""),
        "  detail depth / layers       : %6.2f / %.1f layers%s" % (
            DETAIL_DEPTH, DETAIL_DEPTH / LAYER,
            "   *** UNDER 3 LAYERS - IT WILL NOT READ ***"
            if DETAIL_DEPTH < LAYER * 3 - 1e-9 else ""),
        ("  note                        : %s" % calibration_note())
        if calibration_note() else "",
        "  bore bias                   : %+6.2f%s" % (
            BORE_BIAS,
            "" if CAL_MATERIAL == PRINT_MATERIAL
            else "  (estimated - re-gauge in %s)" % PRINT_MATERIAL),
        "  shroud bore / OD            : %6.2f / %.2f" % (SHROUD_BORE, SHROUD_OD),
        "  kill flash OD / thickness   : %6.2f / %.2f" % (KF_OD, KF_THICK),
        "  collar bore / OD            : %6.2f / %.2f" % (COL_BORE, COL_OD),
        "  cap OD                      : %6.2f" % CAP_OD,
        "  cord hole                   : %6.2f  (1/8 in cord)" % CORD_HOLE,
        "  cord line radius            : %6.2f  (collar ear == cap boss)" % CORD_RADIUS,
        "  collet finger wall / L-t    : %6.2f / %.2f" % (COLLET_WALL, SLOT_LEN / COLLET_WALL),
        "  bore liner allowance        : %6.2f" % LINER_T,
    ] if x])
