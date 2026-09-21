# Assembly

Per eye: 1 collar, 1 kill flash housing, 1 kill flash insert, 1 flip cap,
and about 240 mm of 1/8 in (3.175 mm) shock cord. Double it for a binocular.

The recommended collar is **`01f_collar_lap`**, which needs no hardware
and no tools. If you print a screw collar instead, add 1 M3 socket head cap
screw and 1 M3 hex nut per eye: **16 mm** for `01_collar`, **30 mm** for
`01b_collar_proto` — the prototype's pinch gap is 13 mm wide, so the screw
has to span a lot more air before it closes.

Every part is symmetric about the vertical plane, so there is **no left and
right** — print two of each and they fit either pod.

## Order of operations

> **With a spring collar (`01c` / `01d` / `01e` / `01f`) the collar goes
> on FIRST.**
> None of them will pass over the Ø43.7 housing, so the order below is
> 0 → 1 → 2 → 4. Only the screw collars can be fitted after the housing,
> because they open all the way. Get this wrong and you are pulling a very
> tight press fit back off a coated objective.

**0. Spring collar onto the bare bezel.** *(`01c`–`01f` only —
skip to step 1 for a screw collar and come back at step 3.)*

Cord ears at 3 and 9 o'clock, ears facing **rearward**, lap or gap at 12.

- On **`01f`**, pinch the two tabs **together** — they sit at different
  heights and lap past each other, so they will not butt. About 4 N. The
  lap shortens from 30° to 18° and the bore grows 1.30 mm.
- On **`01e`**, get a fingertip between the two tabs and **spread** them
  apart instead. About 5 N; the gap opens from 6.8 to 10.9 mm.

Slide the ring down the bezel to its seat and release.

Before you let go, confirm the band is not sitting on anything that turns
when you focus. On a PVS-14-pattern objective the focus ring turns, and a
collar clamped to it will bind the focus.

It should not rotate under a firm hand twist. If it does, the bore is too
big — print the `lap-bore` (or `pinch-bore`) sweep and step down.

**1. Housing onto the objective.**
Push the housing straight on, front face forward. Go square — the rear bore
lead-in will help, but a cocked start will gall the bezel. It bottoms
positively against the internal flange; that is the depth stop and it is
hardware-confirmed. Do **not** force a fit that clearly does not want to go;
go back to the gauge.

**2. Kill flash into the FRONT recess.**
The insert presses into the Ø33.00 counterbore on the **front** of the
housing, chamfered edge leading, and seats on the flange 0.20 mm under
flush. Light thumb pressure.

It does not go in from the rear — the objective fills the whole bore and
bottoms on the back of that same flange, so there is no rear pocket. If the
press is wrong, print `07_gauge_killflash`: five plugs stepping 0.15 mm, and
you want the largest one that seats with thumb pressure and does not fall
out when inverted. Put that number in `KF_OD`.

A note on why this needed a gauge at all: an FDM hole comes out undersize
and an FDM boss comes out oversize, and here those two errors stack against
each other on the same 0.30 mm clearance. That is a fit worth measuring
rather than calculating.

**3. Screw collar onto the barrel.** *(Skip if you fitted a spring collar
at step 0.)*
Slide it on behind the housing with the two cord ears at 3 and 9 o'clock,
ears facing **rearward**, and the pinch lugs at 6 o'clock. Confirm one more
time that the band is not sitting on anything that turns when you focus.

Fit the M3 screw from the right-hand lug (counterbored for the head) into
the hex nut trap on the left. The nut pocket is oriented point-up so it
prints without support; press the nut in with a flat blade before starting
the screw.

Snug it until the collar will not rotate under a firm hand twist. It does
not need to be tight — you are clamping an optical assembly, not a
suspension arm. If the gap closes completely before it grips, the bore is
too big; if it grips with the gap barely closed, that is correct.

On the **prototype** collar the gap will close a long way before it grips,
and that is expected — that is the whole point of it. Note roughly how far,
though: a gap that ends up near 0 means the real barrel is close to
38 mm, and one that stays wide means it is close to 42. That is a free
coarse reading while you wait to print the proper gauge.

**4. Cord.**
Cut four pieces about 120 mm each. Per side, per eye:

```
  knot ── collar ear ──────── forward ──────── cap boss ── knot
 (behind)                                              (in front)
```

- Thread from the rear: through the collar ear, forward, through the cap
  boss from the back.
- Tie a figure-eight in the tail behind the collar ear first.
- Hold the cap closed on the housing, pull the front tail until the cord is
  **just taut**, then pull about 3 mm more and tie the front knot there.
  That pre-tension is what holds the cap shut.
- Trim to ~8 mm and melt the ends.

Repeat on the other side. Both cords should end up the same length or the
cap will sit crooked.

## Which collar

Five collars are provided. They are drop-in swaps — same cord ears, same
radius, same install direction — so you can fit one of each and decide on
your own hardware.

| | `01` / `01b` screw clamp | `01c` / `01d` / `01e` / `01f` spring rings |
|---|---|---|
| Hardware | M3 screw + hex nut per eye | none |
| Tools | hex key | none |
| Preload | **adjustable, re-tightenable** | fixed by geometry |
| Grip across a diameter range | narrow (0.83 mm stock, 4.14 mm on `01b`) | wide and self-adjusting |
| Rotational security | high, positive | friction only |
| Parts to lose | 2 | 0 |
| Ages by | loosening you can fix | creeping you cannot |

### `01f` is the one to print

`01f_collar_lap` is the recorder mount's actual mechanism, and getting to it
took working out why every earlier ring moved the wrong way.

On `01c`/`01d`/`01e` the tabs sit on the band either side of a **gap**.
Expanding one of those rings opens the gap, so the tabs move *apart* — which
is why all three have to be **spread**. Lap the two ends **past each other**
instead and each tab rides a free **end**. The ends have crossed, so the
angle between the tips *is* the lap; expanding the ring shortens the lap, and
the tips — with the tabs on them — come **together**. Squeeze to expand.
That is a spring hose clip, and it is what the recorder does.

| Collar | Wrap | Fitting | Tab motion | Install strain | Force | Seated |
|---|---|---|---|---|---|---|
| `01c` push-on | 230° | push on radially | spread | 0.65 % | 12.1 N | 0.21 % |
| `01d` lever | 290° | expand, slide on | spread | 0.45 % | 6.5 N | 0.21 % |
| `01e` pinch | 340° | expand, slide on | spread | 0.37 % | 4.9 N | 0.22 % |
| **`01f` lapped** | **410°** | **expand, slide on** | **squeeze** | **0.66 %** | **2.9 N** | **0.22 %** |

*(Ø36.90 barrel, PLA at 2750 MPa, 0.89–0.90 mm interference on all four, so
the seated column is the same by construction and only the cost of getting
there differs.)*

`01f` is much the lightest squeeze of the four and the only one that reads as
a genuinely closed circle. It is not the lowest strain — `01e` is — because
`01f` carries its load through two thin lapped arms rather than one thick
band. 0.66 % still leaves 2.3× margin in PLA and considerably more in
PAHT-CF, and it buys the right *motion*.

#### How the lap is built, and the one thing it forces

Over 50° the band splits in thickness: a 1.20 mm inner arm, a 0.40 mm
sliding gap, a 1.60 mm outer arm. The split is deliberately uneven. The
inner arm gets a full-wall flange back above the gap, so an even split would
leave the outer arm carrying the whole squeeze on a third of the section at
roughly a fifth more strain than it needs to. Moving 0.20 mm of
wall outward and the divide up to 6.5 mm brings the worst case to 0.66 % and
costs nothing.

The step forces one thing: **the inner arm's tab cannot get out radially**,
because the outer arm is in the way and there is no path through it. So the
outer arm stops at 6.5 mm and the inner arm's tab rides over the top of it
on a full-width flange.

Which leaves that tab starting half way up the band with nothing underneath
it outboard of the OD — a fin hanging 6.8 mm in the air, and a slicer is
right to refuse it. Outboard of the band nothing is in the way, so it
carries straight down to the plate, clear of the outer arm by the same
0.40 mm the arms use. Everything on the part now either stands on the plate
or bridges that 0.30 mm gap above the outer arm — a print-in-place
clearance, not an overhang. **No supports anywhere.**

That in turn is why the lap is 50° and not 30°. Tabs at different heights
could lap past each other; two tabs that both reach the bed cannot, so they
have to stay apart. And a tab may not sit *on* its arm's free end — it hangs
half its width past it and welds that arm to the body — so each is inset 7°,
costing another 14°. What is left keeps the heads 9.4 mm apart at rest and
3.7 mm at full squeeze. Insetting does not change the mechanism: the arms
are rigid, so a tab turns with its arm by the same angle wherever it sits.

> **Check the lap is free before you fit it.** Squeeze the tabs on the bench
> first. If the ring does not visibly grow, the 0.40 mm radial gap or the
> 0.30 mm vertical one has been bridged shut by the slicer and the two arms
> have fused — at which point it is a solid ring and forcing it will break
> it. Turn off any "detect thin walls" or gap-filling option and reslice.

### `01e` — the spread-apart version

`01e_collar_pinch` reads closed at 340°, with two rounded tabs flanking a
narrow gap. You **spread** these, not squeeze them. Kept because it is the
lowest-strain ring in the set and has no sliding clearance to get wrong in
the slicer — if the lap on `01f` fuses, this is the fallback.

> **Neither `01e` nor `01f` can be pushed on. Both go on FIRST, before the
> housing.** Forced on radially, `01e` would need 30.65 mm of spread and
> **2.74 % strain** — 7.5× the axial route, and past PLA's ~1.5 % limit, so
> it would simply break; `01f` laps past itself and cannot open radially at
> all. Neither will pass over the Ø43.7 housing. Fit the collar to the bare
> bezel, then the housing, then the cord. Taking the collar off later means
> pulling the housing first.

### Three mechanisms, not two

`01d` was added after seeing how the BCO recorder mount retains — a ring you
open with your fingers rather than one the hardware forces open. That turns
out not to be a styling choice; it changes what the ring is allowed to be.

A **push-on** ring has to let the barrel through the chord between its tips,
and that chord shrinks fast as the wrap grows — past about 240° the barrel
simply cannot force the gap wide enough. That is what capped `01c` at 230°.

Open it **by hand** and slide it on axially, circlip fashion, and the gap
only has to open by `π × expansion`, which barely changes with wrap. The
constraint disappears:

| Collar | Hardware | Tools | Wrap | Fitting | Gap opens | Install strain | Force | Seated |
|---|---|---|---|---|---|---|---|---|
| `01`/`01b` screw | M3 + nut | hex key | 360° | clamp down | — | — | — | — |
| `01c` push-on C-ring | none | none | 230° | push straight on radially | 5.65 mm | 0.75 % | 13 N | 0.40 % |
| `01d` lever C-ring | none | none | 290° | expand and slide on axially | 7.85 mm | 0.70 % | 9 N | 0.40 % |

So `01d` captures 60° more of the circumference than `01c` *and* takes less
strain and less force to fit. It is strictly the better ring — with one
condition attached.

**It cannot be pushed on radially.** There has to be a clear axial path onto
the barrel. From the front that means over the objective bezel, which is the
smaller diameter, so it should be fine — but it does mean the kill flash
housing comes off before the collar does. If your barrel has no axial
approach, `01c` is the one that works.

To fit `01d`: pinch the two paddles, spread them until the bore clears the
barrel, slide it into place, release. About 9 N at the paddles — firm, not
a struggle.

### Which ring wins depends on the diameter

The lever collar's advantage is **not** unconditional, and it took a
mis-sized test run to notice.

Radial spread scales with the barrel: `D − D_free·sin γ`. Axial spread does
not — it is `π × expansion`, a fixed cost no matter how small the ring gets.
So as the barrel shrinks, the radial route gets cheaper while the axial one
stays put, and somewhere they cross:

| Barrel | `01c` push-on 230° | `01d` lever 290° | Winner |
|---|---|---|---|
| 34 | 0.95 % | 1.01 % | **push-on** |
| 36 | 0.88 % | 0.90 % | **push-on** |
| 38 | 0.82 % | 0.81 % | **lever** |
| 40 | 0.77 % | 0.73 % | **lever** |
| 41 | 0.75 % | 0.70 % | **lever** |
| 43 | 0.70 % | 0.64 % | **lever** |

**Crossover is around Ø38 mm.** Above it the lever ring is strictly better,
as designed. Below it the fixed cost of expanding a small ring by
`π × expansion` outweighs the shrinking chord, and the plain push-on ring is
the better part — on top of which a small seat is likely a *waist* between
two larger diameters, which blocks the axial approach the lever ring needs
in the first place.

Both rings stay in the set for exactly this reason. Gauge the barrel, then
pick.

The barrel came in at **Ø36.90 — below the crossover**, which is why `01c`
and `01d` end up within 0.2 % of each other above and neither is a clear
win. That is the result that made `01e` worth building.

`01e` sidesteps this argument rather than winning it. The crossover exists
because a *push-on* ring gets cheaper as the barrel shrinks while an axial
one does not. At 340° the push-on route is not available at any diameter,
so there is nothing to cross over — the only question left is whether there
is an axial approach, and on this objective there is.

*(Resolved since: `SNAP_INTERF` was a fixed 2.00 mm, which was 4.9 % of a
Ø41 bore but 5.9 % of a Ø34 one. It is now `OBJ_COLLAR_OD × 2.4 %` and
scales with the barrel, as does the pinch ring's.)*

### The snap ring's numbers

Wrap is 230°, so it captures well past the equator. The barrel has to pass
the **chord between the tips**, which is what sets how far the ring flexes:

| Barrel | Interference | Tip spread | Install strain | Seated strain | Margin PLA / PAHT-CF |
|---|---|---|---|---|---|
| 39.2 | 0.20 | 3.85 | 0.51 % | 0.042 % | 2.9x / 4.9x |
| 40.0 | 1.00 | 4.65 | 0.61 % | 0.205 % | 2.4x / 4.1x |
| 41.0 | 2.00 | 5.65 | 0.75 % | 0.400 % | 2.0x / 3.3x |
| 42.0 | 3.00 | 6.65 | 0.88 % | 0.586 % | 1.7x / 2.8x |
| 42.2 | 3.20 | 6.85 | 0.90 % | 0.622 % | 1.7x / 2.8x |

*Install* is transient, while the ring passes over the barrel. *Seated* is
sustained — it is what grips, and it is what creeps.

Two things fall out of that table:

- **Installation is safe everywhere**, with 1.7–2.9× margin in PLA and
  2.8–4.9× in PAHT-CF. The band bends *within* its layers when printed rear
  face down, so this loads X-Y strength and never tests layer adhesion.
- **Grip varies by 15×** across the range, from 0.04 % seated strain on a
  small barrel to 0.62 % on a large one. That is the honest weakness: the
  ring does not know what it is gripping.

### The real decider is creep

A screw clamp holds by a preload you can restore with a hex key. A snap ring
holds by a sustained elastic strain, and every polymer here stress-relaxes —
it will be tightest on the day you fit it and there is nothing you can do
about it afterwards.

That makes the snap ring's viability a **material** question more than a
geometry one. In PLA it is a prototype and nothing more. In PAHT-CF, with a
~170 °C HDT, sustained 0.4 % strain is a much easier ask — which is the same
property that put PAHT-CF on the collar in the first place.

Fit one of each, leave them on the shelf for a month, and see which one you
still trust. That is the test, and it is the reason both exist.

## Why the cap flips the way it does

Both cord holes sit on the same radius (`CORD_RADIUS`, 26.00 mm), so the
line between the two bosses is the hinge axis — and both boss holes lie
**on** that axis. Rotating the cap about it does not change the cord length,
so the bungee only has to stretch the 2.2 mm needed to lift the cap clear of
the register. About 11 % strain on a 20 mm free length: well inside what
1/8 in shock cord does happily, forever.

That is also why nothing needs an anti-rotation key. The cap's orientation
is set by the two cords, not by the register, so the housing is free to sit
at any rotation on the objective.

## Checks after assembly

- Cap closes flat with no rock. If it rocks, the cap is bottoming on the
  register instead of the housing shoulder — increase `CAP_SKIRT_DEPTH`.
- Cap flips up and stays up.
- Collar does not rotate under a firm twist.
- Focus ring still turns freely through its whole range.
- Nothing inside the housing touches the glass.

## Service

Pull the housing off and the kill flash drops out the back for cleaning.
Nothing is bonded, and every fastener is a hardware-store M3.
