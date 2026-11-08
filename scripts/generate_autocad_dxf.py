"""
Master AutoCAD Mechanical Production Drawing Generator - Rev 4.0
Generates:
  1. cad/autocad/co_detector_enclosure_perfect.dxf (Complete ISO A3 Production Blueprint)
  2. cad/dxf/co_detector_enclosure_production.dxf (1:1 Clean Machining Profiles)

Standards: ISO 7200 Title Block, ISO 2768-mK Tolerances, First Angle Projection.
Datum: PCB Bottom-Left Corner = (0.00, 0.00).
Enclosure Outer Dimensions: 86.00 mm x 66.00 mm x 28.00 mm (R = 8.00 mm).
Rev 4.0 Architecture: Figaro TGS2610-C00 LPG Gas Detector with 1100mAh Li-ion Battery Backup & Smart Power-Path.
"""

import math
import os
import ezdxf
from ezdxf import colors, units
from ezdxf.enums import TextEntityAlignment


def build_autocad_production_drawing(output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
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
    bx0, by0 = 25.0, 10.0
    bx1, by1 = 410.0, 287.0
    msp.add_lwpolyline([(bx0, by0), (bx1, by0), (bx1, by1), (bx0, by1), (bx0, by0)],
                       dxfattribs={"layer": "AM_6_BORDER"})
    msp.add_lwpolyline([(0, 0), (420, 0), (420, 297), (0, 297), (0, 0)],
                       dxfattribs={"layer": "AM_6_BORDER", "color": colors.GRAY})

    # Title Block (ISO 7200 Standard: 180mm x 55mm at bottom-right)
    tx0 = bx1 - 180.0
    ty0 = by0
    tx1 = bx1
    ty1 = by0 + 55.0
    msp.add_lwpolyline([(tx0, ty0), (tx1, ty0), (tx1, ty1), (tx0, ty1), (tx0, ty0)],
                       dxfattribs={"layer": "AM_6_BORDER"})
    msp.add_line((tx0, ty0 + 15.0), (tx1, ty0 + 15.0), dxfattribs={"layer": "AM_6_BORDER"})
    msp.add_line((tx0, ty0 + 30.0), (tx1, ty0 + 30.0), dxfattribs={"layer": "AM_6_BORDER"})
    msp.add_line((tx0, ty0 + 42.0), (tx1, ty0 + 42.0), dxfattribs={"layer": "AM_6_BORDER"})
    msp.add_line((tx0 + 60.0, ty0), (tx0 + 60.0, ty0 + 30.0), dxfattribs={"layer": "AM_6_BORDER"})
    msp.add_line((tx0 + 120.0, ty0), (tx0 + 120.0, ty0 + 30.0), dxfattribs={"layer": "AM_6_BORDER"})

    # Title Block Texts
    msp.add_text("PROJECT:", dxfattribs={"layer": "AM_5_TEXT", "height": 2.2}).set_placement((tx0 + 3.0, ty1 - 5.0))
    msp.add_text("SMART LPG GAS DETECTOR & BATTERY CONTROLLER", dxfattribs={"layer": "AM_5_TEXT", "height": 3.6, "style": "Standard"}).set_placement((tx0 + 3.0, ty1 - 10.5))

    msp.add_text("TITLE:", dxfattribs={"layer": "AM_5_TEXT", "height": 2.2}).set_placement((tx0 + 3.0, ty0 + 38.0))
    msp.add_text("PRODUCTION MECHANICAL ENCLOSURE ASSEMBLY", dxfattribs={"layer": "AM_5_TEXT", "height": 3.2}).set_placement((tx0 + 3.0, ty0 + 33.5))

    msp.add_text("DRAWING NO:", dxfattribs={"layer": "AM_5_TEXT", "height": 2.2}).set_placement((tx0 + 3.0, ty0 + 26.0))
    msp.add_text("AGY-LPG-ENC-401", dxfattribs={"layer": "AM_5_TEXT", "height": 4.0}).set_placement((tx0 + 3.0, ty0 + 18.0))

    msp.add_text("REVISION:", dxfattribs={"layer": "AM_5_TEXT", "height": 2.2}).set_placement((tx0 + 63.0, ty0 + 26.0))
    msp.add_text("REV 4.0 (BATTERY BACKUP REDESIGN)", dxfattribs={"layer": "AM_5_TEXT", "height": 3.0}).set_placement((tx0 + 63.0, ty0 + 18.0))

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
        "ENGINEERING & MANUFACTURING SPECIFICATIONS (REV 4.0):",
        "1. ALL DIMENSIONS ARE IN MILLIMETERS [mm]. DATUM (0,0) COINCIDES WITH PCBA LOWER-LEFT CORNER.",
        "2. UNIFORM WALL THICKNESS t = 2.40mm. DRAFT ANGLE 1.5 DEG ON INJECTION CORE & CAVITY FACES.",
        "3. PCBA SECURED VIA 4x M2.5x6mm PAN HEAD SCREWS INTO RUTHEX M2.5 BRASS HEAT-SET INSERTS (H1..H4).",
        "4. INTERNAL INTEGRATED LOWER BATTERY RETENTION POCKET (52 x 36 x 7.5mm) ACCOMMODATES 1100mAh LiPo PACK.",
        "5. 0.96-INCH I2C OLED APERTURE (25 x 14mm) ALIGNED AT X=42.0, Y=25.0 WITH 1.0mm RETENTION PMMA BEZEL.",
        "6. THERMAL CONVECTION: TOP-VENTED CHIMNEY DIRECTLY HOUSES FIGARO TGS2610-C00 LPG GAS SENSOR.",
        "7. 7-HOLE ACOUSTIC ROSETTE DIRECTLY TUNED TO TDK PS1240 RESONANCE FREQUENCY (85dB SPL @ 3m) AT X=60.0, Y=16.0.",
        "8. COMPLIANCE STANDARDS: EN 50194-1 (COMBUSTIBLE GAS ALARM), UL 2075, CE-RED, ROHS 3 & REACH."
    ]
    ny = by1 - 8.0
    for i, line in enumerate(notes):
        h = 2.8 if i == 0 else 2.1
        msp.add_text(line, dxfattribs={"layer": "AM_5_TEXT", "height": h}).set_placement((bx0 + 5.0, ny - i * 4.2))

    # Helper function for rounded rectangle
    def add_rounded_rect(cx, cy, w, h, r, layer):
        x0 = cx - w / 2.0
        y0 = cy - h / 2.0
        x1 = cx + w / 2.0
        y1 = cy + h / 2.0
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
    v1_x = 90.0
    v1_y = 160.0
    p0_x = v1_x - 35.0
    p0_y = v1_y - 25.0

    msp.add_text("VIEW A: FRONT COVER (EXTERIOR TOP PLAN)", dxfattribs={"layer": "AM_5_TEXT", "height": 3.2}).set_placement((v1_x - 42.0, v1_y + 42.0))
    msp.add_text("SCALE 1:1", dxfattribs={"layer": "AM_5_TEXT", "height": 2.0}).set_placement((v1_x - 42.0, v1_y + 38.0))

    # Enclosure Outer Profile: 86.0 x 66.0 mm, R = 8.0 mm
    add_rounded_rect(v1_x, v1_y, 86.0, 66.0, 8.0, "AM_0_OUTLINE")
    add_rounded_rect(v1_x, v1_y, 82.0, 62.0, 6.0, "AM_0_OUTLINE")

    # PCBA Ghost Outline (70 x 50 mm, R = 3.0 mm)
    add_rounded_rect(v1_x, v1_y, 70.0, 50.0, 3.0, "AM_7_PCB_GHOST")

    # 1. 0.96-inch OLED Display Bezel Window at CAD (42.00, 25.00)
    oled_cx = p0_x + 42.00
    oled_cy = p0_y + 25.00
    add_rounded_rect(oled_cx, oled_cy, 25.0, 14.0, 1.5, "AM_0_OUTLINE")
    add_rounded_rect(oled_cx, oled_cy, 21.7, 10.8, 0.5, "AM_1_HIDDEN")
    msp.add_line((oled_cx - 15.0, oled_cy), (oled_cx + 15.0, oled_cy), dxfattribs={"layer": "AM_2_CENTER"})
    msp.add_line((oled_cx, oled_cy - 10.0), (oled_cx, oled_cy + 10.0), dxfattribs={"layer": "AM_2_CENTER"})
    msp.add_text("0.96\" OLED (128x64)", dxfattribs={"layer": "AM_5_TEXT", "height": 1.8}).set_placement((oled_cx - 10.0, oled_cy - 1.0))

    # 2. Tactile Button Openings SW1 & SW2
    # SW2 (HUSH / OLED NAV): CAD (35.00, 13.00)
    sw2_cx = p0_x + 35.00
    sw2_cy = p0_y + 13.00
    msp.add_circle((sw2_cx, sw2_cy), 2.75, dxfattribs={"layer": "AM_0_OUTLINE"})
    msp.add_circle((sw2_cx, sw2_cy), 3.25, dxfattribs={"layer": "AM_0_OUTLINE"})
    msp.add_line((sw2_cx - 4.5, sw2_cy), (sw2_cx + 4.5, sw2_cy), dxfattribs={"layer": "AM_2_CENTER"})
    msp.add_line((sw2_cx, sw2_cy - 4.5), (sw2_cx, sw2_cy + 4.5), dxfattribs={"layer": "AM_2_CENTER"})
    msp.add_text("HUSH", dxfattribs={"layer": "AM_5_TEXT", "height": 1.6}).set_placement((sw2_cx - 3.0, sw2_cy - 6.0))

    # SW1 (TEST / DIAGNOSTIC): CAD (45.00, 13.00)
    sw1_cx = p0_x + 45.00
    sw1_cy = p0_y + 13.00
    msp.add_circle((sw1_cx, sw1_cy), 2.75, dxfattribs={"layer": "AM_0_OUTLINE"})
    msp.add_circle((sw1_cx, sw1_cy), 3.25, dxfattribs={"layer": "AM_0_OUTLINE"})
    msp.add_line((sw1_cx - 4.5, sw1_cy), (sw1_cx + 4.5, sw1_cy), dxfattribs={"layer": "AM_2_CENTER"})
    msp.add_line((sw1_cx, sw1_cy - 4.5), (sw1_cx, sw1_cy + 4.5), dxfattribs={"layer": "AM_2_CENTER"})
    msp.add_text("TEST", dxfattribs={"layer": "AM_5_TEXT", "height": 1.6}).set_placement((sw1_cx - 3.0, sw1_cy - 6.0))

    # 3. 4 Status LEDs at CAD Y = 4.00 mm
    led_configs = [
        ("PWR/CHRG", 28.00),
        ("LPG OK",   34.00),
        ("ALARM",    40.00),
        ("WIFI",     46.00)
    ]
    for lbl, lx in led_configs:
        lcx = p0_x + lx
        lcy = p0_y + 4.00
        msp.add_circle((lcx, lcy), 1.10, dxfattribs={"layer": "AM_0_OUTLINE"})
        msp.add_line((lcx - 1.8, lcy), (lcx + 1.8, lcy), dxfattribs={"layer": "AM_2_CENTER"})
        msp.add_line((lcx, lcy - 1.8), (lcx, lcy + 1.8), dxfattribs={"layer": "AM_2_CENTER"})
    add_rounded_rect(p0_x + 37.00, p0_y + 4.00, 24.0, 3.5, 1.2, "AM_1_HIDDEN")

    # 4. Acoustic Rosette Horn (LS1 Buzzer) at CAD (60.00, 16.00)
    bz_cx = p0_x + 60.00
    bz_cy = p0_y + 16.00
    msp.add_circle((bz_cx, bz_cy), 1.25, dxfattribs={"layer": "AM_0_OUTLINE"})
    for a in range(0, 360, 60):
        rad = math.radians(a)
        hx = bz_cx + 3.2 * math.cos(rad)
        hy = bz_cy + 3.2 * math.sin(rad)
        msp.add_circle((hx, hy), 0.90, dxfattribs={"layer": "AM_0_OUTLINE"})
    msp.add_circle((bz_cx, bz_cy), 6.1, dxfattribs={"layer": "AM_1_HIDDEN"})
    msp.add_line((bz_cx - 5.5, bz_cy), (bz_cx + 5.5, bz_cy), dxfattribs={"layer": "AM_2_CENTER"})
    msp.add_line((bz_cx, bz_cy - 5.5), (bz_cx, bz_cy + 5.5), dxfattribs={"layer": "AM_2_CENTER"})
    msp.add_text("BUZZER 85dB", dxfattribs={"layer": "AM_5_TEXT", "height": 1.6}).set_placement((bz_cx - 6.0, bz_cy - 7.5))

    # 5. S2 Figaro TGS2610-C00 LPG Sensor Thermal Chimney at CAD (60.00, 37.00)
    lpg_cx = p0_x + 60.00
    lpg_cy = p0_y + 37.00
    msp.add_circle((lpg_cx, lpg_cy), 5.50, dxfattribs={"layer": "AM_0_OUTLINE"})
    for dy in [-3.0, -1.0, 1.0, 3.0]:
        msp.add_line((lpg_cx - 4.5, lpg_cy + dy), (lpg_cx + 4.5, lpg_cy + dy), dxfattribs={"layer": "AM_0_OUTLINE"})
    msp.add_line((lpg_cx - 7.0, lpg_cy), (lpg_cx + 7.0, lpg_cy), dxfattribs={"layer": "AM_2_CENTER"})
    msp.add_line((lpg_cx, lpg_cy - 7.0), (lpg_cx, lpg_cy + 7.0), dxfattribs={"layer": "AM_2_CENTER"})
    msp.add_text("LPG CHIMNEY", dxfattribs={"layer": "AM_5_TEXT", "height": 1.8}).set_placement((lpg_cx - 6.5, lpg_cy + 7.5))

    # 6. Left Wall Cutouts: J1 (12V IN) & SW3 (RESET)
    j1_y = p0_y + 38.00
    msp.add_lwpolyline([(v1_x - 43.0, j1_y - 5.5), (v1_x - 40.5, j1_y - 5.5), (v1_x - 40.5, j1_y + 5.5), (v1_x - 43.0, j1_y + 5.5)],
                       dxfattribs={"layer": "AM_0_OUTLINE"})
    msp.add_text("12V DC IN", dxfattribs={"layer": "AM_5_TEXT", "height": 1.8}).set_placement((v1_x - 56.0, j1_y - 1.0))

    sw3_y = p0_y + 20.00
    msp.add_circle((v1_x - 41.5, sw3_y), 1.25, dxfattribs={"layer": "AM_0_OUTLINE"})
    msp.add_text("RESET", dxfattribs={"layer": "AM_5_TEXT", "height": 1.6}).set_placement((v1_x - 52.0, sw3_y - 1.0))

    # Dimensions for View 1
    dim1 = msp.add_aligned_dim(p1=(v1_x - 43.0, v1_y + 35.0), p2=(v1_x + 43.0, v1_y + 35.0), distance=5.0,
                               dxfattribs={"layer": "AM_3_DIMENSION"})
    dim1.render()
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
    add_rounded_rect(v2_x, v2_y, 81.2, 61.2, 5.6, "AM_0_OUTLINE")
    add_rounded_rect(v2_x, v2_y, 70.0, 50.0, 3.0, "AM_7_PCB_GHOST")

    # Internal Battery Pocket (52 x 36 x 7.5 mm) centered under PCB
    add_rounded_rect(v2_x, v2_y, 52.0, 36.0, 3.0, "AM_0_OUTLINE")
    msp.add_text("INTERNAL BATTERY POCKET (52x36x7.5mm for 1100mAh LiPo)", dxfattribs={"layer": "AM_5_TEXT", "height": 1.6}).set_placement((v2_x - 24.0, v2_y - 1.0))

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
        msp.add_circle((bcx, bcy), 3.00, dxfattribs={"layer": "AM_0_OUTLINE"})
        msp.add_circle((bcx, bcy), 1.80, dxfattribs={"layer": "AM_0_OUTLINE"})
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
        msp.add_circle((ccx, ccy), 3.50, dxfattribs={"layer": "AM_0_OUTLINE"})
        msp.add_circle((ccx, ccy), 1.70, dxfattribs={"layer": "AM_0_OUTLINE"})

    # Base Left Wall Terminal Cutout: J1 (Power) ONLY
    msp.add_lwpolyline([(v2_x - 43.0, p2_y + 32.5), (v2_x - 40.6, p2_y + 32.5), (v2_x - 40.6, p2_y + 43.5), (v2_x - 43.0, p2_y + 43.5)],
                       dxfattribs={"layer": "AM_0_OUTLINE"})
    # SW3 Reset hole
    msp.add_circle((v2_x - 41.8, p2_y + 20.00), 1.25, dxfattribs={"layer": "AM_0_OUTLINE"})

    # Dimensions for Standoff Pitch
    dim3 = msp.add_aligned_dim(p1=(p2_x + 3.5, p2_y + 3.5), p2=(p2_x + 66.5, p2_y + 3.5), distance=-8.0,
                               dxfattribs={"layer": "AM_3_DIMENSION"})
    dim3.render()
    dim4 = msp.add_aligned_dim(p1=(p2_x + 3.5, p2_y + 3.5), p2=(p2_x + 3.5, p2_y + 46.5), distance=-8.0,
                               dxfattribs={"layer": "AM_3_DIMENSION"})
    dim4.render()

    # ==========================================================================
    # VIEW 3: FULL CROSS-SECTION A-A (Bottom-Left quadrant)
    # Section cut through Y = 16.00 mm (cutting Battery Pocket, Buzzer LS1)
    # ==========================================================================
    v3_x = 90.0
    v3_y = 55.0

    msp.add_text("SECTION A-A (THROUGH Y = 16.00 mm)", dxfattribs={"layer": "AM_5_TEXT", "height": 3.2}).set_placement((v3_x - 42.0, v3_y + 24.0))
    msp.add_text("SCALE 1:1", dxfattribs={"layer": "AM_5_TEXT", "height": 2.0}).set_placement((v3_x - 42.0, v3_y + 20.0))

    sx0 = v3_x - 43.0
    sx1 = v3_x + 43.0
    sz0 = v3_y - 14.0
    sz_part = sz0 + 12.0
    sz1 = sz0 + 28.0

    # Base Profile
    msp.add_lwpolyline([
        (sx0, sz_part), (sx0, sz0), (sx1, sz0), (sx1, sz_part),
        (sx1 - 2.4, sz_part), (sx1 - 2.4, sz0 + 2.4), (sx0 + 2.4, sz0 + 2.4), (sx0 + 2.4, sz_part), (sx0, sz_part)
    ], dxfattribs={"layer": "AM_0_OUTLINE"})

    # Lower Battery Pocket in Base floor (52mm width, 7.5mm depth)
    bx_0 = v3_x - 26.0
    bx_1 = v3_x + 26.0
    bz_bot = sz0 + 2.4
    bz_top = sz0 + 9.5
    msp.add_lwpolyline([(bx_0, bz_top), (bx_1, bz_top), (bx_1, bz_bot), (bx_0, bz_bot), (bx_0, bz_top)],
                       dxfattribs={"layer": "AM_1_HIDDEN"})
    msp.add_text("1100mAh LiPo PACK (6.5mm thick)", dxfattribs={"layer": "AM_5_TEXT", "height": 1.6}).set_placement((v3_x - 18.0, bz_bot + 2.5))

    # Cover Profile
    msp.add_lwpolyline([
        (sx0, sz_part), (sx0, sz1), (sx1, sz1), (sx1, sz_part),
        (sx1 - 2.4, sz_part), (sx1 - 2.4, sz1 - 2.4), (sx0 + 2.4, sz1 - 2.4), (sx0 + 2.4, sz_part), (sx0, sz_part)
    ], dxfattribs={"layer": "AM_0_OUTLINE"})

    # PCB Board cross-section: Standoff at Z = 10.0mm, PCB thickness 1.6mm
    pcb_z0 = sz0 + 10.0
    pcb_z1 = pcb_z0 + 1.6
    pcb_x0 = v3_x - 35.0
    pcb_x1 = v3_x + 35.0
    msp.add_lwpolyline([(pcb_x0, pcb_z0), (pcb_x1, pcb_z0), (pcb_x1, pcb_z1), (pcb_x0, pcb_z1), (pcb_x0, pcb_z0)],
                       dxfattribs={"layer": "AM_7_PCB_GHOST"})
    msp.add_text("PCBA 4-LAYER (1.6mm)", dxfattribs={"layer": "AM_5_TEXT", "height": 1.6}).set_placement((pcb_x0 + 4.0, pcb_z0 + 3.0))

    # Parting Line Indicator
    msp.add_line((sx0 - 5.0, sz_part), (sx1 + 5.0, sz_part), dxfattribs={"layer": "AM_2_CENTER"})
    msp.add_text("PARTING LINE (Z = 12.0)", dxfattribs={"layer": "AM_5_TEXT", "height": 1.8}).set_placement((sx1 + 6.0, sz_part - 0.8))

    # Total Height Dimension: 28.0 mm
    dim5 = msp.add_aligned_dim(p1=(sx0 - 4.0, sz0), p2=(sx0 - 4.0, sz1), distance=5.0,
                               dxfattribs={"layer": "AM_3_DIMENSION"})
    dim5.render()

    # ==========================================================================
    # VIEW 4: DETACHABLE WALL MOUNT BRACKET (Bottom-Right quadrant)
    # ==========================================================================
    v4_x = 260.0
    v4_y = 55.0

    msp.add_text("VIEW C: WALL MOUNTING BRACKET (REAR ATTACHMENT)", dxfattribs={"layer": "AM_5_TEXT", "height": 3.2}).set_placement((v4_x - 38.0, v4_y + 24.0))
    msp.add_text("SCALE 1:1", dxfattribs={"layer": "AM_5_TEXT", "height": 2.0}).set_placement((v4_x - 38.0, v4_y + 20.0))

    # Bracket Outer Profile: 76.0 mm x 56.0 mm, R = 6.0 mm
    add_rounded_rect(v4_x, v4_y, 76.0, 56.0, 6.0, "AM_0_OUTLINE")

    # 2x Wall Mounting Keyhole Slots at pitch 60.0 mm
    for ky in [-30.0, 30.0]:
        kcy = v4_y + ky
        msp.add_circle((v4_x, kcy), 4.50, dxfattribs={"layer": "AM_0_OUTLINE"})
        dir_y = 1.0 if ky < 0 else -1.0
        msp.add_lwpolyline([
            (v4_x - 2.25, kcy), (v4_x - 2.25, kcy + dir_y * 7.0),
            (v4_x + 2.25, kcy + dir_y * 7.0), (v4_x + 2.25, kcy)
        ], dxfattribs={"layer": "AM_0_OUTLINE"})
        msp.add_line((v4_x - 6.0, kcy), (v4_x + 6.0, kcy), dxfattribs={"layer": "AM_2_CENTER"})
        msp.add_line((v4_x, kcy - 6.0), (v4_x, kcy + 6.0), dxfattribs={"layer": "AM_2_CENTER"})

    # Center In-Wall Cable Knockout Aperture
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
