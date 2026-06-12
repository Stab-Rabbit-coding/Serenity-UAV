# Serenity UAV — Battery Mounting & Exchange System

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Revision:** Rev R
**Date:** 2026-06-11

---

## 1. Battery Specification

The primary flight battery is a 6S 4000 mAh LiPo (see `docs/POWER_DISTRIBUTION.md §2`
and `current-specification/bom_revQ.csv`, ref BATT-6S-4000).

| Parameter | Value |
|---|---|
| Chemistry | Lithium Polymer (LiPo) 6S |
| Nominal voltage | 22.2 V (3.70 V/cell × 6) |
| Capacity | 4000 mAh |
| Mass | 1.65 lbm (750 g) |
| Typical dimensions (Tattu R-Line / Gens Ace 4000 mAh 6S) | 5.59 × 1.97 × 1.50 in (142 × 50 × 38 mm) (L × W × H) |
| Discharge connector | Amass XT60-M |
| Balance connector | JST-XH-7P (2.54 mm, 7-pin) |
| Max cont. discharge | 240 A (60 C) |
| Est. hover endurance | ~5.3 min at 45 A average draw (see §2.2 below) |

> **Endurance note:** 5.3 min is the calculated continuous hover figure at 45 A
> (50 % throttle). In practice, transit, climb/descent, and reduced-throttle segments
> extend usable flight time. The 4000 mAh cell is sized for the mass budget; see
> `POWER_DISTRIBUTION.md §11` for a dual-battery Phase 12 path if endurance is
> insufficient after initial flight testing.

---

## 2. Centre-of-Gravity Analysis

### 2.1 CG Target

For stable VTOL hover and forward-flight transition, the aircraft CG must lie within
the following range measured from the nose datum (X = 0):

| Mode | Acceptable CG range | Target |
|---|---|---|
| VTOL hover | 40 – 52 % of fuselage length | 46 % |
| Fixed-wing glide transition | 38 – 50 % of fuselage length | 44 % |

For a 24.02 in (610 mm) fuselage: **target CG = 11.02 in (280 mm) from nose**; acceptable range
9.33 – 12.48 in (237 – 317 mm).

### 2.2 Component CG Contributions

The table below estimates the moment contribution of each major mass group.
All station measurements are approximate; a CAD CG verification in Blender is
required before first flight (see §6 Procedure, step 3).

| Component group | Mass lbm (g) | Est. station from nose in (mm) | Moment (g·mm) |
|---|---|---|---|
| 4× EDFs + nacelle mounts | 0.838 lbm (380 g) | 20.08 in (510 mm) | 193 800 |
| 4× BLHeli32 ESCs | 0.221 lbm (100 g) | 19.29 in (490 mm) | 49 000 |
| 2× tilt servos + CF pivot rods | 0.322 lbm (146 g) | 19.29 in (490 mm) | 71 540 |
| 8× PocketBeagle 2 Industrial | 0.229 lbm (104 g) | 11.61 in (295 mm) | 30 680 |
| 4× Wash + 4× Zoë | 0.635 lbm (288 g) | 11.61 in (295 mm) | 84 960 |
| 4× Emma | 0.115 lbm (52 g) | 11.61 in (295 mm) | 15 340 |
| Kaylee (enclosed, 278 g) | 0.613 lbm (278 g) | 9.65 in (245 mm) | 68 110 |
| CF keel bar | 0.066 lbm (30 g) | 12.01 in (305 mm) | 9 150 |
| Airframe (shell + foam fill + hardware) | 1.323 lbm (600 g) | 11.42 in (290 mm) | 174 000 |
| Wiring harness + misc | 0.617 lbm (280 g) | 11.61 in (295 mm) | 82 600 |
| **Non-battery subtotal** | **4.98 lbm (2 258 g)** | — | **779 180** |

Non-battery CG = 779 180 / 2 258 = **13.58 in (345 mm) from nose** (57 % of fuselage — tail-heavy).

### 2.3 Required Battery Station

To achieve a 11.02 in (280 mm) total CG with the battery installed:

```
(M_no_batt × X_no_batt + M_batt × X_batt) / (M_no_batt + M_batt) = X_target
(2258 × 345 + 750 × X_batt) / (2258 + 750) = 280
779 010 + 750 × X_batt = 3008 × 280 = 842 240
750 × X_batt = 63 230
X_batt = 84 mm (3.31 in) from nose
```

**The battery centroid must be at approximately 3.31 in (84 mm) from the nose** —
this places it in the forward section of the head/bridge area of the Serenity model.

### 2.4 Battery Bay Location

The 3.31 in (84 mm) station is inside the head (bridge/cockpit) section of the
Serenity hull. The cargo section begins at approximately 3.94 in (100 mm) from the
nose on the 24" build. The battery tray therefore spans stations
**~2.36 – 5.12 in (~60 – 130 mm) from the nose**, sitting beneath the bridge deck
of the head section.

Access: a removable belly panel in the head section (two M3 button-head screws, no
tools required via coin slot in screw heads) exposes the tray from below.

> **Adjustability:** The tray rail system provides ±0.79 in (±20 mm) of fore-aft adjustment.
> Verify CG empirically during first hover by trimming flight controller level trim.
> Lock rail once balance is confirmed.

---

## 3. Battery Tray Design

### 3.1 Tray Envelope

| Parameter | Value |
|---|---|
| Interior cavity | 5.83 × 2.20 × 1.73 in (148 × 56 × 44 mm) L × W × H — battery + 0.118 in (3 mm) foam each side |
| Wall thickness | 0.118 in (3.0 mm) CF-PETG (structural) |
| Floor thickness | 0.157 in (4.0 mm) CF-PETG (load-bearing; battery rests on floor) |
| Rail length | 2.76 in (70 mm) (±0.79 in / ±20 mm travel; locks at 0.39 in / 10 mm increments via M3 detent screws) |
| Mounting rail interface | Two 6 × 3 mm CF flat bar slots (mates with CF-BAR-6X3 keel bar) |
| Strap anchor slots | 4× 0.157 in (4 mm) wide × 0.787 in (20 mm) long through-slots (2 per silicone strap) |
| Anti-vibration lining | 0.118 in (3 mm) closed-cell silicone foam bonded to tray floor and side walls |
| Connector exit | Rear wall slot 0.551 × 0.394 in (14 × 10 mm) — battery XT60 and balance lead pass through |
| Mass (printed, CF-PETG) | ~0.049 lbm (~22 g) |

### 3.2 Retention System

The battery is retained by three independent mechanisms, all tool-free:

1. **Forward positive stop:** A 4 mm CF-PETG rib at the front of the tray cavity
   prevents the battery from sliding forward under braking or negative-G loads.

2. **Silicone hook-and-loop straps (×2):** Two 16 mm wide silicone straps cross
   over the battery at the one-third and two-thirds positions (along battery length).
   Each strap passes through the tray anchor slots, loops over the battery top face,
   and fastens with a metal side-release cam buckle rated to 50 N.

3. **Anti-slip foam floor:** 3 mm medium-density silicone foam (Shore A 20–30) bonded
   to the tray floor provides friction and vibration damping. The foam pre-compresses
   by ~1 mm when the battery is strapped down, locking against vertical vibration.

**Load analysis:** Under 5G vertical crash load the battery experiences 750 g × 5 ×
9.81 m/s² = 36.8 N upward. Each strap buckle is rated 50 N; two straps = 100 N
combined retention force. Safety factor = 100 / 36.8 = **2.7 ×** — acceptable for
a crash retention requirement.

### 3.3 Belly Access Panel

A single 6.30 × 2.56 in (160 × 65 mm) belly panel in the head section provides battery access.

| Parameter | Value |
|---|---|
| Material | 0.079 in (2.0 mm) PETG (non-structural panel, not CF-PETG) |
| Fasteners | 2× M3 × 8 mm stainless button-head screws; coin-slot drive (no tool needed) |
| Hinge type | None — full removal; panel sits in a 0.059 in (1.5 mm) rebate that locates it flush with the hull skin |
| Seal | 0.079 in (2 mm) closed-cell EPDM foam tape in rebate (dust seal; not waterproof) |
| Panel mass | ~0.013 lbm (~6 g) |

The panel is identical on both the port and stbd belly faces, so a single spare covers
both positions.

### 3.4 CG Stability During Battery Exchange

When the battery is removed the aircraft CG shifts from 11.02 in (280 mm) to
13.58 in (345 mm) from the nose (tail-heavy, but inert). The landing legs (PETG-printed, 4-point contact) are
positioned so the aircraft rests stably on a flat surface with the battery absent.
Do not attempt battery exchange while the aircraft is held in hand — place it belly-up
on a flat surface for a controlled exchange.

---

## 4. Wiring Egress

### 4.1 Discharge Lead (XT60)

The XT60 discharge lead exits the battery tray through the rear wall slot, runs aft
along the CF keel bar for ~3.15 in (~80 mm), and enters the Kaylee enclosure through
the M16 EMC cable gland at J_BATT. Maximum lead length from battery terminal to
Kaylee enclosure: **6.30 in (160 mm)** (keeps cable inductance below 150 nH, well
within EMI budget).

Cable construction: 4 AWG silicone, twisted pair, 95 % braid shield, per
`Kaylee.md §Harness Specification`.

### 4.2 Balance Lead (JST-XH-7P)

The balance lead exits through the rear wall slot alongside the discharge lead and
runs to the Kaylee J_BAL connector. The balance lead uses a separate strain-relief
tie to the keel bar so it cannot pull the battery out of the tray during exchange.

Balance lead is not shielded (7-wire ribbon at < 5 µA measurement current) but is
enclosed inside the fuselage cavity and does not exit the aircraft skin.

---

## 5. Thermal Considerations

LiPo batteries generate heat in proportion to I² × R_internal. At sustained 45 A:

```
P_heat = I² × R_int = 45² × 0.030 Ω ≈ 60.75 W dissipated in pack
```

For a 750 g 6S LiPo (thermal mass ≈ 750 × 1.0 J/g·°C = 750 J/°C), a 5-minute
discharge raises pack temperature by:

```
ΔT = P × t / (m × c) = 60.75 × 300 / 750 ≈ 24 °C
```

Starting from 25 °C ambient → pack reaches ~49 °C at end of flight — below the
BQ76930 OTP trip threshold of 60 °C and within safe LiPo operating range.

**Mitigation:** The tray floor has four 8 × 2 mm ventilation slots that allow
fuselage airflow over the battery bottom face during forward flight. The slots are
covered by a stainless 0.5 mm perforated mesh screen to prevent debris ingestion.

---

## 6. Field Exchange Procedure

1. Land; confirm motors stopped; wait 10 s for ESC disarm.
2. Remove the transmitter from arm / put flight controller into safe mode.
3. Place aircraft belly-up on a clean, flat surface.
4. Unscrew the 2× M3 coin-slot belly panel screws (use a coin or flathead
   screwdriver), remove panel, set aside.
5. Disconnect the XT60 discharge connector (pull tab, not cable — Amass XT60
   connectors have an integrated pull tab).
6. Disconnect the JST-XH-7P balance lead (press the latch tab, pull straight).
7. Release both cam buckles; swing straps aside.
8. Slide battery straight out toward nose (tray rail guides prevent binding).
9. Insert fresh battery; slide into tray until it contacts the forward stop rib.
10. Confirm battery centroid is at the correct rail detent (marked "BAL" on tray).
11. Route XT60 lead and balance lead through the rear wall slot.
12. Fasten both cam buckles; confirm straps are not twisted.
13. Connect balance lead (JST-XH-7P, keyed connector — cannot be inserted reversed).
14. Connect XT60 (keyed — cannot be reversed; feel for positive engagement click).
15. Replace belly panel; tighten M3 screws finger-tight then 1/4 turn — do not
    over-torque (PETG boss thread strips at > 0.5 N·m).
16. Perform CG check if pack brand or model changed: hover with very gentle stick
    input and note pitch trim offset; adjust rail detent if > 5° trim required.

---

*© 2026 Steve Griffing, PE(CSE), CISSP-ISSEP, CPP — CC BY 4.0*
