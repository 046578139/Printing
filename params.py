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

OBJ_FRONT_OD    = 36.75   # [BRACKETED] from the coarse gauge: modelled bore 36.65
                          # would not go on, 37.15 went on loose. Provisional
                          # centre 36.90 => 36.90 - FIT_PRESS. Confirm with the
                          # 0.10 mm fine ladder before printing a full set.
OBJ_FRONT_LEN   = 10.00   # [VERIFY] usable straight length of that bezel
OBJ_COLLAR_OD   = 41.00   # [STILL UNVERIFIED - and now suspect. The front bezel
                          # came in 1.3 mm under its PVS-14 nominal, so this one
                          # probably is too. The coarse collar ladder may not even
                          # have bracketed it. Do not print a collar until this is
                          # read off a gauge.]
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
NOZZLE          = 0.40
LAYER           = 0.20
WALL_MIN        = 1.20    # 3 perimeters, minimum for a load-bearing wall
WALL_STD        = 2.40    # 6 perimeters, standard structural wall
THIN_WALL       = 0.45    # single-extrusion wall (kill flash cells)
FIRST_LAYER_SQUISH = 0.00 # set to ~0.05 if your first layer elephant-foots


# ==========================================================================
# 02  KILL FLASH HOUSING (shroud)
# ==========================================================================
SHROUD_BORE     = OBJ_FRONT_OD + FIT_PRESS + BORE_BIAS
SHROUD_WALL     = 3.40
SHROUD_OD       = SHROUD_BORE + 2 * SHROUD_WALL      # ~44.9
SHROUD_GRIP_LEN = 8.00    # how far it swallows the objective bezel
SHROUD_LEAD_IN  = 1.20    # rear chamfer so it starts onto the lens squarely

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
KF_FIT          = 0.25                     # light press of the insert into the bore
KF_OD           = SHROUD_BORE - KF_FIT
KF_THICK        = 5.00                     # depth of the honeycomb
KF_CELL_AF      = 4.00                     # hex across-flats
KF_WALL         = THIN_WALL
KF_RIM          = 1.10                     # solid outer rim
KF_CHAMFER      = 0.50
# Open-area fraction ~= (AF/(AF+wall))^2 ~= 0.80
# Cutoff angle      ~= atan(AF/THICK)     ~= 39 deg off-axis


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
TEX_CELL        = 1.80
TEX_DEPTH       = 0.60
TEX_WALL        = 0.60

# Centre mark. Generic chevron/mountain deboss - swap or disable freely.
MARK_ENABLE     = True
MARK_W          = 17.00
MARK_DEPTH      = 0.70


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
GAUGE_TEXT_D    = 0.60
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
