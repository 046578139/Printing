"""
Single source of truth for every dimension in the NVG objective cap set.

Target hardware : NOCTIS mil-spec objective glass in Nocturn Industries
                  Raptor housings (AN/PVS-14 pattern objective interface).
Retention       : 1/8 in (3.175 mm) shock cord.
Prototype       : Bambu Lab H2C, PETG.
Production      : carbon-filled (PET-CF / PAHT-CF).

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

OBJ_FRONT_OD    = 38.00   # [VERIFY] OD of the fixed front bezel the shroud grips
OBJ_FRONT_LEN   = 10.00   # [VERIFY] usable straight length of that bezel
OBJ_COLLAR_OD   = 41.00   # [VERIFY] OD of the non-rotating body the collar clamps
OBJ_COLLAR_LEN  = 12.00   # [VERIFY] usable straight length there

# Global bore trim. Nudge this one number instead of editing each part:
#   too tight  -> +0.10
#   too loose  -> -0.10
# Carbon-filled filaments shrink more than PETG; expect roughly +0.15 here
# when moving from PETG to PET-CF / PAHT-CF.
BORE_BIAS       = 0.00


# ==========================================================================
# RETENTION CORD
# ==========================================================================
CORD_DIA        = 3.175   # 1/8 in shock cord, nominal
CORD_HOLE       = 3.90    # free-running clearance hole (cord must slide)
CORD_KNOT_D     = 8.50    # overhand knot in 1/8 in cord, for clearance pockets


# ==========================================================================
# FIT CLASSES  --  diametral clearance added to a bore
# ==========================================================================
FIT_PRESS       = 0.15    # shroud onto objective: hand-press, stays put
FIT_SLIP        = 0.40    # collar onto objective: slides, then screw-clamped
FIT_LOCATE      = 0.45    # cap over shroud register: drops on, self-centres
FIT_CLEAR       = 0.60    # general non-critical clearance


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
SHROUD_SLOTS    = 4
SLOT_W          = 1.60
SLOT_LEN        = 6.40    # < SHROUD_GRIP_LEN, so the kill flash seat stays a full ring
SLOT_END_R      = 0.80    # rounded slot end: a square corner is a crack starter

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
CORD_RADIUS     = 26.00
CORD_EDGE_WALL  = 2.55   # material left outboard of the cord hole

# Knurl band for grip with gloves.
KNURL_START     = 3.20
KNURL_LEN       = 6.40
KNURL_DEPTH     = 0.55
KNURL_COUNT     = 40
KNURL_ANGLE     = 32.0


# ==========================================================================
# 03  KILL FLASH INSERT
# ==========================================================================
KF_OD           = SHROUD_BORE - 0.25       # light press into the shroud bore
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
COL_BORE        = OBJ_COLLAR_OD + FIT_SLIP + BORE_BIAS
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
GAUGE_STEP      = 0.50
GAUGE_COUNT     = 9       # odd, so the nominal lands in the middle
GAUGE_SPINE_W   = 4.00
GAUGE_SPINE_T   = 2.00
GAUGE_TEXT_H    = 4.20
GAUGE_TEXT_D    = 0.60
GAUGE_PITCH_PAD = 3.00


def summary() -> str:
    return "\n".join([
        "  objective front OD (verify) : %6.2f" % OBJ_FRONT_OD,
        "  objective collar OD (verify): %6.2f" % OBJ_COLLAR_OD,
        "  bore bias                   : %+6.2f" % BORE_BIAS,
        "  shroud bore / OD            : %6.2f / %.2f" % (SHROUD_BORE, SHROUD_OD),
        "  kill flash OD / thickness   : %6.2f / %.2f" % (KF_OD, KF_THICK),
        "  collar bore / OD            : %6.2f / %.2f" % (COL_BORE, COL_OD),
        "  cap OD                      : %6.2f" % CAP_OD,
        "  cord hole                   : %6.2f  (1/8 in cord)" % CORD_HOLE,
        "  cord line radius            : %6.2f  (collar ear == cap boss)" % CORD_RADIUS,
    ])
