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
| 2026-09-21 | coarse | PLA, 0.60 nozzle | 36.15 → 40.15, 0.50 steps | 36.65 would not go on; 37.15 went on loose → bracketed |
| 2026-09-21 | fine | PLA, 0.60 nozzle | 36.60 → 37.20, 0.10 steps | 36.90 — superseded, read on the wrong hotend |
| 2026-09-21 | **re-gauge** | **PLA, 0.40 nozzle, 0.20 layer** | 36.45 → 37.05, 0.10 steps | **36.85 wins** — mid-ladder, not at an edge |
| | production | PAHT-CF | 36.85 → 37.15, 0.05 steps | *pending — needs a 2–3 week soak before reading* |

**In force:** `OBJ_FRONT_OD = 36.85 − FIT_PRESS = 36.70`, gauged in **PLA on
a 0.40 nozzle at 0.20 layers**. `CAL_NOZZLE` / `CAL_LAYER` now agree with
`NOZZLE` / `LAYER`, so the build summary no longer flags the calibration as
stale.

Confirmed on hardware: the housing built against this number "slides on and
is a very tight fit, and fully bottoms out on the top where it should."

The 0.60 nozzle reading came out 0.05 larger than the 0.40 one, which is the
right sign and about the right size — a fatter nozzle undersizes a hole
more, so the winning *ring* has to be labelled larger to deliver the same
bore. It is worth keeping the superseded row visible for exactly that
reason: it is the evidence that the provenance columns are doing real work.

Worth noting: this is **1.45 mm under** the AN/PVS-14 nominal this project
started from. The nominal was a starting point and it was wrong, which is
the entire reason the gauge exists.

Filament SKU / lot: _________________

### Collar seat — `OBJ_COLLAR_OD`

| Date | Pass | Material | Ladder | Result |
|---|---|---|---|---|
| 2026-09-21 | *triangulated* | — | — | **36.90 assumed**, from the bezel reading — NOT measured |
| | direct | PLA, 0.40 nozzle | `pinch-bore` sweep, 35.60 → 36.80, 0.30 steps | *pending* |

**Still triangulated, not gauged.** The 36.85 ring was read on the front
bezel; the collar sits further back, and nothing has yet been put on that
section of barrel. 36.90 is an inference, and it is the last unverified
dimension in the set.

It is also the one dimension a gauge ring cannot settle on its own. A ring
tells you what diameter slides on; it cannot tell you how much
*interference* a spring ring wants in order to hold the cap's orientation
without being unfittable. So this one is read from the **`pinch-bore`
sweep** instead of a ladder: print all five, fit each over the bare bezel,
and keep the largest bore that still cannot be twisted by hand once seated.
That single plate settles the seat diameter and the grip together.

Criterion, if you do run a plain ladder here: the ring that **just slides
on** with a barely perceptible wobble — a slip fit, not a press. The spring
(or the screw, on 01) takes up the rest.

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
