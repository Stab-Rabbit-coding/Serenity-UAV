#!/usr/bin/env python3
"""
Generate foam-fill build guide SVGs and update overview diagrams.
Serenity-UAV project - Steve Griffing PE(CSE) CISSP-ISSEP CPP - CC BY 4.0 2026
"""
import os

OUT = "serenity/diagrams"
F = "OpenDyslexic',sans-serif"   # font value fragment (use inside attr strings)
FB = "OpenDyslexic',sans-serif"  # bold handled separately

HDR = """<?xml version="1.0" encoding="UTF-8"?>
<!-- (c) 2026 Steve Griffing PE(CSE) CISSP-ISSEP CPP  CC BY 4.0 -->
<!-- Hull: Peter Farell CC BY 4.0 | Nozzle: BamJr CC BY 4.0 -->
<!-- Visual: Firefly/Serenity (c) Joss Whedon/Mutant Enemy/Universal - Fan engineering work -->"""

STYLE = """  <style>
    @import url('https://fonts.cdnfonts.com/css/opendyslexic');
    text, tspan { font-family: 'OpenDyslexic',sans-serif !important; }
    @media print {
      svg { background:#ffffff !important; }
      text, tspan { fill:#111111 !important; }
    }
  </style>"""

def txt(x, y, s, size=10, fill="#222222", anchor="start", bold=False, color=None):
    f_fill = color or fill
    weight = ' font-weight="bold"' if bold else ""
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="\'OpenDyslexic\',sans-serif"'
            f' font-size="{size}"{weight} fill="{f_fill}">{s}</text>')

def rect(x, y, w, h, fill="#ffffff", stroke=None, sw=1, rx=0, opacity=1, dash=""):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    d = f' stroke-dasharray="{dash}"' if dash else ""
    op = f' opacity="{opacity}"' if opacity != 1 else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{s}{d}{op}/>'

def line(x1, y1, x2, y2, stroke="#888", sw=1, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}"{d}/>'

def circle(cx, cy, r, fill="#006db7"):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"/>'

def step_item(cx, cy, n, label, color="#006db7"):
    return (circle(cx, cy, 11, color) +
            txt(cx, cy+4, str(n), size=10, fill="#ffffff", anchor="middle", bold=True) +
            txt(cx+18, cy+4, label[:74], size=10))

def warn_box(x, y, w, h, msg):
    return (rect(x, y, w, h, fill="#fffac0", stroke="#ff7518", sw=2, rx=6) +
            txt(x+16, y+14, "!", size=14, fill="#ff7518", bold=True) +
            txt(x+34, y+15, msg[:90], size=10))

def info_box(x, y, w, h, msg):
    return (rect(x, y, w, h, fill="#b2ebf2", stroke="#00838f", sw=1, rx=6) +
            txt(x+10, y+15, "i", size=10, fill="#00838f", bold=True) +
            txt(x+24, y+15, msg[:95], size=10))

def svg_page(body, step_num, total, phase_label):
    badge = (rect(1040, 8, 144, 48, fill="#ff7518", rx=6) +
             txt(1112, 29, "STEP", size=11, fill="#ffffff", anchor="middle", bold=True) +
             txt(1112, 50, f"{step_num} / {total}", size=22, fill="#ffffff", anchor="middle", bold=True))
    phase = (rect(0, 64, 1200, 40, fill="#dde4ea") +
             txt(24, 90, phase_label, size=16, fill="#006db7", bold=True))
    footer = (rect(0, 872, 1200, 28, fill="#006db7") +
              txt(600, 890,
                  "Hull: Peter Farell CC BY 4.0 - Nozzle: BamJr CC BY 4.0 - "
                  "Visual: Firefly/Serenity (c) Joss Whedon/Mutant Enemy/Universal - Fan engineering work",
                  size=9, fill="#c8dff0", anchor="middle"))
    return (HDR + "\n"
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 900" width="1200" height="900">\n'
            "<defs>\n" + STYLE + "\n</defs>\n" +
            rect(0, 0, 1200, 900, fill="#f5f0e8") +
            rect(0, 0, 1200, 64, fill="#006db7") +
            txt(24, 24, "SERENITY-CLASS TILTROTOR UAV -- BUILD GUIDE",
                size=14, fill="#ffffff", bold=True) +
            txt(24, 46, 'Steve Griffing, PE(CSE), CISSP-ISSEP, CPP - CC BY 4.0 - 2026 - 18" / 457.2mm hull',
                size=11, fill="#c8dff0") +
            badge + phase +
            rect(16, 112, 720, 752, fill="#fffdf6", stroke="#dde4ea", rx=8) +
            rect(752, 112, 432, 752, fill="#fffdf6", stroke="#dde4ea", rx=8) +
            body + footer +
            "\n</svg>")


# ── STEP 02: PRINT HULL + ACCESS FRAMES ────────────────────────────────────────
def make_step02():
    COLORS = ["#c0392b","#2980b9","#27ae60","#8e44ad","#e67e22","#16a085"]
    LABELS = ["A","B","C","D","E","F"]
    NAMES  = ["NOSE","DORSAL FWD","BELLY","DORSAL AFT","AFT SVC","ENGINE"]
    STARTS = [0, 91, 160, 251, 320, 388]
    ENDS   = [91, 165, 251, 320, 388, 457]
    HGHTS  = [24, 56, 68, 62, 54, 38]
    SC     = 620/457.2
    DX, HY = 50, 290

    segs = ""
    for i in range(6):
        x1 = DX + STARTS[i]*SC
        x2 = DX + ENDS[i]*SC
        h  = HGHTS[i]
        mx = (x1+x2)/2
        segs += rect(x1, HY-h//2, x2-x1, h, fill=COLORS[i]+"33", stroke=COLORS[i], sw=2, rx=3)
        segs += txt(mx, HY+5, LABELS[i], size=15, fill=COLORS[i], anchor="middle", bold=True)
        # panel indicator above
        segs += rect(x1+2, HY-h//2-20, x2-x1-4, 16, fill=COLORS[i], rx=3, opacity=0.8)
        segs += txt(mx, HY-h//2-8, NAMES[i], size=8, fill="#ffffff", anchor="middle")

    # colour swatch legend
    legend = ""
    for i in range(6):
        lx = 50 + i*105
        legend += rect(lx, HY+50, 98, 18, fill=COLORS[i], rx=3)
        legend += txt(lx+49, HY+63, f"{LABELS[i]}  {NAMES[i]}", size=9, fill="#ffffff", anchor="middle")

    dim = (line(DX, HY+80, DX+int(457.2*SC), HY+80, stroke="#607080") +
           txt(DX+310, HY+95, '457.2 mm (18.00") total hull length', size=10, fill="#607080", anchor="middle"))

    notes = (txt(50, HY+120, "Total estimated print time: ~38 hours (run hull sections overnight)", size=10) +
             txt(50, HY+138, "Access frames + lids: ~4 hours (small parts, 6 each)", size=10) +
             txt(50, HY+156, "Total PETG consumed: ~285g hull + ~32g frames/lids = ~317g", size=10))

    w1 = warn_box(50, HY+174, 636, 32,
                  "Do NOT bond cockpit cap, engine bell, OR access-panel frames permanently until void formers placed (Step 22)")
    i1 = info_box(50, HY+214, 636, 26,
                  "Bond access-panel frames into hull with 5-min epoxy BEFORE foam pour. Frames stay; lids are removable.")

    # Right panel parts
    parts_data = [
        ("6x","#2e7d32","Hull STL sections (PETG 1.2mm wall)"),
        ("6x","#ff7518","Access-panel FRAME STLs (PETG 100%)"),
        ("6x","#ff7518","Access-panel LID STLs (PETG 100%)"),
        ("3x","#607080","Void-former jig STLs (PLA 15%)"),
        ("1x","#607080","PETG filament >= 300g"),
        ("1x","#607080","5-min epoxy 25mL syringe"),
    ]
    phdr = (rect(760, 120, 416, 28, fill="#006db7", rx=5) +
            txt(968, 139, "PARTS NEEDED", size=11, fill="#ffffff", anchor="middle", bold=True))
    prows = ""
    for j,(qty,col,desc) in enumerate(parts_data):
        py = 155 + j*22
        prows += rect(760, py, 26, 16, fill=col, rx=4)
        prows += txt(773, py+12, qty, size=9, fill="#ffffff", anchor="middle", bold=True)
        prows += txt(792, py+12, desc, size=10)

    steps_data = [
        "Slice hull sections: 8% gyroid, 2 perimeters, 0.20mm layer",
        "Enable seam alignment to dorsal ridge on all sections",
        "Print cockpit cap + section nose-down (best bridging geometry)",
        "Print mid-hull as LEFT + RIGHT halves (centreline split for bed)",
        "Print aft neck vertically - preserves strength at 22.9mm thin section",
        "Print engine bell: 3 walls, 20% infill (airtight EDF duct needed)",
        "Print 6 access-panel FRAMES: 4 perimeters, 100% infill, flush face",
        "Print 6 access-panel LIDS: 4 perimeters, 100% infill, -0.2mm XY comp",
        "Print 3 void-former plug jigs (nose/mid/aft) - PLA 15% infill OK",
    ]
    ihdr = (rect(760, 285, 416, 28, fill="#607080", rx=5) +
            txt(968, 304, "PRINT INSTRUCTIONS", size=11, fill="#ffffff", anchor="middle", bold=True))
    irows = ""
    for j, s in enumerate(steps_data):
        cy = 328 + j*28
        irows += step_item(772, cy, j+1, s)

    body = (txt(356, 148, "18\" HULL -- ACCESS PANEL ZONES (side view)",
                size=13, fill="#006db7", anchor="middle", bold=True) +
            segs + legend + dim + notes + w1 + i1 +
            phdr + prows + ihdr + irows)
    return svg_page(body, "2", 24, "PHASE 1 -- PRINT HULL SECTIONS + ACCESS PANEL FRAMES")


# ── STEP 22: VOID FORMERS ──────────────────────────────────────────────────────
def make_step22():
    COLORS = ["#c0392b","#2980b9","#27ae60","#8e44ad","#e67e22","#16a085"]
    LABELS = ["A","B","C","D","E","F"]
    STARTS = [0,91,160,251,320,388]
    ENDS   = [91,165,251,320,388,457]
    HGHTS  = [24,56,68,62,54,38]
    VOIDS  = [
        ("0-91","Nose bayonet","50x30x86mm EPS","Waxed EPS + bayonet PETG frame"),
        ("91-165","Dorsal fwd M2.5","55x52x74mm EPS","Waxed EPS + M2.5x4 PETG frame"),
        ("160-251","Cargo belly hinge","70x48x91mm EPS","Waxed EPS + hinge PETG frame"),
        ("251-320","Dorsal aft magnet","55x47x69mm EPS","Waxed EPS + magnet x4 frame"),
        ("320-388","Aft service M2.5","50x42x68mm EPS","Waxed EPS + M2.5x4 PETG frame"),
        ("388-457","Engine bell bay","NO FOAM FILL","Bayonet PETG frame only -- open bay"),
    ]
    CONDUITS = [
        ("CAN FD","Port keel rail full length","#e74c3c"),
        ("RS-485","Starboard keel rail full length","#3498db"),
        ("MIL-STD-1553","Dorsal centre spine full length","#f39c12"),
        ("ETH-A","Port side Node1 to COMPHAT-SWITCH","#9b59b6"),
        ("ETH-B","Starboard side Node2 to COMPHAT-SWITCH","#1abc9c"),
        ("PWR","Belly centre battery to BEC to all nodes","#e67e22"),
    ]

    SC, DX, HY = 560/457.2, 50, 265
    # Hull zones
    segs = ""
    for i in range(6):
        x1 = DX + STARTS[i]*SC
        x2 = DX + ENDS[i]*SC
        h  = HGHTS[i]
        mx = (x1+x2)/2
        segs += rect(x1, HY-h//2, x2-x1, h, fill=COLORS[i]+"44", stroke=COLORS[i], sw=2, rx=3)
        segs += txt(mx, HY+5, LABELS[i], size=15, fill=COLORS[i], anchor="middle", bold=True)
    # Conduit lines
    conduit_ys = [HY-6, HY+2, HY+9, HY-13, HY+16, HY+22]
    for i,(name,route,col) in enumerate(CONDUITS):
        cy = conduit_ys[i]
        segs += line(DX, cy, DX+560, cy, stroke=col, sw=2, dash="8 3")

    dim = (line(DX, HY+45, DX+560, HY+45, stroke="#607080") +
           txt(DX+280, HY+58, '457.2mm (18.00")', size=10, fill="#607080", anchor="middle"))

    # Conduit legend
    cleg = txt(50, 328, "CONDUIT ROUTING (5mm OD PTFE tube -- install BEFORE foam):", size=11, bold=True)
    for i,(name,route,col) in enumerate(CONDUITS):
        iy = 346 + i*18
        cleg += line(50, iy, 82, iy, stroke=col, sw=2, dash="6 2")
        cleg += txt(88, iy+4, f"{name} -- {route}", size=10)

    # Void former table
    tab = (rect(36, 440, 680, 22, fill="#006db7", rx=3) +
           txt(50, 455, "PNL  STATION(mm)  VOID SIZE        MATERIAL                         FASTENER",
               size=9, fill="#ffffff", bold=True))
    for i,(sta,atype,mat,fix) in enumerate(VOIDS):
        ry = 462 + i*28
        bg = "#f8f8f8" if i%2==0 else "#ffffff"
        tab += rect(36, ry, 680, 28, fill=bg)
        tab += rect(36, ry, 28, 28, fill=COLORS[i])
        tab += txt(50, ry+18, LABELS[i], size=12, fill="#ffffff", anchor="middle", bold=True)
        for val,x in [(sta,70),(mat[:28],160),(fix[:34],370)]:
            tab += txt(x, ry+18, val, size=9)

    w1 = warn_box(36, 638, 680, 28,
                  "Once foam is poured (Step 23) void formers are hard to remove -- verify ALL conduit routing first")
    i1 = info_box(36, 674, 680, 24,
                  "Zone F (engine bell 388-457mm) gets NO foam fill -- leave open for 40mm EDF access")

    # Right panel steps
    steps = [
        "Bond access-panel frames into hull with 5-min epoxy -- 30min cure",
        "Cut EPS void formers A-E using craft knife + printed jig templates",
        "Formers must clear panel frames by >=5mm on all sides",
        "Apply 2 coats paste wax to ALL void-former surfaces -- buff, 15min dry",
        "Do NOT wax the PTFE conduit tubes (bonding to foam is fine)",
        "Feed 6x PTFE conduit tubes nose-to-tail through hull before formers",
        "Label each conduit BOTH ends: CAN/RS485/1553/ETH-A/ETH-B/PWR",
        "Insert void formers A-E through open dorsal-forward seam",
        "Secure each former with 2x toothpick pins into hull ribs",
        "Apply 3M 4016 gasket strip around all panel frame lips",
        "Test-fit all access panel lids -- must close flush (0.2mm gap OK)",
        "Zone F stays empty -- no void former needed in engine bell",
    ]
    ihdr = (rect(760, 120, 416, 22, fill="#006db7", rx=5) +
            txt(968, 135, "INSTRUCTIONS", size=11, fill="#ffffff", anchor="middle", bold=True))
    irows = ""
    for j,s in enumerate(steps):
        cy = 154 + j*27
        irows += step_item(772, cy, j+1, s)

    parts_data = [
        ("1x","#607080","EPS foam board 25mm x 300mm x 150mm (Foamular 150)"),
        ("1x","#607080","Johnson Paste Wax 16oz tin"),
        ("6x","#607080","PTFE tube 5mm OD x 500mm per conduit"),
        ("16x","#2980b9","M2.5x6 SS button-head (panels B and E)"),
        ("8x","#8e44ad","N42 disc magnets 6x2mm (panel D)"),
        ("1x","#27ae60","3M 4016 closed-cell gasket tape roll"),
        ("1x","#607080","5-minute epoxy 25mL syringe"),
        ("1x","#607080","Toothpicks (temporary void former pins)"),
    ]
    phdr = (rect(760, 468, 416, 22, fill="#607080", rx=5) +
            txt(968, 483, "PARTS NEEDED", size=11, fill="#ffffff", anchor="middle", bold=True))
    prows = ""
    for j,(qty,col,desc) in enumerate(parts_data):
        py = 496 + j*22
        prows += rect(760, py, 26, 16, fill=col, rx=4)
        prows += txt(773, py+12, qty, size=9, fill="#ffffff", anchor="middle", bold=True)
        prows += txt(792, py+12, desc, size=9)

    body = (txt(356, 148, "HULL VOID ZONES A-F + CONDUIT ROUTING (side view)",
                size=13, fill="#006db7", anchor="middle", bold=True) +
            segs + dim + cleg + tab + w1 + i1 +
            ihdr + irows + phdr + prows)
    return svg_page(body, "22", 24, "PHASE 3 -- FOAM FILL PREPARATION: VOID FORMERS")


# ── STEP 23: FOAM FILL ─────────────────────────────────────────────────────────
def make_step23():
    COLORS = ["#c0392b","#2980b9","#27ae60","#8e44ad","#e67e22","#16a085"]

    # Batch diagram boxes
    batches = [
        (60, "BATCH 1 110mL", "Zones A+B", "#c0392b"),
        (230,"BATCH 2 110mL", "Zones C+D", "#27ae60"),
        (400,"BATCH 3 110mL", "Zone E only","#e67e22"),
    ]
    batch_svg = ""
    for bx, blbl, bzone, col in batches:
        batch_svg += rect(bx, 155, 90, 110, fill=col+"33", stroke=col, sw=2, rx=8)
        batch_svg += rect(bx+20, 175, 50, 70, fill=col+"88", rx=4)
        batch_svg += txt(bx+45, 284, blbl.split()[0]+" "+blbl.split()[1], size=10, fill=col, anchor="middle", bold=True)
        batch_svg += txt(bx+45, 298, blbl.split()[2], size=10, fill=col, anchor="middle", bold=True)
        batch_svg += txt(bx+45, 316, bzone, size=9, fill="#555", anchor="middle")
        if bx < 400:
            batch_svg += line(bx+90, 210, bx+170, 210, stroke="#888", sw=1, dash="4 2")
            batch_svg += txt(bx+130, 206, "3 min", size=9, fill="#888", anchor="middle")

    # Expansion visual
    exp = (rect(80, 368, 38, 38, fill="#fff3cd", stroke="#e67e22", sw=2, rx=4) +
           txt(99, 392, "mix", size=9, fill="#e67e22", anchor="middle") +
           txt(132, 392, "->", size=18, fill="#e67e22") +
           rect(155, 348, 90, 72, fill="#fff3cd", stroke="#e67e22", sw=2, rx=6) +
           txt(200, 390, "4x expanded", size=9, fill="#e67e22", anchor="middle") +
           txt(99, 420, "~27mL", size=9, fill="#555", anchor="middle") +
           txt(200, 420, "~110mL foam", size=9, fill="#555", anchor="middle") +
           txt(265, 380, "2-min pot life  |  max 60mL/batch  |  cure 24h", size=11) +
           txt(265, 398, "3 batches x 110mL = 330mL total  |  foam mass: 41.9g", size=11))

    w1 = warn_box(36, 450, 680, 28,
                  "Work outdoors or with ventilation -- PU foam releases CO2 and heat during cure")
    w2 = warn_box(36, 486, 680, 28,
                  "Pot life: 2 MINUTES from mixing -- have everything positioned BEFORE mixing each batch")
    w3 = warn_box(36, 522, 680, 28,
                  "DO NOT mix more than 60mL per batch -- excess heat from large pours WILL warp PETG")
    i1 = info_box(36, 558, 680, 26,
                  "Total foam: ~330mL = 3 batches. Foam mass in airframe: 41.9g. Hull total: 213g.")

    # Cure schedule
    cure = (txt(50, 604, "CURE SCHEDULE:", size=12, bold=True) +
            rect(50, 612, 205, 22, fill="#e8f5e9", stroke="#27ae60", sw=1, rx=4) +
            txt(152, 627, "4h -- initial set (do not move)", size=10, fill="#27ae60", anchor="middle") +
            rect(265, 612, 205, 22, fill="#e3f2fd", stroke="#2980b9", sw=1, rx=4) +
            txt(367, 627, "12h -- safe to handle carefully", size=10, fill="#2980b9", anchor="middle") +
            rect(480, 612, 205, 22, fill="#fff3e0", stroke="#e67e22", sw=1, rx=4) +
            txt(582, 627, "24h -- full cure, void removal OK", size=10, fill="#e67e22", anchor="middle"))

    steps_data = [
        "Close and tape ALL hull joints EXCEPT dorsal-forward seam (leave 20mm gap)",
        "Lay hull belly-down on level surface -- verify with spirit level",
        "Pre-measure 6 cups: 55mL Part A + 55mL Part B each (110mL per cup)",
        "Put on nitrile gloves + safety glasses -- PU foam irritant",
        "BATCH 1: mix 55+55mL, stir 30sec, pour into nose (Zones A+B)",
        "Wait 3 minutes for Batch 1 to gel -- do not disturb hull",
        "BATCH 2: mix 55+55mL, pour into mid-hull (Zones C+D)",
        "Wait 3 minutes for Batch 2 to gel",
        "BATCH 3: mix 55+55mL, pour into aft section (Zone E ONLY)",
        "Seal dorsal-forward seam with 50mm packing tape -- smooth firmly",
        "Do NOT move hull for 4 hours minimum (initial cure phase)",
        "After 24h cure: remove toothpick pins from void formers",
        "Grip each void former, twist +-10deg, pull firmly (wax releases it)",
        "Trim foam flash flush with serrated knife (1-2mm below hull surface)",
        "Pull drawstring through each conduit -- verify all 6 are clear",
    ]
    ihdr = (rect(760, 120, 416, 22, fill="#006db7", rx=5) +
            txt(968, 135, "FOAM FILL INSTRUCTIONS", size=11, fill="#ffffff", anchor="middle", bold=True))
    irows = ""
    for j, s in enumerate(steps_data):
        cy = 154 + j*26
        col = "#c0392b" if j in [3,8] else "#006db7"
        irows += step_item(772, cy, j+1, s, color=col)

    w4 = warn_box(760, 560, 416, 26, "Step 9: Zone F (bell 388-457mm) stays EMPTY")
    i2 = info_box(760, 594, 416, 24, "Step 13: wax allows release with twist+pull")
    i3 = info_box(760, 626, 416, 24, "Step 15: pull wire through each conduit to verify")

    body = (txt(356, 148, "SEQUENTIAL POUR STRATEGY -- FORE TO AFT",
                size=13, fill="#006db7", anchor="middle", bold=True) +
            batch_svg + exp + w1 + w2 + w3 + i1 + cure +
            ihdr + irows + w4 + i2 + i3)
    return svg_page(body, "23", 24, "PHASE 3 -- FOAM FILL + CURE")


# ── STEP 24: ACCESS PANELS + MAINTENANCE MAP ───────────────────────────────────
def make_step24():
    COLORS = ["#c0392b","#2980b9","#27ae60","#8e44ad","#e67e22","#16a085"]
    LABELS = ["A","B","C","D","E","F"]
    PANELS = [
        ("NOSE CAP","Bayonet CCW 30deg","55mm OD","Node 1 SENSORHAT+CM4","GPS patch antenna","Pitot tube fitting"),
        ("DORSAL FWD","4x M2.5 Phillips","65x60mm","Node 2 SENSORHAT+CM4","Power distribution PCB","Pitot line"),
        ("CARGO BELLY","Hinge + servo latch","80x55mm","Winch motor+spool","Payload release servo","Downward FPV camera"),
        ("DORSAL AFT","4x N42 magnets","65x55mm","Node 3 SENSORHAT+CM4","Battery slide rail+XT60","Main 5V BEC"),
        ("AFT SERVICE","4x M2.5 Phillips","60x50mm","Node 4 SENSORHAT+CM4","3x ESCs (50A,50A,25A)","Bus terminus connectors"),
        ("ENGINE BELL","Bayonet CW 30deg","50mm OD","40mm EDF assembly","Variable nozzle servo","Fwd FPV camera conn."),
    ]

    # Top-view hull outline (simplified polygon)
    hull = '<polygon points="50,265 90,242 200,228 310,225 380,230 445,240 545,265 445,290 380,300 310,305 200,302 90,288" fill="#e8e8e8" stroke="#607080" stroke-width="2"/>'

    # Panel overlay rectangles on top view
    px1s = [50, 92, 202, 312, 382, 447]
    px2s = [88, 200, 310, 380, 445, 543]
    py1s = [244, 230, 228, 228, 232, 242]
    py2s = [286, 300, 302, 302, 298, 288]
    panel_svg = hull
    for i in range(6):
        panel_svg += rect(px1s[i], py1s[i], px2s[i]-px1s[i], py2s[i]-py1s[i],
                          fill=COLORS[i]+"55", stroke=COLORS[i], sw=2, rx=4, dash="7 3")
        mx = (px1s[i]+px2s[i])//2
        my = (py1s[i]+py2s[i])//2
        panel_svg += txt(mx, my+5, LABELS[i], size=16, fill=COLORS[i], anchor="middle", bold=True)

    # Nacelle stubs
    panel_svg += '<ellipse cx="295" cy="192" rx="32" ry="20" fill="#cccccc" stroke="#888" stroke-width="1.5"/>'
    panel_svg += txt(295, 197, "NACELLE", size=9, fill="#555", anchor="middle")
    panel_svg += '<ellipse cx="295" cy="338" rx="32" ry="20" fill="#cccccc" stroke="#888" stroke-width="1.5"/>'
    panel_svg += txt(295, 343, "NACELLE", size=9, fill="#555", anchor="middle")

    # Mandatory warning
    mand = (txt(50, 392, "MANDATORY: REMOVE BATTERY AND POWER OFF BEFORE OPENING ANY PANEL",
                size=12, fill="#c0392b", bold=True) +
            txt(50, 410, "Recommended sequence: F -> E -> D -> B -> A -> C (aft to forward, avoids cable strain)",
                size=10, fill="#607080"))

    # Maintenance procedure rows
    maint = [
        ("A","Nose bayonet","Grip nose, rotate CCW 30deg, pull fwd. Install: align 3 tabs, push, rotate CW to click."),
        ("B","Dorsal fwd screws","4x M2.5 Phillips. Store screws in lid thread holes when panel is open."),
        ("C","Cargo belly hinge","Use GCS / stick command to actuate release servo before maintenance access."),
        ("D","Dorsal aft magnets","Lift from forward edge first -- magnets release sequentially. Rear edge first to re-install."),
        ("E","Aft service screws","4x M2.5 Phillips. Need 50mm clearance above hull for panel lid removal."),
        ("F","Engine bell bayonet","Grip bell, rotate CW 30deg, pull aft. ESC pogo-pin connector auto-disconnects."),
    ]
    msvg = ""
    for i,(lbl,name,desc) in enumerate(maint):
        ry = 428 + i*37
        msvg += rect(36, ry, 680, 33, fill=COLORS[i]+"11", stroke=COLORS[i]+"55", rx=4)
        msvg += rect(36, ry, 28, 33, fill=COLORS[i], rx=4)
        msvg += txt(50, ry+20, lbl, size=14, fill="#ffffff", anchor="middle", bold=True)
        msvg += txt(70, ry+13, f"{name}:", size=10, fill=COLORS[i], bold=True)
        msvg += txt(70, ry+27, desc[:85], size=9)

    i1 = info_box(36, 654, 680, 38,
                  "Node replacement: each SENSORHAT+CM4 stack slides on 2x PTFE rails -- "
                  "disconnect JST-GH harness first. Battery: Panel D, slide aft on M3 rail, disconnect XT60.")
    w1 = warn_box(36, 700, 680, 26,
                  "NEVER force a panel -- paste wax residue causes initial adhesion. Use plastic pry tool only.")

    # Right panel: per-panel component list
    psvg = ""
    for i,(title,closure,size,a,b,c) in enumerate(PANELS):
        ry = 120 + i*118
        psvg += rect(760, ry, 416, 112, fill=COLORS[i]+"11", stroke=COLORS[i], sw=2, rx=5)
        psvg += rect(760, ry, 416, 22, fill=COLORS[i], rx=5)
        psvg += rect(760, ry+15, 416, 7, fill=COLORS[i])  # square off top-left/right of header bottom
        psvg += txt(968, ry+15, f"PANEL {LABELS[i]} -- {title}  [{size}]  {closure}",
                    size=10, fill="#ffffff", anchor="middle", bold=True)
        for k,item in enumerate([a,b,c]):
            psvg += txt(772, ry+38+k*22, f"- {item}", size=10)

    body = (txt(356, 148, "MAINTENANCE ACCESS MAP -- TOP VIEW",
                size=13, fill="#006db7", anchor="middle", bold=True) +
            panel_svg + mand + msvg + i1 + w1 + psvg)
    return svg_page(body, "24", 24, "PHASE 3 -- ACCESS PANELS + MAINTENANCE MAP")


# ── OVERVIEW SIDE: add access hatch callouts ───────────────────────────────────
def make_overview_side():
    existing = open("serenity/diagrams/overview_side.svg").read()
    # Panel positions estimated from canonical hull in existing SVG
    panels = [
        (55,  265, "#c0392b", "A", "NOSE CAP", "bayonet"),
        (158, 218, "#2980b9", "B", "DORSAL FWD", "4xM2.5"),
        (263, 340, "#27ae60", "C", "CARGO BELLY", "hinged"),
        (363, 218, "#8e44ad", "D", "DORSAL AFT", "magnetic"),
        (452, 226, "#e67e22", "E", "AFT SERVICE", "4xM2.5"),
        (540, 258, "#16a085", "F", "ENGINE BELL", "bayonet"),
    ]
    callout_lines = []
    for x, y, col, lbl, name, closure in panels:
        above = "DORSAL" in name or "NOSE" in name or "ENGINE" in name
        ly = y - 42 if above else y + 44
        lx = x - 42
        callout_lines.append(
            f'  <line x1="{x}" y1="{y}" x2="{x}" y2="{ly+16}" stroke="{col}" stroke-width="1.5" stroke-dasharray="4 2"/>')
        callout_lines.append(
            f'  <rect x="{lx}" y="{ly-14}" width="96" height="34" rx="4" fill="{col}" opacity="0.92"/>')
        callout_lines.append(
            f'  <text x="{lx+48}" y="{ly+1}" text-anchor="middle" font-family="\'OpenDyslexic\',sans-serif"'
            f' font-weight="bold" font-size="9" fill="#ffffff">{lbl} {name}</text>')
        callout_lines.append(
            f'  <text x="{lx+48}" y="{ly+15}" text-anchor="middle" font-family="\'OpenDyslexic\',sans-serif"'
            f' font-size="8" fill="#ffffffcc">{closure}</text>')

    # Legend box
    legend = [
        '  <rect x="8" y="8" width="202" height="82" rx="5" fill="rgba(255,255,255,0.93)" stroke="#607080" stroke-width="1"/>',
        '  <text x="109" y="24" text-anchor="middle" font-family="\'OpenDyslexic\',sans-serif"'
        ' font-weight="bold" font-size="9" fill="#333">ACCESS PANELS</text>',
        '  <text x="109" y="38" text-anchor="middle" font-family="\'OpenDyslexic\',sans-serif"'
        ' font-size="8" fill="#555">Remove battery before opening any panel</text>',
    ]
    cols = ["#c0392b","#2980b9","#27ae60","#8e44ad","#e67e22","#16a085"]
    for i,lbl in enumerate(["A","B","C","D","E","F"]):
        bx = 12+i*31
        legend.append(f'  <rect x="{bx}" y="58" width="28" height="16" rx="3" fill="{cols[i]}"/>')
        legend.append(f'  <text x="{bx+14}" y="70" text-anchor="middle"'
                      f' font-family="\'OpenDyslexic\',sans-serif" font-weight="bold" font-size="9"'
                      f' fill="#fff">{lbl}</text>')

    inject = ('<g id="access-panel-callouts">\n' +
              "\n".join(callout_lines + legend) +
              '\n</g>\n')
    return existing.replace('</svg>', inject + '</svg>')


# ── OVERVIEW BOTTOM: add belly hatch callouts ──────────────────────────────────
def make_overview_bottom():
    existing = open("serenity/diagrams/overview_bottom.svg").read()
    panels = [
        (75,  290, "#c0392b", "A", "NOSE CAP", "bayonet"),
        (265, 250, "#27ae60", "C", "CARGO BELLY", "hinged (main)"),
        (450, 282, "#e67e22", "E", "AFT SERVICE", "belly access"),
        (538, 295, "#16a085", "F", "ENGINE BELL", "bayonet"),
    ]
    callout_lines = []
    for x, y, col, lbl, name, closure in panels:
        ly = y + 48
        lx = x - 48
        callout_lines.append(
            f'  <line x1="{x}" y1="{y}" x2="{x}" y2="{ly-14}" stroke="{col}" stroke-width="1.5" stroke-dasharray="4 2"/>')
        callout_lines.append(
            f'  <rect x="{lx}" y="{ly-14}" width="108" height="34" rx="4" fill="{col}" opacity="0.92"/>')
        callout_lines.append(
            f'  <text x="{lx+54}" y="{ly+1}" text-anchor="middle" font-family="\'OpenDyslexic\',sans-serif"'
            f' font-weight="bold" font-size="9" fill="#ffffff">{lbl} {name}</text>')
        callout_lines.append(
            f'  <text x="{lx+54}" y="{ly+15}" text-anchor="middle" font-family="\'OpenDyslexic\',sans-serif"'
            f' font-size="8" fill="#ffffffcc">{closure}</text>')

    seq = [
        '  <rect x="8" y="8" width="268" height="54" rx="5" fill="rgba(255,255,255,0.93)" stroke="#607080" stroke-width="1"/>',
        '  <text x="142" y="24" text-anchor="middle" font-family="\'OpenDyslexic\',sans-serif"'
        ' font-weight="bold" font-size="9" fill="#333">MAINTENANCE SEQUENCE (BELLY VIEW)</text>',
        '  <text x="142" y="40" text-anchor="middle" font-family="\'OpenDyslexic\',sans-serif"'
        ' font-size="8" fill="#555">F -> E -> D -> B -> A -> C (aft to forward)</text>',
        '  <text x="142" y="54" text-anchor="middle" font-family="\'OpenDyslexic\',sans-serif"'
        ' font-size="7.5" fill="#888">Remove battery before opening any panel</text>',
    ]
    inject = ('<g id="belly-panel-callouts">\n' +
              "\n".join(callout_lines + seq) +
              '\n</g>\n')
    return existing.replace('</svg>', inject + '</svg>')


# ── MAIN ───────────────────────────────────────────────────────────────────────
tasks = [
    ("build_guide_02_print_hull.svg",  make_step02),
    ("build_guide_22_void_formers.svg", make_step22),
    ("build_guide_23_foam_fill.svg",   make_step23),
    ("build_guide_24_access_panels.svg", make_step24),
    ("overview_side.svg",              make_overview_side),
    ("overview_bottom.svg",            make_overview_bottom),
]

for fname, fn in tasks:
    path = os.path.join(OUT, fname)
    content = fn()
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    kb = os.path.getsize(path) // 1024
    print(f"DONE: {path}  ({kb} KB)")

print("\nAll 6 SVG files written successfully.")
