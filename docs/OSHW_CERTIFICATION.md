# Serenity UAV — Open Source Hardware Certification Readiness

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**Status:** Rev 1 — 2026-08-01 (TODO.md §0.9 item 7 — supporting documents for OSHW certification)
**Standard:** OSHWA Open Source Hardware Certification [REF-LIC-002] — <https://certification.oshwa.org/requirements.html>

> **This document is a readiness checklist, not a certificate.** OSHWA certification is a
> **self-certification program**: the applicant submits an online license form and a signed
> Certification Mark License Agreement, valid one year with annual reaffirmation. There is no
> numbered legal clause to cite the way FCC/FAA regulations are cited elsewhere in this
> project — see `REFERENCES.md` REF-LIC-002. **Submission requires the human maintainer
> (Steve Griffing) to act** — this repository can only prepare the supporting material.

---

## 1. What OSHWA certification requires (verified 2026-08-01)

Per <https://certification.oshwa.org/requirements.html> and
<https://certification.oshwa.org/basics.html>:

1. All of the creator's own contributions to a certified product must be shared as open
   source.
2. All parts within the creator's control must be open source; third-party proprietary
   components must be clearly distinguished, and third-party chips/components must have
   fully accessible and shareable datasheets.
3. All software necessary for the operation of the hardware must be licensed under an
   OSI-approved license.
4. Certification is by self-certification: complete the online license form and a
   Certification Mark License Agreement at <https://certificate.oshwa.org/>.

The exact clause-level text of the Open Source Hardware Definition beyond these four points
(e.g. any specific documentation-completeness or derived-works clauses) has not been
independently re-verified line-by-line against the current oshwa.org text as part of this
pass — treat any such detail as **requires verification** before the actual submission, per
root `AGENTS.md` §4 ("never guess a section number").

## 2. Readiness checklist against requirement 1 — own contributions shared as open source

| Item | Status | Note |
|---|---|---|
| Hardware/CAD/PCB design licensed under an open license | ✅ Done | CERN-OHL-W 2.0 — `LICENSE` (root), `airframe/LICENSE`, `avionics/LICENSE` (TODO.md §0.9 items 3–4) |
| Documentation/code/scripts licensed under an open license | ✅ Done | CC BY-SA 4.0 — `docs/LICENSE`, `tools/LICENSE`, `current-specification/LICENSE`, `graphical-build-guide/LICENSE`, mixed `gcs/LICENSE` / `deferred/LICENSE` (TODO.md §0.9 item 5) |
| Design files publicly available in the repository | ✅ Done | KiCad schematics/PCB/Gerbers, SCAD/STL/FCStd all in-repo |
| Firmware source publicly available | ⚠ Partial | Firmware architecture specs are complete and CC BY-SA 4.0 (`avionics/firmware/`); Phase 7 implementation firmware itself is still open work (TODO.md §4.2–§4.4) — certification should wait until firmware source, not just spec, exists |

## 3. Readiness checklist against requirement 2 — open parts + distinguished third-party components + accessible datasheets

| Item | Status | Note |
|---|---|---|
| Third-party commercial components distinguished from original design | ✅ Done | `current-specification/LICENSE_AND_ATTRIBUTION.md` "Third-Party Software and Firmware" table + "Not covered / separate terms" in `README.md` |
| Third-party chip datasheets accessible | ⚠ Partial | Most key ICs cited with validated datasheet URLs in `REFERENCES.md` Part XII (Sensor and Component Specifications); a handful remain in the "Open Standards Verification Items" table (e.g. RSSI comparator, STS3215 winch servo — datasheet in repo but not yet text-extracted) — resolve those before submission |
| Upstream CAD/reference sources' own licenses distinguished from project's license | ✅ Done | `docs/attribution_and_licensing.md` §3 "Available Component boundary" — REF-CAD-002/003/004 explicitly classified (Available Component vs. reference-only) |

## 4. Readiness checklist against requirement 3 — necessary software OSI-approved

| Item | Status | Note |
|---|---|---|
| Third-party software/firmware dependencies license-audited | ✅ Done | `current-specification/LICENSE_AND_ATTRIBUTION.md` "Third-Party Software and Firmware" table — all entries carry OSI-approved licenses (BSD-3-Clause, Apache-2.0, MIT, GPL-2.0/3.0, LGPL) |
| GPL/LGPL copyleft obligations flagged for commercial derivatives | ✅ Done | "GPL notice" in the same table |
| TI Z-Stack (TI TSPA, non-OSI) flagged as a required-review exception | ⚠ Open | `current-specification/LICENSE_AND_ATTRIBUTION.md` already flags this ("TI TSPA notice") — **this is the one dependency that does not meet requirement 3 as stated** (necessary for Zigbee 2.4 GHz operation, TI TSPA is not an OSI-approved license). Resolve before certifying: either accept Zigbee as a non-certified-scope interface, or find/port to an OSI-licensed Zigbee stack. |

## 5. What this repository cannot do

- **Submit the application.** Certification requires the maintainer to sign the
  Certification Mark License Agreement personally — no agent or automated process can do
  this.
- **Obtain the OSHWA UUID.** Assigned only after a successful submission.
- **Independently verify OSHWA's full Open Source Hardware Definition text clause-by-clause**
  beyond the four requirements confirmed in §1 — do that as part of the actual submission
  review, not from this document.

## 6. Recommended order of operations

1. Resolve the TI Z-Stack exception (§4) — decide whether Zigbee is in scope for the
   certified product.
2. Finish Phase 7 firmware source (§2) so "all of the creator's own contributions" actually
   includes working firmware, not just the architecture spec.
3. Close the remaining datasheet-URL gaps in `REFERENCES.md` "Open Standards Verification
   Items" (§3).
4. Maintainer submits via <https://certificate.oshwa.org/>.

---

*This document is released under CC BY-SA 4.0.*
