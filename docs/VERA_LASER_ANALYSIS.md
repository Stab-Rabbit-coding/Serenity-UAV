# Vera Laser Indicator — Single-Source Feasibility & Spread-Angle Analysis

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**AI-assist:** Claude Opus 4.8 (Anthropic) — analysis authoring, 2026-07-05
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Revision:** Rev A (2026-07-05)
**Status:** Analysis — feeds Vera laser BOM decision (TODO.md §1.2c); no part sourced yet.

---

## 1. Problem Statement

The Vera board is installed at two locations that each project a laser aiming/marking
pattern of a different size at a different range (Vera.md "Laser driver"):

| Install | Pattern | Range | As-designed today |
|---|---|---|---|
| **Nose** (bow sensor pod) | 2 in × 2 in (51 × 51 mm) | 50 ft (15.2 m) | 520 nm green, **Class 3B**, custom-collimated crosshair |
| **Cargo** (nadir FPV mount) | 3 in × 3 in (76 × 76 mm) | 5 ft (1.5 m) | 650 nm red, **Class 3R**, 5 mW crosshair |

Two questions:

1. **Will a single green-dot laser indicator work for both locations?**
2. **Can different lens configurations provide the difference in spread angle?**

This analysis answers both and specifies the resulting design.

---

## 2. Assumptions

- Small-angle projection geometry: pattern is planar, normal to the beam axis, at the stated
  range. Full spread (fan) angle θ = 2·arctan((pattern/2) / range).
- Photopic (daylight, cone-mediated) vision; CIE 1931 luminous-efficiency function V(λ):
  V(520 nm) = 0.710, V(650 nm) = 0.107, V(555 nm) = 1.000 (peak).
- IEC 60825-1:2014+AMD1:2021 [REF-IEC-002] visible-CW (400–700 nm) accessible-emission
  limits, point source: **Class 1** ≈ 0.39 mW, **Class 2** ≤ 1 mW, **Class 3R** ≤ 5 mW,
  **Class 3B** ≤ 500 mW. FDA harmonization per 21 CFR 1040 [REF-FDA-001].
- "Indicator" = the emitted pattern; "source" = the laser diode + collimator + drive
  electronics; "terminal optic" = the pattern-forming element (DOE / line lens / diverging
  lens) at the aperture.

---

## 3. Calculations

### 3.1 Spread (fan) angle required at each install

```text
Nose:  θ = 2·arctan((51 mm / 2) / 15 240 mm) = 0.191°  (3.3 mrad)
Cargo: θ = 2·arctan((76 mm / 2) /  1 524 mm) = 2.864°  (50.0 mrad)
Ratio  θ_cargo / θ_nose = 15.0×
```

The two installs differ in required spread by **15×**. For a **dot** indicator the same
relation holds as beam *divergence* (spot diameter = divergence × range), so a dot sized to
2 in at 50 ft needs ≈ 3.3 mrad divergence and a dot sized to 3 in at 5 ft needs ≈ 50 mrad —
the identical 15× ratio.

### 3.2 Optical power / safety class at each install

Power is driven by **range and ambient**, not by pattern size:

- **Nose, 50 ft, full daylight:** the spot must exceed sunlit-surface contrast at 15 m. This
  is the reason the nose is Class 3B in the current design; green does not remove the
  requirement, it only lowers the *radiant* power needed (§3.3).
- **Cargo, 5 ft, shaded bay:** at 1.5 m almost any visible pointer is plainly visible; the
  current design uses a 5 mW (Class 3R) red module with margin to spare.

### 3.3 Green vs. red — the photopic lever (unifying on 520 nm)

```text
V(520)/V(650) = 0.710 / 0.107 = 6.64×
```

At equal *radiant* power, 520 nm green is **6.64× brighter to the eye/camera** than 650 nm
red. Consequences:

- The retired cargo red module (5 mW, Class 3R) delivers the perceived brightness of only
  **5 mW ÷ 6.64 = 0.75 mW of green**. So a green cargo unit sized for the same 5 ft
  visibility can run **≤ 1 mW → Class 2** (or even Class 1), *improving* cargo-bay eye safety
  over the red it replaces (Class 2 is protected by the blink/aversion reflex; no interlock
  needed).
- The nose still needs Class 3B-level radiant power for reliable 50 ft daylight contrast even
  in green — green reduces the required milliwatts but not enough to leave 3B at that range.

---

## 4. Results — Determination

**A single green (520 nm) laser *source* CAN serve both installs**, but it is **not** a single
fixed "indicator": the two installs remain distinct in **two independent parameters**, and a
single laser cannot collapse both:

| Parameter | Nose | Cargo | Set by | Shareable source? |
|---|---|---|---|---|
| Spread / fan angle | 0.19° (3.3 mrad) | 2.86° (50 mrad) | **Terminal optic** (DOE / lens) | **Yes** — same diode, per-location optic |
| Optical power / IEC 60825-1 class | Class 3B (≤ 500 mW) | Class 2 (≤ 1 mW green) | **Drive current (hardware limit)** | **Yes** — same driver, per-location current limit |
| Class 3B safety apparatus (key interlock, emission indicator, beam shutter, labeling) | **Required** | Not required (Class 2) | IEC 60825-1 / 21 CFR 1040 | Present at nose only |

So the **shared** design is: one 520 nm green laser **diode + collimator + driver board +
MOSFET switch** (Vera already carries exactly one shared driver — Q1 AO3400, R1, R2, J_LASER).
The **per-location** differences are just (1) a terminal optic and (2) a hard current limit.

### 4.1 Answer to Q1 — single green-dot indicator for both?

**Yes for the source and driver; no for a single fixed setpoint.** One green-diode design
populates both boards, but each site is commissioned with its own terminal optic and its own
hardware current limit. The cargo unit, exploiting green's 6.64× photopic advantage, can be
Class 2 (≤ 1 mW) — safer than today's red — and needs none of the nose's Class 3B interlock
hardware. **Critical safety constraint:** because the two boards share a diode capable of
Class 3B power, the cargo current limit **must be hardware-enforced** (fixed sense resistor /
current-limited driver), not firmware-only, so no software fault can drive the cargo diode to
3B levels above ground crew during loading.

### 4.2 Answer to Q2 — different lens configurations for the spread difference?

**Yes.** The spread angle is a property of the *terminal optic*, decoupled from the source:

- **Crosshair (reticle) — matches the current design intent:**
  - *Diffractive optical element (DOE):* the crosshair fan angle is a fixed DOE parameter.
    Catalog DOE crosshair/line generators span roughly 1°–110°; the **cargo 2.86°** is a
    standard off-the-shelf DOE. The **nose 0.19°** is *below* the usual DOE range — it is
    essentially a near-collimated cross, which is why the nose optic is a **custom
    near-collimated element**, not a stock DOE.
  - *Refractive:* crossed cylindrical lenses (or a Powell lens per line) set the fan angle by
    lens geometry; a longer effective focal length gives the tighter nose fan.
- **Dot indicator:** the spot size is set by the collimator focus. The nose runs at the
  collimation/diffraction limit (~3 mrad); the cargo adds a weak **diverging lens** to open
  the spot to ~50 mrad. Same source, one extra plano-concave element at the cargo aperture.

The 15× spread ratio is spanned by two different terminal optics on the *same* collimated
green source — exactly the "different lens configuration per location" the question proposes.
The optic sets **geometry only**; it does **not** address the power/class difference (§4.1).

### 4.3 Dot vs. crosshair trade (informational)

A **dot** is simpler and cheaper (no DOE; the cargo just adds a diverging lens) but conveys
only *position*. A **crosshair** additionally conveys *orientation and scale* (a sized reticle
reads as a measurement). For the nose *aim-point*, a dot is adequate. For the cargo *drop
footprint* (a 3 in × 3 in zone), a dot sized to 3 in reads as the footprint, but a crosshair or
a 4-corner box reads the zone edges more clearly. Pattern choice is independent of the
source/optic/current split above and can be made per install.

---

## 5. Recommended Design

1. **Source (shared):** one 520 nm green laser diode + integrated collimator, driven by the
   existing Vera shared driver (Q1 AO3400 logic-level N-FET, R1 100 Ω gate, R2 10 kΩ
   pulldown, J_LASER). This retires the separate 650 nm red cargo module (unifies BOM to a
   single diode family).
2. **Terminal optic (per location):** nose ≈ 0.19° custom near-collimated crosshair (or ~3
   mrad dot); cargo ≈ 2.86° stock DOE crosshair (or a ~50 mrad diverging-lens dot).
3. **Optical power / class (per location, HARDWARE-limited):**
   - Nose: Class 3B (≤ 500 mW) with the full IEC 60825-1 apparatus already stubbed on Vera
     (LASER_KEY_IN interlock, LASER_IND emission indicator) **plus a mechanical beam shutter**
     (not yet on the board — see §6).
   - Cargo: Class 2 (≤ 1 mW green), blink-reflex safe, no interlock/shutter. Fixed hardware
     current limit sets the cap independent of firmware.
4. **Do not source the green diode or either terminal optic** until a real datasheet with a
   manufacturer-stated (or independently computed) mW rating and IEC 60825-1 class is added
   to REFERENCES.md — this extends the existing pending item under REF-IEC-002 and the
   "Do not fabricate or procure against the placeholder" discipline (TODO.md §1.2c).

---

## 6. Open Items / Follow-on

- **Nose Class 3B beam shutter:** Vera today implements only the electronic interlock
  (LASER_KEY_IN / LASER_IND); IEC 60825-1 Class 3B also requires a mechanical beam-stop/shutter
  — add to the nose optical-mechanical design.
- **Cargo hardware current limit:** confirm the shared driver enforces the Class 2 cap in
  hardware at the cargo install (fixed sense resistor / current-limited LDO), not by firmware.
- **Part sourcing:** 520 nm green diode + nose custom-collimated optic + cargo DOE; each needs
  a verified datasheet + REFERENCES.md entry before procurement.
- **Nose bore reuse flag:** `bow_sensor_pod.scad` `LASER_BORE_D = 12.5 mm` is sized for the old
  12 mm red module — re-verify against the sourced green module's real dimensions (Vera.md
  "Open — stale bore flag").

---

## 7. Standards Citations

- **[REF-IEC-002]** IEC 60825-1:2014+AMD1:2021 — Safety of Laser Products, Part 1: Equipment
  Classification and Requirements. Class thresholds (Class 1/2/3R/3B) and the Class 3B
  requirements for interlock, emission indicator, beam stop, and labeling.
- **[REF-FDA-001]** 21 CFR Part 1040 — Performance Standards for Light-Emitting Products;
  harmonized with IEC 60825-1 for US emission limits.
- **[REF-SENSOR-002]** Benewake TFmini-S (ToF sensor co-located with the laser; unchanged).

---

## 8. References

- CIE 1931 photopic luminous-efficiency function V(λ) — standard tabulated values.
- `avionics/kicad/Vera.md` — "Laser driver — location-specific population", "Open — stale bore
  flag".
- `docs/POWER_DISTRIBUTION.md` §3.2.1 — Vera laser electrical load (nose Class 3B burst).

---

*© 2026 Steve Griffing, PE(CSE), CISSP-ISSEP, CPP — CC BY 4.0*
