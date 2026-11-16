# Cargo Doors — Integrated (Print-in-Place) Hinge vs Separate Doors, SLS

**License:** CC BY-SA 4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Date:** 2026-11-01
**Author:** Steve Griffing, PE(CSE) (Stab-Rabbit-coding). Trade study by
Claude Opus 5.5 (Anthropic) under the author's direction.
**WBS:** §0.13
**Question (owner, 2026-11-01):** should the cargo-bay doors be printed with
integrated hinges, in the same print as the cargo section?

## 1. Recommendation

**Don't print the doors in place.** Keep them as separate SLS parts on the
3 mm CF-rod piano hinge. Take the main benefit of integration, hinge-line
alignment, in two other ways:

1. **Same build:** order the doors in the same 3D Systems build as the
   forward hull section, nested in their installed position or near it. They then
   share a powder lot and a shrink history.
2. **Line-ream the hinge at assembly:** print the knuckle bores undersize.
   With the door clamped closed, ream the shell-side and door-side knuckles
   in one pass to the final pin fit. This gives co-linear bores without
   depending on as-sintered hole accuracy.

The current 0.15 mm per-side bore clearance can't be relied on as-sintered.
It's below the guide's 0.2 mm minimum for SLS-to-SLS gaps
[REF-MFG-001 p. 12]. Line-reaming closes this; see the WBS item.

## 2. What integration would mean

Each door would be printed captive on its hinge, with printed PA CF knuckles
and a printed pin, inside the cargo-shell build. The guide supports
integrated hinges in principle. It prefers an integrated hinge to a living
hinge (p. 13), shows a hybrid integrated hinge at 0.3 mm clearance (p. 5),
and recommends more than 1 mm clearance in the as-built (disengaged) state
(p. 12).

## 3. Trade

Numbers are from the committed STLs, at PA CF 1.11 g/cm³ [REF-MAT-015].

- **Hinge strength: not a discriminator.** The worst door sees 7.24 N
  (1.63 lbf) of air load at 87 kt (`docs/CARGO_DOOR_LATCH_SPEC.md` §1) over
  4 knuckles. That's 0.26 MPa of shear on a printed Ø3 mm pin, against a
  24 MPa estimate (PA CF knocked-down tensile ÷ √3), about 95×. The pin
  axis runs along hull Y, which lies in the build plane in the cargo shell's
  orientation, so the pin is a beam in-plane (R-BEAM). The payload hangs
  from the autolatch, not the doors.
- **Mass: integration gains little.** The shell-side retention blocks
  (4.0 cc, 4.4 g) are already merged into the cargo shell. Integration
  would delete only the two CF rods (about 1.2 g each, at 1.6 g/cm³
  **ASSUMED**) and the grub screws. That's about 3.5 g per aircraft.
- **Repair: strongly against integration.** The doors sit on the belly and swing
  down toward the ground during hover payload operations; they are the most
  exposed printed parts. Separate, a door costs 13.4–14.8 g and a pin pull to
  replace. Integrated, a cracked door or knuckle scraps the whole forward hull
  section (head+cargo in one piece): 457 cc, 507 g in PA CF (commit `d92c4f14`).
  It's the largest part on the aircraft, needs the sPro 140, and carries the
  merged interior and the twin battery tray seat.
- **Print risk: against integration.** A fused hinge is found only at
  breakout and scraps the whole shell. The guide warns that SLS "is very
  sensitive to process variation" (p. 16). The port door also laps 6 mm over
  the starboard door at the centerline (port X −6.0 to 50.5 mm). Printed
  closed, that lap would trap powder in a sub-millimeter gap, so the doors
  would have to be printed open. Opened 90°, each door hangs about 56 mm
  below the belly, adding that height to a section that already needs the
  sPro 140.
- **Powder removal: against integration.** A captive pin at the guide's
  0.3 mm clearance, over 4 × 12 mm knuckles, needs the axle treatment on
  p. 4: rails, 2 mm+ relief and air ports. That's more geometry in a part
  that currently has none.
- **Hinge play: neutral to slightly against.** A printed pin needs at least
  0.3 mm per side (pp. 7, 12), double today's 0.15 mm. That adds door
  flutter margin to the latch hook, which is set at 0.3 mm per side
  (latch spec).
- **Service access: against integration.** A removable door allows bench
  work on the bonded horn, latch hook and pushrod (latch spec §§2–4). A
  captive door means working on them inverted, in the bay.
- **Hinge alignment: for integration.** This is the one real benefit. Both
  hinge halves come from one build with no stack-up. Recommendation steps 1
  and 2 recover it without the costs above.

## 4. When to revisit

Revisit if any of these changes: the doors start carrying payload or ground
loads; the cargo shell becomes cheap to reprint; or 3D Systems reports a
proven print-in-place clearance for DuraForm PA CF, with powder removal, at
this hinge length.
