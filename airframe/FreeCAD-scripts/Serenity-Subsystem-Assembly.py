"""
Serenity-UAV Subsystem Assembly Script
Assembles individual subsystems using FreeCAD Assembly4
Revision: R (June 2026)
"""

import FreeCAD as App
import Assembly4Lib
from FreeCAD import Vector
import os

def assemble_fuselage_hull():
    """
    Assemble the main fuselage hull subsystem
    Components:
    - Hull shell (main_hull.FCStd)
    - Foam fill structure
    - Internal structural braces
    """
    doc = App.newDocument("Fuselage_Assembly")
    
    # Import the main hull model
    hull = doc.addObject("Part::FeaturePython", "MainHull")
    # Assuming hull file exists: hull_shell_24inch.FCStd
    
    # Add internal structure components
    structure_brace_port = doc.addObject("Part::FeaturePython", "StructureBracePort")
    structure_brace_starboard = doc.addObject("Part::FeaturePython", "StructureBraceStarboard")
    
    # Create Assembly4 container
    assy = Assembly4Lib.newAssembly(doc, "Fuselage_Assembly")
    assy.Type = "Assembly"
    
    # Add hull to assembly
    hull_part = Assembly4Lib.importPart(doc, "hull_shell_24inch.FCStd", "MainHull")
    
    # Placement for port structural brace (relative to hull origin)
    brace_port_placement = App.Placement(
        Vector(50, 100, 0),
        App.Rotation(0, 0, 0)
    )
    structure_brace_port.Placement = brace_port_placement
    
    # Placement for starboard structural brace (mirrored)
    brace_starboard_placement = App.Placement(
        Vector(-50, 100, 0),
        App.Rotation(0, 0, 0)
    )
    structure_brace_starboard.Placement = brace_starboard_placement
    
    doc.recompute()
    return doc


def assemble_nacelle_subsystem(side="port"):
    """
    Assemble a single nacelle subsystem with dual EDF configuration
    
    Components per nacelle:
    - EDF_1 (forward 50mm, XFly Galaxy X5)
    - EDF_2 (aft 50mm, tandem, XFly Galaxy X5)
    - Inter-stage stator (11-fin twisted, 33° vane angle)
    - Nacelle pod structure (CF-PETG)
    - Variable-area iris nozzle (8-petal)
    - Tilt servo mount (digital, ≥25 kg·cm @ 6V)
    - Tilt pivot point (at Z=83 mm for CG alignment)
    
    Args:
        side: "port" or "starboard"
    """
    doc = App.newDocument(f"Nacelle_{side.capitalize()}_Assembly")
    
    assy = Assembly4Lib.newAssembly(doc, f"Nacelle_{side}")
    
    # Import nacelle pod
    nacelle_pod = Assembly4Lib.importPart(
        doc, 
        f"nacelle_pod_50mm_tandem_{side}.FCStd",
        f"NacelleBody_{side}"
    )
    
    # EDF 1 (forward) placement
    edf_1_placement = App.Placement(
        Vector(0, 0, 0),
        App.Rotation(0, 0, 0)
    )
    edf_1 = Assembly4Lib.importPart(doc, "EDF_XFly_Galaxy_X5_50mm.FCStd", f"EDF_1_{side}")
    edf_1.Placement = edf_1_placement
    
    # EDF 2 (aft/tandem) placement - 50mm aft of EDF 1
    edf_2_placement = App.Placement(
        Vector(0, 0, -50),  # Tandem series offset
        App.Rotation(0, 0, 0)
    )
    edf_2 = Assembly4Lib.importPart(doc, "EDF_XFly_Galaxy_X5_50mm.FCStd", f"EDF_2_{side}")
    edf_2.Placement = edf_2_placement
    
    # Inter-stage stator (11-fin, 33° vane angle, CF-PETG)
    stator_placement = App.Placement(
        Vector(0, 0, -25),  # Centered between EDF 1 and 2
        App.Rotation(0, 0, 0)
    )
    stator = Assembly4Lib.importPart(
        doc,
        f"nacelle_inter_stage_stator_11fin_33deg.FCStd",
        f"InterStageStator_{side}"
    )
    stator.Placement = stator_placement
    
    # Variable-area iris nozzle (8-petal)
    # Nozzle gear-linked to tilt pivot (M=1.0, no dedicated servo)
    nozzle_placement = App.Placement(
        Vector(0, 0, -60),  # Aft of aft EDF
        App.Rotation(0, 0, 0)
    )
    nozzle = Assembly4Lib.importPart(
        doc,
        "nacelle_iris_nozzle_8petal_linkage.FCStd",
        f"IrisNozzle_{side}"
    )
    nozzle.Placement = nozzle_placement
    
    # Tilt servo mount
    servo_mount_placement = App.Placement(
        Vector(30, 50, 0),  # Side-mounted on fuselage
        App.Rotation(0, 0, 0)
    )
    servo_mount = Assembly4Lib.importPart(
        doc,
        "tilt_servo_mount_25kgcm.FCStd",
        f"TiltServoMount_{side}"
    )
    servo_mount.Placement = servo_mount_placement
    
    # Tilt pivot joint (critical: at Z=83mm for CG alignment to eliminate gravity torque)
    pivot_placement = App.Placement(
        Vector(0, 0, 83),  # CG pivot for zero gravity torque
        App.Rotation(0, 0, 0)
    )
    pivot = Assembly4Lib.importPart(
        doc,
        "nacelle_pivot_bearing_assembly.FCStd",
        f"TiltPivot_{side}"
    )
    pivot.Placement = pivot_placement
    
    # Backlit translucent-blue PETG inner petal faces + WS2812B LED ring
    led_ring_placement = App.Placement(
        Vector(0, 0, -55),  # Inside nozzle
        App.Rotation(0, 0, 0)
    )
    led_ring = Assembly4Lib.importPart(
        doc,
        "WS2812B_LED_ring_addressable.FCStd",
        f"LEDRing_{side}"
    )
    led_ring.Placement = led_ring_placement
    
    # Constraint: Tilt pivot linked to servo
    # This would use Assembly4 constraints if the servo linkage is modeled
    
    doc.recompute()
    return doc


def assemble_cargo_bay():
    """
    Assemble the cargo bay subsystem (Rev P - complete)
    
    Components:
    - Port door (CF-PETG)
    - Starboard door (CF-PETG)
    - 8-barrel piano hinge on 3 mm CF rod
    - Door servo (SG90)
    - Release servo (SG90)
    - DRV8833 H-bridge controller
    - N20 winch motor
    - Dyneema SK75 0.5 mm line
    - Auto-latch payload cradle
    - HX711 load cell
    - FPV camera bezel
    - GPS retention ring
    - 3M foam gasket door seal
    """
    doc = App.newDocument("CargoBay_Assembly")
    assy = Assembly4Lib.newAssembly(doc, "CargoBay")
    
    # Port cargo door
    door_port_placement = App.Placement(
        Vector(-100, 0, 0),  # Port side
        App.Rotation(0, 0, 90)  # Hinge along Y-axis
    )
    door_port = Assembly4Lib.importPart(
        doc,
        "cargo_door_cfpetg_port.FCStd",
        "DoorPort"
    )
    door_port.Placement = door_port_placement
    
    # Starboard cargo door (mirrored)
    door_starboard_placement = App.Placement(
        Vector(100, 0, 0),  # Starboard side
        App.Rotation(0, 0, 90)
    )
    door_starboard = Assembly4Lib.importPart(
        doc,
        "cargo_door_cfpetg_starboard.FCStd",
        "DoorStarboard"
    )
    door_starboard.Placement = door_starboard_placement
    
    # Piano hinge assembly (8-barrel, 3 mm CF rod)
    hinge_placement = App.Placement(
        Vector(0, -50, 0),  # Along aft edge of cargo bay
        App.Rotation(0, 90, 0)
    )
    hinge = Assembly4Lib.importPart(
        doc,
        "piano_hinge_8barrel_3mm_CF.FCStd",
        "CargoDoorHinge"
    )
    hinge.Placement = hinge_placement
    
    # Door servo (SG90) for opening/closing
    door_servo_placement = App.Placement(
        Vector(0, 20, 50),  # Internally mounted
        App.Rotation(0, 0, 0)
    )
    door_servo = Assembly4Lib.importPart(
        doc,
        "SG90_servo.FCStd",
        "DoorServo"
    )
    door_servo.Placement = door_servo_placement
    
    # Release servo (SG90) for payload drop
    release_servo_placement = App.Placement(
        Vector(0, 40, 50),
        App.Rotation(0, 0, 0)
    )
    release_servo = Assembly4Lib.importPart(
        doc,
        "SG90_servo.FCStd",
        "ReleaseServo"
    )
    release_servo.Placement = release_servo_placement
    
    # N20 winch motor
    winch_motor_placement = App.Placement(
        Vector(0, 60, 50),
        App.Rotation(0, 90, 0)
    )
    winch_motor = Assembly4Lib.importPart(
        doc,
        "N20_winch_motor.FCStd",
        "WinchMotor"
    )
    winch_motor.Placement = winch_motor_placement
    
    # Dyneema SK75 line (0.5 mm) - modeled as cylinder constraint
    dyneema_line = Assembly4Lib.importPart(
        doc,
        "dyneema_SK75_0_5mm_line.FCStd",
        "DyneeamLine"
    )
    
    # Auto-latch payload cradle
    cradle_placement = App.Placement(
        Vector(0, 0, 0),  # Center of bay
        App.Rotation(0, 0, 0)
    )
    cradle = Assembly4Lib.importPart(
        doc,
        "payload_cradle_autolatch.FCStd",
        "PayloadCradle"
    )
    cradle.Placement = cradle_placement
    
    # HX711 load cell
    load_cell_placement = App.Placement(
        Vector(0, -80, 0),
        App.Rotation(0, 0, 0)
    )
    load_cell = Assembly4Lib.importPart(
        doc,
        "HX711_load_cell.FCStd",
        "LoadCell"
    )
    load_cell.Placement = load_cell_placement
    
    # FPV camera bezel
    camera_bezel_placement = App.Placement(
        Vector(0, 0, 30),  # Forward viewing
        App.Rotation(0, 0, 0)
    )
    camera_bezel = Assembly4Lib.importPart(
        doc,
        "FPV_camera_bezel.FCStd",
        "CameraBezel"
    )
    camera_bezel.Placement = camera_bezel_placement
    
    # GPS retention ring
    gps_ring_placement = App.Placement(
        Vector(0, 0, 35),
        App.Rotation(0, 0, 0)
    )
    gps_ring = Assembly4Lib.importPart(
        doc,
        "GPS_retention_ring.FCStd",
        "GPSRing"
    )
    gps_ring.Placement = gps_ring_placement
    
    # 3M foam gasket door seal (frame around perimeter)
    gasket_seal = Assembly4Lib.importPart(
        doc,
        "foam_gasket_door_seal_3M.FCStd",
        "DoorSeal"
    )
    
    doc.recompute()
    return doc


def assemble_avionics_bay():
    """
    Assemble the avionics subsystem (Rev Q - EMI-hardened v2 capes)
    
    Components:
    - 8 × PocketBeagle 2 Industrial (AM6254) nodes
    - 4 × Wash (sensor capes: GPS, IMU, barometer, airspeed, FPV camera, TPM 2.0, ADC, ESC telemetry, PWM, GPIO)
    - 4 × Zoë (comms capes: MAVLink/SiK 915 MHz, LoRa RFM95W 915 MHz, TI WL1837MOD WiFi/BT, 49 MHz TDDS transceiver, CAN FD, MIL-STD-1553B, RS-485, Ethernet RSTP ring, TPM 2.0, write-blocker CPLD, NX-enforced microSD)
    - XCVR-49MHZ-2 sub-module (per each node)
    - Power distribution board
    - Isolated transceiver modules (5 kV IEC 62368-1 / VDE 0884-11 certified)
    """
    doc = App.newDocument("AvionicsBay_Assembly")
    assy = Assembly4Lib.newAssembly(doc, "AvionicsBay")
    
    # PocketBeagle 2 node positions: Bays A, B, D, E (4 rows, 2 columns)
    # Bay A (Shepherd's room): nodes 0, 1
    # Bay B (Inara's shuttle): nodes 2, 3
    # Bay D (River's room):    nodes 4, 5
    # Bay E (Simon's medbay):  nodes 6, 7
    
    bay_positions = {
        "BayA": {"offset": Vector(0, 0, 150), "nodes": [0, 1]},
        "BayB": {"offset": Vector(0, 50, 150), "nodes": [2, 3]},
        "BayD": {"offset": Vector(0, 100, 150), "nodes": [4, 5]},
        "BayE": {"offset": Vector(0, 150, 150), "nodes": [6, 7]},
    }
    
    node_counter = 0
    for bay_name, bay_info in bay_positions.items():
        bay_offset = bay_info["offset"]
        nodes = bay_info["nodes"]
        
        for idx, node_id in enumerate(nodes):
            # Offset for left/right stacking within bay
            node_offset = Vector(
                bay_offset.x + (-20 if idx == 0 else 20),
                bay_offset.y,
                bay_offset.z
            )
            
            # PocketBeagle 2 Industrial
