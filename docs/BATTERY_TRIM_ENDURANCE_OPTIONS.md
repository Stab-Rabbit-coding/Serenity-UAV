# Battery Options for Forward Trim and Endurance (live ballast, plan 003 R10)

**License:** CC BY-SA 4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Date:** 2026-10-31
**Feeds:** `docs/plans/2026-10-31-003-feat-forward-trim-room-relocation-plan.md` R10
**Builds on:** `docs/BATTERY_SPLIT_OPTIONS.md` (S1 split pack, head cavity)
**AI note:** Claude Opus 5.5 (Anthropic) under the direction of Steve Griffing
(Stab-Rabbit-coding). The pack data is from manufacturer datasheets and retailer
listings (§4). Arithmetic is screening only.

> **ENGINEERING REVIEW REQUIRED.** Every figure here must be reviewed and accepted by a
> qualified engineer before it is applied to any system carrying risk to life or safety.

## 1. Basis

- **Baseline (S1):** two Tattu R-Line 6S 2200 packs. One is in the head at Y 216 and
  one in the cargo band at Y 344.2. The baseline uses the rail-lever arrangement:
  AUW 6,232 g, CG +16.3 mm aft of the thrust line (Y 326.7).
- **Hover current:** about 150 A (WBS PWR-CONN-01), scaled with AUW^1.5. Parallel packs
  share current roughly in proportion to capacity.
- **Endurance:** capacity × AUW^-1.5, relative to S1. Thrust is 9,480 gf (4 × 2,370 gf, 2026-11-02 correction).
- **"+pivot":** the offset after the single 0.5 in pivot shift (plan R7).
- **Head fit:** the head cavity is about 100–120 mm wide × 90 mm tall over Y 110–232
  (`docs/BATTERY_SPLIT_OPTIONS.md` §2). A harness channel must stay clear. **No option
  below has been fit-checked on the mesh.**

## 2. Results

| Option (head pack; cargo pack unchanged unless noted) | AUW | CG | +pivot | T/W | Endurance | Worst pack, % of rated continuous |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| S1 baseline: Tattu 2200 | 6,232 g (13.74 lbm) | +16.3 mm | +7.4 mm | 1.37 | — | 36 % |
| **A. 2 × Tattu 2200 side by side, flat** (116 × 77 × 34) | 6,553 g (14.45 lbm) | +10.1 mm | **+1.0 mm** | 1.30 | **+39 %** | 26 % |
| B. MaxAmps 6S 4000 (140 × 46 × 54) | 6,503 g (14.34 lbm) | +12.1 mm | +3.0 mm | 1.31 | +32 % | 81 % |
| C. MaxAmps 6S 3750 (140 × 46 × 42) | 6,497 g (14.32 lbm) | +12.2 mm | +3.1 mm | 1.31 | +27 % | 71 % |
| D. 2 × MaxAmps 6S 2375 side by side (85 × 86 × 34) | 6,503 g (14.34 lbm) | +9.6 mm | +0.5 mm | 1.31 | +48 % | **109 % — fails** |
| E. D plus a MaxAmps 2375 in cargo | 6,478 g (14.28 lbm) | +9.6 mm | +0.5 mm | 1.32 | +53 % | **106 % — fails** |
| **F. Both Tattu 2200 in the head, side by side; cargo cradle emptied** | 6,232 g (13.74 lbm) | +9.7 mm | **+0.8 mm** | 1.37 | 0 % | 36 % |

## 3. Findings

1. **Two low-profile packs side by side in the head (A) is the best verified option.**
   - It gives +39 % endurance and moves the CG 6.2 mm forward.
   - It uses a pack that is already qualified. The current load is only 26 % of the
     continuous rating.
   - It costs T/W 1.37 → 1.30. With the 226 g mission payload, T/W falls to about 1.26.
     That is above the 1.2 floor (WA-R18) but narrows the margin.
2. **Moving the cargo pack into the head (F) gives the same CG gain at no mass cost.**
   - It frees the 142 × 50 × 38 mm cargo cradle, which is useful for relocated equipment
     (aft node pouches; the FE can is too tall for it).
   - This is the cheapest balance move found anywhere in this study series. A third pack
     can then go back into the cargo cradle when a mission wants endurance more than
     balance.
3. **The longer single 4000 and 3750 packs (B, C) do less for CG.** At 140 mm they push
   their centroid aft, and they would clash with the cargo pack at Y 286 unless the
   cargo pack moves too.
4. **The MaxAmps 2375 has the best energy density (178 Wh/kg), but it is rated only
   50 A continuous.** Under the 150 A hover it exceeds that rating (D, E). Reject it for
   hover service.
5. **Li-ion (Molicel P45B/P50B 21700 packs) is rejected for hover.**
   - The listings give 45–50 A continuous per 6S2P pack (vendor figures; the cell rating
     conflicts between sources at 50 vs 60 A).
   - The 6S2P pack is about 900 g for 10 Ah.
   - It could only serve as a cruise-segment range extender beside a LiPo pair.
6. **Amprius SiCore (US) is reported at 450 Wh/kg for the SA102,** but no datasheet with
   a C-rate or dimensions was found. Watch item only.

## 4. Sources and sourcing flags

- MaxAmps 6S datasheets (assembled in the USA; cell origin not stated, so confirm it
  against the sourcing rule):
    - 2375: <https://cdn.shopify.com/s/files/1/0609/0811/0079/files/MaxAmps_2375_6S_LiPo_Data_Sheet.pdf>
      (85 × 43 × 34 mm, 296 g, 52.7 Wh, 49.88 A continuous).
    - 3750: <https://cdn.shopify.com/s/files/1/0609/0811/0079/files/MaxAmps_3750_6S_LiPo_Data_Sheet.pdf>
      (140 × 46 × 42 mm, 586 g, 83.3 Wh, 142.5 A continuous).
    - 4000: <https://cdn.shopify.com/s/files/1/0609/0811/0079/files/MaxAmps_4000_6S_LiPo_Data_Sheet.pdf>
      (140 × 46 × 54 mm, 592 g, 88.8 Wh, 128 A continuous).
- Tattu R-Line 6S 2200: see `docs/BATTERY_SPLIT_OPTIONS.md` §3. **Flag:** Tattu (Grepow)
  is PRC-domiciled. The sourcing rule is written for silicon makers, so the owner should
  decide whether it extends to cells. If it does, A and F need a non-PRC 2200-class pack;
  the MaxAmps 2000 6S (68 × 46 × 43 mm, 280 g, datasheet in the same CDN folder) is a
  candidate that still needs a C-rate check.
- Li-ion: KiwiQuads P50B 6S2P listing
  <https://kiwiquads.co.nz/product/kiwiquads-21700-p50b-6s2p-10000mah-li-ion-pack/>.
- Amprius: Q2 2025 shareholder letter
  <https://ir.amprius.com/sec-filings/all-sec-filings/content/0001628280-25-038899/exhibit991q22025letterto.htm>.
- Not yet catalogued in `REFERENCES.md`. That is a TODO before any of these is adopted.

## 5. Next checks

1. Fit two flat packs (77 × 116 × 34 mm, with sled and harness channel) in the head on
   the real mesh.
2. Decide whether the sourcing rule covers cells.
3. Re-run the T/W and current checks at the heaviest-payload AUW with option A.

## 6. Detailed placement (2026-10-31): twin flat tray in a one-piece head+cargo hull

Two tools reproduce this result:

- `tools/merge_head_cargo_shell.py` builds the one-piece head+cargo hull.
- `tools/twin_head_pack_fit.py` checks the tray against every other component.

The tray geometry is in `airframe/openscad/fuselage/twin_pack_tray.scad`. The rendered
parts are in `airframe/stls/fuselage/head/twin_pack_{tray,sled,gate}.stl`.

**Why the head and cargo had to merge.** No 2 × 2200 arrangement fits in the head as
built; the sides, flat and stacked layouts all fail. Only today's single band fits, at
1 mm clearance. Removing the splice collar ring and the cargo cradle opens a twin flat
band.

**The merge**

- The published head is kept for Y < 227 and the published cargo for Y > 241.5.
- The seam zone, Y 227–241.5, is rebuilt as plain 2 mm skin. It is extruded from clean
  rings measured at Y 226 and Y 242. The old collar mating lands are dropped.
- The four cargo cradle hanger bosses are removed.
- The result is one watertight body, about 457 cm³. Every 0.5 mm slice across the seam
  is one closed ring, and the cavity is open through the seam.
- This file, `head_cargo_splice_collar.stl` and the cradle are now retired.

**Placement**

| Item | Where |
| --- | --- |
| Pack band | 69.5 W × 41.0 H, Zc 191, Y 172–292. Both packs lie flat; the lanes are at X ±17.4. |
| Tray | Ceiling, walls bonded to the skin (seat ≤ 52 mm³), full floor, and a forward stop at Y 168–172. |
| Loading | Each pack is lifted in on its own sled through the open clamshell doors, with the payload out. It slides forward on the centreline corridor (\|X\| ≤ 17.75, Y 292–400, Zc 189.5), climbs a 1.5 mm ramp, then steps sideways into its lane. |
| Retention | A hinged aft gate. It has a pocket for each sled tail tab, which holds each pack fore/aft and laterally. |
| Nose avionics trunk | Rerouted to a port side channel at X 38.5–48.5, Z 193–201. |
| Optional third pack | The bare Tattu 6S 1600 (70 × 42 × 41 mm) fits only at Y ≈ 302–372, Zc 190, with 1 mm to the cargo roof above and the payload envelope below. There is no room for a sled or strap: with 1.5 mm of retention allowance it hits the roof or the payload. It does not block the payload, the hoist lines, the winch or the Observer tray, but it sits in the loading corridor, so it comes out first and goes in last. Observer line of sight not yet checked. A third 2200 does not fit (108 mm of room, needs 120). |

All checks pass with a 1 mm gap against both shells and every cargo and head envelope.

**CG and endurance** (same basis as §2; the twin-pack centroid is Y 232)

| Configuration | CG | +pivot | Endurance |
| --- | ---: | ---: | ---: |
| F: two packs in the tray | +11.3 mm | +2.4 mm | 0 % |
| A: tray + Tattu 1600 in the corridor | +10.6 mm | +1.5 mm | +29 % |

These are about 1.5 mm worse than the §2 screen, which assumed the packs sat at the
head-cell station (Y 216).

**Printed parts (PA CF).** The tray is 88.5 g, the two sleds 11.8 g and the gate 3.3 g.
The retired parts are the collar (11.5 g), the cradle (39.2 g), the strap and the
head-cell rail and sled. The ledger has not been updated yet.

**Open items**

- Re-run the gate latch and catch statics for 2 × 321 g at 79.4 g, per
  `docs/BATTERY_MOUNT.md` §8.
- Update the ledger.
- Switch the layout tools over to the merged hull and archive the collar.
- Add the merged part to `bake_hull_frame` / PROJECT_INDEX.
- The 86 MB merged STL is left untracked (regenerable with the tool). Decide whether to commit it; the other shells are 35–49 MB.
