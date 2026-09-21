# NVG objective cap set

A four-piece 3D-printed objective cap system for NOCTIS mil-spec glass in
Nocturn Industries Raptor housings (AN/PVS-14-pattern objective interface),
retained with 1/8 in shock cord.

![parts](preview/_sheet.png)

> ## Read this first
>
> **Front bezel: confirmed at 36.75 in PLA.** The fine ladder picked
> modelled bore 36.90, mid-ladder. That is 1.3 mm under the AN/PVS-14
> nominal this project started from — the nominal was wrong, which is
> exactly why the gauge exists. Valid in PLA only; re-gauge in the
> production filament.
>
> **Collar barrel: still unverified**, and suspect for the same reason.
> Do not print a collar until that number is read off a gauge.
>
> → **[docs/CALIBRATION.md](docs/CALIBRATION.md)** ·
> **[docs/MEASUREMENTS.md](docs/MEASUREMENTS.md)**

## The parts

| File | Part | What it does |
|---|---|---|
| `stl/01f_collar_lap.stl` | **Collar, lapped — print this one** | The recorder mount's actual mechanism: the band wraps 410° so its two ends lap past each other, each carrying a finger tab. **Squeeze** the tabs together and the lap shortens, which makes the circle bigger. 2.9 N — the lightest squeeze of any collar here. No hardware, no tools — [how it works](docs/ASSEMBLY.md#01f-is-the-one-to-print). **Goes on BEFORE the housing.** |
| `stl/01e_collar_pinch.stl` | Collar, pinch | Reads closed at 340°, tabs flanking a gap — you **spread** these, not squeeze them. Lowest install strain in the set and no sliding clearance for a slicer to get wrong, so it is the fallback if `01f`'s lap fuses. **Goes on BEFORE the housing.** |
| `stl/01_collar.stl` | Collar, screw clamp | Split band clamp, M3 pinch screw. The only one that can be fitted *after* the housing, and the only one with a preload you can re-tighten. |
| `stl/01b_collar_proto.stl` | Collar, wide gap | Prototype only. Opens far enough to clamp anywhere across the plausible range, for use before the collar seat has been gauged. Needs an M3 × 30 screw. |
| `stl/01c_collar_snap.stl` | Collar, push-on | Split C-ring, 230° wrap. Pushed straight on; the barrel cams it open. Superseded by `01e` — kept because it is the only spring ring that does not need an axial approach. |
| `stl/01d_collar_lever.stl` | Collar, lever | Circlip-style, 290° wrap with finger paddles. Superseded by `01e`, which does the same job at 340° for less strain and less force. |
| `stl/02_killflash_housing.stl` | Kill flash housing | Presses onto the objective bezel, carries the kill flash, gives the cap a register to close on. |
| `stl/03_killflash_insert.stl` | Kill flash | Printed honeycomb. 71 % open area, 39° off-axis cutoff. |
| `stl/04_flip_cap.stl` | Flip cap | Bungee-retained cover. Cord bosses at 3 and 9, thumb tab at 6, hex grip, centre mark. |
| `stl/05_gauge_shroud.stl` | Fit gauge | Ring ladder for the housing bore. **Print this first.** |
| `stl/06_gauge_collar.stl` | Fit gauge | Ring ladder for the collar bore. **Print this first.** |
| `stl/sweep/lap_*.stl` | Fit sweep | Five `01f` collars stepping 0.30 mm, bore size moulded into each ear. Settles the collar seat *and* the grip on one plate — the last unverified dimension in the set. |

Every part is symmetric about the vertical plane — there is no left and
right. Print two of each for a binocular.

### Prototyping in PLA

Everything is calibrated for PLA right now (`CAL_MATERIAL == PRINT_MATERIAL`,
so the bore bias is exactly zero — the measured case). Print the whole set
in PLA, use `01b_collar_proto` in place of the collar, and you can shake
down cord routing, flip clearance, IPD spacing and glove ergonomics before
the collar barrel has been gauged and before committing any engineering
filament.

**Do not field a PLA set.** It creeps under the collet's sustained hoop load
and softens around 55–60 °C; an afternoon on a dashboard will destroy it.

## Quick start

```bash
python3 build.py        # writes one STL per part into stl/
python3 tests.py        # 277 geometry and interface checks
python3 render.py       # PNG previews into preview/
```

Fine-tune a fit without touching anything else:

```bash
python3 build.py gauge --nominal 38.4 --step 0.1 --count 7
```

Requires `manifold3d`, `trimesh`, `numpy`.

## How it goes together

```
   objective bezel │ kill flash │ housing flange │ register │ cap
   ────────────────┼────────────┼────────────────┼──────────┼──────
       8.0 mm      │   5.0 mm   │     1.6 mm     │  2.2 mm  │ 5.6 mm
                                                                     → +Z
   collar clamps the barrel behind all of this, cord runs forward at r=26
```

The kill flash loads from the **rear** of the housing and seats against an
integral flange, then the objective traps it. No snap ring, no glue, and it
still comes apart for cleaning. → **[docs/ASSEMBLY.md](docs/ASSEMBLY.md)**

## Design notes

**Both cord holes sit on one radius (26.00 mm).** That makes the line
between the two cap bosses the hinge axis, with both holes lying *on* it —
so flipping the cap does not change the cord length. The bungee only
stretches the 2.2 mm needed to clear the register, about 11 % strain.

**Nothing needs an anti-rotation key.** The cap's orientation comes from the
two cords, not from the register, so the housing is free to sit at any
rotation. The collar is screw-clamped because it *is* the rotational datum.

**Every part prints without support.** The housing goes front-face-down so
the kill flash seat becomes an upward-opening pocket; the cap goes
front-face-down so the decorated face gets the plate finish and the grip
texture is debossed rather than raised; the collar's nut trap is rotated
point-up so it bridges itself.

**The housing grip is a four-finger collet, and the fingers are thinner
than the wall.** A solid ring pressed onto an objective barrel has a narrow
acceptance window and puts real hoop stress into an expensive optic. But
slots alone are not enough — radial compliance scales as `t³/L³`, and at the
full 3.4 mm wall the fingers were a stubby plate (L/t = 1.88), not a spring.
There is not enough bezel to lengthen the slots, so the OD is relieved over
the collet instead: 1.90 mm fingers at L/t = 3.16 are **4.7× more
compliant**, at no cost in axial length. Each slot ends in a round keyhole
rather than a flat face, because the root is where it would crack.

**The slots' bore edges are broken.** Four slots leave eight sharp axial
edges in the bore that would otherwise scrape the full grip length of the
bezel on every install. On a coated optic that is the one piece of real
damage this design could do.

**The cap seats on the housing shoulder, not the register.** The pocket is
0.4 mm deeper than the register is tall, so the register locates and the
shoulder takes the load. A cap that lands on the register rocks.

## Layout

```
params.py           every dimension, single source of truth
build.py            emits one STL per part, validates before writing
tests.py            geometry probes + cross-part interface assertions
render.py           headless preview renderer (no GL)
lib/                solids, patterns, seven-segment text
parts/              one module per part
docs/               CALIBRATION, MEASUREMENTS, ASSEMBLY, PRINTING
stl/                output
```

`params.py` is the only file you should need to edit. Two hardware
diameters, plus `CAL_MATERIAL` / `PRINT_MATERIAL` — the bore bias is derived
from those, so changing filament is one line and cannot be got wrong by
forgetting. `BORE_TRIM` is there for a uniform fit correction on top.

## Material

| Part | Material |
|---|---|
| Collar, kill flash housing | **PAHT-CF** — expansion matched to the aluminium bezel, ductile across layers at the collet roots, immune to DEET and CLP |
| Kill flash, flip cap | **ASA Basic** — the 0.45 mm honeycomb wall needs a 0.4 mm nozzle, and CF grades need 0.6 mm hardened; the cap is the only impact-loaded part |
| Prototypes and coarse gauges | **PLA Basic** — not PETG, which is half the stiffness and yields where the production part cracks |
| Fine gauge | **the production filament itself** |

No single material wins all four parts. The reasoning, the tradeoffs being
accepted, and full slicer settings are in
**[docs/PRINTING.md](docs/PRINTING.md)**.

Carbon fibre against a coated objective barrel was **not** cleared — line
the collar bore with 0.13 mm PTFE tape and set `LINER_T = 0.13`.
