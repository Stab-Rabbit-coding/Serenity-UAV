# Observer Laser Indicator — Single-Source Feasibility & Spread-Angle Analysis

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**AI-assist:** Claude Opus 4.8 (Anthropic) — analysis authoring, 2026-07-05
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0
**Revision:** Rev B (2026-07-06)
**Status:** Analysis — feeds Observer laser BOM decision (TODO.md §1.2c); no part sourced yet.
**Rev A1 correction:** the Rev A conclusion that the nose is inherently Class 3B was
over-conservative (worst-case spread-pattern + naked-eye-in-full-sun). For Observer's actual
camera-visibility requirement with camera strobe-difference detection, **both installs are
Class 2 (≤ 1 mW)** — no Class 3B apparatus. See §3.2.
**Rev A2 addition:** the pattern is **a thin-line crosshair, a grid, or a matrix of dots** (not a bare dot) serving as a projected metrology reference.
— A PB2-I computes object **size and orientation** from ToF range + known crosshair angle + trigonometry (§4.4).
The metrology pattern must be sized (fan angle) for enough camera-pixel coverage; a thin-line crosshair or 5x5 dot matrix stays Class 2.

---

## 1. Problem Statement

The Observer board is installed at two locations that each project a laser aiming/marking
pattern of a different size at a different range (Observer.md "Laser driver"):

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
power-*diluted* 2 in spread pattern judged by a *naked human eye* in full direct sun. Observer's
actual requirement is **camera visibility** (Observer is a vision board; the colocated camera is
the observer, and the laser is GPIO-controlled hence strobable). Under that requirement, a
**concentrated ~12 mm green dot detected by strobe + frame-difference needs only ~0.45 mW →
Class 2** (Class 1 with a narrowband detector). Two levers get there:

1. **Concentrate the beam** into a small dot rather than a 2 in spread pattern — the spread
   pattern dilutes the power over ~18× the area (this is the same "different collimation optic"
   of §4.2, now doing double duty).
2. **Let Observer's own camera detect it** (strobe the GPIO-controlled laser, temporally difference
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
MOSFET switch** (Observer already carries exactly one shared driver — Q1 AO3400, R1, R2, J_LASER).
The **per-location** differences are just (1) a terminal optic (spread) and (2) a hardware
current limit (power) — and both current limits sit at **Class 2**.

Class 3B is required **only** in the demanding corner of §3.2 — a power-diluted 2 in *spread
crosshair* that a *human eye* must see in *full direct sun* at 50 ft (~82 mW). That is not
Observer's requirement (camera visibility), so the recommended design does not enter Class 3B and
carries no 3B interlock/shutter obligation.

### 4.1 Answer to Q1 — single green-dot indicator for both?

**Yes — one green-diode design, Class 2 at both sites.** Each site is commissioned with its own
terminal optic (spread) and its own hardware current limit (power), but both limits are ≤ 1 mW
(Class 2). The nose reaches Class 2 by (i) concentrating into a ~12 mm dot instead of a 2 in
spread pattern and (ii) detecting with Observer's own strobed camera + frame-difference (§3.2), not
a naked eye — needing only ~0.45 mW. This **eliminates the Class 3B key-interlock and mechanical
beam shutter entirely**; the `LASER_KEY_IN`/`LASER_IND` lines already on Observer become optional
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

### 4.3 Pattern selection — dot grid (Rev B, supersedes the crosshair)

The chosen pattern is a **regular dot grid** (an N×N dot-matrix DOE), superseding the Rev-A/A1
bare dot and the Rev-A2 crosshair. Three reasons:

- **Higher size+orientation fidelity** — a grid supports a **homography fit** (§4.4.2) that
  recovers the *full* planar pose (tilt magnitude AND azimuth, **no sign ambiguity** — the
  crosshair's weakness) plus scale, least-squares-averaged over N² dots; dot centroids localise
  to ~0.1 px (better than a line fit).
- **Lower cost** — dot-matrix DOEs are commodity parts (mass-produced for 3D-sensing modules),
  whereas a *custom small-angle crosshair* was the expensive/hard optic.
- **Better detection SNR *and* still Class 2** — dots concentrate power into bright points
  (easier for the strobed camera to detect than a diluted line) yet the total splits across N²
  dots, so no single dot exceeds the 1 mW/7 mm-aperture limit — provided the DOE has **low
  zero-order** (the one spec to insist on; the undiffracted central spot is the class-limiting
  point).

### 4.4 Dot grid as a projected metrology reference (size + orientation)

**Requirement:** the grid must have enough measurable spread + resolvable dots for a PB2-I to
compute a detected object's **size** and **relative orientation** from **ToF range + known grid
angle + trigonometry**. At the **nose** the laser/ToF/camera stay boresighted (~7 mm apart) —
the target at 50 ft is effectively at infinity for a small baseline, so pose comes from pattern
geometry, not stereo. (The **cargo** install instead uses a real stereo baseline for true 3D —
§4.5.)

**4.4.1 Size — the grid is a self-calibrating scale bar.** The grid leaves the projector at a
fixed *total* fan angle θ. At the ToF-measured range R its projected size is `S = 2·R·tan(θ/2)`
(surface normal to axis). ToF supplies R, so an object spanning `obj_px` against a grid spanning
`grid_px` has real size `object_size = (obj_px / grid_px) · S`, averaged over all grid rows/cols.

**4.4.2 Orientation — homography (not foreshortening).** A regular grid imaged on a plane tilted
by φ appears as a **perspective-distorted grid**; fitting a homography **H** to the detected dot
centroids and decomposing it yields the plane normal — **tilt magnitude and azimuth together,
with no sign ambiguity** (the grid's keystone convergence is directional). This is an
over-determined, well-posed CV problem (N² dots) and is far more robust than the crosshair
arm-ratio method it replaces.

**4.4.3 Binding constraint = camera pixel coverage.** The grid must span enough pixels *and*
resolve its dots. At R = 50 ft (15.24 m), 1920-px sensor:

| Nose grid (total fan) | array at 50 ft | dot pitch | pitch (px @40° FOV) |
|---|---|---|---|
| 1.0°, 9×9 | 266 mm (10.5 in) | 33 mm (0.125°) | ~6 px |
| 1.0°, 11×11 | 266 mm (10.5 in) | 27 mm (0.100°) | ~5 px |
| 0.7°, 9×9 | 186 mm (7.3 in) | 23 mm | ~4 px |

**Recommended nose optic: ≈1.0° total-fan, 9×9–11×11 dot grid** (still a low/custom angle, but
dot-matrix DOEs flex more easily on angle than a crosshair). Dots ~30 mm apart at 50 ft resolve
to several px, and 81–121 dots give a strongly over-determined homography → ~1 % size, ~1° tilt
(plus the ±1 % TFmini-S range term, REF-SENSOR-002). Cargo grid: 3° 15×15–20×20 (79 mm array,
4–6 mm pitch) — dense, and see §4.5.

**4.4.4 Power — a dot grid is Class 2 with better SNR.** The total splits across N² bright dots
(each ≈ P/N²), so for camera strobe-difference detection the diode runs at its stable
low-power point (~5–15 mW, §4.1) and **no dot exceeds the 1 mW aperture AEL** — *provided the
DOE zero-order is low* (a good-quality DOE keeps zero-order ≤ ~1–2 %; specify it). Concentrated
dots detect at *higher* SNR than the earlier diluted line, so this is strictly better than the
crosshair on both class margin and detectability. The hardware current limit (iC-WKN APC
set-resistor) still caps the total so a fault cannot reach Class 3B.

### 4.5 Cargo install — TRUE 3D imager (stereo baseline, Rev B)

**Upgrade (user, 2026-07-06):** because the cargo camera and the dot-projector are *remote
heads* off Observer (via `J_CAM`/`J_LASER`), their placement in the cargo bay is free — so
**separate them by a real baseline `b`** and make the cargo unit a genuine structured-light 3D
imager (not just 2.5D profiling).

Depth by triangulation: `Z = f·b/d` (d = disparity, px); depth resolution `ΔZ = Z²·δd/(f·b)`.
At Z = 5 ft (1.5 m), f ≈ 3200 px (a ~33° FOV covering ~3 ft), disparity precision δd ≈ 0.2 px:

| Baseline b | Depth resolution ΔZ @ 5 ft | Nominal disparity |
|---|---|---|
| 25 mm (1.0 in) | 5.6 mm | 53 px |
| 50 mm (2.0 in) | 2.8 mm | 107 px |
| **75 mm (3.0 in)** | **1.9 mm** | 160 px |
| 100 mm (3.9 in) | 1.4 mm | 213 px |

**Recommended: b ≈ 75 mm (3 in)** → **~1.9 mm depth resolution at 5 ft** — a real depth camera
(Kinect-class principle). Design points:

- **Pattern: pseudo-random dot field** at the cargo projector (HOLO/OR pseudo-random or Osela
  RPP), **not** a regular grid — random local neighborhoods make the stereo correspondence
  unambiguous for dense block-matching. (The regular grid of §4.4 is for the nose's single-plane
  pose; dense 3D needs the random field.)
- **ToF** anchors absolute scale and bounds the disparity search.
- **One-time camera↔projector calibration** (relative pose) is required and stored on Observer.
- **Why the *nose* stays boresighted (no baseline):** at 50 ft a practical 75 mm baseline gives
  only ~16 px disparity and ~190 mm depth resolution — useless — so the nose keeps the boresighted
  grid-pose method of §4.4; only the close-range cargo install benefits from a baseline.

Mechanical consequence: the cargo `cargo_fpv_bezel` install must provide **two apertures ~75 mm
apart** (camera head + dot-projector head) rather than a colocated cluster — see
`avionics/kicad/Observer/Observer.md` "Cargo install".

---

## 5. Recommended Design

1. **Source (shared):** one 520 nm green laser diode + integrated collimator, driven by the
   existing Observer shared driver (Q1 AO3400 logic-level N-FET, R1 100 Ω gate, R2 10 kΩ
   pulldown, J_LASER). This retires the separate 650 nm red cargo module (unifies BOM to a
   single diode family).
2. **Pattern:** a **dot grid** at both sites (NOT a bare dot) — supersedes the earlier
   crosshair recommendation per §4.3's Rev B decision (nose is a stereo-baseline TRUE-3D
   imager as of the cargo install, §4.5); the grid's known projected geometry is the
   metrology scale/orientation reference (§4.4). Keep individual dots small so power stays
   Class 2 (§4.4.4); let the *fan angle* carry the pixel budget.
3. **Terminal optic + fan angle (per location, co-designed with the camera FOV):** size the
   fan angle so the crosshair spans **N ≈ 24–48 px** at the design range for ~1–2 % size /
   ~1–2° tilt accuracy (§4.4.3). Nose: **larger than the nominal 2 in — target ≈ 4–8 in at
   50 ft (≈0.38–0.76°)** on a wide lens, or a narrower FOV; a DOE/crossed-cylindrical crosshair
   generator. Cargo: 3 in at 5 ft (≈2.86°) is already ample. Same collimated green source both
   places; the optic sets geometry only.
4. **Optical power / class (per location, HARDWARE-limited):** **Class 2 (≤ 1 mW) at BOTH
   sites.** Nose reaches Class 2 via the thin-line crosshair + Observer camera strobe-difference
   detection (~0.2–0.8 mW, §4.4.4). Cargo ≤ 1 mW green. No Class 3B → no key interlock or
   mechanical shutter obligation; the `LASER_KEY_IN`/`LASER_IND` lines on Observer become optional
   defense-in-depth. Keep each cap hardware-enforced (fixed sense resistor / current-limited
   driver), not firmware-only.
5. **Firmware:** (a) strobe the GPIO-controlled laser and temporally difference (laser-on −
   laser-off) in the AM62A7 ISP for daylight crosshair extraction — this buys the nose its
   Class 2 margin; (b) sub-pixel-fit the extracted crosshair lines and compute object size =
   (obj_px/cross_px)·2R·tan(θ/2) and tilt from arm foreshortening (§4.4), using the boresighted
   TFmini-S range R. Budget a laser-sync GPIO/PWM and the crosshair-metrology routine in the
   Observer firmware WBS (TODO.md §4.6).
6. **Do not source the green diode or either terminal optic** until a real datasheet with a
   manufacturer-stated (or independently computed) mW rating and IEC 60825-1 class is added
   to REFERENCES.md — this extends the existing pending item under REF-IEC-002 and the
   "Do not fabricate or procure against the placeholder" discipline (TODO.md §1.2c).

---

## 6. Open Items / Follow-on

- **Confirm the requirement is camera visibility, not human-at-target visibility.** The Class 2
  result rests on Observer's own camera being the observer (strobe + frame-difference). If a person
  standing at the 50 ft target must see the spot in full direct sun, re-open the class decision
  (that corner needs Class 3R for a dot, up to Class 3B for a spread reticle — §3.2).
- **Camera strobe-difference detection** must be implemented for the nose to hold Class 2 in
  bright sun — a firmware/ISP task (laser-sync GPIO + frame differencing); TODO.md §4.6.
- **Hardware current limit at both sites:** confirm the shared driver enforces the ≤ 1 mW
  Class 2 cap in hardware (fixed sense resistor / current-limited driver), not by firmware.
- **Part sourcing:** 520 nm green diode + per-site collimation/diverging optic; each needs a
  verified datasheet + REFERENCES.md entry before procurement.
- **Nose bore reuse flag:** `bow_sensor_pod.scad` `LASER_BORE_D = 12.5 mm` is sized for the old
  12 mm red module — re-verify against the sourced green module's real dimensions (Observer.md
  "Open — stale bore flag").

---

## 7. Standards Citations

- **[REF-IEC-002]** IEC 60825-1:2014+AMD1:2021 — Safety of Laser Products, Part 1: Equipment
  Classification and Requirements. Class thresholds (Class 1/2/3R/3B) and the Class 3B
  requirements for interlock, emission indicator, beam stop, and labeling.
- **[REF-FDA-001]** 21 CFR Part 1040 — Performance Standards for Light-Emitting Products;
  harmonized with IEC 60825-1 for US emission limits.
- **[REF-SENSOR-002]** Benewake TFmini-S (ToF sensor colocated with the laser; unchanged).

---

## 8. References

- CIE 1931 photopic luminous-efficiency function V(λ) — standard tabulated values.
- `avionics/kicad/Observer/Observer.md` — "Laser driver — location-specific population", "Open — stale bore
  flag".
- `docs/POWER_DISTRIBUTION.md` §3.2.1 — Observer laser electrical load (nose Class 3B burst).

---

*© 2026 Steve Griffing, PE(CSE), CISSP-ISSEP, CPP — CC BY-SA 4.0*

---

## Appendix A — Supplier Shortlist & Parts Families (0.5 in / 12.7 mm max mount)

Notes: the Observer installations cannot accept optics with a mounting diameter larger than 0.5 in (12.7 mm). Prefer unmounted or small-height cylindrical lenses (H ≤ 12 mm) or small-form Powell/line-generator optics. The following vendors and part families are vetted starting points; I will fetch product pages and populate SKUs/URLs/pricing below.

- **Thorlabs** — Plano-concave cylindrical lenses (LK series, various f), mounted round cylindrical lenses (e.g. LK1419RM etc. — *note many mounted parts are 1" and therefore too large; prefer unmounted LK items with H ≤ 12 mm*). Thorlabs also supports custom optics requests. Product pages: <https://www.thorlabs.com/cylindrical-lenses> and <https://www.thorlabs.com/item/LK4326-C>

Thorlabs short-list (catalog candidates fitting ≤ 12.7 mm height where noted):

- `LK1395L1-B` — f = -3.91 mm, H = 4.0 mm, L = 6.0 mm, Price ≈ $71.17, Available (Thorlabs)
- `LK1597L2-B` — f = -4.01 mm, H = 4.0 mm, L = 8.0 mm, Price ≈ $79.77
- `LK1523L1-B` — f = -5.79 mm, H = 4.0 mm, L = 6.0 mm, Price ≈ $71.17
- `LK1426L1-B` — f = -24.88 mm, H = 12.0 mm, L = 12.0 mm, Price ≈ $[see site]
- `LK4326-C` — f = -25.0 mm, UV fused silica, H = 15.0 mm (exceeds 12.7 mm — too tall for our mount)

Notes: many Thorlabs focal lengths near the requested ranges (f ≈ 115 mm or 229 mm) are available only in taller heights or mounted 1" variants; for those focal lengths a custom order or unmounted large-diameter lens with a custom small cell is likely required. I'll continue to Edmund Optics next to find Powell and small cylindrical options.
- **Edmund Optics** — Cylindrical lenses and Powell (line-generator) optics; broad focal-length ranges and small-format parts suitable for compact mounts. Start at <https://www.edmundoptics.com> and search "cylindrical lens" / "Powell lens".
- **OptoSigma** — Cylindrical lenses and custom optics (small-form factors available). <https://www.optosigma.com/en>
- **Newport (MKS/Thorlabs/Exoptic resellers)** — cylindrical/line optics catalog; good for alternate sourcing.
- **Resellers / stock optics** — MeetOptics, StockLens, Edmund/Thorlabs distributors — useful when a small, off-the-shelf SKU is needed quickly.

### DOE / Diffractive Suppliers (initial findings)

- **HOLO/OR (Holo-Or)** — Manufacturer of DOEs and diffractive beam shapers.
  Site: <https://www.holoor.co.il/>. Catalogs a wide family of standard DOEs (beam splitters,
  line generators, multispot, homogenizers) and offers custom DOE design + fabrication.
  Small-aperture DOEs (sub-12.7 mm) are possible but typically quoted as custom parts — request
  a quote and spec sheet for clear aperture, substrate (fused silica), and diffraction
  efficiency. Contact/phone on site: +972-89-409687. Lead time and pricing: quote-required.

- **Holo/Or notes:** standard product pages emphasize custom capability for multispot and line-shaping DOEs. For our 0.5 in (12.7 mm) mounting constraint request a "mini" DOE or an unmounted element specified for 520 nm with a CA ≤ 12.7 mm and AR coating for green. Expect commercial quotes rather than catalog SKU pricing.

- **Other DOE houses to query (next):** Holoeye (Germany), RPC Photonics (US), Jenoptik (DE), Edmund Optics (DOE catalog), and small custom houses (e.g., SUSS MicroOptics partners). Many DOE suppliers run quote-based sales for apertures below common catalog sizes; include a request for blank substrate + pattern vs. mounted cell pricing.

I will now query each vendor (Thorlabs, Edmund Optics, OptoSigma, Newport/stock resellers) and record candidate SKUs for both plano-concave cylindrical lenses and Powell/line-generator optics that meet the 0.5 in mounting constraint.

Also include in search: dot-matrix grids / diffractive dot-array elements (DOE) and small microlens arrays as alternate line/point-generation approaches. Search terms: "dot matrix grid", "diffractive dot array", "DOE dot array", "microlens array", "dot-matrix grating". Filter results for clear aperture ≤ 12.7 mm when possible.
