# Documentation — Agent Instructions

Adds documentation-specific rules to root `AGENTS.md`, which wins wherever it speaks. Scope:
design specifications, analyses, standards references, build guides, and compliance records.
Documentation is a design artifact: every specification and analysis shall be traceable to
authoritative sources.

## Citation Procedure

This file is the one home for the citation procedure; root `AGENTS.md` §4 states the rule.

**`REFERENCES.md` entry fields:** designation and full title; issuing body; validated URL
(verified against the issuing body); date accessed and verification date; the chapter,
section, and paragraph applied; and every repository location that cites it.

**Format:** `[REF-ID §section.subsection.paragraph]`, e.g., `[REF-FCC-001 §15.247(b)(3)(ii)]`,
`[REF-NIST-001 §2.1, §2.2, §3.3]`.

**Adding a citation:**

1. Look up the standard in `REFERENCES.md` by REF-ID.
2. If absent, add it with the fields above.
3. Cite the REF-ID, and add the citing location to its entry.

**Auditing a citation:**

1. Confirm the URL is valid and points to the official document.
2. Confirm the cited section/paragraph exists in that document.
3. If it cannot be verified, mark it "requires verification" in `REFERENCES.md` and open an
   item in `docs/WBS.md` (root §10).
4. If it is wrong, correct or remove every use, and record the removal and reason in
   `REFERENCES.md` "Removed / Superseded Citations" (e.g., "Misattributed — the rule was from
   Part 97, not Part 95").

No fabricated, unverifiable, or misattributed reference is permitted.

## Applicable Standards Bodies

US bodies take precedence (root §4). Vet design specifications against: FAA (airworthiness,
registration, operations); FCC (RF emissions, unlicensed bands); NIST (cybersecurity, zero
trust); DoD/DLA (MIL-STD-1553, encrypted comms); ISO (data buses, safety); IEC (component
safety, isolators); VDE (high-voltage isolators); IEEE (networking); ISA/IEC 62443 (OT/ICS
security); AUVSI/ASTM F38 (UAS); ICAO (international aviation).

## Canonical Shape References

`docs/references/` holds the canonical-accuracy library (REF-CAD-002/003/004). Its authority
order and usage rules are owned by `airframe/HULL_FRAME_REFERENCE.md` "Canonical Accuracy
References". The QMx blueprint pack (REF-CAD-003) is a copyrighted product retained for
internal reference only and is **not** relicensed. Creative-universe attribution:
`REFERENCES.md` and `current-specification/LICENSE_AND_ATTRIBUTION.md`.

## Document Structure

`docs/DOC_TEMPLATES.md` is the authoritative template set (specification, analysis, and
compliance-record fields; build-guide content; changelog conventions). WARNING/CAUTION/NOTE and
wording follow root §6. Units follow root §5.

## Work Tracking

Explain each change in its commit message. Archive superseded documents under `archives/`.
Track multi-document work as items in `docs/WBS.md` (root §10 federation).
Each theme within a plan shall be built on its own branch named `Theme-[Letter]-S[Number]-S[Number]`
(first and last sprint of the theme, e.g., `Theme-N-S2-S6`); commit and push it often so no work is lost.
