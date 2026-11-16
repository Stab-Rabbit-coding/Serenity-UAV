# Coordinator synthesis (engineering analysis of the verified notes)

Written by the coordinator from project_sizing_basis.md and the four verified_*.md notes. It
combines their figures; it adds no new web sources. Treat as analysis to be checked, with every
input traced to those notes.

## 1. Current cases (from the QX-Motor QF2822-2300KV manufacturer sheet, project_sizing_basis.md)
- Sustained (VTOL hover, the whole mission): 33 A at 24 V, up to about 38 A at 21.0 V late in the pack.
- Peak: 57 A at 24 V full throttle; 60 A / 10 s datasheet limit.
- Phase-lead RMS (ESTIMATE, ideal six-step): about 35 A hover, about 46.5 A full throttle.
- **Owner correction (2026-11-11):** the QF2822-2300KV is the specified motor (owner correction 2026-11-02, REF-EDF-003). No other variant is specified or authorized; the item below is a procurement check only.
- Conflict to flag: the QX-Motor product page lists QF2822 KV options 2200/2400/3500/3800/4300 and
  no 2300 KV (verified_phase_lead.md), while the repository holds a QX-Motor-branded 2300 KV
  instruction-manual image linked from qx-motor.co/product/2365/ (REF-EDF-003). The 2300 KV sheet's
  figures are used here; confirm the variant and its lead gauge with the vendor or a delivered motor.

## 2. Feed ampacity (FAA AC 43.13-1B Chapter 11, verified_faa_nasa.md addendum, raster readings ±5 %)
4 wires in a bundle, 100 % loading curve factor 0.68 (Fig. 11-5), sea level 1.00 (Fig. 11-6):
| Case | Temperature difference | 10 AWG | 8 AWG |
|---|---|---|---|
| Spar-limited: CF-epoxy tube about 200 F (93 C) max, 104 F (40 C) ambient | about 50 C | 49 x 0.68 = **33 A** | 72 x 0.68 = **49 A** |
| Spar not limiting: 150 C wire in 40 C ambient | 110 C | 71 x 0.68 = **48 A** | 107 x 0.68 = 73 A |
Readings run 2-3 % low against the AC's own worked examples. Free-air basis; inside a closed tube the
"ambient" is the tube interior, so AC para 11-66d(5) load-bank/chamber testing applies.
**Conclusion:** with the standard 200 F (93 C) epoxy spar, 10 AWG is exactly at the bottom of the
sustained range and below the 38 A late-pack case; 8 AWG passes; 10 AWG also passes if the spar is a
high-temperature-resin tube (Rock West offers a 400 F (204 C) resin, ampacity_flex_sleeving.md) so that
the 150 C wire rating, not the spar, sets the limit.

## 3. Spar-bore fit (four wires, 2 x 2, circumscribed 2.414 d, plus 2 x 0.059 in (1.5 mm) twist clearance, bore 0.642 in (16.3 mm))
| Wire (verified) | AWG | OD | Bundle + clearance | Fits? |
|---|---|---|---|---|
| Alpha 391000 silicone 105/30 | 10 | 0.204 in (5.18 mm) | 15.5 mm | yes |
| Daburn 2617/10 silicone 105/30 | 10 | 0.207 in (5.30 mm) | 15.8 mm | yes |
| Daburn 2621/10 fine-strand silicone 1092/40 | 10 | 0.223 in (5.66 mm) | 16.7 mm | **no, 0.4 mm over** (fits only if twist clearance is cut to 1.3 mm) |
| GS22759 /34-10 XL-ETFE 37x26 | 10 | 0.134 in (3.40 mm) | 11.2 mm | yes |
| GS22759 /34-8 XL-ETFE 133x29 | 8 | 0.195 in (4.95 mm) | 14.95 mm | yes |
| Alpha 398133 / Daburn 2621/8 silicone | 8 | 0.295 / 0.292 in | 21+ mm | no |

## 4. Bend radius after the spar (as-built channels: 0.65 in (16.5 mm) and 0.87 in (22 mm) centreline)
- NASA-STD-8739.4A Table 7-1 (verified): overall harness AWG 10 or smaller minimum 3 x OD; AWG 8 or
  larger minimum 6 x OD; optimum 10 x OD. OD is the harness OD; for a single wire take the wire OD.
- FAA AC 43.13-1B para 11-117 (verified): at least 10 x OD of the largest wire (6 x at supported breakouts).
| Wire | 3 x OD | 6 x OD | 10 x OD | Meets the 16.5 mm channel at |
|---|---|---|---|---|
| 10 AWG silicone 0.207 in | 15.8 mm | 31.6 mm | 52.6 mm | NASA 3x only |
| 10 AWG XL-ETFE 0.134 in | 10.2 mm | 20.4 mm | 34.0 mm | NASA 3x; AC 6x at 22 mm only |
| 8 AWG XL-ETFE 0.195 in | (n/a: 8 AWG row is 6x) | 29.7 mm | 49.5 mm | **fails NASA 6x** |
**Conclusion:** the decided OD-17 channels meet NASA 3 x OD for 10 AWG only. 8 AWG would need the
bend chamber re-drawn (larger shift), i.e. reopen OD-17. No option meets AC 43.13 10 x OD.

## 5. Recommended feed configuration (for the owner to decide; Owner Decision Brief needed)
- Keep 10 AWG and the OD-17 geometry; **change the spar to a high-temperature-resin CF tube** (or
  prove by a load-bank/thermocouple test that the spar wall stays below its resin limit at 38 A
  sustained), so the 4-wire ampacity is about 48 A.
- Conductor: tinned copper, silicone, 600 V, OD <= 0.207 in (5.26 mm): Daburn 2617/10 (UL 3212, 150 C,
  105/30, 46.69 lbm/1000 ft) or Alpha 391000 (UL AWM 3212, 150 C, 105/30, 0.204 in).
- Torsion: all verified parts that fit have coarse 105 x 30 AWG strands; the fine-strand Daburn 2621/10
  (1092/40) is 0.4 mm too large for the bore with full twist clearance. A torsion-cycle test of the
  chosen wire at 140 deg over the spar length is required either way.
- Abrasion: braided PET sleeve over the bundle in the spar (Techflex PTN0.50, 257 F (125 C),
  datasheet still unverified) and a chamfer or grommet at the spar mouth. Check sleeved OD vs bore.
- No pre-tinning of crimped ends: NASA-STD-8739.4A section 7.2.26 a-c (crimp contacts with stranded
  wire only; solid tinned wire not in crimps) and the Change 1 history entry prohibiting crimping of
  solder-tinned stranded wire; 13.3.1 explains wicking stiffness.
- AC 43.13-1B para 11-66a: no fewer than 19 strands (all candidates comply).

## 6. Phase leads
- Current about 35 A RMS hover, 46.5 A RMS peak; near the motor, assume ambient up to about 176 F (80 C)
  (ESTIMATE). 200 C wire gives about 120 C difference: Fig. 11-4a #12 about 56 A, #14 about 42 A free
  air (interpolated from the 110 C readings, ESTIMATE); with a 3-lead group factor of about 0.7
  (NOT read; between the 4-wire 0.68 and 1.0): #12 about 39 A (passes hover), #14 about 29 A (fails).
- **12 AWG, 200 C rated**: Daburn 2616/12 (UL 3135 silicone, 65/30 tinned, 0.156 in (3.95 mm),
  27.05 lbm/1000 ft) or Alpha AT121925 (SAE AS22759/11 PTFE, 19/25 silver-plated, 0.111 in (2.82 mm)).
  The BOM's WIRE-16AWG phase leads are undersized (16.5 W/m at 35 A RMS).
- Conflict: the pod's stage-1 lead conduit is Dia 0.197 in (5.0 mm); three 12 AWG leads need about
  0.24 in (6.1 mm) (PTFE) or 0.34 in (8.5 mm) (silicone). Conduit enlargement is a pod design change.
- Bullet connectors: Castle 5.5 mm (13-10 AWG, 150 A) / 4 mm (16-13 AWG, 75 A) ratings are retailer
  claims, not verified. QX-Motor does not publish lead gauge, length or connector.

## 7. ESC and protection
- ESC: the manufacturer recommends 80 A; sustained 33-38 A, peak 57-60 A. 80 A settles OD-3 on the
  datasheet; the earlier finding that 50 A sustained is not thermally survivable in the bay stays open.
- **Branch fuse (CAUTION-level finding; reclassified 2026-11-11 per AGENTS.md, aircraft loss without risk to people):** BOM FUSE-ESC-40A (40 A mini blade) is below the 57 A
  full-throttle draw and barely above the 38 A late-pack hover. A fuse opening in hover loses one of
  four fans. The fuse must carry 38 A continuous and 57-60 A for up to 10 s, yet protect a wire whose
  bundle ampacity is about 33-48 A. That needs the fuse time-current curve, the wire short-time
  rating and the ESC's own current limit together; it is an owner decision with a coordination study.
