# Harness ampacity, derating, flex life, plating limits and abrasion sleeving (4 x 10 AWG ESC feed in 0.64 in (16.3 mm) ID CF spar; 12/14 AWG motor phases)

> **Access limitation (read first).** In this research session the network proxy blocked
> `www.faa.gov` and `standards.nasa.gov` (DNS ENOTFOUND for both; `curl` got proxy 403), so
> **neither FAA AC 43.13-1B nor NASA-STD-8739.4A Change 3 was read.** No paragraph, table,
> figure or clause number below has been verified against a primary document unless it is
> marked VERIFIED, and none is. Every number is cited to the secondary or manufacturer
> source it came from. To close this, allow `www.faa.gov` and `standards.nasa.gov` in the
> session's network settings and re-read:
> - https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_43.13-1B_w-chg1.pdf
> - https://standards.nasa.gov/sites/default/files/standards/NASA/A/3/nasa-std-87394a_w_change_3.pdf
>
> Two copies of the FAA text are published elsewhere and could be read instead, but I did not
> fetch them: a FAASafety.gov Chapter 11 extract
> (https://www.faasafety.gov/files/events/SO/SO35/2020/SO35100907/AC_43.13_Chapter_11_Electrical.pdf)
> and a third-party mirror (https://rivetbangers.com/documents/AC43.13-1b.pdf).
> All findings below come from search-result summaries. They are leads, not verified quotes.

## 1. SAE AS50881 and FAA AC 43.13-1B: single-wire and bundle ampacity, bundle and altitude derating

### Takeaway
SAE AS50881 is paywalled, and the FAA and NASA hosts were blocked, so no table or figure number could be checked. Secondary sources agree on the method: start from the free-air rating for the gauge, then multiply by a bundle-derating factor (set by wire count and percent loading) and an altitude factor (curves up to about 100,000 ft). They also agree that the AS50881 curves are conservative in general but not in every case.

### Cited Findings
- AS50881 gives "a conservative estimate" for bundle and altitude derating that "may be used as a universal reference point". A specific assembly should ideally be evaluated on its own. The main derating factors are bundle size, altitude and source frequency. Glenair's explanation: once wires touch each other they lose the ability to shed heat, and this is worst at the centre of a large bundle. — [Glenair Air Taxi Interconnect catalog](https://catalogs.glenair.com/view/1063911466/13/)
- Lectromec summarises the AS50881 method as I = H·I_g(x): allowable current equals an altitude factor times the current for the same gauge at standard conditions. The curves assume the ambient temperature at altitude, so a temperature-controlled bay needs recalculating. AS50881 covers altitudes up to about 100,000 ft. — [Lectromec derating tool tutorial](https://lectromec.com/lectromec-derating-tool-tutorial-ewis/); [Lectromec](https://lectromec.com/?p=339)
- A Fokker Elmo thermal model was compared with new lab data and with the AS50881 formulas. For a **single wire in air**, some gauge and current combinations in the AS50881 curves underestimated the heat generated, even though the curves have "historically been viewed as being conservative". — [NLR report](https://reports.nlr.nl/bitstreams/918226f2-467e-4b8f-8ed6-4c3c29e22ff4/download)
- NASA notes that the standard derating procedure does not fully cover insulation type and thickness, varying ambient temperature, different conductor materials, different bundle loadings, mixed wire sizes or vacuum. NASA proposes a generalised bundle model that includes wire-to-wire conduction and radiation. — [NASA NTRS 20160011474](https://ntrs.nasa.gov/api/citations/20160011474/downloads/20160011474corrected.pdf); [NASA NESC Academy, wire derating](https://www.nasa.gov/learning-resources/for-professionals/courses-curriculums/nasa-engineering-safety-center-academy/re-architecting-the-nasa-wire-derating-approach)
- Rickman and Iannello (WIT Transactions) define "ampacity" as the current-carrying capacity of wires singly or in bundles. Their keywords include AS50881. — [WIT Press](https://www.witpress.com/elibrary/wit-transactions-on-engineering-sciences/106/35795)
- **AC 43.13-1B (secondary source only, NOT VERIFIED):** an exam-prep study guide says bundled wire is derated using **Figure 11-5**, as a function of wire count and percent of bundle capacity used, and that the wire tables are **Tables 11-11 and 11-12**. A trade-magazine article also calls Figure 11-5 the bundle-derating curves. — [open-exam-prep, 10.3 Electrical Wire Sizing](https://open-exam-prep.com/study-guides/faa-ia-inspection/hardware-systems-standards/electrical-wire-sizing-load); [Avionics News, July 2020, p. 75](https://www.nxtbook.com/allen/avne/57-7/index.php?startid=75)
- A training deck states that the continuous current ratings in the AC 43.13-1B tables and figures "were derived only for wire application", not for connectors or terminals. — [Scribd, Aircraft Wiring Practice](https://www.scribd.com/doc/279927351/Aircraft-Wiring-Practice)
- A DTIC report on steady-state current and temperature rise in uniform aircraft-cable bundles exists. It is a possible free primary dataset. — [DTIC AD1216673](https://apps.dtic.mil/sti/html/trecms/AD1216673/index.html)

### Inferences
- With 4 conductors in a closed CF tube, the bundle has little convective cooling. The tube wall, not free air, sets the ambient, so a free-air single-wire rating should not be used for 33–37 A sustained per 10 AWG conductor.
- Because NLR found single-wire-in-air cases where AS50881 is not conservative, a measured temperature-rise test of the real 4 x 10 AWG bundle inside the real spar tube is the defensible basis for qualification. Standards-based derating alone is not enough.

### Gaps
- None of the following were read or verified: AS50881 table and figure numbers, its free-air ampacity values for 10/12/14 AWG, and its bundle and altitude factors. The standard is paywalled at sae.org and the abstract page was not fetched.
- The AC 43.13-1B paragraph numbers, the Figure 11-2/11-3 wire-chart content, and which of Figures 11-4 and 11-5 is bundle derating versus altitude derating are unverified, because faa.gov was blocked. The secondary claim above ("Figure 11-5 = bundle derating") must be checked before it is cited.

## 2. Conductor plating temperature limits (tin, silver, nickel)

### Takeaway
The usual industry limits are about **302 °F (150 °C) for tin-coated copper, 392 °F (200 °C) for silver-plated and 500 °F (260 °C) for nickel-plated**. The source found is a conductor manufacturer (Fisk Alloy), not the ASTM standards. ASTM B33, B298 and B355 define the coatings themselves, and the search results did not show those standards assigning temperature ratings.

### Cited Findings
- Tin coating "is generally recognized to increase the operating temperature of copper conductors to 150 ºC". Silver plating raises it to 200 ºC and nickel plating to 260 ºC. Tin and copper form intermetallic compounds even at room temperature, which degrades solderability over time. — [Fisk Alloy, Conductor Facts (electroplating)](https://fiskalloy.com/conductor-facts/electroplating/); [Fisk Alloy, solderability](https://fiskalloy.com/conductor-facts/solderability/)
- ASTM B33 covers tin-coated copper, B298 silver-coated and B355 nickel-coated. The ASTM B286 hook-up-wire specification calls up B33, B189, B298 and B355 for conductor coatings. — [Fisk Alloy, Conductor Facts](https://fiskalloy.com/conductor-facts/electroplating/); [ASTM B286-07(2017) sample](https://cdn.standards.iteh.ai/samples/97227/1beee673316a4a37b583a2853f7897e5/ASTM-B286-07-2017-.pdf)
- A study-guide summary of AC 43.13-1B describes M22759/34 as a tin-plated, 150 °C (302 °F) XL-ETFE wire. This is NOT VERIFIED against the AC. — [open-exam-prep](https://open-exam-prep.com/study-guides/faa-ia-inspection/hardware-systems-standards/electrical-wire-sizing-load)

### Inferences
- In this application the conductor plating is not the limiting temperature. Even tin-coated copper at 302 °F (150 °C) is well above the spar epoxy's roughly 200–225 °F (93–107 °C) rating (section 5). The tube wall therefore governs.

### Gaps
- The ASTM B33, B298 and B355 abstract pages were not read, so it is not known whether the ASTM texts state any temperature. SAE AS22759 (paywalled) was not read for per-slash-sheet plating and temperature pairings. The AC 43.13-1B plating-temperature text was not read.

## 3. NASA-STD-8739.4A: bend radius (Table 7-1, §7.2.19) and pre-tinning stranded wire before crimping

### Takeaway
The standard could not be fetched, so no clause was read or quoted. NASA workmanship pages derived from the standard say solder-tinned stranded wire must not be crimped, and they give cable bend radii of 6 x OD (10 x OD for Kapton-insulated). Neither is verified against Table 7-1 or §7.2.19 of Change 3.

### Cited Findings
- A table of contents found by search lists **Table 7-1 "Bend Radii for Completed Interconnecting Cable or Harness"** (shown on p. 36 in one edition). The table values were not seen. — search-result summary only; source PDFs: [corpora.tika govdocs 407911](https://corpora.tika.apache.org/base/docs/govdocs1/407/407911.pdf), [Scribd copy](https://www.scribd.com/document/676886244/CABLES-87394)
- From the NASA workmanship appendix: crimping is for stranded wire only, and "crimping of solid wire, and stranded wire that has been solder tinned, is prohibited". A Marshall Space Flight Center (MSFC) tailoring guide adds that wires for crimp terminations "shall not be tinned". — [NASA Workmanship, Appendix](https://workmanship.nasa.gov/lib/insp/2%20books/links/sections/Appendix.html); [NASA Workmanship, Crimped terminations](https://workmanship.nasa.gov/lib/insp/2%20books/links/sections/210%20Shield%20Crimps.html)
- Also from NASA workmanship pages: cables insulated with materials other than Kapton "shall not be bent less than six outer diameters", and Kapton-insulated cables not less than ten outer diameters. Flexible coax has a minimum inside bend radius of 6 diameters, and semi-rigid or rigid coax 2 diameters. — [NASA Workmanship, Coaxial](https://workmanship.nasa.gov/lib/insp/2%20books/links/sections/404%20Coaxial.html); [workmanship section 403](https://workmanship.nasa.gov/lib/insp/2%20books/links/sections/files/403.pdf)

### Inferences
- If the 6 x OD rule applies to the finished 4 x 10 AWG bundle (about 0.5–0.6 in OD from the brief), the minimum bend radius is about 3.0–3.6 in (76–91 mm). Check this against the spar entry and exit geometry once Table 7-1 is verified.
- Do not pre-tin the 10/12/14 AWG strands before crimping ESC or motor terminals. This is consistent with the NASA workmanship guidance above.

### Gaps
- The exact wording and clause numbers of Table 7-1 and §7.2.19 in the 2016 Change 3 edition, and the clause number of the tinning prohibition in the standard itself, are not verified because standards.nasa.gov was blocked.

## 4. Torsional and flex life versus strand diameter and lay

### Takeaway
No primary, quantitative dataset (cycles versus strand diameter) was found for copper conductors. Manufacturers state qualitatively that finer and more numerous strands raise flex life. A cable maker notes that **torsion behaves differently from bending**: torsion life depends on long lay length and a torsionally balanced construction, not only on fine strands. Alpha Wire also says its flex-test cycle counts cannot be translated into service life.

### Cited Findings
- Alpha Wire lists flex-life classes of roughly 1 million cycles (standard flex series) up to 14 million (85000 continuous-flex series) and 6 million (86000 series). A torsion series is listed at about 1 million cycles, but that table is garbled in the source. — [Alpha Wire via element14, High-Flex / Torsional-Flex / Continuous-Flex](https://community.element14.com/products/manufacturers/alphawire/w/documents/3091/high-performance-flexibility-alpha-wire-s-xtra-guard-flex-cable-series-alpha-connect); [Alpha Wire "To Flex" PDF](https://eproc-my.element14.com/wcsstore/ExtendedSitesCatalogAssetStore/cms/asset/images/common/storefront/alpha-wire/To-Flex.pdf)
- Alpha Wire has stated there is "no way, at this time, to relate flex test performance to cable life", and that its protocol is more severe than most C-track (cable-carrier) use. — [Alpha Wire "To Flex"](https://eproc-my.element14.com/wcsstore/ExtendedSitesCatalogAssetStore/cms/asset/images/common/storefront/alpha-wire/To-Flex.pdf)
- Pelican Wire, a custom-wire vendor: finer strands lower the strain per cycle, and going from 7 to 19 to 37 strands raises flex life. This is a qualitative vendor claim. — [Pelican Wire, high-flex robotics wire](https://pelicanwire.com/industries/high-flex-robotics-wire/)
- A copper-conductor maker: robot torsion calls for longer lay lengths and a torsionally balanced construction. The "shorter lay is better for bending" rule does not carry over to torsion. — [JT Copper article](https://en.jtcopper.com/why-can-robot-cables-bend-millions-of-times-without-breaking-the-real-challenge-is-not-the-jacket-but-the-copper-wire-structure.html)
- General high-flex failure guidance from distributors (IEWC, DigiKey) is available but was not read in full. — [IEWC, Optimize the lifespan of high-flex cables](https://www.iewc.com/resources/educational-resources/optimize-the-lifespan-of-your-high-flex-cables); [DigiKey, Five reasons for premature failure of high-flex cable](https://www.digikey.dk/da/blog/five-reasons-for-premature-failure-of-high-flex-cable)
- Wire-rope fatigue literature (DTIC) found that load range, construction and core dominate fatigue, and that wire-level fatigue does not predict rope-level fatigue. The steel-rope data do not transfer directly to copper. — [DTIC ADA026115](https://apps.dtic.mil/sti/pdfs/ADA026115.pdf); [DTIC AD0743924](https://apps.dtic.mil/sti/pdfs/AD0743924.pdf)

### Inferences
- A 140° twist per tilt cycle is torsion. Spreading that twist over the longest free length available in the spar lowers shear strain per unit length. Choose a torsion-rated, fine-strand, rope-lay conductor with a long lay, and qualify it by testing the actual twist angle and length for the required cycle count.

### Gaps
- No published cycles-versus-strand-diameter curve for copper in torsion was found. No UL or SAE torsion test standard for hook-up wire was identified.

## 5. Service temperature of roll-wrapped carbon-fibre-epoxy tubes

### Takeaway
Standard epoxy CF tubes from these vendors are rated at only about **200–238 °F (93–114 °C)**. Rock West gives "Max Operating Temp (Tg) 200–224 °F" for its standard filament-wound carbon tubes. DragonPlate gives 200 °F (93 °C) maximum for its standard tubes. Both offer high-temperature resins, up to 400 °F (204 °C) at Rock West and 500 °F (260 °C) phenolic at DragonPlate. No roll-wrapped carbon tube Tg was found directly.

### Cited Findings
- Rock West build-your-own filament-wound carbon tube: "Temperature Rating (F) 225.0", "Max Operating Temp (Tg) 200F to 224F" (93–107 °C). A higher-Tg resin "good for up to 400F" (204 °C) is available. — [Rock West, filament-wound BYOT](https://www.rockwestcomposites.com/byot-fw.html); [Rock West, filament-wound carbon fiber tubes](https://www.rockwestcomposites.com/filament-wound-carbon-fiber-tubes)
- Rock West roll-wrapped **fiberglass** tube 0.25 x 0.32 x 60 in (EHM32 resin): "Temperature Rating (F) 238.0", Tg 225–249 °F (107–121 °C). This is the closest roll-wrapped data point found. — [Rock West 45161-FG](https://www.rockwestcomposites.com/45161-fg.html)
- DragonPlate standard tube (0.375 in OD x 0.290 in ID): "Max Temperature 200 F" (93 °C). The high-temperature phenolic-prepreg tubes are rated to 500 °F (260 °C). — [DragonPlate 0.375 OD tube](https://dragonplate.com/dragonplate-carbon-tube-375od-x-290id-x-48); [DragonPlate high-temperature tube](https://dragonplate.com/high-temperature-carbon-fiber-round-tube-2-id-x-48)

### Inferences
- Use about 200 °F (93 °C) as the allowable spar-wall temperature, and apply a margin below Tg because stiffness falls before Tg. The bundle's temperature rise at 37 A sustained and 57 A peak, plus the hottest ambient, should keep the tube wall comfortably below this. The tube is the limiting material, not the 302 °F (150 °C) tin plating or the 257 °F (125 °C) PET sleeving.

### Gaps
- The Tg of the exact roll-wrapped carbon tube used for the spar, and which Tg test method each vendor quotes (DMA or DSC), are not known. Ask the vendor for its resin datasheet.

## 6. Abrasion and cut-through sleeving for a 0.5–0.6 in bundle

### Takeaway
1/2 in (13 mm) braided PET is the common fit, with an expansion range of about 1/4–3/4 in (6–19 mm). Examples are Techflex Flexo PET PTN0.50 and Tenneco (formerly Federal-Mogul) Roundit 2000, size 13 mm. Both are rated to about **257 °F (125 °C)**. Nomex sleeving (Techflex NXN, Roundit 2000 NX) is rated higher, but the Techflex Nomex sheet reports **low** abrasion resistance on a Taber test.

### Cited Findings
- **Techflex Flexo PET PTN0.50:** −94 °F to 257 °F (−70 °C to 125 °C), expansion 1/4 in min to 3/4 in max, 10 mil PET monofilament. The spec sheet lists UL 94 V-0, FAR 25 and FMVSS 302. — [AWC, PTN0.50](https://www.awcwire.com/product/ptn0-50); [Flexo PET spec sheet (CableOrganizer)](https://www.cableorganizer.com/cdn/shop/files/Flexo_PET.pdf); [DigiKey PTN0-50BK500](https://www.digikey.com/en/products/detail/techflex/PTN0-50BK500/2502451). Del City lists −103 °F to 257 °F (−75 °C to 125 °C) — [Del City PTN0.50BK](https://delcity.net/catalogdetails?item=844). GlobalSpec lists −67 °F to 275 °F (−55 °C to 135 °C) but also names nylon and polyolefin, so that record looks mismatched — [GlobalSpec](https://datasheets.globalspec.com/ds/techflex/ptn0-50bk/9c005f4a-0fe1-4921-bcc7-5d1990337729)
- **Techflex Flexo Tight Weave PTT0.50** (denser PET weave) is also sold in 1/2 in. Its temperature rating was not read. — [Del City PTT0.50BK](https://www.delcity.net/catalogdetails?item=32103)
- **Roundit 2000 (PET wrap-around split sleeve), 13 mm:** a reseller gives −85 °F to 257 °F (−65 °C to 125 °C). The V0 sheet gives a 13 mm (1/2 in) nominal size, an 8–13 mm (5/16–1/2 in) application range, 0.009 in wall and 50 m (164 ft) packaging. — [Xtramotorsport](https://xtramotorsport.com/product/roundit-2000-13-mm/); [IEWC Roundit 2000 sheet](https://media.iewc.com/SpecificationSheets/ROUNDIT2000.pdf); [Roundit 2000 V0 PDF](https://www.expresselectrical.co.uk/files//0c716662-da6a-4fc4-9d45-a92300e0e38b/Roundit%202000%20V0.pdf)
- **Roundit 2000 NX (Nomex) wrap:** −76 °F to 392 °F (−60 °C to 200 °C). — [Hilltop Products, Roundit 2000 NX HT 13](https://hilltop-products.co.uk/cable-management/cable-tidies-rapstrap-velcro-and-more/roundit-2000/round-it-2000-nx-ht-13-0-5-sp.html); [IEWC Roundit 2000 NX sheet](https://media.iewc.com/SpecificationSheets/ROUNDIT%202000%20NX.pdf)
- **Techflex Flexo NX (Nomex) NXN:** melt point 662 °F (350 °C) per ASTM D2117. This is a melt point, not a continuous rating. Minimum continuous is −76 °F (−60 °C). Abrasion resistance is "Low" (Taber 5150), and Flexo Aramid is "Medium" on the same test. A 1/2 in size (NXN0.50) exists. — [IEWC NXN0.38 data sheet](https://media.iewc.com/SpecificationSheets/NXN0.38%20-%20Data%20Sheet.pdf); [NXN0.50 datasheet](https://datasheet.chipsmall.com/NXN0-50GN/339052.pdf)

### Inferences
- For abrasion inside the spar and at the pivot, braided PET (PTN or tight-weave PTT) or Roundit 2000 is a better choice than Nomex, given Techflex's own "Low" Taber abrasion rating for Nomex. The 257 °F (125 °C) PET rating is above the spar epoxy's roughly 200 °F (93 °C) limit, so the sleeve is not the thermal constraint. A 1/2 in PET braid expanded to 0.5–0.6 in leaves room under its 3/4 in maximum. Check that the sleeved OD still clears the 0.64 in (16.3 mm) tube ID.

### Gaps
- No PTFE sleeving, Alpha Wire FIT or TE sleeving datasheets were retrieved. No cut-through test data were found for any sleeve. No Techflex Nomex maximum continuous temperature was found.
