# Measurements — do this before you print anything else

Two numbers decide whether this set works or becomes scrap. Everything else
in `params.py` is derived from them.

| Parameter | What it is | Current value |
|---|---|---|
| `OBJ_FRONT_OD` | OD of the **fixed front bezel** the kill flash housing presses onto | **38.00 — NOT MEASURED** |
| `OBJ_COLLAR_OD` | OD of the **non-rotating barrel section** the collar clamps | **41.00 — NOT MEASURED** |

Those two values are nominal AN/PVS-14-pattern figures. They are a starting
point, not a measurement of your hardware. Nocturn Raptor housings take
PVS-14-pattern objectives, so they should be close — but "close" on a press
fit means the part either splits or slides off.

## Step 1 — measure

With digital calipers, on each objective:

1. **Front bezel OD.** The cylindrical band at the very front of the
   objective, ahead of the focus ring. Take three readings at 60° apart and
   use the **largest**. If the three differ by more than 0.10 mm the bezel is
   out of round; tell me and I will add an ovality allowance.
2. **Front bezel usable length.** How much straight cylinder there is before
   anything steps or knurls. Needs to be ≥ 8.0 mm, or `SHROUD_GRIP_LEN` has
   to come down.
3. **Collar barrel OD.** Pick a band that does **not turn when you focus** —
   this is the one thing most likely to bite. Turn the focus ring and watch:
   whatever moves is off limits. Same three-readings-largest rule.
4. **Collar barrel usable length.** Needs to be ≥ 11.0 mm.

Also worth checking and telling me about:

- Distance from the front bezel face back to where the collar band will sit.
  This sets how much shock cord you need and nothing else.
- Whether the objective already has a sacrificial window or demist shield
  fitted. If it does, the shroud presses onto *that*, not onto the bezel,
  and the diameter is different.
- Interpupillary spacing at the narrowest setting you actually use. The cap
  is Ø52 mm with the cord bosses reaching to Ø60 mm; at a narrow IPD the two
  caps can touch. If that is a problem, `CAP_OD` comes down.

## Step 2 — print the gauges

The gauge is a **null measurement**, and that is the whole trick. Print the
gauge in the same material, on the same plate, with the same first-layer
settings as the real part, and every offset — shrinkage, die swell, hole
undersize, moisture swell — cancels *identically*. You never have to know
what any of them are, and you never have to guess at `BORE_BIAS`.

That means two passes, not one.

### Pass 1 — coarse, in PLA Basic

```
python3 build.py
```

Print `05_gauge_shroud.stl` and `06_gauge_collar.stl`. About 20 minutes
each. PLA is right here: lowest shrink, no drying, no hardened nozzle, and
the most dimensionally honest material on the shelf. This pass brackets the
real diameter and confirms seating depth, cord routing and IPD clearance.

Note the winning ring on each ladder.

### Pass 2 — fine, in the production filament

This is the one that actually sets the number.

```
python3 build.py gauge --nominal <coarse winner> --step 0.05 --count 5
```

Print it in **the exact filament you will produce in**, at your production
settings. About 15 g and 20 minutes.

**If that filament is PAHT-CF (or any nylon), you have to condition it
before you read it.** Nylon absorbs moisture and grows; a ring measured at
48 hours is not its final size. Diffusion through the wall takes roughly
12 days to reach 90 %. Leave it at ambient for **2–3 weeks** before you
judge the fit. The gauge wall is 2.60 mm and the housing wall is 3.40 mm, so
they equilibrate at different rates — give both the full soak.

Skipping this is the single most likely way to end up with a housing that
fits perfectly on the bench and is tight a month later.

## Step 3 — read the gauges

Each ring is labelled with its bore diameter.

- **Shroud gauge:** you want the ring that goes on with *firm thumb
  pressure* and does **not** fall off when you turn the objective upside
  down. That is your press fit. If a ring needs a mallet it is too tight;
  if it slides on under its own weight it is too loose.
- **Collar gauge:** you want the ring that *just slides on* with no force
  and has a barely perceptible wobble. The screw takes up the rest.

Note the number on the winning ring for each.

## Step 4 — set the numbers

Open `params.py` and set:

```python
OBJ_FRONT_OD  = <fine gauge winner>   - FIT_PRESS   # subtract 0.15
OBJ_COLLAR_OD = <collar gauge winner> - FIT_SLIP    # subtract 0.40
BORE_BIAS     = 0.00                                # leave it there
```

The rings are labelled with their **modelled bore**, which already includes
the design allowance, so you subtract it back out to recover the hardware
number. Leave `BORE_BIAS` at zero — because the fine gauge was printed in
the production material, the material offset is already baked into the
winning ring. Then rebuild:

```
python3 build.py && python3 tests.py
```

**Write down the filament SKU and lot number** next to whatever you commit.
Bambu reformulates and discontinues filaments; a calibration pinned to a
spool you cannot re-buy expires silently.

## Step 5 — acceptance test

Before you trust it in the field:

1. Seat the housing. It should take firm thumb pressure.
2. Invert the goggle and shake it. Nothing should move.
3. **Heat soak it** — four hours at 70–80 °C, or an afternoon on a car
   dashboard — and invert again.

If it still holds after the heat soak, you are done. If it loosens, the
material is creeping under the collet's sustained hoop load; that is what
the PAHT-CF recommendation in [PRINTING.md](PRINTING.md) is guarding
against.

## If you are between rings

Run a fine sweep around the winner:

```
python3 build.py gauge --nominal 38.4 --step 0.1 --count 7
```

## If everything is uniformly tight or loose

Do not edit the two hardware numbers — they are a record of your hardware.
Use the single trim instead:

```python
BORE_BIAS = +0.10   # everything 0.10 mm looser
BORE_BIAS = -0.10   # everything 0.10 mm tighter
```

This is also the knob for moving between materials. See `docs/PRINTING.md`.
