# DuraForm PA CF: build-axis (Z) mechanical data and minimum wall

Research date: 2026-11-11. Every value below was read on the cited page or PDF. Where a source used different units, the conversions in parentheses are mine (1 MPa = 145.04 psi; 1 in = 25.4 mm).

Which hosts could be reached: www.3dsystems.com, www.protolabs.com and www.materialise.com all responded to curl. WebFetch could not resolve www.materialise.com (ENOTFOUND), so I read Materialise pages with curl instead. support.3dsystems.com and quickparts.com were refused by the proxy (403). I did not reach them, and these notes contain nothing from them.

## Q1: Does 3D Systems publish orientation-specific (Z) data for DuraForm PA CF?

### Takeaway
No. All 3D Systems material I found for DuraForm PA CF gives one set of mechanical values with no orientation stated. This covers the material page, both 3DS-30108A datasheet variants (US-EN and A4) and the SLS design guide. The datasheet says "Complete data set will be available in Q1 2024", but no later revision turned up.

### Cited Findings
- **Material page** ([3D Systems DuraForm PA CF](https://www.3dsystems.com/materials/duraform-pa-cf-sls), fetched 2026-11-11):
  - Qualitative claims only: "33% carbon fiber filled nylon 12", "high stiffness, low weight".
  - No numbers, no orientation data and no wall guidance.
  - Links to one datasheet, `2023-11/3d-systems-duraform-pa-cf-datasheet-us-en-2023-10-31-a_web65.pdf`, and to a support.3dsystems.com documentation page, which was blocked.
  - No application notes or case studies are linked.
- **A4 datasheet** ([3D Systems DuraForm PA CF datasheet, A4, doc 3DS-30108A, dated 10-23](https://www.3dsystems.com/sites/default/files/2023-11/3d-systems-duraform-pa-cf-datasheet-us-a4-2023-10-31-a_web52.pdf)). The US-EN variant ([PDF](https://www.3dsystems.com/sites/default/files/2023-11/3d-systems-duraform-pa-cf-datasheet-us-en-2023-10-31-a_web65.pdf)) has the same values and the same 3DS-30108A 10-23 footer. Neither has an X, Y, Z or orientation column. Values:

  | Property | Method | US | Metric |
  |---|---|---|---|
  | Ultimate tensile strength | ASTM D638 Type I | 12,200 psi | 84 MPa |
  | Tensile strength at yield | ASTM D638 Type I | did not yield | did not yield |
  | Tensile modulus | ASTM D638 Type I | 1,230 ksi | 8,500 MPa |
  | Elongation at break | ASTM D638 Type I | 3.8 % | 3.8 % |
  | Flexural strength | ASTM D790 | 19,700 psi | 140 MPa |
  | Flexural modulus | ASTM D790 | 1,010 ksi | 7,000 MPa |
  | Izod notched impact | ASTM D256 | 1 ft-lb/in | 52 J/m |
  | Izod unnotched impact | ASTM D4812 | 9 ft-lb/in | 490 J/m |
  | Shore hardness | ASTM D2240 | 80 D | 80 D |
  | HDT at 66 psi (0.455 MPa) | ASTM D648 | 357 °F | 181 °C |
  | HDT at 264 psi (1.82 MPa) | ASTM D648 | 351 °F | 177 °C |
  | Density | ASTM D792 | 0.04 lb/in³ | 1.11 g/cm³ |
  | 24 h water absorption | ASTM D570 | 0.47 % | 0.47 % |

  The electrical rows are blank. The sheet notes "Complete data set will be available in Q1 2024."
- **Datasheet applications**: wind tunnel model testing, high-performance motorsports parts, small-format short-run tools, jigs and fixtures, and high-impact sports equipment. These are an application list only; the sheet gives no case-study data ([A4 datasheet](https://www.3dsystems.com/sites/default/files/2023-11/3d-systems-duraform-pa-cf-datasheet-us-a4-2023-10-31-a_web52.pdf)).
- **Launch timing**: 3D Systems announced DuraForm PA CF at Formnext 2024 as an SLS 380 material, "planned to ship in December 2024". The press release has no mechanical or orientation data ([3D Systems Formnext 2024 press release](https://www.3dsystems.com/press-releases/3d-systems-empowers-innovation-transforms-industries-new-products-formnext-2024)).
- **Case studies**: a site-restricted search of 3dsystems.com found motorsport case studies for other materials only:
  - Alpine F1 uses DuraForm PA and GF ([Alpine F1 story](https://www.3dsystems.com/customer-stories/3d-printing-productivity-drives-rd-alpine-f1-team)).
  - An Indy manifold uses DuraForm EX ([Indy manifold](https://www.3dsystems.com/learning-center/case-studies/rapid-manufactured-manifold-propels-indy-racecar)).

  None of the PA CF results gave orientation data.
- **Material Finder**: the [3D Systems Material Finder](https://www.3dsystems.com/material-finder) page downloaded (HTTP 200), but its static HTML has no "PA CF" entry. It is probably rendered by script, which I did not run.

### Inferences
- The 3D Systems values are most likely XY, the strong in-plane direction, because they nearly match the X-plane values a bureau publishes for a PA12 carbon-filled grade (see Q2). This is not verified: 3D Systems does not state an orientation.
- Treat 84 MPa / 8,500 MPa / 3.8 % as best-direction values, not as allowables for Z.

### Gaps
- I found no DuraForm PA CF data from 3D Systems for Z or Z45, and no later revision than 3DS-30108A (10-23) with the "complete data set".
- The support.3dsystems.com documentation page (SDS, user manual, possibly a technical data sheet) was blocked by the proxy (403) and is unchecked.
- I found no 3D Systems application note or white paper on PA CF anisotropy.

## Q2: Which service bureaus offer DuraForm PA CF or SLS carbon-filled nylon, and do they publish XY/Z data?

### Takeaway
Protolabs UK/Europe publishes a full X/Y/Z datasheet for "PA12 Carbon Filled Black", an SLS material, dated 14-11-24 in the filename. It does not say whether the material is DuraForm PA CF.

In that sheet, Z tensile strength is 45 MPa against 85 MPa in X (53 %). Z modulus is 2,900 MPa against 8,300 MPa (35 %). Z elongation is 2.2 % against 3.2 %.

Protolabs US does not list a carbon-filled SLS material. The Materialise "PA-CF" is an FDM filament, not SLS.

### Cited Findings
- **Protolabs UK datasheet** ([Protolabs UK "PA12 Carbon Filled Black" Product Specifications PDF, file pa12-carbon-filled-black-en-14_11_24.pdf, © Proto Labs 1999–2024](https://www.protolabs.com/media/0okiybqf/pa12-carbon-filled-black-en-14_11_24.pdf)):
  - Strength and modulus test method: DIN EN ISO 527. This is not the ASTM D638 that 3D Systems uses.
  - Density: 1.2 ± 0.1 g/cm³ (DIN EN ISO 1183-1).
  - HDT at 0.46 MPa: 170 ± 5 °C.
  - Text: "The carbon-fiber filler provides different mechanical properties based on the considered three axis direction."
  - Listed applications include "aerodynamic products for wind tunnel tests".

  | Property | X plane | Y plane | Z plane |
  |---|---|---|---|
  | Tensile strength | 85 ± 5 MPa (12,330 psi) | 55 ± 4 MPa (7,980 psi) | 45 ± 4 MPa (6,530 psi) |
  | Tensile modulus ("E-Module") | 8,300 ± 400 MPa (1,204 ksi) | 3,400 ± 400 MPa (493 ksi) | 2,900 ± 400 MPa (421 ksi) |
  | Elongation at break | 3.2 ± 2 % | 3.0 ± 2 % | 2.2 ± 1 % |

- **Protolabs UK SLS service page** ([Protolabs UK SLS service](https://www.protolabs.com/en-gb/services/3d-printing/selective-laser-sintering/), fetched 2026-11-11):
  - Lists "PA 12 - Carbon Filled Black" with a maximum part size of 490 × 490 × 490 mm.
  - Its property table gives 85 ± 5 MPa / 8,300 ± 400 MPa / 3.2 ± 2 %, footnoted "* X plane".
  - The same page names its SLS equipment as sPro140 and sPro 60 machines, which are 3D Systems platforms. It does not say which machine runs the carbon-filled grade.
- **Protolabs UK SLS materials guide** ([Protolabs UK SLS materials guide](https://www.protolabs.com/en-gb/resources/design-tips/sls-materials/), datePublished 20/06/2025, dateModified 29/08/2025): repeats 85 ± 5 MPa, 8,300 ± 400 MPa, 170 ± 5 °C HDT and 3.2 ± 2 % elongation, with no orientation label.
- **Protolabs US SLS page** ([Protolabs US SLS](https://www.protolabs.com/services/3d-printing/selective-laser-sintering/), fetched 2026-11-11): no carbon-filled material. Its SLS list is PA11 Black, PA12 Black, White and Value, PA12 Mineral-Filled (DuraForm HST), PA12 40 % GF, PP and TPU 70-A. The word "carbon" does not appear on the page.
- **Materialise "PA-CF"** ([Materialise PA-CF](https://www.materialise.com/en/industrial/3d-printing-materials/pa-cf), read via curl):
  - It is "PA-CF for Fused Deposition Modeling", a filament "reinforced with chopped carbon fiber — 35% by weight".
  - Values: 83.5 MPa tensile, 9,460 MPa modulus, 2.4 % elongation, 153 MPa / 11,100 MPa flexural.
  - Minimum wall 1.4 mm, minimum detail 0.6 mm.

  This is not SLS and not DuraForm PA CF, so it is not relevant to the DuraForm Z data question. It is recorded here only to prevent confusion.
- **Materialise materials list**: on [Materialise manufacturing materials](https://www.materialise.com/en/manufacturing/materials), no carbon-filled SLS polyamide appeared. The only "carbon" hits were stainless steel and ABS-ESD7.

### Inferences
- I found no proof that Protolabs UK's "PA12 Carbon Filled Black" is DuraForm PA CF. Unverified.
  - For: the X-plane values (85 MPa / 8,300 MPa) are close to the DuraForm figures (84 MPa / 8,500 MPa), and Protolabs runs sPro machines.
  - Against: the elongation differs (3.2 % vs 3.8 %), the density differs (1.2 vs 1.11 g/cm³), and the test standard differs.
- If this sheet is used as a stand-in for DuraForm PA CF in Z, these knock-downs follow from it:

  | Property | Z as % of X |
  |---|---|
  | Tensile strength | about 53 % (45/85) |
  | Tensile modulus | about 35 % (2,900/8,300) |
  | Elongation | about 69 % (2.2/3.2) |

  Applied to the 3D Systems values, that would give roughly 44 MPa (6,400 psi) Z tensile and roughly 3,000 MPa Z modulus. These are derived estimates, not published DuraForm values.
- In this sheet the Y plane is also much weaker than X (55 vs 85 MPa). Fibre alignment along the recoater direction is a plausible cause, though the sheet does not say so. This means "XY" is not one isotropic in-plane value for CF-filled SLS. In-plane orientation of a part matters as well as Z.

### Gaps
- No bureau states that its carbon-filled SLS grade is DuraForm PA CF.
- No bureau publishes orientation-specific flexural data for carbon-filled SLS PA12.
- Xometry, Shapeways, Quickparts and other bureaus were outside the allowed hosts. quickparts.com was blocked (403); the rest were not attempted.

## Q3: What minimum wall, minimum feature and recommended wall do 3D Systems and the bureaus give for carbon-fibre-filled SLS PA?

### Takeaway
The only carbon-filled-specific figure found is a minimum feature size of 0.031 in (0.80 mm) for PA 12 Carbon Filled Black, from Protolabs UK.

The other figures are generic SLS guidance:

| Source | Figure |
|---|---|
| Protolabs UK, uniform wall | 0.059–0.150 in (1.5–3.8 mm) recommended |
| Protolabs UK, vapour smoothing | 0.059 in (1.5 mm) minimum |
| Protolabs UK, hollowing thick areas | 0.079–0.157 in (2–4 mm) |
| Protolabs US, SLS nylons | 0.030 in (0.762 mm) minimum wall |
| Protolabs design guide | 0.031–0.039 in (0.8–1 mm) minimum wall |
| 3D Systems SLS design guide | keep features above 0.039 in (1 mm) |

3D Systems publishes no minimum wall specific to DuraForm PA CF.

### Cited Findings
- **Protolabs UK SLS service page** ([Protolabs UK SLS service](https://www.protolabs.com/en-gb/services/3d-printing/selective-laser-sintering/)):
  - Minimum feature size at normal resolution: "0.75mm* / 0.80mm** / 1.0mm***", where * is PA 12 White, ** is PA 12 Carbon Filled Black and *** is TPU-88A Black. That gives 0.031 in (0.80 mm) for carbon-filled.
  - Layer thickness: 0.1 mm.
  - "Uniform wall thickness between 1.5mm to 3.8mm, recommended to reduce in-build curl and potential for warping."
  - Thick areas (> 4 mm) must be hollowed "to a wall thickness of 2 to 4 mm".
  - "minimum feature size is 1mm" for text; inset text is limited to features no smaller than 0.5 mm.
  - "For proper smoothing, a minimum wall thickness of 1.5 mm is required" (vapour smoothing).
  - Tolerances: ±0.20 mm plus 0.002 mm/mm. The carbon-filled datasheet adds ±0.3 % for parts over 100 mm ([Protolabs UK PA12 CF datasheet](https://www.protolabs.com/media/0okiybqf/pa12-carbon-filled-black-en-14_11_24.pdf)).
- **Protolabs nylon design guide** ([Protolabs "How to Design for Nylon 3D Printing" (en-gb)](https://www.protolabs.com/en-gb/resources/design-tips/how-to-design-for-nylon-3d-printing/), datePublished 21/07/2020, dateModified 29/12/2023):
  - "The minimum allowable wall thickness is 0.8mm - 1mm in SLS and 0.5mm in MJF". That is 0.031–0.039 in (0.8–1 mm) for SLS.
  - Minimum channel gap: 1 mm (0.039 in).
  - To limit warpage, keep the part "close to the uniform thickness of 3mm", or choose a filled grade such as "Carbon filled Nylon".
  - Hollow thick features to 3–5 mm (0.118–0.197 in).
- **Protolabs US SLS page** ([Protolabs US SLS](https://www.protolabs.com/services/3d-printing/selective-laser-sintering/)):
  - Minimum wall for nylons: 0.030 in (0.762 mm).
  - PP and TPU: 0.04 in (1.01 mm).
  - Recommended uniform thickness: 0.125 in (3.175 mm) for warp stability.

  These figures cover the US materials only, which do not include carbon-filled.
- **3D Systems SLS design guide** ([3D Systems Rapid Manufacturing SLS Design Guide, 2016, PDF created 2016-09-28](https://www.3dsystems.com/sites/default/files/2017-01/3dsystems-sls-designguide-2016.pdf)):
  - Tags section: "Try to keep all features above 1mm thickness" (0.039 in).
  - A pressure-tight tank needs "density >0.98g/cc with a wall thickness >1mm".
  - Clearance between moving parts: 0.2 mm minimum.
  - The guide predates DuraForm PA CF and is not specific to it.
- **Materialise FDM PA-CF** ([Materialise PA-CF](https://www.materialise.com/en/industrial/3d-printing-materials/pa-cf)): minimum wall 1.4 mm (0.055 in). This is for FDM only and does not apply to SLS.

### Inferences
- For a DuraForm PA CF design, the best-supported floors are:
  - minimum feature about 0.031 in (0.80 mm), the carbon-filled-specific Protolabs UK figure;
  - minimum wall about 0.039 in (1.0 mm), the 3D Systems guide and the Protolabs 0.8–1 mm band;
  - recommended structural walls of 0.059–0.150 in (1.5–3.8 mm).

  None of these is a DuraForm PA CF-specific statement from 3D Systems.
- Thin walls built along Z also carry the Z knock-downs from Q2. This is one more reason to stay at or above the recommended range rather than the minimum.

### Gaps
- I found no minimum wall from 3D Systems specific to DuraForm PA CF; the SLS 380 or material support documents may contain one but were not reachable.
- No bureau states a minimum wall, as distinct from a minimum feature, for carbon-filled SLS PA.
