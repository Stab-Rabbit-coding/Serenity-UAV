# Thin-wall fluoropolymer 10 AWG and 8 AWG feed wire (AS22759 / M22759 and Raychem equivalents)

**Read this first: how much of this has been checked.** In this session the network policy blocked direct fetches of
www.glenair.com and docs.rs-online.com (WebFetch "ENOTFOUND"; curl "CONNECT tunnel failed, response 403"; proxy
log `connect_rejected` for www.glenair.com:443). I followed the instruction to stop trying further hosts. So I did
**not open any specification or datasheet PDF myself.** Every figure below comes from web-search result text that
quotes the linked page, often a verbatim table row, but I did not open the page and read it. Under the project rule
("only record figures read on a specification or manufacturer datasheet"), **every figure here is UNVERIFIED** until
someone opens the URL and checks it. The status column marks:
- **U-mfr**: the snippet quotes a manufacturer or licensee table (Glenair, Thermax, TE drawing).
- **U-dist**: the snippet quotes a distributor page.

To verify, allow www.glenair.com, docs.rs-online.com, www.mouser.com and media.iewc.com in the session network
settings, then re-read the URLs listed here.

Project load context (from the assignment, not re-derived here): about 25 V DC; 33–37 A sustained and 57 A peak per
conductor; four conductors in a 0.64 in (16.3 mm) ID carbon spar; 140° twist per tilt cycle; abrasive edges nearby.
The current silicone 10 AWG assumption is 0.217 in (5.5 mm) OD.

## Q1. Which M22759 slash sheets are available in 10 AWG and 8 AWG, with OD, weight, plating and temperature?

### Takeaway
The normal-weight ETFE and XL-ETFE sheets that cover 10 AWG and 8 AWG are /16 (ETFE, tin, 150 °C), /34 (XL-ETFE,
tin, 150 °C), /41 (XL-ETFE, nickel, 200 °C) and /43 (XL-ETFE, silver, 200 °C). PTFE /11 (silver) and /12 (nickel,
260 °C) also cover 10 AWG. At 10 AWG they all use 37 x 26 stranding, at about 0.13–0.14 in (3.3–3.6 mm) OD and about
32–35 lbm/1000 ft. At 8 AWG they use 133 x 29 stranding, at about 0.195–0.20 in (4.95–5.1 mm) OD and about
60–65 lbm/1000 ft. In what I found, the thin-wall and lightweight sheets go no larger than 10 AWG (/18) or 12 AWG
(/32, /33, /44), and /35 lists only 20–26 AWG.

### Product table (all figures UNVERIFIED; see the note at the top)

| Product / part no. | Mfr (domicile) | AWG | Stranding, plating | Insulation | Nominal OD in (mm) | Temp | V | Weight lbm/1000 ft (kg/km) | Price | Status | URL |
|---|---|---|---|---|---|---|---|---|---|---|---|
| M22759/16-10-* | Glenair table (USA) | 10 | 37 x 26, tin-plated Cu; conductor 0.106–0.112 in | extruded ETFE, normal wall | 0.139 ± 0.003 (3.53 ± 0.08) | 150 °C | 600 V | 35.1 max (52.2) | – | U-mfr | https://www.glenair.com/wire-and-cable/as22759/pdf/m22759-16.pdf |
| M22759/16-10-* | Farnell-hosted datasheet (maker not identified) | 10 | 37 x 26, tin | ETFE | 0.136–0.142 (3.45–3.61) | 150 °C | 600 V | snippet shows "34.0 (50.6)" but the column was garbled | – | U-dist | https://www.farnell.com/datasheets/2576654.pdf |
| M22759/16-10-9 (white) | QPL; Harbour Industries listed at Arrow (Harbour: USA) | 10 | 37 x 26, tin | ETFE | – | 150 °C | 600 V | AWC gives about 33 | Wiremasters: $1.06/ft (qty 1), $1.02/ft (250), $0.97/ft (500) | U-dist | https://www.wiremasters.com/product/wire-and-cable/wire/m22759/m22759-16 ; https://www.arrow.com/en/products/m2275916-10-9/harbour-industries ; https://www.awcwire.com/product/m22759_16-10 |
| M22759/16-8-* | Safsale PD372183 datasheet (maker not identified) | 8 | 133 x 29, tin | ETFE | 0.199 ± 0.003 (5.05 ± 0.08) | 150 °C | 600 V | about 63.5 (94.5) | – | U-dist | https://safsale.com/pdf/PD372183-AN.PDF |
| M22759/16-8-* | rf-microwave.com table | 8 | 133 x 29, tin | ETFE | 0.196–0.202 (4.98–5.13) | 150 °C | 600 V | 63.3 (94.2) | – | U-dist | https://www.rf-microwave.com/resources/products_attachments/5a43870e91ab7.pdf |
| M22759/16-8-9 | Carlisle Interconnect Technologies (USA), via Arrow | 8 | 133 x 29 bunch, tin | ETFE | max 5.13 mm (0.202 in) | – | – | – | – | U-dist | https://www.arrow.com/en/products/m2275916-8-9/carlisle-interconnect-technologies |
| M22759/18-10-* | Thermax table, via fdhaero (Thermax: USA, Carlisle) | 10 | 37/26, tin; conductor 0.110 in (2.79 mm) | thin-wall ETFE | 0.131–0.137 (3.33–3.48) | 150 °C | 600 V | 33.1 (49.3) | – | U-dist (quotes a mfr table) | https://fdhaero.com/item/m22759-18-wire/10-amcfz-3726-id-8745/ |
| M22759/18-10-* | Glenair table | 10 | 37 x 26, tin; conductor 0.106–0.112 in | thin-wall ETFE | 0.134 ± 0.003 (3.40 ± 0.08) | 150 °C | 600 V | 34.1 max (50.7), which conflicts with the Thermax 33.1 | – | U-mfr | https://draft.glenair.com/wire-and-cable/pdf/b/m22759-18.pdf |
| M22759/34-10 | AWC (distributor) | 10 | 37/26, tin | XL-ETFE insulation and jacket | 0.130–0.138 (3.30–3.51) | -55 to 150 °C | 600 V | about 32.4 (48.2) | – | U-dist | https://www.awcwire.com/product/m22759_34-10 |
| M22759/34-8-* | TE Raychem Spec 55 / manufacturer table (TE: domiciled Switzerland, US operations) | 8 | 133 x 29, tin; conductor 0.158–0.173 in; 0.701 Ω/1000 ft | XL-ETFE, normal weight | 0.195 ± 0.008 (4.95 ± 0.20) | 150 °C | 600 V | 60.3 (89.7) | – | U-mfr (the snippet does not name the table's maker) | https://docs.rs-online.com/6cee/0900766b814ddd69.pdf ; https://www.awcwire.com/product/m22759_34-8 |
| 22759/34-8-X | RSCC Aerodefense (USA, Marmon/Berkshire Hathaway) via Nassau | 8 | 133/29, tin; 8.61 mm² | XL-ETFE | 0.195 (4.95) | 150 °C (200 °C short-term per listing title) | 600 V | 61.9 (92.1) | – | U-dist | https://www.nassauelectrical.com/products/rscc-aerodefense-8-awg-sae-as22759-34-normal-weight-wall-600v-150-200c-cross-linked-etfe-cable-22759-34-8-x |
| 55A0811-8 (TE Raychem Spec 55; its own drawing number for an /34-type construction) | TE Connectivity | 8 | 133 x 29, tin | modified XL-ETFE, normal weight | 0.195 ± 0.008 (4.95 ± 0.20) | 150 °C | 600 V | 60.3 max (89.7) | – | U-mfr (TE drawing at Arrow) | https://static6.arrow.com/aropdfconversion/528bdd0133d66083c859cc55780912089daade78/engcd55a0811aa.pdf |
| 55A0111-10-2 / -9 (TE Spec 55, lightweight) | TE Connectivity | 10 | 37 x 26, tin; conductor 0.111 in (2.82 mm) | XL-ETFE, 0.005 in wall per Heilind | 0.128 (3.25); Master Electronics gives 3.4 mm | -65 to 150 °C | 600 V | – | – | U-dist | https://www.heilind.com/ryc55a0111-10-2m.html ; https://www.heilind.com/ryc55a0111-10-9.html |
| 55A0111-8-0 | TE Connectivity | 8 | conductor 0.165 in | XL-ETFE, lightweight | 4.78 mm (0.188 in) | – | – | not found | – | U-dist | https://heilind.com/ryc55a0111-8-0.html |
| M22759/32-10-9 (lightweight /32) | TE Connectivity, via RS UK (marked no longer stocked) | 10 | 37/26, tin | XL-ETFE, lightweight | 3.25 mm (0.128 in) | 150 °C | 600 V | – | – | U-dist; **conflicts** with sea-wire, which lists /32 only for 30–12 AWG | https://uk.rs-online.com/web/p/hook-up-wire/1135779 ; https://www.sea-wire.com/?p=730 |
| M22759/41-10 | AWC / Sea Wire (distributors) | 10 | 37/26, nickel-plated Cu | XL-ETFE | 0.130–0.138 (3.30–3.51) | 200 °C | 600 V | 32.4 (48.2) | – | U-dist | https://www.awcwire.com/product/m22759_41-10 ; https://www.sea-wire.com/mil-w-22759-41/ |
| M22759/41-8 | AWC / Sea Wire / Glenair GS equivalent | 8 | 133/29, nickel (per AS29606) | XL-ETFE | 0.187–0.203 (4.75–5.16) | 200 °C | 600 V | AWC about 60.3; Sea 64.2 (95.5); Glenair GS22759-41-8 67.4 max (100.3) | – | U-dist / U-mfr; sources disagree | https://www.awcwire.com/product/m22759_41-8 ; https://www.glenair.com/wire-and-cable/pdf/mil-star/gs22759-41.pdf |
| M22759/43-10 | AWC / Sea via Nassau | 10 | 37/26, silver-coated Cu | XL-ETFE | max 0.138 (3.51) | 200 °C | 600 V | 32.4 (48.2) | – | U-dist | https://nassaunationalcable.com/products/sea-m22759-43-10-10-awg-37-26-stranded-silver-coated-copper-xl-etfe-600v-200c-aerospace-cable |
| M22759/43-8 | AWC; Glenair GS22759-43-8 (Glenair calls it a "better than QPL" equivalent) | 8 | 133/29, silver-coated Cu | XL-ETFE | AWC max 0.203 (5.16); Glenair 0.195 ± 0.008 (4.95 ± 0.20) | 200 °C | 600 V | AWC about 61.9 (92.1); Glenair 65.0 max (96.7); Glenair 0.658 Ω/1000 ft | – | U-dist / U-mfr | https://www.awcwire.com/mil-spec-wire-and-cable/m22759/m22759-43?page=2 ; https://www.glenair.com/wire-and-cable/pdf/mil-star/gs22759-43.pdf |
| M22759/12-10 | AWC / Standard Wire / Nassau | 10 | 37/26, nickel-plated Cu; conductor 0.109 in | extruded PTFE | 0.135–0.143 (3.43–3.63) | -55 to 260 °C (/11 silver: 200 °C) | 600 V | about 35 (52); AWC notes the spec allows splices | – | U-dist | https://www.awcwire.com/product/m22759_12-10 ; https://nassaunationalcable.com/products/10-awg-37-26-stranded-m22759-12-nickel-plated-copper-thin-wall-extruded-ptfe-600v-hookup-wire |
| M22759/44 (lightweight, silver) | Judd Wire (USA, Sumitomo Electric group, Japan) | 12 is the largest size I found | – | XL-ETFE | 12 AWG: 0.103 in; 14 AWG: 0.085 in | 200 °C | 600 V | 12 AWG: 19.7; 14 AWG: 13.0 | – | U-mfr; no 10 or 8 AWG row found | https://static.datasheets.com/doc/26836536-judd-wire-m22759-33-26-9-ds.pdf |

### Cited Findings
- In the sea-wire tables, /32 (XL-ETFE, tin, -65 to +150 °C, 600 V) is listed for 30–12 AWG and /33 (silver-coated high-strength alloy, 200 °C) for 30–20 AWG. — [Sea Wire /32](https://www.sea-wire.com/?p=730); [Sea Wire /33](https://www.sea-wire.com/mil-w-22759-33/)
- The /35 listings found cover only 20–26 AWG (high-strength silver alloy, XL-ETFE). — [Sea Wire /35](https://www.sea-wire.com/?p=740); [Sycor /35](https://www.sycor.com/products/mil-spec-wire/mil-w-22759/m22759-35.html)
- The /18 tables (Thermax, Glenair) run 26 AWG through 10 AWG, so there is no 8 AWG /18. — [Glenair /18](https://draft.glenair.com/wire-and-cable/pdf/b/m22759-18.pdf); [fdhaero Thermax](https://fdhaero.com/item/m22759-18-wire/10-amcfz-3726-id-8745/)
- NASA NEPP explains the part-number structure and slash-sheet families: /35 and /43 are normal-weight silver 200 °C; /44 is lightweight silver. — [NASA NEPP PN guide](https://nepp.nasa.gov/npsl/wire/22759/22759pn.htm); [NEPP style list](https://nepp.nasa.gov/npsl/wire/22759/22759sty_bottom.htm)
- Only one price was found: M22759/16-10-9 at Wiremasters, $1.06/ft (qty 1), $1.02/ft (250 ft), $0.97/ft (500 ft). — [Wiremasters](https://www.wiremasters.com/product/wire-and-cable/wire/m22759/m22759-16)

### Inferences
- At 10 AWG, every fluoropolymer slash sheet is about 0.128–0.142 in (3.25–3.6 mm) OD, about 36–40 % smaller than
  the 0.217 in silicone assumption. At 8 AWG (about 0.195–0.20 in, 4.95–5.1 mm), the fluoropolymer wire is still
  smaller than 10 AWG silicone. So 8 AWG XL-ETFE gives roughly 1.6x the copper area of 10 AWG at a smaller OD than
  the silicone the project assumes.
- For the four-conductor bundle in a 0.64 in ID spar, I calculated the circle-packing diameter (about 2.414 x d) at
  0.139 in x 2.414 ≈ 0.34 in for 10 AWG and 0.20 in x 2.414 ≈ 0.48 in for 8 AWG. Both fit; the silicone assumption
  gives about 0.52 in. This is my arithmetic on the unverified ODs above.
- Because /34, /41 and /43 differ only in plating and temperature (tin 150 °C, nickel 200 °C, silver 200 °C) at
  essentially the same OD and weight, the tin-plated /34 or /16 is the natural choice at 25 V, unless the
  manufacturer's flex data favours one plating.

### Gaps
- None of the slash-sheet PDFs (DLA ASSIST AS22759/16, /34, /41, /43) was opened. DLA quicksearch was not attempted
  because of the host-block instruction.
- I found no confirmed 10 AWG or 8 AWG rows for /32, /33, /35 or /44. The RS listing of a "M22759/32-10-9" conflicts
  with sea-wire's size range, so check it against the slash sheet.
- I found no M22759/16-8 weight from a manufacturer page, and no prices beyond the one Wiremasters quote.
- Harbour Industries, Judd Wire, Prestolite, Axon' and PIC Wire datasheets for 10 AWG and 8 AWG were not reached.

## Q2. Are there extra-flexible (high strand count) fluoropolymer constructions in 10 AWG and 8 AWG?

### Takeaway
Every AS22759 10 AWG and 8 AWG construction found uses standard concentric or bunch stranding: 37 x 26 at 10 AWG and
133 x 29 at 8 AWG. The one fine-strand fluoropolymer lead found is the TE Raychem 82A0113-10 family, with 665 x 38
strands at 10 AWG, described as modified radiation-cross-linked ETFE. Its DigiKey listing (82A0113-10-9-F874) is
marked discontinued.

### Cited Findings
- 82A0113 drawing (TE, hosted by Mouser): the 10 AWG entry is 665 x 38 stranding, with insulation minimums of 75 %
  elongation and 3500 lbf/in² tensile for 24–10 AWG. — [TE 82A0113 drawing at Mouser](https://www.mouser.com/datasheet/2/418/2/NG_CD_82A0113_F-673225.pdf) (U-mfr)
- DigiKey lists "10 AWG Hook-Up Wire 665/38 White 600V", TE part 82A0113-10-9-F874, as Discontinued. — [DigiKey](https://www.digikey.com.mx/en/products/detail/te-connectivity-aerospace-defense-and-marine/82A0113-10-9-F874/5329769) (U-dist)
- Other 82-series listings describe "Modified Radiation Cross-linked ETFE" insulation, 600 V, and in one listing
  (82A0112-10-9) -65 to 200 °C. The snippet also gave "Cable Type: Spec 80", which is inconsistent with the 82
  prefix and unresolved. — search summary of TE distributor listings, e.g. [Master Electronics 82A0111](https://media.masterelectronics.com/productfiles/mf-ray/ray-82a0111269-12272518.pdf) (U-dist)
- The 10 AWG fine-strand (105-strand) leads found are XLPE, XLPVC or silicone (UL 3321, 1431, 3239), not
  fluoropolymer. — [IEWC UL 3321](https://www.iewc.com/product/3321-slsh-10t105-2)
- One search summary describes a UL 10109 Tefzel lead wire at 10 AWG 37/26, 200 °C, tin or silver. It is not
  high-flex. — [fdhaero UL10109](https://fdhaero.com/item/v-wire-200%c2%bac-tefzel-750-insulation-commercial-wi-2/ul10109-10-3726-ul/)

### Inferences
- A 665 x 38 conductor (38 AWG ≈ 0.004 in strands) is the fluoropolymer counterpart of hobby silicone fine strand
  (1050 x 0.08 mm). If a current 82A variant can still be bought, it is the closest match to a torsion-flex
  requirement. Its OD and weight are not yet known.

### Gaps
- I found no 8 AWG high-strand fluoropolymer product. I found no OD, weight, temperature or price for 82A0113-10.
  The "-F874" suffix meaning is unknown.
- Not searched for lack of tool budget: Axon' (France), PIC Wire (USA), Daburn (USA), Calmont (USA) fine-strand
  ETFE/FEP/PFA "flex lead" products.

## Q3. How does the OD of each compare with fine-strand silicone 10 AWG (assumed 0.217 in / 5.5 mm)?

### Takeaway
Hobby fine-strand silicone 10 AWG is about 5.4–5.5 mm (0.213–0.217 in) OD with a 1.3 mm wall, so the 0.217 in
assumption is consistent with published listings. Fluoropolymer 10 AWG is about 3.3–3.6 mm, and 8 AWG about
4.95–5.1 mm.

### Cited Findings
- Powerwerx table: 10 AWG 1050-strand silicone, finished diameter 5.4 mm (0.213 in), 1.30 mm insulation. — [Powerwerx](https://powerwerx.com/silicone-wire-10-25-red) (U-dist)
- Retail listings give 5.5 mm ± 0.1 mm OD for 1050 x 0.08 mm, -60 to 200 °C, 600 V. — search summary of retailer listings such as [vxb](https://vxb.com/products/10-gauge-silicone-wire-spool-red-and-black-30-ft-f) (U-dist)
- Mueller WI-M-10 (Farnell): 10 AWG 1050/0.08 tinned, "0.197 in (5 mm)" silicone jacket, 45 A. — [Farnell](https://www.farnell.com/datasheets/3895756.pdf) (U-dist)

### Inferences
- OD ratio against 0.217 in silicone: /16-10 at 0.139 in ≈ 0.64; /18-10 at 0.134 in ≈ 0.62; 55A0111-10 at 0.128 in
  ≈ 0.59; /34-8 at 0.195 in ≈ 0.90; /16-8 at 0.199 in ≈ 0.92.

### Gaps
- None.

## Q4. What do the specifications or manufacturers say about repeated flexing or torsion?

### Takeaway
I found no statement in any AS22759 text, or by any manufacturer, that approves these wires for repeated torsion.
One testing lab says AS22759/34 and /87 call up dynamic cut-through and flex-life tests (AS4373 methods). One vendor
guide ranks /33 and /35 (high-strength alloy) as "medium-flex" and names a "/36" as "dynamic/high-flex"; that /36
claim is unconfirmed and should not be relied on. Lectromec advises against single-core conductors in regular-flex
applications, which concerns solid wire, not stranded.

### Cited Findings
- Lectromec: the flex tests come from AS4373. Dynamic cut-through and flex life appear in the product specs for
  AS22759/34 and /87. — [Lectromec](https://lectromec.com/blog/non-standard-standard-part-performance/)
- Sea Wire guide: /32 and /34 for static use; /33 and /35 for medium flex; /36 for dynamic or high-flex use
  (turrets, robotic arms). — [Sea Wire AS22759 families PDF](https://www.sea-wire.com/wp-content/uploads/2026/04/AS22759-Wire-Families-Explained-When-to-Use-32%5EJ-33%5EJ-34%5EJ-35%5EJ-and-36-.pdf) (U-dist). A separate search for AS22759/36 at 10 AWG returned nothing, so this is unconfirmed.
- Lectromec: single-core conductors should not be used where flexing is regular, because of conductor fatigue. — [Lectromec EWIS](https://lectromec.com/blog/what-is-an-ewis-qualified-wire/)
- M22759/16 is marketed for "enhanced mechanical toughness". — search summary of [fdhaero /16](https://fdhaero.com/?p=3214) (U-dist)

### Inferences
- At 10 AWG and 8 AWG, the high-strength-alloy sheets (/33, /35) that the vendor guide calls more flex-tolerant do not
  appear to be made. So the AS22759 options at this size are tin, nickel or silver annealed copper with 37 or 133
  strands. For a 140° twist cycle these are much stiffer and less fatigue-tolerant than 1050-strand silicone. Any
  choice needs a project flex or torsion test, or the 665 x 38 82A-type fine-strand lead.
- XL-ETFE's cut-through and abrasion toughness (the reason /34 lists dynamic cut-through) suits the carbon and nylon
  edge exposure better than silicone does. This is qualitative; I found no numeric cut-through values.

### Gaps
- No numeric flex-life cycles, dynamic cut-through force or abrasion values were found for any 10 AWG or 8 AWG part.
  The /34 slash sheet's requirement values were not read.
- Neither the existence nor the construction of AS22759/36 is confirmed.
