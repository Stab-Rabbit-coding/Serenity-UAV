---
title: Landing-Gear Corner Cartridge Field Swap - Plan
date: 2026-11-02
type: feat
artifact_contract: ce-unified-plan/v1
artifact_readiness: requirements-only
product_contract_source: ce-brainstorm
execution: code
---

# Landing-Gear Corner Cartridge Field Swap - Plan

## Goal Capsule

**Objective.** A broken landing-gear corner can be replaced in the field as one pre-assembled cartridge.  The cartridge comes out through a removable canonical hatch in the fused gear box.

**Product authority.** Owner (Stab-Rabbit-coding), 2026-11-02 brainstorm.  This builds on the canonical gear box in `docs/plans/2026-11-01-001-feat-canonical-gear-box-plan.md` (box fused into the one-piece SLS forward hull).

**Open blockers.**
- The current bolted bay plate (54 × 78 mm) cannot leave the fused box in any direction.  The cartridge has to be re-architected (R1).
- The out-of-plane thigh side load is unresolved (canonical gear box plan, side-load item).  It sizes the cartridge's hip structure.

## Product Contract

### Summary

Each gear corner becomes a self-contained cartridge: leg, hip pin, CF backbone, A1B tension fuses and spring row, and its mounting frame.  In the field the operator opens the angled hatch on the gear box's outboard face (Henning's canonical hatch panel), releases the cartridge, slides it out outboard, and slides in a spare.  The broken cartridge goes back to the bench.  The box stays fused to the hull and is never removed.

### Problem Frame

The gear is designed to fail first: the leg breaks before the bay or hull, and the ductile fuses are scrap after an arrest.  Corners will therefore be replaced after hard landings.

Before the box was fused, the bay bolted to the flank with four M3s driven from the cargo hold.  Fusing the box buried that plate.  A sweep of the current bay + backbone + members 120 mm out of the fused hull clashes in every direction (2026-11-02):

| Corner | Out the pillar | Inboard | Down | Outboard |
|---|---|---|---|---|
| fore-port | 12,732 | 30,224 | 9,220 | 13,545 |
| aft-port | 9,803 | 13,074 | 9,429 | 8,201 |

Values are mm³ of clash.

### Key Decisions

- **Swap a whole corner cartridge in the field; repair at the bench.**  (session-settled: user-directed — chosen over in-place part replacement and over a removable box: fastest field turn, keeps the box fused and canonical.)  Governs R1, R2, R6.
- **The cartridge leaves through a removable canonical side hatch, outboard.**  (session-settled: user-directed — chosen over a belly drop-out panel and a pillar slide-out: canon element, lowest aft clash, no aircraft roll-over to service.)  Governs R3, R4, R5.
- **The gear boxes are not removable.**  A removable box would add seams, flanges and mass that the one-piece hull was chosen to avoid.  The hatch gives the access a removable box would have given.  Governs R5.

### Requirements

**Cartridge**
- R1. Each corner's leg, hip pin, CF backbone, A1B members and mounting frame form one cartridge that leaves and enters the box through its hatch without disassembly.
- R2. Port and starboard cartridges are exact mirror images (owner symmetry rule).  Fore and aft cartridges may differ.  The field spares set is therefore two types per side.
- R3. The cartridge carries the full gear load into hull-fixed structure inside the box.  It keeps the existing failure hierarchy: the leg breaks before the cartridge mount, and the mount fails before the hull.

**Hatch**
- R4. Each gear box carries one removable hatch per corner, sized to pass that corner's cartridge.  It is styled as Henning's angled, ribbed hatch panel on the box face.
- R5. A hatch is a fairing only: it carries no primary gear load, and the box and hull keep their stiffness with it open.
- R6. Hatch and cartridge release use only tools a field kit already carries.  No fastener is reachable only from inside the cargo hold.

**Mass and character**
- R7. The cartridge mount, hatch frame and fasteners stay within the owner's weight-and-balance budget.  The net change is reported against the 14.19 lbm AUW ledger and the thrust line Y 326.7.
- R8. Every visible element (hatch seam, fasteners, panel ribs) keeps Serenity's style and character (root `AGENTS.md`, "Airframe geometry").

### Key Flows

- F1. **Field swap** (Covers R1, R4, R6): open hatch → release cartridge → slide out outboard → slide spare in → secure → close hatch → functional check (stance, stroke).
- F2. **Bench repair** (Covers R1, R3): replace the scrap fuses and/or the broken leg in the removed cartridge, re-verify, and return it to the spares set.

### Acceptance Examples

- AE1. (Covers R1, R6) Given a fired ductile fuse at aft-port, when the operator follows F1 with the field kit, then a spare aft-port cartridge is installed without removing any other part of the hull, the wing or the box.
- AE2. (Covers R5) Given any one hatch removed, the fused hull still passes `tools/assembly_integrity_check.py` for structure.  The open hatch itself is the only new opening.
- AE3. (Covers R2) The fore-stbd cartridge is the exact mirror of fore-port about the centreline.

### Scope Boundaries

- In scope: cartridge architecture, hatch geometry and retention, field and bench flows, mass and balance.
- Out of scope: the thigh side-load resolution (tracked in the canonical gear box plan); field repair of the hull or box themselves.

### Outstanding Questions

**Resolve Before Planning**
- None.  The owner chose the swap level and the exit path.

**Deferred to Planning**
- Cartridge-to-hull mount: rails/keys on box-integral seats vs the existing four-M3 seat re-oriented to face the hatch.  Each must still pass R3 and R6.
- Hatch retention: quarter-turn vs M2/M3 screws into heat-set inserts.  Check SLS PA12-CF insert pull-out (no cited allowable).
- Hatch placement and size per corner: fore cartridge plates stand near-vertical (strut 80°) and aft at 154°.  The swept-clash numbers above are the starting point.
- Whether opening the old flank skin inside the box (powder drain) can now be enlarged, since the bay seats move to the cartridge mount.
