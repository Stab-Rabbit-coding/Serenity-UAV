# Battery options: split pack, low profile, and an ad hoc third pack (BATT-02)

**Status:** options for owner decision.
**Date:** 2026-10-26
**Author:** Claude (Claude Opus 5.5, Anthropic), under the direction of Stab-Rabbit-coding, per `AGENTS.md` §3.
**License:** CC BY-SA 4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)

## 1. Why

The verified Admiral Pro 6S 4000 (139 × 44 × 48 mm, 624 g) does not fit the
cargo roof band in either orientation (WBS BATT-02). The band is boxed in by
the tilt-actuator brackets (X ±31), the payload keep-out below (top Z 167.2)
and the roof. The existing cradle envelope is **142 × 50 × 38 mm**.

## 2. Space that is really free

| Bay | Free envelope | Already there |
| --- | --- | --- |
| Cargo roof band | 142 × 50 × 38 mm (the cradle) | tilt brackets each side, winch drums above (Phase 7), payload below |
| Head, Y 110–232 | cavity about 100–120 mm wide × 90 mm tall | forward of it: the nose Observer board behind the bow faceplate (camera, ToF, laser bores, Y about 0–70), node A / Bay A (Y 0–91) and the nose pitot line. The nose avionics trunk (Ethernet ring, CAN) runs aft through this bay, so a head pack must leave a harness channel. |
| Payload box (stowed) | 76.2 × 101.6 × 76.2 mm (3 × 4 × 3 in) | the mission payload, on the Observer hooks |

The head battery bay is not new: `docs/BATTERY_MOUNT.md` §3.3 already defines
a 160 × 65 mm head belly access panel from when the battery lived in the head.

## 3. Packs with verified listings (read 2026-10-26)

| Pack | Size L × W × H (mm) | Mass | Rating | Fits |
| --- | --- | --- | --- | --- |
| Tattu R-Line 6S 2200 95C, XT60 [PyroDrone listing] | 116 × 34 × 38.5 | 321 g | 95C | cargo cradle on its side (117 × 39.5 × 35 with fit), head |
| PyroDrone Graphene 6S 2200 75C, XT60 | 105 × 51 × 35 | 365 g | 75C | head; cargo cradle 2 mm too wide |
| Tattu R-Line v6.0 6S 1600 160C SQ, XT60 | 70 × 42 × 41 | 240 g | 160C | payload box |
| Admiral Pro 6S 4000 60C, EC5 (Motion RC) | 139 × 44 × 48 | 624 g | 60C | head only |
| Spektrum 6S 4000 50C G2 (retailer listing) | 144 × 42 × 43 | 580 g | 50C | head only |

Listings: <https://pyrodrone.com/collections/batteries/products/tattu-2200mah-6s-95c-22-2v-r-line-lipo-battery-for-7-quads-xt60>,
<https://pyrodrone.com/collections/batteries/products/pyro-drone-graphene-2200mah-6s-22-25v-75c-by-who-cares>,
<https://pyrodrone.com/collections/batteries/products/tattu-r-line-version-6-0-1600mah-6s-22-2v-160c-sq-lipo-battery-pack-xt60>,
<https://motionrc.com/eu/products/admiral-pro-4000mah-6s-22-2v-60c-lipo-battery-with-ec5-connector-epr40006pro>,
<https://kiwiquads.co.nz/product/spektrum-4000mah-6s-22-2v-smart-g2-lipo-50c-ic5/>.
No 6S 4000 with a verifiable listing is 38 mm or less thick. The Turnigy
6S 4000 40C (listed 142 × 37 × 43, 457 g) would fit on its side, but its
listing could not be read, and 40C is too little margin. A custom pack built
with 37 mm-wide cells on edge (MaxAmps advertises custom dimensions) is the
only single-pack 4000 mAh route for the cargo band.

## 4. Configurations

Hover current about 150 A (WBS PWR-CONN-01). Packs in parallel share current
roughly in proportion to capacity, so the demand is 150 A divided by the total
capacity. Thrust 8,540 gf; T/W floor 1.2 (WA-R18). CG is given relative to the
hover thrust line (tilt axis, Y +326.7).

| Configuration | AUW | CG vs thrust line | T/W | Capacity | C demand |
| --- | --- | --- | --- | --- | --- |
| Baseline 1 × Admiral 6S 4000 (does not fit) | 6,053 g (13.34 lbm) | +22.6 mm | 1.41 | 4,000 mAh | 37.5C |
| **S1: 2 × Tattu 6S 2200 95C, cargo + head, parallel** | **6,091 g (13.43 lbm)** | **+14.3 mm** | 1.40 | 4,400 mAh | 34.1C (95C rated) |
| S2: 2 × PyroDrone 6S 2200 75C, cargo + head | 6,179 g (13.62 lbm) | +13.0 mm | 1.38 | 4,400 mAh | 34.1C (75C) |
| **S1 + ad hoc third pack (Tattu 6S 1600 160C) in the payload box** | 6,336 g (13.97 lbm) | +15.0 mm | 1.35 | 6,000 mAh | 25.0C |
| S1 + third pack + 226 g mission payload | 6,562 g (14.47 lbm) | +15.7 mm | 1.30 | 6,000 mAh | 25.0C |
| L: one slim 6S 4000 in cargo (Turnigy, unverified) | 5,886 g (12.98 lbm) | +23.5 mm | 1.45 | 4,000 mAh | 37.5C |

Masses include an estimated 20–25 g of extra 10 AWG lead for the head pack.
Rough hover endurance scales as capacity × AUW^-1.5. On that basis S1 is about
+9 % on the baseline, and S1 plus the third pack about +29 % on S1.

## 5. How it leverages the Flight Engineer plan

The deferred Phase 12 range-extender plan (`deferred/WBS.md` §Phase12) already
adds a `J_BATT2` input and an ideal-diode / current-share combiner
(LTC4359- or LTC4370-class) to the Flight Engineer, plus a second-pack context
in `pwr_fault`. The split main pack uses that same combiner for its two halves.

- **Main pair (cargo + head):** `J_BATT` and `J_BATT2`. A two-input
  current-share combiner (LTC4370 class) keeps the halves balanced. The pair is
  charged and installed as a matched set.
- **Ad hoc third pack:** a third ideal-diode channel, `J_BATT3`, on the
  same combiner rail. Each channel is reverse-blocking, so an absent or
  faulted pack cannot drain or back-feed the others, and the third pack can be
  fitted only when a mission needs it.
- **Sharing:** with plain ideal-diode OR-ing the highest-voltage pack leads
  until it sags to the others. Every candidate above can carry the full 150 A
  alone (95C × 2.2 Ah = 209 A, 160C × 1.6 Ah = 256 A), so momentary hogging is
  within rating.

## 6. Maintainability

- **Cargo pack:** swapped from below through the open doors into the
  existing cradle, with cam straps and no roof access (`docs/BATTERY_MOUNT.md`
  Rev T5). The cradle needs a shim, because the pack is 117 × 39.5 × 35 inside
  142 × 50 × 38.
- **Head pack:** swapped through the head belly access panel (160 × 65 mm,
  `BATTERY_MOUNT.md` §3.3). The pack's 116 × 38.5 mm face passes through it.
- **Third pack:** clips into the payload box on the Observer hooks and is
  jettisonable, per the Phase 12 plan.

## 7. Open before build

1. A head-bay layout check, with the pack, its tray, the harness channel for
   the nose avionics trunk, the Observer pocket and the pitot line as
   solids. The head shell SCAD is still in the legacy frame (`TODO.md` §1.1.1).
2. Flight Engineer revision: `J_BATT2` / `J_BATT3`, combiner, fuses. The
   LTC4359 / LTC4370 data sheets must be read and cited, and Analog Devices'
   domicile confirmed under `AGENTS.md` §5.
3. The battery connector (PWR-CONN-01): XT60 parts are rated well below 150 A
   for the combined rail. Each pack carries a share; the combined lead needs an
   XT90 / AS150 class connector.
4. Bench check of each pack's temperature rise and voltage sag at its share of
   150 A, because published C ratings are manufacturer claims.
5. Tattu is a brand of a PRC-domiciled maker. `AGENTS.md` §5 governs
   semiconductors, not cells, but the owner's sourcing intent should decide
   between Tattu and an equivalent from another maker.
