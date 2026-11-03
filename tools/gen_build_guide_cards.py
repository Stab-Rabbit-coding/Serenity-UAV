#!/usr/bin/python3
"""Generate the Rev T+ graphical build-guide cards from one spec table.

Replaces the hand-drawn pre-Rev-N cards (archived 2026-10-31 to
archives/graphical-build-guide-pre-revt/).  Every card is built from:

  * a highlight render of the FreeCAD master assembly
    (airframe/blender-scripts/build_guide_card_renders.py), so the art is
    always the airframe as placed -- never a drawing of it; and
  * the CARDS table below, whose text is taken from the Rev T+ build guide
    (graphical-build-guide/REVN_BUILD_GUIDE_24IN.md) and the authority
    documents each card names in its SOURCE line.

Cards whose procedure has not been re-audited for Rev T+ (graphical-build-guide
WBS 1.5.6) say so on the card instead of carrying unverified steps.

Pipeline (run from the repo root):

  1. xvfb-run -a freecadcmd -c "import sys; sys.argv=['x','--','MESH']; \\
         exec(open('tools/export_assembly_meshes.py').read())"
  2. /usr/bin/python3 tools/gen_build_guide_cards.py views VIEWS_JSON
  3. blender -b -P airframe/blender-scripts/build_guide_card_renders.py -- \\
         MESH VIEWS_JSON graphical-build-guide/card-renders
  4. /usr/bin/python3 tools/gen_build_guide_cards.py svg

Writes graphical-build-guide/build_guide_NN_<slug>.svg (27 cards),
build_plan.svg and components_overview.svg.  Renders are linked, not
EMBEDDED as base64 JPEG data URIs (render_href(), 2026-11-01).  Linked
renders showed as blank frames in GitHub, the VS Code preview and other
viewers, which refuse to load an external file referenced from inside an
SVG.  The PNGs in card-renders/ stay the render masters.

Units: US customary primary, metric in parentheses (AGENTS.md).  Coordinates
are aircraft datum R2 (tools/hull_datums.py).

Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
Stab-Rabbit-coding, 2026-10-31, per AGENTS.md AI attribution.
License: MIT (software) -- see tools/LICENSE.  The SVG cards it writes are
documents, licensed CC BY-SA 4.0 (SPDX-License-Identifier: CC-BY-SA-4.0).
"""

# ruff: noqa: C408, ISC004 -- dict() keeps the CARDS table readable as keyword
# records; adjacent string literals inside the SVG fragment lists are deliberate.

import json
import os
import sys
import textwrap
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
GUIDE = os.path.join(HERE, "..", "graphical-build-guide")
N_CARDS = 27

# Parts every interior view hides so the internals can be seen.
SHELLS = [
    "Hull_Forward",          # head+cargo, one SLS piece (2026-10-31)
    "Hull_Aft",              # middle+rear, one SLS piece (2026-11-01)
    "Cargo_Middle_Splice",   # the one remaining hull joint
    "Cargo_Door",
    "Cargo_Hinge",
]
UNPLACED = ["Dorsal_Antenna_Fin"]  # VERIFY placement at the datum origin

PENDING = (
    "Procedure pending the Rev T+ re-audit of guide Phases 4-11 "
    "(graphical-build-guide/WBS.md 1.5.6). This card shows the Rev T+ "
    "architecture only; follow the authority documents named below."
)


def render_href(png_name, quality=85):
    """Data URI of a card render, re-encoded as JPEG to keep the SVG small.
    Embedded, not linked, so every SVG viewer shows the image."""
    import base64
    import io

    from PIL import Image

    path = os.path.join(GUIDE, "card-renders", png_name)
    with Image.open(path) as im:
        buf = io.BytesIO()
        im.convert("RGB").save(buf, "JPEG", quality=quality, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


# ---------------------------------------------------------------------------
# Card table.  view: highlight prefixes, hide prefixes, camera direction,
# framing margin.  parts: (qty, item, BOM ref or note).  steps: ordered text.
# warn: (level, text) with level WARNING / CAUTION / NOTE (REF-MIL-003 SS1.5).
# ---------------------------------------------------------------------------
CARDS = [
    dict(
        slug="cover",
        phase="",
        title="SERENITY-CLASS TILTROTOR UAV",
        sub="Illustrated build guide - Rev T+ (24 in hull)",
        view=dict(highlight=[], dir=(1.0, -1.1, 0.75), margin=1.08),
        parts=[
            ("", "Hull length 24.00 in (609.6 mm)", ""),
            ("", "2 tilting tandem-EDF nacelles (64 mm pods)", ""),
            ("", "Worm-drive tilt, -5 to 135 deg stops", ""),
            ("", "Servo-scheduled shingled nozzles", ""),
            ("", "3.0 in (76 mm) R6 landing gear", ""),
            ("", "8 avionics nodes + Observer, FE, Commo", ""),
        ],
        steps=[
            "Cards 01-05: print and cut every part before the first epoxy joint.",
            "Cards 06-16: structure, gear, cargo, tilt, nacelles, power, void formers, foam.",
            "Cards 17-22: avionics, buses, security, lights, antennas, sensors.",
            "Cards 23-26: software, calibration, test and first flight, markings.",
        ],
        warn=[
            (
                "NOTE",
                "Performance figures (AUW, thrust, T/W) are provisional until the "
                "bottom-up AUW ledger closes: read docs/WBS.md 0.10.1, not this card.",
            )
        ],
        source="graphical-build-guide/REVN_BUILD_GUIDE_24IN.md (Rev T+ Configuration)",
    ),
    dict(
        slug="print_prep",
        phase="PHASE 0 - PRINT",
        title="ORDER THE SLS PARTS",
        sub="3D Systems: DuraForm PA CF and PA11",
        view=dict(highlight=[], dir=(0.0, 0.0, 1.0), margin=1.05),
        parts=[
            ("", "DuraForm PA CF (PA12-CF): structure, shells, gears", "REF-MAT-015"),
            ("", "DuraForm PA11 Black: gear feet (impact)", "REF-MAT-016"),
            ("", "SLS 380 15 x 13 x 18 in; sPro 140 22 x 22 x 18 in", "REF-MFG-001 p. 17"),
            ("", "per-part material + orientation list", "SLS_PRINT_ORIENTATION.md"),
        ],
        steps=[
            "Export every current part listed in docs/SLS_PRINT_ORIENTATION.md 4.",
            "Send each STL with its material and requested build orientation.",
            "Agree the final orientation and machine for each part with 3D Systems.",
            "Order the forward hull section on the sPro 140 (lies flat there).",
            "Order the cargo doors in the same build as the forward hull section.",
            "On delivery: bead-blast check every blind hole; line-ream the door knuckles.",
        ],
        warn=[
            (
                "NOTE",
                "The repo orientations are a design-intent request, not a release "
                "instruction (owner decision 2026-11-01).",
            ),
            (
                "CAUTION",
                "Do not print structural parts in FDM CF-PETG. The sizing now uses "
                "PA CF allowables (tools/sls_materials.py).",
            ),
        ],
        source="docs/SLS_MIGRATION.md; docs/SLS_PRINT_ORIENTATION.md; REF-MFG-001",
    ),
    dict(
        slug="print_hull",
        phase="PHASE 0 - PRINT",
        title="HULL: TWO SLS SECTIONS + ONE COLLAR",
        sub="Forward (head+cargo), aft (middle+rear), cargo/middle collar",
        view=dict(
            highlight=["Hull_Forward", "Hull_Aft", "Cargo_Middle_Splice"],
            hide=UNPLACED,
            dir=(1.0, -0.6, 0.45),
            margin=1.05,
        ),
        parts=[
            ("1", "head_cargo_shell24_2mm_merged.stl (sPro 140)", "forward section"),
            ("1", "middle_rear_shell24_2mm_merged.stl (SLS 380)", "aft section"),
            ("1", "cargo_middle_splice_collar.stl", "PRINT-CARGO-MIDDLE-COLLAR"),
        ],
        steps=[
            "Order both sections in DuraForm PA CF, lying flat (Y in the build plane).",
            "Order the cargo/middle collar. Its mating faces are OPEN by design.",
            "Dry-fit the collar into both sections before any bond.",
            "Mark port and starboard on each section interior.",
        ],
        warn=[
            (
                "NOTE",
                "The head/cargo and middle/rear seams are printed, blended skin, "
                "checked against the QMx blueprints (SLS_PRINT_ORIENTATION.md 6).",
            )
        ],
        source="docs/SLS_PRINT_ORIENTATION.md 3 and 6; tools/merge_*_shell.py",
    ),
    dict(
        slug="print_nacelle",
        phase="PHASE 0 - PRINT",
        title="PRINT NACELLES, TRUNNIONS, NOZZLES",
        sub="64 mm pods, 6704ZZ trunnions, Rev T3 shingled nozzle, ESC covers",
        view=dict(
            highlight=["Nacelle_Port", "Nacelle_Stbd"],
            hide=UNPLACED,
            dir=(1.0, -0.9, 0.6),
            margin=1.1,
        ),
        parts=[
            ("2", "nacelle_{port,stbd}_64mm.stl", "PRINT-NACELLE-PORT/STBD"),
            ("2", "nacelle_trunnion_64mm_{port,stbd}.stl", "PRINT-NACELLE-TRUNNION"),
            ("8+8", "nozzle flaps: 4 master + 4 seal per nacelle", "PRINT-NACELLE-FLAP-*"),
            ("2+2", "nozzle throat, unison ring", "-THROAT, -RING"),
            ("4", "ESC covers {port,stbd}_{a,b}, all distinct", "PRINT-NACELLE-ESC-COVER"),
        ],
        steps=[
            "Order both pods in PA CF; they are mirror parts, not copies.",
            "Print the trunnions; check that each 6704ZZ seat accepts its bearing.",
            "Print 4 master + 4 seal flaps per nacelle; dry-lap all 8 on the ring.",
            "Print the four ESC covers; each fits one bay only.",
        ],
        warn=[
            (
                "NOTE",
                "The BOM still carries 50 mm EDF rows until the NAC-64 gates close; "
                "the assembly and these cards show the 64 mm pod.",
            )
        ],
        source="REVN_BUILD_GUIDE_24IN.md Phase 0; docs/NACELLE_64MM_VERIFICATION.md",
    ),
    dict(
        slug="print_cargo_gear",
        phase="PHASE 0 - PRINT",
        title="PRINT CARGO, TILT-DRIVE AND GEAR PARTS",
        sub="Interior parts shown with the shells hidden",
        view=dict(
            highlight=[
                "Tilt_",
                "Twin_Pack",
                "Chin_Node_Shelf",
                "Gateway_Door_Tray",
                "Door_Latch",
                "Cargo_Door_Servo",
                "Cargo_Release_Servo",
                "LG_Bay",
                "Cargo_FPV",
                "Cargo_GPS",
            ],
            hide=UNPLACED + SHELLS,
            dir=(1.0, -0.8, 0.7),
            margin=1.1,
        ),
        parts=[
            ("2", "tilt_actuator_bracket_{port,stbd}", "PRINT-TILT-BRACKET"),
            ("2+2", "tilt worm, worm wheel", "PRINT-TILT-WORM/WHEEL"),
            ("2", "tilt_brake_guide + _stbd (MIRRORED print)", "PRINT-TILT-BRAKE-GUIDE"),
            ("4", "lg_r6_3_0in_bay_*_print.stl, 4 distinct", "PRINT-LG-*"),
            ("4", "leg frames (fore/aft) + 4 feet", "PRINT-LG-LEG-FRAME-3.0IN"),
            ("", "doors, latch, servo brackets, door tray, shelf", "PRINT-CARGO-*"),
            ("1+2+1", "twin pack tray, 2 sleds, gate (head)", "twin_pack_tray.scad"),
        ],
        steps=[
            "Print the tilt brackets, worms, and wheels; the worm turns the wheel freely by hand.",
            "Print the starboard brake guide from its own STL; it is a mirror, not a copy.",
            "Print the four gear bays from the *_print.stl files; label each corner.",
            "Print the cargo doors, latch brackets and cranks, door horns, and servo brackets.",
            "Print the twin pack tray, sleds and gate, chin node shelf, GPS ring, FPV bezel, "
            "and door tray.",
        ],
        warn=[
            (
                "NOTE",
                "The winch has no hull-frame STLs yet; print it from the "
                "PRINT-CARGO-WINCH-* rows. It is not shown.",
            )
        ],
        source="REVN_BUILD_GUIDE_24IN.md Phase 0 Print Schedule",
    ),
    dict(
        slug="cut_cf_machined",
        phase="PHASE 0 - CUT",
        title="CF CUTS AND MACHINED PARTS",
        sub="Fixed spar, tilt shafts, metal pinions, gear cheeks",
        view=dict(
            highlight=["Wing_Port", "Wing_Stbd", "Wing_Root_Flange"],
            hide=UNPLACED,
            dir=(0.3, -0.5, 1.0),
            margin=1.1,
        ),
        parts=[
            ("2", "CF tube 20 mm OD x 16.3 mm ID", "SPAR-CF-20X16"),
            ("2", "Steel tube 4 mm OD x 0.5 mm wall, ~9.8 in (250 mm)", "SHAFT-TILT-4MM"),
            ("2", "14T tilt pinion, BRASS or STEEL, machined", "no BOM row yet"),
            ("8", "CF 1/8 in (3.2 mm) quasi-iso cheeks, waterjet", "LG-A1B-CF-CHEEK"),
            ("1", "CF flat bar 6 x 3 mm keel, 2 segments", ""),
        ],
        steps=[
            "Cut both wing spars per docs/TILT_SPAR_ANALYSIS.md; deburr the ends.",
            "Cut the two 4 mm tilt shafts; they run in BUSH-TILT-4MM bronze bushings.",
            "Machine the 14T pinions in brass or steel from wing_tilt_pinion.scad.",
            "Waterjet the 8 A1b backbone cheeks (2 per leg).",
            "Cut the keel segments and the 2 ring-frame profiles.",
        ],
        warn=[
            (
                "WARNING",
                "CF dust is a respiratory and eye hazard. Wear an N95 and safety "
                "glasses; cut outdoors or with dust extraction.",
            ),
            (
                "CAUTION",
                "Never print the tilt pinion. A printed pinion is below the "
                "76 MPa allowable (NACELLE_64MM_VERIFICATION 5c).",
            ),
        ],
        source="REVN_BUILD_GUIDE_24IN.md Phase 0 CF Cuts and Machined Parts",
    ),
    dict(
        slug="hull_join",
        phase="PHASE 1 - HULL",
        title="JOIN THE HULL: ONE COLLAR, KEEL, RING FRAMES",
        sub="The cargo/middle collar joins the two sections",
        view=dict(
            highlight=["Cargo_Middle_Splice"],
            hide=UNPLACED + ["Hull_Aft", "Cargo_Door"],
            # one collar, not three: widen the frame so the joint reads in
            # context (forward section shown, aft section hidden)
            dir=(1.0, 0.35, 0.45),
            margin=3.2,
        ),
        parts=[
            ("1", "cargo/middle splice collar", "PRINT-CARGO-MIDDLE-COLLAR"),
            ("1", "West System 105/206 epoxy kit", ""),
            ("2", "CF keel segments (card 05)", ""),
            ("2", "CF ring frames", "airframe/diagrams/ring_frames/"),
        ],
        steps=[
            "Bond the keel segments into the forward (cargo) and aft (rear) keel runs.",
            "Bond the two ring frames into their keel notches.",
            "Bond the collar into both sections; clamp and cure.",
        ],
        warn=[
            (
                "NOTE",
                "Keel splice and frame stations are still in the R1 datum and "
                "predate the one-piece aft section; re-derive them in R2 before "
                "cutting notches (WBS 1.5.6 re-audit).",
            )
        ],
        source="docs/SLS_PRINT_ORIENTATION.md 3; docs/structural_analysis.md 4.1-4.2, 7.4",
    ),
    dict(
        slug="wing_root",
        phase="PHASE 1 - HULL",
        title="WING ROOT: BONDED FLANGE, RELEASABLE SPAR",
        sub="Flange bonds to the hull; spar bonds to the wing",
        view=dict(
            highlight=["Wing_Root_Flange"],
            hide=UNPLACED
            + [
                "Hull_Forward",
                "Cargo_Door",
                "Cargo_Hinge",
                "Cargo_Middle_Splice",
            ],
            dir=(1.0, -0.7, 0.5),
            margin=2.6,
        ),
        parts=[
            ("2", "wing_root_flange_{port,stbd}.stl", "PRINT-WING-ROOT-FLANGE"),
            ("2", "CF spar 20 mm (card 05)", "SPAR-CF-20X16"),
            ("1", "West System 105/206", ""),
            ("2", "WA-R3 split collar", "NOT YET A PART (WA-R17)"),
        ],
        steps=[
            "Bond each flange to the inner cargo sidewall per the adhesive maker's cure schedule.",
            "DRY-FIT the spar through flange and hull with NO adhesive, then withdraw it.",
            "Cap the spar passage so foam cannot enter it.",
            "Bond the spar into the wing root as a separate wing + spar sub-assembly.",
            "Hold final wing fit until the WA-R3 split collar exists.",
        ],
        warn=[
            (
                "CAUTION",
                "Never bond the spar into the hull or let foam into the spar "
                "passage: the wing would become unremovable.",
            )
        ],
        source="REVN_BUILD_GUIDE_24IN.md Phase 1 step 5; docs/WING_ATTACH_INTERFACE.md 3.3-3.4",
    ),
    dict(
        slug="landing_gear",
        phase="PHASE 1 - HULL",
        title="LANDING GEAR: BAYS + 3.0 IN R6 LEGS",
        sub="Conforming bays, A1b balanced-couple absorber",
        view=dict(
            highlight=["Landing_Gear", "LG_Bay"], hide=UNPLACED, dir=(1.0, -0.7, -0.25), margin=1.15
        ),
        parts=[
            ("4", "conforming bays, 4 distinct mirror prints", "PRINT-LG-*"),
            ("4", "3.0 in leg frames + feet", "PRINT-LG-LEG-FRAME-3.0IN"),
            ("8", "music-wire springs, 2 per leg", "LG-SPRING-WIRE"),
            ("8", "6061-T6 tension fuses, 2 per leg", "LG-A1B-FUSE"),
            ("4+4", "reversing sleeve + cage, 1 each per leg", "LG-A1B-SLEEVE/CAGE"),
            ("20", "O4 mm pins with clips, 5 per leg", "LG-A1B-PIN"),
            ("4", "Dyneema safety cord ~16 in (400 mm)", "LG-SAFETY-CORD"),
        ],
        steps=[
            "Seat each bay in its sponson rebate; port and starboard bays are not interchangeable.",
            "Fasten each bay with its 4 x M3.",
            "Build each leg: CF cheeks, springs, fuses, sleeve, cage, pins (DRAFT, not "
            "bench-verified).",
            "Pin each leg into its bay; fit the safety cord as secondary retention.",
            "Check all four feet touch a flat plate together.",
        ],
        warn=[
            (
                "WARNING",
                "The gear is not flight-cleared. Do not fly until the gear "
                "analysis closes (docs/LANDING_GEAR_ANALYSIS.md).",
            )
        ],
        source="docs/LANDING_GEAR_ANALYSIS.md; tools/generate_lg_bays.py; bom_revT.csv LG-*",
    ),
    dict(
        slug="cargo_doors",
        phase="PHASE 1 - HULL",
        title="CARGO DOORS, LATCH, DOOR GATEWAY",
        sub="Lapped clamshell doors, one bell-crank latch",
        view=dict(
            highlight=[
                "Cargo_Door",
                "Cargo_Hinge",
                "Door_Latch",
                "Gateway_Door_Tray",
                "Cargo_Door_Servo",
                "Cargo_Release_Servo",
            ],
            hide=UNPLACED + ["Landing_Gear", "LG_Bay"],
            dir=(0.6, -0.5, -1.0),
            margin=1.2,
        ),
        parts=[
            ("2", "cargo_door_{port,stbd}", "PRINT-CARGO-DOOR-*"),
            ("1", "cargo_hinge_retention", ""),
            ("2+2", "latch brackets (fixed) + bell-cranks", "PRINT-DOOR-LATCH-*"),
            ("2", "door horns", "PRINT-DOOR-HORN"),
            ("3", "SG90 servos: 2 doors + 1 release", "SERVO-CARGO"),
            ("1", "door gateway card-edge tray", "PRINT-GW-DOOR-TRAY"),
        ],
        steps=[
            "Hang both doors on the hinge retention; they lap at the seam.",
            "Fit each bell-crank on its pivot pin in its fixed bracket; the port crank carries the "
            "latch hook.",
            "Fit the door horns and pushrods.",
            "Mount the door and release servos on their brackets; wire them to the door gateway.",
            "Check that the hook drops into its fixed mortise with the doors closed.",
        ],
        warn=[
            (
                "NOTE",
                "The servos are bus-networked through their own gateway, "
                "not driven from a local H-bridge.",
            )
        ],
        source="bom_revT.csv PRINT-DOOR-*, PRINT-GW-DOOR-TRAY; docs/CARGO_WINCH_SPECIFICATION.md",
    ),
    dict(
        slug="tilt_drive",
        phase="PHASE 3 - TILT",
        title="TILT DRIVE: WORM, WHEEL, PIN BRAKE",
        sub="Cargo-bay actuator, one per side (shells hidden)",
        view=dict(highlight=["Tilt_"], hide=UNPLACED + SHELLS, dir=(0.8, -1.0, 0.9), margin=1.8),
        parts=[
            ("2", "Pololu 20D 25:1 CB 6 V gearmotor", "GM-TILT-20D"),
            ("2", "tilt controller (Open-Secure-ESC brushed)", "OSESC-TILT-TC"),
            ("2", "pull solenoid brake", "SOL-TILT-BRAKE"),
            ("2", "3 A mini blade fuse", "FUSE-TILT-3A"),
            ("2+2+2", "bracket, six-start worm, 40T wheel", "PRINT-TILT-*"),
        ],
        steps=[
            "Mount each bracket on its three shell feet.",
            "Fit the worm, mesh the 40T wheel, and grub-screw the wheel to the 4 mm shaft.",
            "Mount the gearmotor; wire it through its own fused feed to the tilt controller.",
            "Fit the brake solenoid on its guide (mirrored guide on starboard).",
            "Brake check: motor unpowered, the pin locks the worm collar against hand load.",
        ],
        warn=[
            (
                "CAUTION",
                "The worm train is NOT self-locking. Never leave a nacelle unbraked "
                "and unpowered under load: it will back-drive.",
            )
        ],
        source="REVN_BUILD_GUIDE_24IN.md Phase 3; docs/TILT_ACTUATOR_SELECTION.md",
    ),
    dict(
        slug="trunnion",
        phase="PHASE 3 - TILT",
        title="TRUNNION + PINION: HANG THE NACELLE",
        sub="2 x 6704ZZ on the fixed spar, 14T into the 50T ring gear (port pod hidden)",
        view=dict(
            highlight=["Nacelle_Port_Trunnion", "Wing_Port_Tilt"],
            hide=UNPLACED + ["Nacelle_Port"],
            dir=(0.9, 0.5, 0.8),
            margin=3.2,
        ),
        parts=[
            ("4", "6704ZZ bearings, 2 per trunnion", "PRINT-NACELLE-TRUNNION"),
            ("2", "14T machined pinion (card 05)", ""),
            ("4", "bronze bushing 4 x 8 x 5 mm", "BUSH-TILT-4MM"),
            ("2", "AK7455 tilt-encoder PCB", "SKIPPER-TILT-ENC-PCB"),
        ],
        steps=[
            "Seat the trunnion with its 6704ZZ pair on the fixed spar at the wing tip.",
            "Run the 4 mm shaft out through its bushings; mesh the 14T pinion with the 50T ring "
            "gear.",
            "Fit the AK7455 at the trunnion ring magnet.",
            "Fit the hard stops at -5 and 140 deg.",
            "Command -5 -> 90 -> 135 deg and back; set soft limits to -5 and 135 deg.",
        ],
        warn=[
            (
                "NOTE",
                "Open owner decision: the 6704ZZ pair runs at 89 % of C0 under "
                "ultimate load (NACELLE_64MM_VERIFICATION 5b).",
            )
        ],
        source="REVN_BUILD_GUIDE_24IN.md Phase 3; owner ruling 2026-10-31 (tilt range)",
    ),
    dict(
        slug="edf_install",
        phase="PHASE 2 - NACELLE",
        title="EDF INSTALL: 64 MM TANDEM STAGES",
        sub="Stator-as-mount, Z measured aft from the pod nose",
        view=dict(
            highlight=["Nacelle_Port"],
            hide=UNPLACED + ["Nacelle_Port_Trunnion"],
            dir=(1.0, -0.3, 0.4),
            margin=1.3,
        ),
        parts=[
            ("4", "tandem EDF stages, 2 per nacelle", "EDF-50-6S row until NAC-64"),
            ("4", "ESC in hinged nacelle bays", "rating held for NAC-64 power gate"),
            ("", "slow-cure structural epoxy", ""),
            ("", "8 mm wire sleeve ~20 in (500 mm)", ""),
        ],
        steps=[
            "Bench-test rotation: port CW from the intake, starboard CCW; swap two phases to "
            "reverse.",
            "Stage 1 (fore): pod Z 1.20-4.06 in (30.5-103.2 mm); stator/mount 1.66-4.06 in "
            "(42.2-103.2 mm).",
            "Stage 2 (aft): pod Z 4.10-6.96 in (104.2-176.9 mm); hold the 0.04 in (1.0 mm) "
            "interstage gap.",
            "Bolt each motor to its stator (4 x M3 on O16 mm, VERIFY); fit stage 2 first.",
            "Route phase leads along the vanes to the ESC bays (from Z 3.40 in / 86.35 mm aft).",
        ],
        warn=[
            (
                "WARNING",
                "EDFs on bench power can cut fingers. Keep hands, tools, and "
                "clothing clear of the duct during the rotation test.",
            ),
            (
                "NOTE",
                "Motor and rotor stations are VERIFY until NAC-64-FIT-02 measures a real QF2822.",
            ),
        ],
        source="nacelle_pod_64mm_tandem.scad; REVN_BUILD_GUIDE_24IN.md Phase 2A",
    ),
    dict(
        slug="nozzle_servo",
        phase="PHASE 2 - NACELLE",
        title="SHINGLED NOZZLE + SERVO DRIVE",
        sub="75 % of bore at 0 deg, 105 % from 90 to 140 deg",
        view=dict(
            highlight=["Nacelle_Stbd"],
            hide=UNPLACED + ["Nacelle_Stbd_Trunnion"],
            dir=(-1.0, 0.6, -0.3),
            margin=1.3,
        ),
        parts=[
            ("2", "nozzle throat", "PRINT-NACELLE-THROAT"),
            ("2", "unison ring", "PRINT-NACELLE-RING"),
            ("8+8", "master + seal flaps", "PRINT-NACELLE-FLAP-*"),
            ("2", "sub-micro nozzle servo", "plan 2026-09-28-001"),
            ("2", "torsion return spring + hard 105 % stop", ""),
        ],
        steps=[
            "Press the throat onto the pod exit; fit the unison ring over the throat housing.",
            "Hang 8 flaps alternating master and seal; each seal laps 0.2 mm outboard.",
            "Mount the servo forward of the ring; fit the pull-only slotted link (slot >= full "
            "stroke).",
            "Fit the torsion spring and the hard 105 % stop.",
            "Fail-safe: servo unpowered, push the ring to 75 % and release; it returns to 105 % "
            "every time.",
        ],
        warn=[
            (
                "CAUTION",
                "Never run the nozzle schedule with the EDFs spinning until the "
                "gateway fault logic (105 % command, then load-switch trip) is bench-verified.",
            ),
            (
                "NOTE",
                "The nozzle is not yet a placed part in the assembly (coverage gap); "
                "the render shows the hover-attitude starboard pod exit.",
            ),
        ],
        source="docs/NOZZLE_DRIVE_TRADE.md (2026-09-28); REVN_BUILD_GUIDE_24IN.md 2B-2C",
    ),
    dict(
        slug="power_routing",
        phase="PHASE 2 - NACELLE",
        title="POWER: PDB TO NACELLE ESCs",
        sub="10 AWG through the fixed spar to the disconnect bay",
        view=dict(
            highlight=["Twin_Pack", "Wing_Root_Flange", "Nacelle_Port", "Nacelle_Stbd"],
            hide=UNPLACED + SHELLS + ["Nacelle_Port_Trunnion", "Nacelle_Stbd_Trunnion"],
            dir=(0.0, -0.35, 1.0),
            margin=1.08,
        ),
        parts=[
            ("1", "Flight Engineer PDB, J_ESCn per ESC", "FlightEngineer.md"),
            ("4", "40 A mini blade fuse, 1 per ESC", "FUSE-ESC-40A"),
            ("", "10 AWG silicone, 11.8 in (300 mm) max per branch", ""),
            ("4", "ESC in hinged nacelle bay", "PRINT-NACELLE-ESC-COVER"),
        ],
        steps=[
            "Leg 1: PDB J_ESCn in the fuselage to the wing root.",
            "Leg 2: through the FIXED 20 mm spar bore; the 4-wire bundle twists freely through "
            "tilt.",
            "Leg 3: spar bore to the nacelle 10 AWG disconnect bay (pod Z 2.27 in / 57.6 mm).",
            "Leg 4: disconnect bay to each ESC, strain-relieved: ROUTE NOT YET DRAWN (WA-R10).",
            "Close each ESC bay with its own cover (4 distinct).",
        ],
        warn=[
            (
                "CAUTION",
                "Before cutting leads, measure the real run from PDB to each ESC, "
                "confirm it is within 11.8 in (300 mm), and check that nothing chafes at the "
                "trunnion through the full -5 to 140 deg travel.",
            )
        ],
        source="FlightEngineer.md; wings-nacelles WBS SPAR-20-1/-2; NACELLE_64MM_VERIFICATION 5",
    ),
    dict(
        slug="void_formers",
        phase="PHASE 4 - FOAM",
        title="VOID FORMERS AND CONDUITS",
        sub="Everything that must stay hollow goes in before the pour",
        view=dict(
            highlight=["Twin_Pack", "Chin_Node_Shelf", "Wing_Root_Flange"],
            hide=UNPLACED + ["Hull_Aft", "Cargo_Door"],
            dir=(1.0, -0.9, 0.8),
            margin=1.3,
        ),
        parts=[
            (
                "3",
                "void_former_cargo_{harness_trunk_port, harness_trunk_stbd, node_bay}",
                "PRINT-VOID-FORMER-CARGO",
            ),
            ("", "release wax, 2 coats", ""),
            ("", "PTFE conduits + pull strings", ""),
        ],
        steps=[
            "Wax every former twice.",
            "Seat the three cargo void formers; check that none rocks against the shell wall.",
            "Cap the spar passages (card 07) and keep the gear-bay pockets clear.",
            "Run every conduit with a pull string accessible at both ends.",
            "Full dry fit with all wiring before mixing any foam.",
        ],
        warn=[
            (
                "CAUTION",
                "The foam pour is the point of no return. Anything left out now "
                "cannot be added later.",
            ),
            (
                "NOTE",
                "The collar_rim and batt_chimney formers are obsolete: their collar "
                "and battery cradle were retired with the one-piece forward section.",
            ),
        ],
        source="bom_revT.csv PRINT-VOID-FORMER-CARGO; REVN_BUILD_GUIDE_24IN.md Anti-Rework Rules",
    ),
    dict(
        slug="foam_pour",
        phase="PHASE 4 - FOAM",
        title="FOAM POUR AND CLOSE-UP",
        sub="2 lb/ft3 closed-cell PU, fore to aft",
        view=dict(
            highlight=["Hull_Forward", "Hull_Aft"],
            hide=UNPLACED,
            dir=(1.0, -0.2, 0.25),
            margin=1.05,
        ),
        parts=[
            ("1", "2-part PU foam, 2 lb/ft3", ""),
            ("", "mixing cups, scale", ""),
            ("", "PPE: gloves, eye protection, ventilation", ""),
        ],
        steps=[
            PENDING,
            "Never foam the nacelle interior, the spar passages, or the gear bays.",
            "Cure fully before removing void formers; then fit the access-panel lids.",
        ],
        warn=[
            (
                "WARNING",
                "PU foam releases heat and vapor while curing. Work with "
                "ventilation, gloves, and eye protection.",
            )
        ],
        source="REVN_BUILD_GUIDE_24IN.md Phase 4 + Anti-Rework Rules 3, 4, 6",
    ),
    dict(
        slug="avionics_nodes",
        phase="PHASE 5 - AVIONICS",
        title="AVIONICS NODES",
        sub="PocketBeagle 2 Industrial + Pilot / TACCO capes",
        view=dict(
            highlight=["Chin_Node_Shelf", "Twin_Pack", "Gateway_Door_Tray"],
            hide=UNPLACED + SHELLS,
            dir=(1.0, -1.0, 0.9),
            margin=1.3,
        ),
        parts=[
            ("8", "PocketBeagle 2 Industrial", ""),
            ("4+4", "Pilot capes + TACCO capes", "avionics/kicad/"),
            ("1", "chin node shelf (CN2/CN3 pouches)", "PRINT-CHIN-SHELF"),
            ("2", "cargo node saddles: MOUNT OPEN (cradle retired)", "PRINT-NODE-SADDLE"),
            ("1", "Simon saddle (CN4/FC4), aft-section neck", "simon_node_saddle.scad"),
            ("1+1+1", "Observer, Flight Engineer, Commo", ""),
        ],
        steps=[
            PENDING,
            "Node stations come from tools/cargo_layout_fit.py (single source).",
            "Each node is pouch-wrapped (Faraday) on its saddle or shelf.",
        ],
        warn=[
            (
                "NOTE",
                "Board names: Pilot, TACCO, Observer, Flight Engineer, Commo "
                "(2026-08-01 call-sign rename).",
            ),
            (
                "CAUTION",
                "The two cargo node saddles bolted to the battery cradle, which is "
                "retired. Do not install them until a new mount is designed (WBS 0.13).",
            ),
        ],
        source="AGENTS.md 1 (avionics architecture); bom_revT.csv; tools/cargo_layout_fit.py",
    ),
    dict(
        slug="bus_wiring",
        phase="PHASE 6 - 8 NODES",
        title="INTER-NODE BUSES",
        sub="CAN FD, MIL-STD-1553C, RS-485, Ethernet",
        view=dict(
            highlight=["Chin_Node_Shelf", "Twin_Pack", "Gateway_Door_Tray", "Tilt_Bracket"],
            hide=UNPLACED + SHELLS,
            dir=(0.0, -0.3, 1.0),
            margin=1.4,
        ),
        parts=[
            ("", "CAN FD, RS-485, Ethernet harnesses", ""),
            ("", "MIL-STD-1553C stubs (HI-6138)", ""),
            ("", "termination per bus", ""),
        ],
        steps=[
            PENDING,
            "All 8 nodes interconnect on CAN FD, 1553, RS-485, and Ethernet, 5 kV isolated.",
            "Commo joins CAN FD / RS-485 / 1553C only (no Ethernet).",
            "Each nacelle EDF is PID-controlled by two different SBCs; any FC node can take any "
            "EDF.",
        ],
        warn=[("NOTE", "Bus electrical rules: avionics/AGENTS.md and each board's .md.")],
        source="AGENTS.md 1 (avionics architecture); avionics/README.md",
    ),
    dict(
        slug="security_hw",
        phase="PHASE 6 - 8 NODES",
        title="SECURITY HARDWARE",
        sub="TPM on every SBC cape, secure elements on non-SBC nodes",
        view=dict(
            highlight=["Chin_Node_Shelf", "Twin_Pack", "Gateway_Door_Tray"],
            hide=UNPLACED + SHELLS,
            dir=(1.0, -0.6, 0.8),
            margin=1.4,
        ),
        parts=[
            ("8", "SLB9672 TPM 2.0 (Pilot + TACCO)", "current-specification/README.md"),
            ("", "secure element on non-SBC nodes (Commo Rev T)", ""),
            ("", "OPTIGA Trust M on ESC + servo controllers", ""),
            ("4", "CPLD write-blocker ATF16V8BQL", ""),
        ],
        steps=[
            PENDING,
            "Provision every node before first flight.",
            "Pair each OPTIGA Trust M part: the default 0xE140 object is world-readable.",
        ],
        warn=[
            (
                "CAUTION",
                "TPM provisioning is non-reversible. Complete every dependent "
                "check before provisioning.",
            )
        ],
        source="current-specification/README.md Avionics; avionics/AGENTS.md; guide Anti-Rework "
               "Rule 8",
    ),
    dict(
        slug="nav_lights",
        phase="PHASE 6 - 8 NODES",
        title="NAVIGATION + ANTI-COLLISION LIGHTS",
        sub="Red port / green starboard on the nacelle OUTBOARD faces",
        view=dict(
            highlight=["Nacelle_Port", "Nacelle_Stbd"],
            hide=UNPLACED + ["Nacelle_Port_Trunnion", "Nacelle_Stbd_Trunnion"],
            dir=(0.0, -1.0, 0.35),
            margin=1.05,
        ),
        parts=[
            ("2", "nav lights: red (port), green (stbd)", ""),
            ("", "3-core lead through the internal cableway", ""),
            ("", "anti-collision light, visible 3 statute miles", "REF-FAA-002 107.29"),
        ],
        steps=[
            PENDING,
            "Mount red on the port and green on the starboard nacelle outboard face.",
            "Route the nav-light wires through the internal cableway; nothing protrudes.",
            "WS2812B LED rings are retired; do not fit them.",
        ],
        warn=[
            (
                "NOTE",
                "No flash rate is mandated for Part 107; 60 FPM is a design "
                "convention (REFERENCES.md disposition).",
            )
        ],
        source="airframe/wings-nacelles/WBS.md nav-light items; REFERENCES.md REF-FAA-002/003",
    ),
    dict(
        slug="antennas_c2",
        phase="PHASE 6 - 8 NODES",
        title="ANTENNAS + C2 LINKS",
        sub="Five command-and-control paths",
        view=dict(
            highlight=["Cargo_GPS", "Cargo_FPV"], hide=UNPLACED, dir=(0.6, -0.8, 1.0), margin=4.0
        ),
        parts=[
            ("", "Wi-Fi 5 GHz, Zigbee 2.4 GHz, mLRS on every TACCO", ""),
            ("", "SiK 915 MHz MAVLink via Commo", ""),
            ("", "AX.25 49 MHz (Part 15 15.235) via Commo", "REF-FCC-003"),
            ("1", "GPS retention ring", "PRINT-GPS-RETENTION"),
            ("1", "FPV bezel", "PRINT-FPV-BEZEL"),
        ],
        steps=[
            PENDING,
            "All five links are usable for C2; S-Bus is not a C2 channel.",
            "49 MHz is unlicensed Part 15, NOT Part 95 RCRS.",
            "Band-by-band FCC citations: avionics/AGENTS.md.",
        ],
        warn=[
            ("NOTE", "The dorsal antenna fin is not yet placed in the assembly and is not shown.")
        ],
        source="AGENTS.md 1 (external C2); avionics/AGENTS.md",
    ),
    dict(
        slug="obstacle_sensors",
        phase="PHASE 6 - 8 NODES",
        title="OBSTACLE SENSING",
        sub="12 x VL53L5CX ToF + 2 lasers, Observer board",
        view=dict(
            highlight=["Hull_Forward", "Cargo_FPV"], hide=UNPLACED, dir=(0.7, -1.0, 0.5), margin=1.2
        ),
        parts=[
            ("12", "VL53L5CX ToF sensors", "current-specification/README.md"),
            ("2", "laser (Class 3B nose / 3R cargo)", ""),
            ("1", "Observer vision/ToF/laser board", ""),
        ],
        steps=[
            PENDING,
            "Sensor stations come from the current head and cargo layouts, not the Rev O map.",
            "Observer sensors sit on the board edge.",
        ],
        warn=[
            (
                "WARNING",
                "Class 3B lasers can injure eyes. Never look into the nose "
                "aperture with the laser powered.",
            )
        ],
        source="current-specification/README.md Avionics; avionics/kicad/Observer/",
    ),
    dict(
        slug="software",
        phase="PHASE 5 - FIRST FLIGHT",
        title="SOFTWARE AND FIRMWARE",
        sub="SBC images, cape firmware, controller firmware",
        view=dict(
            highlight=["Chin_Node_Shelf", "Twin_Pack"],
            hide=UNPLACED + SHELLS,
            dir=(1.0, -0.8, 0.9),
            margin=1.4,
        ),
        parts=[
            ("", "USB-C cable, microSD reader", ""),
            ("", "SBC OS image", ""),
            ("", "LibreServo / Open-Secure-ESC firmware", ""),
        ],
        steps=[
            PENDING,
            "Flash and verify every node before the security provisioning in card 19.",
            "Record every image hash in the build log.",
        ],
        warn=[
            ("NOTE", "Software build instructions live with each firmware tree, not on this card.")
        ],
        source="avionics/README.md; gcs/AGENTS.md",
    ),
    dict(
        slug="calibration",
        phase="PHASE 5 - FIRST FLIGHT",
        title="CALIBRATION: CG, TILT, NOZZLE",
        sub="CG on the hover thrust line, Y 12.86 in (326.7 mm)",
        view=dict(
            highlight=["Wing_Port", "Wing_Stbd", "Nacelle_Port_Trunnion", "Nacelle_Stbd_Trunnion"],
            hide=UNPLACED,
            dir=(0.55, -0.25, 1.0),
            margin=1.1,
        ),
        parts=[
            ("1", "digital angle gauge", ""),
            ("1", "scale + knife-edge balance", ""),
            ("1", "GCS laptop", ""),
        ],
        steps=[
            "Balance the aircraft on the tilt axis: CG target = hover thrust line, Y 12.86 in "
            "(326.7 mm) aft of the nose.",
            "Zero each AK7455 at 0 deg (cruise) with the angle gauge.",
            "Sweep each nacelle -5 -> 135 deg; both track within 2 deg at 0 and 90 deg.",
            "Verify the nozzle schedule: 75 % at 0 deg, 105 % from 90 to 140 deg.",
            PENDING,
        ],
        warn=[("NOTE", "CG reference: docs/BATTERY_SPLIT_OPTIONS.md (thrust line Y +326.7).")],
        source="docs/BATTERY_SPLIT_OPTIONS.md; REVN_BUILD_GUIDE_24IN.md Phase 3 checks",
    ),
    dict(
        slug="test_flight",
        phase="PHASE 5 - FIRST FLIGHT",
        title="GROUND TEST AND FIRST FLIGHT",
        sub="Tethered first, then free hover",
        view=dict(highlight=[], hide=UNPLACED, dir=(1.0, -1.0, 0.2), margin=1.05),
        parts=[
            ("1", "tether straps + anchored bench", ""),
            ("1", "GCS laptop with C2 link", ""),
            ("1", "IR thermometer", ""),
            ("1", "FAA registration on the airframe", "REF-FAA-001"),
        ],
        steps=[
            "Tether the aircraft firmly before any spin-up.",
            "Verify C2 heartbeat, attitude, tilt, and nozzle response on the ground.",
            PENDING,
            "Operate under 14 CFR Part 107 (REF-FAA-002).",
        ],
        warn=[
            (
                "WARNING",
                "Spinning EDFs and a free aircraft can cause serious injury. "
                "Keep all people clear of the duct plane and the flight area.",
            ),
            ("WARNING", "The landing gear is not flight-cleared; see card 08."),
        ],
        source="REVN_BUILD_GUIDE_24IN.md Phase 5; REFERENCES.md REF-FAA-001/002",
    ),
    dict(
        slug="markings",
        phase="PHASE 8 - FINISH",
        title="MARKINGS AND DECALS",
        sub="FAA registration marking first, show decals second",
        view=dict(
            highlight=["Hull_Forward", "Hull_Aft"],
            hide=UNPLACED,
            dir=(0.0, 0.0, 1.0),
            margin=1.05,
        ),
        parts=[
            ("1", "FAA registration number marking", "REF-FAA-001 (14 CFR Part 48)"),
            ("1", "decal sheet", "graphical-build-guide/decal_sheet.svg"),
            ("", "soft cloth, warm water", ""),
        ],
        steps=[
            "Apply your issued FAA registration number where it is visible on inspection.",
            "Replace every placeholder number on the decal sheet with your issued number.",
            "Apply the show decals from decal_sheet.svg.",
            "Keep markings clear of the access covers and the nacelle ESC covers.",
        ],
        warn=[
            ("NOTE", "Fan-work markings are decorative; the FAA marking is the only required one.")
        ],
        source="REFERENCES.md REF-FAA-001; decal_sheet.svg",
    ),
]
assert len(CARDS) == N_CARDS, len(CARDS)

ATTRIB = (
    "Hull: misubisu CC BY-SA 4.0 · Iris-nozzle concept: BamJr CC BY 4.0 · "
    "Fan work inspired by Firefly/Serenity © Joss Whedon / Mutant Enemy / Universal — not licensed"
)
LICENSE = (
    "© 2026 Steve Griffing (Stab-Rabbit-coding) · CC BY-SA 4.0 · "
    "card art: Claude (Opus 5.5) from the master assembly"
)
LEVEL_COLOR = {"WARNING": "#b3261e", "CAUTION": "#c77700", "NOTE": "#2b5c8a"}


def card_name(i, card):
    """Return the SVG file name for card i."""
    return f"build_guide_{i:02d}_{card['slug']}.svg"


def write_views(path):
    """Write the render view list for build_guide_card_renders.py."""
    views = []
    for i, card in enumerate(CARDS):
        v = dict(card["view"])
        v.setdefault("hide", UNPLACED)
        v["name"] = f"card{i:02d}"
        views.append(v)
    views.append(
        dict(name="components", highlight=[], hide=UNPLACED, dir=(1.0, -1.1, 0.75), margin=1.05)
    )
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(views, fh, indent=1)
    print(f"[cards] {len(views)} views -> {path}")


def tspan_lines(x, y, text, width, size, lh, attrs=""):
    """Return (svg, new_y) for word-wrapped text."""
    out = []
    for line in textwrap.wrap(text, width) or [""]:
        out.append(f'<text x="{x}" y="{y}" font-size="{size}" {attrs}>{escape(line)}</text>')
        y += lh
    return "\n".join(out), y


def card_svg(i, card):
    """Build one 1200 x 900 card."""
    o = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        'viewBox="0 0 1200 900" width="1200" height="900" '
        'font-family="DejaVu Sans, Helvetica, Arial, sans-serif">',
        f"<title>Serenity UAV build guide {i:02d} - {escape(card['title'])}</title>",
        "<metadata>SPDX-License-Identifier: CC-BY-SA-4.0. Generated by "
        "tools/gen_build_guide_cards.py; edit the CARDS table, not this file.</metadata>",
        '<rect width="1200" height="900" fill="#f7f5f0"/>',
        '<rect width="1200" height="96" fill="#1f2a36"/>',
        '<text x="28" y="30" font-size="13" fill="#9fb3c8" letter-spacing="2">'
        "SERENITY-CLASS TILTROTOR UAV · BUILD GUIDE · REV T+</text>",
        f'<text x="28" y="64" font-size="27" font-weight="bold" '
        f'fill="#ffffff">{escape(card["title"])}</text>',
        f'<text x="28" y="86" font-size="14" fill="#d6dee6">{escape(card["sub"])}</text>',
    ]
    if i:
        o += [
            '<rect x="1050" y="12" width="132" height="72" rx="8" fill="#e8892a"/>',
            '<text x="1116" y="36" font-size="12" fill="#1f2a36" text-anchor="middle">STEP</text>',
            f'<text x="1116" y="72" font-size="32" font-weight="bold" fill="#1f2a36" '
            f'text-anchor="middle">{i}/{N_CARDS - 1}</text>',
            f'<text x="1036" y="86" font-size="12" fill="#e8892a" '
            f'text-anchor="end">{escape(card["phase"])}</text>',
        ]
    # render
    o += [
        '<rect x="20" y="110" width="760" height="450" rx="6" fill="#ffffff" stroke="#c9c4b8"/>',
        f'<image x="30" y="116" width="740" height="410" preserveAspectRatio="xMidYMid meet" '
        f'xlink:href="{render_href(f"card{i:02d}.png")}"/>',
        '<rect x="32" y="534" width="14" height="14" fill="#ff5c00"/>'
        '<text x="52" y="546" font-size="12" fill="#444">this step</text>'
        '<rect x="128" y="534" width="14" height="14" fill="#dbdbd9" stroke="#999"/>'
        '<text x="148" y="546" font-size="12" fill="#444">already built / context</text>',
    ]
    # parts column
    o.append(
        '<rect x="796" y="110" width="384" height="450" rx="6" fill="#ffffff" stroke="#c9c4b8"/>'
    )
    o.append(
        '<text x="812" y="136" font-size="15" font-weight="bold" fill="#1f2a36">'
        + ("AT A GLANCE" if i == 0 else "PARTS NEEDED")
        + "</text>"
    )
    y = 162
    for qty, item, ref in card["parts"]:
        if qty:
            bw = max(46, 8 * len(qty) + 18)  # badge grows with "2+2+2"
            o.append(
                f'<rect x="812" y="{y - 15}" width="{bw}" height="21" rx="4" fill="#1f2a36"/>'
                f'<text x="{812 + bw / 2}" y="{y}" font-size="12" fill="#fff" '
                f'text-anchor="middle">{escape(qty)}x</text>'
            )
        tx = 812 + max(46, 8 * len(qty) + 18) + 8 if qty else 812
        svg, y2 = tspan_lines(tx, y, item, 36 if qty else 43, 13, 16, 'fill="#222"')
        o.append(svg)
        if ref:
            svg, y2 = tspan_lines(tx, y2, ref, 40, 11, 14, 'fill="#7a6f5c"')
            o.append(svg)
        y = y2 + 10
    # steps
    o.append(
        '<text x="28" y="592" font-size="15" font-weight="bold" fill="#1f2a36">'
        + ("SEQUENCE" if i == 0 else "INSTRUCTIONS")
        + "</text>"
    )
    y = 618
    for n, step in enumerate(card["steps"], 1):
        o.append(
            f'<circle cx="40" cy="{y - 5}" r="11" fill="#e8892a"/>'
            f'<text x="40" y="{y}" font-size="12" font-weight="bold" fill="#1f2a36" '
            f'text-anchor="middle">{n}</text>'
        )
        svg, y = tspan_lines(60, y, step, 96, 13, 17, 'fill="#222"')
        o.append(svg)
        y += 5
    # warnings, bottom-up above the footer
    wy = max(y + 4, 760)
    for level, text in card["warn"]:
        lines = textwrap.wrap(text, 128)
        h = 22 + 15 * len(lines)
        o.append(
            f'<rect x="20" y="{wy}" width="1160" height="{h}" rx="5" fill="#ffffff" '
            f'stroke="{LEVEL_COLOR[level]}" stroke-width="2"/>'
        )
        o.append(
            f'<text x="32" y="{wy + 17}" font-size="12" font-weight="bold" '
            f'fill="{LEVEL_COLOR[level]}">{level}</text>'
        )
        ty = wy + 17
        for line in lines:
            o.append(f'<text x="110" y="{ty}" font-size="12" fill="#222">{escape(line)}</text>')
            ty += 15
        wy += h + 6
    height = max(900, wy + 60)
    o[1] = o[1].replace(
        'viewBox="0 0 1200 900" width="1200" height="900"',
        f'viewBox="0 0 1200 {height}" width="1200" height="{height}"',
    )
    o[4] = f'<rect width="1200" height="{height}" fill="#f7f5f0"/>'
    fy = height - 44
    o += [
        f'<line x1="20" y1="{fy - 8}" x2="1180" y2="{fy - 8}" stroke="#c9c4b8"/>',
        f'<text x="28" y="{fy + 6}" font-size="11" fill="#555">SOURCE: '
        f'{escape(card["source"])}</text>',
        f'<text x="28" y="{fy + 21}" font-size="10" fill="#777">{escape(ATTRIB)}</text>',
        f'<text x="28" y="{fy + 35}" font-size="10" fill="#777">{escape(LICENSE)}</text>',
        "</svg>",
    ]
    return "\n".join(o) + "\n"


PHASES = [  # build_plan rows, from REVN_BUILD_GUIDE_24IN.md Phase Overview
    ("0", "Print all parts + CF cuts", "01-05", "All parts printed, cut, machined"),
    ("1", "Hull structure + provisions", "06-09", "Hull joined, wing root, gear, cargo doors"),
    ("2", "Nacelle assembly", "12-14", "EDFs, servo nozzle, ESC power route"),
    ("3", "Tilt mechanism", "10-11", "Worm drive, brake, trunnion, -5/135 deg stops"),
    ("4", "Foam pour + close-up", "15-16", "Void formers, foam, lids"),
    (
        "5",
        "Minimum viable flyer",
        "17, 23-25",
        "First nodes, software, calibration, tethered hover",
    ),
    ("6", "Full 8-node architecture", "18-22", "Buses, security, lights, C2, sensors"),
    ("7", "Cargo system", "09", "Doors, latch, winch delivery"),
    ("8", "Finishing", "26", "Markings, records"),
    ("9-10", "Tuning + advanced autonomy", "-", "Flight envelope, BVLOS readiness"),
    ("11", "Aft EDF (deferred)", "-", "deferred/AGENTS.md"),
]


def build_plan_svg():
    """Master build-sequence chart."""
    o = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 760" width="1200" height="760" '
        'font-family="DejaVu Sans, Helvetica, Arial, sans-serif">',
        "<title>Serenity UAV Rev T+ phased build plan</title>",
        "<metadata>SPDX-License-Identifier: CC-BY-SA-4.0. Generated by "
        "tools/gen_build_guide_cards.py.</metadata>",
        '<rect width="1200" height="760" fill="#f7f5f0"/><rect width="1200" height="80" '
        'fill="#1f2a36"/>',
        '<text x="28" y="48" font-size="26" font-weight="bold" fill="#fff">PHASED BUILD PLAN — REV '
        'T+</text>',
        '<text x="28" y="70" font-size="13" fill="#d6dee6">Install every conduit, void former, and '
        'mount '
        "before the foam pour (Phase 4). Phase 11 is deferred.</text>",
    ]
    y = 104
    for ph, name, cards, goal in PHASES:
        o.append(
            f'<rect x="28" y="{y}" width="1144" height="50" rx="6" fill="#fff" stroke="#c9c4b8"/>'
        )
        o.append(f'<rect x="28" y="{y}" width="92" height="50" rx="6" fill="#e8892a"/>')
        o.append(
            f'<text x="74" y="{y + 32}" font-size="18" font-weight="bold" fill="#1f2a36" '
            f'text-anchor="middle">{ph}</text>'
        )
        o.append(
            f'<text x="136" y="{y + 22}" font-size="15" font-weight="bold" '
            f'fill="#1f2a36">{escape(name)}</text>'
        )
        o.append(f'<text x="136" y="{y + 41}" font-size="12" fill="#444">{escape(goal)}</text>')
        o.append(
            f'<text x="1156" y="{y + 32}" font-size="13" fill="#7a6f5c" text-anchor="end">'
            f"cards {escape(cards)}</text>"
        )
        y += 58
    o += [
        f'<text x="28" y="{y + 14}" font-size="11" fill="#555">SOURCE: REVN_BUILD_GUIDE_24IN.md '
        "Phase Overview. Card numbers are the drawing sequence; follow phase order.</text>",
        f'<text x="28" y="{y + 30}" font-size="10" fill="#777">{escape(LICENSE)}</text>',
        "</svg>",
    ]
    return "\n".join(o) + "\n"


SUBSYSTEMS = [  # components_overview, from the guide's Rev T+ Configuration table
    ("Hull", "4 printed sections + 3 splice collars, foam-filled, 24.00 in (609.6 mm)"),
    ("Wing", "S1223-derived; FIXED bonded 20 mm CF spar; bonded root flanges"),
    ("Nacelle", "64 mm tandem-EDF pod on a 2 x 6704ZZ trunnion"),
    ("Tilt", "20D 25:1 + six-start worm, pin brake, 14T/50T; stops -5/135 deg"),
    ("Nozzle", "Rev T3 shingled 8-flap; servo on measured tilt; spring to 105 %"),
    ("Gear", "3.0 in (76 mm) R6 legs, A1b couple, 4 conforming bays"),
    ("Cargo", "Lapped clamshell doors, bell-crank latch, door gateway, winch"),
    ("Avionics", "8 PB2-I nodes (4 Pilot + 4 TACCO) + Observer, Flight Engineer, Commo"),
    ("Power", "Flight Engineer PDB -> 10 AWG through the spar -> nacelle ESCs"),
    ("C2", "Wi-Fi, Zigbee, mLRS (TACCO); SiK 915 MHz, 49 MHz (Commo)"),
]


def components_svg():
    """Subsystem map around the whole-aircraft render."""
    o = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        'viewBox="0 0 1200 760" width="1200" height="760" font-family="DejaVu Sans, Helvetica, '
        'Arial, sans-serif">',
        "<title>Serenity UAV Rev T+ components overview</title>",
        "<metadata>SPDX-License-Identifier: CC-BY-SA-4.0. Generated by "
        "tools/gen_build_guide_cards.py.</metadata>",
        '<rect width="1200" height="760" fill="#f7f5f0"/><rect width="1200" height="80" '
        'fill="#1f2a36"/>',
        '<text x="28" y="48" font-size="26" font-weight="bold" fill="#fff">COMPONENTS OVERVIEW — '
        'REV T+</text>',
        '<text x="28" y="70" font-size="13" fill="#d6dee6">Rendered from the FreeCAD master '
        'assembly; '
        "port nacelle at cruise, starboard at hover.</text>",
        '<image x="20" y="96" width="700" height="408" '
        f'xlink:href="{render_href("components.png")}" preserveAspectRatio="xMidYMid meet"/>',
    ]
    y = 112
    for name, text in SUBSYSTEMS:
        o.append(
            f'<text x="740" y="{y}" font-size="14" font-weight="bold" '
            f'fill="#e8892a">{escape(name)}</text>'
        )
        svg, y = tspan_lines(740, y + 18, text, 50, 12, 15, 'fill="#222"')
        o.append(svg)
        y += 12
    o += [
        '<text x="28" y="724" font-size="11" fill="#555">SOURCE: REVN_BUILD_GUIDE_24IN.md '
        "Rev T+ Configuration; authority documents listed there.</text>",
        f'<text x="28" y="740" font-size="10" fill="#777">{escape(LICENSE)}</text>',
        "</svg>",
    ]
    return "\n".join(o) + "\n"


def main():
    """CLI: `views PATH` or `svg`."""
    if len(sys.argv) >= 3 and sys.argv[1] == "views":
        write_views(sys.argv[2])
        return 0
    if len(sys.argv) == 2 and sys.argv[1] == "svg":
        for i, card in enumerate(CARDS):
            with open(os.path.join(GUIDE, card_name(i, card)), "w", encoding="utf-8") as fh:
                fh.write(card_svg(i, card))
        for name, body in (
            ("build_plan.svg", build_plan_svg()),
            ("components_overview.svg", components_svg()),
        ):
            with open(os.path.join(GUIDE, name), "w", encoding="utf-8") as fh:
                fh.write(body)
        print(f"[cards] wrote {len(CARDS)} cards + build_plan + components_overview")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
