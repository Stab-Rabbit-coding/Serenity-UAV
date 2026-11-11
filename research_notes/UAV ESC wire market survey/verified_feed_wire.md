# Verified 10 AWG / 8 AWG ESC feed-wire candidates: primary-document check (2026-11-11)

**Scope and method.** This file checks the candidates in `silicone_feed_wire.md` and `fluoropolymer_feed_wire.md`. Each value below was read in this session on the manufacturer's own web page or PDF, downloaded with curl and read as text with `pdftotext -layout`. Anything not read on a primary document is marked **UNVERIFIED**. **FLAG** marks a value that differs from the earlier unverified figure.

**Hosts reached:** www.alphawire.com, www.daburn.com, www.glenair.com (the `pdf/mil-star/gs22759-NN.pdf` sheets; the old `as22759/pdf/m22759-16.pdf` path returns a Glenair 403 page), www.cicoil.com and docs.rs-online.com.

**Hosts not reached:**
- www.helukabel.com: every URL 301-redirects to shop.helu.com, which the session proxy rejects.
- www.te.com and www.digikey.com: the site's own (Akamai) "Access Denied" 403. I did not try to get around it.
- www.mouser.com: empty reply / HTTP/2 stream error.
- quicksearch.dla.mil: the root answers, but I did not attempt the slash-sheet document search.

**Units.** Inches first, mm in parentheses. Where a document gives only inches, I converted to mm (×25.4) myself and mark it "(conv.)". kg/km = lbm/1000 ft × 1.488 (my conversion).

## Q1. What do the manufacturer documents actually say for each silicone candidate (Alpha, Daburn, Helukabel, Cicoil)?

### Takeaway
- **Alpha 391000 (10 AWG):** the nominal OD is **0.204 ± 0.004 in (5.18 ± 0.10 mm conv.)**, not the 0.212 in carried earlier (**FLAG**). The conductor is a coarse 105/30 tinned copper. UL AWM 3212, 150 °C, 600 V.
- **Alpha 398133 (8 AWG):** 0.295 ± 0.006 in (7.49 ± 0.15 mm conv.), 133 (7x19)/29 tinned. Its marking is UL AWM **3213** only (**FLAG**: earlier "3212/3213/3214").
- **Daburn #2621 Daflex** is the only true fine-strand tinned silicone found on a primary sheet: 10 AWG = 1092/40 at 0.223 in (5.664 mm) nominal OD; 8 AWG = 665/36 at 0.292 in (7.417 mm).
- **Daburn #2616 (UL 3135)** stops at 12 AWG. **Daburn #2617 (UL 3212)** has a 10 AWG row, 105/30 at 0.207 in (5.30 mm), but no 8 AWG row.
- **Cicoil** 10 AWG is 0.33 in and 8 AWG is 0.39 in. Cicoil does not publish the strand count.
- **Helukabel:** not reached.

### Cited Findings

**Alpha Wire 391000, Premium silicone hook-up, 10 AWG** — [Alpha 391000 product page](https://www.alphawire.com/en/Products/Wire/Hook-Up-Wire/Premium/391000)
- Conductor: "10 (105/30) AWG Tinned Copper", conductor diameter 0.110 in (2.79 mm conv.).
- Insulation: "0.047" Wall, Nom. Silicone Rubber". Diameter: "0.204+/- 0.004" in.
  - **FLAG:** the earlier note had 0.212 in (Farnell copy) and 0.210 in (RS). The 0.204 in that the earlier note dismissed as untraceable is the manufacturer's figure.
- Print: "E163869 RU AWM STYLE 3212 150C 600V"; CSA AWM I A/B 150 °C 600 V FT2; halogen-free.
- Temperature: −40 to 150 °C.
- Bend radius 10× cable diameter; pull tension 82 lbs maximum; conductor DCR 1.15 Ω/1000 ft at 20 °C nominal.
- **Weight per 1000 ft: not stated on the page (UNVERIFIED / gap).**
- No flex-life, torsion or cut-through statement.

**Alpha Wire 398133, Premium silicone hook-up, 8 AWG** — [Alpha 398133 product page](https://www.alphawire.com/en/Products/Wire/Hook-Up-Wire/Premium/398133)
- Conductor: "8 (133(7x19)/29) AWG Tinned Copper", conductor diameter 0.169 in (4.29 mm conv.).
- Insulation: 0.063 in nominal silicone rubber wall. OD "0.295+/- 0.006" in. This matches the earlier 0.295 in, which now has a tolerance.
- Print and specification: "RU AWM STYLE 3213 150C 600V"; CSA AWM I A/B 150 °C 600 V FT2.
  - **FLAG:** the page lists UL AWM 3213 only, not 3212/3213/3214.
- Temperature: −40 to 150 °C.
- Bend radius 10× diameter; pull tension 134 lbs maximum; DCR 0.67 Ω/1000 ft nominal.
- **Weight: not stated (gap).** No flex, torsion or cut-through statement.

**Daburn #2621 Daflex Ultra Flexible High Strand Silicone Rubber Wire, Revision C** — [Daburn 2621 spec sheet](https://www.daburn.com/specs/2621_Spec_Sheet.pdf)
- Description: "Single conductor, high stand count, tinned copper insulated with extruded silicone rubber". The sheet also says it is "designed for continuous flexing applications".
- Rating: −40 °C to +150 °C, 600 V.
- **No UL style is stated (FLAG / note):** this is not a UL 3135 product.
- Rows (nominal values; no tolerances are given):

| Cat. no. | AWG | Stranding | Nom. wall | Nom. OD |
|---|---|---|---|---|
| 2621/10 | 10 | 1092/40 | 0.045 in (1.14 mm) | 0.223 in (5.664 mm) |
| 2621/8 | 8 | 665/36 | 0.066 in (1.68 mm) | 0.292 in (7.417 mm) |

- **Weight and resistance: not given on the sheet (gap).** No flex-life number.

**Daburn #2616 Ultra-Flexible Silicone Rubber Wire, UL 3135, 200 °C, 600 V** — [Daburn 2616 spec sheet](https://www.daburn.com/specs/2616_Spec_Sheet_12-23-2013.pdf)
- Construction: tinned stranded copper, 0.031 in silicone wall. Rated −40 to +200 °C, 600 V UL, spark test 6,000 V, FT2.
- The table runs **12 to 26 AWG only**, which confirms there is no 10 or 8 AWG row.
- 12 AWG row: 65/30, 0.031 in (0.78 mm) wall, 0.156 in (3.95 mm) OD, 1.72 Ω/mft, 27.05 lbs/mft.

**Daburn #2617 Ultra-Flexible Silicone Rubber Wire, UL 3212, 150 °C, 600 V** (newly found) — [Daburn 2617 spec sheet](https://www.daburn.com/specs/2617_Spec_Sheet_12-23-2013.pdf)
- Construction: tinned stranded copper, 0.045 in silicone wall. Rated −40 to +150 °C, 600 V UL, spark test 6,000 V.
- 10 AWG row 2617/10: 105/30, 0.045 in (1.15 mm) wall, **0.207 in (5.30 mm) nominal OD**, 1.08 Ω/mft, **46.69 lbs/1000 ft (≈69.5 kg/km conv.)**.
- The largest size is 10 AWG; there is no 8 AWG row.

**Daburn #2618 (silver-plated, 200 °C, 300 V) and #2619 (tinned, 150 °C, 300 V) Daflex** — [2618 sheet](https://www.daburn.com/specs/2618_Spec_Sheet.pdf); [2619 sheet](https://www.daburn.com/specs/2619_Spec_Sheet_12-15-2015.pdf)
- Both tables stop at 16 AWG (665/44, 0.104 in OD). Neither has a 10 or 8 AWG row.

**Cicoil Hi-Flex Unshielded Single Conductor Cable (969M101-xx-1)** — [Cicoil product page](https://www.cicoil.com/flat-cable/unshielded-cables/hi-flex-unshielded-single-conductor-cable)
- 10 AWG, **969M101-10-1**: 47 A rating, "42K" volts DC, diameter **0.33 in** (8.4 mm conv.).
- 8 AWG, **969M101-8-1**: 65 A, 42K V DC, diameter **0.39 in** (9.9 mm conv.).
- These match the earlier fragmentary figures. "42K" is shown as "Volts DC", meaning up to 42,000 V DC.
- Conductors: "Ultra flexible, finely stranded, tinned copper". **The strand count and diameter are not given on the page (FLAG** against the earlier "66 base strands", which came from a different Cicoil page and was not re-read).
- Insulation and jacket: Flexx-Sil (Cicoil silicone), 65 Shore A, dielectric strength 450 V/mil.
- Temperature: −104 °C to +165 °C.
  - **FLAG:** the earlier figure was −104 to +260 °C, from a different Cicoil page.
- Minimum bend radius: 6× cable height for intermediate flex, 10× for continuous flex. LSZH.
- **No UL style, no weight, and no OD tolerance on the page.** The 10-million-cycle life figure was not re-read in this session; it remains UNVERIFIED here.

**Helukabel M47021 / SiF UL 3135**
- Not reachable: www.helukabel.com redirects to shop.helu.com, which the session blocks.
- All 10 and 8 AWG values remain **UNVERIFIED**.

### Inferences
- 40 AWG ≈ 0.0031 in (0.080 mm) and 36 AWG ≈ 0.0050 in (0.127 mm) per the standard AWG table (not from these documents).
  - Daburn 2621/10 (1092/40) is therefore the RC-style ~0.08 mm fine-strand construction.
  - 2621/8 (665/36) has ~0.127 mm strands, slightly coarser than the 0.05–0.10 mm target.

### Gaps
- No weight per 1000 ft for Alpha 391000/398133, Daburn 2621 or Cicoil.
- No OD tolerance from Daburn or Cicoil.
- Helukabel not read.
- No manufacturer flex-life, torsion or cut-through figure for any silicone candidate. Daburn 2621 offers only a qualitative "designed for continuous flexing applications".

## Q2. What do the manufacturer documents say for the M22759 / XL-ETFE candidates (/16, /34, /41, /43, TE 82A0113, Spec 55)?

### Takeaway
I read Glenair's GS22759 sheets for /16, /34, /41 and /43. Glenair states each GS part is "made in accordance with AS22759/NN". The sheets confirm the 10 and 8 AWG constructions and ODs, with **maximum** weights.

Two weights are higher than the earlier unverified distributor figures:
- /16-8: 66.7 lbm max vs 63.3–63.5.
- /34-8: 63.3 lbm max vs 60.3.

The RS-hosted PDF that was earlier cited for /34-8 is in fact an **AS22759/32** sheet, which stops at 12 AWG (**FLAG**).

The DLA slash sheets and the TE Raychem 82A0113 and Spec 55 documents could not be reached. Those values remain UNVERIFIED.

### Cited Findings

**Glenair GS22759 equivalents** (Glenair, Glendale CA; CAGE 06324)
- All rated 600 V RMS at sea level. Conductors per AS29606. Weights are "lbs/1000 ft max". Resistance is "Ohms/1000 ft max" at 20 °C. Conductor diameters are min–max.
- Insulation by sheet:
  - /16: extruded ETFE, single wall.
  - /34, /41 and /43: dual-wall, crosslinked extruded modified ETFE primary plus crosslinked modified ETFE jacket.

| Glenair part (per AS22759/NN) | AWG | Stranding | Plating | Conductor dia. in | Finished OD in (mm conv.) | Max Ω/1000 ft | Max wt lbm/1000 ft (kg/km conv.) | Temp | Source | vs earlier |
|---|---|---|---|---|---|---|---|---|---|---|
| GS22759-16-10 (/16) | 10 | 37 x 26 | Tin | 0.106–0.112 | 0.139 ± 0.003 (3.53 ± 0.08) | 1.26 | 35.1 (52.2) | 150 °C | [GS22759-16](https://www.glenair.com/wire-and-cable/pdf/mil-star/gs22759-16.pdf) | matches |
| GS22759-16-8 (/16) | 8 | 133 x 29 | Tin | 0.158–0.169 | 0.199 ± 0.003 (5.05 ± 0.08) | 0.701 | **66.7 (99.3)** | 150 °C | same | **FLAG**: earlier 63.3–63.5 (distributors) |
| GS22759-34-10 (/34) | 10 | 37 x 26 | Tin | 0.106–0.114 | **0.134 ± 0.004 (3.40 ± 0.10)** | 1.26 | 32.4 (48.2) | 150 °C | [GS22759-34](https://www.glenair.com/wire-and-cable/pdf/mil-star/gs22759-34.pdf) | consistent with AWC 0.130–0.138 |
| GS22759-34-8 (/34) | 8 | 133 x 29 | Tin | 0.158–0.173 | 0.195 ± 0.008 (4.95 ± 0.20) | 0.701 | **63.3 (94.2)** | 150 °C | same | **FLAG**: earlier 60.3 (TE/RS attribution); RSCC 61.9 |
| GS22759-41-10 (/41) | 10 | 37 x 26 | Nickel | 0.106–0.113 | 0.134 ± 0.004 (3.40 ± 0.10) | 1.24 | 32.4 (48.2) | 200 °C | [GS22759-41](https://www.glenair.com/wire-and-cable/pdf/mil-star/gs22759-41.pdf) | matches |
| GS22759-41-8 (/41) | 8 | 133 x 29 | Nickel | 0.158–0.173 | 0.195 ± 0.008 (4.95 ± 0.20) | 0.694 | 67.4 (100.3) | 200 °C | same | matches the earlier Glenair figure |
| GS22759-43-10 (/43) | 10 | 37 x 26 | Silver | 0.106–0.112 | 0.134 ± 0.004 (3.40 ± 0.10) | 1.19 | 32.4 (48.2) | 200 °C | [GS22759-43](https://www.glenair.com/wire-and-cable/pdf/mil-star/gs22759-43.pdf) | matches |
| GS22759-43-8 (/43) | 8 | 133 x 29 | Silver | 0.158–0.169 | 0.195 ± 0.008 (4.95 ± 0.20) | 0.658 | 65.0 (96.7) | 200 °C | same | matches |

- None of the four Glenair sheets carries a flex-life, torsion or cut-through statement. Note that these are Glenair's GS equivalents, **not** the SAE slash sheets themselves.
- **AS22759/32 datasheet** — [RS-hosted PDF](https://docs.rs-online.com/6cee/0900766b814ddd69.pdf). The maker is not named in the extracted text.
  - Construction: XL-ETFE single wall, tinned copper, −65 to +150 °C, 600 V, NEMA WC27500 symbol SB.
  - The table ends at **M22759/32-12** (37 x 28, 0.103 ± 0.006 in, 19.70 lbm/1000 ft max). There is no 10 AWG row.
  - **FLAG:** `fluoropolymer_feed_wire.md` cited this URL as the source of /34-8 (0.195 in, 60.3 lbm). It contains no /34 data.
  - It supports sea-wire's statement that /32 ends at 12 AWG, which casts doubt on the RS UK "M22759/32-10-9" listing.
- **Daburn ETFE lines** — [2430 sheet (/16 equivalent)](https://www.daburn.com/specs/2430_Spec_Sheet_06-30-2014.pdf); [2432 sheet (/34 equivalent)](https://www.daburn.com/specs/2432_Spec_Sheet_06-30-2014.pdf)
  - 2430 (cross-referenced to M22759/16) runs 12–24 AWG only.
  - 2432 (cross-referenced to M22759/34) runs 16–24 AWG only.
  - Neither has a 10 or 8 AWG row.
- **TE Raychem 82A0113-10 (665 x 38), 55A0811-8 and 55A0111-10:** www.te.com and www.digikey.com returned Akamai "Access Denied" and www.mouser.com gave an empty reply. **Every value for these parts in `fluoropolymer_feed_wire.md` remains UNVERIFIED.**
- **DLA ASSIST slash sheets:** not retrieved. AS22759 is an SAE document.

### Inferences
- Under the Glenair maximum weights, 8 AWG /34 (63.3 lbm/1000 ft) weighs about 1.95× the 10 AWG /34 (32.4).
- The 8 AWG /34 OD (0.195 in max +0.008 = 0.203 in) still sits below the verified silicone 10 AWG ODs (0.204–0.223 in).

### Gaps
- No primary TE document read.
- No SAE or DLA slash sheet read.
- No flex-life, torsion or dynamic cut-through value read for any AS22759 construction.

## Q3. Does any of these makers publish a 10 AWG wire with OD ≤ 0.217 in (5.5 mm) and a fine-strand (0.05–0.10 mm) tinned-copper conductor?

### Takeaway
**No.** Among the primary documents read, none combines both properties:
- The fine-strand option (Daburn 2621/10, 1092/40 tinned, ~0.08 mm) is 0.223 in (5.664 mm) nominal, 0.006 in over the limit.
- The silicone 10 AWG parts that do fit, Alpha 391000 at 0.204 ± 0.004 in and Daburn 2617/10 at 0.207 in, use coarse 105/30 (~0.25 mm) strands.
- All AS22759 10 AWG parts are 37 x 26 (~0.40 mm strands, my AWG-table figure) at 0.134–0.139 in.
- Cicoil is 0.33 in.
- Helukabel and TE 82A0113-10 (665 x 38 ≈ 0.10 mm, per the earlier unverified note) could not be checked. TE 82A0113-10 is the only remaining lead that might meet both conditions.

### Cited Findings
- Daburn 2621/10: 1092/40 tinned, 0.223 in (5.664 mm) nominal OD — [Daburn 2621](https://www.daburn.com/specs/2621_Spec_Sheet.pdf)
- Alpha 391000: 105/30 tinned, 0.204 ± 0.004 in — [Alpha 391000](https://www.alphawire.com/en/Products/Wire/Hook-Up-Wire/Premium/391000)
- Daburn 2617/10: 105/30 tinned, 0.207 in (5.30 mm) — [Daburn 2617](https://www.daburn.com/specs/2617_Spec_Sheet_12-23-2013.pdf)
- Glenair GS22759-16/34/41/43-10: 37 x 26, 0.134–0.139 in — [GS22759-34](https://www.glenair.com/wire-and-cable/pdf/mil-star/gs22759-34.pdf)
- Cicoil 969M101-10-1: 0.33 in — [Cicoil](https://www.cicoil.com/flat-cable/unshielded-cables/hi-flex-unshielded-single-conductor-cable)

### Inferences
- Four-round bundle check (circumscribed diameter ≈ 2.414 d; my geometry): Daburn 2621/10 at 0.223 in gives 0.538 in, which still fits a 0.64 in ID.
  - The 0.217 in OD assumption is therefore about 0.006 in **non-conservative** for the only verified fine-strand silicone.
  - It is conservative for Alpha 391000 (0.204 in, or 0.208 in at the tolerance limit).
- For 8 AWG silicone, both verified fine and coarse parts (Daburn 2621/8 at 0.292 in, Alpha 398133 at 0.295 in) exceed the 0.265 in four-up limit computed in `silicone_feed_wire.md`. Only the AS22759 8 AWG parts (≤ 0.203 in) fit four-up.

### Gaps
- TE 82A0113-10 OD, weight and availability are unverified (www.te.com, www.mouser.com and www.digikey.com were blocked).
- Helukabel M47021 10 AWG rows were not read.
- Daburn could be asked whether 2621/10 has a maximum OD tolerance or a thinner-wall variant.
