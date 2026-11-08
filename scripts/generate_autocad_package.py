"""
AutoCAD Mechanical Production Drawing Package Generator
Generates:
  1. cad/autocad/co_detector_enclosure_drawing.dxf  (Master Assembly - ISO A3)
  2. cad/autocad/detail_front_cover.dxf             (Sheet 2: Front Bezel - ISO A4)
  3. cad/autocad/detail_rear_chassis.dxf            (Sheet 3: Rear Chassis - ISO A4)
  4. cad/autocad/detail_wall_bracket.dxf            (Sheet 4: Wall Bracket - ISO A4)
  5. cad/autocad/MECHANICAL_BOM.csv                 (Mechanical Fastener & Hardware BOM)
  6. cad/autocad/build_enclosure_drawing.lsp        (AutoLISP Automation Suite)
  7. cad/autocad/import_3d_enclosure.scr            (AutoCAD 3D STEP Import Script)
"""

import math
import os

class AutoCADDrawing:
    def __init__(self, filename):
        self.filename = filename
        self.entities = []

    def line(self, x1, y1, x2, y2, layer="AM_0"):
        self.entities.append(f"0\nLINE\n8\n{layer}\n10\n{x1:.4f}\n20\n{y1:.4f}\n30\n0.0\n11\n{x2:.4f}\n21\n{y2:.4f}\n31\n0.0")

    def circle(self, cx, cy, r, layer="AM_0"):
        self.entities.append(f"0\nCIRCLE\n8\n{layer}\n10\n{cx:.4f}\n20\n{cy:.4f}\n30\n0.0\n40\n{r:.4f}")

    def arc(self, cx, cy, r, start_ang, end_ang, layer="AM_0"):
        self.entities.append(f"0\nARC\n8\n{layer}\n10\n{cx:.4f}\n20\n{cy:.4f}\n30\n0.0\n40\n{r:.4f}\n50\n{start_ang:.4f}\n51\n{end_ang:.4f}")

    def rect(self, x1, y1, x2, y2, layer="AM_0"):
        self.line(x1, y1, x2, y1, layer)
        self.line(x2, y1, x2, y2, layer)
        self.line(x2, y2, x1, y2, layer)
        self.line(x1, y2, x1, y1, layer)

    def rounded_rect(self, cx, cy, w, h, r, layer="AM_0"):
        x1 = cx - w/2 + r
        x2 = cx + w/2 - r
        y1 = cy - h/2 + r
        y2 = cy + h/2 - r
        self.line(x1, cy - h/2, x2, cy - h/2, layer)
        self.line(cx + w/2, y1, cx + w/2, y2, layer)
        self.line(x2, cy + h/2, x1, cy + h/2, layer)
        self.line(cx - w/2, y2, cx - w/2, y1, layer)
        self.arc(x2, y1, r, 270, 360, layer)
        self.arc(x2, y2, r, 0, 90, layer)
        self.arc(x1, y2, r, 90, 180, layer)
        self.arc(x1, y1, r, 180, 270, layer)

    def centerline(self, cx, cy, length, orientation="cross", layer="AM_2"):
        hl = length / 2
        if orientation in ["cross", "both"]:
            self.line(cx - hl, cy, cx + hl, cy, layer)
            self.line(cx, cy - hl, cx, cy + hl, layer)
        elif orientation == "horiz":
            self.line(cx - hl, cy, cx + hl, cy, layer)
        elif orientation == "vert":
            self.line(cx, cy - hl, cx, cy + hl, layer)

    def text(self, x, y, height, text_str, layer="AM_5", angle=0):
        self.entities.append(f"0\nTEXT\n8\n{layer}\n10\n{x:.4f}\n20\n{y:.4f}\n30\n0.0\n40\n{height:.4f}\n1\n{text_str}\n50\n{angle:.2f}")

    def dimension_horiz(self, x1, x2, y, text_override="", layer="AM_3"):
        self.line(x1, y - 2, x1, y + 2, layer)
        self.line(x2, y - 2, x2, y + 2, layer)
        self.line(x1, y, x2, y, layer)
        self.line(x1, y, x1 + 1.5, y + 0.6, layer)
        self.line(x1, y, x1 + 1.5, y - 0.6, layer)
        self.line(x2, y, x2 - 1.5, y + 0.6, layer)
        self.line(x2, y, x2 - 1.5, y - 0.6, layer)
        val = text_override if text_override else f"{abs(x2 - x1):.1f}"
        self.text((x1 + x2)/2 - len(val)*1.0, y + 1.2, 2.5, val, layer)

    def dimension_vert(self, y1, y2, x, text_override="", layer="AM_3"):
        self.line(x - 2, y1, x + 2, y1, layer)
        self.line(x - 2, y2, x + 2, y2, layer)
        self.line(x, y1, x, y2, layer)
        self.line(x, y1, x + 0.6, y1 + 1.5, layer)
        self.line(x, y1, x - 0.6, y1 + 1.5, layer)
        self.line(x, y2, x + 0.6, y2 - 1.5, layer)
        self.line(x, y2, x - 0.6, y2 - 1.5, layer)
        val = text_override if text_override else f"{abs(y2 - y1):.1f}"
        self.text(x + 1.2, (y1 + y2)/2 - 1.2, 2.5, val, layer)

    def save(self):
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        layers = [
            ("0", 7, "CONTINUOUS"),
            ("AM_0", 7, "CONTINUOUS"),      # Visible contours
            ("AM_1", 2, "HIDDEN2"),         # Hidden lines
            ("AM_2", 1, "CENTER2"),         # Centerlines
            ("AM_3", 3, "CONTINUOUS"),      # Dimensions
            ("AM_4", 4, "CONTINUOUS"),      # Hatches
            ("AM_5", 6, "CONTINUOUS"),      # Text/Notes
            ("AM_BORDER", 5, "CONTINUOUS")  # Frame/Title block
        ]
        with open(self.filename, 'w', encoding='ascii') as f:
            f.write("0\nSECTION\n2\nHEADER\n9\n$ACADVER\n1\nAC1021\n9\n$INSUNITS\n70\n4\n0\nENDSEC\n")
            f.write("0\nSECTION\n2\nTABLES\n0\nTABLE\n2\nLTYPE\n")
            f.write("0\nLTYPE\n2\nCONTINUOUS\n70\n0\n3\nSolid line\n72\n65\n73\n0\n40\n0.0\n")
            f.write("0\nLTYPE\n2\nHIDDEN2\n70\n0\n3\nHidden line\n72\n65\n73\n2\n40\n4.0\n49\n2.5\n49\n-1.5\n")
            f.write("0\nLTYPE\n2\nCENTER2\n70\n0\n3\nCenter line\n72\n65\n73\n4\n40\n8.0\n49\n5.0\n49\n-1.0\n49\n1.0\n49\n-1.0\n")
            f.write("0\nENDTAB\n")
            f.write("0\nTABLE\n2\nLAYER\n")
            for lname, color, ltype in layers:
                f.write(f"0\nLAYER\n2\n{lname}\n70\n0\n62\n{color}\n6\n{ltype}\n")
            f.write("0\nENDTAB\n0\nENDSEC\n")
            f.write("0\nSECTION\n2\nENTITIES\n")
            for ent in self.entities:
                f.write(ent + "\n")
            f.write("0\nENDSEC\n0\nEOF\n")
        print(f"Generated AutoCAD Drawing: {self.filename}")


# ==============================================================================
# SHEET 1: MASTER ENCLOSURE ASSEMBLY (ISO A3 - 420x297mm)
# ==============================================================================
def build_master_drawing():
    cad = AutoCADDrawing("cad/autocad/co_detector_enclosure_drawing.dxf")

    cad.rect(0, 0, 420, 297, layer="AM_BORDER")
    cad.rect(20, 10, 410, 287, layer="AM_BORDER")

    # Title Block
    tb_x1, tb_y1, tb_x2, tb_y2 = 230, 10, 410, 65
    cad.rect(tb_x1, tb_y1, tb_x2, tb_y2, layer="AM_BORDER")
    cad.line(tb_x1, 40, tb_x2, 40, layer="AM_BORDER")
    cad.line(tb_x1, 25, tb_x2, 25, layer="AM_BORDER")
    cad.line(320, 10, 320, 40, layer="AM_BORDER")

    cad.text(tb_x1 + 4, 56, 3.8, "PROJECT: SMART DUAL GAS DETECTOR (CO + LPG)", layer="AM_5")
    cad.text(tb_x1 + 4, 46, 3.0, "SHEET 1: GENERAL ENCLOSURE ASSEMBLY (NO PCBA)", layer="AM_5")
    cad.text(tb_x1 + 4, 31, 2.5, "MATERIAL: PC/ABS FLAME RETARDANT (UL 94-V0)", layer="AM_5")
    cad.text(tb_x1 + 4, 16, 2.5, "WALL THICKNESS: 2.20 mm +/- 0.15 mm", layer="AM_5")
    cad.text(324, 31, 2.5, "REVISION: 2.0 (STAGE 5)", layer="AM_5")
    cad.text(324, 16, 2.5, "SCALE: 1:1  |  UNITS: mm", layer="AM_5")

    # General Notes
    cad.text(25, 278, 3.2, "GENERAL MECHANICAL NOTES:", layer="AM_5")
    cad.text(25, 272, 2.2, "1. ALL DIMENSIONS ARE IN MILLIMETERS UNLESS SPECIFIED OTHERWISE.", layer="AM_5")
    cad.text(25, 267, 2.2, "2. GENERAL TOLERANCES: ISO 2768-mK (LINEAR +/-0.2mm, ANGULAR +/-30').", layer="AM_5")
    cad.text(25, 262, 2.2, "3. MOLD DRAFT: 1.0 DEG EXTERIOR SURFACES, 0.5 DEG INTERNAL SHUT-OFFS.", layer="AM_5")
    cad.text(25, 257, 2.2, "4. 4x PCB STANDOFF BOSSES SIZED FOR RUTHEX M2.5x5.7 BRASS INSERTS (CORE DIA 3.6mm).", layer="AM_5")
    cad.text(25, 252, 2.2, "5. ENCLOSURE 3D SOLIDS IMPORTABLE VIA 'IMPORT' COMMAND USING INCLUDED STEP FILES.", layer="AM_5")

    # View 1: Front Cover Plan View
    v1_x, v1_y = 125, 185
    cad.text(v1_x - 35, v1_y + 45, 3.0, "VIEW 1: FRONT HOUSING COVER (TOP PLAN VIEW)", layer="AM_5")
    cad.rounded_rect(v1_x, v1_y, 92.0, 72.0, 10.0, layer="AM_0")
    cad.rounded_rect(v1_x, v1_y, 87.6, 67.6, 7.8, layer="AM_1")
    cad.centerline(v1_x, v1_y, 104.0, orientation="horiz", layer="AM_2")
    cad.centerline(v1_x, v1_y, 84.0, orientation="vert", layer="AM_2")

    ls1_cx = v1_x - 3.0
    ls1_cy = v1_y + 13.0
    cad.circle(ls1_cx, ls1_cy, 1.6, layer="AM_0")
    cad.circle(ls1_cx, ls1_cy, 3.6, layer="AM_2")
    for a in range(0, 360, 60):
        rad = math.radians(a)
        cad.circle(ls1_cx + 3.6 * math.cos(rad), ls1_cy + 3.6 * math.sin(rad), 1.1, layer="AM_0")
    cad.circle(ls1_cx, ls1_cy, 7.0, layer="AM_1")

    cad.rounded_rect(v1_x - 3.4, v1_y + 21.0, 14.0, 3.8, 1.2, layer="AM_0")
    for lx in [-8.2, -5.0, -1.8, 1.4]:
        cad.circle(v1_x + lx, v1_y + 21.0, 1.0, layer="AM_1")

    cad.rounded_rect(v1_x + 7.0, v1_y + 16.0, 18.0, 12.0, 2.5, layer="AM_0")

    s1_cx = v1_x + 21.5
    s1_cy = v1_y + 10.5
    cad.circle(s1_cx, s1_cy, 10.0, layer="AM_1")
    for dy in [-6.0, -3.0, 0.0, 3.0, 6.0]:
        cad.rounded_rect(s1_cx, s1_cy + dy, 14.0, 1.2, 0.6, layer="AM_0")

    for dx in [-8.0, -4.0, 0.0, 4.0, 8.0]:
        cad.rounded_rect(v1_x + 24.0 + dx, v1_y + 32.0, 2.0, 5.0, 1.0, layer="AM_0")

    cad.dimension_horiz(v1_x - 46, v1_x + 46, v1_y + 40, "92.0", layer="AM_3")
    cad.dimension_vert(v1_y - 36, v1_y + 36, v1_x + 50, "72.0", layer="AM_3")

    # Section Cut A-A
    cad.line(v1_x - 52, v1_y + 13.0, v1_x + 52, v1_y + 13.0, layer="AM_BORDER")
    cad.line(v1_x - 52, v1_y + 13.0, v1_x - 52, v1_y + 20.0, layer="AM_BORDER")
    cad.line(v1_x + 52, v1_y + 13.0, v1_x + 52, v1_y + 20.0, layer="AM_BORDER")
    cad.text(v1_x - 55, v1_y + 22.0, 3.5, "A", layer="AM_5")
    cad.text(v1_x + 51, v1_y + 22.0, 3.5, "A", layer="AM_5")

    # View 2: Rear Chassis Base Plan View
    v2_x, v2_y = 295, 185
    cad.text(v2_x - 40, v2_y + 45, 3.0, "VIEW 2: REAR CHASSIS BASE (INTERIOR PLAN VIEW)", layer="AM_5")
    cad.rounded_rect(v2_x, v2_y, 92.0, 72.0, 10.0, layer="AM_0")
    cad.rounded_rect(v2_x, v2_y, 87.6, 67.6, 7.8, layer="AM_0")
    cad.centerline(v2_x, v2_y, 104.0, orientation="horiz", layer="AM_2")
    cad.centerline(v2_x, v2_y, 84.0, orientation="vert", layer="AM_2")

    bosses = [(-31.5, -21.5), (31.5, -21.5), (-31.5, 21.5), (31.5, 21.5)]
    for bx, by in bosses:
        cbx = v2_x + bx
        cby = v2_y + by
        cad.circle(cbx, cby, 2.75, layer="AM_0")
        cad.circle(cbx, cby, 1.80, layer="AM_0")
        for ang in [0, 120, 240]:
            rad = math.radians(ang)
            cad.line(cbx, cby, cbx + 4.2 * math.cos(rad), cby + 4.2 * math.sin(rad), layer="AM_0")

    cad.rect(v2_x - 46.0, v2_y - 19.0, v2_x - 43.8, v2_y - 7.0, layer="AM_0")
    cad.rect(v2_x - 46.0, v2_y + 7.0, v2_x - 43.8, v2_y + 19.0, layer="AM_0")
    for i in range(-2, 3):
        cad.rounded_rect(v2_x + 24.0 + i*4.5, v2_y - 18.5, 2.0, 14.0, 1.0, layer="AM_0")

    cad.dimension_horiz(v2_x - 31.5, v2_x + 31.5, v2_y - 28.0, "63.0 (PCB X-PITCH)", layer="AM_3")
    cad.dimension_vert(v2_y - 21.5, v2_y + 21.5, v2_x + 38.0, "43.0 (PCB Y-PITCH)", layer="AM_3")

    # View 3: Section A-A
    v3_x, v3_y = 125, 75
    cad.text(v3_x - 30, v3_y + 35, 3.0, "VIEW 3: SECTION A-A (LONGITUDINAL ELEVATION)", layer="AM_5")
    cad.rect(v3_x - 46, v3_y - 14, v3_x + 46, v3_y - 4, layer="AM_0")
    cad.rect(v3_x - 43.8, v3_y - 11.8, v3_x + 43.8, v3_y - 4, layer="AM_0")
    cad.rect(v3_x - 34.25, v3_y - 11.8, v3_x - 28.75, v3_y - 7.3, layer="AM_0")
    cad.rect(v3_x + 28.75, v3_y - 11.8, v3_x + 34.25, v3_y - 7.3, layer="AM_0")
    cad.rect(v3_x - 46, v3_y - 4, v3_x + 46, v3_y + 14, layer="AM_0")
    cad.rect(v3_x - 43.8, v3_y - 4, v3_x + 43.8, v3_y + 11.8, layer="AM_0")
    cad.rect(v3_x - 10.0, v3_y + 5.8, v3_x + 4.0, v3_y + 11.8, layer="AM_0")
    cad.rect(v3_x + 16.3, v3_y + 0.8, v3_x + 17.7, v3_y + 11.8, layer="AM_0")

    cad.dimension_vert(v3_y - 14, v3_y - 4, v3_x - 52, "10.0", layer="AM_3")
    cad.dimension_vert(v3_y - 4, v3_y + 14, v3_x - 52, "18.0", layer="AM_3")
    cad.dimension_vert(v3_y - 14, v3_y + 14, v3_x - 62, "28.0 (TOTAL)", layer="AM_3")

    # View 4: Wall Bracket Plan View
    v4_x, v4_y = 295, 75
    cad.text(v4_x - 30, v4_y + 35, 3.0, "VIEW 4: WALL MOUNT BRACKET (PLAN VIEW)", layer="AM_5")
    cad.rounded_rect(v4_x, v4_y, 86.0, 66.0, 8.0, layer="AM_0")
    cad.rounded_rect(v4_x, v4_y, 34.0, 22.0, 4.0, layer="AM_0")
    for kx in [-30.0, 30.0]:
        cad.circle(v4_x + kx, v4_y, 4.5, layer="AM_0")
        cad.circle(v4_x + kx, v4_y + 4.5, 2.25, layer="AM_0")
        cad.line(v4_x + kx - 2.25, v4_y, v4_x + kx - 2.25, v4_y + 4.5, layer="AM_0")
        cad.line(v4_x + kx + 2.25, v4_y, v4_x + kx + 2.25, v4_y + 4.5, layer="AM_0")

    for ky in [-24.0, 24.0]:
        cad.circle(v4_x, v4_y + ky, 4.5, layer="AM_0")
        cad.circle(v4_x + 4.5, v4_y + ky, 2.25, layer="AM_0")

    cad.dimension_horiz(v4_x - 30, v4_x + 30, v4_y - 25, "60.0 (EU BOX)", layer="AM_3")
    cad.save()


# ==============================================================================
# SHEET 2: FRONT COVER DETAIL DRAWING (ISO A4 - 297x210mm)
# ==============================================================================
def build_detail_front_cover():
    cad = AutoCADDrawing("cad/autocad/detail_front_cover.dxf")

    cad.rect(0, 0, 297, 210, layer="AM_BORDER")
    cad.rect(15, 10, 287, 200, layer="AM_BORDER")

    # Title Block
    cad.rect(157, 10, 287, 45, layer="AM_BORDER")
    cad.line(157, 28, 287, 28, layer="AM_BORDER")
    cad.line(222, 10, 222, 28, layer="AM_BORDER")
    cad.text(160, 37, 3.2, "PART: FRONT HOUSING BEZEL (COVER)", layer="AM_5")
    cad.text(160, 31, 2.2, "DWG NO: CO-ENC-DET-001  |  REV: 2.0", layer="AM_5")
    cad.text(160, 18, 2.2, "MATERIAL: PC/ABS (UL 94-V0)", layer="AM_5")
    cad.text(225, 18, 2.2, "SCALE: 1:1 (mm)", layer="AM_5")

    # Plan View
    cx, cy = 100, 125
    cad.text(cx - 35, cy + 50, 2.8, "FRONT COVER - EXTERIOR TOP VIEW", layer="AM_5")
    cad.rounded_rect(cx, cy, 92.0, 72.0, 10.0, layer="AM_0")
    cad.rounded_rect(cx, cy, 87.6, 67.6, 7.8, layer="AM_1")
    cad.centerline(cx, cy, 102.0, "horiz", "AM_2")
    cad.centerline(cx, cy, 82.0, "vert", "AM_2")

    # Acoustic Rosette
    cad.circle(cx - 3.0, cy + 13.0, 1.6, layer="AM_0")
    for a in range(0, 360, 60):
        rad = math.radians(a)
        cad.circle(cx - 3.0 + 3.6 * math.cos(rad), cy + 13.0 + 3.6 * math.sin(rad), 1.1, layer="AM_0")

    # UI Windows
    cad.rounded_rect(cx - 3.4, cy + 21.0, 14.0, 3.8, 1.2, layer="AM_0")
    cad.rounded_rect(cx + 7.0, cy + 16.0, 18.0, 12.0, 2.5, layer="AM_0")

    # CO Louvers
    for dy in [-6.0, -3.0, 0.0, 3.0, 6.0]:
        cad.rounded_rect(cx + 21.5, cy + 10.5 + dy, 14.0, 1.2, 0.6, layer="AM_0")

    # Dimensions
    cad.dimension_horiz(cx - 46, cx + 46, cy + 42, "92.0", layer="AM_3")
    cad.dimension_vert(cy - 36, cy + 36, cx + 50, "72.0", layer="AM_3")
    cad.text(cx - 40, cy - 45, 2.0, "SURFACE FINISH: SPI D-2 / VDI 24 MATTE TEXTURE", layer="AM_5")
    cad.text(cx - 40, cy - 50, 2.0, "DRAFT ANGLE: 1.5 DEG ON EXTERNAL VERTICAL WALLS", layer="AM_5")

    # Elevation Section View
    sec_x, sec_y = 215, 125
    cad.text(sec_x - 30, sec_y + 50, 2.8, "SECTION B-B (WALL DETAIL)", layer="AM_5")
    cad.rect(sec_x - 35, sec_y - 9, sec_x + 35, sec_y + 9, layer="AM_0")
    cad.rect(sec_x - 32.8, sec_y - 9, sec_x + 32.8, sec_y + 6.8, layer="AM_0")
    # Internal barrier rib
    cad.rect(sec_x + 16.3, sec_y - 4.2, sec_x + 17.7, sec_y + 6.8, layer="AM_0")
    cad.dimension_vert(sec_y - 9, sec_y + 9, sec_x + 40, "18.0", layer="AM_3")
    cad.dimension_vert(sec_y + 6.8, sec_y + 9, sec_x - 40, "2.2 WALL", layer="AM_3")

    cad.save()


# ==============================================================================
# SHEET 3: REAR CHASSIS BASE DETAIL DRAWING (ISO A4 - 297x210mm)
# ==============================================================================
def build_detail_rear_chassis():
    cad = AutoCADDrawing("cad/autocad/detail_rear_chassis.dxf")

    cad.rect(0, 0, 297, 210, layer="AM_BORDER")
    cad.rect(15, 10, 287, 200, layer="AM_BORDER")

    # Title Block
    cad.rect(157, 10, 287, 45, layer="AM_BORDER")
    cad.line(157, 28, 287, 28, layer="AM_BORDER")
    cad.line(222, 10, 222, 28, layer="AM_BORDER")
    cad.text(160, 37, 3.2, "PART: REAR CHASSIS BASE", layer="AM_5")
    cad.text(160, 31, 2.2, "DWG NO: CO-ENC-DET-002  |  REV: 2.0", layer="AM_5")
    cad.text(160, 18, 2.2, "MATERIAL: PC/ABS (UL 94-V0)", layer="AM_5")
    cad.text(225, 18, 2.2, "SCALE: 1:1 (mm)", layer="AM_5")

    # Interior Plan View
    cx, cy = 100, 125
    cad.text(cx - 35, cy + 50, 2.8, "REAR CHASSIS - INTERIOR PLAN VIEW", layer="AM_5")
    cad.rounded_rect(cx, cy, 92.0, 72.0, 10.0, layer="AM_0")
    cad.rounded_rect(cx, cy, 87.6, 67.6, 7.8, layer="AM_0")
    cad.centerline(cx, cy, 102.0, "horiz", "AM_2")
    cad.centerline(cx, cy, 82.0, "vert", "AM_2")

    bosses = [(-31.5, -21.5), (31.5, -21.5), (-31.5, 21.5), (31.5, 21.5)]
    for bx, by in bosses:
        cbx = cx + bx
        cby = cy + by
        cad.circle(cbx, cby, 2.75, layer="AM_0")
        cad.circle(cbx, cby, 1.80, layer="AM_0")
        for ang in [0, 120, 240]:
            rad = math.radians(ang)
            cad.line(cbx, cby, cbx + 4.2 * math.cos(rad), cby + 4.2 * math.sin(rad), layer="AM_0")

    cad.rect(cx - 46.0, cy - 19.0, cx - 43.8, cy - 7.0, layer="AM_0")
    cad.rect(cx - 46.0, cy + 7.0, cx - 43.8, cy + 19.0, layer="AM_0")

    cad.dimension_horiz(cx - 31.5, cx + 31.5, cy - 28.0, "63.00", layer="AM_3")
    cad.dimension_vert(cy - 21.5, cy + 21.5, cx + 38.0, "43.00", layer="AM_3")

    # Section View of Boss Detail
    sec_x, sec_y = 220, 125
    cad.text(sec_x - 30, sec_y + 50, 2.8, "DETAIL C: PCB BOSS (2:1 SCALE)", layer="AM_5")
    # Base floor 2.2mm
    cad.rect(sec_x - 20, sec_y - 10, sec_x + 20, sec_y - 5.6, layer="AM_0")
    # Boss body dia 5.5mm x height 4.5mm
    cad.rect(sec_x - 5.5, sec_y - 5.6, sec_x + 5.5, sec_y + 3.4, layer="AM_0")
    # Insert pilot hole dia 3.6mm
    cad.rect(sec_x - 3.6, sec_y - 5.6, sec_x + 3.6, sec_y + 3.4, layer="AM_1")
    # Centerline
    cad.centerline(sec_x, sec_y - 1, 18.0, "vert", "AM_2")

    cad.dimension_horiz(sec_x - 5.5, sec_x + 5.5, sec_y + 8.0, "DIA 5.50 (BOSS OD)", layer="AM_3")
    cad.dimension_horiz(sec_x - 3.6, sec_x + 3.6, sec_y - 15.0, "DIA 3.60 (INSERT ID)", layer="AM_3")
    cad.dimension_vert(sec_y - 5.6, sec_y + 3.4, sec_x + 12.0, "4.50 STANDOFF", layer="AM_3")

    cad.save()


# ==============================================================================
# SHEET 4: WALL BRACKET DETAIL DRAWING (ISO A4 - 297x210mm)
# ==============================================================================
def build_detail_wall_bracket():
    cad = AutoCADDrawing("cad/autocad/detail_wall_bracket.dxf")

    cad.rect(0, 0, 297, 210, layer="AM_BORDER")
    cad.rect(15, 10, 287, 200, layer="AM_BORDER")

    # Title Block
    cad.rect(157, 10, 287, 45, layer="AM_BORDER")
    cad.line(157, 28, 287, 28, layer="AM_BORDER")
    cad.line(222, 10, 222, 28, layer="AM_BORDER")
    cad.text(160, 37, 3.2, "PART: WALL MOUNT BRACKET", layer="AM_5")
    cad.text(160, 31, 2.2, "DWG NO: CO-ENC-DET-003  |  REV: 2.0", layer="AM_5")
    cad.text(160, 18, 2.2, "MATERIAL: PC/ABS (UL 94-V0)", layer="AM_5")
    cad.text(225, 18, 2.2, "SCALE: 1:1 (mm)", layer="AM_5")

    cx, cy = 100, 125
    cad.text(cx - 35, cy + 48, 2.8, "WALL BRACKET - DRILLING TEMPLATE", layer="AM_5")
    cad.rounded_rect(cx, cy, 86.0, 66.0, 8.0, layer="AM_0")
    cad.centerline(cx, cy, 96.0, "horiz", "AM_2")
    cad.centerline(cx, cy, 76.0, "vert", "AM_2")

    # Central opening
    cad.rounded_rect(cx, cy, 34.0, 22.0, 4.0, layer="AM_0")

    # Keyholes
    for kx in [-30.0, 30.0]:
        cad.circle(cx + kx, cy, 4.5, layer="AM_0")
        cad.circle(cx + kx, cy + 4.5, 2.25, layer="AM_0")
        cad.line(cx + kx - 2.25, cy, cx + kx - 2.25, cy + 4.5, layer="AM_0")
        cad.line(cx + kx + 2.25, cy, cx + kx + 2.25, cy + 4.5, layer="AM_0")

    # Bayonet tabs
    for bx, by in [(-30, -20), (30, -20), (-30, 20), (30, 20)]:
        cad.circle(cx + bx, cy + by, 3.2, layer="AM_0")

    cad.dimension_horiz(cx - 30, cx + 30, cy - 25, "60.0 (EU 60mm BOX)", layer="AM_3")
    cad.dimension_horiz(cx - 43, cx + 43, cy + 38, "86.0", layer="AM_3")
    cad.dimension_vert(cy - 33, cy + 33, cx + 48, "66.0", layer="AM_3")

    # Side Profile
    sec_x, sec_y = 220, 125
    cad.text(sec_x - 30, sec_y + 48, 2.8, "SIDE PROFILE (PLATE THICKNESS)", layer="AM_5")
    cad.rect(sec_x - 33, sec_y - 1.5, sec_x + 33, sec_y + 1.5, layer="AM_0")
    # Bayonet lugs
    cad.rect(sec_x - 23, sec_y + 1.5, sec_x - 17, sec_y + 4.5, layer="AM_0")
    cad.rect(sec_x + 17, sec_y + 1.5, sec_x + 23, sec_y + 4.5, layer="AM_0")

    cad.dimension_vert(sec_y - 1.5, sec_y + 1.5, sec_x + 38, "3.0 PLATE", layer="AM_3")
    cad.dimension_vert(sec_y - 1.5, sec_y + 4.5, sec_x - 42, "6.0 TOTAL", layer="AM_3")

    cad.save()


# ==============================================================================
# MECHANICAL FASTENER & HARDWARE BOM
# ==============================================================================
def build_mechanical_bom():
    bom_path = "cad/autocad/MECHANICAL_BOM.csv"
    rows = [
        ["Item", "Part Number / Description", "Category", "Material / Finish", "Qty", "Manufacturer / Vendor", "Assembly Function"],
        ["1", "CO_Enclosure_Front_Cover", "Plastic Molded Part", "PC/ABS UL 94-V0 (White)", "1", "Custom Injection Molding", "Front cosmetic housing, acoustic horn, UI aperture"],
        ["2", "CO_Enclosure_Chassis_Base", "Plastic Molded Part", "PC/ABS UL 94-V0 (White)", "1", "Custom Injection Molding", "Rear carrier chassis, PCB mounting standoffs, vents"],
        ["3", "CO_Enclosure_Wall_Bracket", "Plastic Molded Part", "PC/ABS UL 94-V0 (Grey)", "1", "Custom Injection Molding", "Quick-mount wall plate with EU/US gang box keyholes"],
        ["4", "RX-M2.5x5.7", "Threaded Insert", "Brass (Knurled)", "4", "Ruthex / McMaster-Carr", "M2.5 ultrasonic heat-set inserts for PCB standoff bosses"],
        ["5", "92095A182", "Machine Screw", "A2 Stainless Steel (Black)", "4", "McMaster-Carr / Fastenal", "M2.5 x 6mm Pan Head Torx (T8) PCB retention screws"],
        ["6", "PORON 4701-30", "Acoustic Gasket", "Polyurethane Foam (1.5mm thk)", "1", "Rogers Corp / 3M", "Annular sealing ring (OD 12mm, ID 9mm) for LS1 buzzer"],
        ["7", "PTFE-VM-020", "Dust / Gas Filter", "Hydrophobic ePTFE Membrane", "1", "Porex / Donaldson", "IP52 dust/water barrier for Winsen ME3-CO diffusion well"],
        ["8", "MAKROLON 2807", "Optical Light Guide", "Optical Polycarbonate (Clear)", "1", "Custom Injection Molding", "4-channel light pipe with lens contours for D4, D5, D6, D8"],
        ["9", "PTS-CAP-01", "Tactile Button Cap", "ABS (Pantone Cool Grey 1C)", "1", "Custom Molded", "Dual-action compliant button cap actuating SW1 and SW2"],
        ["10", "SPIRIT-VIAL-08", "Bubble Level Vial", "Acrylic / Mineral Spirit", "1", "Keystone / Empire", "Dia 8.0mm x 15mm cylindrical spirit level for wall bracket"]
    ]
    with open(bom_path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(",".join([f'"{c}"' for c in r]) + "\n")
    print(f"Generated Mechanical BOM: {bom_path}")


def main():
    build_master_drawing()
    build_detail_front_cover()
    build_detail_rear_chassis()
    build_detail_wall_bracket()
    build_mechanical_bom()
    print("\nALL AUTOCAD MECHANICAL DRAWING SHEETS AND BOM GENERATED!")

if __name__ == "__main__":
    main()
