# Fine-strand silicone 10 AWG / 8 AWG ESC feed wire — market survey (2026-11-11)

> **READ FIRST — verification status of every figure in this file.**
> This session's network policy blocked every manufacturer and distributor host (WebFetch/curl: `www.daburn.com`, `americancableassemblies.com`, `assets-cdn.helukabel.com`, `www.datasheets.com`, `www.digikey.com`, `www.mouser.com`, `www.alphawire.com`, `www.remingtonindustries.com`, `www.farnell.com`, `media.iewc.com`, `letronic.de`, `www.lappusa.com`, `www.te.com`, `www.newark.com` all returned DNS-fail or proxy 403).
> **No datasheet PDF was opened and read first-hand.** Every number below came from a WebSearch result summary that quotes the URL shown. This meets the bar of "URL identified" but **not** "datasheet read". Each figure is tagged:
> - **[SE-MFR]**: search excerpt attributed to a manufacturer datasheet or manufacturer page. Probably right, but **re-verify against the PDF before it goes into `bom_revU.json`**.
> - **[SE-DIST]**: search excerpt from a distributor listing. Unverified.
> - **[SELLER]**: seller or marketplace listing with no datasheet. Unverified by definition.
>
> To finish this survey, allow these hosts in the environment's network settings: daburn.com, alphawire.com, helukabel.com, remingtonindustries.com, digikey.com, mouser.com, cicoil.com.

## Which manufacturers publish real datasheets for fine-strand silicone 10 AWG and 8 AWG, and which are US-domiciled?

### Takeaway
Only **Alpha Wire** (US) turned up a manufacturer datasheet that covers silicone hook-up wire at **both 10 AWG and 8 AWG**: 10 AWG 391000 (UL AWM 3212, 105/30 tinned) and 8 AWG 398133 (UL AWM 3212/3213/3214, 133/29 tinned). Alpha's construction is coarse (30/29 AWG strands, about 0.25-0.29 mm), not the 0.08 mm "ultra-flex" RC style. Daburn (US) publishes ultra-flex UL 3135 silicone sheets, but the #2616 table stops at 12 AWG. Remington (US) sells no silicone 10 AWG product that I could confirm. Helukabel (Germany) publishes a UL 3135 sheet (M47021) whose 10/8 AWG rows I could not read. Hobby brands (BNTECHGO) publish only seller-page figures.

### Cited Findings

**Candidate product table** (inches first, mm in parentheses; "—" = not found)

| Mfr (domicile) | Part no. | AWG | Conductor / plating | Stranding | Insulation / wall | Nom. OD | Temp | Voltage | Standard | Weight | Ampacity / flex | Price / source | Source URL | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Alpha Wire (US, NJ) | 391000 (BK005, WH001, WH002 colour suffixes) | 10 | Copper, tinned | 105/30 AWG | Silicone rubber, 0.047 in (1.19 mm) [SE-DIST, RS] | 0.212 in (5.38 mm) [SE-MFR, Farnell-hosted Alpha datasheet]; RS lists 0.210 in; another summary said about 0.204 in (conflict) | 150 °C max [SE-DIST, Mouser] | 600 V [SE-DIST, Mouser] | UL AWM 3212 [SE-DIST, RS/Lapp Tannehill] | — | — | — (RS, Mouser, Lapp Tannehill stock it) | [Farnell-hosted Alpha datasheet](https://www.farnell.com/datasheets/1681218.pdf); [Alpha product page](https://alphawire.com/en/Products/Wire/Hook-Up-Wire/Premium/391000); [RS](https://us.rs-online.com/product/alpha-wire/391000-bk005/70321411/); [Mouser](https://www.mouser.com/ProductDetail/Alpha-Wire/391000-WH002?qs=G7mWZQZ8fQngbjqHI3yBug%3D%3D) | SE only |
| Alpha Wire (US) | 391040 BK005 | 10 | Copper (plating not stated in excerpt) | 105/30 | Silicone rubber | — | — | 10 kV | UL 3239 (high-voltage) | — | — | — (RS) | [RS](https://us.rs-online.com/product/alpha-wire/391040-bk005/70479238/) | SE-DIST; HV wall, likely oversize for the spar |
| Alpha Wire (US) | 398133 (BK005) | 8 | Copper, tinned | 133/29 AWG | Silicone rubber, 0.063 in (1.60 mm) [SE-MFR, Alpha catalog] | 0.295 in (7.49 mm) [SE-MFR, catalog; SE-DIST, Newark] | 150 °C max | 600 V | UL AWM 3212/3213/3214 | — | — | — (Newark, RS UK) | [Alpha hook-up wire catalog](https://www.alphawire.com/en/onlinetools/~/media/files/mastercatalog2011/hookupwire.pdf); [Newark](https://www.newark.com/alpha-wire/398133-bk005/style-3213-8-awg-133-29-tinned/dp/25C2629); [RS UK](https://uk.rs-online.com/web/p/hook-up-wire/7417919?gb=s) | SE only |
| Alpha Wire (US) | 390845 BK001 | 8 | Copper, tinned | 133/29 | Silicone, 0.045 in | 0.259 in (6.58 mm) | — | 15 kV | — | — | — | — (Lapp Tannehill) | [Lapp Tannehill](https://www.lapptannehill.com/390845-bk001-alpha-wire-high-voltage-wire-8-awg-silicone-insulation-133-29-stranded-conductor-tinned-copper-15000v-15kv-black-1000ft) | SE-DIST |
| Daburn (US, NY) | 2616 series | 12 to 26 only; **no 10 or 8** | Copper, tinned | e.g. 12 AWG = 65/30 | Silicone, 0.031 in (0.78 mm) nominal wall, all sizes | 12 AWG: 0.156 in (3.95 mm) | 200 °C | 600 V | UL 3135 | — | — | — | [Daburn 2616 spec sheet](http://www.daburn.com/specs/2616_Spec_Sheet_12-23-2013.pdf); [Daburn product page](https://www.daburn.com/UL-3135-Silicone-Rubber-Wire-2616-Ultra-Flexible.aspx) | SE-MFR; excerpt warned that column alignment was unclear |
| Daburn (US) | 2621 "Daflex" ultra-flex high-strand | 8 / 10 rows **not extracted** | Fine tinned copper | — | Silicone | — | −40 to +150 °C | 600 V | — | — | — | — | [2621 spec sheet (ACA-hosted)](https://americancableassemblies.com/content/db/2621_Spec_Sheet.pdf) | SE-MFR, incomplete |
| Daburn (US) | 2604 DaFlex silicone HV | range 4 to 30 AWG | Fine tinned copper | — | Silicone | — | — | HV | — | — | — | — | [Daburn 2604 sheet](https://www.daburn.com/specs/2604_Specification_Sheet.pdf) | SE-MFR, no 10/8 row data |
| Daburn (US) | 2627 | 8 | Copper | 168/30 | Silicone + **fiberglass braid**, 0.060 in wall | 0.283 in | — | — | UL 3231 | — | — | — | [2627 sheet (ACA-hosted)](https://americancableassemblies.com/content/db/2627_Spec_Sheet_10-01-2014_Rev_A.pdf) | SE-MFR; braided, not a hook-up match |
| Helukabel (Germany) | Single Core UL Style 3135, M47021 | AWG range per sheet; 10/8 rows **not read** | Copper, tinned | — | Silicone | — | −60 to +200 °C | 600 V | UL 758 AWM Style 3135 | — | Bend radius given as multiples of OD | — | [Helukabel M47021 datasheet](https://assets-cdn.helukabel.com/suppliers/Helukabel/documents/db/HELUKABEL_M47021_EN_GB.pdf); [shop](https://shop.helukabel.com/ca-en/helukabel-single-core-ul-style-3135-m47021) | SE-MFR, incomplete |
| BNTECHGO (seller brand; domicile not established) | 10 AWG silicone spools and kits (no formal P/N found) | 10 | Copper, tinned | 1050 × 0.08 mm | Silicone, wall not stated | 0.217 in (5.5 mm) ±0.1 mm | 200 °C (also claims −60 °C) | 600 V | none cited | — | — | various (bntechgo.com, Amazon) | [BNTECHGO 250 ft spool](https://bntechgo.com/bntechgo-10-gauge-silicone-wire-spool-black-250-feet-ultra-flexible-high-temp-200-c-600v-10-awg-silicone-rubber-wire-with-1050-strands-of-tinned-copper-wire-stranded-wire-for-model-battery/); [Amazon](https://www.amazon.com/BNTECHGO-Silicone-Flexible-Strands-Stranded/dp/B01ABOPO2S) | **[SELLER]**, no datasheet |
| Cicoil (US, CA) | 969M101-10-1 / 969M101-8-1 (unshielded hi-flex single conductor) | 10 / 8 | — | "66 base strands" High-Flex construction | Flexx-Sil silicone jacket | 0.33 in / 0.39 in "outside dimension" (fragmentary) | (−104 to +260 °C quoted on a different Cicoil page) | "42K" (meaning unclear) | — | — | 10,000,000 flex cycles nominal (Cicoil generic claim) | — | [distributor-hosted Cicoil catalog](https://www.micro-semiconductor.fr/datasheet/ad-969M101-20-1.pdf); [Cicoil life expectancy note](https://www.cicoil.com/images/pdf/technical-support/Cicoil_Cable_Life_Expectancy.pdf) | SE; excerpt was fragmentary; OD too large for 4 in a 0.64 in tube? See Inferences |

**Domicile and source notes**
- Remington Industries: I found no silicone 10 AWG or 8 AWG product. Remington's 10 AWG category shows only GPT (PVC) and UL3173 products — [Remington 10 AWG category](https://www.remingtonindustries.com/hook-up-wire/hook-up-wire-by-awg/10-awg/). Remington's electronics page calls UL3173 "silicone-insulated" — [Remington electronic wire](https://www.remingtonindustries.com/hook-up-wire/electronics/). Two other sources contradict this: Remington's own clearance SKU lists UL3321/UL3173 as **XLPE** — [Remington clearance](https://www.remingtonindustries.com/clearance-items/10-awg-stranded-hook-up-wire-ul3321-black-xlpe-insulation-1000-ft-spool/) — and Zoro lists 10UL3173STR jacket as XLPE — [Zoro](https://zoro.com/remington-industries-10-awg-gauge-ul3173-stranded-hook-up-wire-600v-0187in-diameter-red-25-ft-length-10ul3173strred25/i/G110059506). Remington's data sheet gives 10UL3173STR as 105/30 stranding, 0.1019 in conductor, 0.187 in (4.75 mm) OD, rated 125 °C — [Remington UL3173 data sheet](https://www.remingtonindustries.com/content/UL3173%20Hook%20Up%20Wire%20Data%20Sheet.pdf); [Remington UL3173 page](https://www.remingtonindustries.com/hook-up-wire/hook-up-wire-10-awg-ul3173-stranded-10-colors-7-spool-sizes-available/). [SE-MFR]
- Other 10 AWG silicone motor-lead references (not ultra-flex hook-up): State Electric SRML 10 AWG, 105 strands, tinned, 150/200 °C, 600 V, OD 0.23 in — [State Electric](https://www.stateelectric.com/products/wire-copper-srml10bk) [SE-DIST]. Nassau 10 AWG SRML SEWF-2 UL 3070, OD 0.227 in, 0.045 in wall — [Nassau National Cable](https://www.nassaunationalcable.com/products/10-awg-srml-sewf-2-ul-3070-high-temperature-motor-lead-wire) [SE-DIST]. Belden 32410 is a glass-braided silicone lead (UL 3075), 0.238 in (6.05 mm) OD — [Belden 32410 techdata](https://catalog.belden.com/techdata/EN/32410_techdata.pdf) [SE-MFR].
- Lapp sells an 8 AWG hook-up wire, 80/0.0161 in, 750 V (P/N 4520095), at DigiKey. Its insulation was not confirmed as silicone — [DigiKey](https://www.digikey.com/en/products/detail/lapp/4520095/25551362).
- Not reached in this session (no results): Calmont, Turnigy, Powerwerx, Striveday, TE Connectivity silicone lines.

### Inferences
- US-domiciled makers with manufacturer datasheets: **Alpha Wire, Daburn, Cicoil, Remington** (Remington has no silicone product in this size). Helukabel is German. BNTECHGO's domicile is not established; it looks like a marketplace brand.
- For both AWGs, **Alpha Wire is the only manufacturer-datasheet, UL-recognised, tinned, silicone option I found**. It is "flexible" (105/30, 133/29), not RC-style "ultra-flexible" (0.08 mm).

### Gaps
- None of the datasheets was opened first-hand (network block). All rows need PDF verification.
- Daburn 2621 and Helukabel M47021 10/8 AWG rows were not extracted.
- Calmont, Turnigy, Powerwerx, Striveday and TE were not searched within the budget.
- No prices were captured from any distributor.

## What outside diameter does each 10 AWG and 8 AWG product actually have (project assumes 0.217 in / 5.5 mm at 10 AWG)?

### Takeaway
At 10 AWG, the assumed 0.217 in (5.5 mm) matches only the **BNTECHGO seller claim** (5.5 mm ±0.1), which has no datasheet behind it. Alpha 391000 is 0.212 in (5.38 mm) per the Farnell-hosted Alpha datasheet, so the assumption is about 0.005 in conservative for that part. Motor-lead silicone 10 AWG runs 0.227-0.23 in. At 8 AWG, Alpha 398133 is 0.295 in (7.49 mm), and the HV Alpha 390845 is 0.259 in (6.58 mm).

### Cited Findings
- Alpha 391000 OD 0.212 in (5.38 mm) — [Farnell-hosted Alpha datasheet](https://www.farnell.com/datasheets/1681218.pdf). RS lists 0.210 in — [RS](https://us.rs-online.com/product/alpha-wire/391000-bk005/70321411/). Mouser lists 5.38 mm — [Mouser](https://www.mouser.com/ProductDetail/Alpha-Wire/391000-WH002?qs=G7mWZQZ8fQngbjqHI3yBug%3D%3D). One search summary also mentioned about 0.204 in with no traceable source: a conflict, left unresolved.
- BNTECHGO 10 AWG OD 5.5 mm ±0.1 mm — [BNTECHGO](https://bntechgo.com/silicone-wire/10-gauge-silicone-wire-1/) [SELLER]
- State Electric SRML 10 AWG 0.23 in — [State Electric](https://www.stateelectric.com/products/wire-copper-srml10bk); Nassau SEWF-2 10 AWG 0.227 in — [Nassau](https://www.nassaunationalcable.com/products/10-awg-srml-sewf-2-ul-3070-high-temperature-motor-lead-wire)
- Alpha 398133 8 AWG OD 7.49 mm, 1.60 mm wall — [Alpha catalog](https://www.alphawire.com/en/onlinetools/~/media/files/mastercatalog2011/hookupwire.pdf); [Newark](https://www.newark.com/alpha-wire/398133-bk005/style-3213-8-awg-133-29-tinned/dp/25C2629). The catalog's 8 AWG 133/29 entries span about 5.13 to 7.49 mm depending on series (search summary).
- Alpha 390845 8 AWG OD 0.259 in (6.58 mm) — [Lapp Tannehill](https://www.lapptannehill.com/390845-bk001-alpha-wire-high-voltage-wire-8-awg-silicone-insulation-133-29-stranded-conductor-tinned-copper-15000v-15kv-black-1000ft)
- Cicoil 969M101-10-1 0.33 in, -8-1 0.39 in (fragmentary excerpt) — [distributor-hosted Cicoil PDF](https://www.micro-semiconductor.fr/datasheet/ad-969M101-20-1.pdf)

### Inferences
- Four-round bundle fit check (my geometry, not sourced): the circumscribing circle of 4 equal circles is d × (1 + √2) ≈ 2.414 d.
  - 10 AWG: 0.217 in → 0.524 in; 0.212 in → 0.512 in; 0.23 in → 0.555 in. All fit inside 0.64 in ID.
  - 8 AWG: Alpha 398133 at 0.295 in → 0.712 in, which **does not fit** the 0.64 in spar. Alpha 390845 at 0.259 in → 0.625 in, essentially zero clearance (0.015 in diametral). The largest OD that fits is 0.64 / 2.414 = 0.265 in (6.7 mm), with zero margin.
  - Cicoil 0.33 in single conductors do not fit four-up.

### Gaps
- No manufacturer-verified OD for any ultra-flex (0.08 mm strand) 10 AWG or 8 AWG silicone product.
- Daburn 2621 and Helukabel 10/8 OD not obtained.

## Which offer tinned copper strands, and at what strand diameters?

### Takeaway
All the silicone candidates found are tinned. Strand diameters: Alpha uses 30 AWG (10 AWG part) and 29 AWG (8 AWG part). Daburn 2616 uses 30 AWG at 12 AWG. BNTECHGO claims 0.08 mm. No 0.05 mm or 0.10 mm construction was confirmed at 10 or 8 AWG from a manufacturer sheet.

### Cited Findings
- Alpha 391000: tinned copper, 105/30 — [RS](https://us.rs-online.com/product/alpha-wire/391000-bk005/70321411/); [Lapp Tannehill](https://www.lapptannehill.com/391000-wh001-alpha-wire-ul-3212-silicone-wire-10-awg-silicone-insulation-105-30-stranded-conductor-tinned-copper-600v-white-1000ft)
- Alpha 398133: tinned, 133/29 — [Newark](https://www.newark.com/alpha-wire/398133-bk005/style-3213-8-awg-133-29-tinned/dp/25C2629)
- Daburn 2616: stranded tinned copper, 12 AWG 65/30 — [Daburn 2616 sheet](http://www.daburn.com/specs/2616_Spec_Sheet_12-23-2013.pdf)
- Daburn 2621: "high strand count of fine tinned copper"; strand size not extracted — [2621 sheet](https://americancableassemblies.com/content/db/2621_Spec_Sheet.pdf)
- BNTECHGO: 1050 × 0.08 mm tinned — [BNTECHGO](https://bntechgo.com/silicone-wire/10-gauge-silicone-wire-1/) [SELLER]
- Helukabel M47021: tinned copper — [Helukabel shop](https://shop.helukabel.com/ca-en/helukabel-single-core-ul-style-3135-m47021)

### Inferences
- Nominal strand sizes (standard AWG table, not from these sources): 30 AWG ≈ 0.0100 in (0.254 mm); 29 AWG ≈ 0.0113 in (0.287 mm). Alpha's strands are therefore about 3× the diameter of the 0.08 mm RC-style wire. That means much stiffer torsion and bend behaviour per conductor.
- Area check: 1050 × 0.08 mm ≈ 5.28 mm² vs 10 AWG nominal 5.26 mm² (my arithmetic). The claimed BNTECHGO construction is consistent with full 10 AWG.

### Gaps
- No manufacturer datasheet found for a 0.05 mm, 0.08 mm or 0.10 mm stranded 10/8 AWG silicone wire. Silver-plated options were not found.

## Do any publish flex or torsion life, abrasion or cut-through data?

### Takeaway
Only **Cicoil** publishes a flex-life number (10 million cycles nominal, generic to its hi-flex line). No source found gives torsion life, abrasion or cut-through data for 10/8 AWG silicone hook-up wire. Helukabel gives bend radius as an OD multiple.

### Cited Findings
- Cicoil: "typical life expectancy: 10 million cycles", the default unless the customer specifies otherwise; High-Flex wire uses 66 base strands vs 19 for "flexible" — [Cicoil Cable Life Expectancy](https://www.cicoil.com/images/pdf/technical-support/Cicoil_Cable_Life_Expectancy.pdf); [Cicoil motor power flex](https://www.cicoil.com/motor-power-cable/flex)
- Helukabel M47021: minimum bend radius stated as multiples of OD (values not extracted) — [Helukabel datasheet](https://assets-cdn.helukabel.com/suppliers/Helukabel/documents/db/HELUKABEL_M47021_EN_GB.pdf)
- No ampacity figure from any silicone-wire manufacturer was captured. Remington publishes general ampacity tables on its hook-up wire resource page (values not extracted) — [Remington hook-up wire resources](https://www.remingtonindustries.com/resources/hook-up-wire/)

### Inferences
- Silicone rubber has low tear and cut-through strength in general (general engineering knowledge, not sourced here). For a twisting bundle inside a carbon tube with cut edges, abrasion protection (sleeve or liner) probably has to come from the design, not from the wire datasheet.
- The Cicoil 10 M-cycle figure is for a bending flex test of its own construction. It does not transfer to a 140° torsion cycle or to other brands.

### Gaps
- No torsion-life data from any manufacturer.
- No abrasion or cut-through data.
- No weight-per-length figures were captured for any product (lbm/ft or g/m). All are needed from the PDFs.
