# Manufacturer-published XY versus Z (build-axis) mechanical data for fibre- and glass-filled SLS polyamide

Retrieval date for every source: 2026-11-11. EOS web datasheets are rendered on request and print "Status as of 11.11.2026" (the retrieval date). The ALM PA 603-CF sheet also prints "Last changed on 10.11.2026". EOS publishes no separate revision number on these pages. Unit conversions are mine: 1 MPa = 145.04 psi, and 1000 MPa = 145.04 ksi. Ratios are computed from the published values, rounded to 2 decimals. No value has been estimated.

Hosts that were unreachable from this session: advancedlasermaterials.com (proxy 403 and DNS failure; EOS links ALM's own PDFs there), www.alm-llc.com (connection reset), www.windform.com (403 and DNS failure), and sinterit.com (proxy 403). Prodways' materials page loads its content with JavaScript, and I found no datasheet links in it. Those materials therefore stay unverified. For any of them to be checked, the hosts have to be allowed in the session's network settings.

## Which filled SLS powders publish Z data (manufacturer-verified table)

### Takeaway
Only two filled SLS PA12 powders had both XY and Z values that I could read on the manufacturer's own document: EOS PA 3200 GF (glass beads) and ALM PA 603-CF on the EOS P3 NEXT (carbon fibre). EOS publishes separate X, Y and Z values for both. 3D Systems publishes a single, non-directional value for every DuraForm grade. Windform, ALM's own PDFs, Prodways and Sinterit could not be reached, so they are unverified.

### Cited Findings

**Verified table: values read on the manufacturer's document**

| Material (maker) | Filler | Std | Property | X | Y | Z | Z/X | Z/Y |
|---|---|---|---|---|---|---|---|---|
| ALM PA 603-CF on P3 NEXT (EOS PDS) | carbon fibre, 33 % ("33% Carbon-Fiber-Filled Nylon 12"; basis wt/vol not stated) | ISO 527-1/-2, dry | Tensile modulus | 8000 MPa (1160 ksi) | 4200 MPa (609 ksi) | 2900 MPa (421 ksi) | 0.36 | 0.69 |
| | | ISO 527-1/-2 | Tensile strength | 85 MPa (12,330 psi) | 60 MPa (8,700 psi) | 42 MPa (6,090 psi) | 0.49 | 0.70 |
| | | ISO 527-1/-2 | Elongation at break | 3.8 % | 6.1 % | 3.5 % | 0.92 | 0.57 |
| | | ASTM D638, dry | Tensile modulus | 8600 MPa (1247 ksi) | 4200 MPa (609 ksi) | 3000 MPa (435 ksi) | 0.35 | 0.71 |
| | | ASTM D638 | Tensile strength | 85 MPa (12,330 psi) | 60 MPa (8,700 psi) | 37 MPa (5,370 psi) | 0.44 | 0.62 |
| | | ASTM D638 | Elongation at break | 3.5 % | 4.4 % | 3.0 % | 0.86 | 0.68 |
| | | — | Flexural strength / modulus | not published | | | | |
| EOS PA 3200 GF | glass beads, 40 wt % | ISO 527-1/-2, dry | Tensile modulus | 3200 MPa (464 ksi) | 3200 MPa (464 ksi) | 2500 MPa (363 ksi) | 0.78 | 0.78 |
| | | ISO 527-1/-2 | Tensile strength | 51 MPa (7,400 psi) | 51 MPa (7,400 psi) | 47 MPa (6,820 psi) | 0.92 | 0.92 |
| | | ISO 527-1/-2 | Elongation at break | 9 % | 9 % | 5.5 % | 0.61 | 0.61 |
| | | ISO 178 | Flexural modulus | 2900 MPa (421 ksi), X only | — | not published | — | — |
| | | ISO 178 | Flexural strength | 73 MPa (10,590 psi), X only | — | not published | — | — |

Sources: ALM PA 603-CF, [EOS Process Data Sheet "PDS ALM PA 603-CF on P3 NEXT"](https://www.eos.info/polymer-solutions/data-sheets/pds-alm-pa-603-cf), last changed 10.11.2026. PA 3200 GF, [EOS MDS PA 3200 GF](https://www.eos.info/en-us/polymer-solutions/polymer-materials/data-sheets/mds-pa-3200-gf?topdf), status 11.11.2026. The PA 3200 GF sheet states "polyamide 12 powder filled with glass beads (40 wt%)".

**Unfilled EOS contrast materials (manufacturer-verified, ISO 527-1/-2, dry unless stated)**

| Material | Property | X = Y | Z | Z/XY |
|---|---|---|---|---|
| [EOS PA 1101 (PA11)](https://www.eos.info/en-us/polymer-solutions/polymer-materials/data-sheets/mds-pa-1101?topdf) | Tensile modulus | 1650 MPa (239 ksi) | 1650 MPa | 1.00 |
| | Tensile strength | 50 MPa (7,250 psi) | 48 MPa (6,960 psi) | 0.96 |
| | Elongation at break | 30 % | 15 % (P 110 Velocis: 22 % Z; EOS P 770: 12 % Z) | 0.50 |
| [EOS PA 2200 (PA12)](https://www.eos.info/en-us/polymer-solutions/polymer-materials/data-sheets/mds-pa-2200?topdf) | Tensile modulus | 1650 MPa (239 ksi) | 1650 MPa | 1.00 |
| | Tensile strength | 48 MPa (6,960 psi) | 42 MPa (6,090 psi) | 0.88 |
| | Elongation at break | 18 % | 4 % | 0.22 |
| | Flexural modulus (ISO 178) | 1500 MPa (218 ksi), X only | — | — |
| [EOS PA 2241 FR (PA12, halogen FR, unfilled)](https://www.eos.info/en-us/polymer-solutions/polymer-materials/data-sheets/mds-pa-2241-fr?topdf) | Tensile modulus, dry / cond. | 1900 / 1600 MPa (276 / 232 ksi) | 1900 / 1600 MPa | 1.00 / 1.00 |
| | Tensile strength, dry / cond. | 49 / 44 MPa (7,110 / 6,380 psi) | 46 / 41 MPa (6,670 / 5,950 psi) | 0.94 / 0.93 |
| | Strain at tensile strength, dry / cond. | 7 / 11 % | 6 / 6 % | 0.86 / 0.55 |
| | Elongation at break, dry / cond. | 15 / 22 % | 6 / 9 % | 0.40 / 0.41 |

- EOS PA 1102 black publishes ISO 527 tensile rows, but my text extraction did not capture its orientation values, so they are not recorded here. — [EOS MDS PA 1102 black](https://www.eos.info/en-us/polymer-solutions/polymer-materials/data-sheets/mds-pa-1102-black?topdf)

**3D Systems: XY-only, single non-directional values (manufacturer-verified)**
- DuraForm ProX GF (glass-filled; percentage not stated): tensile strength 45 MPa (6,550 psi), tensile modulus 3720 MPa (540 ksi), elongation 2.8 % (D638); flexural strength 60 MPa (8,930 psi), flexural modulus 3120 MPa (450 ksi) (D790). No orientation is given. — [3D Systems DuraForm ProX GF datasheet, 2020-06-10, © 2020](https://www.3dsystems.com/sites/default/files/2020-07/3d-systems-duraform-prox-gf-plastic-sls-datasheet-usen-2020-06-10-web.pdf)
- DuraForm HST Composite (described as "fiber-reinforced", with "anisotropic mechanical properties"; filler percentage not stated): tensile strength 48–51 MPa (7,050–7,350 psi), tensile modulus 5475–5725 MPa (795–831 ksi), elongation 4.5 % (ASTM D638); flexural strength 83–89 MPa (12,000–12,900 psi), flexural modulus 4400–4550 MPa (638–660 ksi) (ASTM D790). Built on a Sinterstation HiQ + HS at 0.1 mm layers. The values are ranges with no orientation stated, and the sheet never says whether the range spans build directions. — [3D Systems DuraForm HST datasheet, 2020-06-11](https://www.3dsystems.com/sites/default/files/2020-07/3d-systems-duraform-hst-datasheet-usen-2020-06-11-web.pdf)
- DuraForm ProX HST ("proprietary mineral-filled composite"): 44 MPa (6,340 psi), 4123 MPa (600 ksi), 4.3 % (D638); flexural 75 MPa, 3430 MPa (D790). No orientation is given. — [3D Systems DuraForm ProX HST datasheet, 2020-06-11](https://www.3dsystems.com/sites/default/files/2020-07/3d-systems-duraForm-prox-hst-sls-datasheet-usen-2020-06-11-web.pdf)
- 3D Systems' SLS selection guide gives single values, all ASTM D638/D790: DuraForm GF 26 MPa / 4068 MPa / 1.4 %, flexural 37 MPa / 3106 MPa; DuraForm PA 43 MPa / 1586 MPa / 14 %; DuraForm ProX PA 47 MPa / 1770 MPa / 22 %; DuraForm ProX AF+ 37 MPa / 4340 MPa / 3 %. A footnote labels only the ProX EX elongation as "XY orientation at 5mm/min". — [3D Systems SLS Material Selection Guide, 2023-02-09](https://www.3dsystems.com/sites/default/files/2023-02/3d-systems-sls-material-selection-guide-usen-2023-02-09-web.pdf)
- I found no DuraForm PA CF datasheet on 3dsystems.com in this pass.

**Unverified: reseller, service bureau or summary sources only**
- ALM PA 640-GSL (PA12 "filled with both hollow glass beads and carbon fibers" per [EOS multipurpose page](https://www.eos.info/polymer-solutions/polymer-materials/multipurpose); percentages not stated). EOS store, XY only: 3816 MPa / 49 MPa / 3 % — [EOS store](https://store.eos.info/products/pa-640-gsl). A search snippet attributes Z values of 33 MPa tensile strength and 1945 MPa modulus (ASTM D638) to a Shapeways page — [Shapeways](https://www.shapeways.com/materials/carbon-reinforced-lightweight-nylon-pa12). I did not open that page. The Z ratios it implies are 0.67 for strength and 0.51 for modulus. Both values are UNVERIFIED; ALM's own PDF (`advancedlasermaterials.com/hubfs/ALM/DataSheets/PA-640-GSL-Data-Sheet.pdf`, linked from EOS) was blocked.
- PA 614-GS (PA12 40 % glass-filled), Protolabs page citing the "supplier data sheet", ASTM D638 at 10 mm/min: E-modulus 3600 ± 400 MPa in both x-y and z (ratio 1.00); tensile strength 46 ± 4 MPa x-y, 42 ± 5 MPa z (ratio 0.91); elongation 5 ± 2 % x-y, 3 ± 2 % z (ratio 0.60). UNVERIFIED. — [Protolabs PA12 40% Glass-Filled](https://www.protolabs.com/services/3d-printing/plastic/nylon/pa12-40-glass-filled/)
- Windform XT 2.0 (PA + carbon fibre): a search summary of the Windform page gives 83.84 MPa (12,200 psi) tensile strength (UNI EN ISO 527-1), and a third-party PDF gives 8930 MPa modulus and 3.8 % elongation. No Z value was found. UNVERIFIED because windform.com was unreachable. — [Windform XT 2.0 page](https://www.windform.com/top-line/windform-xt-2-0/)
- ALM PA 602-CF: a datasheet copy exists on a service bureau's site and was not read. — [Prototek copy](https://prototek.com/wp-content/uploads/2025/03/PA-602-CF-Data-Sheet-2021.pdf)

### Inferences
- For build-axis design, the EOS PA 3200 GF Z values are the best verified glass-bead set: 47 MPa strength (0.92 of XY), 2500 MPa modulus (0.78) and 5.5 % elongation (0.61). They are ISO 527 values, not ASTM.
- For carbon fibre, the PA 603-CF Z strength of 42 MPa (ISO) or 37 MPa (ASTM) is lower than the glass-bead Z strength of 47 MPa, despite an X strength of 85 MPa. Carbon-fibre filling buys in-plane stiffness and strength but almost nothing in Z.

### Gaps
- Windform XT 2.0, SL and GT; ALM's own PDFs for PA 640-GSL, 614-GS, 650-ESD and 602-CF; Prodways PA12-GF and CF; and Sinterit PA12 Smooth and PA11 Onyx could not be read from the manufacturer. Their hosts are blocked in this session, or the page loads its content with JavaScript.
- No manufacturer flexural value in Z was found for any material.
- MJF HP 3D HR PA 12 GB is out of scope (MJF, not SLS), and I did not check it.

## Z/XY ratios and whether carbon fibre is more anisotropic than glass beads

### Takeaway
Yes. On EOS's own sheets, carbon fibre (PA 603-CF) gives Z/X of about 0.36 for modulus and 0.44–0.49 for strength. Glass beads (PA 3200 GF) give 0.78 and 0.92. Unfilled PA12 and PA11 keep their modulus fully in Z (1.00) and lose 4–12 % of strength. In every material, elongation suffers the largest Z loss.

### Cited Findings
- PA 603-CF (CF 33 %), ISO 527: Z/X = 0.36 for modulus, 0.49 for strength and 0.92 for elongation; Z/Y = 0.69, 0.70 and 0.57. — [EOS PDS ALM PA 603-CF](https://www.eos.info/polymer-solutions/data-sheets/pds-alm-pa-603-cf)
- PA 3200 GF (40 wt % glass beads), ISO 527: Z/XY = 0.78 for modulus, 0.92 for strength and 0.61 for elongation. — [EOS MDS PA 3200 GF](https://www.eos.info/en-us/polymer-solutions/polymer-materials/data-sheets/mds-pa-3200-gf?topdf)
- The unfilled EOS powders, ISO 527, keep modulus at 1.00 in Z. Strength ratios are 0.88 (PA 2200), 0.96 (PA 1101) and 0.94 (PA 2241 FR). Elongation ratios are 0.22, 0.50 and 0.40. — EOS MDS [PA 2200](https://www.eos.info/en-us/polymer-solutions/polymer-materials/data-sheets/mds-pa-2200?topdf), [PA 1101](https://www.eos.info/en-us/polymer-solutions/polymer-materials/data-sheets/mds-pa-1101?topdf), [PA 2241 FR](https://www.eos.info/en-us/polymer-solutions/polymer-materials/data-sheets/mds-pa-2241-fr?topdf)
- 3D Systems calls DuraForm HST "anisotropic … just like fiber-filled" injection-molded parts, but publishes no directional numbers. — [DuraForm HST datasheet](https://www.3dsystems.com/sites/default/files/2020-07/3d-systems-duraform-hst-datasheet-usen-2020-06-11-web.pdf)

### Inferences
- Spherical glass beads add no direction of their own. The modest Z loss in PA 3200 GF looks like ordinary interlayer fusion weakness. Fibres lie down in the layer plane, so Z sees an essentially unreinforced, interlayer-limited matrix.
- PA 603-CF has a higher Z elongation ratio (0.92 vs X) because X is fibre-dominated and brittle at 3.8 %. Its Z elongation of 3.5 % is still the lowest absolute figure of any verified material.
- From the unverified figures, PA 640-GSL (Z/XY 0.67 strength, 0.51 modulus) would sit between glass beads and pure carbon fibre. That fits its mixed hollow-glass plus carbon-fibre filler, but it needs the ALM PDF to confirm.

### Gaps
- I verified only one carbon-fibre and one glass-bead powder at the manufacturer, so the comparison is n = 1 each and on the same OEM platform. Windform XT 2.0 data would be the most useful second CF point.
- The datasheets do not say whether Z specimens are standard dumbbells built upright or a reduced geometry.

## X versus Y (recoat direction) differences

### Takeaway
EOS's ALM PA 603-CF sheet is the only manufacturer document I found that shows a large X versus Y split. On the same EOS sheets, every unfilled and glass-bead material lists X equal to Y.

### Cited Findings
- PA 603-CF on P3 NEXT, ISO 527: X 8000 vs Y 4200 MPa modulus (Y/X 0.53); 85 vs 60 MPa strength (Y/X 0.71); 3.8 vs 6.1 % elongation. ASTM D638: 8600 vs 4200 MPa (Y/X 0.49); 85 vs 60 MPa; 3.5 vs 4.4 %. — [EOS PDS ALM PA 603-CF](https://www.eos.info/polymer-solutions/data-sheets/pds-alm-pa-603-cf)
- On EOS's own sheets, PA 3200 GF, PA 2200, PA 1101 and PA 2241 FR all list identical X and Y values. — EOS MDS pages cited above

### Inferences
- The X versus Y split is consistent with fibres aligning along one in-plane direction during spreading, most likely the recoat or roller travel. The in-plane minimum (Y) is therefore a more conservative "XY" value for CF powders than the X headline figure. For PA 603-CF, Z/Y (0.69–0.70) is the ratio to use against a randomly oriented in-plane load.

### Gaps
- The PA 603-CF sheet does not say which machine axis X is, relative to the recoater on the P3 NEXT, so mapping X to the recoat direction is my inference and not stated by the manufacturer.
- No other manufacturer document I could read gives X versus Y values.
