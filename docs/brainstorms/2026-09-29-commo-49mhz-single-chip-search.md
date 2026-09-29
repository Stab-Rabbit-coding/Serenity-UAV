# Commo 49 MHz Single-Chip Transceiver Search

- **Date:** 2026-09-29
- **Author:** Claude Opus 5.5 (AI research, Anthropic); not human-reviewed
- **Status:** Brainstorm (requirements and options only; nothing implemented,
  no KiCad files touched)
- **Governing rule:** 47 CFR 15.235, 49.82-49.90 MHz [REF-FCC-003]

## Problem

Commo Rev T needs a transmit-and-receive path in 49.82-49.90 MHz for
1200-baud AX.25 (Bell-202 AFSK preferred, or 2-FSK with AFSK framing in the
MSPM0G3519 host). The planned onsemi AX5043 (27-1050 MHz) is discontinued
(datasheet Rev 4, "Document Discontinued", 2026-06-11), so it is rejected.

## Requirements

1. R1 - TX and RX at 49.82-49.90 MHz, emission kept inside the band
   [REF-FCC-003].
2. R2 - 2-FSK or FM able to carry 1200 Bd Bell-202 AFSK.
3. R3 - Part in active production; lifecycle status recorded with source and
   date.
4. R4 - Runs from Commo's 3.3 V / 5 V rails; small and light.
5. R5 (nice to have) - Less FCC test burden: a module with a 15.212 modular
   grant, or a reference design that already has a grant.

## Main finding

As of 2026-09-29 this search found **no in-production single-chip
transceiver whose datasheet covers 49.86 MHz.** The AX5043 was the only one
known, and it is discontinued. Every mainstream sub-GHz transceiver checked
has a lower limit of 80 MHz or more. The search also found **no 49 MHz
module with a modular grant**. The 49 MHz grants that turned up are for
finished products such as toys, not modules. Any option below therefore
means certifying Commo itself under 15.235.

## Ranked candidates

| Rank | Part | Maker | Band coverage | Modulation | TX power | Supply / current | Package | Lifecycle (source, date) | FCC modular grant | AFSK/AX.25 fit |
| ---- | ---- | ----- | ------------- | ---------- | -------- | ---------------- | ------- | ------------------------ | ----------------- | -------------- |
| 1 | CMX994 family (RX) with a separate TX | CML Microcircuits | Datasheet: 100-940 MHz I/Q demodulator, "extended low frequency operation down to 50 MHz"; Table 20 gives a complete receive chain at 50 MHz [1]. Microwave Journal says the CMX994G goes down to 30 MHz [2]. 49.86 MHz is **not** in the CMX994 datasheet. | RX only (I/Q baseband; the MCU or a DSP demodulates) | n/a (RX only) | Single 3.3 V [2]; current requires verification | 40-pin VQFN [2] | Requires verification: cmlmicro.com product page returned 404 on 2026-09-29 | None (RX only; Commo would need its own grant) | Good for RX: I/Q to MCU ADC and software FM/AFSK demodulation. A TX path must be built separately. |
| 2 | Discrete TX (PLL/synth + FM VCO or DDS) with a CMX994G receiver | various | Needs design | FM/AFSK | Set by design; 15.235 field-strength limit | Requires verification | Several ICs | Depends on chosen parts | None | Workable but uses the most board area |
| 3 | Legacy 49 MHz FM transceiver modules (e.g. T5002 walkie-talkie cores [3]) | various (hobby/toy) | 49.86 MHz fixed channel [3] | FM voice (AFSK through the audio path) | about 25 mW (third-party claim [3]) | Requires verification | Module | No OEM lifecycle data found | Only finished-product grants (e.g. a toy TX, FCC ID NLB49028TX [4]); not modular | Voice-FM audio path can carry Bell-202, but there is no datasheet |

## Rejected candidates

| Part | Reason | Source |
| ---- | ------ | ------ |
| onsemi AX5043 | Discontinued (datasheet Rev 4, 2026-06-11) | avionics/datasheets/ax5043-d.pdf |
| ADI ADF7021 / -N / -V | Lowest frequency is 80 MHz (external-inductor VCO) [5]. A third-party copy of an eval-board document says it is NRND (requires verification on analog.com). | [5] |
| ADI ADF7020-1 | 135-650 MHz | [6] |
| ADI ADF7023 / ADF7024 | Sub-GHz ISM only, well above 49 MHz | [7] |
| Silicon Labs Si4463/61/60 | 119-1050 MHz (B1B); rev C2A major bands from 142 MHz | [8] |
| TI CC1020 / CC1021 | 402-470 MHz and 804-940 MHz | [9] |
| onsemi AX5042 | Earlier Axsem UHF part; frequency range and lifecycle require verification; not a lower-frequency successor | [10] |
| TI CC1101/CC13xx, Semtech SX123x | Not checked against datasheets in this pass; reported to start at 287 MHz or higher. Requires verification before they can be ruled out formally. | - |

## Options for the owner

- **A. Direct-sampling SDR on the MCU plus a simple synthesized TX.** No
  RF front-end IC is needed below 50 MHz if a filtered LNA feeds a fast ADC.
  This needs a check of the MSPM0 ADC rate against undersampling at 49.86
  MHz (open question).
- **B. CMX994 receiver plus a discrete TX (Rank 1/2).** The CMX994
  datasheet only characterizes operation down to 50 MHz, and 49.86 MHz is
  just below that, so CML must confirm it before this is designed in.
- **C. Keep searching for a last-time-buy or broker supply of AX5043.** This
  goes against R3 and is not recommended for an actual build.
- **D. Move the link to a band that single-chip transceivers cover.** REF-FCC
  notes in REFERENCES.md already record that other bands were researched and
  rejected on 2026-06-20. Reopening that is the owner's decision.

## Recommendation

No part meets R1+R3+R5 together. Recommended next steps:

1. Ask CML Microcircuits in writing to confirm CMX994G (or /A/E)
   performance at 49.86 MHz and its lifecycle status.
2. In parallel, run a feasibility study of option A or B with a discrete
   15.235-compliant TX.
3. Budget for full 15.235 certification of Commo, because no modular grant
   exists to reuse.

## Open questions

- Q1 - Does CML support the CMX994G at 49.86 MHz, and is it active?
- Q2 - Is ADF7021 NRND on analog.com (not needed for rejection, but should
  be recorded)?
- Q3 - Supply current for the CMX994 in the chosen mode.

## References

1. CML Microcircuits, "CMX994 Direct Conversion Receiver" datasheet
   (3-page summary), <https://www.rfmw.com/datasheets/cml/cmx994ds.pdf>,
   saved as avionics/datasheets/cmx994ds.pdf, retrieved 2026-09-29.
2. Microwave Journal, "CML Family of Direct Conversion Receiver ICs,"
   2020-11-12,
   <https://www.microwavejournal.com/articles/34968-cml-family-of-direct-conversion-receiver-ics>
   (secondary source; verify against the CML datasheet).
3. HFUnderground wiki, "Part 15," <https://www.hfunderground.com/wiki/Part_15>
   (secondary, hobbyist source).
4. FCC ID NLB49028TX (49.860 MHz toy transmitter), mirrored at
   <https://fccid.io/NLB49028TX/Test-Report/Test-Report-3090754>; confirm at
   <https://apps.fcc.gov/oetcf/eas/reports/GenericSearch.cfm>.
5. Analog Devices, ADF7021 datasheet Rev. D,
   <https://www.analog.com/media/en/technical-documentation/data-sheets/ADF7021.pdf>
   (analog.com timed out on direct fetch 2026-09-29; the range was taken from
   the search index of this URL).
6. Analog Devices, ADF7020-1 datasheet Rev. A,
   <https://www.analog.com/media/en/technical-documentation/data-sheets/adf7020-1.pdf>.
7. Analog Devices, ADF7023 datasheet,
   <https://www.analog.com/media/en/technical-documentation/data-sheets/adf7023.pdf>.
8. Silicon Labs, Si4463/61/60-C datasheet,
   <https://www.silabs.com/documents/public/data-sheets/Si4463-61-60-C.pdf>.
9. Texas Instruments, CC1020 product page, <https://www.ti.com/product/CC1020>.
10. onsemi, AX5042 datasheet,
    <https://www.onsemi.com/download/data-sheet/pdf/ax5042-d.pdf>.
11. FCC KDB 996369, Module certification (15.212),
    <https://apps.fcc.gov/oetcf/kdb/forms/FTSSearchResultPage.cfm?id=44637&switch=P>.
