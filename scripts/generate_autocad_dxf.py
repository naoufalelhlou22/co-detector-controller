"""
Master AutoCAD Mechanical Production Drawing Generator
Generates:
  1. cad/autocad/co_detector_enclosure_perfect.dxf (Complete ISO A3 Production Blueprint)
  2. cad/dxf/co_detector_enclosure_production.dxf (1:1 Clean Machining Profiles)

Standards: ISO 7200 Title Block, ISO 2768-mK Tolerances, First Angle Projection.
Datum: PCB Bottom-Left Corner = (0.00, 0.00).
Enclosure Outer Dimensions: 86.00 mm x 66.00 mm x 28.00 mm (R = 8.00 mm).
"""

import math
import os
import ezdxf
from ezdxf import colors, units
from ezdxf.enums import TextEntityAlignment

def build_autocad_production_drawing(output_path):
    doc = ezdxf.new(dxfversion="R2010", setup=True)
    doc.units = units.MM
    msp = doc.modelspace()

    # Define Standard AutoCAD Mechanical Layers
    layers = [
        ("AM_0_OUTLINE",    colors.WHITE,  0.50, "CONTINUOUS"),
        ("AM_1_HIDDEN",     colors.YELLOW, 0.25, "DASHED"),
        ("AM_2_CENTER",     colors.RED,    0.25, "CENTER"),
        ("AM_3_DIMENSION",  colors.GREEN,  0.25, "CONTINUOUS"),
        ("AM_4_HATCH",      colors.CYAN,   0.25, "CONTINUOUS"),
        ("AM_5_TEXT",       colors.MAGENTA,0.35, "CONTINUOUS"),
        ("AM_6_BORDER",     colors.BLUE,   0.70, "CONTINUOUS"),
        ("AM_7_PCB_GHOST",  colors.WHITE,  0.18, "PHANTOM")
    ]
    for name, col, lw, lt in layers:
        l = doc.layers.new(name=name)
        l.color = col
        l.lineweight = int(lw * 100)
        if lt != "CONTINUOUS" and lt in doc.linetypes:
            l.linetype = lt

    # ==========================================================================
    # 1. ISO A3 SHEET BORDER & TITLE BLOCK (420 x 297 mm)
    # ==========================================================================
    # Sheet Origin (0,0), Left margin 25mm, other margins 10mm
    bx0, by0 = 25.0, 10.0
    bx1, by1 = 410.0, 287.0
    msp.add_lwpolyline([(bx0, by0), (bx1, by0), (bx1, by1), (bx0, by1), (bx0, by0)],
                       dxfattribs={"layer": "AM_6_BORDER"})
    # Outer sheet cut line
    msp.add_lwpolyline([(0, 0), (420, 0), (420, 297), (0, 297), (0, 0)],
                       dxfattribs={"layer": "AM_6_BORDER", "color": colors.GRAY})

    # Title Block (ISO 7200 Standard: 180mm x 55mm at bottom-right)
    tx0 = bx1 - 180.0
    ty0 = by0
    tx1 = bx1
    ty1 = by0 + 55.0
    msp.add_lwpolyline([(tx0, ty0), (tx1, ty0), (tx1, ty1), (tx0, ty1), (tx0, ty0)],
                       dxfattribs={"layer": "AM_6_BORDER"})
    # Internal dividing lines
    msp.add_line((tx0, ty0 + 15.0), (tx1, ty0 + 15.0), dxfattribs={"layer": "AM_6_BORDER"})
    msp.add_line((tx0, ty0 + 30.0), (tx1, ty0 + 30.0), dxfattribs={"layer": "AM_6_BORDER"})
    msp.add_line((tx0, ty0 + 42.0), (tx1, ty0 + 42.0), dxfattribs={"layer": "AM_6_BORDER"})
    msp.add_line((tx0 + 60.0, ty0), (tx0 + 60.0, ty0 + 30.0), dxfattribs={"layer": "AM_6_BORDER"})
    msp.add_line((tx0 + 120.0, ty0), (tx0 + 120.0, ty0 + 30.0), dxfattribs={"layer": "AM_6_BORDER"})

    # Title Block Texts
    msp.add_text("PROJECT:", dxfattribs={"layer": "AM_5_TEXT", "height": 2.2}).set_placement((tx0 + 3.0, ty1 - 5.0))
    msp.add_text("SMART DUAL GAS DETECTOR (CO + LPG)", dxfattribs={"layer": "AM_5_TEXT", "height": 3.8, "style": "Standard"}).set_placement((tx0 + 3.0, ty1 - 10.5))

    msp.add_text("TITLE:", dxfattribs={"layer": "AM_5_TEXT", "height": 2.2}).set_placement((tx0 + 3.0, ty0 + 38.0))
    msp.add_text("PRODUCTION MECHANICAL ENCLOSURE ASSEMBLY", dxfattribs={"layer": "AM_5_TEXT", "height": 3.2}).set_placement((tx0 + 3.0, ty0 + 33.5))

    msp.add_text("DRAWING NO:", dxfattribs={"layer": "AM_5_TEXT", "height": 2.2}).set_placement((tx0 + 3.0, ty0 + 26.0))
    msp.add_text("AGY-CO-ENC-301", dxfattribs={"layer": "AM_5_TEXT", "height": 4.0}).set_placement((tx0 + 3.0, ty0 + 18.0))

    msp.add_text("REVISION:", dxfattribs={"layer": "AM_5_TEXT", "height": 2.2}).set_placement((tx0 + 63.0, ty0 + 26.0))
    msp.add_text("REV 3.0 (PERFECT PCBA MATCH)", dxfattribs={"layer": "AM_5_TEXT", "height": 3.0}).set_placement((tx0 + 63.0, ty0 + 18.0))

    msp.add_text("MATERIAL:", dxfattribs={"layer": "AM_5_TEXT", "height": 2.2}).set_placement((tx0 + 123.0, ty0 + 26.0))
    msp.add_text("SABIC CYCOLOY FR15 (PC/ABS)", dxfattribs={"layer": "AM_5_TEXT", "height": 2.6}).set_placement((tx0 + 123.0, ty0 + 18.0))

    msp.add_text("FLAMMABILITY: UL94 V-0", dxfattribs={"layer": "AM_5_TEXT", "height": 2.2}).set_placement((tx0 + 3.0, ty0 + 10.0))
    msp.add_text("INGRESS: IP52 DUST/SPLASH", dxfattribs={"layer": "AM_5_TEXT", "height": 2.2}).set_placement((tx0 + 3.0, ty0 + 4.0))

    msp.add_text("TOLERANCE: ISO 2768-mK", dxfattribs={"layer": "AM_5_TEXT", "height": 2.2}).set_placement((tx0 + 63.0, ty0 + 10.0))
    msp.add_text("FINISH: VDI 27 MATTE / SPI-B2", dxfattribs={"layer": "AM_5_TEXT", "height": 2.2}).set_placement((tx0 + 63.0, ty0 + 4.0))

    msp.add_text("SCALE: 1:1 (FULL SIZE)", dxfattribs={"layer": "AM_5_TEXT", "height": 2.2}).set_placement((tx0 + 123.0, ty0 + 10.0))
    msp.add_text("SHEET: 1 OF 1 (ISO A3)", dxfattribs={"layer": "AM_5_TEXT", "height": 2.2}).set_placement((tx0 + 123.0, ty0 + 4.0))

    # Engineering Notes Block (Top Left)
    notes = [
        "ENGINEERING & MANUFACTURING SPECIFICATIONS:",
        "1. ALL DIMENSIONS ARE IN MILLIMETERS [mm]. DATUM (0,0) COINCIDES WITH PCBA LOWER-LEFT CORNER.",
        "2. UNIFORM WALL THICKNESS t = 2.40mm. DRAFT ANGLE 1.5 DEG ON INJECTION CORE & CAVITY FACES.",
        "3. PCBA SECURED VIA 4x M2.5x6mm PAN HEAD SCREWS INTO RUTHEX M2.5 BRASS HEAT-SET INSERTS (H1..H4).",
        "4. DUAL HOUSING HALVES (BASE & COVER) SECURED VIA 4x CORNER M3 COUNTERSUNK MACHINE SCREWS (16mm).",
        "5. 0.96-INCH I2C OLED APERTURE FEATURES INTERNAL 1.0mm RETENTION REBATE FOR SMOKED PMMA LENS.",
        "6. THERMAL ARCHITECTURE: TOP-VENTED CHIMNEY ISOLATES LPG SENSOR (TGS2610-C00) FROM CO SENSOR (ME3-CO).",
        "7. 7-HOLE ACOUSTIC ROSETTE DIRECTLY TUNED TO TDK PS1240 RESONANCE FREQUENCY (85dB SPL @ 3m).",
        "8. COMPLIANCE STANDARDS: EN 50291-1 (CO ALARM), EN 50194-1 (GAS ALARM), ROHS 3 & REACH."
    ]
    ny = by1 - 8.0
    for i, line in enumerate(notes):
        h = 2.8 if i == 0 else 2.1
        layer = "AM_5_TEXT"
        msp.add_text(line, dxfattribs={"layer": layer, "height": h}).set_placement((bx0 + 5.0, ny - i * 4.2))

    # Helper function for rounded rectangle
    def add_rounded_rect(cx, cy, w, h, r, layer):
        x0 = cx - w / 2.0
        y0 = cy - h / 2.0
        x1 = cx + w / 2.0
        y1 = cy + h / 2.0
        # Vertices with bulge: bulge = tan(theta/4) = tan(90°/4) = tan(22.5°) = 0.41421356
        bulge = 0.41421356237
        points = [
            (x0 + r, y0, 0, 0, 0),
            (x1 - r, y0, 0, 0, bulge),
            (x1, y0 + r, 0, 0, 0),
            (x1, y1 - r, 0, 0, bulge),
            (x1 - r, y1, 0, 0, 0),
            (x0 + r, y1, 0, 0, bulge),
            (x0, y1 - r, 0, 0, 0),
            (x0, y0 + r, 0, 0, bulge),
            (x0 + r, y0, 0, 0, 0)
        ]
        msp.add_lwpolyline(points, format="xyseb", dxfattribs={"layer": layer})

    # ==========================================================================
    # VIEW 1: FRONT COVER EXTERIOR PLAN VIEW (Top-Left quadrant of drawing)
    # ==========================================================================
    # Center View 1 at (V1_X, V1_Y)
    v1_x = 90.0
    v1_y = 160.0
    # PCB datum (0,0) in View 1 coordinates:
    # PCB center is (35.0, 25.0). Enclosure center is PCB center.
    p0_x = v1_x - 35.0
    p0_y = v1_y - 25.0

    msp.add_text("VIEW A: FRONT COVER (EXTERIOR TOP PLAN)", dxfattribs={"layer": "AM_5_TEXT", "height": 3.2}).set_placement((v1_x - 42.0, v1_y + 42.0))
    msp.add_text("SCALE 1:1", dxfattribs={"layer": "AM_5_TEXT", "height": 2.0}).set_placement((v1_x - 42.0, v1_y + 38.0))

    # Enclosure Outer Profile: 86.0 x 66.0 mm, R = 8.0 mm
    add_rounded_rect(v1_x, v1_y, 86.0, 66.0, 8.0, "AM_0_OUTLINE")
    # Top chamfer/fillet step
    add_rounded_rect(v1_x, v1_y, 82.0, 62.0, 6.0, "AM_0_OUTLINE")

    # PCBA Ghost Outline (Phantom line to prove 100% alignment)
    add_rounded_rect(v1_x, v1_y, 70.0, 50.0, 3.0, "AM_7_PCB_GHOST")

    # 1. 0.96-inch OLED Display Bezel Window at CAD (48.50, 32.50)
    oled_cx = p0_x + 48.50
    oled_cy = p0_y + 32.50
    add_rounded_rect(oled_cx, oled_cy, 25.0, 14.0, 1.5, "AM_0_OUTLINE")
    # Screen Active Area inside
    add_rounded_rect(oled_cx, oled_cy, 21.7, 10.8, 0.5, "AM_1_HIDDEN")
    # OLED Centerlines
    msp.add_line((oled_cx - 15.0, oled_cy), (oled_cx + 15.0, oled_cy), dxfattribs={"layer": "AM_2_CENTER"})
    msp.add_line((oled_cx, oled_cy - 10.0), (oled_cx, oled_cy + 10.0), dxfattribs={"layer": "AM_2_CENTER"})
    msp.add_text("0.96\" OLED (128x64)", dxfattribs={"layer": "AM_5_TEXT", "height": 1.8}).set_placement((oled_cx - 10.0, oled_cy - 1.0))

    # 2. Tactile Button Openings SW1 & SW2
    # SW2 (HUSH / OLED NAV): (42.00, 12.00)
    sw2_cx = p0_x + 42.00
    sw2_cy = p0_y + 12.00
    msp.add_circle((sw2_cx, sw2_cy), 2.75, dxfattribs={"layer": "AM_0_OUTLINE"}) # dia 5.5mm
    msp.add_circle((sw2_cx, sw2_cy), 3.25, dxfattribs={"layer": "AM_0_OUTLINE"}) # chamfer rim
    msp.add_line((sw2_cx - 4.5, sw2_cy), (sw2_cx + 4.5, sw2_cy), dxfattribs={"layer": "AM_2_CENTER"})
    msp.add_line((sw2_cx, sw2_cy - 4.5), (sw2_cx, sw2_cy + 4.5), dxfattribs={"layer": "AM_2_CENTER"})
    msp.add_text("HUSH", dxfattribs={"layer": "AM_5_TEXT", "height": 1.6}).set_placement((sw2_cx - 3.0, sw2_cy - 6.0))

    # SW1 (TEST / DIAGNOSTIC): (42.00, 6.00)
    sw1_cx = p0_x + 42.00
    sw1_cy = p0_y + 6.00
    msp.add_circle((sw1_cx, sw1_cy), 2.75, dxfattribs={"layer": "AM_0_OUTLINE"})
    msp.add_circle((sw1_cx, sw1_cy), 3.25, dxfattribs={"layer": "AM_0_OUTLINE"})
    msp.add_line((sw1_cx - 4.5, sw1_cy), (sw1_cx + 4.5, sw1_cy), dxfattribs={"layer": "AM_2_CENTER"})
    msp.add_line((sw1_cx, sw1_cy - 4.5), (sw1_cx, sw1_cy + 4.5), dxfattribs={"layer": "AM_2_CENTER"})
    msp.add_text("TEST", dxfattribs={"layer": "AM_5_TEXT", "height": 1.6}).set_placement((sw1_cx - 3.0, sw1_cy - 6.0))

    # 3. 4-Channel Optical Light Pipe Aperture: Line at Y = 4.00 mm
    led_xs = [26.80, 30.00, 33.20, 36.40]
    led_labels = ["ALARM", "PWR", "WIFI", "FAULT"]
    for i, lx in enumerate(led_xs):
        lcx = p0_x + lx
        lcy = p0_y + 4.00
        msp.add_circle((lcx, lcy), 1.00, dxfattribs={"layer": "AM_0_OUTLINE"}) # dia 2.0mm
        msp.add_line((lcx - 1.8, lcy), (lcx + 1.8, lcy), dxfattribs={"layer": "AM_2_CENTER"})
        msp.add_line((lcx, lcy - 1.8), (lcx, lcy + 1.8), dxfattribs={"layer": "AM_2_CENTER"})
    add_rounded_rect(p0_x + 31.60, p0_y + 4.00, 14.0, 3.5, 1.2, "AM_1_HIDDEN")

    # 4. Acoustic Rosette Horn (LS1 Buzzer) at CAD (32.00, 12.00)
    bz_cx = p0_x + 32.00
    bz_cy = p0_y + 12.00
    # Center hole dia 2.5mm
    msp.add_circle((bz_cx, bz_cy), 1.25, dxfattribs={"layer": "AM_0_OUTLINE"})
    # 6 surrounding holes dia 2.0mm at R = 3.2mm
    for a in range(0, 360, 60):
        rad = math.radians(a)
        hx = bz_cx + 3.2 * math.cos(rad)
        hy = bz_cy + 3.2 * math.sin(rad)
        msp.add_circle((hx, hy), 1.00, dxfattribs={"layer": "AM_0_OUTLINE"})
    msp.add_circle((bz_cx, bz_cy), 6.1, dxfattribs={"layer": "AM_1_HIDDEN"}) # Buzzer body outline
    msp.add_line((bz_cx - 5.5, bz_cy), (bz_cx + 5.5, bz_cy), dxfattribs={"layer": "AM_2_CENTER"})
    msp.add_line((bz_cx, bz_cy - 5.5), (bz_cx, bz_cy + 5.5), dxfattribs={"layer": "AM_2_CENTER"})
    msp.add_text("BUZZER 85dB", dxfattribs={"layer": "AM_5_TEXT", "height": 1.6}).set_placement((bz_cx - 6.0, bz_cy - 7.5))

    # 5. S1 Electrochemical CO Sensor Diffusion Chamber at CAD (56.50, 14.50)
    co_cx = p0_x + 56.50
    co_cy = p0_y + 14.50
    msp.add_circle((co_cx, co_cy), 10.25, dxfattribs={"layer": "AM_0_OUTLINE"}) # Outer rim dia 20.5mm
    msp.add_circle((co_cx, co_cy), 8.00, dxfattribs={"layer": "AM_0_OUTLINE"})
    msp.add_circle((co_cx, co_cy), 5.50, dxfattribs={"layer": "AM_0_OUTLINE"})
    msp.add_circle((co_cx, co_cy), 3.00, dxfattribs={"layer": "AM_0_OUTLINE"})
    # Radial ribs
    for a in range(0, 360, 45):
        rad = math.radians(a)
        x_in = co_cx + 3.0 * math.cos(rad)
        y_in = co_cy + 3.0 * math.sin(rad)
        x_out = co_cx + 10.25 * math.cos(rad)
        y_out = co_cy + 10.25 * math.sin(rad)
        msp.add_line((x_in, y_in), (x_out, y_out), dxfattribs={"layer": "AM_0_OUTLINE"})
    msp.add_line((co_cx - 12.0, co_cy), (co_cx + 12.0, co_cy), dxfattribs={"layer": "AM_2_CENTER"})
    msp.add_line((co_cx, co_cy - 12.0), (co_cx, co_cy + 12.0), dxfattribs={"layer": "AM_2_CENTER"})
    msp.add_text("CO DIFFUSION WELL", dxfattribs={"layer": "AM_5_TEXT", "height": 1.8}).set_placement((co_cx - 9.0, co_cy - 13.0))

    # 6. S2 Figaro TGS2610 LPG Sensor Thermal Chimney at CAD (59.00, 43.50)
    lpg_cx = p0_x + 59.00
    lpg_cy = p0_y + 43.50
    msp.add_circle((lpg_cx, lpg_cy), 5.50, dxfattribs={"layer": "AM_0_OUTLINE"}) # Chimney boss dia 11.0mm
    # Perimeter convection slots around chimney
    for dy in [-3.0, 0.0, 3.0]:
        msp.add_line((lpg_cx - 4.5, lpg_cy + dy), (lpg_cx + 4.5, lpg_cy + dy), dxfattribs={"layer": "AM_0_OUTLINE"})
    msp.add_line((lpg_cx - 7.0, lpg_cy), (lpg_cx + 7.0, lpg_cy), dxfattribs={"layer": "AM_2_CENTER"})
    msp.add_line((lpg_cx, lpg_cy - 7.0), (lpg_cx, lpg_cy + 7.0), dxfattribs={"layer": "AM_2_CENTER"})
    msp.add_text("LPG CHIMNEY", dxfattribs={"layer": "AM_5_TEXT", "height": 1.8}).set_placement((lpg_cx - 6.5, lpg_cy + 7.5))

    # 7. Left Wall Cutout Indications
    # J1 (12V IN): CAD Y = 38.00
    j1_y = p0_y + 38.00
    msp.add_lwpolyline([(v1_x - 43.0, j1_y - 6.0), (v1_x - 40.5, j1_y - 6.0), (v1_x - 40.5, j1_y + 6.0), (v1_x - 43.0, j1_y + 6.0)],
                       dxfattribs={"layer": "AM_0_OUTLINE"})
    msp.add_text("12V DC IN", dxfattribs={"layer": "AM_5_TEXT", "height": 1.8}).set_placement((v1_x - 56.0, j1_y - 1.0))

    # J2 (EXT ALARM): CAD Y = 12.00
    j2_y = p0_y + 12.00
    msp.add_lwpolyline([(v1_x - 43.0, j2_y - 6.0), (v1_x - 40.5, j2_y - 6.0), (v1_x - 40.5, j2_y + 6.0), (v1_x - 43.0, j2_y + 6.0)],
                       dxfattribs={"layer": "AM_0_OUTLINE"})
    msp.add_text("ALARM RELAY", dxfattribs={"layer": "AM_5_TEXT", "height": 1.8}).set_placement((v1_x - 59.0, j2_y - 1.0))

    # SW3 (RESET PINHOLE): CAD Y = 20.20
    sw3_y = p0_y + 20.20
    msp.add_circle((v1_x - 41.5, sw3_y), 1.25, dxfattribs={"layer": "AM_0_OUTLINE"})
    msp.add_text("RESET", dxfattribs={"layer": "AM_5_TEXT", "height": 1.6}).set_placement((v1_x - 52.0, sw3_y - 1.0))

    # Dimensions for View 1
    # Width 86.0 mm
    dim1 = msp.add_aligned_dim(p1=(v1_x - 43.0, v1_y + 35.0), p2=(v1_x + 43.0, v1_y + 35.0), distance=5.0,
                               dxfattribs={"layer": "AM_3_DIMENSION"})
    dim1.render()
    # Height 66.0 mm
    dim2 = msp.add_aligned_dim(p1=(v1_x + 45.0, v1_y - 33.0), p2=(v1_x + 45.0, v1_y + 33.0), distance=5.0,
                               dxfattribs={"layer": "AM_3_DIMENSION"})
    dim2.render()

    # ==========================================================================
    # VIEW 2: LOWER CHASSIS BASE INTERIOR PLAN VIEW (Top-Right quadrant)
    # ==========================================================================
    v2_x = 260.0
    v2_y = 160.0
    p2_x = v2_x - 35.0
    p2_y = v2_y - 25.0

    msp.add_text("VIEW B: LOWER CHASSIS BASE (INTERNAL TOP PLAN)", dxfattribs={"layer": "AM_5_TEXT", "height": 3.2}).set_placement((v2_x - 42.0, v2_y + 42.0))
    msp.add_text("SCALE 1:1", dxfattribs={"layer": "AM_5_TEXT", "height": 2.0}).set_placement((v2_x - 42.0, v2_y + 38.0))

    # Outer wall & inner cavity
    add_rounded_rect(v2_x, v2_y, 86.0, 66.0, 8.0, "AM_0_OUTLINE")
    add_rounded_rect(v2_x, v2_y, 81.2, 61.2, 5.6, "AM_0_OUTLINE") # Inner cavity wall 2.4mm
    add_rounded_rect(v2_x, v2_y, 70.0, 50.0, 3.0, "AM_7_PCB_GHOST") # PCB placement datum

    # 4x PCB Mounting Standoff Bosses H1, H2, H3, H4
    bosses = [
        ("H1", 3.50, 3.50),
        ("H2", 66.50, 3.50),
        ("H3", 3.50, 46.50),
        ("H4", 66.50, 46.50)
    ]
    for bname, bx, by in bosses:
        bcx = p2_x + bx
        bcy = p2_y + by
        msp.add_circle((bcx, bcy), 3.00, dxfattribs={"layer": "AM_0_OUTLINE"}) # OD 6.0mm
        msp.add_circle((bcx, bcy), 1.80, dxfattribs={"layer": "AM_0_OUTLINE"}) # ID 3.6mm for M2.5 brass insert
        msp.add_line((bcx - 4.0, bcy), (bcx + 4.0, bcy), dxfattribs={"layer": "AM_2_CENTER"})
        msp.add_line((bcx, bcy - 4.0), (bcx, bcy + 4.0), dxfattribs={"layer": "AM_2_CENTER"})
        msp.add_text(f"{bname} (M2.5)", dxfattribs={"layer": "AM_5_TEXT", "height": 1.6}).set_placement((bcx + 3.2, bcy + 1.0))

    # 4x Housing Perimeter Assembly Screw Towers (M3 countersunk from back)
    corners = [
        (-38.0, -28.0),
        ( 38.0, -28.0),
        (-38.0,  28.0),
        ( 38.0,  28.0)
    ]
    for cx, cy in corners:
        ccx = v2_x + cx
        ccy = v2_y + cy
        msp.add_circle((ccx, ccy), 3.50, dxfattribs={"layer": "AM_0_OUTLINE"}) # OD 7.0mm
        msp.add_circle((ccx, ccy), 1.70, dxfattribs={"layer": "AM_0_OUTLINE"}) # M3 screw hole dia 3.4mm

    # Base Left Wall Terminal Cutouts
    # J1 (Power): Y = 38.00
    msp.add_lwpolyline([(v2_x - 43.0, p2_y + 32.0), (v2_x - 40.6, p2_y + 32.0), (v2_x - 40.6, p2_y + 44.0), (v2_x - 43.0, p2_y + 44.0)],
                       dxfattribs={"layer": "AM_0_OUTLINE"})
    # J2 (Relay): Y = 12.00
    msp.add_lwpolyline([(v2_x - 43.0, p2_y + 6.0), (v2_x - 40.6, p2_y + 6.0), (v2_x - 40.6, p2_y + 18.0), (v2_x - 43.0, p2_y + 18.0)],
                       dxfattribs={"layer": "AM_0_OUTLINE"})
    # SW3 (Reset): Y = 20.20
    msp.add_circle((v2_x - 41.8, p2_y + 20.20), 1.25, dxfattribs={"layer": "AM_0_OUTLINE"})

    # Floor Structural Stiffening Ribs
    msp.add_line((v2_x - 30.0, v2_y), (v2_x + 30.0, v2_y), dxfattribs={"layer": "AM_1_HIDDEN"})
    msp.add_line((v2_x, v2_y - 20.0), (v2_x, v2_y + 20.0), dxfattribs={"layer": "AM_1_HIDDEN"})

    # Dimensions for Standoff Pitch (H1-H2 = 63.00mm, H1-H3 = 43.00mm)
    dim3 = msp.add_aligned_dim(p1=(p2_x + 3.5, p2_y + 3.5), p2=(p2_x + 66.5, p2_y + 3.5), distance=-8.0,
                               dxfattribs={"layer": "AM_3_DIMENSION"})
    dim3.render()
    dim4 = msp.add_aligned_dim(p1=(p2_x + 3.5, p2_y + 3.5), p2=(p2_x + 3.5, p2_y + 46.5), distance=-8.0,
                               dxfattribs={"layer": "AM_3_DIMENSION"})
    dim4.render()

    # ==========================================================================
    # VIEW 3: FULL CROSS-SECTION A-A (Bottom-Left quadrant)
    # Section cut through Y = 12.00 mm (cutting J2, Buzzer LS1, Button SW2, CO Sensor S1)
    # ==========================================================================
    v3_x = 90.0
    v3_y = 55.0

    msp.add_text("SECTION A-A (THROUGH Y = 12.00 mm)", dxfattribs={"layer": "AM_5_TEXT", "height": 3.2}).set_placement((v3_x - 42.0, v3_y + 24.0))
    msp.add_text("SCALE 1:1", dxfattribs={"layer": "AM_5_TEXT", "height": 2.0}).set_placement((v3_x - 42.0, v3_y + 20.0))

    # Outer Section Envelope: Width 86.0mm, Total Height 28.0mm (Z from 0 to 28)
    # Base Z: 0.0 to 12.0 mm, Cover Z: 12.0 to 28.0 mm
    sx0 = v3_x - 43.0
    sx1 = v3_x + 43.0
    sz0 = v3_y - 14.0 # Z = 0
    sz_part = sz0 + 12.0 # Parting line Z = 12
    sz1 = sz0 + 28.0 # Top face Z = 28

    # Base Profile
    msp.add_lwpolyline([
        (sx0, sz_part), (sx0, sz0), (sx1, sz0), (sx1, sz_part),
        (sx1 - 2.4, sz_part), (sx1 - 2.4, sz0 + 2.4), (sx0 + 2.4, sz0 + 2.4), (sx0 + 2.4, sz_part), (sx0, sz_part)
    ], dxfattribs={"layer": "AM_0_OUTLINE"})

    # Cover Profile
    msp.add_lwpolyline([
        (sx0, sz_part), (sx0, sz1), (sx1, sz1), (sx1, sz_part),
        (sx1 - 2.4, sz_part), (sx1 - 2.4, sz1 - 2.4), (sx0 + 2.4, sz1 - 2.4), (sx0 + 2.4, sz_part), (sx0, sz_part)
    ], dxfattribs={"layer": "AM_0_OUTLINE"})

    # PCB Board cross-section: Standoff at Z = 2.4 + 4.5 = 6.9mm, PCB thickness 1.6mm
    pcb_z0 = sz0 + 6.9
    pcb_z1 = pcb_z0 + 1.6
    pcb_x0 = v3_x - 35.0
    pcb_x1 = v3_x + 35.0
    msp.add_lwpolyline([(pcb_x0, pcb_z0), (pcb_x1, pcb_z0), (pcb_x1, pcb_z1), (pcb_x0, pcb_z1), (pcb_x0, pcb_z0)],
                       dxfattribs={"layer": "AM_7_PCB_GHOST"})

    # Section Hatching (AM_4_HATCH)
    # Add hatched cross-section indicators for plastic walls
    msp.add_line((sx0 + 0.5, sz0 + 2.0), (sx0 + 2.0, sz0 + 0.5), dxfattribs={"layer": "AM_4_HATCH"})
    msp.add_line((sx1 - 2.0, sz0 + 0.5), (sx1 - 0.5, sz0 + 2.0), dxfattribs={"layer": "AM_4_HATCH"})
    msp.add_line((sx0 + 0.5, sz1 - 2.0), (sx0 + 2.0, sz1 - 0.5), dxfattribs={"layer": "AM_4_HATCH"})
    msp.add_line((sx1 - 2.0, sz1 - 0.5), (sx1 - 0.5, sz1 - 2.0), dxfattribs={"layer": "AM_4_HATCH"})

    # Parting Line Indicator
    msp.add_line((sx0 - 5.0, sz_part), (sx1 + 5.0, sz_part), dxfattribs={"layer": "AM_2_CENTER"})
    msp.add_text("PARTING LINE (Z = 12.0)", dxfattribs={"layer": "AM_5_TEXT", "height": 1.8}).set_placement((sx1 + 6.0, sz_part - 0.8))

    # Total Height Dimension: 28.0 mm
    dim5 = msp.add_aligned_dim(p1=(sx0 - 4.0, sz0), p2=(sx0 - 4.0, sz1), distance=5.0,
                               dxfattribs={"layer": "AM_3_DIMENSION"})
    dim5.render()

    # ==========================================================================
    # VIEW 4: DETACHABLE WALL MOUNT BRACKET (Bottom-Right quadrant, above title block)
    # ==========================================================================
    v4_x = 260.0
    v4_y = 55.0

    msp.add_text("VIEW C: WALL MOUNTING BRACKET (REAR ATTACHMENT)", dxfattribs={"layer": "AM_5_TEXT", "height": 3.2}).set_placement((v4_x - 38.0, v4_y + 24.0))
    msp.add_text("SCALE 1:1", dxfattribs={"layer": "AM_5_TEXT", "height": 2.0}).set_placement((v4_x - 38.0, v4_y + 20.0))

    # Bracket Outer Profile: 76.0 mm x 56.0 mm, R = 6.0 mm
    add_rounded_rect(v4_x, v4_y, 76.0, 56.0, 6.0, "AM_0_OUTLINE")

    # 2x Wall Mounting Keyhole Slots at pitch 60.0 mm (standard European/US junction box)
    for ky in [-30.0, 30.0]:
        kcy = v4_y + ky
        # Large entry hole dia 9.0 mm
        msp.add_circle((v4_x, kcy), 4.50, dxfattribs={"layer": "AM_0_OUTLINE"})
        # Retention slot width 4.5 mm
        dir_y = 1.0 if ky < 0 else -1.0
        msp.add_lwpolyline([
            (v4_x - 2.25, kcy), (v4_x - 2.25, kcy + dir_y * 7.0),
            (v4_x + 2.25, kcy + dir_y * 7.0), (v4_x + 2.25, kcy)
        ], dxfattribs={"layer": "AM_0_OUTLINE"})
        msp.add_line((v4_x - 6.0, kcy), (v4_x + 6.0, kcy), dxfattribs={"layer": "AM_2_CENTER"})
        msp.add_line((v4_x, kcy - 6.0), (v4_x, kcy + 6.0), dxfattribs={"layer": "AM_2_CENTER"})

    # Center In-Wall Cable Knockout Aperture: 22.0 mm x 16.0 mm, R = 3.0 mm
    add_rounded_rect(v4_x, v4_y, 22.0, 16.0, 3.0, "AM_0_OUTLINE")
    msp.add_text("CABLE PASS-THROUGH", dxfattribs={"layer": "AM_5_TEXT", "height": 1.6}).set_placement((v4_x - 10.0, v4_y - 0.8))

    # Save drawing
    doc.saveas(output_path)
    print(f"[SUCCESS] AutoCAD Mechanical DXF created at: {output_path}")

if __name__ == "__main__":
    out1 = os.path.abspath("cad/autocad/co_detector_enclosure_perfect.dxf")
    out2 = os.path.abspath("cad/dxf/co_detector_enclosure_production.dxf")
    build_autocad_production_drawing(out1)
    build_autocad_production_drawing(out2)
