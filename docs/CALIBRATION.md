# Calibration log

This whole design hangs on two hardware diameters, and both were read off a
printed gauge rather than measured directly. A gauge reading is only valid
in the material, printer and settings it was taken in — so it is worth
writing down what those were, because in six months nobody remembers.

Add a row every time you gauge. Fill in the filament SKU and lot: Bambu
reformulates and discontinues filaments, and a calibration pinned to a spool
you cannot re-buy expires silently.

## Readings

### Front bezel — `OBJ_FRONT_OD`

| Date | Pass | Material | Ladder | Result |
|---|---|---|---|---|
| 2026-09-21 | coarse | PLA | 36.15 → 40.15, 0.50 steps | **36.65 would not go on; 37.15 went on loose** → bracketed between them |
| 2026-09-21 | fine | PLA | 36.60 → 37.20, 0.10 steps | **36.90 wins** — mid-ladder, not at an edge |
| | production | PAHT-CF | 36.85 → 37.15, 0.05 steps | *pending — needs a 2–3 week soak before reading* |
| | **re-gauge** | **PLA on a 0.40 nozzle** | 36.45 → 37.05, 0.10 steps | *pending — the reading above is not valid on this hotend* |

**In force:** `OBJ_FRONT_OD = 36.90 − FIT_PRESS = 36.75`, gauged in **PLA on a
0.60 nozzle at 0.30 layers**.

> **That reading is now stale.** The printer has moved to 0.40 / 0.20. A
> delivered bore is as much a property of the nozzle as of the material — a
> 0.60 nozzle undersizes a hole by roughly 0.20–0.35 mm, a 0.40 by roughly
> 0.10–0.20 — so the shift is larger than the entire 0.15 mm design
> clearance. The press fit will have become a slip fit.
>
> `params.py` now carries `CAL_NOZZLE` / `CAL_LAYER` alongside
> `CAL_MATERIAL`, and the build summary prints
> `*** CALIBRATION STALE - RE-GAUGE ***` until they agree. Print
> `05_gauge_shroud_regauge04`, read it, set `OBJ_FRONT_OD` and then set
> `CAL_NOZZLE = 0.40`, `CAL_LAYER = 0.20`.

Worth noting: that is **1.3 mm under** the AN/PVS-14 nominal this project
started from. The nominal was a starting point and it was wrong, which is
the entire reason the gauge exists.

Filament SKU / lot: _________________

### Collar barrel — `OBJ_COLLAR_OD`

| Date | Pass | Material | Ladder | Result |
|---|---|---|---|---|
| | coarse | PLA | 37.00 → 43.00, 0.60 steps | *pending* |

**Not yet read.** Still sitting on its unverified 41.00, and suspect for the
same reason the bezel was — do not print a collar against it.

Criterion here is different from the bezel: you want the ring that **just
slides on** with a barely perceptible wobble, not one that presses. The
screw takes up the rest.

Filament SKU / lot: _________________

## How to read a ladder

- **Press fit (housing):** the largest ring that still needs firm thumb
  pressure to seat and does **not** fall off when you invert the goggle.
  A ring that needs a mallet is too tight; one that slides on under its own
  weight is too loose.
- **Slip fit (collar):** the ring that just slides on freely with a barely
  perceptible wobble.

Then `OBJ_* = <winning ring label> − <the fit class>`, because the rings are
labelled with their modelled bore and that already includes the allowance.

## Why the material matters so much

A delivered bore is the net of shrinkage, die swell and hole undersize —
all process and material properties, none of them geometry. That is why
`params.py` carries `CAL_MATERIAL` and `PRINT_MATERIAL` rather than a bare
bias number: set them equal and the bias is exactly zero, which is the only
case that is genuinely *measured*.

The clean way to move to production is not to trust the estimate in the
table. Print a fine ladder in the production filament, read it, and set both
material fields to that filament. Everything then cancels identically and
the bias goes back to zero. It costs 15 g and 20 minutes.

**If that filament is a nylon, condition it first.** PAHT-CF takes up
moisture and grows; diffusion through the wall is roughly 12 days to 90 %.
Leave the ladder at ambient for **2–3 weeks** before you judge it. A ring
read at 48 hours is not its final size, and skipping this is the most
likely way to end up with a housing that fits on the bench and is tight a
month later.
