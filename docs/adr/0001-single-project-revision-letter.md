# One project-wide revision letter

**Status:** accepted (owner, 2026-11-17)
**License:** CC BY-SA 4.0 — see LICENSES/CC-BY-SA-4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)

Revision letters had drifted per component: Rev U for the project baseline, Rev T for Commo,
Rev S1/S2 for avionics boards and the WBS federation, and "Rev R2" for the aircraft datum, which
collided with the R2 numbered-modification scheme. Nothing said which letter was current, so
agents stamped new work with whatever label they had last seen. The owner chose one
project-wide letter (currently Rev U) over per-board letters, because a letter revision is
defined as a whole-aircraft checkpoint and per-board letters made "current" ambiguous. Existing
board letters are frozen as historical labels and every active component is restamped Rev U
when Rev U closes (WBS REVU-RELABEL), rather than relabelling mid-revision. Coordinate frames
are named "frame R1"/"frame R2", never as revisions. Rule: root `AGENTS.md` §8.

**Considered options:** per-board letters with the current project letter stated in §8
(rejected: two meanings of "current"); relabel everything now (rejected: churn in the middle of
Rev U, and KiCad title blocks would change outside the ERC/DRC cycle).
