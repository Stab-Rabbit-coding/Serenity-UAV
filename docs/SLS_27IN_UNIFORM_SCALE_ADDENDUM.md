# Serenity UAV — 27 in Uniform Fuselage Scale: Addendum to the Trim Study

**License:** CC BY-SA 4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Date:** 2026-10-31
**Tool:** `tools/sls_scale_trim_study.py` section (F)
**Supersedes:** the forward-plug results (§3 option rows and §8 item 1) of
`docs/SLS_27IN_TWO_SECTION_TRIM_STUDY.md`. Its two-section, joint and datasheet content stands.

> [!WARNING]
> **ENGINEERING REVIEW REQUIRED — this output is not a substitute for a
> qualified engineer.** Every result, calculation, and recommendation produced
> with this skill **must be independently reviewed and accepted by a properly
> qualified individual** — a licensed Professional Engineer or an equivalently
> qualified authority for the jurisdiction and discipline — **before it is
> applied to any system carrying risk to life or safety.**

> [!CAUTION]
> **This skill informs engineering judgment; it does not replace it.** Applying
> unreviewed results to real equipment or hardware — even where no life-safety
> risk exists — carries a risk of equipment damage or property loss. It is
> reference material provided AS-IS (see LICENSE §5), is not an engineering
> service, and does not constitute a sealed, certified, or reviewed work
> product for any specific project.

Labels: **[REPO]** repo document or tool output. **[CALC]** my arithmetic. **[ASSUMED]** needs
verification. Datum R2, Y aft-positive, positive offset = CG aft of the thrust line.

## 1. Owner direction (2026-10-31)

1. The extra length is **distributed over the whole fuselage, scaled uniformly** (no plug).
2. **Nose electronics are installed and maintained through the cargo bay.**

Item 2 closes the access question I raised for merging the head and cargo sections: the head's open
aft face is not needed, so one head+cargo print is fine. It adds a design requirement: Bay A, the
nose Observer and the head cell have to be installable as cartridges or sleds from the cargo
aperture. At 27 in every reach grows 12.5%.

## 2. What a uniform scale does to the CG problem

Method [CALC]: fuselage stations ×k about the nose; hull shells and collars ×k² in mass (2 mm
wall kept); nacelles, wings and procured parts keep their size, with the nacelles riding the
pivot. Baseline is the 10-27 rail-lever arrangement (AUW 6,232 g, +16.3 mm) [REPO].

| Length | Hull mass added (CF-PETG, ledger basis) | AUW | Offset at the scaled pivot | Pivot move to zero | Offset after your 0.5 in move |
|---|---|---|---|---|---|
| 24 in | 0 | 6,232 g | +16.3 mm | 0.91 in | +7.4 mm |
| 25 in | +80 g | 6,313 g | +17.6 mm | 0.98 in | +8.7 mm |
| 26 in | +164 g | 6,396 g | +19.0 mm | 1.05 in | +10.0 mm |
| **27 in** | **+250 g** | **6,483 g** | **+20.5 mm** | **1.13 in** | **+11.4 mm** |

Uniform scaling keeps the pivot at the same fraction of hull length, so the required fraction
does not change (about 57% of length from the nose, against 54% now). The absolute move grows with
length. **Your 0.5 in move leaves +11.4 mm at 27 in, worse than +7.4 mm at 24 in.** Scaling by
itself does not help the CG. What it provides is volume.

## 3. How much trim the extra volume buys

The cell rail runs from the stop (Y 156) to about Y 402; the two cells fill 232 mm of that 246 mm
(14 mm of slack) [REPO CG study]. If the rail span grows with the hull, 27 in adds about 31 mm
[CALC, ASSUMED: the real limit is set by fixed-size parts such as the tilt brackets, winch and
payload keep-out, which do not scale].

| Trim source | Authority [CALC] |
|---|---|
| Both cells sliding together through 45 mm of slack | 642 g × 45 mm / 6,483 g = **4.5 mm** total (±2.2 mm) |
| One cell alone through 45 mm | 2.2 mm total |
| 100 g removable ballast at the nose | 5 mm (arm ~312 mm), costs ~2.4% endurance |
| **Pivot station, 1 mm of shift** | **~0.71 mm of CG** (1 − nacelle mass fraction 0.286) |

My earlier ±6.4 mm working target would need about 129 mm of slack from cell travel alone, three
times what uniform scaling provides. So the cells cannot supply it.

**The strongest trim lever is the pivot itself.** Your own plan already moves the spar aft. If the
spar carry-through had two or three **indexed pivot stations** (for example ±0.5 in about nominal,
in 0.25 in steps), that would give about ±9 mm of CG authority with no added mass and no moving
mass. It is a bench-and-field adjustment. It also moves the wing relative to the CG, so it needs
the transition-pitch check and a load-path review of the spar saddle, tilt brackets and wing-root
flanges before it is a design [REPO skill, `weight-and-balance.md` §4].

## 4. Mass and endurance at 27 in, PA CF hull

Hull and collars today: 943.7 g. Endurance by mass^-1.5 on 6,232 g [REPO mass-diet plan].

| Density basis for the real FDM shells | PA CF hull, scaled | Change vs today | Endurance |
|---|---|---|---|
| 1.28 g/cc (solid) | ×1.2656 × 0.867 | **+92 g** | −2.2% |
| 1.05 g/cc (ledger) | ×1.2656 × 1.057 | **+318 g** | −7.2% |

At 25 in the same table gives −56 g (+1.4%) and +139 g (−3.2%); at 26 in, +17 g (−0.4%) and +227 g
(−5.2%). This cuts against the mass-diet plan, which needs a 555 g reduction. Uniform 27 in
costs endurance in every case, and the retrieval sortie is already unmet [REPO R9]. Weighing a
printed 2 mm shell decides which row applies, as before.

## 5. Joint J2 at 27 in (two-section hull, one collar)

The collar moves to Y ≈ 490. Aft mass 942 g (aft shells scale, equipment does not), arm 85 mm.
At the repo's 79.4 g design load [REPO plan 001 R7], load normal to the hull axis [CALC]:

| | 24 in | 27 in |
|---|---|---|
| Shear | 645 N (145 lbf) | **733 N (165 lbf)** |
| Bending | 46.9 N·m (415 lbf·in) | **62.7 N·m (555 lbf·in)** |
| Ultimate at FOS 3.0 [REPO] | 141 N·m (1,245 lbf·in) | **188 N·m (1,665 lbf·in)** |

The aft mass is assumed rigid and the whole load reacted at J2; no bond allowable is sourced, so I
report no margin. Test the coupon to the 27 in ultimate.

## 6. Printing at 27 in uniform [CALC, bounding boxes]

Two sections: front (head+cargo) about 490 × 225 × 186 mm; rear (middle+rear) about
214 × 225 × 204 mm; one piece 686 × 225 × 236 mm.

| Machine | Front | Rear | One piece |
|---|---|---|---|
| EOS P 770 (700 × 380 × 580) | flat | flat | flat, 14 mm spare |
| 3D Systems sPro 230 (550 × 550 × 750) | flat | flat | tilted only |
| Quickparts listing (500 × 500 × 725) | flat | flat | tilted only |
| Protolabs listing (482 × 482 × 431) | tilted | flat | no |
| ProX 6100 (381 × 330 × 460) | no | flat | no |

Ask 3D Systems about the front section at 490 mm on a machine that runs PA CF.

## 7. Revised recommendation

1. **Decide the length by the trim lever, not the volume.** If the aim is trim authority, the
   cheapest lever is an indexed pivot station (±9 mm of CG, no mass). Volume from scaling adds only
   about ±2 mm and costs 92–318 g.
2. If fidelity requires 27 in uniform, plan the spar pivot **1.1 in aft of the scaled position** and
   an **indexed pivot** around it, so the field adjustment is in the pivot, not in ballast.
3. **Before committing to 27 in, rebuild the free-space search on scaled shells.** The 10-27 study
   found no further equipment moves at 24 in because the tightest items had no clear forward slot.
   Scaling adds length in the cargo and head sections. Whether the flight engineer, aft nodes or
   Observer can move forward there is unknown until the scaled meshes exist. I did not run it:
   it needs re-baked shells, and my numbers above use scaled stations only.
4. Single-piece printing at 27 in fits only a P 770-class machine flat. Two sections still fit more
   machines.
5. Weigh a printed 2 mm shell before relying on any SLS weight saving.

## 8. Not done

No scaled-mesh free-space search, no FEA, no transition-pitch analysis, no vendor quote. The rail
slack figure is an assumption. All other limits are as in the earlier study.
