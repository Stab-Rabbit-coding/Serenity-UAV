# Pilot documentation set

Prepared 2026-10-19 by Claude Sonnet 5.5 (Anthropic) for sgriffing. License CC BY-SA 4.0.

| Document | Content |
| --- | --- |
| [Pilot-ICD-External.md](Pilot-ICD-External.md) | Interface control: the eight cable / field connectors |
| [Pilot-ICD-PB2I.md](Pilot-ICD-PB2I.md) | Interface control: the two PocketBeagle 2 Industrial rails |
| [Pilot-HDD.md](Pilot-HDD.md) | Hardware design description |
| [Pilot-Manufacturing-Transfer.md](Pilot-Manufacturing-Transfer.md) | Sunstone fab package and Cyber City assembly data |
| [Pilot-Design-Review.md](Pilot-Design-Review.md) | Gates, findings, owner decisions |
| `figures/` | kidoc renders: architecture, bus topology, EMC severity, schematic SVG |
| `analysis/` | analyzer JSON used for the figures and counts |

The ICD tables are generated, not typed:

```bash
python3 avionics/kicad/Pilot/scripts/gen_pilot_icd.py
```

The analysis and figures come from the kidoc and kicad skills (`kidoc_scaffold.py --type icd
--schematic-json ... --pcb-json ... --emc-json ... --thermal-json ...`). The kidoc ICD scaffold
itself (`Pilot-ICD.md` in earlier drafts) was discarded: it listed ICs as connectors, left direction and
level blank and printed `__unnamed_n` nets. PDF output needs kidoc's venv (`kidoc_venv.py` writes it
inside the project, so build it outside the repository tree).
