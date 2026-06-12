#!/usr/bin/env python3
"""
generate_placeholders.py — Serenity UAV non-printable component placeholder generator.

Generates dimensionally-accurate bounding-geometry STL files for every non-printable
component in the Rev R BOM (and the deferred Phase-11 rear-EDF items), suitable for
import into FreeCAD assembly exploded views and build guides.

Usage (no external dependencies required — standard library only):
    python3 airframe/placeholders/generate_placeholders.py

Output tree (relative to this script):
    propulsion/     EDFs, ESCs
    servos/         DS3218MG, SG90
    bearings/       MF104ZZ, MR63ZZ, 6804
    structural/     CF rods / tubes / bar / plate, PTFE sleeve
    avionics/       PocketBeagle2, Cape-A-2/B-2, XCVR-49MHZ-2, Kaylee PDB, microSD
    power/          LiPo packs, automotive fuses, Bourns shunt
    cargo/          N20 winch motor, HX711, DRV8833
    gears/          M=1.0 sector, pinion, bevel pair, crown (resin-print or SDP-SI)
    hardware/       hinge pins, heat-set inserts, screws, PTFE sleeve, cam straps
    lighting/       WS2812B ring, WS2812C-2020 SMD
    wiring/         PTFE conduit, representative wire bundle cross-sections
    gcs/            Malcolm enclosure, GCS LiPo, antenna types, tripod, encoders

Every STL header carries the marker "SerenityUAV PLACEHOLDER R1" (distinct from the
hull-frame baked STL marker).  Shapes are solid representations of each component's
outer envelope; hollow cylinder (tube) shapes are used where bore is assembly-critical.

Mesh quality: n=24 segments for small cylinders, n=32 for larger/primary ones.
All dimensions in millimetres, consistent with the project hull-frame standard.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0 — creativecommons.org/licenses/by/4.0

References:
    [1] current-specification/bom_revR.csv — Rev R BOM (canonical)
    [2] CLAUDE.md — project coordinate system and fabrication standards
    [3] Supplier datasheets: Surpass Hobby 2627-3200KV, DS3218MG, SG90, MF104ZZ,
        Tattu 6S 4000mAh, Hammond 1455N1601, Mini-Circuits ZFSC-2-1W-S+
"""

import math
import os
import struct

# ---------------------------------------------------------------------------
# Script-relative output root
# ---------------------------------------------------------------------------
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Binary STL primitives
# ---------------------------------------------------------------------------

_STL_HEADER = b"SerenityUAV PLACEHOLDER R1"


def _normal(v0, v1, v2):
    """Unit outward normal for triangle v0→v1→v2 (right-hand rule)."""
    ax = v1[0] - v0[0]
    ay = v1[1] - v0[1]
    az = v1[2] - v0[2]
    bx = v2[0] - v0[0]
    by = v2[1] - v0[1]
    bz = v2[2] - v0[2]
    nx = ay * bz - az * by
    ny = az * bx - ax * bz
    nz = ax * by - ay * bx
    length = math.sqrt(nx * nx + ny * ny + nz * nz)
    if length < 1e-12:
        return (0.0, 0.0, 1.0)
    return (nx / length, ny / length, nz / length)


def _T(v0, v1, v2):
    """Build (normal, v0, v1, v2) triangle record."""
    return (_normal(v0, v1, v2), v0, v1, v2)


def _write(path, tris):
    """Write binary STL; create parent directories as needed. Returns facet count."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    header = _STL_HEADER.ljust(80, b"\x00")
    with open(path, "wb") as fh:
        fh.write(header)
        fh.write(struct.pack("<I", len(tris)))
        for rec in tris:
            n, v0, v1, v2 = rec
            fh.write(struct.pack("<fff", *n))
            fh.write(struct.pack("<fff", *v0))
            fh.write(struct.pack("<fff", *v1))
            fh.write(struct.pack("<fff", *v2))
            fh.write(struct.pack("<H", 0))
    return len(tris)


def _out(subdir, filename):
    """Absolute output path inside placeholders/<subdir>/."""
    return os.path.join(_SCRIPT_DIR, subdir, filename)


# ---------------------------------------------------------------------------
# Geometric primitive builders — return list of (normal, v0, v1, v2) tuples
# ---------------------------------------------------------------------------

def _box(lx, ly, lz):
    """12-triangle solid box: (0,0,0) → (lx, ly, lz)."""
    x, y, z = lx, ly, lz
    return [
        # Bottom −Z
        _T((0, 0, 0), (x, y, 0), (x, 0, 0)),
        _T((0, 0, 0), (0, y, 0), (x, y, 0)),
        # Top +Z
        _T((0, 0, z), (x, 0, z), (x, y, z)),
        _T((0, 0, z), (x, y, z), (0, y, z)),
        # Front −Y
        _T((0, 0, 0), (x, 0, 0), (x, 0, z)),
        _T((0, 0, 0), (x, 0, z), (0, 0, z)),
        # Back +Y
        _T((0, y, 0), (x, y, z), (x, y, 0)),
        _T((0, y, 0), (0, y, z), (x, y, z)),
        # Left −X
        _T((0, 0, 0), (0, 0, z), (0, y, z)),
        _T((0, 0, 0), (0, y, z), (0, y, 0)),
        # Right +X
        _T((x, 0, 0), (x, y, 0), (x, y, z)),
        _T((x, 0, 0), (x, y, z), (x, 0, z)),
    ]


def _cyl(r, h, n=32):
    """4n-triangle solid cylinder: base Z=0, top Z=h, axis +Z."""
    ang = [2.0 * math.pi * k / n for k in range(n)]
    vb = [(r * math.cos(a), r * math.sin(a), 0.0) for a in ang]
    vt = [(r * math.cos(a), r * math.sin(a), h) for a in ang]
    bc, tc = (0.0, 0.0, 0.0), (0.0, 0.0, h)
    tris = []
    for k in range(n):
        k1 = (k + 1) % n
        tris.append(_T(bc, vb[k1], vb[k]))          # bottom cap −Z
        tris.append(_T(tc, vt[k], vt[k1]))          # top cap +Z
        tris.append(_T(vb[k], vb[k1], vt[k1]))      # side quad T1
        tris.append(_T(vb[k], vt[k1], vt[k]))       # side quad T2
    return tris


def _tube(r_o, r_i, h, n=32):
    """8n-triangle hollow cylinder: base Z=0, top Z=h, outer R=r_o, bore R=r_i."""
    ang = [2.0 * math.pi * k / n for k in range(n)]
    ob = [(r_o * math.cos(a), r_o * math.sin(a), 0.0) for a in ang]
    ot = [(r_o * math.cos(a), r_o * math.sin(a), h) for a in ang]
    ib = [(r_i * math.cos(a), r_i * math.sin(a), 0.0) for a in ang]
    it = [(r_i * math.cos(a), r_i * math.sin(a), h) for a in ang]
    tris = []
    for k in range(n):
        k1 = (k + 1) % n
        # Bottom annulus −Z
        tris.append(_T(ob[k], ib[k1], ob[k1]))
        tris.append(_T(ob[k], ib[k],  ib[k1]))
        # Top annulus +Z
        tris.append(_T(ot[k], ot[k1], it[k1]))
        tris.append(_T(ot[k], it[k1], it[k]))
        # Outer wall +R
        tris.append(_T(ob[k], ob[k1], ot[k1]))
        tris.append(_T(ob[k], ot[k1], ot[k]))
        # Inner wall −R
        tris.append(_T(ib[k], it[k],  it[k1]))
        tris.append(_T(ib[k], it[k1], ib[k1]))
    return tris


def _sector(r, h, angle_deg, n_seg=None):
    """Solid disk sector 0°→angle_deg, height h (pie-wedge shape for sector gears)."""
    if n_seg is None:
        n_seg = max(4, int(round(32.0 * angle_deg / 360.0)))
    ar = math.radians(angle_deg)
    angs = [ar * k / n_seg for k in range(n_seg + 1)]
    vc = [(r * math.cos(a), r * math.sin(a)) for a in angs]
    bc, tc = (0.0, 0.0, 0.0), (0.0, 0.0, h)
    tris = []
    for k in range(n_seg):
        v0b = (vc[k][0],     vc[k][1],     0.0)
        v1b = (vc[k + 1][0], vc[k + 1][1], 0.0)
        v0t = (vc[k][0],     vc[k][1],     h)
        v1t = (vc[k + 1][0], vc[k + 1][1], h)
        tris.append(_T(bc, v1b, v0b))          # bottom −Z
        tris.append(_T(tc, v0t, v1t))          # top +Z
        tris.append(_T(v0b, v1b, v1t))         # arc face T1
        tris.append(_T(v0b, v1t, v0t))         # arc face T2
    # Flat radial face at angle = 0
    r0b = (r, 0.0, 0.0)
    r0t = (r, 0.0, h)
    tris.append(_T(bc, r0b, r0t))
    tris.append(_T(bc, r0t, tc))
    # Flat radial face at angle = angle_deg
    rab = (vc[-1][0], vc[-1][1], 0.0)
    rat = (vc[-1][0], vc[-1][1], h)
    tris.append(_T(bc, rat, rab))
    tris.append(_T(bc, tc, rat))
    return tris


def _translate(tris, dx, dy, dz):
    """Shift all vertices by (dx, dy, dz)."""
    def _shift(v):
        return (v[0] + dx, v[1] + dy, v[2] + dz)
    return [(n, _shift(v0), _shift(v1), _shift(v2)) for (n, v0, v1, v2) in tris]


def _cat(*tri_lists):
    """Concatenate triangle lists from multiple primitives into one mesh."""
    out = []
    for tl in tri_lists:
        out.extend(tl)
    return out


# ---------------------------------------------------------------------------
# Component generators — one function per unique physical component type
# ---------------------------------------------------------------------------

# ---- Propulsion ---------------------------------------------------------- #

def gen_edf_50mm_6s():
    """
    50 mm 6S EDF unit — Surpass Hobby / XFly Galaxy X5 2627-3200KV style.
    Outer duct envelope 50 mm OD × 50 mm long; motor can stub 27 mm dia.
    BOM: EDF-50-6S (×4, 2 per nacelle tandem).
    Ref [3]: XFly Galaxy X5 datasheet.
    """
    duct = _tube(25.0, 22.5, 50.0, n=32)          # 50 mm OD, 45 mm bore
    motor = _cyl(13.5, 28.0, n=24)                # 27 mm motor can
    motor = _translate(motor, 0.0, 0.0, 11.0)     # centred in duct
    return _cat(duct, motor)


def gen_edf_120mm_6s():
    """
    120 mm 6S EDF unit — Phase-11 rear EDF (deferred).
    Envelope 120 mm OD × 80 mm long; motor can 45 mm dia.
    BOM: EDF-120-6S (×1, deferred/aft-edf).
    """
    duct = _tube(60.0, 55.0, 80.0, n=32)
    motor = _cyl(22.5, 40.0, n=24)
    motor = _translate(motor, 0.0, 0.0, 20.0)
    return _cat(duct, motor)


def gen_esc_40a():
    """
    40 A 6S BLHeli32 ESC — DSHOT600.
    Envelope 65 × 35 × 15 mm (body + capacitors).
    BOM: ESC-40A-6S (×4).
    """
    return _box(65.0, 35.0, 15.0)


def gen_esc_80a():
    """
    80 A 6S BLHeli32 ESC — Phase-11 rear EDF (deferred).
    Envelope 72 × 38 × 18 mm.
    BOM: ESC-80A-6S (×1, deferred).
    """
    return _box(72.0, 38.0, 18.0)


# ---- Servos -------------------------------------------------------------- #

def gen_ds3218mg():
    """
    DS3218MG 25 kg·cm digital metal-gear servo.
    Body 40.7 × 20.2 × 38.0 mm; output spline stub 5.8 mm dia × 5 mm.
    BOM: SERVO-TILT (×2 nacelle tilt), MAL-GIMBAL-SERVO (×2 GCS gimbal).
    Ref [3]: DS3218MG datasheet.
    """
    body = _box(40.7, 20.2, 38.0)
    spline = _cyl(2.9, 5.0, n=16)
    spline = _translate(spline, 20.35 - 2.9, 10.1 - 2.9, 38.0)
    return _cat(body, spline)


def gen_sg90():
    """
    SG90 9 g micro servo.
    Body 22.2 × 11.8 × 22.0 mm; horn disk 12 mm dia × 1.5 mm.
    BOM: SERVO-CARGO (×2), SERVO-REAR-NOZZLE (×1).
    Ref [3]: SG90 datasheet.
    """
    body = _box(22.2, 11.8, 22.0)
    horn = _cyl(6.0, 1.5, n=16)
    horn = _translate(horn, 11.1 - 6.0, 5.9 - 6.0, 22.0)
    return _cat(body, horn)


# ---- Bearings ------------------------------------------------------------ #

def gen_brg_mf104zz():
    """
    MF104ZZ flanged ball bearing 4 × 10 × 4 mm.
    Outer race ring OD=10 mm, ID=4 mm, W=4 mm; flange OD=11.5 mm, W=0.5 mm.
    BOM: BRG-MF104ZZ (×4, 2 per nacelle pivot housing).
    """
    race = _tube(5.0, 2.0, 4.0, n=24)
    flange = _tube(5.75, 2.0, 0.5, n=24)          # slightly larger OD flange
    flange = _translate(flange, 0.0, 0.0, -0.5)   # at bottom (Z=-0.5 to 0)
    return _cat(race, flange)


def gen_brg_mr63zz():
    """
    MR63ZZ miniature ball bearing 3 × 6 × 2.5 mm.
    OD=6 mm, ID=3 mm, W=2.5 mm.
    BOM: BRG-MR63ZZ (×8, 2 per gear pinion/crown × 4 pinions).
    """
    return _tube(3.0, 1.5, 2.5, n=24)


def gen_brg_6804():
    """
    6804-2RS thin-section bearing 20 × 32 × 7 mm (GCS gimbal pan stage).
    OD=32 mm, ID=20 mm, W=7 mm.
    BOM: MAL-BRG-6804.
    """
    return _tube(16.0, 10.0, 7.0, n=32)


# ---- Structural / CF hardware -------------------------------------------- #

def gen_cf_rod_4mm():
    """
    4 mm OD solid CF rod — nacelle tilt pivot (300 mm stock; cut 120 mm per nacelle).
    BOM: CF-ROD-4MM (×2 nacelles).
    """
    return _cyl(2.0, 300.0, n=16)


def gen_cf_rod_3mm():
    """
    3 mm OD solid CF rod — M=1.0 gear shaft stock (300 mm).
    BOM: SHAFT-CF-3MM (×1).
    """
    return _cyl(1.5, 300.0, n=16)


def gen_cf_tube_12mm_spar():
    """
    12 mm OD × 1.5 mm wall CF tube — wing spar (350 mm per wing).
    BOM: CF-TUBE-12MM (×2).
    """
    return _tube(6.0, 4.5, 350.0, n=24)


def gen_cf_bar_6x3():
    """
    6 × 3 mm CF flat bar 620 mm — hull keel + 49 MHz RCRS counterpoise.
    BOM: CF-BAR-6X3 (×1).
    """
    return _box(620.0, 6.0, 3.0)


def gen_cf_plate_2mm():
    """
    2 mm CF sheet 200 × 300 mm — ring-frame profiles at 5 hull stations.
    BOM: CF-PLATE-2MM (×1 sheet, jig-cut to 5 frame rings).
    """
    return _box(200.0, 300.0, 2.0)


def gen_ptfe_sleeve_4mm():
    """
    PTFE sleeve 4 mm OD × 3 mm ID × 52 mm — gear longitudinal shaft lubrication.
    BOM: PTFE-SLEEVE-4MM (×1, 52 mm per nacelle inside bevel conduit).
    """
    return _tube(2.0, 1.5, 52.0, n=16)


# ---- Avionics PCBs -------------------------------------------------------- #

def gen_pocketbeagle2():
    """
    PocketBeagle 2 Industrial AM6254 SBC — 56 × 35 mm PCB, ~8 mm assembled height.
    Used as both FC node (Wash cape) and CN node (Zoë cape) upper slot.
    BOM: PB2-I-FC (×4), PB2-I-CN (×4), MAL-PB2-I (×1 GCS).
    Ref [3]: BeagleBoard.org PocketBeagle 2 Industrial datasheet.
    """
    pcb = _box(56.0, 35.0, 1.6)
    components = _box(50.0, 30.0, 6.4)            # component zone top side
    components = _translate(components, 3.0, 2.5, 1.6)
    return _cat(pcb, components)


def gen_cape_a2():
    """
    Cape-A-2 PCB 55 × 35 mm — EMI-hardened Wash (Flight Control) cape.
    Same form factor as PocketBeagle 2 Industrial SBC.
    Includes ISOW1044BDFMR CAN FD isolator, ADM2795EBRWZ RS-485, 2× DP83825I ETH PHY.
    Assembled height ~10 mm (PCB + isolation ICs + JST-GH connectors).
    BOM: CAPE-A-2 (×4, all FC positions).
    Dimensions verified against Wash.kicad_pcb Edge.Cuts (X: 121–176, Y: 87.5–122.5 mm).
    """
    pcb = _box(55.0, 35.0, 1.6)
    components = _box(49.0, 29.0, 8.4)
    components = _translate(components, 3.0, 3.0, 1.6)
    return _cat(pcb, components)


def gen_cape_b2():
    """
    Cape-B-2 PCB 55 × 35 mm — EMI-hardened Zoë (Comms / Logging / Payload) cape.
    Same form factor as PocketBeagle 2 Industrial SBC and Cape-A-2.
    Adds MAVLink SiK, LoRa RFM95W, TI WL1837MOD WiFi/BT, SLB9670 TPM 2.0,
    ATF16V8BQL CPLD write-blocker, log microSD.
    Assembled height ~12 mm (RF module stack + JST-GH connectors).
    BOM: CAPE-B-2 (×4 aircraft), MAL-CAPE-B-2 (×1 GCS).
    Dimensions verified against Zoë.kicad_pcb Edge.Cuts (X: 121–176, Y: 87.5–122.5 mm).
    """
    pcb = _box(55.0, 35.0, 1.6)
    components = _box(49.0, 29.0, 10.4)
    components = _translate(components, 3.0, 3.0, 1.6)
    return _cat(pcb, components)


def gen_xcvr_49mhz2():
    """
    XCVR-49MHZ-2 sub-module PCB 55 × 35 mm — EMI-hardened 49 MHz AX.25 RCRS transceiver.
    SRF2012-100Y CMC, PRTR5V0U2X TVS, X2Y cap; 4-layer 55 × 35 mm PCB.
    Assembled height ~6 mm.
    BOM: XCVR-49MHZ-2 (×4 aircraft), MAL-XCVR-49MHZ-2 (×1 GCS).
    """
    pcb = _box(55.0, 35.0, 1.6)
    components = _box(49.0, 29.0, 4.4)
    components = _translate(components, 3.0, 3.0, 1.6)
    return _cat(pcb, components)


def gen_kaylee_pdb():
    """
    Kaylee Power Distribution Board — custom 4-layer 90 × 65 mm PCB.
    Dual 5 V/10 A BEC (TPS54620×2), 6 V/5 A BEC (TPS54540),
    5× INA226 current monitors, BQ76930 6S cell monitor.
    150 A MAXI main fuse + 4× 40 A mini ESC fuses.
    Assembled height ~10 mm (tall electrolytic caps + fuse holders).
    BOM: Kaylee (×1).
    """
    pcb = _box(90.0, 65.0, 1.6)
    components = _box(84.0, 59.0, 8.4)
    components = _translate(components, 3.0, 3.0, 1.6)
    return _cat(pcb, components)


def gen_microsd():
    """
    64 GB microSD card — Cape-B write-blocked flight log.
    Standard microSD form factor: 15 × 11 × 1.0 mm.
    BOM: MICROSD-LOG (×4 aircraft), MAL-MICROSD-LOG (×1 GCS).
    """
    return _box(15.0, 11.0, 1.0)


# ---- Power --------------------------------------------------------------- #

def gen_lipo_6s_4000mah():
    """
    6S 4000 mAh 60C LiPo — primary hover / high-endurance flight battery.
    Nominal dimensions (Tattu 6S 4000 mAh): 138 × 44 × 36 mm.
    XT60 discharge connector modelled as small protrusion.
    BOM: BATT-6S-4000 (×1).
    Ref [3]: Tattu 4000 mAh 6S 22.2V 60C datasheet.
    """
    body = _box(138.0, 44.0, 36.0)
    xt60 = _box(12.0, 10.0, 8.0)
    xt60 = _translate(xt60, 0.0, 17.0, 36.0)      # top centre
    return _cat(body, xt60)


def gen_lipo_6s_2800mah():
    """
    6S 2800 mAh LiPo — cargo-delivery battery (lower mass alternative).
    Nominal dimensions: 115 × 35 × 35 mm.
    BOM: BATT-6S-2800 (×1).
    """
    body = _box(115.0, 35.0, 35.0)
    xt60 = _box(12.0, 10.0, 8.0)
    xt60 = _translate(xt60, 0.0, 12.5, 35.0)
    return _cat(body, xt60)


def gen_lipo_4s_10000mah_gcs():
    """
    4S 10000 mAh 14.8 V LiPo — Malcolm GCS field power pack.
    Nominal dimensions: 175 × 64 × 38 mm.
    BOM: MAL-FIELD-BATTERY (×1).
    """
    body = _box(175.0, 64.0, 38.0)
    xt60 = _box(12.0, 10.0, 8.0)
    xt60 = _translate(xt60, 0.0, 27.0, 38.0)
    return _cat(body, xt60)


def gen_fuse_maxi_150a():
    """
    Littelfuse 0297150.ZXNV 150 A MAXI blade fuse — main battery bus.
    Standard MAXI blade: 29.2 × 15.2 × 16.6 mm (body only, no terminals).
    BOM: FUSE-MAIN-150A (×1 on Kaylee).
    """
    return _box(29.0, 15.0, 17.0)


def gen_fuse_mini_40a():
    """
    Littelfuse 0297040.WXNV 40 A mini blade fuse — per-ESC branch.
    Standard mini blade: 19.0 × 11.0 × 16.6 mm.
    BOM: FUSE-ESC-40A (×4 on Kaylee).
    """
    return _box(19.0, 11.0, 17.0)


def gen_shunt_1mohm():
    """
    Bourns CSS2H-2512K 1 mΩ 3 W Kelvin shunt resistor — 2512 SMD package.
    Package: 6.4 × 3.2 × 2.3 mm.
    BOM: SHUNT-1MOHM (×5 on Kaylee).
    """
    return _box(6.4, 3.2, 2.3)


# ---- Cargo system -------------------------------------------------------- #

def gen_n20_motor():
    """
    N20 300 RPM 6 V gear motor — cargo clamshell winch.
    Body: 10 × 12 mm cross-section, ~28 mm total length (gear box + motor).
    Output shaft: 3 mm dia × 10 mm extension.
    BOM: N20-WINCH (×1).
    """
    gearbox = _box(10.0, 12.0, 28.0)
    shaft = _cyl(1.5, 10.0, n=12)
    shaft = _translate(shaft, 5.0 - 1.5, 6.0 - 1.5, 28.0)
    return _cat(gearbox, shaft)


def gen_hx711():
    """
    HX711 24-bit load-cell ADC breakout module.
    PCB: 24 × 18 × 4 mm (populated).
    BOM: HX711-LC (×1 cargo tension monitoring).
    """
    return _box(24.0, 18.0, 4.0)


def gen_drv8833():
    """
    DRV8833 dual H-bridge motor-driver breakout — cargo door + release servo.
    PCB pocket per cargo_drv8833_tray.stl: 23 × 19 mm; height ~5 mm assembled.
    BOM: DRV8833-CARGO (×1).
    """
    return _box(23.0, 19.0, 5.0)


# ---- Gears (M=1.0 resin-print or SDP-SI) ---------------------------------- #

def gen_sector_m1_r22():
    """
    M=1.0 sector gear, pitch radius R=22 mm — fixed to nacelle tilt bracket.
    The stationary sector; Pinion-A rolls along the arc during 0°→90° tilt.
    Tip radius ≈ 23 mm (R + 1 module); root radius ≈ 21 mm; width 7 mm.
    Arc spans ≈ 120° to give 90° tilt range with angular margin.
    Approximated as a 23 mm radius disk sector (no individual teeth modelled).
    BOM: SECTOR-M1-R22 (×2, one per nacelle).
    """
    return _sector(23.0, 7.0, 120.0)


def gen_pinion_m1_12t():
    """
    M=1.0 Drive Pinion-A, N=12T, pitch radius R=6 mm.
    Tip radius ≈ 7 mm; width 7 mm; 2× MR63ZZ bearings (3 × 6 × 2.5 mm).
    Also models Crown Pinion (same geometry, drives nozzle ring rack).
    Approximated as a 7 mm radius cylinder.
    BOM: PINION-A-M1-12T (×2), CROWN-M1-12T (×2).
    """
    return _cyl(7.0, 7.0, n=20)


def gen_bevel_m1_14t():
    """
    M=1.0 bevel gear pair N=14T, 45° pitch cone — 90° axis redirect.
    Approximate envelope: 14.5 mm dia × 12 mm depth per gear.
    Pair represented as two abutting cylinders.
    BOM: BEVEL-M1-14T (×4, 2 pairs = 4 gears total; 2 per nacelle bevel box).
    """
    gear_a = _cyl(7.5, 12.0, n=20)
    gear_b = _cyl(7.5, 12.0, n=20)
    # B rotated 90° about X axis — approximate as box for the stacked pair
    gear_b = _translate(gear_b, 0.0, 0.0, -12.0)  # behind gear_a
    return _cat(gear_a, gear_b)


def gen_bevel_housing():
    """
    Bevel gear housing block — CF-PETG, 24 × 14 × 20 mm.
    Mounts to nacelle inboard boss posts via M2.5 screws.
    BOM: BEVEL-HOUSING (×2, one per nacelle).
    """
    return _box(24.0, 14.0, 20.0)


# ---- Miscellaneous hardware ---------------------------------------------- #

def gen_pin_3x5():
    """
    Stainless roll pin 3 mm OD × 5 mm — iris nozzle petal hinge.
    BOM: PIN-3X5 (×24: 8 per nacelle × 2 + 8 rear nozzle).
    """
    return _cyl(1.5, 5.0, n=12)


def gen_insert_m25():
    """
    M2.5 brass heat-set threaded insert M2.5 × L5, OD ≈ 3.5 mm.
    BOM: INSERT-M25-BRASS (×8, 4 per pylon sector-gear mount × 2 pylons).
    """
    return _tube(1.75, 1.25, 5.0, n=12)


def gen_insert_m3():
    """
    M3 brass heat-set threaded insert M3 × L5, OD ≈ 4.2 mm.
    BOM: INSERT-M3-WING (×8, 4 per pylon wing-block × 2 pylons).
    """
    return _tube(2.1, 1.5, 5.0, n=12)


def gen_screw_m3x8():
    """
    M3 × 8 mm stainless button-head cap screw (ISO 7380).
    Head: dia 5.7 mm × 1.65 mm; shank 3 mm dia × 6.35 mm.
    BOM: SCREW-M3-8-BTN (×4, belly panel fasteners).
    """
    head = _cyl(2.85, 1.65, n=16)
    shank = _cyl(1.5, 6.35, n=12)
    shank = _translate(shank, 0.0, 0.0, -6.35)
    return _cat(head, shank)


def gen_piano_wire_ring():
    """
    0.8 mm piano / music wire — bent into iris nozzle link rings.
    Modelled as a torus-approximated ring: tube R_torus=14 mm, wire r=0.4 mm.
    BOM: PIANO-WIRE-0.8 (×1 stock; 3 bent rings total).
    """
    R = 14.0         # link ring radius (mm)
    r = 0.4          # wire cross-section radius
    n_ring = 32      # segments around the ring
    n_tube = 8       # segments around the wire cross-section
    tris = []
    for i in range(n_ring):
        a0 = 2.0 * math.pi * i / n_ring
        a1 = 2.0 * math.pi * (i + 1) / n_ring
        for j in range(n_tube):
            b0 = 2.0 * math.pi * j / n_tube
            b1 = 2.0 * math.pi * (j + 1) / n_tube
            # Four vertices of a quad on the tube surface

            def vtx(a, b):
                cx = (R + r * math.cos(b)) * math.cos(a)
                cy = (R + r * math.cos(b)) * math.sin(a)
                cz = r * math.sin(b)
                return (cx, cy, cz)

            v00 = vtx(a0, b0)
            v10 = vtx(a1, b0)
            v01 = vtx(a0, b1)
            v11 = vtx(a1, b1)
            tris.append(_T(v00, v10, v11))
            tris.append(_T(v00, v11, v01))
    return tris


def gen_batt_strap():
    """
    16 mm silicone cam-buckle strap — battery retention (50 N rated).
    Modelled as a flat rectangular strip 16 mm wide × 2 mm thick × 200 mm long,
    representing the strap pass-through length over the battery.
    BOM: BATT-STRAP-CAM (×2, cross battery at 1/3 and 2/3 positions).
    """
    return _box(200.0, 16.0, 2.0)


def gen_dyneema():
    """
    Dyneema SK75 0.5 mm braided line — cargo winch spool.
    Modelled as a small cylindrical coil: OD=10 mm, ID=4 mm, h=8 mm.
    BOM: DYNEEMA-SK75 (×1, 2 m deployed from 100 m spool).
    """
    return _tube(5.0, 2.0, 8.0, n=24)


# ---- Lighting ------------------------------------------------------------ #

def gen_ws2812b_ring_50mm():
    """
    WS2812B addressable RGB LED ring — 50 mm dia nozzle backlight.
    OD=50 mm, ring width=5 mm (ID=40 mm), PCB thickness=2 mm.
    BOM: LED-WS2812B (×3: 1 per nacelle nozzle × 2 + 1 rear nozzle).
    """
    return _tube(25.0, 20.0, 2.0, n=32)


def gen_ws2812c_2020():
    """
    WS2812C-2020 addressable RGB LED — nacelle tip navigation lights.
    Package: 2.0 × 2.0 × 0.8 mm SMD.
    Port = RED, Stbd = GREEN per FAA 14 CFR 91.209.
    BOM: LED-WS2812C-NAC (×4: 1 tip + 1 spare per nacelle × 2 nacelles).
    """
    return _box(2.0, 2.0, 0.8)


# ---- Wiring -------------------------------------------------------------- #

def gen_ptfe_conduit_3mm():
    """
    PTFE conduit 4 mm OD × 3 mm ID × 700 mm — data bus run full hull length.
    Houses CAN FD / RS-485 / MIL-STD-1553 / Ethernet bundle.
    BOM: CONDUIT-PTFE (×1).
    """
    return _tube(2.0, 1.5, 700.0, n=16)


def gen_wire_4awg():
    """
    4 AWG silicone wire — main battery bus (200 mm per polarity).
    Approximate conductor + insulation OD ≈ 9 mm.
    Shown as two parallel cylinders (positive + negative conductors).
    BOM: WIRE-4AWG (×1 pair, 200 mm each).
    """
    pos = _cyl(4.5, 200.0, n=12)
    neg = _translate(_cyl(4.5, 200.0, n=12), 10.0, 0.0, 0.0)
    return _cat(pos, neg)


def gen_wire_10awg():
    """
    10 AWG silicone wire — ESC branch wiring (Kaylee XT30 → ESC XT30).
    OD ≈ 6 mm; shown as a 400 mm bundle (4 ESC runs × ~100 mm each).
    BOM: WIRE-10AWG (×1).
    """
    return _cyl(3.0, 400.0, n=12)


def gen_wire_28awg_stp():
    """
    28 AWG shielded twisted pair — servo signal and DSHOT leads.
    OD ≈ 3 mm per pair; shown as representative 500 mm section.
    BOM: WIRE-28AWG-STP (×1, 5 m spool; bundle shown).
    """
    return _cyl(1.5, 500.0, n=12)


def gen_wire_49mhz():
    """
    49 MHz dorsal wire antenna — 0.3 mm stainless steel, ~470 mm.
    BOM: WIRE-49MHZ (×1 end-fed dorsal spine).
    """
    return _cyl(0.15, 470.0, n=8)


# ---- GCS (Malcolm) components -------------------------------------------- #

def gen_malcolm_enclosure():
    """
    Hammond 1455N1601 IP65 aluminium project box — Malcolm field enclosure.
    Exterior: 145 × 90 × 65 mm; EPDM gasket; 40 mm fan cutout.
    BOM: MAL-ENCLOSURE (×1).
    Ref [3]: Hammond 1455N1601 datasheet.
    """
    body = _box(145.0, 90.0, 65.0)
    # Fan cutout face (front panel detail): approximate as recessed cylinder
    fan = _cyl(20.0, 5.0, n=24)
    fan = _translate(fan, 72.5 - 20.0, 0.0, 32.5 - 20.0)
    return _cat(body)             # solid body only (internal detail omitted)


def gen_pololu_bec_5v():
    """
    Pololu D24V50F5 5 V/5 A step-down BEC — Malcolm comms-node 5 V rail.
    PCB: 33 × 15 × 8 mm.
    BOM: MAL-PWR-5V-BEC (×1).
    """
    return _box(33.0, 15.0, 8.0)


def gen_pololu_bec_6v():
    """
    Pololu D24V22F6 6 V/2.2 A step-down BEC — Malcolm gimbal servo 6 V rail.
    PCB: 27 × 15 × 8 mm.
    BOM: MAL-PWR-6V-BEC (×1).
    """
    return _box(27.0, 15.0, 8.0)


def gen_ant_915_omni():
    """
    5 dBi 915 MHz RP-SMA rubber duck — SiK / LoRa bench antenna.
    Approximate: 5 mm dia × 120 mm tall whip element.
    BOM: MAL-ANT-915-OMNI (×2: one SiK + one LoRa).
    """
    base = _cyl(6.0, 15.0, n=16)         # SMA/RP-SMA base
    whip = _cyl(2.5, 105.0, n=12)
    whip = _translate(whip, 0.0, 0.0, 15.0)
    return _cat(base, whip)


def gen_ant_915_yagi():
    """
    9 dBi 915 MHz Yagi — shared SiK + LoRa directional field antenna.
    Approximate boom: 1200 × 20 × 20 mm with 5 element stubs (30 mm × 3 mm dia).
    BOM: MAL-ANT-915-YAGI (×1).
    """
    boom = _box(1200.0, 20.0, 20.0)
    elements = _cat(
        _translate(_cyl(1.5, 60.0, n=12),  100.0, 10.0, 20.0),
        _translate(_cyl(1.5, 55.0, n=12),  350.0, 10.0, 20.0),
        _translate(_cyl(1.5, 50.0, n=12),  600.0, 10.0, 20.0),
        _translate(_cyl(1.5, 47.0, n=12),  850.0, 10.0, 20.0),
        _translate(_cyl(1.5, 45.0, n=12), 1100.0, 10.0, 20.0),
    )
    return _cat(boom, elements)


def gen_ant_wifi_panel():
    """
    14 dBi 5 GHz flat-panel antenna — Malcolm WiFi directional.
    Approximate panel: 100 × 100 × 20 mm.
    BOM: MAL-ANT-WIFI-PNL (×1).
    """
    return _box(100.0, 100.0, 20.0)


def gen_ant_49mhz_whip():
    """
    49 MHz base-loaded ¼-wave whip + 4 ground radials (~940 mm physical).
    Base coil + housing: 30 mm dia × 80 mm; mast: 12 mm dia × 860 mm.
    BOM: MAL-ANT-49MHZ (×1, SO-239 mount, 4 × 1.5 m radials).
    """
    base = _cyl(15.0, 80.0, n=20)
    mast = _cyl(6.0, 860.0, n=12)
    mast = _translate(mast, 0.0, 0.0, 80.0)
    return _cat(base, mast)


def gen_ant_zigbee():
    """
    3 dBi 2.4 GHz RP-SMA rubber duck dipole — Zigbee link.
    5 mm dia × 100 mm.
    BOM: MAL-ANT-ZIGBEE (×1).
    """
    base = _cyl(5.0, 15.0, n=16)
    whip = _cyl(2.5, 85.0, n=12)
    whip = _translate(whip, 0.0, 0.0, 15.0)
    return _cat(base, whip)


def gen_ant_gnss_patch():
    """
    u-blox ANN-MB-00 active GNSS patch — GCS operator position fix.
    Ceramic patch: 25 × 25 × 5 mm + SMA pigtail stub.
    BOM: MAL-ANT-GPS (×1).
    """
    patch = _box(25.0, 25.0, 5.0)
    return patch


def gen_gps_module():
    """
    SparkFun GPS-17285 / u-blox M10Q GNSS breakout — GCS position module.
    PCB: 25 × 25 × 7 mm assembled.
    BOM: MAL-GPS-MODULE (×1).
    """
    return _box(25.0, 25.0, 7.0)


def gen_rf_splitter():
    """
    Mini-Circuits ZFSC-2-1W-S+ 2-way 915 MHz RF splitter.
    Approximate housing: 37 × 19 × 14 mm (SMA connectors add ~20 mm per port).
    BOM: MAL-RF-SPLITTER (×1, shared SiK + LoRa Yagi path).
    """
    body = _box(37.0, 19.0, 14.0)
    port1 = _cyl(3.5, 20.0, n=12)
    port1 = _translate(port1, 0.0, 9.5, 3.5)
    port2 = _cyl(3.5, 20.0, n=12)
    port2 = _translate(port2, 37.0, 9.5, 3.5)
    common = _cyl(3.5, 20.0, n=12)
    common_t = (18.5 - 3.5, 19.0, 3.5)
    common = _translate(common, *common_t)
    return _cat(body, port1, port2, common)


def gen_as5600_encoder():
    """
    AS5600 12-bit magnetic encoder breakout PCB — gimbal pan/tilt axes.
    PCB: 15 × 15 × 4 mm.
    BOM: MAL-GIMBAL-ENC (×2).
    """
    return _box(15.0, 15.0, 4.0)


def gen_n42_magnet():
    """
    N42 diametrically magnetised disc magnet 6 × 2 mm — AS5600 encoder rotor.
    BOM: MAL-GIMBAL-MAG (×2, epoxy to servo output shaft).
    """
    return _cyl(3.0, 2.0, n=16)


def gen_tca9548a():
    """
    TCA9548A 1-to-8 I²C mux breakout (Adafruit 2717) — encoder address isolation.
    PCB: 25 × 15 × 4 mm.
    BOM: MAL-TCA9548A (×1).
    """
    return _box(25.0, 15.0, 4.0)


def gen_malcolm_tripod():
    """
    Heavy-duty camera tripod / antenna mast — GCS antenna support.
    Collapsed: ~600 mm; extended: ≥1500 mm; head: 60 × 60 mm.
    Modelled as: head box + 3 leg tubes (simplified vertical form).
    BOM: MAL-TRIPOD (×1, 5 kg rated, 3/8-16 mount, ≥1.5 m extended).
    """
    head = _box(60.0, 60.0, 40.0)
    # Three telescoping leg sections collapsed — shown as single central tube
    mast = _cyl(12.0, 1460.0, n=16)
    mast = _translate(mast, 30.0 - 12.0, 30.0 - 12.0, 40.0)
    return _cat(head, mast)


def gen_wire_post_49mhz():
    """
    49 MHz RCRS wire post + base-loading coil — dorsal hull antenna mount.
    PETG post 12×12×9 mm; coil wound on post; modelled as square mast + small cylinder.
    BOM: POST-FWD-49, POST-AFT-49 (×2 total, forward + aft hull positions).
    """
    base = _box(12.0, 12.0, 2.0)          # mount flange
    mast = _box(8.0, 8.0, 7.0)            # mast
    mast = _translate(mast, 2.0, 2.0, 2.0)
    coil = _tube(4.0, 3.0, 12.0, n=16)   # base-loading coil bobbin
    coil = _translate(coil, 6.0 - 4.0, 6.0 - 4.0, 9.0)
    return _cat(base, mast, coil)


# ---------------------------------------------------------------------------
# Generation table: (generator_fn, subdir, filename, bom_ref, description)
# ---------------------------------------------------------------------------

_COMPONENTS = [
    # Propulsion
    (gen_edf_50mm_6s,       "propulsion", "EDF_50mm_6S.stl",
     "EDF-50-6S",           "50 mm 6S EDF — nacelle tandem (×4 aircraft)"),
    (gen_edf_120mm_6s,      "propulsion", "EDF_120mm_6S_deferred.stl",
     "EDF-120-6S",          "120 mm 6S rear EDF — Phase 11 deferred (×1)"),
    (gen_esc_40a,            "propulsion", "ESC_40A_6S_BLHeli32.stl",
     "ESC-40A-6S",          "40 A 6S BLHeli32 DSHOT600 ESC (×4)"),
    (gen_esc_80a,            "propulsion", "ESC_80A_6S_BLHeli32_deferred.stl",
     "ESC-80A-6S",          "80 A 6S BLHeli32 ESC — Phase 11 deferred (×1)"),
    # Servos
    (gen_ds3218mg,           "servos",     "DS3218MG_25kgcm.stl",
     "SERVO-TILT / MAL-GIMBAL-SERVO",
     "DS3218MG digital metal-gear servo (×2 nacelle tilt + ×2 GCS gimbal)"),
    (gen_sg90,               "servos",     "SG90_micro.stl",
     "SERVO-CARGO / SERVO-REAR-NOZZLE",
     "SG90 9 g micro servo (×2 cargo + ×1 rear nozzle)"),
    # Bearings
    (gen_brg_mf104zz,        "bearings",   "MF104ZZ_4x10x4mm.stl",
     "BRG-MF104ZZ",
     "MF104ZZ flanged bearing 4×10×4 mm (×4, 2 per nacelle pivot)"),
    (gen_brg_mr63zz,         "bearings",   "MR63ZZ_3x6x2p5mm.stl",
     "BRG-MR63ZZ",          "MR63ZZ miniature bearing 3×6×2.5 mm (×8 gear pinions)"),
    (gen_brg_6804,           "bearings",   "B6804_20x32x7mm_GCS.stl",
     "MAL-BRG-6804",        "6804-2RS thin bearing 20×32×7 mm (×1 GCS gimbal pan)"),
    # Structural / CF hardware
    (gen_cf_rod_4mm,         "structural", "CF_rod_4mm_300mm_stock.stl",
     "CF-ROD-4MM",
     "4 mm solid CF pivot rod, 300 mm stock (×2 nacelles, cut 120 mm)"),
    (gen_cf_rod_3mm,         "structural", "CF_rod_3mm_300mm_stock.stl",
     "SHAFT-CF-3MM",         "3 mm solid CF gear shaft rod, 300 mm stock (×1)"),
    (gen_cf_tube_12mm_spar,  "structural", "CF_tube_12mm_OD_1p5w_350mm_spar.stl",
     "CF-TUBE-12MM",         "12 mm OD 1.5 mm wall CF tube — wing spar 350 mm (×2)"),
    (gen_cf_bar_6x3,         "structural", "CF_bar_6x3mm_620mm_keel.stl",
     "CF-BAR-6X3",
     "6×3 mm CF flat bar 620 mm — hull keel + RCRS counterpoise (×1)"),
    (gen_cf_plate_2mm,       "structural", "CF_plate_2mm_200x300mm.stl",
     "CF-PLATE-2MM",         "2 mm CF sheet 200×300 mm — ring frame stock (×1 sheet)"),
    (gen_ptfe_sleeve_4mm,    "structural", "PTFE_sleeve_4mm_OD_3mm_ID_52mm.stl",
     "PTFE-SLEEVE-4MM",
     "PTFE tube 4 mm OD × 3 mm ID × 52 mm — gear shaft sleeve (×1)"),
    # Avionics
    (gen_pocketbeagle2,      "avionics",   "PocketBeagle2_Industrial_56x35mm.stl",
     "PB2-I-FC / PB2-I-CN / MAL-PB2-I",
     "PocketBeagle 2 Industrial AM6254 SBC 56×35 mm (×8 aircraft + ×1 GCS)"),
    (gen_cape_a2,            "avionics",   "Cape_A2_PCB_55x35mm.stl",
     "CAPE-A-2",             "Cape-A-2 Wash FC cape PCB 55×35 mm (×4 aircraft)"),
    (gen_cape_b2,            "avionics",   "Cape_B2_PCB_55x35mm.stl",
     "CAPE-B-2 / MAL-CAPE-B-2",
     "Cape-B-2 Zoë Comms cape PCB 55×35 mm (×4 aircraft + ×1 GCS)"),
    (gen_xcvr_49mhz2,        "avionics",   "XCVR_49MHZ2_PCB_55x35mm.stl",
     "XCVR-49MHZ-2 / MAL-XCVR-49MHZ-2",
     "XCVR-49MHZ-2 49 MHz RCRS sub-module 55×35 mm (×4 aircraft + ×1 GCS)"),
    (gen_kaylee_pdb,         "avionics",   "Kaylee_PDB_90x65mm.stl",
     "Kaylee",               "Kaylee Power Distribution Board 90×65 mm (×1)"),
    (gen_microsd,            "avionics",   "microSD_64GB.stl",
     "MICROSD-LOG / MAL-MICROSD-LOG",
     "64 GB microSD — write-blocked flight log (×4 aircraft + ×1 GCS)"),
    # Power
    (gen_lipo_6s_4000mah,    "power",      "LiPo_6S_4000mAh_138x44x36mm.stl",
     "BATT-6S-4000",         "6S 4000 mAh 60C LiPo — primary flight battery (×1)"),
    (gen_lipo_6s_2800mah,    "power",      "LiPo_6S_2800mAh_115x35x35mm.stl",
     "BATT-6S-2800",         "6S 2800 mAh LiPo — cargo-delivery battery (×1)"),
    (gen_lipo_4s_10000mah_gcs, "power",    "LiPo_4S_10000mAh_175x64x38mm_GCS.stl",
     "MAL-FIELD-BATTERY",    "4S 10000 mAh GCS field battery (×1)"),
    (gen_fuse_maxi_150a,     "power",      "Fuse_MAXI_150A.stl",
     "FUSE-MAIN-150A",       "150 A MAXI blade fuse — main battery bus (×1 on Kaylee)"),
    (gen_fuse_mini_40a,      "power",      "Fuse_mini_40A.stl",
     "FUSE-ESC-40A",         "40 A mini blade fuse — per-ESC branch (×4 on Kaylee)"),
    (gen_shunt_1mohm,        "power",      "Shunt_CSS2H_2512K_1mohm.stl",
     "SHUNT-1MOHM",          "Bourns CSS2H 1 mΩ Kelvin shunt, 2512 SMD (×5 on Kaylee)"),
    # Cargo
    (gen_n20_motor,          "cargo",      "N20_motor_300RPM_6V.stl",
     "N20-WINCH",            "N20 300 RPM gear motor — cargo winch (×1)"),
    (gen_hx711,              "cargo",      "HX711_loadcell_ADC_breakout.stl",
     "HX711-LC",             "HX711 24-bit load-cell ADC module (×1)"),
    (gen_drv8833,            "cargo",      "DRV8833_Hbridge_breakout.stl",
     "DRV8833-CARGO",        "DRV8833 dual H-bridge driver PCB 23×19 mm (×1)"),
    (gen_dyneema,            "cargo",      "Dyneema_SK75_0p5mm_coil.stl",
     "DYNEEMA-SK75",
     "Dyneema SK75 0.5 mm braided line coil — winch spool (×1)"),
    # Gears
    (gen_sector_m1_r22,      "gears",      "Sector_gear_M1_R22mm.stl",
     "SECTOR-M1-R22",        "M=1.0 sector gear R=22 mm — fixed tilt bracket (×2)"),
    (gen_pinion_m1_12t,      "gears",      "Pinion_M1_12T_R6mm.stl",
     "PINION-A-M1-12T / CROWN-M1-12T",
     "M=1.0 12T pinion / crown R=6 mm (×2 pinion-A + ×2 crown)"),
    (gen_bevel_m1_14t,       "gears",      "Bevel_M1_14T_pair.stl",
     "BEVEL-M1-14T",
     "M=1.0 bevel pair N=14T 45° — 90° axis redirect (×4 gears = 2 pairs)"),
    (gen_bevel_housing,      "gears",      "Bevel_housing_CF_PETG.stl",
     "BEVEL-HOUSING",        "Bevel gear housing block CF-PETG 24×14×20 mm (×2)"),
    # Hardware
    (gen_pin_3x5,            "hardware",   "Pin_SS_3x5mm_hinge.stl",
     "PIN-3X5",
     "Stainless roll pin 3 mm × 5 mm — iris nozzle petal hinge (×24)"),
    (gen_insert_m25,         "hardware",   "Insert_M25_brass_L5.stl",
     "INSERT-M25-BRASS",     "M2.5 brass heat-set insert OD 3.5 mm × L5 mm (×8)"),
    (gen_insert_m3,          "hardware",   "Insert_M3_brass_L5.stl",
     "INSERT-M3-WING",       "M3 brass heat-set insert OD 4.2 mm × L5 mm (×8)"),
    (gen_screw_m3x8,         "hardware",   "Screw_M3x8mm_button_ISO7380.stl",
     "SCREW-M3-8-BTN",
     "M3×8 stainless button-head cap screw ISO 7380 (×4 belly panel)"),
    (gen_piano_wire_ring,    "hardware",   "Piano_wire_0p8mm_iris_ring.stl",
     "PIANO-WIRE-0.8",
     "0.8 mm music wire link ring — iris nozzle actuation (×3 rings)"),
    (gen_batt_strap,         "hardware",   "Batt_strap_silicone_16mm_CAM.stl",
     "BATT-STRAP-CAM",
     "16 mm silicone cam-buckle strap 50 N — battery retention (×2)"),
    # Lighting
    (gen_ws2812b_ring_50mm,  "lighting",   "WS2812B_ring_50mm.stl",
     "LED-WS2812B",          "WS2812B LED ring 50 mm dia — nozzle backlight (×3)"),
    (gen_ws2812c_2020,       "lighting",   "WS2812C_2020_SMD.stl",
     "LED-WS2812C-NAC",      "WS2812C-2020 SMD RGB LED — nacelle nav lights (×4)"),
    # Wiring
    (gen_ptfe_conduit_3mm,   "wiring",     "PTFE_conduit_4mm_OD_3mm_ID_700mm.stl",
     "CONDUIT-PTFE",
     "PTFE conduit 4 mm OD × 3 mm ID × 700 mm — data bus run (×1)"),
    (gen_wire_4awg,          "wiring",     "Wire_4AWG_silicone_200mm_pair.stl",
     "WIRE-4AWG",            "4 AWG silicone wire pair 200 mm — main battery bus (×1)"),
    (gen_wire_10awg,         "wiring",     "Wire_10AWG_silicone_400mm.stl",
     "WIRE-10AWG",           "10 AWG silicone wire 400 mm — ESC branch (×1)"),
    (gen_wire_28awg_stp,     "wiring",     "Wire_28AWG_STP_bundle_500mm.stl",
     "WIRE-28AWG-STP",       "28 AWG shielded twisted pair 500 mm — signal leads (×1)"),
    (gen_wire_49mhz,         "wiring",     "Wire_49MHz_antenna_0p3mm_470mm.stl",
     "WIRE-49MHZ",           "0.3 mm stainless dorsal antenna wire 470 mm (×1)"),
    (gen_wire_post_49mhz,    "wiring",     "Post_49MHz_base_load_coil.stl",
     "POST-FWD-49 / POST-AFT-49",
     "49 MHz wire post + base-loading coil (×2: forward + aft hull)"),
    # GCS
    (gen_malcolm_enclosure,  "gcs",        "Malcolm_enclosure_IP65_145x90x65mm.stl",
     "MAL-ENCLOSURE",        "Hammond 1455N1601 IP65 Al enclosure 145×90×65 mm (×1)"),
    (gen_pololu_bec_5v,      "gcs",        "Pololu_D24V50F5_5V5A_BEC.stl",
     "MAL-PWR-5V-BEC",       "Pololu D24V50F5 5 V/5 A step-down BEC (×1 GCS)"),
    (gen_pololu_bec_6v,      "gcs",        "Pololu_D24V22F6_6V2A_BEC.stl",
     "MAL-PWR-6V-BEC",       "Pololu D24V22F6 6 V/2.2 A step-down BEC (×1 GCS)"),
    (gen_ant_915_omni,       "gcs",        "Antenna_915MHz_omni_5dBi.stl",
     "MAL-ANT-915-OMNI",     "5 dBi 915 MHz rubber duck — SiK/LoRa bench (×2 GCS)"),
    (gen_ant_915_yagi,       "gcs",        "Antenna_915MHz_Yagi_9dBi.stl",
     "MAL-ANT-915-YAGI",
     "9 dBi 915 MHz Yagi — shared SiK+LoRa field directional (×1)"),
    (gen_ant_wifi_panel,     "gcs",        "Antenna_5GHz_panel_14dBi.stl",
     "MAL-ANT-WIFI-PNL",     "14 dBi 5 GHz flat panel — Malcolm WiFi directional (×1)"),
    (gen_ant_49mhz_whip,     "gcs",        "Antenna_49MHz_whip_940mm.stl",
     "MAL-ANT-49MHZ",        "49 MHz base-loaded ¼-wave whip + radials ~940 mm (×1)"),
    (gen_ant_zigbee,         "gcs",        "Antenna_2p4GHz_zigbee_rubber_duck.stl",
     "MAL-ANT-ZIGBEE",       "3 dBi 2.4 GHz rubber duck — Zigbee link (×1 GCS)"),
    (gen_ant_gnss_patch,     "gcs",        "Antenna_GNSS_patch_ANN_MB00.stl",
     "MAL-ANT-GPS",          "u-blox ANN-MB-00 active GNSS patch 25×25×5 mm (×1)"),
    (gen_gps_module,         "gcs",        "GPS_module_M10Q_SparkFun.stl",
     "MAL-GPS-MODULE",       "SparkFun M10Q GNSS breakout PCB 25×25×7 mm (×1)"),
    (gen_rf_splitter,        "gcs",        "RF_splitter_915MHz_2way_ZFSC.stl",
     "MAL-RF-SPLITTER",      "Mini-Circuits ZFSC-2-1W-S+ 2-way 915 MHz splitter (×1)"),
    (gen_as5600_encoder,     "gcs",        "AS5600_encoder_breakout_15x15mm.stl",
     "MAL-GIMBAL-ENC",       "AS5600 12-bit magnetic encoder breakout (×2 pan + tilt)"),
    (gen_n42_magnet,         "gcs",        "N42_disc_magnet_6x2mm.stl",
     "MAL-GIMBAL-MAG",       "N42 diametric disc magnet 6×2 mm — AS5600 rotor (×2)"),
    (gen_tca9548a,           "gcs",        "TCA9548A_I2C_mux_breakout.stl",
     "MAL-TCA9548A",         "TCA9548A 1-to-8 I²C mux breakout 25×15×4 mm (×1 GCS)"),
    (gen_brg_6804,           "gcs",        "B6804_20x32x7mm_gimbal_pan.stl",
     "MAL-BRG-6804",         "6804-2RS thin bearing 20×32×7 mm — GCS gimbal pan (×1)"),
    (gen_malcolm_tripod,     "gcs",        "Malcolm_tripod_antenna_mast.stl",
     "MAL-TRIPOD",           "Heavy-duty tripod / antenna mast ≥1.5 m (×1 GCS)"),
]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    """Generate all placeholder STL files and print a summary report."""
    total_tris = 0
    generated = 0
    errors = []

    print("Serenity UAV — Placeholder STL generation (Rev R BOM)")
    print("=" * 60)

    for (fn, subdir, fname, bom_ref, description) in _COMPONENTS:
        path = _out(subdir, fname)
        try:
            tris = fn()
            count = _write(path, tris)
            total_tris += count
            generated += 1
            rel = os.path.relpath(path, _SCRIPT_DIR)
            print(f"  OK  {rel:52s}  {count:5d} tri  [{bom_ref}]")
        except Exception as exc:
            errors.append((fname, exc))
            print(f"  ERR {fname}: {exc}")

    print("=" * 60)
    print(f"Generated {generated}/{len(_COMPONENTS)} files, "
          f"{total_tris} total triangles.")
    if errors:
        print(f"ERRORS ({len(errors)}):")
        for name, exc in errors:
            print(f"  {name}: {exc}")
        return 1
    print("All placeholder STLs written successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
