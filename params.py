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

OBJ_FRONT_OD    = 36.75   # [CONFIRMED in PLA] fine ladder (0.10 steps) picked
                          # modelled bore 36.90, mid-ladder rather than at an
                          # edge. 36.90 - FIT_PRESS = 36.75. Valid in PLA only -
                          # re-gauge in the production filament. See
                          # docs/CALIBRATION.md.
OBJ_FRONT_LEN   = 13.00   # [CONFIRMED] the bezel inserts the full bore depth
OBJ_COLLAR_OD   = 36.90   # [TRIANGULATED, not yet gauged] Two oversized test
                          # prints agree: the 39.00 snap ring read ~2 mm loose
                          # and the 42.20 bolt-on ~5 mm loose, which both land
                          # on a ~37.0 seat. So it is NOT much smaller than the
                          # 36.75 front bezel - it is essentially the same
                          # diameter. Confirm on the 30-42 ladder.
OBJ_COLLAR_LEN  = 12.00   # [VERIFY] usable straight length there

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
CAL_MATERIAL    = "PLA"      # material of the gauge that set OBJ_FRONT_OD
PRINT_MATERIAL  = "PLA"      # material you are printing the parts in NOW

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
    "PETG":   +0.05,   # estimate
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
NOZZLE          = 0.60
LAYER           = 0.30

# A single-extrusion wall has to be at least ~1.1x the nozzle or the slicer
# refuses it and the feature silently disappears. The first kill flash used
# 0.45 mm cells on a 0.60 nozzle - 75% of nozzle diameter - and every cell
# wall was dropped. The part came off the plate as a bare rim.
THIN_WALL       = round(NOZZLE * 1.25, 2)   # reliable single pass
WALL_MIN        = round(NOZZLE * 3, 2)      # 3 perimeters, load-bearing
WALL_STD        = round(NOZZLE * 6, 2)      # 6 perimeters, structural
# A deboss or emboss needs 3 layers to read cleanly, not 2.
DETAIL_DEPTH    = round(LAYER * 3, 2)
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
KF_FIT          = 0.30                             # diametral, press fit
KF_SINK         = 0.20                             # sits this far below flush
KF_OD           = KF_RECESS_D - KF_FIT
KF_THICK        = KF_RECESS_LEN - KF_SINK

# 0.80 mm is exactly two 0.40 extrusions. The first insert used 0.45 mm
# single-extrusion walls and the slicer dropped every one of them - the part
# came off the plate as a bare rim. Two full perimeters is the smallest wall
# that is not at the mercy of thin-wall detection.
KF_WALL         = THIN_WALL
KF_CELL_AF      = 4.20
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
CAP_BOSS_D      = 8.20
CAP_BOSS_PROJ   = CORD_RADIUS + CAP_BOSS_D / 2 - CAP_OD / 2
CAP_T           = CAP_FACE_T + CAP_SKIRT_DEPTH   # total cap thickness

# Thumb tab on the lower edge - hook a gloved thumb under it and flip up.
TAB_W           = 17.00
TAB_PROJ        = 5.40
TAB_T           = 4.60
TAB_UNDERCUT    = 1.80

# Grip texture panels at 12 and 6 o'clock.
TEX_CELL        = 2.60
TEX_DEPTH       = DETAIL_DEPTH
TEX_WALL        = round(NOZZLE * 1.6, 2)

# Centre mark. Generic chevron/mountain deboss - swap or disable freely.
MARK_ENABLE     = True
MARK_W          = 18.00
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


def summary() -> str:
    return "\n".join([
        "  objective front OD (verify) : %6.2f" % OBJ_FRONT_OD,
        "  objective collar OD (verify): %6.2f" % OBJ_COLLAR_OD,
        "  calibrated in / printing in : %s / %s" % (CAL_MATERIAL, PRINT_MATERIAL),
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
    ])
