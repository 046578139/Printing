# Printing

Bambu Lab H2C. **The nozzle is a design input, not a slicer setting.**

`params.py` currently declares `NOZZLE = 0.60`, `LAYER = 0.30` — the draft
setup — and every thin feature in the project is derived from it: cell
walls, texture grooves, rim widths, deboss depths. Change the nozzle at the
machine and you must change it in `params.py` and rebuild, or features that
were sized for the old one quietly fall below what the new one can extrude.

`tests.py` runs a minimum-feature audit against `NOZZLE` on every build. It
is the most useful test in the file: the first kill flash shipped with
0.45 mm cell walls on a 0.60 nozzle — 75 % of nozzle diameter, below what
can be extruded at all — and the slicer discarded every cell. The part came
off the plate as a bare rim with stubs.

### 0.6 / 0.3 draft vs 0.4 / 0.2

Keep the 0.6 for fit work. Fits are diameter-driven, not resolution-driven,
and as long as the gauge and the part are printed the same way the error
cancels — that is the whole basis of the calibration. Draft speed is worth
more than surface finish while the dimensions are still moving.

Drop to 0.4 / 0.2 for:

- **The cap**, if you want the grip texture to read as hexagons rather than
  bumps and the centre mark to come out crisp. At 0.6 those features are
  near the floor of what can be resolved, which is exactly how they printed.
- **Anything final**, and anything in carbon fill — which needs a hardened
  nozzle regardless.

If you do switch:

```
python3 build.py --nozzle 0.4 --layer 0.2        # whole set
python3 build.py cap --nozzle 0.4 --layer 0.2 --tag fine   # just one part
```

Cell wall, texture groove, rim and deboss depths all follow automatically.

### When to switch — batch it, don't pay twice

**A nozzle change invalidates the fit calibration.** A different nozzle
delivers a different bore, so the gauge reading you earned at 0.6/0.3 does
not carry across and every press fit has to be re-gauged.

Right now the housing fits, and that is a calibrated state worth keeping.
You will have to re-gauge anyway when you move to PAHT-CF or ASA, because
every production filament needs its own calibration and carbon fill needs a
hardened nozzle regardless. **Do both at once** and you pay the calibration
cost once instead of twice.

The exception is the **cap**, which can switch on its own. Its only fit is
0.35 mm of clearance over the register — loose enough that a nozzle change
cannot break it. So if you want the grip texture to read as hexagons rather
than bumps, print `04_flip_cap_fine` at 0.4/0.2 and leave everything else
where it is.

## Orientation

Every part is modelled so that it prints **without support** in one specific
orientation. Get these wrong and you will be picking support out of a kill
flash seat.

| Part | Orientation | Why |
|---|---|---|
| `01f_collar_lap` | **Rear face down** — already oriented, flat on the plate | Same reason as `01e`, plus: the lap's two sliding clearances (0.40 mm radial, 0.30 mm vertical) are only clearances in *this* orientation. Turn OFF thin-wall detection and gap filling — a slicer that helpfully bridges those two gaps welds the arms together and the ring will not expand at all |
| `01e_collar_pinch` | **Rear face down** — already oriented, flat on the plate | Cord ears at the bottom so they are not a mid-air overhang. Printed this way the band flexes *within* its layers when you spread the tabs, so installing it loads X-Y strength and never tests layer adhesion — which is the whole reason a printed spring ring works at all |
| `01_collar` | **Rear face down** — cord ears and clamp lugs on the plate | Ears sit at the bottom so they are not a mid-air overhang; the hex nut pocket is rotated point-up so it bridges itself |
| `02_killflash_housing` | **Front face down** — register on the plate | Makes the kill flash seat an upward-opening pocket. The only overhang is a 1.3 mm shoulder ledge, which bridges clean |
| `03_killflash_insert` | **Flat**, either way up | Symmetric |
| `04_flip_cap`, `04b`, `04c` and every `_inlay` | **Front face down** — decorated face on the plate | Register pocket, thumb scoop and cord holes all open upward; the grip texture is debossed rather than raised specifically so the face can lie flat |
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

### Two-tone face — use the 3MF

**An STL cannot carry colour.** It is a bag of triangles with no notion of a
part or a filament, so no amount of combining produces a two-tone cap. That
is what 3MF is for: objects, the parts inside them, and which extruder each
part prints with.

| File | Contents |
|---|---|
| `20_cap_FUCK_2color.3mf` | FUCK cap, body + lettering + hex |
| `21_cap_YOU_2color.3mf` | YOU cap, same |
| `22_caps_FUCK_YOU_2color.3mf` | Both caps on one plate |
| `23_cap_2color.3mf` | The standard P cap |

Each is **two filaments**: body on slot 1, lettering and hex field both on
slot 2. Three parts, two colours. Open it, check the filament slots on the
right match what is loaded, slice. Nothing to position or assign.

`python3 tools/make_3mf.py` regenerates them. Swap `GREY`/`TEAL` at the top
of that file to move a part to a different slot.

#### If the 3MF does not come in right

Load `04b_flip_cap_FUCK.stl`, then right-click it → **Add Part → Load** and
pick `04b_inlay_FUCK.stl`, then again for `04b_inlay_hex_FUCK.stl`. Click
each inlay in the object tree and set its filament. Same result, three
clicks.

### The inlay files

The decorated face can be printed in two or three filaments. Every recess on
it has a matching **inlay** file that fills it exactly flush:

| Cap | Lettering inlay | Hex field inlay |
|---|---|---|
| `04_flip_cap` | `04_inlay_mark` | `04_inlay_hex` |
| `04b_flip_cap_FUCK` | `04b_inlay_FUCK` | `04b_inlay_hex_FUCK` |
| `04c_flip_cap_YOU` | `04c_inlay_YOU` | `04c_inlay_hex_YOU` |

In the slicer: load the cap, then **right-click → Add Part → Load** each
inlay you want, and assign it a filament. They come in already aligned to the
cap, so **do not move or rotate them** — that is the whole reason they are
separate files rather than something to position by eye.

Mix freely: lettering only, field only, or both in different colours. Take
the inlays from the same cap as the body, though. The hex field is cut around
the lettering, so `04b_inlay_hex_FUCK` on a YOU cap puts plugs where the
letters are.

**This is the easier print, not the harder one.** Debossed and printed face
down, every letter floor and every dimple floor is a ceiling bridged over
air. Filled with a second filament there is no void left to bridge — the
whole face builds off the plate as one solid first layer.

What it costs is purge. The recesses are 0.60 mm deep, so the swaps are
confined to the first five layers at 0.12 — but within those five layers the
lettering is one compact region while the hex field is 30–40 plugs scattered
over the whole face. Both want a tool change per layer regardless; the field
just makes those layers longer. Five layers of swaps is a few grams of purge,
not a few tens.

## One-file plates

Three files carry a whole plate, parts already laid out and oriented:

| File | What's on it | Footprint |
|---|---|---|
| `10_plate_set` | One pod: cinch collar, housing, kill flash, cap | 180 x 97 mm |
| `11_plate_pair` | A full binocular set, two of each | 204 x 151 mm |
| `12_plate_caps_FUCK_YOU` | Both custom caps | 128 x 56 mm |

Drop one on the bed and slice. Everything is spaced 8 mm apart, which is a
brim's width, and nothing needs rotating.

Two things a plate **cannot** do:

**Colour.** An STL carries geometry and nothing else. The cap inlays are
separate files precisely so the slicer can hand each one its own filament;
merged onto a plate they would just be more plastic. Two-tone stays on the
individual files above.

**Per-part settings, unless you load it as multiple parts.** The kill flash
wants 1 wall loop, 0 top/bottom and thin-wall detection ON, and the rest of
the set very much does not. When the slicer asks *"multi-part object
detected — load as a single object with multiple parts?"* answer **yes**:
you can then right-click the insert in the object tree and set them on that
part alone. Answer no and the whole plate gets one set of settings, and the
insert comes out a disc full of holes.

If you would rather not deal with that, print `10_plate_set` without the
insert selected and run `03_killflash_insert` on its own — it is 25 minutes.

Each plate has a matching `.svg` next to it in `stl/`, a top view of the
layout on the bed. `python3 tools/plate_preview.py` regenerates them.

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

Short version: **you already own the right material for the two parts that
grip the optic. Buy one spool of ASA Basic (~$30) for the other two.**

| Part | Material | Have it? |
|---|---|---|
| 01 collar | **PAHT-CF** | yes |
| 02 kill flash housing | **PAHT-CF** | yes |
| 03 kill flash insert | **ASA Basic** | order |
| 04 flip cap | **ASA Basic** | order |
| gauges (coarse) | **PLA Basic** | — |
| gauges (fine) | **the production filament** | — |

No single material wins all four parts. Every attempt to claim one — ASA for
the set, PET-CF for the set, PAHT-CF for the set — failed an adversarial
review. Split it.

### Why PAHT-CF for the collar and housing

**Thermal expansion match to the aluminium bezel.** This is the term that
decides it, and it is the one nobody thinks about. Aluminium is ~23 ppm/K.
Fibre-filled grades run 25–35 ppm/K in the hoop direction; every *unfilled*
polymer — ASA, ABS, PC, PETG, PLA — runs 60–95. Over a −20 °C to +60 °C
service span an unfilled shroud gains or loses **0.06–0.10 mm** of
interference. The whole design fit is 0.15 mm. A fibre-filled one moves
~0.01 mm. For plastic clamped on metal, fibre fill is not a strength choice,
it is a dimensional requirement — and it disqualifies unfilled materials for
these two parts outright.

**Ductility across layers at the collet roots.** The housing prints
front-face-down, so the collet fingers bend *across* layer lines and Z
properties govern, not the headline X-Y numbers. PAHT-CF: ~5.2 % Z
elongation. PET-CF: ~2.4 %. On a notched feature that cycles every time you
pull the shroud to clean the kill flash, that is the difference between a
part that flexes and one that snaps.

**Chemistry and heat.** Semi-crystalline polyamide is the only class here
with real resistance to DEET, CLP and sunscreen esters — and the housing is
the one part under *permanent* strain, which is the textbook precondition
for environmental stress cracking. HDT ~170 °C makes a closed summer vehicle
a non-event. PET-CF's Tg is ~75 °C, so as-printed it sits essentially *at*
its glass transition under sustained collet load, and you cannot anneal it
without destroying the bore.

**The tradeoff being accepted:** PAHT-CF absorbs moisture (~0.88 %), which
grows the bore roughly 0.03–0.06 mm from dry to equilibrium over 2–3 weeks.
That is real. It is also a *calibration* cost rather than a defect, and it
cancels completely if you gauge in conditioned PAHT-CF — see
[MEASUREMENTS.md](MEASUREMENTS.md). Trading a reversible, measurable offset
for PET-CF's irreversible creep near Tg is the right call for field gear.

**Do not use the PPA-CF for the housing when it arrives.** It is a fine
material, but it is another semi-crystalline polyamide with the same
moisture discipline and no advantage here, and every production filament
needs its own gauge calibration. Save yourself a second calibration.

### Why ASA for the kill flash and cap

**Kill flash — this one is not close.** `KF_WALL` is a 0.45 mm *single
extrusion*, which needs a 0.4 mm nozzle. Bambu's guidance for every CF grade
is a 0.6 mm hardened nozzle to avoid fibre clogs. At 0.45 mm the chopped
fibre bundles are the same order as the wall itself — the filler stops being
reinforcement and becomes a defect population spread over ~81 cells and
~14 m of single-wall path per part. Unfilled is the materially correct
answer. UV matters most here too: photo-oxidation is skin-depth limited and
a 0.45 mm wall cannot afford to lose 100 µm. ASA's acrylate rubber has no
butadiene to photo-oxidise. Treat the insert as a consumable and reprint it
every year or two.

**Cap — the only genuinely impact-loaded part.** ASA publishes ~19.6 kJ/m²
notched Charpy: roughly 2.3× PET-CF's X-Y figure and 4× its Z figure. Bambu
publishes *no* notched figure for PAHT-CF at all, and a daily-pried thumb
tab is not something to spec on a missing number. ASA is also unfilled, so
it cannot abrade the register or shed fibre near the glass, and its lower
modulus closes quieter — which matters at night. `CAP_SKIRT_BORE` has
0.35 mm of clearance, so ASA's higher expansion is irrelevant here.

**If you would rather not order anything:** PETG is an acceptable fallback
for both of these. It gives up UV life on the insert and impact on the cap,
but it will work, it needs no hardened nozzle, and you likely have it.

### Carbon fibre against your objective — read this

This was **not** cleared. The comfortable argument ("CF is softer than
anodising") was refuted three ways: it contradicts Bambu's own mandatory
hardened-nozzle requirement, it ignores that in mud and sand the *polymer*
is the grit-embedding member, and it says nothing about the carbon/aluminium
galvanic couple in salt and rain.

Two mitigations, both cheap:

1. **Line the collar bore** with 0.13 mm self-adhesive PTFE or UHMW tape.
   Non-conductive (kills the galvanic loop), slippery, inert, sacrificial.
   Set `LINER_T = 0.13` in `params.py` and the bore opens to suit. The collar
   is the higher-risk part — it clamps 11 mm of barrel under sustained screw
   load.
2. **The housing's bore edges are already broken in CAD.** The four collet
   slots used to leave eight square axial edges that would scrape the full
   grip length of the bezel on every install; `SLOT_EDGE_BREAK` now relieves
   them. Nothing for you to do, but do not set it to zero.

Never bead-blast a bore. Leave it as printed.

**No TPU liner.** Abrasive embeds in the softer member and laps the harder
one, so a TPU sleeve in mud becomes a grit-charged lap against your bezel.
It also has 150–200 ppm/K expansion and heavy compression set. PTFE is soft
*and* slippery; TPU is only soft.

### Why PLA and not PETG for prototypes

PETG is the intuitive choice and it is the wrong one, for two specific
reasons:

- **Stiffness.** Your acceptance test is a hand-felt seating force, and
  collet force scales with modulus. PETG (~2050 MPa) under-reports seating
  force against PAHT-CF (~4120 MPa) by about half. PLA Basic (~2750 MPa) is
  off by a third. PLA-CF (~3950 MPa) is within 4 %.
- **Failure mode.** PETG is ductile — at over-interference it *yields* and
  then reports "fits fine". PAHT-CF and PET-CF crack. A proxy that cannot
  reproduce the production failure mode cannot validate margin against it.
  PLA is brittle and fails the way the real part will.

PLA is also the lowest-shrink, no-drying, no-hardened-nozzle material on the
shelf, which is exactly what a measurement artifact should be.

If you want one high-fidelity check before committing nylon, print a single
housing in **PLA-CF**: within 4 % of PAHT-CF's modulus, fails brittle, and
genuinely matte so the same print also reads out glint and whether the
0.45 mm honeycomb resolves.

### What would change this

Stated plainly, because some of it is inference rather than published data:

- **PET-CF takes the housing back** if you condition a PAHT-CF ring and a
  PET-CF ring side by side for a month and the PAHT-CF bore has moved more
  than ~0.06 mm. The case rests on the swell being fibre-restrained in the
  hoop direction; Bambu publishes no dimensional-change coefficient, so that
  is inferred.
- **PET-CF also wins** if you decide you will essentially never remove the
  housing. The argument leans on the fingers cycling.
- **PAHT-CF takes the cap** if Bambu ever publishes a notched Charpy for it
  above ~15 kJ/m². Cheap test that settles it yourself: freeze one of each
  overnight at −20 °C and break the thumb tabs by hand. Nobody publishes
  low-temperature impact figures for these, so that is the only data that
  will ever exist.

## Settings by material

### PAHT-CF — collar and housing

| Setting | Value |
|---|---|
| Nozzle | **0.4 mm hardened steel, mandatory.** Not a high-flow hotend — a CF clog there is effectively unclearable |
| Nozzle / bed | 280 °C / 100 °C, textured PEI |
| Chamber | **60–65 °C, actively heated.** This is what drives interlayer strength, which is exactly what the collet roots need |
| Drying | **80 °C for 8–12 h before, and keep it dry during.** Wet nylon means poor layer adhesion at the slot roots — the one place you cannot afford it |
| Wall loops | **5** — the grip section is load-bearing and Z-loaded |
| Part cooling | 20–30 % max |
| Speed | ≤100 mm/s outer walls; slow through the collet |
| Seam | Aligned, **forced off the collet slots and the pinch lug** — a seam at a slot root is where it cracks |
| Brim | **Yes on the housing.** Its first layer is a ~550 mm² annulus carrying a tall part, and it is the surface that sets `REG_OD` |

### ASA Basic — kill flash and cap

| Setting | Value |
|---|---|
| Nozzle | 0.4 mm standard — **no hardened nozzle needed**, the only fieldable material here that can say that |
| Nozzle / bed | 255 °C / 100 °C, textured PEI |
| Chamber | 50–60 °C |
| Drying | 80 °C for 6–8 h. Not needed during the print |
| Part cooling | **0–15 % on the cap** — styrenics delaminate and warp with fan |
| Brim | **Yes on the cap** |

**The honeycomb has one genuine conflict:** ASA wants almost no fan, but the
insert's layers are short (~560 mm of single-wall path) and need to set
before the next one lands. Do not solve it with the fan. **Put 4–6 inserts
on the plate at once** — that multiplies layer time by 4–6× and lets you
keep the fan at 20–30 % in a hot chamber. Also drop the speed to 30–40 mm/s;
this part has no reason to be fast.

### PLA Basic — prototypes and coarse gauges

| Setting | Value |
|---|---|
| Nozzle / bed | 220 °C / 55 °C |
| Chamber | **Off, door open** — a hot chamber heat-creeps PLA in the extruder |
| Drying | none |
| Layer / walls / infill | **match your production settings exactly**, or the gauge means nothing |
| Part cooling | 100 % |

Honeycomb prints beautifully in PLA Basic — it is the best thin-wall
material of the lot, which is why it is the right proxy for checking whether
the cells resolve.
