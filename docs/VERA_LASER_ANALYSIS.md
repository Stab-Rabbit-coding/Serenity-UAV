# Vera Laser Indicator — Single-Source Feasibility & Spread-Angle Analysis

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**AI-assist:** Claude Opus 4.8 (Anthropic) — analysis authoring, 2026-07-05
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Revision:** Rev A1 (2026-07-05)
**Status:** Analysis — feeds Vera laser BOM decision (TODO.md §1.2c); no part sourced yet.
**Rev A1 correction:** the Rev A conclusion that the nose is inherently Class 3B was
over-conservative (worst-case spread-pattern + naked-eye-in-full-sun). For Vera's actual
camera-visibility requirement with a concentrated dot + camera strobe-difference detection,
**both installs are Class 2 (≤ 1 mW)** — no Class 3B apparatus. See §3.2.

---

## 1. Problem Statement

The Vera board is installed at two locations that each project a laser aiming/marking
pattern of a different size at a different range (Vera.md "Laser driver"):

| Install | Pattern | Range | As-designed today |
|---|---|---|---|
| **Nose** (bow sensor pod) | 2 in × 2 in (51 × 51 mm) | 50 ft (15.2 m) | 520 nm green, **Class 3B**, custom-collimated crosshair — *revised to Class 2 dot, §3.2/§4* |
| **Cargo** (nadir FPV mount) | 3 in × 3 in (76 × 76 mm) | 5 ft (1.5 m) | 650 nm red, **Class 3R**, 5 mW crosshair — *revised to Class 2 green, §3.3* |

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

The required power is set by the spot's detectability against the sunlit background. Contrast
C = E_spot / E_background-in-band, with E_spot = P / A_spot, so **P = C · E_bg · A_spot**. Three
variables drive it — **pattern concentration (A_spot), detector, and any spectral filtering** —
*not* range alone. Using E_bg = 400 W/m² (full visible solar, no filter) or 15 W/m² (10 nm band
at 520 nm), and detection-contrast thresholds C ≈ 0.10 (human eye), 0.05 (camera single frame),
0.01 (camera strobe + frame-difference):

| Nose pattern (at 50 ft / 15.2 m) | Detector | P (mW) | Class |
|---|---|---|---|
| 2 in (51 mm) spread crosshair | human eye, full sun (worst case) | ~82 | **3B** |
| 2 in spread crosshair | camera strobe + difference | ~8.2 | 3B |
| 12 mm concentrated dot | human eye, full sun | ~4.5 | 3R |
| 12 mm dot | camera single frame | ~2.3 | 3R |
| **12 mm dot** | **camera strobe + difference** | **~0.45** | **Class 2** |
| 12 mm dot | camera + 10 nm 520 nm filter | ~0.08 | Class 1 |

**The nose is NOT inherently Class 3B.** Class 3B only appears in the worst-case corner — a
power-*diluted* 2 in spread pattern judged by a *naked human eye* in full direct sun. Vera's
actual requirement is **camera visibility** (Vera is a vision board; the co-located camera is
the observer, and the laser is GPIO-controlled hence strobable). Under that requirement, a
**concentrated ~12 mm green dot detected by strobe + frame-difference needs only ~0.45 mW →
Class 2** (Class 1 with a narrowband detector). Two levers get there:

1. **Concentrate the beam** into a small dot rather than a 2 in spread pattern — the spread
   pattern dilutes the power over ~18× the area (this is the same "different collimation optic"
   of §4.2, now doing double duty).
2. **Let Vera's own camera detect it** (strobe the GPIO-controlled laser, temporally difference
   laser-on − laser-off): pulls the detection threshold from ~10 % (eye) to ~1 %, another order
   of magnitude.

- **Cargo, 5 ft, shaded bay:** trivially Class 2 (or Class 1) — at 1.5 m almost any visible dot
  is plainly detectable; the retired red module was 5 mW Class 3R with margin to spare.

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
- Green's 6.64× advantage compounds with §3.2's concentration + camera-detection levers: the
  nose green dot at ~0.45 mW (Class 2) already assumes a green source; the same detection with
  red would need 6.64× more power, pushing it toward Class 3R/3B. Unifying on green is part of
  what keeps the nose in Class 2.

---

## 4. Results — Determination

**A single green (520 nm) laser *source* CAN serve both installs.** With a concentrated dot and
camera-side detection (§3.2), **both installs are Class 2 (≤ 1 mW)** — the nose is *not*
inherently Class 3B. The two sites differ in only two parameters, and neither forces 3B:

| Parameter | Nose | Cargo | Set by | Shareable source? |
|---|---|---|---|---|
| Spread / divergence | ~3 mrad (12 mm dot @ 50 ft) | ~50 mrad (76 mm @ 5 ft) | **Terminal optic** (collimation / DOE / lens) | **Yes** — same diode, per-location optic |
| Optical power / IEC 60825-1 class | **Class 2** (~0.45 mW, dot + camera strobe-difference) | **Class 2** (≤ 1 mW green) | **Drive current (hardware limit)** | **Yes** — same driver, per-location current limit |
| Class 3B apparatus (key interlock, beam shutter, labeling) | **Not required** at Class 2 | Not required | IEC 60825-1 / 21 CFR 1040 | Neither site |

So the **shared** design is: one 520 nm green laser **diode + collimator + driver board +
MOSFET switch** (Vera already carries exactly one shared driver — Q1 AO3400, R1, R2, J_LASER).
The **per-location** differences are just (1) a terminal optic (spread) and (2) a hardware
current limit (power) — and both current limits sit at **Class 2**.

Class 3B is required **only** in the demanding corner of §3.2 — a power-diluted 2 in *spread
crosshair* that a *human eye* must see in *full direct sun* at 50 ft (~82 mW). That is not
Vera's requirement (camera visibility), so the recommended design does not enter Class 3B and
carries no 3B interlock/shutter obligation.

### 4.1 Answer to Q1 — single green-dot indicator for both?

**Yes — one green-diode design, Class 2 at both sites.** Each site is commissioned with its own
terminal optic (spread) and its own hardware current limit (power), but both limits are ≤ 1 mW
(Class 2). The nose reaches Class 2 by (i) concentrating into a ~12 mm dot instead of a 2 in
spread pattern and (ii) detecting with Vera's own strobed camera + frame-difference (§3.2), not
a naked eye — needing only ~0.45 mW. This **eliminates the Class 3B key-interlock and mechanical
beam shutter entirely**; the `LASER_KEY_IN`/`LASER_IND` lines already on Vera become optional
defense-in-depth rather than a mandatory Class 3B requirement. Class 2 is blink-reflex safe at
both sites — including a Class 2 diode over ground crew in the cargo bay.

**Residual safety note:** if a single physical diode were later sized larger, keep each site's
current limit **hardware-enforced** (fixed sense resistor / current-limited driver, not
firmware) so the ≤ 1 mW Class 2 cap cannot be exceeded by a software fault. At Class 2 the
consequence of a fault is far milder than the Class 3B case, but hardware limiting remains good
practice.

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
2. **Pattern:** a **concentrated dot** at both sites (nose ~12 mm at 50 ft, cargo ~76 mm at
   5 ft), *not* a spread crosshair — concentration is what keeps the nose in Class 2 (§3.2).
   If a crosshair reticle is later wanted for aiming precision, re-check the power budget: a
   spread pattern raises the required power and can push the nose back toward Class 3R/3B.
3. **Terminal optic (per location):** nose ~3 mrad near-collimated (12 mm dot @ 50 ft); cargo
   ~50 mrad diverging-lens (76 mm dot @ 5 ft). Same collimated green source both places.
4. **Optical power / class (per location, HARDWARE-limited):** **Class 2 (≤ 1 mW) at BOTH
   sites.** Nose reaches Class 2 via the concentrated dot + Vera camera strobe-difference
   detection (~0.45 mW). Cargo ≤ 1 mW green. No Class 3B → no key interlock or mechanical
   shutter obligation; the `LASER_KEY_IN`/`LASER_IND` lines on Vera become optional
   defense-in-depth. Keep each cap hardware-enforced (fixed sense resistor / current-limited
   driver), not firmware-only.
5. **Firmware:** strobe the GPIO-controlled laser and temporally difference (laser-on −
   laser-off) in the AM62A7 ISP for daylight spot detection — this is what buys the nose its
   Class 2 margin; budget a laser-sync GPIO/PWM in the Vera firmware WBS (TODO.md §4.6).
6. **Do not source the green diode or either terminal optic** until a real datasheet with a
   manufacturer-stated (or independently computed) mW rating and IEC 60825-1 class is added
   to REFERENCES.md — this extends the existing pending item under REF-IEC-002 and the
   "Do not fabricate or procure against the placeholder" discipline (TODO.md §1.2c).

---

## 6. Open Items / Follow-on

- **Confirm the requirement is camera visibility, not human-at-target visibility.** The Class 2
  result rests on Vera's own camera being the observer (strobe + frame-difference). If a person
  standing at the 50 ft target must see the spot in full direct sun, re-open the class decision
  (that corner needs Class 3R for a dot, up to Class 3B for a spread reticle — §3.2).
- **Camera strobe-difference detection** must be implemented for the nose to hold Class 2 in
  bright sun — a firmware/ISP task (laser-sync GPIO + frame differencing); TODO.md §4.6.
- **Hardware current limit at both sites:** confirm the shared driver enforces the ≤ 1 mW
  Class 2 cap in hardware (fixed sense resistor / current-limited driver), not by firmware.
- **Part sourcing:** 520 nm green diode + per-site collimation/diverging optic; each needs a
  verified datasheet + REFERENCES.md entry before procurement.
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
