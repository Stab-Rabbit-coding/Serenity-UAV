# Verified phase-lead wire, bullet connectors and QX-Motor QF2822 lead data (primary-source check)

Scope: check the earlier UNVERIFIED figures in `phase_lead_wire.md` against the manufacturers' own pages and datasheets. Read on 2026-11-11.

**Access results (read first).**
- Read directly: www.daburn.com (product pages and spec PDFs), www.alphawire.com (customer-specification PDFs from the Alpha spec-PDF endpoint), qx-motor.co (both product pages).
- **Blocked:**
  - www.te.com and www.mouser.com returned "Access Denied" bot-protection pages (HTTP 403 and 200 respectively). www.digikey.com returned HTTP 403. **No TE Raychem 55A0111 value is verified.**
  - www.castlecreations.com answers with a 301 redirect to `castlecreations.com` (no `www`). That host is not on the session allowlist (proxy CONNECT 403; WebFetch ENOTFOUND). **No Castle value is verified.** `castlecreations.com` must be allowed for a re-check.
- PDFs were downloaded to `/tmp/claude-0/-home-user-Serenity-UAV/e7935527-d46a-5ced-9dfc-025dd0daf273/scratchpad/dl_phase/` and read with `pdftotext -layout`.

Units: inches first, mm in parentheses. Where the datasheet gives only inches, the mm value is my conversion (marked "conv."). Weights in g/ft are my conversions from lb/1000 ft.

## Verified wire values (Daburn, Alpha Wire) and status of TE Raychem 55A0111

### Takeaway
Every Daburn and Alpha Wire figure in the earlier notes is confirmed on the manufacturer documents, except four:
- the Daburn 2616/12 OD (0.156 in = 3.95 mm, not 3.96 mm);
- the 2616/12 wall, now verified at 0.031 in (0.78 mm);
- the AT121925 wall, which is 0.0125 in nominal (DigiKey's 0.013 in was rounded);
- Alpha Wire's address, which is Richmond, IN, not Elizabeth, NJ.

Daburn publishes weights for 2617 and 2616 only. Alpha publishes no weight per 1000 ft.

New finding: Daburn also makes a fine-strand 12 / 14 AWG silicone wire with a datasheet, the 2621 series (672/40 and 441/40, 600 V, 150 °C). This contradicts the earlier gap note that no fine-strand wire with a datasheet was found.

No TE 55A0111 value could be verified, because te.com, Mouser and DigiKey all block automated access.

### Verified table

| Part no. | AWG | Strands x dia | Plating | Insulation / nom. wall in (mm) | Nom. OD in (mm) | Temp | Voltage | UL style / SAE | Wt lb/1000 ft (g/ft conv.) | DCR @20 °C | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Daburn 2617/12 | 12 | 65/30 | Tinned Cu | Silicone rubber, .045 (1.15) | .183 (4.66) | -40 to +150 °C | 600 V UL (spark 6,000 V) | UL 3212, FT2 | 32.26 (14.63) | 1.72 Ω/Mft | [Daburn 2617 page](https://www.daburn.com/2617-Ultra-Flexible-Silicone-Rubber-Wire-UL-3212.aspx); [2617 spec PDF](http://www.daburn.com/specs/2617_Spec_Sheet_12-23-2013.pdf) |
| Daburn 2617/14 | 14 | 41/30 | Tinned Cu | Silicone rubber, .045 (1.15) | .165 (4.20) | -40 to +150 °C | 600 V UL | UL 3212, FT2 | 23.21 (10.53) | 2.73 Ω/Mft | same |
| Daburn 2616/12 | 12 | 65/30 | Tinned Cu | Silicone rubber, .031 (0.78) | .156 (3.95) | -40 to +200 °C | 600 V UL (spark 6,000 V) | UL 3135, FT2 | 27.05 (12.27) | 1.72 Ω/Mft | [Daburn 2616 page](https://www.daburn.com/UL-3135-Silicone-Rubber-Wire-2616-Ultra-Flexible.aspx); [2616 spec PDF](http://www.daburn.com/specs/2616_Spec_Sheet_12-23-2013.pdf) |
| Daburn 2616/14 (extra) | 14 | 41/30 | Tinned Cu | Silicone rubber, .031 (0.78) | .136 (3.46) | -40 to +200 °C | 600 V UL | UL 3135, FT2 | 18.58 (8.43) | 2.73 Ω/Mft | same |
| Daburn 2627/12 | 12 | 65/30 | Tinned Cu | Silicone rubber + fiberglass braid, 0.031 (0.78) | 0.176 (4.46) | -40 to +200 °C | 600 V | UL 3231, FT2 | not published | 1.921 Ω/Mft | [Daburn 2627 page](https://www.daburn.com/2627-UL-3231-Silicone-Rubber-Wire-with-Fiberglass-Braid-600V-200-C.aspx); [2627 spec PDF Rev A](http://www.daburn.com/specs/2627_Spec_Sheet_10-01-2014_Rev_A.pdf) |
| Daburn 2627/14 (extra) | 14 | 41/30 | Tinned Cu | as above, 0.031 (0.78) | 0.150 (3.81) | -40 to +200 °C | 600 V | UL 3231, FT2 | not published | 2.701 Ω/Mft | same |
| Daburn 2621/12 (new) | 12 | 672/40 | Tinned Cu | Extruded silicone rubber, .035 (0.889) | .169 (4.293) | -40 to +150 °C | 600 V | no UL style stated | not published | not published | [Daburn 2621 page](https://www.daburn.com/2621-Ultra-Flexible-High-Strand-Silicone-Rubber-Wire-600V-150-C.aspx); [2621 spec PDF Rev C](http://www.daburn.com/specs/2621_Spec_Sheet.pdf) |
| Daburn 2621/14 (new) | 14 | 441/40 | Tinned Cu | Extruded silicone rubber, .035 (0.889) | .153 (3.886) | -40 to +150 °C | 600 V | no UL style stated | not published | not published | same |
| Alpha Wire AT121925 | 12 | 19/25 | Silver-plated Cu (conductor dia 0.086 in, 2.18 mm conv.) | PTFE, 0.0125 nom. (0.32 conv.) | 0.111 ±0.003 (2.82 ±0.08 conv.) | -55 to 200 °C | 600 VRMS | SAE-AS22759/11 (200 °C / 600 VRMS) | not published | 1.74 Ω/1000 ft nom. | [Alpha AT121925 customer spec PDF](https://www.alphawire.com/disteAPI/SpecPDF/DownloadProductSpecPdf?productPartNumber=AT121925) |
| Alpha Wire AT141927 | 14 | 19/27 | Silver-plated Cu (conductor dia 0.069 in, 1.75 mm conv.) | PTFE, 0.0105 nom. (0.27 conv.) | 0.090 ±0.002 (2.29 ±0.05 conv.) | -55 to 200 °C | 600 VRMS | SAE-AS22759/11 (200 °C / 600 VRMS) | not published | 2.8 Ω/1000 ft nom. | [Alpha AT141927 customer spec PDF](https://www.alphawire.com/disteAPI/SpecPDF/DownloadProductSpecPdf?productPartNumber=AT141927) |
| TE Raychem 55A0111-12 / -14 | 12 / 14 | **UNVERIFIED** | **UNVERIFIED** | **UNVERIFIED** (earlier: XL-ETFE, 0.006 in) | **UNVERIFIED** (earlier: ~0.103 in / 2.62 mm for -12) | **UNVERIFIED** | **UNVERIFIED** | Spec 55 (earlier: M22759/32), **UNVERIFIED** | **UNVERIFIED** (earlier: 19.7 for -12) | — | te.com, mouser.com and digikey.com blocked the request (bot protection) |

### Cited Findings
- Daburn 2617 is "single conductor stranded tinned copper insulated with .045" silicone rubber insulation", rated -40 °C to +150 °C and 600 Volts UL (spark voltage 6,000 V), FT2, and meets UL Style 3212. The table values for /12 and /14 are as above — [2617 spec PDF](http://www.daburn.com/specs/2617_Spec_Sheet_12-23-2013.pdf); [2617 page](https://www.daburn.com/2617-Ultra-Flexible-Silicone-Rubber-Wire-UL-3212.aspx).
- Daburn 2616 is tinned copper with ".031" silicone rubber insulation", -40 °C to +200 °C, 600 V UL, FT2, and meets UL Style 3135. 2616/12: .156 in (3.95 mm) OD, 27.05 lb/Mft — [2616 spec PDF](http://www.daburn.com/specs/2616_Spec_Sheet_12-23-2013.pdf).
- Daburn 2627 is silicone rubber with a fiberglass braid and stranded tinned copper, UL 3231, 200 °C, 600 V, FT2. 2627/12: 65/30, 0.031 in (0.78 mm) wall, 0.176 in (4.46 mm) OD — [2627 spec PDF Rev A](http://www.daburn.com/specs/2627_Spec_Sheet_10-01-2014_Rev_A.pdf).
- Daburn 2621 "Daflex" is high-strand-count fine tinned copper with extruded silicone, -40 °C to +150 °C, 600 V, "designed for continuous flexing applications". 2621/12 is 672/40 at .169 in (4.293 mm) OD; 2621/14 is 441/40 at .153 in (3.886 mm) — [2621 spec PDF](http://www.daburn.com/specs/2621_Spec_Sheet.pdf).
- Daburn 2618 (silver-plated, 200 °C, 300 V high-strand silicone) stops at 16 AWG (665/44, .104 in / 2.642 mm), so there is no 12 or 14 AWG part — [2618 spec PDF](http://www.daburn.com/specs/2618_Spec_Sheet.pdf).
- Alpha AT121925 datasheet: "12 (19/25) AWG Silver Plated Copper 0.086", "0.0125" Wall, Nom. PTFE 0.111+/- 0.003", SAE-AS22759/11 200 °C / 600 VRMS, -55 to 200 °C, bend radius 10x cable diameter, pull tension 48 lb max, DCR 1.74 Ω/1000 ft. No weight is given — [AT121925 PDF](https://www.alphawire.com/disteAPI/SpecPDF/DownloadProductSpecPdf?productPartNumber=AT121925).
- Alpha AT141927 datasheet: "14 (19/27) AWG Silver Plated Copper 0.069", "0.0105" Wall, Nom. PTFE 0.090+/- 0.002", SAE-AS22759/11 200 °C / 600 VRMS, -55 to 200 °C, bend radius 10x, pull tension 30 lb max, DCR 2.8 Ω/1000 ft. No weight is given — [AT141927 PDF](https://www.alphawire.com/disteAPI/SpecPDF/DownloadProductSpecPdf?productPartNumber=AT141927).
- The Alpha Wire datasheet address is 2200 US Highway 27 South, Richmond, IN 47374 — [AT121925 PDF](https://www.alphawire.com/disteAPI/SpecPDF/DownloadProductSpecPdf?productPartNumber=AT121925).

### Differences from the earlier unverified figures
- Daburn 2617/12 and 2617/14: all values match. The wall in mm is 1.15 mm on the datasheet; the earlier notes said 1.14 mm (a conversion).
- Daburn 2616/12:
  - The OD is .156 in (**3.95 mm**), not 3.96 mm.
  - The wall (.031 in / 0.78 mm), the weight (27.05 lb/Mft) and the FT2 rating are now verified. All three were missing before.
  - The temperature (200 °C), voltage (600 V) and UL 3135 rating match.
- Daburn 2627/12: everything matches. The plating is now confirmed as tinned copper. Daburn publishes no weight.
- Alpha AT121925: the wall is 0.0125 in nominal. DigiKey's "0.013 in / 0.33 mm" was a rounding. The OD (0.111 in) matches, and the tolerance of ±0.003 in is new.
- Alpha AT141927: everything matches. The tolerance of ±0.002 in is new.
- Alpha domicile: the datasheet gives Richmond, IN. The earlier notes said "Elizabeth, NJ". That may be the corporate HQ, but it is not confirmed here.
- Earlier gap "no fine-strand silicone with a manufacturer datasheet": **contradicted** by Daburn 2621 (672/40 at 12 AWG, 441/40 at 14 AWG). Daburn does not say where the wire is made.

### Inferences
- In this candidate set, Daburn 2616/12 is the thinnest 200 °C 12 AWG silicone, at 0.156 in (3.95 mm). It is 0.027 in (0.70 mm) thinner than 2617/12 and adds 50 °C of rating.
- Daburn 2621/12 is the fine-strand option for flexibility, but it is rated only 150 °C, and Daburn states no UL style for it.
- Alpha PTFE is still the smallest (0.111 in / 0.090 in), with a 10x OD bend radius: about 1.1 in (28 mm) at 12 AWG and 0.9 in (23 mm) at 14 AWG (my calculation).

### Gaps
- TE Raychem 55A0111-12 / -14: every value is unverified. te.com, Mouser and DigiKey all serve bot-protection pages to this session. The values need a manual browser check of the TE product page or of the Raychem Spec 55 / 55A01 specification.
- Weight per 1000 ft is not published for Alpha AT121925 / AT141927, Daburn 2627 or Daburn 2621.
- Daburn gives no country of manufacture on any of these sheets.

## Castle Creations bullet connectors (3.5 / 4 / 5.5 mm): current rating and wire range

### Takeaway
**Not verified.** www.castlecreations.com redirects to `castlecreations.com`, which is outside the session allowlist, so no Castle page was read. All earlier Castle figures remain retailer claims:
- 4 mm: 75 A, 16-13 AWG (CCBUL43 / 011-0065-00);
- 5.5 mm: 150 A, 13-10 AWG (CCBUL553);
- 6.5 mm: 200 A.

### Cited Findings
- Request to `https://www.castlecreations.com/en/accessories/connectors` returned HTTP 301, redirect to `https://castlecreations.com/en/accessories/connectors`. The proxy refused that host (CONNECT 403), and WebFetch returned ENOTFOUND for www.castlecreations.com. (Observed in this session; no URL to cite beyond the attempt.)

### Inferences
- None beyond the earlier notes.

### Gaps
- The Castle current ratings, the wire-gauge ranges and whether Castle sells a 3.5 mm bullet are all unverified. Add `castlecreations.com` (bare host) to the allowlist and re-read the Castle connector pages.

## QX-Motor QF2822 / 64 mm EDF set: lead gauge, lead length, connector

### Takeaway
QX-Motor's own pages **do not publish** the lead gauge, the lead length or the connector type for the QF2822 or the 64 mm EDF set. Also, **QX-Motor does not list a 2300KV variant**. Its page lists 2200, 2400, 3500, 3800 and 4300 KV. The earlier "QF2822-2300KV" came from a Fruugo listing (2100/2300/3300/4300 KV) and conflicts with the manufacturer's page. The second URL (product/2365) is the 64 mm EDF **without a motor** and has no electrical data.

### Cited Findings
- QX-Motor page title: "QX-MOTOR New 64mm EDF 2200KV/2400KV/3500KV/3800KV Brushless Motor with 12 Blades Ducted Fan". Additional information lists:
  - KV: 2200, 2400, 3500, 3800 and 4300 KV;
  - configuration 9N6P;
  - 3-6S LiPo;
  - "Max Continuous Current/10S": 50 A, 60 A, 66 A, 68 A, 70 A;
  - "Max Continuous Power/10S": 1000, 1050, 1110, 1300, 860 W;
  - shipping weight 0.2 kg.

  It gives no wire, lead or connector data — [QX-Motor 64 mm EDF QF2822 set](https://qx-motor.co/product/64mm-edf-12-blade-2822-brushless-motor-set/).
- QX-Motor test table (64 mm, 12 blades):
  - QF2822-2200KV, 60 A ESC: 22.2 V, 47.0 A, 1043.4 W, 1870 g;
  - QF2822-2400KV, 60 A ESC: 22.2 V, 57.0 A, 1265.4 W, 2135 g;
  - QF2822-3500KV, 80 A ESC: 16 V, 66.0 A, 1810 g;
  - QF2822-3800KV, 80 A ESC: 16 V, 70.0 A, 1925 g;
  - QF2822-4300KV, 80 A ESC: 12.6 V, 68.0 A, 1550 g

  — [same page](https://qx-motor.co/product/64mm-edf-12-blade-2822-brushless-motor-set/).
- product/2365 is "64MM EDF without Motor 12 Blades Ducted Fan CW/CCW", with no specifications in the text — [QX-Motor product 2365](https://qx-motor.co/product/2365/).
- The company is Shenzhen Qunxi Electronics Co., Ltd. (site footer) — [QX-Motor](https://qx-motor.co/product/64mm-edf-12-blade-2822-brushless-motor-set/).

### Inferences
- QX-Motor publishes current figures of 47-70 A per motor, above the project's 47 A RMS full-throttle value. Re-leading with 12 AWG is therefore consistent with the manufacturer's current figures. The stock lead gauge must be measured.
- If the project assumes 2300 KV, the motor selection should be re-checked against the KV values QX-Motor actually lists.

### Gaps
- Lead gauge, lead length and bullet size are not published as text by QX-Motor. They may appear in product images, which I could not read, or must be measured on a delivered motor.
