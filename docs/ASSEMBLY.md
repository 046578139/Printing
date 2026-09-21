# Assembly

Per eye: 1 collar, 1 kill flash housing, 1 kill flash insert, 1 flip cap,
1 M3 socket head cap screw, 1 M3 hex nut, and about 240 mm of 1/8 in
(3.175 mm) shock cord. Double it for a binocular.

Screw length depends on which collar you print: **16 mm** for
`01_collar`, **30 mm** for `01b_collar_proto` — the prototype's pinch gap
is 13 mm wide, so the screw has to span a lot more air before it closes.

Every part is symmetric about the vertical plane, so there is **no left and
right** — print two of each and they fit either pod.

## Order of operations

**1. Kill flash into the housing.**
The insert loads from the **rear** of the housing (the wide end) and seats
against the integral front flange. It should need light thumb pressure. If
it drops through, the flange is missing or the aperture is wrong — stop and
check. Nothing glues; the objective traps it in the next step.

**2. Housing onto the objective.**
Push the housing straight on, front flange forward. Go square — the rear
lead-in chamfer will help, but a cocked start will gall the bezel. It should
take firm thumb pressure and stay put when inverted. Do **not** force a fit
that clearly does not want to go; go back to the gauge.

**3. Collar onto the barrel.**
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

## Which collar: screw or snap

Two mechanisms are provided. They are drop-in swaps — same cord ears, same
radius, same install direction — so you can fit one of each and decide on
your own hardware.

| | `01_collar` / `01b` screw clamp | `01c` snap C-ring |
|---|---|---|
| Hardware | M3 screw + hex nut per eye | none |
| Tools | hex key | none |
| Preload | **adjustable, re-tightenable** | fixed by geometry |
| Grip across a diameter range | narrow (0.83 mm stock, 4.14 mm on `01b`) | wide and self-adjusting |
| Rotational security | high, positive | friction only |
| Parts to lose | 2 | 0 |
| Ages by | loosening you can fix | creeping you cannot |

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
