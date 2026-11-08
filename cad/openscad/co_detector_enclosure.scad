// ==============================================================================
// Smart Dual Gas Detector (CO + LPG) - Parametric Enclosure Model
// Revision: 2.0 (Stage 5 Architecture)
// Compatible with: OpenSCAD, FreeCAD, and SolidWorks Import
// ==============================================================================

$fn = 64; // High-resolution mesh curves

// ------------------------------------------------------------------------------
// 1. GLOBAL ENCLOSURE PARAMETERS
// ------------------------------------------------------------------------------
pcb_x        = 70.0;   // PCB length (mm)
pcb_y        = 50.0;   // PCB width (mm)
pcb_t        = 1.6;    // PCB thickness (mm)
margin       = 11.0;   // Perimeter margin around PCB (mm)

encl_x       = pcb_x + 2 * margin; // 92.0 mm
encl_y       = pcb_y + 2 * margin; // 72.0 mm
corner_r     = 10.0;   // Outer squircle corner radius (mm)

wall_t       = 2.20;   // Nominal uniform wall thickness (mm)
base_h       = 10.00;  // Lower chassis height (mm)
cover_h      = 18.00;  // Upper front cover height (mm)
standoff_h   = 4.50;   // PCB boss standoff height (mm)

// ------------------------------------------------------------------------------
// 2. COMPONENT COORDINATES (Centered Enclosure Origin [0, 0, 0])
// ------------------------------------------------------------------------------
// PCB Center is at [0, 0]
// PCB lower-left corner was (0,0) in KiCad -> Offset by [-35, -25]

boss_offsets = [
    [-31.5, -21.5], // H3
    [ 31.5, -21.5], // H4
    [-31.5,  21.5], // H1
    [ 31.5,  21.5]  // H2
];

ls1_pos      = [-3.00,  13.00]; // Buzzer center (32.0 - 35, 38.0 - 25)
s1_co_pos    = [21.50,  10.50]; // Winsen ME3-CO (56.5 - 35, 35.5 - 25)
s2_lpg_pos   = [24.00, -18.50]; // Figaro TGS2610 (59.0 - 35, 6.5 - 25)
thermal_x    = 17.00;          // Barrier rib X position (52.0 - 35)

led_x        = [-8.20, -5.00, -1.80, 1.40]; // D4, D5, D6, D8 (pitch 3.2mm)
led_y        = 21.00;                       // Y=46 - 25
btn_pos      = [7.00, 16.00];               // Center of SW1 & SW2 cluster

term_j1_y    = -13.00; // J1 Terminal center (12.0 - 25)
term_j2_y    =  13.00; // J2 Terminal center (38.0 - 25)

// ------------------------------------------------------------------------------
// 3. BASE PRIMITIVES
// ------------------------------------------------------------------------------
module rounded_rect_2d(length, width, radius) {
    hull() {
        translate([-(length/2 - radius), -(width/2 - radius), 0]) circle(r=radius);
        translate([ (length/2 - radius), -(width/2 - radius), 0]) circle(r=radius);
        translate([-(length/2 - radius),  (width/2 - radius), 0]) circle(r=radius);
        translate([ (length/2 - radius),  (width/2 - radius), 0]) circle(r=radius);
    }
}

module squircle_box(length, width, height, radius) {
    linear_extrude(height = height)
        rounded_rect_2d(length, width, radius);
}

// ------------------------------------------------------------------------------
// 4. LOWER CHASSIS BASE MODULE
// ------------------------------------------------------------------------------
module rear_chassis_base() {
    difference() {
        // Outer solid
        squircle_box(encl_x, encl_y, base_h, corner_r);
        
        // Inner cavity
        translate([0, 0, wall_t])
            squircle_box(encl_x - 2*wall_t, encl_y - 2*wall_t, base_h, corner_r - wall_t);
            
        // Terminal block cutouts (Left side, X = -encl_x/2)
        translate([-encl_x/2 - 1, term_j1_y - 6, wall_t + 2])
            cube([wall_t + 2, 12, base_h]);
            
        translate([-encl_x/2 - 1, term_j2_y - 6, wall_t + 2])
            cube([wall_t + 2, 12, base_h]);
            
        // Bottom convection intake slots for LPG sensor (Zone F)
        for (i = [-2 : 2]) {
            translate([s2_lpg_pos[0] + i*4, -encl_y/2 - 1, wall_t + 1.5])
                cube([2.0, wall_t + 2, 4.0]);
        }
        
        // Bottom draft slots underneath PCB
        for (i = [-2 : 2]) {
            translate([s2_lpg_pos[0] + i*4.5, s2_lpg_pos[1] - 8, -1])
                cube([2.0, 16.0, wall_t + 2]);
        }
        
        // Perimeter stepped lap-joint shelf (for interlocking cover)
        translate([0, 0, base_h - 1.2])
            difference() {
                squircle_box(encl_x + 1, encl_y + 1, 2, corner_r);
                squircle_box(encl_x - 1.4, encl_y - 1.4, 3, corner_r - 1.0);
            }
            
        // 4x Bayonet slide lock slots on bottom floor
        for (pos = [[-30, -20], [30, -20], [-30, 20], [30, 20]]) {
            translate([pos[0], pos[1], -1]) {
                cylinder(r=3.5, h=wall_t+2);
                translate([0, -3, 0]) cube([4.0, 6.0, wall_t+2], center=true);
            }
        }
    }
    
    // 4x PCB Mounting Bosses with M2.5 heat-set insert cores
    for (p = boss_offsets) {
        translate([p[0], p[1], wall_t]) {
            difference() {
                cylinder(r=2.75, h=standoff_h); // OD = 5.5mm
                cylinder(r=1.80, h=standoff_h + 1); // ID = 3.6mm for M2.5 insert
            }
            // Gusset reinforcement ribs (3x per boss)
            for (a = [0, 120, 240]) {
                rotate([0, 0, a])
                    translate([1.5, -0.6, 0])
                        cube([3.5, 1.2, standoff_h * 0.75]);
            }
        }
    }
}

// ------------------------------------------------------------------------------
// 5. UPPER FRONT HOUSING COVER MODULE
// ------------------------------------------------------------------------------
module front_housing_cover() {
    difference() {
        // Outer aesthetic shell with domed ceiling
        union() {
            squircle_box(encl_x, encl_y, cover_h - 3, corner_r);
            // Domed top cap
            translate([0, 0, cover_h - 3])
                intersection() {
                    squircle_box(encl_x, encl_y, 6, corner_r);
                    translate([0, 0, -240])
                        sphere(r=246);
                }
        }
        
        // Inner cavity (uniform 2.2mm wall)
        translate([0, 0, -1])
            squircle_box(encl_x - 2*wall_t, encl_y - 2*wall_t, cover_h - wall_t, corner_r - wall_t);
            
        // 1. Acoustic Rosette Horn Grill (LS1 Buzzer)
        translate([ls1_pos[0], ls1_pos[1], cover_h - 6]) {
            cylinder(r=1.6, h=10); // Center hole
            for (a = [0 : 60 : 300]) {
                rotate([0, 0, a])
                    translate([3.6, 0, 0])
                        cylinder(r=1.1, h=10); // Satellite holes
            }
        }
        
        // 2. Optical Light Pipe Aperture (4 LEDs)
        translate([ (led_x[0]+led_x[3])/2, led_y, cover_h - 6])
            cube([15.0, 3.8, 10], center=true);
            
        // 3. Ergonomic Test/Mute Button Aperture
        translate([btn_pos[0], btn_pos[1], cover_h - 6])
            rounded_rect_slot(18.0, 12.0, 2.5, 10);
            
        // 4. CO Sensor Diffusion Louvers (Over S1 Winsen ME3-CO)
        for (dy = [-6 : 3 : 6]) {
            translate([s1_co_pos[0], s1_co_pos[1] + dy, cover_h - 6])
                cube([14.0, 1.2, 10], center=true);
        }
        
        // 5. LPG Convective Exhaust Vents (Top perimeter of Zone F)
        for (i = [-2 : 2]) {
            translate([s2_lpg_pos[0] + i*4, encl_y/2 - wall_t - 1, cover_h - 7])
                cube([2.0, wall_t + 2, 4.0]);
        }
        
        // Interlocking stepped lip (engages rear chassis)
        translate([0, 0, -1])
            difference() {
                squircle_box(encl_x - 1.2, encl_y - 1.2, 2.5, corner_r - 0.8);
                squircle_box(encl_x - 2*wall_t, encl_y - 2*wall_t, 4, corner_r - wall_t);
            }
    }
    
    // Internal Thermal & Gas Barrier Rib (Isolates CO cell from LPG heater plume)
    translate([thermal_x - 0.7, -(encl_y/2 - wall_t - 1), 5.0])
        cube([1.4, encl_y - 2*wall_t - 2, cover_h - 5.0 - wall_t]);
        
    // Buzzer Acoustic Shroud Cylinder (compresses O-ring against LS1)
    translate([ls1_pos[0], ls1_pos[1], 10.0])
        difference() {
            cylinder(r=7.0, h=cover_h - 10.0 - wall_t);
            cylinder(r=5.5, h=cover_h - 10.0 - wall_t + 1);
        }
}

module rounded_rect_slot(length, width, radius, height) {
    linear_extrude(height = height)
        hull() {
            translate([-(length/2 - radius), -(width/2 - radius), 0]) circle(r=radius);
            translate([ (length/2 - radius), -(width/2 - radius), 0]) circle(r=radius);
            translate([-(length/2 - radius),  (width/2 - radius), 0]) circle(r=radius);
            translate([ (length/2 - radius),  (width/2 - radius), 0]) circle(r=radius);
        }
}

// ------------------------------------------------------------------------------
// 6. WALL MOUNT BRACKET MODULE
// ------------------------------------------------------------------------------
module wall_mount_bracket() {
    brk_x = encl_x - 6.0; // 86.0 mm
    brk_y = encl_y - 6.0; // 66.0 mm
    brk_t = 3.0;          // 3.0 mm
    
    difference() {
        // Base plate
        squircle_box(brk_x, brk_y, brk_t, corner_r - 2);
        
        // 1. EU Standard 60mm Junction Box Keyholes
        translate([-30.0, 0, -1]) keyhole();
        translate([ 30.0, 0, -1]) keyhole();
        
        // 2. US Standard 83.5mm Gang Box Keyholes
        translate([0, -41.75, -1]) rotate([0, 0, 90]) keyhole();
        translate([0,  41.75, -1]) rotate([0, 0, 90]) keyhole();
        
        // 3. Central Wire Pass-Through Opening
        translate([0, 0, -1])
            rounded_rect_slot(34.0, 22.0, 4.0, brk_t + 2);
            
        // 4. Bubble Level Alignment Pocket
        translate([0, 22.0, brk_t - 1.5])
            cylinder(r=4.2, h=3); // Recess for dia 8mm spirit level vial
    }
    
    // 4x Bayonet Sliding Wedge Lugs (dock into rear chassis)
    for (pos = [[-30, -20], [30, -20], [-30, 20], [30, 20]]) {
        translate([pos[0], pos[1], brk_t]) {
            cylinder(r=3.2, h=2.5);
            translate([0, 0, 2.5])
                cylinder(r=4.5, h=1.8);
        }
    }
}

module keyhole() {
    union() {
        cylinder(r=4.5, h=10); // Entry hole for screw head
        translate([0, 4.5, 0])
            cylinder(r=2.4, h=10); // Locking slot for screw shank
        translate([-2.4, 0, 0])
            cube([4.8, 4.5, 10]);
    }
}

// ------------------------------------------------------------------------------
// 7. OPTICAL LIGHT PIPE (4-Channel Polycarbonate)
// ------------------------------------------------------------------------------
module optical_light_pipe() {
    union() {
        // Common runner spine
        translate([ (led_x[0]+led_x[3])/2, led_y, 6.0])
            cube([13.5, 2.6, 2.0], center=true);
            
        // 4x Light Guide Columns
        for (lx = led_x) {
            translate([lx, led_y, 0]) {
                // Cylindrical core
                cylinder(r=1.0, h=8.0);
                // Lower convex light gathering lens
                translate([0, 0, 0.4])
                    sphere(r=1.1);
            }
        }
    }
}

// ------------------------------------------------------------------------------
// 8. ERGONOMIC COMPLIANT TEST BUTTON CAP
// ------------------------------------------------------------------------------
module button_actuator_cap() {
    union() {
        // Main button touch surface
        translate([btn_pos[0], btn_pos[1], 0])
            difference() {
                rounded_rect_slot(17.0, 11.0, 2.0, 2.2);
                // Tactile finger concavity
                translate([0, 0, 26.0])
                    sphere(r=25.0);
            }
            
        // Plunger pins contacting SW1 and SW2
        translate([7.0, 19.0, -3.0]) cylinder(r=1.5, h=3.0);
        translate([7.0, 13.0, -3.0]) cylinder(r=1.5, h=3.0);
    }
}

// ------------------------------------------------------------------------------
// 9. DUMMY PCB (For Visual Verification)
// ------------------------------------------------------------------------------
module pcb_assembly_preview() {
    color([0.1, 0.5, 0.2, 0.9])
        translate([0, 0, standoff_h + wall_t]) {
            difference() {
                translate([-pcb_x/2, -pcb_y/2, 0])
                    cube([pcb_x, pcb_y, pcb_t]);
                for (p = boss_offsets)
                    translate([p[0], p[1], -1])
                        cylinder(r=1.6, h=pcb_t + 2);
            }
        }
        
    // Winsen ME3-CO Model
    color([0.8, 0.8, 0.8])
        translate([s1_co_pos[0], s1_co_pos[1], standoff_h + wall_t + pcb_t])
            cylinder(r=10.0, h=16.5);
            
    // Figaro TGS2610 Model
    color([0.7, 0.7, 0.3])
        translate([s2_lpg_pos[0], s2_lpg_pos[1], standoff_h + wall_t + pcb_t])
            cylinder(r=4.6, h=8.5);
            
    // Buzzer LS1 Model
    color([0.2, 0.2, 0.2])
        translate([ls1_pos[0], ls1_pos[1], standoff_h + wall_t + pcb_t])
            cylinder(r=6.1, h=6.5);
}

// ------------------------------------------------------------------------------
// 10. DISPLAY SELECTOR (Uncomment desired view)
// ------------------------------------------------------------------------------
// View 1: Complete Assembled Unit
// front_housing_cover();
// rear_chassis_base();

// View 2: Exploded Assembly View
module exploded_view() {
    translate([0, 0,  35]) color([0.95, 0.95, 0.95, 0.85]) front_housing_cover();
    translate([0, 0,  40]) color([0.90, 0.20, 0.20]) button_actuator_cap();
    translate([0, 0,  38]) color([0.80, 0.90, 1.00, 0.80]) optical_light_pipe();
    translate([0, 0,   0]) pcb_assembly_preview();
    translate([0, 0, -18]) color([0.30, 0.30, 0.35]) rear_chassis_base();
    translate([0, 0, -32]) color([0.20, 0.20, 0.20]) wall_mount_bracket();
}

exploded_view();
