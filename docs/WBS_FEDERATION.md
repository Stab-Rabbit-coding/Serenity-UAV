# WBS.md / TODO.md Federation Inventory (Rev S2)

Governing file: the root `AGENTS.md` §10 "WBS.md / TODO.md Federation" — that section states
the two-file rule and the governance policy; this document holds the per-subsystem inventory it
points to. Split detail files are governed by their parent folder's `AGENTS.md` (no separate
federated `AGENTS.md` per split — e.g. `avionics/observer/` follows `avionics/AGENTS.md`).

Several subsystems keep `WBS.md` detail split across more than one file so none exceeds ~500
lines (the threshold at which a subsystem gets a new detail file rather than an ever-growing
one):

- **avionics/** — `avionics/{TODO,WBS}.md` (Pilot/XO/Commo cape hardware, names, workload),
  `avionics/rev-s1/{TODO,WBS}.md` (Commo/XO/Flight Engineer Rev S1 redesign),
  `avionics/emi-hardening/{TODO,WBS}.md` (§0.6, §1.4 EMI hardening beyond the PCBs),
  `avionics/observer/{TODO,WBS}.md` (Observer board + firmware), `avionics/firmware/{TODO,WBS}.md`
  (Pilot/XO node firmware)
- **airframe/** — `airframe/{TODO,WBS}.md` (hull-frame standard, non-printable placeholders,
  procurement), `airframe/fuselage-joints/{TODO,WBS}.md`, `airframe/fuselage-covers/{TODO,WBS}.md`,
  `airframe/fuselage-mid/{TODO,WBS}.md` (fuselage §1.1.1, split 3 ways),
  `airframe/wings-nacelles/{TODO,WBS}.md`, `airframe/landing-gear/{TODO,WBS}.md`
- **graphical-build-guide/** — `graphical-build-guide/{TODO,WBS}.md` (Phases 0-4 + SVG rebuild
  pipeline), `graphical-build-guide/flight-phases/{TODO,WBS}.md` (Phases 5-10)
- **docs/**, **gcs/**, **deferred/** — a single `{TODO,WBS}.md` pair each (well under the cap)
- **tools/**, **current-specification/** — reference-index `TODO.md` files only, no `WBS.md`
  (own no WBS branch and no checkboxes of their own; pointer views into the owning
  subsystem's `WBS.md`/`TODO.md`)
