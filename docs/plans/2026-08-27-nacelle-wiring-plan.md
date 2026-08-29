# nacelle wiring

## Problemm

### 4 x 10AWG conductors can't fit in a 7mm cableway

Minimum space is 12x12mm internal diameter -> 16mm od tube

### 4 x off axis 10AWG conductors can't rotate or bend around 145 deg of tilt

ESC cables must route along axis of nacelle rotation to avoid binding and damage

### 8mm steel rotating spar doesn't work

## Proposed solution:

Replace steel rotating spar with a 16mm carbon fiber tube to provide a hollow lumen for wiring.  Re-engineer airfoil to support the new tube and provide cableways for navigation lights and sensor data.

Create a pivoting joint at the wingtip joint with the nacelle and a structural ring to the nacelle around the pivot, removing the skewered shaft

Drive the nacelle tilt using a toothed belt and sprockets from the fuselage mounted servo motors.

Create a belt path through the wing.

`This landing is going to be interesting.` - Wash
`Define interesting.` - Mal
`Oh God, oh God, we're all going to die.` - Wash

### 1. Parameter Block & Lumen Partitioning (nacelle_pod_50mm_tandem.scad)

    [ ] Step 1.1: Set up the 16 mm spar and internal wire parameters:

    ```OpenSCAD

        SPAR_OD         = 16.0;   // [mm] fixed carbon fiber spar outer diameter
        SPAR_BORE_D     = 11.0;   // [mm] internal lumen diameter for 4x 10 AWG power bundle
    ```

    [ ] Step 1.2: Retain and Relocate Signal Channels: Do not delete the nav light channel. Instead, adapt NAV_CHAN_* to run along the outside of the 16 mm spar (within the rotating collar or pylon fairing wall) or allocate a dedicated, isolated micro-channel separated from the 10 AWG power bundle.

    [ ] Step 1.3: Update PIVOT_Z = 111.5 and mass breakdowns to reflect the 16 mm structural envelope.

### 2 Signal Isolation & Auxiliary Routing

    [ ] Step 2.1: Nav Light Circuit Path:

        Maintain the internal channel from the outboard WS2812C recess (NAV_LIGHT_Z = 70.0) down into the rotating nacelle pylon collar.

        Provide a low-profile slip-ring or flexible service loop bridge inside the wingtip garage so the 3-core signal wire can bridge the rotating nacelle interface safely without binding.

    [ ] Step 2.2: Hall Effect (HE) Tilt Encoder Architecture:

        Design Recommendation: Mount the HE encoder chip (e.g., an AS5600 magnetic encoder board) statically to the fixed wingtip rib/spar mount, facing a diametric magnet embedded in the rotating nacelle hub.

        Wiring Benefit: Because the sensor is stationary on the fixed wing side, its wiring stays entirely within the fixed wing harness. It never enters the twisting spar lumen, eliminating wire fatigue and keeping it physically isolated from the 10 AWG power EMI.

### 3: Wingtip "Garage" & Field-Maintainable Junction

    [ ] Step 3.1: Model the removable wingtip access hatch module to expose the outboard end of the fixed spar, bullet connectors for the 4x 10 AWG power lines, and the static HE encoder plug.

    [ ] Step 3.2: Implement the Split-Collar Pinch Clamp with M3 heat-set inserts to secure the 16 mm spar without crushing it.

    [ ] Step 3.3: Ensure the wingtip garage internal volume has logical partitioning to keep the high-power ESC bullet connectors physically separated from the low-voltage signal connections (HE encoder & nav light).

### 4 Mesh Export, Baking & Verification

    [ ] Step 4.1: Render and export updated port and starboard STLs:
    
    ```bash

        openscad -o nacelle_port_revs.stl nacelle_pod_50mm_tandem.scad -D SWIRL_DIR=-1 -D PYLON_SIDE=-1 -D NACELLE_SIDE=-1
        
        openscad -o nacelle_stbd_revs.stl nacelle_pod_50mm_tandem.scad -D SWIRL_DIR=1 -D PYLON_SIDE=1 -D NACELLE_SIDE=1
    ```

[ ] Step 4.2: Re-run the hull frame baking script:

    ```bash

        python3 tools/bake_hull_frame.py Nacelle_Port Nacelle_Stbd

    ```

[ ] Step 4.3: Inspect meshes in FreeCAD to confirm the 16 mm bore clearance, power lumen, isolated nav-light path, and HE encoder bracket alignment.
