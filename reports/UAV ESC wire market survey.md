> [!WARNING]
> **ENGINEERING REVIEW REQUIRED — this output is not a substitute for a qualified engineer.** Every result, calculation, and recommendation produced with this skill **must be independently reviewed and accepted by a properly qualified individual** — a licensed Professional Engineer or an equivalently qualified authority for the jurisdiction and discipline — **before it is applied to any system carrying risk to life or safety.**

> [!CAUTION]
> **This skill informs engineering judgment; it does not replace it.** Applying unreviewed results to real equipment or hardware — even where no life-safety risk exists — carries a risk of equipment damage or property loss. It is reference material provided AS-IS (see LICENSE §5), is not an engineering service, and does not constitute a sealed, certified, or reviewed work product for any specific project.

# Hover current, not peak, sizes Serenity's nacelle wiring

License: CC BY-SA 4.0 — see LICENSES/CC-BY-SA 4.0 (SPDX-License-Identifier: CC-BY-SA-4.0). AI-generated synthesis (Claude Opus 5.5) of the research notes in `research_notes/UAV ESC wire market survey/`; every figure traces to those notes and their cited sources. Not reviewed by a human engineer.

The QX-Motor QF2822-2300KV datasheet sets three numbers that drive everything: **57 A at 24 V full throttle, a 60 A / 10 s maximum, and an 80 A recommended ESC** ([QX-Motor 2300KV instruction sheet](https://cdn.shopify.com/s/files/1/0713/6424/7837/files/64_2822-2300KV_00.png)). But the case that actually sizes the copper is the long one: VTOL hover, which on the 6,500 g (14.33 lbm) ledger pulls **about 33 A per fan at 24 V and 37-38 A late in the pack at 21.0 V** (ESTIMATE, interpolated from the datasheet table). Against that load, a **10 AWG, 302 deg F (150 deg C), 600 V tinned-copper silicone feed lead with OD at most 0.217 in (5.5 mm)** fits the existing spar bore and the OD-17 bend channels. It carries the load only if the carbon spar is not what limits temperature. In a standard 200 deg F (93 deg C) epoxy tube, the FAA bundle method gives the four-wire group **about 33 A per wire, which is below the 38 A late-pack case** (ESTIMATE). The phase leads must go up from the BOM's 16 AWG to **12 AWG rated 392 deg F (200 deg C)**, which no longer fits the pod's 0.197 in (5.0 mm) lead conduit. The 40 A branch fuse in the BOM sits below the full-throttle draw and barely above late-pack hover; a fuse that opens in hover shuts down one of four fans. That is a **WARNING-level** item for the owner. The searchable wire specifications are below. Every part number in them was read on a manufacturer document; the five owner decisions follow them.

**How figures are marked.** **[V]** means read on the manufacturer document or the standard. **[U]** means unverified: from a seller, a distributor or search excerpt, or a document that could not be reached. **[E]** means an engineering ESTIMATE derived here or in the coordinator synthesis. Call-outs follow the CNAF M-3710.7 convention: WARNING for risk of life or aircraft loss, CAUTION for risk of equipment damage, NOTE for everything else.

## Summary wire specification

### (1) ESC power-feed lead: four per nacelle, through the CF spar

| Attribute | Specification |
|---|---|
| Gauge | **10 AWG** [E: sized below]; 8 AWG only under Decision 1 option C |
| Conductor | Copper, **tin-plated**, stranded, **at least 19 strands** (AC 43.13-1B para 11-66a [V]); 105/30 is the construction that fits [V] |
| Insulation and listing | Silicone rubber, **UL AWM Style 3212** (Alpha 391000 [V]; Daburn 2617 [V]). Alternate: crosslinked ETFE per **SAE AS22759/34** (Glenair GS22759-34 [V]) |
| Temperature rating | **-40 to 302 deg F (-40 to 150 deg C)** silicone [V]; -67 to 302 deg F (-55 to 150 deg C) is the usual /34 range [U: the Glenair sheet gives 150 deg C maximum, and the low end was not read] |
| Voltage rating | **600 V** [V] |
| Maximum OD | **0.217 in (5.5 mm)** for 4-up in the 0.642 in (16.3 mm) bore with 0.059 in (1.5 mm) twist clearance [E, geometry] |
| Search string | `10 AWG UL 3212 silicone 600V 150C tinned copper 105/30` |

| Part number (manufacturer) | Stranding | OD | Weight | Status |
|---|---|---|---|---|
| **Daburn 2617/10** (Daburn Electronics & Cable) | 105/30 tinned | 0.207 in (5.3 mm) nominal | **46.69 lbm/1000 ft (69.5 kg/km)** | [V] ([Daburn 2617 sheet](https://www.daburn.com/specs/2617_Spec_Sheet_12-23-2013.pdf)) |
| **Alpha Wire 391000** (Alpha Wire; colour suffix per vendor) | 105/30 tinned | **0.204 ± 0.004 in (5.18 ± 0.10 mm)** | not published | [V] ([Alpha 391000](https://www.alphawire.com/en/Products/Wire/Hook-Up-Wire/Premium/391000)) |
| **Glenair GS22759-34-10** (Glenair; "made in accordance with AS22759/34") | 37 x 26 tinned | 0.134 ± 0.004 in (3.40 ± 0.10 mm) | 32.4 lbm/1000 ft max (48.2 kg/km) | [V] ([GS22759-34](https://www.glenair.com/wire-and-cable/pdf/mil-star/gs22759-34.pdf)) |

### (2) Motor phase lead: three per motor, ESC to motor

| Attribute | Specification |
|---|---|
| Gauge | **12 AWG** [E: sized below]; replaces BOM WIRE-16AWG |
| Conductor | Copper, **silver-plated** (PTFE option) or **tin-plated** (silicone option), at least 19 strands [V] |
| Insulation and listing | PTFE per **SAE AS22759/11** (Alpha AT121925 [V]) or silicone **UL 3135** (Daburn 2616 [V]) or silicone with fibreglass braid **UL 3231** (Daburn 2627 [V]) |
| Temperature rating | **392 deg F (200 deg C)** minimum [E: needed near the motor]; the parts below are -67 to 392 deg F (-55 to 200 deg C) for PTFE and -40 to 392 deg F (-40 to 200 deg C) for silicone [V] |
| Voltage rating | **600 V** (600 VRMS for AS22759/11) [V] |
| Maximum OD | **0.114 in (2.90 mm)** if the conduit is enlarged only to about 0.28 in (7.0 mm); 0.18 in (4.5 mm) if it goes to about 0.39 in (10 mm) [E, geometry; Decision 3] |
| Search string | `12 AWG M22759/11 PTFE silver plated 200C 600V` or `12 AWG UL 3135 silicone 200C 600V` |

| Part number (manufacturer) | Stranding | OD | Weight | Status |
|---|---|---|---|---|
| **Alpha Wire AT121925** (Alpha Wire, Richmond IN) | 19/25 silver-plated | **0.111 ± 0.003 in (2.82 ± 0.08 mm)** | not published | [V] ([AT121925 spec](https://www.alphawire.com/disteAPI/SpecPDF/DownloadProductSpecPdf?productPartNumber=AT121925)) |
| **Daburn 2616/12** (Daburn) | 65/30 tinned | 0.156 in (3.95 mm) | **27.05 lbm/1000 ft (40.3 kg/km)** | [V] ([Daburn 2616 sheet](http://www.daburn.com/specs/2616_Spec_Sheet_12-23-2013.pdf)) |
| **Daburn 2627/12** (Daburn; silicone plus fibreglass braid) | 65/30 tinned | 0.176 in (4.46 mm) | not published | [V] ([Daburn 2627 sheet](http://www.daburn.com/specs/2627_Spec_Sheet_10-01-2014_Rev_A.pdf)) |

### (3) ESC rating: one per motor (BOM OSESC-NAC, in-house build, OD-3)

| Attribute | Specification |
|---|---|
| Continuous rating | **80 A**, the manufacturer's recommendation [V] ([QX-Motor sheet](https://cdn.shopify.com/s/files/1/0713/6424/7837/files/64_2822-2300KV_00.png)). This closes OD-3 (70 A vs 80 A) in favour of 80 A |
| Duty it must survive | **38 A sustained for the whole hover mission** at bay temperature [E]; **57 A at full throttle, 60 A for 10 s** [V] |
| Input | 6S LiPo [V: motor rated 3-6S]. Feed input from (1), M3 stud ring terminals at the disconnect bay [project geometry] |
| Output | Three 12 AWG phase leads per (2) |
| Current limit | Set at or below the feed lead's short-time capability and coordinated with the branch fuse (Decision 4) [E] |
| Part numbers | **None verified.** The BOM carries the in-house Open-Secure-ESC build (OSESC-NAC), whose 52.7 g mass is a roll-up estimate of a 70 A design. The research notes contain no verified commercial 80 A ESC datasheet |

## The datasheet gives 57 A, but hover's 38 A runs all mission

The 24 V table on the QX-Motor sheet runs from 10.0 A at 50 % throttle to **57.0 A, 1,368 W and 2,370 g of thrust at 100 %**. The sheet also states a **maximum continuous current of 60 A / 10 s** and recommends an **80 A ESC** [V] ([QX-Motor sheet](https://cdn.shopify.com/s/files/1/0713/6424/7837/files/64_2822-2300KV_00.png)). The sheet publishes no winding resistance, lead gauge, lead length or connector [V]. Hover at 1,625-1,651 gf per fan interpolates to **32.2-33.0 A at 24 V and about 77-78 % throttle**. Holding the same 773-791 W as the pack sags to 3.5 V/cell takes **37-38 A at 21.0 V** [E]. VTOL hover is the sustained case for the whole mission. That makes 38 A, not 57 A, the continuous design current; 57-60 A is a short-time case. The repository's older "28 A sustained hover" figure came before the weight growth and is superseded.

Phase-lead current is higher than the DC feed because of commutation. Under an ideal six-step model, the RMS phase current is about **35 A in hover and 46.5 A at full throttle** [E]. That one calculation rules out the BOM's 16 AWG phase leads. At 35 A RMS, 16 AWG dissipates **16.5 W/m against 6.5 W/m for 12 AWG** [E] in a hot pod right next to the motor.

The motor itself carries an unresolved identity question (Decision 5). QX-Motor's current product page lists the QF2822 in **2200, 2400, 3500, 3800 and 4300 KV, with no 2300 KV**. The 2300 KV figure in the earlier unverified note traced back to a Fruugo seller listing ([QX-Motor QF2822 set](https://qx-motor.co/product/64mm-edf-12-blade-2822-brushless-motor-set/)) [V]. The sizing still holds if the delivered motor turns out to be the 2400 KV. That variant is listed at **60 A / 10 s and tests at 57.0 A, 1,265 W and 2,135 g on 22.2 V**, which is the same current envelope [V]. The same page pairs the 2200 and 2400 KV motors with a **60 A ESC**, while the 2300 KV sheet asks for 80 A [V]. The more conservative 80 A recommendation governs.

## The carbon spar, not the wire, caps the feed at 33 A

FAA AC 43.13-1B sizes a bundle in three steps ([AC 43.13-1B CHG 1](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_43.13-1B_w-chg1.pdf)) [V]. Take the single-wire free-air current at the allowable temperature difference from **Figure 11-4a/b**. Multiply by the bundle factor from **Figure 11-5**, then by the altitude factor from **Figure 11-6** (paras 11-67c-e). The figures are raster charts, so the readings below are chart measurements, not printed values. They are good to ±5 % and run 2-3 % low against the AC's own worked examples [E]. Four wires that all carry load sit on the 100 % curve at **0.68**, and sea level reads **1.00** [E, chart reading].

| Case | Temperature difference | 10 AWG per wire | 8 AWG per wire |
|---|---|---|---|
| Standard epoxy spar, about 200 deg F (93 deg C) limit, 104 deg F (40 deg C) ambient | 90 deg F (50 deg C) | 49 x 0.68 = **33 A** [E] | 72 x 0.68 = **49 A** [E] |
| Spar not limiting: 302 deg F (150 deg C) wire, 104 deg F (40 deg C) ambient | 198 deg F (110 deg C) | 71 x 0.68 = **48 A** [E] | 107 x 0.68 = 73 A [E] |

The governing constraint is the epoxy around the wire, not the wire. The AC caps tin-plated copper at **302 deg F (150 deg C)** (para 11-77b) [V]. Standard carbon tubes are rated far lower: Rock West's filament-wound tubes at **Tg 200-224 deg F (93-107 deg C)** and DragonPlate's at **200 deg F (93 deg C)** [U: search-sourced; the spar vendor's resin datasheet was not read]. Rock West offers a resin "good for up to 400F" (204 deg C) [U] ([Rock West filament-wound BYOT](https://www.rockwestcomposites.com/byot-fw.html); [DragonPlate tube](https://dragonplate.com/dragonplate-carbon-tube-375od-x-290id-x-48)). With the wire touching a 200 deg F tube wall, the 10 AWG bundle reaches **33 A, which is the bottom of the 33-38 A hover band and short of the late-pack 38 A**. In a high-temperature tube the same wire reaches **48 A**, a 26 % margin over 38 A [E].

Two corrections to earlier figures follow from this. First, the BOM's WIRE-10AWG note says "55 A rated free air". The AC chart gives **about 49 A** free air for 10 AWG at a 90 deg F (50 deg C) difference, and the four-wire bundle in the spar is lower again. Second, **AC Table 11-9 does not apply**: its 26 A (150 deg C) and 32 A (200 deg C) ratings for 10 AWG assume 33 or more wires at 158 deg F (70 deg C) ambient and 60,000 ft [V]. All of these are free-air numbers for a bundle that actually sits in a closed tube. The AC itself recommends **load-bank and high-temperature-chamber testing** at worst-case ambient and current (para 11-66d(5)) [V]. A thermocouple on the spar wall at 38 A sustained is the qualification that settles the question.

Resistance and voltage drop are not the problem. Daburn 2617/10 measures **1.08 ohm/1000 ft at 68 deg F (20 deg C)** [V]. Over an estimated 0.5 m (1.6 ft) one-way run, the loop drops **about 0.14 V at 38 A (0.6 % of 24 V)**, and the 0.173 m (6.8 in) of spar dissipates **about 3.5 W across all four conductors** at 68 deg F, rising roughly 31 % when hot [E]. Heat matters only because the tube traps it.

## Three verified 10 AWG wires clear the 0.642 in bore

The 2 x 2 bundle of four wires of diameter d circumscribes 2.414 d. Adding 0.059 in (1.5 mm) of twist clearance per side inside the 0.642 in (16.3 mm) bore sets the **0.217 in (5.5 mm) maximum OD** [E, geometry]. The manufacturer documents change two figures that the earlier unverified notes carried. **Alpha 391000 is 0.204 ± 0.004 in, not the 0.212 in from a Farnell copy.** Its 8 AWG sibling **398133 is listed as UL AWM 3213 only**, not 3212/3213/3214 ([Alpha 391000](https://www.alphawire.com/en/Products/Wire/Hook-Up-Wire/Premium/391000); [Alpha 398133](https://www.alphawire.com/en/Products/Wire/Hook-Up-Wire/Premium/398133)) [V].

| Wire | AWG | OD | Bundle + clearance vs 16.3 mm | Fits? |
|---|---|---|---|---|
| Alpha 391000, silicone 105/30 | 10 | 0.204 in (5.18 mm) [V] | 15.5 mm [E] | yes |
| Daburn 2617/10, silicone 105/30 | 10 | 0.207 in (5.3 mm) [V] | 15.8 mm [E] | yes |
| Daburn 2621/10, fine-strand silicone 1092/40 | 10 | 0.223 in (5.66 mm) [V] | 16.7 mm [E] | **no**: fits only with clearance cut to 0.051 in (1.3 mm) |
| Glenair GS22759-34-10, XL-ETFE 37 x 26 | 10 | 0.134 in (3.40 mm) [V] | 11.2 mm [E] | yes |
| Glenair GS22759-34-8, XL-ETFE 133 x 29 | 8 | 0.195 ± 0.008 in (4.95 mm) [V] | 14.95 mm [E] | yes |
| Alpha 398133 / Daburn 2621/8, silicone | 8 | 0.295 / 0.292 in [V] | over 21 mm [E] | no |

Bend radius after the spar separates 10 AWG from 8 AWG. **NASA-STD-8739.4A Table 7-1** sets a minimum of **3 x OD for an overall harness of AWG 10 or smaller and 6 x OD for AWG 8 or larger**, with 10 x OD as the optimum ([NASA-STD-8739.4A Chg 3, p. 30](https://standards.nasa.gov/sites/default/files/standards/NASA/A/3/nasa-std-87394a_w_change_3.pdf)) [V]. That corrects the earlier unverified "6 x OD" note, which applies only to the 8 AWG and coax rows. The OD-17 channels have 0.65 in (16.5 mm) and 0.87 in (22 mm) centrelines. They meet 3 x OD for 10 AWG silicone (0.62 in, 15.8 mm) [E]. They fail 6 x OD for 8 AWG XL-ETFE (1.17 in, 29.7 mm) [E]. **AC 43.13-1B para 11-117** asks for 10 x the largest wire OD (6 x at supported breakouts) [V], and no option meets it. Alpha's own sheet also states a **10 x cable-diameter bend radius**, 2.04 in (52 mm) for 391000 [V]. That is a manufacturer limit the 0.65 in channel does not meet. Daburn's 2617 sheet, as read, states no bend radius, so NASA's 3 x OD is the controlling figure for it. **This is the reason Daburn 2617/10 leads the feed table.**

**CAUTION — torsion life is unqualified for every candidate.** The 140 deg twist per tilt cycle is torsion. None of the manufacturer documents read gives a torsion, flex-life or cut-through figure for any 10 AWG candidate [V: absence confirmed]. Every verified part that fits uses coarse strands: 105/30 at about 0.25 mm, or 37 x 26 at about 0.40 mm [E: AWG table]. A cable maker's note warns that torsion life depends on a long lay and a balanced construction, not only on fine strands [U] ([JT Copper](https://en.jtcopper.com/why-can-robot-cables-bend-millions-of-times-without-breaking-the-real-challenge-is-not-the-jacket-but-the-copper-wire-structure.html)). A torsion-cycle test of the chosen wire at 140 deg over the real spar length is required whichever wire is chosen.

**CAUTION — do not solder-tin crimped ends.** NASA-STD-8739.4A §7.2.26 a-c restricts crimp contacts to stranded wire and bars solid, tinned wire. The explicit ban on "crimping of solder tinned stranded wire" survives only in the Change 1 history-log entry. §13.3.1 explains the mechanism: solder wicking stiffens the conductor and concentrates flex stress where the wicking stops [V] ([NASA-STD-8739.4A Chg 3](https://standards.nasa.gov/sites/default/files/standards/NASA/A/3/nasa-std-87394a_w_change_3.pdf)).

**NOTE — abrasion sleeve.** The coordinator calls for braided PET over the bundle in the spar plus a chamfer or grommet at the spar mouth. Techflex PTN0.50 is rated -94 to 257 deg F (-70 to 125 deg C) [U] ([AWC PTN0.50](https://www.awcwire.com/product/ptn0-50)). The sleeve also takes up bore. Roundit 2000's sheet gives a 0.009 in (0.23 mm) wall [U] ([IEWC Roundit 2000](https://media.iewc.com/SpecificationSheets/ROUNDIT2000.pdf)). That adds about 0.018 in (0.46 mm) to the bundle diameter and brings Daburn 2617/10 to **about 16.25 mm against the 16.3 mm bore** [E]. A thicker PET braid would push it over. Measure the sleeved bundle before committing to a sleeve.

## Phase leads need 12 AWG at 392 deg F, which outgrows the conduit

The chart method has to be stretched for the phase leads. Near the motor the ambient is assumed to reach **176 deg F (80 deg C)** [E]. A 392 deg F (200 deg C) wire then has a 216 deg F (120 deg C) difference, for which the Figure 11-4a readings interpolate to **about 56 A free air for #12 and 42 A for #14** [E]. A 3-lead group factor of **about 0.7** was not read off Figure 11-5; it is taken as falling between the 4-wire 0.68 and 1.0 [E]. With it, **#12 carries about 39 A and passes 35 A RMS hover; #14 carries about 29 A and fails** [E]. The same arithmetic disqualifies the 302 deg F (150 deg C) parts. At a 126 deg F (70 deg C) difference, #12 reads about 43 A free air, or **about 30 A grouped, below hover** [E]. That excludes Daburn 2617/12 and the fine-strand Daburn 2621/12 (672/40, 302 deg F (150 deg C), no UL style stated) [V] ([Daburn 2621 sheet](http://www.daburn.com/specs/2621_Spec_Sheet.pdf)). The 46.5 A RMS full-throttle case exceeds the grouped figure. It is a short-time case bounded by the motor's 10 s rating, and the AC's continuous charts do not cover it.

Among the 392 deg F (200 deg C) options, **Alpha AT121925** (AS22759/11 PTFE, 19/25 silver-plated, 0.111 ± 0.003 in) is the thinnest. **Daburn 2616/12** (UL 3135, 65/30 tinned, 0.156 in, 27.05 lbm/1000 ft) is the more flexible silicone. **Daburn 2627/12** (UL 3231, fibreglass braid, 0.176 in) adds abrasion protection ([AT121925](https://www.alphawire.com/disteAPI/SpecPDF/DownloadProductSpecPdf?productPartNumber=AT121925); [Daburn 2616](http://www.daburn.com/specs/2616_Spec_Sheet_12-23-2013.pdf); [Daburn 2627](http://www.daburn.com/specs/2627_Spec_Sheet_10-01-2014_Rev_A.pdf)) [V]. The verified notes corrected two earlier figures here: the 2616/12 OD is 0.156 in (3.95 mm), not 3.96 mm, and the AT121925 wall is 0.0125 in, not DigiKey's rounded 0.013 in. Each insulation trades something away. AC Table 11-2b ranks **PTFE most flexible but last for abrasion and cut-through** [V] ([AC 43.13-1B, p. 11-37](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_43.13-1B_w-chg1.pdf)), and Alpha states a 10 x OD bend radius of about **1.1 in (28 mm)** for AT121925 [V/E].

Each 12 AWG option outgrows the pod's **0.197 in (5.0 mm)** stage-1 conduit. Three round leads circumscribe 2.155 d. That gives **about 0.24 in (6.1-6.2 mm) for the PTFE and 0.34 in (8.5 mm) for Daburn 2616/12**, before any clearance [E]. The only lead small enough for the existing conduit, Alpha AT141927 at 14 AWG (0.090 in) [V], fails on ampacity.

**NOTE — bullet connectors.** QX-Motor does not publish the stock lead gauge, length or connector [V]. Castle's 5.5 mm (13-10 AWG, 150 A) and 4 mm (16-13 AWG, 75 A) ratings remain **retailer claims [U]**, because castlecreations.com was not reachable. The 16-13 AWG range on the 4 mm part suggests a 12 AWG lead points to the 5.5 mm bullet [U] ([Graves RC](https://gravesrc.com/csem0002-castle-creations-5-5mm-bullet-connector-13g-10g-150a-3)). AC para 11-67 says that the contact rating, not the wire, sets the limit where the contact is weaker [V]. Measure a delivered motor's leads and read Castle's own pages before ordering terminations.

## Owner Decision Brief

### Decision 1: feed temperature margin — high-temperature spar, test, or 8 AWG (reopens OD-17)

| | A. High-temperature-resin CF spar, 10 AWG | B. Keep the standard spar, 10 AWG, qualify by load-bank test | C. 8 AWG XL-ETFE (GS22759-34-8) |
|---|---|---|---|
| Bundle ampacity | about 48 A per wire [E] | about 33 A on paper [E]; the test decides | about 49 A in the standard spar [E] |
| Bore fit | yes, 15.8 mm [E] | yes | yes, 14.95 mm [E] |
| OD-17 bend channels | meets NASA 3 x OD [E] | meets 3 x OD | **fails NASA 6 x OD**; reopens OD-17 |
| Mass, 4 conductors | 46.69 lbm/1000 ft each (Daburn) [V] | same | 63.3 lbm/1000 ft max each [V]: about 1.95 x /34-10 |
| Cost and schedule | new tube; bonded-joint and stiffness re-check | test rig only | re-draw bend chamber, re-bake pod |

**Recommendation: A, then confirm with B's test.** A keeps the decided OD-17 geometry and the NASA bend rule, and it moves the limit from a roughly 200 deg F resin to the 302 deg F wire rating. B alone is attractive if the thermocouple shows margin. On paper, though, it starts at zero margin against 38 A. **Unverified:** the Tg of the spar actually being procured; the Rock West 400 deg F resin [U]; any stiffness change with a different resin (the spar's 300 MPa allowable is already flagged unverified in the BOM).

### Decision 2: fine-strand Daburn 2621/10 versus coarse-strand 2617/10

| | Daburn 2617/10 (105/30, UL 3212) | Daburn 2621/10 (1092/40, no UL style) |
|---|---|---|
| OD | 0.207 in [V] | 0.223 in [V] |
| Twist clearance left | full 0.059 in (1.5 mm) [E] | **0.051 in (1.3 mm)** [E] |
| Flex claim | none | "designed for continuous flexing applications" (qualitative) [V] |
| Weight, UL listing | 46.69 lbm/1000 ft; UL 3212 [V] | not published; no UL style [V] |

**Recommendation: 2617/10, with the torsion-cycle test as the gate.** 2621/10 fits only if the owner accepts a 13 % cut in twist clearance. Daburn publishes no OD tolerance, so even 1.3 mm is not assured, and there is no sleeve allowance left. If 2617/10 fails the torsion test, 2621/10 is the fallback, together with a request to Daburn for a maximum OD or a thinner-wall variant. **Unverified:** torsion life of either wire; whether the 2621/10 ±OD tolerance exists; TE Raychem 82A0113-10 (665 x 38 XL-ETFE), the only other fine-strand lead, could not be read and is listed as discontinued at DigiKey [U].

### Decision 3: phase-lead conduit enlargement

| | PTFE AT121925 | Silicone Daburn 2616/12 | Braided Daburn 2627/12 |
|---|---|---|---|
| Three-lead bundle, no clearance | about 0.24 in (6.2 mm) [E] | about 0.34 in (8.5 mm) [E] | about 0.38 in (9.6 mm) [E] |
| Suggested conduit | about 0.28 in (7.0 mm) [E] | about 0.37 in (9.5 mm) [E] | about 0.41 in (10.5 mm) [E] |
| Abrasion | worst of the AC ranking [V] | silicone, no data | fibreglass braid |

**Recommendation: AT121925 with the conduit and the stage-2 slot opened to about 0.28 in (7.0 mm).** It is the smallest pod change that carries the current, and the lead runs fixed in a conduit, so flexibility matters less than it does in the spar. If the pod's wall budget allows 0.37 in (9.5 mm), Daburn 2616/12 adds flexibility and publishes a weight. **Unverified:** whether the pod wall around LEAD_CONDUIT_D and LEAD_SLOT_W2/D2 can take the growth; the 0.7 grouping factor; the 176 deg F near-motor ambient.

### Decision 4 — WARNING: branch-fuse rating and coordination

> **WARNING — loss of a fan in hover.** The BOM's FUSE-ESC-40A (Littelfuse 0297040.WXNV, 40 A mini blade) sits **below the 57 A full-throttle draw and only about 5 % above the 37-38 A late-pack hover current** [E]. A fuse that opens in VTOL hover stops one of four fans. That threatens the aircraft. Its BOM note says it "coordinates with 10AWG wire (55A rated)", but that 55 A wire figure is contradicted by the AC chart (about 49 A free air, about 33-48 A in the spar bundle). The coordination basis is invalid.

| | A. Keep 40 A | B. Larger branch fuse, coordinated with wire and ESC limit | C. No branch fuse; rely on the ESC current limit and an upstream fuse |
|---|---|---|---|
| Nuisance opening in hover | likely, late in pack [E] | avoided if its curve carries 38 A continuous and 60 A / 10 s | none |
| Wire protection on a fault | yes | yes, if the curve sits under the wire's short-time capability | lost on a branch short; one fault takes the shared bus |
| Fits mini-blade holder | yes | **unverified**; may need another fuse family (the BOM's deferred ESC-50A row already uses a 60 A MIDI) | n/a |

**Recommendation: B, done as a coordination study, not a part swap.** The fuse must carry 38 A continuous at bay temperature and 57-60 A for 10 s. It must also open before the feed wire is damaged, and with Decision 1 option A the wire is worth about 48 A continuous. Set the ESC's firmware current limit as the overload layer below the fuse. That way the fuse protects against faults rather than trimming peak throttle. The study needs three curves on one plot: the fuse's time-current curve, the wire's short-time rating and the ESC current-limit setting. **Unverified:** the 0297040.WXNV time-current curve and temperature derating (not read); any short-time rating for the candidate wires (none found); the OSESC-NAC current-limit behaviour.

### Decision 5: QF2822 2300 KV listing conflict

| | Use the 2300 KV sheet (as now) | Re-base on the listed 2400 KV |
|---|---|---|
| Source | QX-branded instruction image, REF-EDF-003 [V as read] | QX-Motor product page [V] |
| Peak current | 57 A at 24 V; 60 A / 10 s | 57 A at 22.2 V; 60 A / 10 s |
| ESC recommendation | 80 A | tested with a 60 A ESC |

**Recommendation: keep the 2300 KV figures for sizing and confirm the variant with the vendor or by measuring a delivered motor.** The wire and ESC sizing above holds for either variant, because both peak at 57-60 A. What changes is the thrust-per-amp interpolation behind the 38 A hover figure. The delivered motor must also be measured for lead gauge, length and bullet size, because QX publishes none [V]. **Unverified:** which KV ships under the ordered SKU; hover current for the 2400 KV at 6,500 g AUW.

## What the verified notes overturned

Several figures in the earlier unverified notes did not survive the primary-document check. The verified value governs in each case. The 10 AWG Alpha OD is 0.204 in, not 0.212 in. Alpha 398133 is listed as UL 3213 only. The Glenair maximum weight for /34-8 is 63.3 lbm/1000 ft, not 60.3, and the RS-hosted PDF once cited for /34-8 turned out to be an **AS22759/32 sheet that stops at 12 AWG** ([GS22759-34](https://www.glenair.com/wire-and-cable/pdf/mil-star/gs22759-34.pdf)). Cicoil's single-conductor maximum is 329 deg F (165 deg C), not 500 deg F (260 deg C) ([Cicoil](https://www.cicoil.com/flat-cable/unshielded-cables/hi-flex-unshielded-single-conductor-cable)). NASA's bend minimum for 10 AWG harnesses is 3 x OD, not 6 x. AC altitude derating is Figure 11-6, not 11-4. A fine-strand silicone with a datasheet does exist (Daburn 2621), contrary to the earlier gap note. Values that remain unverified because their hosts blocked automated access are excluded from the specification: TE Raychem 55A0111 and 82A0113, Helukabel M47021, the SAE and DLA slash sheets themselves, and Castle connectors.

## Conclusion

The wire choice was never the real constraint. Verified 10 AWG wires fit the spar, the bend channels and the current. What decides whether the design closes is the system around them: the resin in a carbon tube, the width of a printed conduit, and a 40 A fuse chosen before the aircraft gained weight. Two inherited numbers carried the risk. One was the BOM's "55 A free air" rating for the feed wire. The other was the "28 A hover" current it was checked against. The datasheet re-sizing and the FAA bundle method together cut the margin between them from comfortable to zero.

Two measurements will settle most of the open items: a thermocouple on the spar wall at 38 A sustained, and a 140 deg torsion-cycle run on Daburn 2617/10 over the real spar length. The fuse coordination study is the one item that cannot wait for hardware. Until a fuse curve, the wire's short-time rating and the ESC current limit are plotted together, every hover flight carries a single-point path to losing a fan.
