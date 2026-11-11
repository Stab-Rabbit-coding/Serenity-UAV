# Verified FAA AC 43.13-1B Chapter 11 and NASA-STD-8739.4A (Change 3): wire sizing, derating, bend radius, tinning before crimp

I read both primary documents directly. On 2026-11-11 I downloaded them with curl into the scratchpad (not the repository) and converted them with `pdftotext -layout`. Figures 11-4a, 11-4b, 11-5 and 11-6 are raster graphs, so I rendered PDF pages 522 to 525 to PNG and inspected them by eye.

- **AC 43.13-1B CHG 1:** footer "AC 43.13-1B CHG 1, 9/27/01". Source: https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_43.13-1B_w-chg1.pdf
- **NASA-STD-8739.4A:** cover reads "NASA-STD 8739.4A Change 3, Approved: 2016-06-30". The 2016-06-30 date is the Revision A approval. The history log dates Change 3 to **2021-11-02** ("Revalidated…"). Pages are numbered "N of 114". Source: https://standards.nasa.gov/sites/default/files/standards/NASA/A/3/nasa-std-87394a_w_change_3.pdf

How to read these notes:
- Page numbers are as printed in each document's page footer.
- Temperatures are given in deg F (deg C). Where the source gives deg C only, I converted to deg F, and the converted value is marked "(conv.)".
- These notes supersede the unverified leads in `ampacity_flex_sleeving.md` §1–§3. Corrections to those leads are listed under "Corrections" at the end.

## Q1. AC 43.13-1B Chapter 11: where the ampacity, bundle-derating, altitude-derating and voltage-drop data are, and the values for 8/10/12/14 AWG

### Takeaway
Wire rating is Chapter 11, **Section 5, "Electrical Wire Rating"**, paragraphs **11-66 to 11-69** on pages 11-21 to 11-34a. The data are in these places:
- **Single copper wire in free air:** Figures 11-4a and 11-4b. These are graphs of current against temperature difference (wire rating minus ambient). They are not tables by conductor rating.
- **Bundle derating:** Figure 11-5.
- **Altitude derating:** Figure 11-6.
- **Wire size against voltage drop:** Figures 11-2 (continuous flow) and 11-3 (intermittent flow), with Table 11-6 giving the allowable drop.
- **Table 11-9** is the only tabulated copper ampacity, and it is **not** a free-air rating. It applies to a 33-or-more-wire bundle (9 or more wires for size 8 and larger), 158 deg F (70 deg C) ambient, at most 20 % loading and 60,000 ft. Its values: 10 AWG is 17/26/32 A at 105/150/200 deg C conductor rating, and 8 AWG is 38/57/71 A.

### Cited Findings

**Figure and table titles and page numbers (as printed in the figure captions and the Chapter 11 contents list):**
- Figure 11-2. Conductor chart, continuous flow. Page 11-30. — [AC 43.13-1B CHG 1](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_43.13-1B_w-chg1.pdf)
- Figure 11-3. Conductor chart, intermittent flow. Page 11-31. — [AC 43.13-1B](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_43.13-1B_w-chg1.pdf)
- Figure 11-4a. Single copper wire in free air. Page 11-32. Covers wire sizes 26 to 10; current axis 4–100 A. The chart carries the note "NOT TO BE USED AS SINGLE WIRE" against sizes 26 and 24. — [AC 43.13-1B](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_43.13-1B_w-chg1.pdf)
- Figure 11-4b. Single copper wire in free air. Page 11-33. Covers wire sizes 8 to 4/0; current axis 40–1000 A. — [AC 43.13-1B](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_43.13-1B_w-chg1.pdf)
- Figure 11-5. Bundle derating curves. Page 11-34. Abscissa: "NUMBER OF WIRES IN BUNDLE", 1 to 41. Ordinate: "CURRENT DERATING FACTOR", 0.1 to 1.0. One curve each for "BUNDLE LOADING, PERCENT" of 20, 40, 60, 80 and 100. — [AC 43.13-1B](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_43.13-1B_w-chg1.pdf)
- Figure 11-6. Altitude derating curve. Page 11-34a (and 11-34b). Abscissa: "ALTITUDE (x 1,000 feet)", 0 to 100. Ordinate: "CURRENT DERATING FACTOR", 1.00 down to 0.70. — [AC 43.13-1B](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_43.13-1B_w-chg1.pdf)
- Table 11-6. Tabulation chart (allowable voltage drop between bus and utilization equipment ground). Page 11-21. — [AC 43.13-1B](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_43.13-1B_w-chg1.pdf)
  - 14 V nominal system: 0.5 V continuous, 1 V intermittent.
  - 28 V: 1 V continuous, 2 V intermittent.
  - 115 V: 4 V continuous, 8 V intermittent.
  - 200 V: 7 V continuous, 14 V intermittent.
- Table 11-9. "Current carrying capacity and resistance of copper wire." Page 11-23. Table 11-10 (aluminum) is on page 11-24. — [AC 43.13-1B](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_43.13-1B_w-chg1.pdf)

**Paragraph text that ties each figure to its purpose (para 11-67, page 11-25):**
- 11-67c, "Single Wire in Free Air": "Determining a wiring system's current carrying capacity begins with determining the maximum current that a given-sized wire can carry without exceeding the allowable temperature difference (wire rating minus ambient °C). The curves are based upon a single copper wire in free air. (See figures 11-4a and 11-4b.)" — [AC 43.13-1B, p. 11-25](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_43.13-1B_w-chg1.pdf)
- 11-67d, "Wires in a Harness": "When wires are bundled into harnesses, the current derived for a single wire must be reduced as shown in figure 11-5. The amount of current derating is a function of the number of wires in the bundle and the percentage of the total wire bundle capacity that is being used." — [AC 43.13-1B, p. 11-25](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_43.13-1B_w-chg1.pdf)
- 11-67e, "Harness at Altitude": "Since heat loss from the bundle is reduced with increased altitude, the amount of current should be derated. Figure 11-6 gives a curve whereby the altitude-derating factor may be obtained." — [AC 43.13-1B, p. 11-25](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_43.13-1B_w-chg1.pdf)
- 11-67 lead-in: "In some instances, the wire may be capable of carrying more current than is recommended for the contacts of the related connector. In this instance, it is the contact rating that dictates the maximum current to be carried by a wire." — [AC 43.13-1B, p. 11-25](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_43.13-1B_w-chg1.pdf)
- 11-67b, "Maximum Operating Temperature": "The current that causes a temperature steady state condition equal to the rated temperature of the wire should not be exceeded. Rated temperature of the wire may be based upon the ability of either the conductor or the insulation to withstand continuous operation without degradation." — [AC 43.13-1B, p. 11-25](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_43.13-1B_w-chg1.pdf)

**Table 11-9 (page 11-23), copied exactly for the gauges in scope.** Column heading: "Continuous duty current (amps)-Wires in bundles, groups, harnesses, or conduits. (See Note #1)". Ratings are by wire conductor temperature rating.

| Wire size | 105 °C, 221 °F (conv.) | 150 °C, 302 °F (conv.) | 200 °C, 392 °F (conv.) | Max resistance, ohms/1000 ft at 20 °C, tin-plated | Nominal area, circ. mils |
|---|---|---|---|---|---|
| 14 | 10 | 14 | 18 | 3.06 | 3,831 |
| 12 | 13 | 19 | 25 | 2.02 | 5,874 |
| 10 | 17 | 26 | 32 | 1.26 | 9,354 |
| 8 | 38 | 57 | 71 | 0.70 | 16,983 |

  Source: [AC 43.13-1B, Table 11-9, p. 11-23](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_43.13-1B_w-chg1.pdf)

- Table 11-9 Note #1, verbatim: "Rating is for 70°C ambient, 33 or more wires in the bundle for sizes 24 through 10, and 9 wires for size 8 and larger, with no more than 20 percent of harness current carrying capacity being used, at an operating altitude of 60,000 feet. For rating of wires under other conditions or configurations see paragraph 11-69." Note #2: "For resistance of silver or nickel-plated conductors see wire specifications." — [AC 43.13-1B, p. 11-23](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_43.13-1B_w-chg1.pdf)

**Free-air single-wire values (Figures 11-4a and 11-4b).** These figures are graphs, not tables. The only free-air numbers the AC states in text are its own worked readings. — [AC 43.13-1B, pp. 11-27 to 11-29](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_43.13-1B_w-chg1.pdf)
- **#14, 150 °C temperature difference: 47 A.** Para 11-68e, Example No. 2, step (3): "Follow the 150 °C corresponding horizontal line to intersect with #14 wire size, drop vertically and read 47 Amps" (page 11-27). This is for a wire with a 200 °C rating at 50 °C ambient.
- **#12, 175 °C temperature difference: 68 A; 140 °C temperature difference: 61 A.** Para 11-69b, Example 2, Step 1: "the free air ratings of size #12 are 68 amps and 61 amps, respectively" (page 11-29). These are for 200 °C wire at 25 °C and 60 °C ambient.
- **#20 and #22, 140 °C temperature difference: 21.5 A and 16.2 A.** Para 11-69a, Example 1, Step 1 (page 11-28).
- The AC prints no free-air value for #10 or #8 in text. Reading Figure 11-4a (#10) or 11-4b (#8) at a chosen temperature difference means interpolating a log-scale raster graph. I did not do this, so **no free-air #10 or #8 number is given here.** Read it off the figure for the project's actual temperature difference, and treat the result as a chart reading, not a quotation.

**Bundle and altitude factors stated in the AC's worked examples (pages 11-28 to 11-29):**
- Figure 11-5: 35 wires, 20 % curve gives 0.52 (11-69a, Step 2). 12 wires, 100 % curve gives 0.43 (11-69b, Step 2).
- Figure 11-6: 60,000 ft gives 0.79 (11-69a, Step 4). Sea level gives 1.0 and 20,000 ft gives 0.91 (11-69b, Step 4).
- The AC prints no value for a 4-wire bundle. Figure 11-5 shows all curves starting at 1.0 for 1 wire and falling quickly through 3 to 7 wires. I did not read a 4-wire value off the raster figure.

**Voltage-drop and wire-chart text (paras 11-66 and 11-68, pages 11-21 to 11-27):**
- 11-66b: "The voltage drop in the main power wires from the generation source or the battery to the bus should not exceed 2 percent of the regulated voltage when the generator is carrying rated current or the battery is being discharged at the 5-minute rate." (page 11-21)
- 11-66d(1): values in Tables 11-7 and 11-8 "are for tin-plated copper conductor wires." Tin-plated wire has "slightly higher" resistance than nickel- or silver-plated wire, so the run lengths from the charts are slightly conservative for those platings. (page 11-21)
- 11-66d(4): when the conductor temperature T2 exceeds 20 °C (68 °F, conv.), the run length is shortened from L1 by L2 = (254.5 °C)(L1) / ((234.5 °C) + T2) for copper. The formula is printed exactly like this on page 11-22.
- 11-66d(5): "laboratory testing using a load bank and a high-temperature chamber is recommended. Such tests should be run at anticipated worse case ambient temperature and maximum current-loading combinations." (page 11-22)
- 11-66d(6): T2 = T1 + (TR − T1)(I2/Imax), where T1 is ambient temperature, TR is the conductor temperature rating and Imax is the maximum allowable current at TR. The AC says: "This formula is quite conservative and will typically yield somewhat higher estimated temperatures than are likely to be encountered under actual operating conditions." (pages 11-22 to 11-23)
- 11-68a: "two major requirements must be met": (1) the wire is large enough to prevent excessive voltage drop, and (2) it is large enough to prevent overheating. (page 11-25)
- 11-68 describes Figures 11-2 and 11-3: "The scale on the left of the chart represents maximum wire length in feet to prevent an excessive voltage drop for a specified voltage source system (e.g., 14V, 28V, 115V, 200V)… The scale (slant lines) on top of the chart represents amperes. The scale at the bottom of the chart represents wire gauge." Use 11-2 for continuous flow and 11-3 for intermittent flow, and 11-68d defines intermittent as "(maximum two minutes)". The chart lists voltages of 14, 28, 115 and 200 V only; it has no 25 V column. (pages 11-26 to 11-27)

Source for all of the above: [AC 43.13-1B](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_43.13-1B_w-chg1.pdf)

**Error in the AC itself:** para 11-68e(4) and (5), page 11-27, swap the two figures. It says "Use figure 11-5, left side of chart reads 0.91 for 20,000 feet", which is altitude data, and "Use figure 11-6, find the derate factor for 8 wires in a bundle at 60 percent… 0.6", which is bundle data. The figure captions and para 11-67d/e put bundle derating in Figure 11-5 and altitude derating in Figure 11-6. Para 11-69 uses them that way too. Cite the captions, not 11-68e. — [AC 43.13-1B, p. 11-27](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_43.13-1B_w-chg1.pdf)

**Bend radius in AC Chapter 11 (para 11-117, page 11-51):** "The minimum radii for bends in wire groups or bundles must not be less than 10 times the outside diameter of their largest wire. They may be bent at six times their outside diameters at breakouts or six times the diameter where they must reverse direction in a bundle, provided that they are suitably supported." 11-117a: "RF cables should not bend on a radius of less than six times the outside diameter of the cable." Separately, para 11-137b(2) on page 11-55 says: "Service loop must maintain a minimum bend radius of 3 times the harness diameter." — [AC 43.13-1B](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_43.13-1B_w-chg1.pdf)

### Inferences
- **Table 11-9 does not fit the ESC feed.** It assumes 33 or more wires at 20 % loading, which is a much larger bundle than 4 x 10 AWG. On its face it allows 26 A (150 °C) or 32 A (200 °C) per 10 AWG wire. Both are below the 33–38 A sustained target. Under the same conditions, 8 AWG is rated 57 A (150 °C) or 71 A (200 °C). To size a 4-wire, 100 %-loaded bundle by the AC method:
  1. Read the #10 free-air current from Figure 11-4a at the actual temperature difference (TR − T_ambient).
  2. Multiply by the Figure 11-5 factor at 4 wires on the 100 % curve. All four feed wires carry load, so the 100 % curve applies.
  3. Multiply by the Figure 11-6 factor for the operating altitude.
- **The tube interior is the ambient.** The figures assume free air, and Figure 11-6 assumes loss of convection at altitude only. Inside a sealed carbon-fibre tube, the ambient T1 should be the tube-interior temperature. Para 11-66d(5) recommends a load-bank and chamber test, and the AC's own guidance supports testing as the real basis.
- **The wire charts need adapting to 25 V.** The voltage-drop charts have no 25 V scale. The 28 V scale (1 V continuous drop) is the nearest. Alternatively, compute the drop directly using the Table 11-9 resistance: 1.26 ohm/1000 ft for #10 at 20 °C (68 °F), corrected with the L2 formula.
- **Motor phases.** The AC's #14 example gives 47 A free air at a 150 °C temperature difference. That matches the 47 A RMS peak only for a 392 °F (200 °C) wire at 122 °F (50 °C) ambient in free air, before any bundle derating. Three phase leads routed together are a 3-wire bundle in Figure 11-5.

### Gaps
- Free-air currents for #10 and #8, and Figure 11-5 factors for 3 and 4 wires, are only available graphically. I did not read them off the raster charts, so they are not stated.
- I did not view Figures 11-2 and 11-3 as images, beyond their titles and the paragraph 11-68 description. No run-length values were extracted.

## Q2. AC 43.13-1B: conductor plating temperature limits, and wire for flexing service

### Takeaway
Para **11-77b, "Plating"** (page 11-36) sets the plating limits:
- Tin-coated copper: up to "the limiting temperature of 150 °C" (302 °F, conv.).
- Silver-coated: "where temperatures do not exceed 200 °C (392 °F)".
- Nickel-coated: "retains its properties beyond 260 °C" (500 °F, conv.), but the AC warns that most insulation systems on nickel-plated wire cannot take that long-term.

For flexing service, the AC says to strand the conductor (11-77c) and use no wire with fewer than 19 strands (11-66a). It prefers MIL-W-22759 types "for areas that require repeated bending and flexing" (11-88), and it advises against wire smaller than #20 where there is repeated bending.

### Cited Findings
- 11-77b, verbatim: "Plating. Bare copper develops a surface oxide coating at a rate dependent on temperature. This oxide film is a poor conductor of electricity and inhibits determination of wire. Therefore, all aircraft wiring has a coating of tin, silver, or nickel, that have far slower oxidation rates." — [AC 43.13-1B, p. 11-36](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_43.13-1B_w-chg1.pdf)
  - (1) "Tin coated copper is a very common plating material. Its ability to be successfully soldered without highly active fluxes diminishes rapidly with time after manufacture. It can be used up to the limiting temperature of 150 °C."
  - (2) "Silver-coated wire is used where temperatures do not exceed 200 °C (392 °F)."
  - (3) "Nickel coated wire retains its properties beyond 260 °C, but most aircraft wire using such coated strands have insulation systems that cannot exceed that temperature on long-term exposure. Soldered terminations of nickel-plated conductor require the use of different solder sleeves or flux than those used with tin or silver-plated conductor."
- 11-77c, verbatim: "Conductor Stranding. Because of flight vibration and flexing, conductor round wire should be stranded to minimize fatigue breakage." — [AC 43.13-1B, p. 11-36](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_43.13-1B_w-chg1.pdf)
- 11-77d: "The wire temperature rating is typically a measure of the insulation's ability to withstand the combination of ambient temperature and current related conductor temperature rise." Wires are categorised as suitable for "open wiring" or "protected wiring" by AS50881A Appendix A, Tables A-I and A-II. — [AC 43.13-1B, p. 11-36](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_43.13-1B_w-chg1.pdf)
- 11-66a: "Wire containing less than 19 strands must not be used." Wires smaller than #20 "should not be used in applications where they will be subjected to excessive vibration, repeated bending, or frequent disconnection from screw termination." — [AC 43.13-1B, p. 11-21](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_43.13-1B_w-chg1.pdf)
- 11-88: "Suitable wire types selected from MIL-W-22759 are preferred for areas that require repeated bending and flexing of the wire. Consideration should be made to areas that require frequent component removal or repair. (See table 11-11.)" — [AC 43.13-1B, p. 11-39](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_43.13-1B_w-chg1.pdf)
- Table 11-2b, "Comparable properties of wire insulation systems" (page 11-37), ranks "Flexibility" in the order PTFE, ETFE, COMP, PI (most to least desirable). It ranks "Abrasion resistance" and "Cut-through resistance" with PI first and PTFE last. — [AC 43.13-1B, p. 11-37](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_43.13-1B_w-chg1.pdf)
- 11-118: "Wires connected to movable or shock-mounted equipment should have sufficient length to allow full travel without tension on the bundle." — [AC 43.13-1B, p. 11-52](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_43.13-1B_w-chg1.pdf)

### Inferences
- **Plating is not the limiting temperature.** The prior notes found a roughly 200 °F (93 °C) epoxy limit for the carbon-fibre tube, well below even the 302 °F (150 °C) tin limit. Using 150 °C or 200 °C Table 11-9 columns therefore presumes a conductor temperature that the spar resin would not tolerate where the wire touches the tube wall.
- **Insulation choice for the tilting phase leads involves a trade-off.** Table 11-2b ranks PTFE most flexible but worst for abrasion and cut-through. The AC gives no flex-cycle data.

### Gaps
- The AC gives no flex-life numbers, strand-count recommendations beyond the 19-strand minimum, or torsion guidance.

## Q3. NASA-STD-8739.4A Change 3: §7.2.19, Table 7-1 bend radii, and the tinning-before-crimp clause

### Takeaway
§7.2.19 (page 29 of 114) says Table 7-1 applies to bending in the installed harness or cable. Table 7-1 is on page 30 of 114:
- Overall harness with AWG 10 or smaller, no coaxial cable: optimum 10 x OD, **minimum 3 x OD**.
- Overall harness with AWG 8 or larger (or with coaxial cable): optimum 10 x OD, **minimum 6 x OD**.
- Anything with polyimide (Kapton) insulation: optimum 15 x OD, minimum 10 x OD.

OD is footnoted only as "Outside Diameter (OD)". Because the rows are "Overall harness", it is the harness OD. The Change 3 body text on crimping is **§7.2.26 a–c** (page 29 of 114). It forbids solid wire and "Solid, tinned wire" in crimped contacts. The explicit sentence "Crimping of solder tinned stranded wire is prohibited" appears **only in the Document History Log**, as a Change 1 (2006-01-27) edit to the old "Para 4.3 No. 4". I could not find it in the body of the Change 3 text.

### Cited Findings
- §7.2 (page 28 of 114), "Design Considerations": "The following considerations shall be taken in any interconnecting cable or harness design and incorporated into the design as applicable." — [NASA-STD-8739.4A Chg 3](https://standards.nasa.gov/sites/default/files/standards/NASA/A/3/nasa-std-87394a_w_change_3.pdf)
- **§7.2.19**, verbatim: "The bend radius data given in Table 7-1 shall apply for bending that occurs in the installed interconnecting harness or cable." (page 29 of 114) — [NASA-STD-8739.4A Chg 3](https://standards.nasa.gov/sites/default/files/standards/NASA/A/3/nasa-std-87394a_w_change_3.pdf)
- **Table 7-1, "Bend Radii for Completed Interconnecting Cable or Harness"** (page 30 of 114; the contents list also gives page 30). In the PDF the caption has a broken field and prints as "Table Error! No text of specified style in document.-1". The rows, verbatim:

| Wire or Harness Type | Optimum Bend Radius | Minimum Bend Radius |
|---|---|---|
| Individual coaxial cable. | 10 x OD 1/ | 6 x OD |
| Polyimide (Kapton) insulated | 15 x OD | 10 x OD |
| Overall harness (with coaxial cable or AWG size 8 or larger). | 10 x OD | 6 x OD |
| Overall harness (with AWG size 10 or smaller without coaxial cable). | 10 x OD | 3 x OD |
| Overall harness (with polyimide insulated wires included). | 15 x OD | 10 x OD |

  Footnote: "1/ Outside Diameter (OD)". The acronym list (page 17 of 114) also defines "OD — Outside Diameter". — [NASA-STD-8739.4A Chg 3, p. 30](https://standards.nasa.gov/sites/default/files/standards/NASA/A/3/nasa-std-87394a_w_change_3.pdf)
- **§7.2.26**, verbatim (page 29 of 114): "The following requirements apply for crimped connections. a. Crimped contacts shall be used with stranded wire only. b. Solid wire shall not be used with crimped contacts. c. Solid, tinned wire shall not be used in crimped contacts." — [NASA-STD-8739.4A Chg 3](https://standards.nasa.gov/sites/default/files/standards/NASA/A/3/nasa-std-87394a_w_change_3.pdf)
- **Document History Log**, Change 1, 2006-01-27 (page 2 of 114), verbatim: "Para 4.3 No. 4: Change sentence to 'Crimping. Stranded wire shall be used for crimping. Crimping of solid wire is prohibited. Crimping of solder tinned stranded wire is prohibited.'" This entry records a change to the pre-Revision-A baseline. In Revision A, Change 3, §4 is "General" (§4.1 onward) and does not contain this sentence. A text search of the whole Change 3 document for "solder tinned", "tinned stranded" and "Stranded wire shall be used" found it only in the history log. — [NASA-STD-8739.4A Chg 3](https://standards.nasa.gov/sites/default/files/standards/NASA/A/3/nasa-std-87394a_w_change_3.pdf)
- Revision A, 2016-06-30: "Synchronized requirements with NASA-STD-8739.6". Change 3 is 2021-11-02, described as: "Revalidated with change to: a. Replace references to NPD 8730.5… b. Add Section 2.3 Order of Precedence. c. Include other editorial edits to Chapter 1, Chapter 2, and Chapter 3" (page 6 of 114). — [NASA-STD-8739.4A Chg 3](https://standards.nasa.gov/sites/default/files/standards/NASA/A/3/nasa-std-87394a_w_change_3.pdf)
- **Related clauses in the same standard:**
  - §13.3.1 (pages 62 to 63 of 114), on solder-type connectors: "Wire shall be bent only in flexible, unwicked parts of the conductor to maintain stress relief for solder dipped conductors. In all instances, stranded conductors will experience solder-wicking during attachment. The conductor will be rigid up to the point where the wicking stops and flexible beyond it. Wire movement concentrates stress at the point where wicking stops and normal harness handling can produce conductor fatigue and failure."
  - §7.2.18: "The length of lay for each twisted layer shall be between 8 and 16 times the outer diameter of the harness."
  - §7.2.11: harnesses shall be protected "from abrasion, cold flow, cut through, vibration, chafing, flexing, and sharp edges".
  - §7.2.36: "Splices shall not be located in areas of the cable where flexing may occur…"
  
  Source: [NASA-STD-8739.4A Chg 3](https://standards.nasa.gov/sites/default/files/standards/NASA/A/3/nasa-std-87394a_w_change_3.pdf)

### Inferences
- **Bend radius for the 4 x 10 AWG feed bundle.** This bundle has no coax and no wire of 8 AWG or larger, so it falls in the "AWG size 10 or smaller" row: minimum 3 x harness OD, optimum 10 x OD.
  - At the 0.5–0.6 in (12.7–15.2 mm) bundle OD from the prior notes, the minimum is about 1.5–1.8 in (38–46 mm) and the optimum about 5–6 in (127–152 mm).
  - If the conductors are polyimide (Kapton) insulated, the polyimide row applies instead: 10 x OD minimum, about 5–6 in (127–152 mm).
  - The prior notes' "6 x OD" figure applies only to the AWG 8-or-larger, coax or individual-coax rows.
  - If the feed is upsized to 8 AWG, the minimum becomes 6 x OD, about 3.0–3.6 in (76–91 mm).
- **AC and NASA bend radii differ.** The AC's para 11-117 (10 x OD of the largest wire, 6 x OD at supported breakouts) uses individual-wire OD. NASA Table 7-1 uses harness OD. Cite both and state which basis each uses.
- **Tinning before crimp.**
  - The Change 3 body clause §7.2.26c, read literally, prohibits *solid, tinned* wire. It does not explicitly name *solder-tinned stranded* wire.
  - The explicit prohibition on stranded wire is documented only in the history log as a Change 1 edit to the old para 4.3.
  - §13.3.1 gives the mechanism: solder wicking makes the conductor rigid and concentrates flex stress where the wicking stops.
- **Recommendation for the spec:** cite §7.2.26a–c as the current clause and add "do not solder-tin stranded conductors before crimping". Support that with the history-log Change 1 sentence and §13.3.1, so the spec does not claim the current body text contains a stranded-wire prohibition that it does not.

### Gaps
- NASA-STD-8739.4A has no current-carrying capacity or derating tables. I did not open NASA-STD-8739.6 or J-STD-001FS, which Revision A says it synchronised with, to see whether either carries the stranded-wire tinning prohibition.

## Corrections to the earlier unverified notes (`ampacity_flex_sleeving.md`)

- **Figure numbers.** Figure 11-5 is bundle derating (confirmed). Figure 11-6, not 11-4, is altitude derating. Figures 11-4a and 11-4b are single copper wire in free air. Figures 11-2 and 11-3 are conductor charts for continuous and intermittent flow.
- **Wire tables.** Tables 11-11 (Open Wiring, page 11-40) and 11-12 (Protected Wiring, page 11-41) list acceptable wire types. The ampacity table is Table 11-9.
- **Plating limits.** The AC confirms tin at 150 °C (302 °F) and silver at 200 °C (392 °F). For nickel it says "beyond 260 °C" (500 °F), qualified by the insulation limit.
- **NASA bend radii.** "6 x OD (10 x OD Kapton)" is incomplete. For an overall harness of AWG 10 or smaller without coax, Table 7-1 gives minimum 3 x OD and optimum 10 x OD. 6 x OD applies to AWG 8 and larger, or to harnesses containing coax. Table 7-1 is on page 30 of 114 in Change 3, not page 36.
- **Tinning clause.** The workmanship-site quote ("crimping of… stranded wire that has been solder tinned, is prohibited") matches the Change 1 history-log wording. The current body clause is §7.2.26c, "Solid, tinned wire shall not be used in crimped contacts."
