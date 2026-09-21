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

```
python3 build.py
```

Print `05_gauge_shroud.stl` and `06_gauge_collar.stl`. Roughly 20 minutes
each in PLA, and PLA is the right material here — the gauges are throwaway
and PLA is the most dimensionally honest thing on the shelf.

**Print them in the same material, on the same plate type, at the same
layer height you will use for the real parts if you can.** A gauge that was
printed differently from the part is measuring the wrong thing.

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
OBJ_FRONT_OD  = <shroud gauge winner>  - FIT_PRESS   # subtract 0.15
OBJ_COLLAR_OD = <collar gauge winner>  - FIT_SLIP    # subtract 0.40
```

The gauge rings are labelled with their **bore**, and the bores already
include the design clearance, so you subtract it back out to recover the
hardware diameter. Then rebuild:

```
python3 build.py && python3 tests.py
```

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
