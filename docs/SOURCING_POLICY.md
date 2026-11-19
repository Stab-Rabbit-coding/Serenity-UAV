# Component Sourcing and Openness Policy

**Revision:** Rev U, 2026-11-17. **Status:** in force (owner rule, 2026-10-17).
**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP (owner). Text moved verbatim from root
`AGENTS.md` §5 by Claude (Anthropic) at the owner's direction, 2026-11-17 (AGENTS.md review,
Q6: design narrative moves to the owning document; root keeps the gate).
**License:** CC BY-SA 4.0 — see LICENSES/CC-BY-SA-4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)

These rules gate every part selection, on every board, before a part enters a schematic or BOM.
A part that fails either rule **shall not** be designed in. Existing parts that fail are
replaced and tracked in the owning WBS.

- **No restricted-country silicon.** No integrated circuit, discrete semiconductor, or
  semiconductor-bearing module shall be used whose manufacturer (the design owner / brand of
  record) meets any of the following:
    - It is domiciled in a restricted country: the People's Republic of China (including Hong
      Kong and Macau), the Russian Federation, the Islamic Republic of Iran, the Democratic
      People's Republic of Korea, or any country later designated a "foreign country of
      concern" [REF-LAW-003].
    - It is owned by, controlled by, or subject to the direction of the government or ruling
      party of a restricted country, or it is a subsidiary or affiliate of such an entity
      [REF-LAW-002 §1822(1)(D)-(E)].
    - It is a named or determined covered entity [REF-LAW-001 §5949(j)(3)] [REF-LAW-002
      §1822(1)].

  **Scope.** The test is the manufacturer's domicile and control (owner decision 2026-10-17).
  The wafer-fab and assembly/test sites are recorded wherever the vendor publishes them, but
  they do not disqualify a part. The rule is stricter than the statutes, which bind federal
  procurement only. It exists because this airframe's avionics are "the components that
  control the unmanned aircraft" and its "communication links" [REF-LAW-002 §1823(a)], and
  because the fleet trust architecture assumes an auditable supply chain.

  **Generic part numbers.** A part number sold by many manufacturers (for example SMAJ33CA)
  satisfies the rule only once a compliant manufacturer is named in its MPN / BOM entry.
- **Open, NDA-free documentation only.** Every IC and module shall have a datasheet, and any
  design information its circuit depends on, that is publicly available and shareable without
  a non-disclosure agreement, a confidentiality marking such as "CONFIDENTIAL: Development
  Partners Only", or redistribution terms that would stop the repository from citing and
  archiving it. This is the OSHWA certification condition: "third-party components such as
  chips must have fully accessible and shareable datasheets" [REF-LIC-002]. A free
  registration wall is acceptable only if the documents carry no confidentiality terms; record
  the access route in `REFERENCES.md`.
- When a candidate fails either rule, record it as rejected, with the reason, in the board's
  design document, so it is not proposed again.
