#!/usr/bin/env python3
"""sls_print_orientation.py -- build orientation for every printed Serenity
part on the 3D Systems SLS 380 (15 x 13 x 18 in), chosen so each part's most
critical tensile / bending stress lies IN the build plane (machine X-Y).

Why: DuraForm PA CF [REF-MAT-015] publishes XY properties only.  Fibre-filled
SLS is weakest ACROSS the layers (build Z), and the sizing tools carry an
ASSUMED 0.5 Z knockdown (tools/sls_materials.py, WBS 0.12).  Putting the
critical stress in X-Y lets that knockdown be dropped for that load.
DuraForm PA11 [REF-MAT-016] is near-isotropic, so its parts are oriented for
finish and fit instead.

Method, per part (table ORIENT below, one row per printed STL):
  * STL frame = the file's own axes.  Hull-frame parts use the aircraft datum
    R2: X = lateral (stbd +), Y = longitudinal, Z = vertical.
  * The row names which STL axis becomes build Z, the critical load, and why.
    Rules used, in order of preference:
      R-PLATE  plates / panels in bending: plate normal -> build Z (bending
               stress runs in the plate plane; every layer carries it).
      R-RING   rings, sleeves, gears, revolved ducts: axis of revolution ->
               build Z (hoop stress and tooth-root bending in plane; round
               bores are not stair-stepped).
      R-BEAM   beams, shafts, cantilevers, hull shells in longitudinal
               bending: the span axis stays IN plane; the least-loaded
               cross axis -> build Z.
  * The two in-plane axes are then laid on machine X/Y in whichever way
    fits; rotation about build Z does not change strength.
  * Envelope check against 381.0 x 330.2 x 457.2 mm (owner 2026-11-01,
    [REF-MFG-001 p. 17]), axis-aligned, no nesting margin.  A part that
    fits only in a weaker orientation is reported as CONFLICT, never
    silently re-oriented.

Run:  /usr/bin/python3 tools/sls_print_orientation.py
Writes docs/sls-study/sls_print_orientation.json and prints the table that
docs/SLS_PRINT_ORIENTATION.md is built from.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP (Stab-Rabbit-coding)
AI note: Written by Claude Opus 5.5 (Anthropic) under the author's direction,
         2026-11-01.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

import json
import os
import sys

import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
STL = os.path.join(ROOT, "airframe", "stls")
ENV_XY = (15 * 25.4, 13 * 25.4)   # 381.0 x 330.2 mm build plane
ENV_Z = 18 * 25.4                 # 457.2 mm build height
AX = "XYZ"

# part (path under airframe/stls) : (STL axis -> build Z, material,
#                                    critical load, rule + reason, confidence)
# confidence: "H" geometry and load path both documented in repo;
#             "M" load path inferred from the part's function;
#             "V" verify -- frame or load path not confirmed in source.
HULL = ("Z", "PA CF", "fuselage vertical bending -> longitudinal (Y) skin stress",
        "R-BEAM: Y and X in plane, hull vertical -> Z; ring frames and webs "
        "stand vertical so their in-plane bending is in X-Y too", "H")
ORIENT = {
    # ---- bow / head ------------------------------------------------------
    "fuselage/bow_sensor_faceplate.stl": ("Z", "PA CF", "panel bending (handling)", "R-PLATE", "M"),
    "fuselage/head/bow_sensor_bay_insert.stl": ("Z", "PA CF", "sensor mount bending", "R-PLATE: base flange flat", "M"),
    "fuselage/head_shell24.stl": HULL,
    "fuselage/head_shell24_2mm_repaired.stl": HULL,
    "fuselage/head/head_cell_rail.stl": ("Z", "PA CF", "fwd/aft crash load into longitudinal webs (Y)",
                                         "R-BEAM: webs run along Y, stand vertical; ceiling bending in X-Y "
                                         "(tools/gen_head_cell_rail.py)", "H"),
    "fuselage/head/head_cell_sled.stl": ("Z", "PA CF", "floor bending under cell, fwd/aft crash (Y)", "R-PLATE", "H"),
    "fuselage/head/head_cell_catch.stl": ("Z", "PA CF", "leaf-spring bending along X (LEAF_T is Z)",
                                          "R-PLATE: leaf strain in plane, 0.5 % << 3.8 %", "H"),
    "fuselage/head/twin_pack_tray.stl": ("Z", "PA CF", "ceiling + side-wall bending under packs", "R-BEAM", "M"),
    "fuselage/head/twin_pack_sled.stl": ("Z", "PA CF", "sled floor bending", "R-PLATE", "M"),
    "fuselage/head/twin_pack_gate.stl": ("Y", "PA CF", "gate plate bending under pack fwd load",
                                         "R-PLATE: normal is Y (4 mm)", "M"),
    "fuselage/head_cargo_splice_collar.stl": ("Z", "PA CF", "splice moment -> Y tension at crown/keel",
                                              "R-BEAM: same frame as hull so crown/keel Y stress is in plane", "H"),
    "fuselage/head_cargo_shell24_2mm_merged.stl": HULL,
    # ---- cargo -----------------------------------------------------------
    "fuselage/cargo/cargo_sect_shell24_2mm_repaired.stl": HULL,
    "fuselage/cargo/cargo_sect_shell24_repaired.stl": HULL,
    "fuselage/battery_tray.stl": ("Z", "PA CF", "battery inertia fwd/aft (Y) + vertical g", "R-BEAM", "M"),
    "fuselage/cargo/battery_cradle.stl": ("Z", "PA CF", "inverted-U cradle bending under battery g",
                                          "R-BEAM: U legs vertical, span X in plane", "M"),
    "fuselage/cargo/cargo_cradle_autolatch.stl": ("Z", "PA CF", "payload hook load, vertical", "R-BEAM", "V"),
    "fuselage/cargo/cargo_door_port.stl": ("Z", "PA CF", "door panel bending (air load)", "R-PLATE", "H"),
    "fuselage/cargo/cargo_door_stbd.stl": ("Z", "PA CF", "door panel bending (air load)", "R-PLATE", "H"),
    "fuselage/cargo/cargo_hinge_retention.stl": ("Z", "PA CF", "hinge-pin retention plate bending", "R-PLATE", "M"),
    "fuselage/cargo/door_latch_crank_port.stl": ("Z", "PA CF", "crank arm bending about pivot", "R-PLATE: arm in plane", "M"),
    "fuselage/cargo/door_latch_crank_stbd.stl": ("Z", "PA CF", "crank arm bending about pivot", "R-PLATE: arm in plane", "M"),
    "fuselage/cargo/door_latch_bracket_port.stl": ("Z", "PA CF", "pivot-boss bearing + base bending", "R-PLATE", "M"),
    "fuselage/cargo/door_latch_bracket_stbd.stl": ("Z", "PA CF", "pivot-boss bearing + base bending", "R-PLATE", "M"),
    "fuselage/cargo/door_horn.stl": ("Y", "PA CF", "horn arm bending (servo torque)", "R-PLATE: thinnest axis Y", "M"),
    "fuselage/cargo/cargo_door_servo_bracket.stl": ("Z", "PA CF", "servo-ear bending", "R-PLATE", "M"),
    "fuselage/cargo/cargo_release_servo_bracket.stl": ("Z", "PA CF", "servo-ear bending", "R-PLATE", "M"),
    "fuselage/cargo/cargo_drv8833_tray.stl": ("Z", "PA CF", "board tray, light", "R-PLATE", "M"),
    "fuselage/cargo/gateway_door_tray.stl": ("Y", "PA CF", "board tray, light", "R-PLATE: normal is Y (15 mm)", "V"),
    "fuselage/cargo/chin_node_shelf.stl": ("Z", "PA CF", "shelf bending under node", "R-PLATE", "H"),
    "fuselage/cargo/cargo_fpv_bezel.stl": ("Z", "PA CF", "cosmetic / light", "R-PLATE", "M"),
    "fuselage/cargo/cargo_gps_retention_ring.stl": ("Z", "PA CF", "ring hoop", "R-RING", "M"),
    "fuselage/cargo/cargo_vera_faraday.stl": ("Z", "PA CF", "enclosure, light", "R-PLATE: base flat", "M"),
    "fuselage/cargo/cargo_winch_motor_mount.stl": ("Z", "PA CF", "motor torque reaction in base", "R-PLATE", "M"),
    "fuselage/cargo/cargo_winch_spool.stl": ("Z", "PA CF", "line tension -> drum hoop + flange bending",
                                             "R-RING: drum axis Z", "M"),
    "fuselage/cargo/tilt_actuator_bracket_port.stl": ("X", "PA CF", "worm thrust + wheel reaction in bracket plate (Y-Z)",
                                                      "R-PLATE: plate normal X (28 mm)", "M"),
    "fuselage/cargo/tilt_actuator_bracket_stbd.stl": ("X", "PA CF", "worm thrust + wheel reaction in bracket plate (Y-Z)",
                                                      "R-PLATE: plate normal X (28 mm)", "M"),
    "fuselage/cargo/tilt_actuator_wheel.stl": ("X", "PA CF", "worm-wheel tooth-root bending",
                                               "R-RING: wheel axis X (13 mm face)", "H"),
    "fuselage/cargo/tilt_actuator_worm.stl": ("X", "PA CF", "thread-root shear along the worm axis (Y) + shaft torsion",
                                              "R-BEAM: worm axis Y stays in plane", "M"),
    "fuselage/cargo/tilt_brake_guide.stl": ("Z", "PA CF", "brake-pin bore hoop + side load", "R-RING: bore axis Z", "V"),
    "fuselage/cargo/tilt_brake_guide_stbd.stl": ("Z", "PA CF", "brake-pin bore hoop + side load", "R-RING: bore axis Z", "V"),
    "fuselage/inara_access_cover.stl": ("Z", "PA CF", "cover panel bending", "R-PLATE", "H"),
    "fuselage/river_access_cover.stl": ("Z", "PA CF", "cover panel bending", "R-PLATE", "H"),
    "fuselage/belly_panel.stl": ("Y", "PA CF", "panel bending", "R-PLATE: normal is Y (3.5 mm)", "V"),
    "fuselage/cargo_middle_splice_collar.stl": ("Z", "PA CF", "splice moment -> Y tension at crown/keel",
                                                "R-BEAM: same frame as hull", "H"),
    "fuselage/wing_root_flange_port.stl": ("X", "PA CF", "wing root moment -> flange plate bending (Y-Z plane)",
                                           "R-PLATE: flange normal X (26 mm)", "H"),
    "fuselage/wing_root_flange_stbd.stl": ("X", "PA CF", "wing root moment -> flange plate bending (Y-Z plane)",
                                           "R-PLATE: flange normal X (26 mm)", "H"),
    # ---- middle / rear ---------------------------------------------------
    "fuselage/middle_shell24_2mm_repaired.stl": HULL,
    "fuselage/middle_canonical_shell24.stl": ("Z", "PA CF", "fuselage bending (frame not confirmed)", "R-BEAM", "V"),
    "fuselage/middle_canonical_edf_intake.stl": ("Z", "PA CF", "intake duct, light", "R-BEAM", "V"),
    "fuselage/middle_rear_splice_collar.stl": ("Z", "PA CF", "splice moment -> Y tension at crown/keel",
                                               "R-BEAM: same frame as hull", "H"),
    "fuselage/rear_shell24_2mm_repaired.stl": HULL,
    "fuselage/dorsal_antenna_fin.stl": ("Y", "PA CF", "fin root bending (side gust)", "R-PLATE: normal is Y (4 mm)", "M"),
    # ---- landing gear (print-frame files only) ---------------------------
    "fuselage/landing-gear/lg_r6_3_0in_leg_frame.stl": ("Z", "PA CF", "leg frame in-plane bending (strike)",
                                                        "R-PLATE: frame plane X-Y, 16 mm thick", "H"),
    "fuselage/landing-gear/lg_r6_3_0in_leg_frame_fore.stl": ("Z", "PA CF", "leg frame in-plane bending (strike)",
                                                             "R-PLATE", "H"),
    "fuselage/landing-gear/lg_r6_1_5in_leg_frame.stl": ("Z", "PA CF", "bench/handling article", "R-PLATE", "H"),
    "fuselage/landing-gear/lg_r6_common_foot.stl": ("Z", "PA11", "ground strike; PA11 isotropic",
                                                    "sole flat for finish", "H"),
    "fuselage/landing-gear/lg_r6_3_0in_bay_aft-port_print.stl": ("X", "PA CF", "leg side-load bending along the socket axis (print Z)",
                                                                 "R-BEAM: socket axis in plane", "V"),
    "fuselage/landing-gear/lg_r6_3_0in_bay_aft-stbd_print.stl": ("X", "PA CF", "leg side-load bending along the socket axis (print Z)",
                                                                 "R-BEAM: socket axis in plane", "V"),
    "fuselage/landing-gear/lg_r6_3_0in_bay_fore-port_print.stl": ("X", "PA CF", "leg side-load bending along the socket axis (print Z)",
                                                                  "R-BEAM: socket axis in plane", "V"),
    "fuselage/landing-gear/lg_r6_3_0in_bay_fore-stbd_print.stl": ("X", "PA CF", "leg side-load bending along the socket axis (print Z)",
                                                                  "R-BEAM: socket axis in plane", "V"),
    "fuselage/landing-gear/lg_r6_common_bay.stl": ("X", "PA CF", "leg side-load bending along the socket axis (Z)",
                                                   "R-BEAM: socket axis in plane", "V"),
    "fuselage/landing-gear/lg_a1b_housing_fore-port.stl": ("Y", "PA CF", "balanced-couple housing; metal carries the couple",
                                                           "R-BEAM: long axis Z in plane", "V"),
    "fuselage/landing-gear/lg_a1b_housing_fore-stbd.stl": ("Y", "PA CF", "balanced-couple housing; metal carries the couple",
                                                           "R-BEAM: long axis Z in plane", "V"),
    # ---- wings -----------------------------------------------------------
    "wings/wing_port_s1223_revo.stl": ("Z", "PA CF", "spanwise bending (CF spar is primary)",
                                       "R-PLATE: airfoil thickness Z; span + chord in plane", "H"),
    "wings/wing_stbd_s1223_revo.stl": ("Z", "PA CF", "spanwise bending (CF spar is primary)",
                                       "R-PLATE: airfoil thickness Z; span + chord in plane", "H"),
    "wings/wing_tilt_pinion_port.stl": ("X", "PA CF", "14T pinion tooth-root bending", "R-RING: gear axis X", "H"),
    "wings/wing_tilt_pinion_stbd.stl": ("X", "PA CF", "14T pinion tooth-root bending", "R-RING: gear axis X", "H"),
    # ---- nacelles (port + stbd) -----------------------------------------
    "nacelles/nacelle_port_64mm.stl": ("Z", "PA CF", "pod bending about trunnion -> axial (Y) duct stress",
                                       "R-BEAM: duct axis Y in plane", "H"),
    "nacelles/nacelle_stbd_64mm.stl": ("Z", "PA CF", "pod bending about trunnion -> axial (Y) duct stress",
                                       "R-BEAM: duct axis Y in plane", "H"),
    "nacelles/nacelle_port_revs.stl": ("Z", "PA CF", "legacy 50 mm pod", "R-BEAM: duct axis Y in plane", "M"),
    "nacelles/nacelle_stbd_revs.stl": ("Z", "PA CF", "legacy 50 mm pod", "R-BEAM: duct axis Y in plane", "M"),
    "nacelles/eng_left_shell24_50mm_repaired.stl": ("X", "PA CF", "legacy 50 mm pod, duct axis Z in this file",
                                                    "R-BEAM: duct axis in plane", "M"),
    "nacelles/eng_right_shell24_50mm_repaired.stl": ("X", "PA CF", "legacy 50 mm pod, duct axis Z in this file",
                                                     "R-BEAM: duct axis in plane", "M"),
    "nacelles/nacelle_trunnion_64mm_port.stl": ("X", "PA CF", "2 x 6804 bearing seat (Ø32 H7) hoop + barrel-to-flange bending",
                                                "R-RING: bearing axis X -> Z keeps the H7 bore round; flange plate in plane", "M"),
    "nacelles/nacelle_trunnion_64mm_stbd.stl": ("X", "PA CF", "2 x 6804 bearing seat (Ø32 H7) hoop + barrel-to-flange bending",
                                                "R-RING: bearing axis X -> Z keeps the H7 bore round; flange plate in plane", "M"),
    "nacelles/nacelle_trunnion.stl": ("Z", "PA CF", "legacy 50 mm disc trunnion", "R-RING", "M"),
    "nacelles/nacelle_servo_bracket.stl": ("Z", "PA CF", "servo-ear bending", "R-PLATE", "V"),
    "nacelles/edf_motor_mount_64mm_stage2_stbd.stl": ("Z", "PA CF", "motor torque + thrust through stator vanes",
                                                      "R-RING: duct axis Z; vanes radial in plane", "M"),
    "nacelles/edf_stator_sleeve.stl": ("Z", "PA CF", "stator vane bending (swirl torque), sleeve hoop", "R-RING", "H"),
    "nacelles/edf_aft_spider_sleeve.stl": ("Z", "PA CF", "spider arm bending, sleeve hoop", "R-RING", "H"),
    "nacelles/esc/nacelle_esc_cover_port_a.stl": ("Y", "PA CF", "flush cover panel bending", "R-PLATE: normal Y", "M"),
    "nacelles/esc/nacelle_esc_cover_port_b.stl": ("Y", "PA CF", "flush cover panel bending", "R-PLATE: normal Y", "M"),
    "nacelles/esc/nacelle_esc_cover_stbd_a.stl": ("Y", "PA CF", "flush cover panel bending", "R-PLATE: normal Y", "M"),
    "nacelles/esc/nacelle_esc_cover_stbd_b.stl": ("Y", "PA CF", "flush cover panel bending", "R-PLATE: normal Y", "M"),
    "nacelles/nozzles/nacelle_nozzle_fixed.stl": ("Z", "PA CF", "duct hoop + bond-lip shear", "R-RING", "H"),
    "nacelles/nozzles/nacelle_nozzle_throat.stl": ("Z", "PA CF", "duct hoop", "R-RING", "H"),
    "nacelles/nozzles/nacelle_nozzle_ring.stl": ("Z", "PA CF", "unison-ring hoop + tooth bending", "R-RING", "H"),
    "nacelles/nozzles/nacelle_nozzle_flap.stl": ("X", "PA CF", "flap cantilever bending along its 50 mm length (Z)",
                                                 "R-BEAM: flap length in plane", "M"),
    "nacelles/nozzles/nacelle_nozzle_flap_seal.stl": ("X", "PA CF", "flap cantilever bending along its 50 mm length (Z)",
                                                      "R-BEAM: flap length in plane", "M"),
}
# Hull-frame copies of parts that ship a leg-local *_print.stl; not print files.
NOT_PRINT = {
    "fuselage/landing-gear/lg_r6_3_0in_bay_aft-port.stl", "fuselage/landing-gear/lg_r6_3_0in_bay_aft-stbd.stl",
    "fuselage/landing-gear/lg_r6_3_0in_bay_fore-port.stl", "fuselage/landing-gear/lg_r6_3_0in_bay_fore-stbd.stl",
}


def place(ext, zax):
    """Return (machine X, Y, Z extents, mapping, fits) for build-Z = STL axis zax."""
    zi = AX.index(zax)
    a, b = [i for i in range(3) if i != zi]
    for p, q in ((a, b), (b, a)):           # rotate 90 deg about build Z if needed
        if ext[p] <= ENV_XY[0] and ext[q] <= ENV_XY[1] and ext[zi] <= ENV_Z:
            return (ext[p], ext[q], ext[zi]), f"{AX[p]}->X {AX[q]}->Y {AX[zi]}->Z", True
    return (ext[a], ext[b], ext[zi]), f"{AX[a]}->X {AX[b]}->Y {AX[zi]}->Z", False


def main():
    on_disk = sorted(os.path.relpath(os.path.join(dp, f), STL)
                     for dp, _, fs in os.walk(STL) for f in fs if f.endswith(".stl"))
    audited = {r["part"].replace("airframe/stls/", "")
               for r in json.load(open(os.path.join(ROOT, "docs", "sls-study", "sls_dfm_audit.json")))}
    missing = sorted(audited - set(ORIENT) - NOT_PRINT)
    if missing:  # every printed part shall have an orientation
        print("NO ORIENTATION ASSIGNED:", *missing, sep="\n  ")
        return 1
    rows = []
    for part, (zax, mat, load, rule, conf) in ORIENT.items():
        if part not in on_disk:
            print(f"listed but not on disk: {part}")
            return 1
        ext = trimesh.load(os.path.join(STL, part), force="mesh").extents.tolist()
        mach, mapping, ok = place(ext, zax)
        row = {"part": part, "material": mat, "build_z_stl_axis": zax, "mapping": mapping,
               "machine_xyz_mm": [round(v, 1) for v in mach], "fits": ok,
               "critical_load": load, "rule": rule, "confidence": conf}
        if not ok:
            # report the strongest orientation that DOES fit, as a conflict
            alt = [(z, place(ext, z)) for z in AX if z != zax and place(ext, z)[2]]
            row["conflict"] = ("does not fit the SLS 380 in the strength orientation; fits only with "
                               + (", ".join(f"build Z = STL {z}" for z, _ in alt) or "no orientation"))
        rows.append(row)
        print(f"{'ok  ' if ok else 'CONF'} {part:58s} Z<-{zax} {mapping:20s} "
              f"{row['machine_xyz_mm']} {mat:6s} {conf}")
    out = os.path.join(ROOT, "docs", "sls-study", "sls_print_orientation.json")
    with open(out, "w") as fh:
        json.dump(rows, fh, indent=1)
    nc = sum(not r["fits"] for r in rows)
    print(f"\n{len(rows)} parts oriented, {nc} conflict(s) -> {os.path.relpath(out, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
