# Printing

Bambu Lab H2C, 0.4 mm nozzle, 0.2 mm layer unless noted.

## Orientation

Every part is modelled so that it prints **without support** in one specific
orientation. Get these wrong and you will be picking support out of a kill
flash seat.

| Part | Orientation | Why |
|---|---|---|
| `01_collar` | **Rear face down** — cord ears and clamp lugs on the plate | Ears sit at the bottom so they are not a mid-air overhang; the hex nut pocket is rotated point-up so it bridges itself |
| `02_killflash_housing` | **Front face down** — register on the plate | Makes the kill flash seat an upward-opening pocket. The only overhang is a 1.3 mm shoulder ledge, which bridges clean |
| `03_killflash_insert` | **Flat**, either way up | Symmetric |
| `04_flip_cap` | **Front face down** — decorated face on the plate | Register pocket, thumb scoop and cord holes all open upward; the grip texture is debossed rather than raised specifically so the face can lie flat |
| `05/06_gauge` | **Flat as generated** | — |

No supports on anything. If your slicer wants to add some, you have it the
wrong way up.

## The thing that will actually bite you: first-layer squish

Elephant's foot makes the first layer wider than the rest. On the parts here
that is not cosmetic — it lands directly on the bore that has to fit your
objective:

- The **collar** prints bore-vertical, so the first layer bulges *into* the
  bore at the bottom.
- The **gauge rings** do exactly the same thing.

That is fine, and it is why the gauges work: as long as the gauges and the
real parts are printed with **the same elephant's-foot compensation, the
same plate, and the same first-layer settings**, the error cancels. A gauge
printed differently from the part is measuring the wrong thing.

Set elephant's-foot compensation (Bambu Studio: *Quality → Elephant foot
compensation*) once, to whatever you normally use, and then do not touch it.

## Settings

### Everything except the kill flash

| Setting | Value | Note |
|---|---|---|
| Layer height | 0.20 mm | 0.16 for a nicer cap face |
| Wall loops | **4** | 3 minimum; these are load-bearing walls, not shells |
| Top / bottom layers | 5 / 5 | |
| Infill | **25 % gyroid** | Gyroid, not grid — it is isotropic, which matters for the cord bosses |
| Seam position | **Aligned**, and move it off the collet slots and cord bosses | A seam up a boss is where it will tear |
| Brim | Off, except the cap | |

### Kill flash insert — the one part with special settings

The cell walls are a **single 0.45 mm extrusion**. Slicers drop thin walls by
default and you will get a disc full of holes.

| Setting | Value |
|---|---|
| Detect thin walls | **ON** |
| Wall loops | 1 |
| Top / bottom layers | 0 |
| Infill | 0 % |
| Slow down for overhangs | Off |

Slice it and **look at the preview** before you print. Every cell wall should
show as a continuous extrusion. If cells are missing, raise `KF_WALL` in
`params.py` to 0.50 and re-slice.

### Flip cap

Print a **brim**. It is a 52 mm flat plate with a thin edge chamfer and it
will lift at a corner otherwise. The debossed grip texture and centre mark
are on the plate side, so plate finish is what you see — a smooth PEI sheet
gives a satin face, a textured sheet gives a matte one. For night vision,
**textured**: no glint.

## Print order

1. **`05_gauge_shroud` and `06_gauge_collar` first.** ~20 min each. Do not
   skip this. → [MEASUREMENTS.md](MEASUREMENTS.md)
2. Set the two numbers, rebuild, then print **one** housing and check it on
   the objective before committing to a full set.
3. Then the rest, two of each.

Rough times at 0.2 mm on an H2C: collar ~35 min, housing ~40 min, kill flash
~25 min, cap ~45 min. A full binocular set is about 5 hours of machine time
and roughly 80 g of filament.

## Moving between materials

Prototype and production materials do **not** shrink the same amount, so a
bore that fit in PETG will not fit in a carbon-filled resin. That is what
`BORE_BIAS` in `params.py` is for — one number that trims every
hardware-facing bore at once:

```python
BORE_BIAS = +0.15   # production part comes out tighter than the prototype
```

The honest way to find that number is to reprint the **gauge** in the
production material and compare which ring wins. It costs one 20-minute
print and removes all the guesswork.

## Material selection

See the next section — being finalised.
