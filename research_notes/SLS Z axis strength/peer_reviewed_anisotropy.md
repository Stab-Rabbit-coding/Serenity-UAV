# Peer-reviewed build-orientation anisotropy (XY vs Z) of SLS polyamides, with emphasis on carbon-fibre-filled PA12/PA11

Scope note: these values were read from the full-text PDFs (CC BY, fetched from mdpi-res.com) of five peer-reviewed papers. The table or figure number is given for each value. Values marked "secondary" are another paper's summary of earlier work and were not checked against the original papers. Unit conversion: 1 MPa = 145.04 psi. Every Z/XY ratio below is my own arithmetic on the published means.

Access limits during this research: www.mdpi.com returned HTTP 403 (Akamai "Access Denied"). pmc.ncbi.nlm.nih.gov returned a reCAPTCHA page. link.springer.com PDFs were refused by the proxy (CONNECT 403). WebFetch failed DNS on all three hosts. Only mdpi-res.com PDFs could be downloaded (into `/tmp/claude-0/-home-user-Serenity-UAV/e7935527-d46a-5ced-9dfc-025dd0daf273/scratchpad/dl_z_lit/`). Because of this, the Springer paper s40964-025-01386-w (Progress in Additive Manufacturing, 2025) and the JOANNEUM/Leoben PA-CF anisotropy paper were not read.

## Study table (primary data read in full text)

| # | Study | Material / filler | Machine, key params | Specimen std, n | Orientations | Key measured values (mean ± SD) | Z/XY ratios (computed) |
|---|---|---|---|---|---|---|---|
| 1 | Slager J.J., Green J.T., Levine S.D., Gonzalez R.V. (2025). "The Influence of Print Orientation and Discontinuous Carbon Fiber Content on the Tensile Properties of Selective Laser-Sintered Polyamide 12." *Polymers* 17(15):2028. DOI [10.3390/polym17152028](https://doi.org/10.3390/polym17152028). OA PDF: [mdpi-res](https://mdpi-res.com/d_attachment/polymers/polymers-17-02028/article_deploy/polymers-17-02028.pdf) | Sintratec PA12 (fresh powder) dry-blended with Carbiso M80 recycled milled CF (≤0.08 mm long, 7 µm dia), 0/2.5/5/10 vol% | Custom SLS printer, 5 W 455 nm blue diode, 0.1 mm layers, bed 150–162 °C, 3-pass lasing (speeds Table 1), single-blade double-pass recoat | ASTM D638-14 Type V (modified); "minimum of three" per blend; 3–6 horizontal and 6–12 vertical printed; ADMET eXpert 5603 at ~23 °C | Horizontal = load ∥ recoater; Vertical = load along build (Z) axis | Table 4 (see detail below) | UTS 0.90 (neat) → 0.61 (2.5%) → 0.64 (5%) → 0.04 (10%); E 0.91 → 0.82 → 0.75 → 0.11; failure strain 0.09 → 0.20 → 0.25 → 0.08 |
| 2 | Zárybnická L., Petrů J., Krpec P., Pagáč M. (2022). "Effect of Additives and Print Orientation on the Properties of Laser Sintering-Printed Polyamide 12 Components." *Polymers* 14(6):1172. DOI [10.3390/polym14061172](https://doi.org/10.3390/polym14061172). OA PDF: [mdpi-res](https://mdpi-res.com/d_attachment/polymers/polymers-14-01172/article_deploy/polymers-14-01172.pdf) | EOS PA2200, PA2210 FR, PA3200 GF (38.35 wt% filler by TGA), Alumide; ALM PA 640-GSL ("mix of glass and carbon fibers") | EOS P396 (CO2, 70 W), 0.12 mm layers, EOS default parameters; refresh 50/50 (PA2200), 70/30 (GF, 640-GSL), 100% new (FR, Alumide) (Table 1) | ISO 527-2 dog bones, 10 per orientation; Instron 3345, 1 mm/min | A1, B1 = two in-plane (XY) orientations; G1 = "printing of the samples in the direction of the z-axis" | Table 7: strength and modulus only (no elongation reported) | PA2200 0.90 / 1.00; PA3200GF 1.00 / 0.95; PA640-GSL (GF+CF) 0.82 / 0.84; Alumide 0.97 / 1.00; FR 0.90 / 0.93 (strength / modulus, G1 ÷ mean(A1,B1)) |
| 3 | Baba M.N. (2022). "Flatwise to Upright Build Orientations under Three-Point Bending Test of Nylon 12 (PA12) Additively Manufactured by SLS." *Polymers* 14(5):1026. DOI [10.3390/polym14051026](https://doi.org/10.3390/polym14051026). OA PDF: [mdpi-res](https://mdpi-res.com/d_attachment/polymers/polymers-14-01026/article_deploy/polymers-14-01026.pdf) | Formlabs Nylon 12, 50% refresh | Formlabs Fuse 1, 5 W, 2000 mm/s, 0.1 mm layers, 178.3–178.6 °C | 3-point bend, 80×10×4 mm bars per ISO 178 (abstract says "ISO 173", which appears to be a typo), large-deflection correction per ISO 14125; 7 printed per orientation, 1 outlier excluded per group | Flatwise (XY, 0°), flat-to-upright (45°), upright (ZY, 90°) | Table 1 (see detail below) | Flexural strength 0.29; flexural modulus 0.74 |
| 4 | Pilipović A., Ilinčić P., Tujmer M., Rujnić Havstad M. (2024). "Impact of Part Positioning along Chamber Z-Axis and Processing Parameters in Selective Laser Sintering on Polyamide Properties." *Applied Sciences* 14(3):976. DOI [10.3390/app14030976](https://doi.org/10.3390/app14030976). OA PDF: [mdpi-res](https://mdpi-res.com/d_attachment/applsci/applsci-14-00976/article_deploy/applsci-14-00976.pdf) | PA12 (EOS) | EOS Formiga P100; hatch 21 W at 2500 mm/s; contour 16 W at 1500 mm/s; 168 °C; hatch distance 0.23–0.6 mm; two chamber levels (6–48 mm and 174–216 mm above platform); 3 separate jobs | HRN EN ISO 527:2019; 3 specimens per run; Messphysik Beta 50-5 with video extensometer, 5 mm/min, 23 °C | Orientation 0–60° in 15° steps (described as "orientation in the z axis"; whether the tilt is toward vertical is not defined clearly) | Table 2 (upper level) | Not an XY-vs-Z study. It is the energy-density (hatch distance) and part-height evidence |
| 5 | Heckner T., Seitz M., Raisch S.R., Huelder G., Middendorf P. (2020). "Selective Laser Sintering of PA6: Effect of Powder Recoating on Fibre Orientation." *J. Compos. Sci.* 4(3):108. DOI [10.3390/jcs4030108](https://doi.org/10.3390/jcs4030108). OA PDF: [mdpi-res](https://mdpi-res.com/d_attachment/jcs/jcs-04-00108/article_deploy/jcs-04-00108.pdf) | PA6 + 30 wt% glass beads + 10 wt% glass fibre, dry-blended | Farsoon FS6140GF processing parameters (Table 2), N2 atmosphere; full-factorial DoE on recoat speed, layer thickness and laser power | DIN EN ISO 527-2 1A; Zwick Z050; µCT (GE v\|tome\|x m) | Recoat-direction (X) tensile only, plus CT fibre-orientation tensors | E = 6417–8154 MPa depending on parameters (Table 3); orientation tensor X 0.49–0.58, Y 0.28, Z 0.18 | No Z tensile measured. Fibre fraction aligned with Z is ≈0.18 |

### Detail: Slager et al. 2025, Table 4 (PA12 + milled CF, ASTM D638 Type V)

| CF vol% | Orient. | E, MPa (ksi) | Yield, MPa | UTS, MPa (psi) | Failure strain, % |
|---|---|---|---|---|---|
| 0 | Horizontal | 1832 ± 171 (265.7) | 36.41 ± 2.04 | 51.24 ± 0.75 (7432) | 52.85 ± 2.23 |
| 0 | Vertical (Z) | 1666 ± 286 (241.6) | 33.17 ± 0.69 | 46.07 ± 1.65 (6682) | 4.94 ± 2.46 |
| 2.5 | Horizontal | 2203 ± 65 (319.5) | 37.04 ± 1.12 | 54.29 ± 0.49 (7874) | 13.18 ± 1.06 |
| 2.5 | Vertical (Z) | 1809 ± 165 (262.4) | 24.69 ± 1.24 | 33.13 ± 1.03 (4805) | 2.68 ± 0.38 |
| 5 | Horizontal | 3217 ± 104 (466.6) | 41.26 ± 1.50 | 65.05 ± 0.80 (9435) | 10.49 ± 1.79 |
| 5 | Vertical (Z) | 2412 ± 81 (349.8) | 29.46 ± 1.94 | 41.33 ± 1.36 (5994) | 2.58 ± 0.08 |
| 10 | Horizontal | 7589 (n = 1) (1100.7) | 42.09 | 80.46 (11670) | 5.23 |
| 10 | Vertical (Z) | 854 ± 490 (123.9) | 3.35 ± 2.33 | 3.35 ± 2.33 (486) | 0.44 ± 0.10 |

Table 4 footnote: only one horizontal 10 vol% specimen survived post-processing and strained beyond 0.30%. Most 10 vol% vertical specimens broke along a layer during depowdering (Figure 8) or during grip tightening. 10 vol% CF is about 15 wt%, so this is far below the 30–35 wt% of commercial CF-PA12. The paper reports that blends up to 40 vol% could be spread and sintered but had "significant voids".

### Detail: Baba 2022, Table 1 (Formlabs PA12, 3-point bend)

| Orientation | Flexural strength, MPa (psi) | CoV | Flexural modulus, MPa (ksi) | CoV |
|---|---|---|---|---|
| Flatwise 0° (XY) | 53.9 ± 3.76 (7818 ± 545) | 0.069 | 1541.9 ± 215.1 (223.6) | 0.139 |
| 45° | 21.72 ± 1.58 (3150) | 0.072 | 4577.2 ± 817.7 (663.9) | 0.178 |
| Upright 90° (ZY) | 15.46 ± 1.47 (2242 ± 213) | 0.095 | 1135.3 ± 53.4 (164.7) | 0.047 |

The 45° modulus is anomalously high. The author calls it "surprising". Treat it with caution.

### Detail: Zárybnická et al. 2022, Table 7 (EOS P396, ISO 527-2, n = 10)

| Powder | A1 UTS / E (MPa) | B1 UTS / E (MPa) | G1 (Z) UTS / E (MPa) |
|---|---|---|---|
| PA2200 | 44.4 ± 0.9 / 1387 ± 51 | 43.2 ± 0.4 / 1290 ± 26 | 39.5 ± 2.4 (5729 psi) / 1339 ± 23 |
| PA2210 FR | 34.9 ± 0.2 / 2025 ± 30 | 35.3 ± 0.4 / 1986 ± 60 | 31.4 ± 0.2 / 1867 ± 44 |
| PA3200 GF | 31.9 ± 0.7 / 2363 ± 74 | 32.8 ± 0.5 / 2212 ± 97 | 32.2 ± 1.0 (4670 psi) / 2180 ± 46 |
| Alumide | 33.9 ± 1.1 / 2660 ± 127 | 33.8 ± 0.4 / 2493 ± 127 | 32.9 ± 0.6 / 2571 ± 31 |
| PA 640-GSL (GF+CF) | 30.8 ± 0.9 / 1996 ± 43 | 33.8 ± 1.2 / 2307 ± 37 | 26.5 ± 0.4 (3844 psi) / 1807 ± 19 |

### Secondary flexural data (Baba 2022, Appendix Table A1; originals not read)

| Source as cited | Machine / powder | Std | 0° strength / E (MPa) | 90° strength / E (MPa) | 90/0 ratio |
|---|---|---|---|---|---|
| Ajoku et al. 2006, Proc IMechE B 220:1077 | 3D Systems Vanguard SI, DuraForm PA, 11 W, 0.1 mm, virgin powder | ISO 178 | 60.3 / 1104 | 57.7 / 1054 | 0.96 / 0.95 |
| Marsavina & Stoia 2020, Mater Des Process Commun 2:e112 | EOS Formiga P100, PA2200 | ASTM D5045-99 | 59.2 / 551 | 19.9 / 345 (45°: 46.3 / 433) | 0.34 / 0.63 |
| Schneider & Kumar 2020, Polym Test 86:106357 | 3D Systems Vanguard SI, DuraForm PA, 2.8 W, 0.1 mm | ASTM D790 | 66 / 1166 | 70 / 1281 | 1.06 / 1.10 |

Table A1 does not say whether "90°" means upright (Z) or on-edge in each case.

## What Z/XY strength and modulus ratios are measured for unfilled SLS PA12 and PA11?

### Takeaway
For unfilled PA12 the tensile ratios measured in full text are about 0.89–0.90 for strength and 0.91–1.00 for modulus. Flexural results range much more widely, from about 0.96 down to 0.29, depending on machine and study. I found no peer-reviewed orientation data for unfilled PA11 that I could read.

### Cited Findings
- Neat PA12 on a custom 5 W diode SLS printer (ASTM D638 Type V): vertical/horizontal UTS = 46.07/51.24 MPa (ratio 0.90); modulus 1666/1832 MPa (0.91); yield 33.17/36.41 MPa (0.91) (Table 4). The abstract nonetheless describes neat specimens loaded in either direction as having "similar tensile properties" — [Slager et al. 2025](https://mdpi-res.com/d_attachment/polymers/polymers-17-02028/article_deploy/polymers-17-02028.pdf)
- EOS PA2200 on an EOS P396 (ISO 527-2, n = 10, 50/50 refresh): Z (G1) 39.5 ± 2.4 MPa against 44.4 ± 0.9 and 43.2 ± 0.4 MPa in-plane (ratio 0.89–0.91). Modulus is about the same in all three orientations (1339 against 1387 and 1290 MPa) (Table 7). Scatter in Z (SD 2.4 MPa) was 2.7–6× the in-plane SD — [Zárybnická et al. 2022](https://mdpi-res.com/d_attachment/polymers/polymers-14-01172/article_deploy/polymers-14-01172.pdf)
- In-plane X vs Y (A1 vs B1) for PA2200 differed by only 2.7% in strength and 7% in modulus (Table 7) — [Zárybnická et al. 2022](https://mdpi-res.com/d_attachment/polymers/polymers-14-01172/article_deploy/polymers-14-01172.pdf)
- Formlabs Fuse 1 PA12, three-point bending: upright flexural strength 15.46 MPa against 53.9 MPa flatwise (ratio 0.29); modulus 1135 against 1542 MPa (0.74). Upright had the highest strength CoV (0.095) (Table 1) — [Baba 2022](https://mdpi-res.com/d_attachment/polymers/polymers-14-01026/article_deploy/polymers-14-01026.pdf)
- Secondary (Baba Table A1): DuraForm PA flexural 90°/0° ratio 0.96 (Ajoku 2006) and 1.06 (Schneider & Kumar 2020). PA2200 ratio 0.34 (Marsavina & Stoia 2020, tested to a fracture-type ASTM D5045 standard) — [Baba 2022, Table A1](https://mdpi-res.com/d_attachment/polymers/polymers-14-01026/article_deploy/polymers-14-01026.pdf)
- Secondary: Caulfield et al. 2007 (DTM Sinterstation 2500plus, DuraForm PA) reported higher modulus and tensile strength along x than z — [Baba 2022 intro](https://mdpi-res.com/d_attachment/polymers/polymers-14-01026/article_deploy/polymers-14-01026.pdf)

### Inferences
- For well-processed industrial PA12 (EOS, 3D Systems), tensile Z/XY of about 0.9 for strength and about 1.0 for modulus is the consistent full-text result. The 0.29 flexural ratio comes from a 5 W benchtop machine. It also compares an upright bar that fractured with a flatwise bar that sustained large deflection (Baba notes the flatwise bars underwent large deflections), so it is probably not representative of industrial machines.
- A design value for unfilled PA12 in Z of about 0.85 × XY strength looks conservative for tensile, given the study-to-study spread and the larger Z scatter. This is a judgement call, not a measured value.

### Gaps
- Unfilled PA11 (e.g. DuraForm PA11, EOS PA1101): no peer-reviewed full-text orientation data was read. 3D Systems marketing describes its PA11 as "generally isotropic", but that was seen only in a search snippet.
- The 2025 Springer paper (s40964-025-01386-w) and the Calignano 2021 and Cai 2020 SLS-vs-MJF orientation studies (cited by Slager) were not readable. Springer was blocked and the others are paywalled.

## What ratios for carbon-fibre-filled SLS PA12/PA11 (any fibre fraction), and for glass-filled?

### Takeaway
Carbon fibre makes Z worse. In the only full-text CF-PA12 orientation study, Z/XY UTS fell from 0.90 (neat) to about 0.61–0.64 at 2.5–5 vol% CF, and Z modulus to 0.75–0.82. At 10 vol% the Z specimens were essentially unusable (0.04). A commercial glass+carbon PA12 (ALM PA 640-GSL) gave 0.82/0.84. Glass-bead/fibre PA3200 GF was about isotropic (1.00/0.95). I found no peer-reviewed study of 3D Systems DuraForm PA CF or any other 30–35 wt% CF-PA12.

### Cited Findings
- PA12 + milled CF, vertical/horizontal UTS ratios: 2.5 vol% 33.13/54.29 = 0.61; 5 vol% 41.33/65.05 = 0.64; 10 vol% 3.35/80.46 = 0.04 (horizontal n = 1). Modulus ratios: 0.82, 0.75, 0.11 (Table 4). Horizontal UTS rose by 57% from 0 to 10 vol% while vertical fell — [Slager et al. 2025](https://mdpi-res.com/d_attachment/polymers/polymers-17-02028/article_deploy/polymers-17-02028.pdf)
- Abstract: "fiber-reinforced vertical specimens have significantly reduced consistency and tensile strength as fiber content increased, while the opposite is true for horizontal specimens" — [Slager et al. 2025](https://mdpi-res.com/d_attachment/polymers/polymers-17-02028/article_deploy/polymers-17-02028.pdf)
- ALM PA 640-GSL (described as PA12 with a mix of glass and carbon fibres, 70/30 refresh, EOS P396): Z 26.5 ± 0.4 MPa against 30.8 ± 0.9 and 33.8 ± 1.2 MPa in-plane (ratio 0.78–0.86, 0.82 against the in-plane mean). Modulus 1807 against 1996 and 2307 MPa (0.84). This was the lowest Z strength of all five powders (Table 7) — [Zárybnická et al. 2022](https://mdpi-res.com/d_attachment/polymers/polymers-14-01172/article_deploy/polymers-14-01172.pdf)
- EOS PA3200 GF (38.35 wt% filler by TGA, Table 4): Z 32.2 ± 1.0 MPa against 31.9 and 32.8 MPa (ratio 1.00); modulus 2180 against 2363 and 2212 MPa (0.95) (Table 7) — [Zárybnická et al. 2022](https://mdpi-res.com/d_attachment/polymers/polymers-14-01172/article_deploy/polymers-14-01172.pdf)
- PA6 with 30 wt% glass beads + 10 wt% glass fibre: CT orientation tensor X 0.49–0.58 (recoat direction), Y 0.28, Z 0.18. X-direction modulus ranged 6417–8154 MPa with process parameters (Table 3, Figure 10) — [Heckner et al. 2020](https://mdpi-res.com/d_attachment/jcs/jcs-04-00108/article_deploy/jcs-04-00108.pdf)
- Secondary: Arai et al. 2019 (Opt. Laser Technol. 113:345) found glass-fibre-PBT fibre orientation of 50% in the recoat direction, 35% cross and 15% Z at a 100 µm layer. Tensile strength and modulus were highest in the recoat direction and lowest in the build direction — [Heckner et al. 2020 intro](https://mdpi-res.com/d_attachment/jcs/jcs-04-00108/article_deploy/jcs-04-00108.pdf)
- Search snippet only (not read): a JOANNEUM/Montanuniversität Leoben 2020 study of short-CF polyamide 1212 found 85–95% of fibres in the layer plane, mostly along the roller direction — [JOANNEUM publication page](https://www.joanneum.at/en/publications/systematic-analysis-of-the-mechanical-anisotropy-of-fibre-reinforced-polymer-specimens-produced-by-laser-sintering/)

### Inferences
- With roughly 0.15–0.18 of fibres aligned in Z (Arai, Heckner), CF adds stiffness and strength almost only in-plane. Z strength is then governed by matrix interlayer bonding, now with CF-CF contacts and fibre ends acting as defects. A 30–35 wt% CF-PA12 such as DuraForm PA CF should therefore be expected to show a Z/XY ratio well below neat PA12's 0.9. The two data points (0.61–0.64 at 2.5–5 vol% lab-blend; 0.82 for a commercial GF/CF blend) bracket a plausible 0.5–0.8 range. That range is an extrapolation, not a measurement. A commercial compounded powder made with an optimised process will likely do better than Slager's dry blend on a 5 W diode laser.
- Glass beads, which are isotropic fillers, do not create anisotropy. PA3200 GF behaving isotropically fits this. EOS markets PA 3200 GF as glass-bead-filled, though Zárybnická calls it "glass fiber" (from my background knowledge, not verified here).

### Gaps
- DuraForm PA CF / 33% CF-PA12 peer-reviewed Z data: none found. Search snippets show 3D Systems calls DuraForm PA CF a 33% CF-filled PA12 and that its datasheet said a "complete data set will be available in Q1 2024". The datasheet was not read for this note.
- CF-PA11 (BASF Ultrasint PA11 CF, Sinterit PA11 CF): only vendor datasheet values appeared in search snippets, and they were not read or verified. Vendor datasheets are outside this note's peer-reviewed scope.
- Jansson & Pejryd's study of CF-PA12 (EOS CarbonMide) and Yan et al.'s CF/PA12 SLS work (cited by Slager as ref. 28) were not located or read. Their Z data, if any, is unknown.

## Is elongation in Z much lower (brittle Z failure)? Any fatigue or temperature data by orientation?

### Takeaway
Yes. Z elongation collapses even in neat PA12, to about 9% of the horizontal value (4.9% against 52.9%), and to 0.4–2.7% with CF. Flexural failure moves from ductile flatwise to quasi-brittle upright. I found no fatigue or elevated-temperature data by orientation in the papers read.

### Cited Findings
- Failure strain, vertical against horizontal: neat 4.94 ± 2.46% against 52.85 ± 2.23%; 2.5 vol% CF 2.68 against 13.18%; 5 vol% 2.58 against 10.49%; 10 vol% 0.44 against 5.23% (Table 4). Vertical neat scatter was ±50% of the mean — [Slager et al. 2025](https://mdpi-res.com/d_attachment/polymers/polymers-17-02028/article_deploy/polymers-17-02028.pdf)
- Upright and 45° bend specimens "failed at much" smaller deflections than flatwise (Figure 3). The failure mechanism is "transiting from ductile in the case of flatwise built orientation to quasi-brittle for upright standing oriented specimens". Upright fracture surfaces are relatively smooth (Figure 7) — [Baba 2022](https://mdpi-res.com/d_attachment/polymers/polymers-14-01026/article_deploy/polymers-14-01026.pdf)
- Baba applied a Weibull analysis (Figure 8) to bending strength to capture flaw-controlled failure by orientation — [Baba 2022](https://mdpi-res.com/d_attachment/polymers/polymers-14-01026/article_deploy/polymers-14-01026.pdf)
- Secondary: Caulfield et al. 2007 reported that 0° specimens had less elongation at fracture than 90° specimens over the energy-density range tested. This is the opposite of Slager's trend, and the 0°/90° definitions may differ — [Baba 2022 intro](https://mdpi-res.com/d_attachment/polymers/polymers-14-01026/article_deploy/polymers-14-01026.pdf)
- Secondary: Arai et al. 2019 found glass-fibre-PBT samples built in the coating direction had the highest heat deflection temperature — [Heckner et al. 2020](https://mdpi-res.com/d_attachment/jcs/jcs-04-00108/article_deploy/jcs-04-00108.pdf)

### Inferences
- For design, Z-loaded SLS PA12 (and CF-PA12 especially) should be treated as a low-strain, flaw-controlled material. Thin Z-loaded walls in CF-PA12 are likely to fail at layer interfaces with little warning. Strength knockdown alone is not the right Z margin; use a strain allowable of about 2–3% or less for CF grades.

### Gaps
- No orientation-resolved fatigue (S-N) or elevated-temperature tensile data was found in the readable full texts. Literature I know of on SLS PA12 fatigue by orientation (e.g. van Hooreweder et al.) could not be retrieved or verified here.

## How much does part position in the build, powder refresh ratio or energy density change Z properties?

### Takeaway
Energy density, through hatch distance, has by far the largest effect. In one study, raising PA12 hatch distance from 0.23 to 0.6 mm cut tensile strength from 46 to 8 MPa. The literature cited reports that Z properties are more sensitive to energy input than XY. Chamber height (two levels about 170 mm apart) changed achievable strength only modestly (maximum about 47 MPa at both levels). The papers read did not isolate refresh ratio against orientation.

### Cited Findings
- Formiga P100 PA12, upper chamber level (Table 2): hatch distance 0.23 mm at 0° gave 46.27 ± 0.14 MPa; 0.6 mm at 0° gave 8.16 ± 0.87 MPa; 0.42 mm gave 29–32 MPa at all angles (0° 30.62, 60° 29.07). At fixed hatch distance the orientation angle mattered little — [Pilipović et al. 2024](https://mdpi-res.com/d_attachment/applsci/applsci-14-00976/article_deploy/applsci-14-00976.pdf)
- Abstract: specimens at both chamber levels "had the potential to reach a maximum tensile strength of 47 N/mm2". Level did not influence dimensions. The authors conclude it is "easier to obtain good tensile strength at the upper level" — [Pilipović et al. 2024](https://mdpi-res.com/d_attachment/applsci/applsci-14-00976/article_deploy/applsci-14-00976.pdf)
- Secondary: Caulfield et al. 2007 found 90°-oriented yield strength "exhibit[s] a pronounced dependence on the energy level" compared with 0°, and higher energy density gives more ductile behaviour. Hofland et al. 2017 (PA2200, 50/50 refresh, ISO 527-2) found "the directional dependence of mechanical properties becomes more pronounced with the increase of energy input" — [Baba 2022 intro](https://mdpi-res.com/d_attachment/polymers/polymers-14-01026/article_deploy/polymers-14-01026.pdf)
- In CF-PA12, 10 vol% blends "require the highest energy density for sintering". Vertical builds took 15–25 h against 1–1.5 h for horizontal, which "periodically resulted in reservoir powder degradation", most severely at 10 vol% CF. This was blamed in part for poor vertical layer adhesion. Only fresh powder was used, to remove refresh effects — [Slager et al. 2025](https://mdpi-res.com/d_attachment/polymers/polymers-17-02028/article_deploy/polymers-17-02028.pdf)
- For glass-filled PA6, thinner layers and higher laser power increased recoat-direction stiffness. Thinner layers raised the X orientation tensor by about 7%. Recoat speed had little effect. Volumetric energy densities were 87–236 J/cm³ (Table 3) — [Heckner et al. 2020](https://mdpi-res.com/d_attachment/jcs/jcs-04-00108/article_deploy/jcs-04-00108.pdf)
- Secondary: Lanzl et al. found that varying energy density from 0.04 to 0.06 J/mm² had little influence on fibre-filled part modulus, but very low energy density reduced modulus sharply — [Heckner et al. 2020](https://mdpi-res.com/d_attachment/jcs/jcs-04-00108/article_deploy/jcs-04-00108.pdf)
- Mechanism (Baba): interlayer "grooves" (term from Coy et al.) form because the previous layer partly solidifies before the next is fused. These act as stress risers, so strength anisotropy comes from inter-layer packing and modulus anisotropy from intra-layer packing — [Baba 2022](https://mdpi-res.com/d_attachment/polymers/polymers-14-01026/article_deploy/polymers-14-01026.pdf)
- Mechanism (Slager): CF-CF contact points do not bond during sintering and act "effectively as a void and stress concentrator". There was more fibre pull-out on vertical fracture surfaces. Fibres were aligned along the recoat direction in both orientations — [Slager et al. 2025](https://mdpi-res.com/d_attachment/polymers/polymers-17-02028/article_deploy/polymers-17-02028.pdf)

### Inferences
- Z strength is the property most sensitive to under-sintering. If a CF-PA12 part depends on Z strength, it should be built with the vendor's full-density parameter set. Test coupons should be built in Z in the same job and at the same height. Expect Z scatter 2–6× larger than XY (Zárybnická PA2200 SD; Slager neat vertical strain).
- Tall Z builds mean long exposure of the feed powder to heat. For CF grades this may degrade Z more than refresh ratio alone would suggest (Slager). Few-layer, nested builds reduce this exposure.

### Gaps
- None of the readable papers varied refresh ratio against orientation. Hofland 2017 (Adv. Mater. Sci. Eng. 2017:4953173) is the closest lead and was not read.
- Pilipović's lower-level tensile table and its exact orientation-angle definition were not fully extracted, so I cannot give a quantified level-to-level Z delta.
- No study read reported the energy density (J/mm²) of Slager's diode printer, so its results cannot be mapped to CO2-laser industrial parameters.
