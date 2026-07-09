Edmund Optics short-note (Powell + cylindrical):

- Powell lenses: Edmund Optics maintains a Powell/line-generator family (see https://www.edmundoptics.com/f/powell-lenses/12245). Powell lenses provide a highly uniform line but catalog minimum fan angles are typically around ~1°; 0.5° is usually a custom-order item.
- Cylindrical lenses: Edmund's catalog includes small-format cylindrical/plano-concave elements; specific SKUs and pricing require a manual site visit because automated scraping is blocked by Cloudflare challenge pages. If needed I can manually capture SKUs and prices by interactively opening Edmund product pages.

Note: automated fetch attempts hit Cloudflare "Just a moment..." interstitials; I recommend manual verification for Edmund Optics SKUs/prices (or I can collect them interactively if you want me to continue). The search link above is a direct starting point.
# Vera Laser Indicator — Single-Source Feasibility & Spread-Angle Analysis

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**AI-assist:** Claude Opus 4.8 (Anthropic) — analysis authoring, 2026-07-05
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Revision:** Rev A2 (2026-07-05)
**Status:** Analysis — feeds Vera laser BOM decision (TODO.md §1.2c); no part sourced yet.
**Rev A1 correction:** the Rev A conclusion that the nose is inherently Class 3B was
over-conservative (worst-case spread-pattern + naked-eye-in-full-sun). For Vera's actual
camera-visibility requirement with camera strobe-difference detection, **both installs are
Class 2 (≤ 1 mW)** — no Class 3B apparatus. See §3.2.
**Rev A2 addition:** the pattern is a **thin-line crosshair** (not a bare dot) serving as a
projected metrology reference — a PB2-I computes object **size and orientation** from ToF
range + known crosshair angle + trigonometry (§4.4). The crosshair must be sized (fan angle)
for enough camera-pixel coverage; a thin-line crosshair stays Class 2.

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
actual requirement is **camera visibility** (Vera is a vision board; the colocated camera is
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

### 4.3 Dot vs. crosshair trade

A **dot** conveys only *position*. A **crosshair** of *known projected angle* also conveys
*scale and orientation* — and §4.4 shows Vera needs exactly that, so **the crosshair (not a
bare dot) is the specified pattern** at both installs. (Rev A/A1 leaned toward a bare dot to
minimize power; §4.4 supersedes that — a *thin*-line crosshair keeps Class 2 anyway, §4.4.4.)

### 4.4 Crosshair as a projected metrology reference (object size + orientation)

**Requirement (added 2026-07-05):** the crosshair must have enough measurable spread for a
PocketBeagle-2-I to compute a detected object's **size** and **relative orientation** from
**ToF range + known laser spread + trigonometry**. The laser+ToF+camera are boresighted
(~7 mm apart on Vera), so all three look at the same patch.

**4.4.1 Size — the crosshair is a self-calibrating scale bar.** The crosshair leaves the laser
at a fixed fan angle θ (a design constant of the DOE/optic). At the ToF-measured range R its
projected physical size is

```text
S = 2 · R · tan(θ/2)          (on a surface normal to the axis)
```

Because the crosshair subtends ~θ at the near-colocated camera *independent of R*, its apparent
angular size alone is not a range cue — **ToF supplies R**, and S = 2R·tan(θ/2) turns the
crosshair into a metric ruler laid on the object. An object spanning `obj_px` against a
crosshair spanning `cross_px` in the same frame then has real size

```text
object_size = (obj_px / cross_px) · S
```

**4.4.2 Orientation — crosshair foreshortening.** On a surface tilted by φ from normal, the
projection stretches by 1/cos φ along the tilt azimuth: the two arms image to different lengths
and a square reticle skews. Measuring the arm-length ratio (= cos φ) recovers the tilt
magnitude; the skew azimuth gives its direction → the surface normal, hence the object's pose
relative to the camera. Caveats: sensitivity is poor near normal incidence (cos φ ≈ 1 is flat),
and the tilt **sign** is ambiguous from a colocated crosshair (the 7 mm baseline gives
negligible parallax at 15 m) — an asymmetric pattern (crosshair + one offset tick, or a 3×3
grid) resolves the sign and improves accuracy if needed.

**4.4.3 The binding constraint is camera angular resolution, not power.** Accuracy scales with
the pixel count `N` across the crosshair, so the crosshair must be sized (fan angle) large
enough — co-designed with the camera lens FOV. At R = 50 ft with a 1920-px-wide sensor:

| Crosshair | 60° FOV | 40° FOV | 30° FOV | 15° FOV |
|---|---|---|---|---|
| 2 in (51 mm) | 5.6 px | 8.8 px | 12 px | 24 px |
| 4 in (102 mm) | 11 px | 18 px | 24 px | 49 px |
| 8 in (203 mm) | 22 px | 35 px | 48 px | 97 px |

Accuracy vs. N (line-endpoint location σ ≈ 0.3 px):

| N (px across) | size error | tilt err @30° | tilt err @10° |
|---|---|---|---|
| 12 | ~3.5 % | ~4° | ~12° |
| 24 | ~1.8 % | ~2° | ~6° |
| 48 | ~0.9 % | ~1° | ~3° |

So the nominal **2 in @ 50 ft crosshair is too small (≈6 px on a wide lens)** for useful
orientation — **the user's instinct for "enough detectable spread" is correct.** For ~1–2 %
size and ~1–2° tilt at moderate angles, target **N ≈ 24–48 px**, i.e. a **larger fan angle
(≈4–8 in at 50 ft, 0.38–0.76°)** on a wide FOV, or a narrower FOV, or a higher-res sensor.
(Size accuracy also inherits the TFmini-S range error, ≈ ±1 % — REF-SENSOR-002.) The cargo
install at 5 ft has ~10× the pixel density, so its 3 in crosshair is already ample.

**4.4.4 Power — a metrology crosshair is still Class 2.** A crosshair concentrates power in
*thin lines*, whose illuminated area is small even when the pattern spans inches, so it is as
power-efficient as a dot. Line power for camera strobe-difference detection (C = 0.01,
E_bg = 400 W/m²), two 51 mm arms:

| Line width | Power | Class |
|---|---|---|
| 0.5 mm | ~0.20 mW | Class 2 |
| 1.0 mm | ~0.41 mW | Class 2 |
| 2.0 mm | ~0.82 mW | Class 2 |

So the metrology crosshair **stays Class 2** provided the lines are thin (≤ ~1 mm at the
target) — no conflict with §4.1. Keep the lines thin and let the *spread* (fan angle), not the
line width, carry the pixel budget.

---

## 5. Recommended Design

1. **Source (shared):** one 520 nm green laser diode + integrated collimator, driven by the
   existing Vera shared driver (Q1 AO3400 logic-level N-FET, R1 100 Ω gate, R2 10 kΩ
   pulldown, J_LASER). This retires the separate 650 nm red cargo module (unifies BOM to a
   single diode family).
2. **Pattern:** a **thin-line crosshair** at both sites (NOT a bare dot) — the crosshair's
   known projected angle is the metrology scale/orientation reference (§4.4). Keep the lines
   thin (≤ ~1 mm at the target) so power stays Class 2 (§4.4.4); let the *fan angle* carry the
   pixel budget.
3. **Terminal optic + fan angle (per location, co-designed with the camera FOV):** size the
   fan angle so the crosshair spans **N ≈ 24–48 px** at the design range for ~1–2 % size /
   ~1–2° tilt accuracy (§4.4.3). Nose: **larger than the nominal 2 in — target ≈ 4–8 in at
   50 ft (≈0.38–0.76°)** on a wide lens, or a narrower FOV; a DOE/crossed-cylindrical crosshair
   generator. Cargo: 3 in at 5 ft (≈2.86°) is already ample. Same collimated green source both
   places; the optic sets geometry only.
4. **Optical power / class (per location, HARDWARE-limited):** **Class 2 (≤ 1 mW) at BOTH
   sites.** Nose reaches Class 2 via the thin-line crosshair + Vera camera strobe-difference
   detection (~0.2–0.8 mW, §4.4.4). Cargo ≤ 1 mW green. No Class 3B → no key interlock or
   mechanical shutter obligation; the `LASER_KEY_IN`/`LASER_IND` lines on Vera become optional
   defense-in-depth. Keep each cap hardware-enforced (fixed sense resistor / current-limited
   driver), not firmware-only.
5. **Firmware:** (a) strobe the GPIO-controlled laser and temporally difference (laser-on −
   laser-off) in the AM62A7 ISP for daylight crosshair extraction — this buys the nose its
   Class 2 margin; (b) sub-pixel-fit the extracted crosshair lines and compute object size =
   (obj_px/cross_px)·2R·tan(θ/2) and tilt from arm foreshortening (§4.4), using the boresighted
   TFmini-S range R. Budget a laser-sync GPIO/PWM and the crosshair-metrology routine in the
   Vera firmware WBS (TODO.md §4.6).
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
- **[REF-SENSOR-002]** Benewake TFmini-S (ToF sensor colocated with the laser; unchanged).

---

## 8. References

- CIE 1931 photopic luminous-efficiency function V(λ) — standard tabulated values.
- `avionics/kicad/Vera.md` — "Laser driver — location-specific population", "Open — stale bore
  flag".
- `docs/POWER_DISTRIBUTION.md` §3.2.1 — Vera laser electrical load (nose Class 3B burst).

---

*© 2026 Steve Griffing, PE(CSE), CISSP-ISSEP, CPP — CC BY 4.0*

---

## Appendix A — Supplier Shortlist & Parts Families (0.5 in / 12.7 mm max mount)

Notes: the Vera installations cannot accept optics with a mounting diameter larger than 0.5 in (12.7 mm). Prefer unmounted or small-height cylindrical lenses (H ≤ 12 mm) or small-form Powell/line-generator optics. The following vendors and part families are vetted starting points; I will fetch product pages and populate SKUs/URLs/pricing below.

- **Thorlabs** — Plano-concave cylindrical lenses (LK series, various f), mounted round cylindrical lenses (e.g. LK1419RM etc. — *note many mounted parts are 1" and therefore too large; prefer unmounted LK items with H ≤ 12 mm*). Thorlabs also supports custom optics requests. Product pages: https://www.thorlabs.com/cylindrical-lenses and https://www.thorlabs.com/item/LK4326-C
- **Thorlabs** — Plano-concave cylindrical lenses (LK series, various f), mounted round cylindrical lenses (e.g. LK1419RM etc. — *note many mounted parts are 1" and therefore too large; prefer unmounted LK items with H ≤ 12 mm*). Thorlabs also supports custom optics requests. Product pages: https://www.thorlabs.com/cylindrical-lenses and https://www.thorlabs.com/item/LK4326-C

Thorlabs short-list (catalog candidates fitting ≤ 12.7 mm height where noted):

- `LK1395L1-B` — f = -3.91 mm, H = 4.0 mm, L = 6.0 mm, Price ≈ $71.17, Available (Thorlabs)
- `LK1597L2-B` — f = -4.01 mm, H = 4.0 mm, L = 8.0 mm, Price ≈ $79.77
- `LK1523L1-B` — f = -5.79 mm, H = 4.0 mm, L = 6.0 mm, Price ≈ $71.17
- `LK1426L1-B` — f = -24.88 mm, H = 12.0 mm, L = 12.0 mm, Price ≈ $[see site]
- `LK4326-C` — f = -25.0 mm, UV fused silica, H = 15.0 mm (exceeds 12.7 mm — too tall for our mount)

Notes: many Thorlabs focal lengths near the requested ranges (f ≈ 115 mm or 229 mm) are available only in taller heights or mounted 1" variants; for those focal lengths a custom order or unmounted large-diameter lens with a custom small cell is likely required. I'll continue to Edmund Optics next to find Powell and small cylindrical options.
- **Edmund Optics** — Cylindrical lenses and Powell (line-generator) optics; broad focal-length ranges and small-format parts suitable for compact mounts. Start at https://www.edmundoptics.com and search "cylindrical lens" / "Powell lens".
- **OptoSigma** — Cylindrical lenses and custom optics (small-form factors available). https://www.optosigma.com/en
- **Newport (MKS/Thorlabs/Exoptic resellers)** — cylindrical/line optics catalog; good for alternate sourcing.
- **Resellers / stock optics** — MeetOptics, StockLens, Edmund/Thorlabs distributors — useful when a small, off-the-shelf SKU is needed quickly.

### DOE / Diffractive Suppliers (initial findings)

- **HOLO/OR (Holo-Or)** — Manufacturer of DOEs and diffractive beam shapers. Site: https://www.holoor.co.il/ (international pages at https://holoor.co.il/). Catalogs a wide family of standard DOEs (beam splitters, line generators, multispot, homogenizers) and offers custom DOE design + fabrication. Their website documents application notes and example product families; small-aperture DOEs (sub-12.7 mm) are possible but typically quoted as custom parts — request a quote and specification sheet for clear aperture, substrate (fused silica), and diffraction efficiency. Contact/phone found on site: +972-89-409687. Lead time and pricing: quote-required.

- **Holo/Or notes:** standard product pages emphasize custom capability for multispot and line-shaping DOEs. For our 0.5 in (12.7 mm) mounting constraint request a "mini" DOE or an unmounted element specified for 520 nm with a CA ≤ 12.7 mm and AR coating for green. Expect commercial quotes rather than catalog SKU pricing.

- **Other DOE houses to query (next):** Holoeye (Germany), RPC Photonics (US), Jenoptik (DE), Edmund Optics (DOE catalog), and small custom houses (e.g., SUSS MicroOptics partners). Many DOE suppliers run quote-based sales for apertures below common catalog sizes; include a request for blank substrate + pattern vs. mounted cell pricing.

I will now query each vendor (Thorlabs, Edmund Optics, OptoSigma, Newport/stock resellers) and record candidate SKUs for both plano-concave cylindrical lenses and Powell/line-generator optics that meet the 0.5 in mounting constraint.

Also include in search: dot-matrix grids / diffractive dot-array elements (DOE) and small microlens arrays as alternate line/point-generation approaches. Search terms: "dot matrix grid", "diffractive dot array", "DOE dot array", "microlens array", "dot-matrix grating". Filter results for clear aperture ≤ 12.7 mm when possible.
