"""
AutoCAD Mechanical Production Drawing Generator for Smart Dual Gas Detector Enclosure
Outputs:
  - cad/autocad/co_detector_enclosure_drawing.dxf (ISO A3 Multi-View Blueprint)
  - cad/autocad/build_enclosure_drawing.lsp (AutoLISP automation routine)
  - cad/autocad/import_3d_enclosure.scr (AutoCAD 3D STEP import script)
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
        # Extension lines
        self.line(x1, y - 2, x1, y + 2, layer)
        self.line(x2, y - 2, x2, y + 2, layer)
        # Dim line
        self.line(x1, y, x2, y, layer)
        # Arrow ticks
        self.line(x1, y, x1 + 1.5, y + 0.6, layer)
        self.line(x1, y, x1 + 1.5, y - 0.6, layer)
        self.line(x2, y, x2 - 1.5, y + 0.6, layer)
        self.line(x2, y, x2 - 1.5, y - 0.6, layer)
        # Dim text
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

    def hatch_lines(self, x1, y1, x2, y2, pitch=2.5, angle_deg=45, layer="AM_4"):
        # Simple section hatch fill
        rad = math.radians(angle_deg)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        w = x2 - x1
        h = y2 - y1
        steps = int((w + h) / pitch)
        for i in range(-steps, steps * 2):
            offset = i * pitch
            # Intersect with box
            pts = []
            # Bottom edge (y1)
            t_bot = (y1 - offset) / (sin_a / cos_a) if abs(cos_a) > 1e-4 else None
            # Left edge (x1)
            # Generate clipped lines
            lx1 = x1 + offset * cos_a - 50 * sin_a
            ly1 = y1 + offset * sin_a + 50 * cos_a
            lx2 = x1 + offset * cos_a + 50 * sin_a
            ly2 = y1 + offset * sin_a - 50 * cos_a
            # Simple clipped hatch inside box:
            hx1 = max(x1, min(x2, x1 + offset))
            hy1 = y1
            hx2 = x1
            hy2 = min(y2, max(y1, y1 + offset))
            if hx1 <= x2 and hy2 <= y2 and (hx1 != hx2 or hy1 != hy2):
                self.line(hx1, hy1, hx2, hy2, layer)

    def save(self):
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        # Header with AutoCAD Mechanical Standard Layers
        layers = [
            ("0", 7, "CONTINUOUS"),
            ("AM_0", 7, "CONTINUOUS"),      # Visible contours (0.50mm)
            ("AM_1", 2, "HIDDEN2"),         # Hidden lines (Yellow, 0.25mm)
            ("AM_2", 1, "CENTER2"),         # Centerlines (Red, 0.25mm)
            ("AM_3", 3, "CONTINUOUS"),      # Dimensions (Green, 0.25mm)
            ("AM_4", 4, "CONTINUOUS"),      # Hatches (Cyan, 0.25mm)
            ("AM_5", 6, "CONTINUOUS"),      # Text/Notes (Magenta, 0.35mm)
            ("AM_BORDER", 5, "CONTINUOUS")  # Frame/Title block (Blue, 0.70mm)
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


def build_drawing():
    cad = AutoCADDrawing("cad/autocad/co_detector_enclosure_drawing.dxf")

    # -------------------------------------------------------------------------
    # ISO A3 BORDER & TITLE BLOCK (420mm x 297mm)
    # -------------------------------------------------------------------------
    cad.rect(0, 0, 420, 297, layer="AM_BORDER") # Sheet boundary
    cad.rect(20, 10, 410, 287, layer="AM_BORDER") # Drawing frame (20mm binding edge)

    # Title Block (Bottom-Right, 180mm x 55mm)
    tb_x1, tb_y1, tb_x2, tb_y2 = 230, 10, 410, 65
    cad.rect(tb_x1, tb_y1, tb_x2, tb_y2, layer="AM_BORDER")
    cad.line(tb_x1, 40, tb_x2, 40, layer="AM_BORDER")
    cad.line(tb_x1, 25, tb_x2, 25, layer="AM_BORDER")
    cad.line(320, 10, 320, 40, layer="AM_BORDER")

    cad.text(tb_x1 + 4, 56, 3.8, "PROJECT: SMART DUAL GAS DETECTOR (CO + LPG)", layer="AM_5")
    cad.text(tb_x1 + 4, 46, 3.0, "DRAWING: MECHANICAL ENCLOSURE BLUEPRINT (NO PCBA)", layer="AM_5")
    cad.text(tb_x1 + 4, 31, 2.5, "MATERIAL: PC/ABS FLAME RETARDANT (UL 94-V0)", layer="AM_5")
    cad.text(tb_x1 + 4, 16, 2.5, "WALL THICKNESS: 2.20 mm +/- 0.15 mm", layer="AM_5")
    cad.text(324, 31, 2.5, "REVISION: 2.0 (STAGE 5)", layer="AM_5")
    cad.text(324, 16, 2.5, "SCALE: 1:1  |  UNITS: mm", layer="AM_5")

    # General Notes
    cad.text(25, 278, 3.2, "GENERAL MECHANICAL NOTES:", layer="AM_5")
    cad.text(25, 272, 2.2, "1. ALL DIMENSIONS ARE IN MILLIMETERS UNLESS SPECIFIED OTHERWISE.", layer="AM_5")
    cad.text(25, 267, 2.2, "2. GENERAL TOLERANCES: ISO 2768-mK (LINEAR +/-0.2mm, ANGULAR +/-30').", layer="AM_5")
    cad.text(25, 262, 2.2, "3. MOLD DRAFT: 1.0 DEG EXTERIOR SURFACES, 0.5 DEG INTERNAL SHUT-OFFS.", layer="AM_5")
    cad.text(25, 257, 2.2, "4. 4x PCB STANDOFF BOSSES SIZED FOR RUTHEX M2.5x5.7 BRASS HEAT-SET INSERTS (CORE DIA 3.6mm).", layer="AM_5")
    cad.text(25, 252, 2.2, "5. ENCLOSURE COMPONENT GEOMETRY IMPORTABLE AS ACIS 3D SOLID VIA 'IMPORT' COMMAND.", layer="AM_5")

    # -------------------------------------------------------------------------
    # VIEW 1: FRONT COVER - TOP PLAN VIEW (Center: 125, 185)
    # -------------------------------------------------------------------------
    v1_x, v1_y = 125, 185
    cad.text(v1_x - 35, v1_y + 45, 3.0, "VIEW 1: FRONT HOUSING COVER (TOP PLAN VIEW)", layer="AM_5")

    # Outer squircle: 92 x 72, R10
    cad.rounded_rect(v1_x, v1_y, 92.0, 72.0, 10.0, layer="AM_0")
    # Inner wall boundary (hidden line)
    cad.rounded_rect(v1_x, v1_y, 87.6, 67.6, 7.8, layer="AM_1")
    # Centerlines
    cad.centerline(v1_x, v1_y, 104.0, orientation="horiz", layer="AM_2")
    cad.centerline(v1_x, v1_y, 84.0, orientation="vert", layer="AM_2")

    # 1. Acoustic Rosette (LS1 at -3.0, 13.0)
    ls1_cx = v1_x - 3.0
    ls1_cy = v1_y + 13.0
    cad.centerline(ls1_cx, ls1_cy, 18.0, orientation="cross", layer="AM_2")
    cad.circle(ls1_cx, ls1_cy, 1.6, layer="AM_0") # Center hole dia 3.2mm
    cad.circle(ls1_cx, ls1_cy, 3.6, layer="AM_2") # Pitch circle dia 7.2mm
    for a in range(0, 360, 60):
        rad = math.radians(a)
        hx = ls1_cx + 3.6 * math.cos(rad)
        hy = ls1_cy + 3.6 * math.sin(rad)
        cad.circle(hx, hy, 1.1, layer="AM_0") # 6 satellite dia 2.2mm
    cad.circle(ls1_cx, ls1_cy, 7.0, layer="AM_1") # Shroud OD 14mm hidden

    # 2. Status LED Light Pipe Window (-3.4, 21.0)
    cad.rounded_rect(v1_x - 3.4, v1_y + 21.0, 14.0, 3.8, 1.2, layer="AM_0")
    for lx in [-8.2, -5.0, -1.8, 1.4]:
        cad.circle(v1_x + lx, v1_y + 21.0, 1.0, layer="AM_1")

    # 3. Test/Hush Button Cutout (7.0, 16.0)
    cad.rounded_rect(v1_x + 7.0, v1_y + 16.0, 18.0, 12.0, 2.5, layer="AM_0")

    # 4. CO Sensor Diffusion Well (21.5, 10.5)
    s1_cx = v1_x + 21.5
    s1_cy = v1_y + 10.5
    cad.centerline(s1_cx, s1_cy, 24.0, orientation="cross", layer="AM_2")
    cad.circle(s1_cx, s1_cy, 10.0, layer="AM_1") # Winsen ME3-CO boundary
    for dy in [-6.0, -3.0, 0.0, 3.0, 6.0]:
        cad.rounded_rect(s1_cx, s1_cy + dy, 14.0, 1.2, 0.6, layer="AM_0")

    # 5. LPG Sensor Exhaust Vents (24.0, 32.0)
    for dx in [-8.0, -4.0, 0.0, 4.0, 8.0]:
        cad.rounded_rect(v1_x + 24.0 + dx, v1_y + 32.0, 2.0, 5.0, 1.0, layer="AM_0")

    # Dimensions for View 1
    cad.dimension_horiz(v1_x - 46, v1_x + 46, v1_y + 40, "92.0", layer="AM_3")
    cad.dimension_vert(v1_y - 36, v1_y + 36, v1_x + 50, "72.0", layer="AM_3")
    cad.dimension_horiz(v1_x, s1_cx, v1_y + 28, "21.5", layer="AM_3")
    cad.dimension_vert(v1_y, s1_cy, v1_x + 36, "10.5", layer="AM_3")

    # Section Cut Line A-A
    cad.line(v1_x - 52, v1_y + 13.0, v1_x + 52, v1_y + 13.0, layer="AM_BORDER")
    cad.line(v1_x - 52, v1_y + 13.0, v1_x - 52, v1_y + 20.0, layer="AM_BORDER")
    cad.line(v1_x + 52, v1_y + 13.0, v1_x + 52, v1_y + 20.0, layer="AM_BORDER")
    cad.text(v1_x - 55, v1_y + 22.0, 3.5, "A", layer="AM_5")
    cad.text(v1_x + 51, v1_y + 22.0, 3.5, "A", layer="AM_5")

    # -------------------------------------------------------------------------
    # VIEW 2: REAR CHASSIS BASE - INTERIOR PLAN VIEW (Center: 295, 185)
    # -------------------------------------------------------------------------
    v2_x, v2_y = 295, 185
    cad.text(v2_x - 40, v2_y + 45, 3.0, "VIEW 2: REAR CHASSIS BASE (INTERIOR PLAN VIEW)", layer="AM_5")

    # Outer and inner shells
    cad.rounded_rect(v2_x, v2_y, 92.0, 72.0, 10.0, layer="AM_0")
    cad.rounded_rect(v2_x, v2_y, 87.6, 67.6, 7.8, layer="AM_0")
    cad.centerline(v2_x, v2_y, 104.0, orientation="horiz", layer="AM_2")
    cad.centerline(v2_x, v2_y, 84.0, orientation="vert", layer="AM_2")

    # 4x PCB Mounting Bosses (+/-31.5, +/-21.5)
    bosses = [(-31.5, -21.5), (31.5, -21.5), (-31.5, 21.5), (31.5, 21.5)]
    for bx, by in bosses:
        cbx = v2_x + bx
        cby = v2_y + by
        cad.centerline(cbx, cby, 10.0, orientation="cross", layer="AM_2")
        cad.circle(cbx, cby, 2.75, layer="AM_0") # OD 5.5mm
        cad.circle(cbx, cby, 1.80, layer="AM_0") # ID 3.6mm
        # Gusset ribs
        for ang in [0, 120, 240]:
            rad = math.radians(ang)
            gx = cbx + 4.2 * math.cos(rad)
            gy = cby + 4.2 * math.sin(rad)
            cad.line(cbx, cby, gx, gy, layer="AM_0")

    # Terminal block cutouts on left wall
    cad.rect(v2_x - 46.0, v2_y - 19.0, v2_x - 43.8, v2_y - 7.0, layer="AM_0")
    cad.rect(v2_x - 46.0, v2_y + 7.0, v2_x - 43.8, v2_y + 19.0, layer="AM_0")

    # Bottom convection slots below LPG sensor (Zone F)
    for i in range(-2, 3):
        cad.rounded_rect(v2_x + 24.0 + i*4.5, v2_y - 18.5, 2.0, 14.0, 1.0, layer="AM_0")

    # Dimensions for View 2
    cad.dimension_horiz(v2_x - 31.5, v2_x + 31.5, v2_y - 28.0, "63.0 (PCB X-PITCH)", layer="AM_3")
    cad.dimension_vert(v2_y - 21.5, v2_y + 21.5, v2_x + 38.0, "43.0 (PCB Y-PITCH)", layer="AM_3")
    cad.text(v2_x - 18, v2_y - 32.0, 2.2, "4x M2.5 BRASS INSERT BOSSES", layer="AM_5")

    # -------------------------------------------------------------------------
    # VIEW 3: SECTION A-A - LONGITUDINAL SECTION (Center: 125, 75)
    # -------------------------------------------------------------------------
    v3_x, v3_y = 125, 75
    cad.text(v3_x - 30, v3_y + 35, 3.0, "VIEW 3: SECTION A-A (LONGITUDINAL ELEVATION)", layer="AM_5")

    # Base Chassis Section: 92mm wide, 10mm high, wall 2.2mm
    cad.rect(v3_x - 46, v3_y - 14, v3_x + 46, v3_y - 4, layer="AM_0") # Outer base
    cad.rect(v3_x - 43.8, v3_y - 11.8, v3_x + 43.8, v3_y - 4, layer="AM_0") # Inner cavity
    # Base bosses in section (+/-31.5)
    cad.rect(v3_x - 34.25, v3_y - 11.8, v3_x - 28.75, v3_y - 7.3, layer="AM_0")
    cad.rect(v3_x + 28.75, v3_y - 11.8, v3_x + 34.25, v3_y - 7.3, layer="AM_0")
    # Insert pilot hole
    cad.rect(v3_x - 33.3, v3_y - 11.8, v3_x - 29.7, v3_y - 7.3, layer="AM_1")
    cad.rect(v3_x + 29.7, v3_y - 11.8, v3_x + 33.3, v3_y - 7.3, layer="AM_1")

    # Front Cover Section: 92mm wide, 18mm high (offset up from base)
    cad.rect(v3_x - 46, v3_y - 4, v3_x + 46, v3_y + 14, layer="AM_0")
    cad.rect(v3_x - 43.8, v3_y - 4, v3_x + 43.8, v3_y + 11.8, layer="AM_0")

    # Internal Buzzer Acoustic Shroud (at -3.0mm, ID 11, OD 14, extends down 6mm)
    cad.rect(v3_x - 10.0, v3_y + 5.8, v3_x + 4.0, v3_y + 11.8, layer="AM_0")
    cad.rect(v3_x - 8.5, v3_y + 5.8, v3_x + 2.5, v3_y + 11.8, layer="AM_0")

    # Internal Thermal Barrier Rib (at X = 17.0mm, thickness 1.4mm, extends down 11mm)
    cad.rect(v3_x + 16.3, v3_y + 0.8, v3_x + 17.7, v3_y + 11.8, layer="AM_0")

    # Rosette through-holes in top ceiling
    cad.line(v3_x - 4.6, v3_y + 11.8, v3_x - 4.6, v3_y + 14.0, layer="AM_0")
    cad.line(v3_x - 1.4, v3_y + 11.8, v3_x - 1.4, v3_y + 14.0, layer="AM_0")

    # Height dimensions
    cad.dimension_vert(v3_y - 14, v3_y - 4, v3_x - 52, "10.0 (BASE)", layer="AM_3")
    cad.dimension_vert(v3_y - 4, v3_y + 14, v3_x - 52, "18.0 (COVER)", layer="AM_3")
    cad.dimension_vert(v3_y - 14, v3_y + 14, v3_x - 62, "28.0 (TOTAL)", layer="AM_3")
    cad.dimension_vert(v3_y - 11.8, v3_y - 7.3, v3_x + 50, "4.5 STANDOFF", layer="AM_3")
    cad.dimension_vert(v3_y + 11.8, v3_y + 14.0, v3_x + 50, "2.2 WALL", layer="AM_3")

    # -------------------------------------------------------------------------
    # VIEW 4: WALL MOUNT BRACKET (Center: 295, 75)
    # -------------------------------------------------------------------------
    v4_x, v4_y = 295, 75
    cad.text(v4_x - 30, v4_y + 35, 3.0, "VIEW 4: WALL MOUNT BRACKET (PLAN VIEW)", layer="AM_5")

    # Plate: 86 x 66, R8
    cad.rounded_rect(v4_x, v4_y, 86.0, 66.0, 8.0, layer="AM_0")
    cad.centerline(v4_x, v4_y, 96.0, orientation="horiz", layer="AM_2")
    cad.centerline(v4_x, v4_y, 76.0, orientation="vert", layer="AM_2")

    # Central wire opening: 34 x 22, R4
    cad.rounded_rect(v4_x, v4_y, 34.0, 22.0, 4.0, layer="AM_0")

    # EU 60mm keyholes (+/-30, 0)
    for kx in [-30.0, 30.0]:
        ckx = v4_x + kx
        cad.circle(ckx, v4_y, 4.5, layer="AM_0")
        cad.circle(ckx, v4_y + 4.5, 2.25, layer="AM_0")
        cad.line(ckx - 2.25, v4_y, ckx - 2.25, v4_y + 4.5, layer="AM_0")
        cad.line(ckx + 2.25, v4_y, ckx + 2.25, v4_y + 4.5, layer="AM_0")

    # US 83.5mm keyholes (0, +/-41.75) -> scaled inside margin
    for ky in [-24.0, 24.0]:
        cky = v4_y + ky
        cad.circle(v4_x, cky, 4.5, layer="AM_0")
        cad.circle(v4_x + 4.5, cky, 2.25, layer="AM_0")
        cad.line(v4_x, cky - 2.25, v4_x + 4.5, cky - 2.25, layer="AM_0")
        cad.line(v4_x, cky + 2.25, v4_x + 4.5, cky + 2.25, layer="AM_0")

    # 4x Bayonet lugs (+/-30, +/-20)
    for bx, by in [(-30, -20), (30, -20), (-30, 20), (30, 20)]:
        cad.circle(v4_x + bx, v4_y + by, 3.2, layer="AM_0")

    # Dimensions for View 4
    cad.dimension_horiz(v4_x - 30, v4_x + 30, v4_y - 25, "60.0 (EU JUNCTION BOX)", layer="AM_3")
    cad.dimension_horiz(v4_x - 43, v4_x + 43, v4_y + 26, "86.0", layer="AM_3")
    cad.dimension_vert(v4_y - 33, v4_y + 33, v4_x + 47, "66.0", layer="AM_3")

    cad.save()


def build_autolisp_script():
    lsp_path = "cad/autocad/build_enclosure_drawing.lsp"
    content = """; ==============================================================================
; AutoCAD Mechanical AutoLISP Automation Routine: CO Detector Enclosure
; Architecture: Revision 2.0 (Stage 5)
; Instructions:
;   1. Open AutoCAD Mechanical.
;   2. Type (load "build_enclosure_drawing.lsp") in the command line (or drag-and-drop).
;   3. Type DRAW_ENCLOSURE and press Enter.
; ==============================================================================

(defun c:DRAW_ENCLOSURE ()
  (setvar "CMDECHO" 0)
  (setvar "OSMODE" 0)
  
  ;; 1. Setup Mechanical Standard Layers
  (command "-LAYER" "M" "AM_0" "C" "7" "" "LW" "0.50" "" "") ; Contours
  (command "-LAYER" "M" "AM_1" "C" "2" "" "L" "HIDDEN2" "" "LW" "0.25" "" "") ; Hidden
  (command "-LAYER" "M" "AM_2" "C" "1" "" "L" "CENTER2" "" "LW" "0.25" "" "") ; Centerlines
  (command "-LAYER" "M" "AM_3" "C" "3" "" "LW" "0.25" "" "") ; Dimensions
  (command "-LAYER" "M" "AM_4" "C" "4" "" "LW" "0.25" "" "") ; Hatch
  (command "-LAYER" "M" "AM_5" "C" "6" "" "LW" "0.35" "" "") ; Text
  (command "-LAYER" "M" "AM_BORDER" "C" "5" "" "LW" "0.70" "" "") ; Border
  
  ;; 2. Draw A3 Border & Frame
  (setvar "CLAYER" "AM_BORDER")
  (command "RECTANG" "0,0" "420,297")
  (command "RECTANG" "20,10" "410,287")
  
  ;; Title Block
  (command "RECTANG" "230,10" "410,65")
  (command "LINE" "230,40" "410,40" "")
  (command "LINE" "230,25" "410,25" "")
  (command "LINE" "320,10" "320,40" "")
  
  (setvar "CLAYER" "AM_5")
  (command "TEXT" "234,55" "3.5" "0" "PROJECT: SMART DUAL GAS DETECTOR (CO + LPG)")
  (command "TEXT" "234,45" "2.8" "0" "DRAWING: MECHANICAL ENCLOSURE BLUEPRINT")
  (command "TEXT" "234,30" "2.5" "0" "MATERIAL: PC/ABS FLAME RETARDANT (UL 94-V0)")
  (command "TEXT" "234,16" "2.5" "0" "WALL THICKNESS: 2.20 mm +/- 0.15 mm")
  (command "TEXT" "324,30" "2.5" "0" "REV: 2.0 (STAGE 5)")
  (command "TEXT" "324,16" "2.5" "0" "SCALE: 1:1 (mm)")
  
  ;; 3. View 1: Front Cover Plan View
  (setvar "CLAYER" "AM_0")
  (command "RECTANG" "F" "10" "79,149" "171,221")
  
  (setvar "CLAYER" "AM_2")
  (command "LINE" "73,185" "177,185" "")
  (command "LINE" "125,143" "125,227" "")
  
  ;; Rosette Acoustic Horn (at LS1: 122, 198)
  (setvar "CLAYER" "AM_0")
  (command "CIRCLE" "122,198" "1.6") ; Center hole
  (command "CIRCLE" "125.6,198" "1.1")
  (command "CIRCLE" "123.8,201.1" "1.1")
  (command "CIRCLE" "120.2,201.1" "1.1")
  (command "CIRCLE" "118.4,198" "1.1")
  (command "CIRCLE" "120.2,194.9" "1.1")
  (command "CIRCLE" "123.8,194.9" "1.1")
  
  ;; Button Cutout (at 132, 201)
  (command "RECTANG" "F" "2.5" "123,195" "141,207")
  
  ;; 4. Zoom Extents
  (command "ZOOM" "E")
  (setvar "CMDECHO" 1)
  (princ "\nAutoCAD Mechanical: Dual Gas Detector Enclosure successfully generated!")
  (princ)
)
"""
    with open(lsp_path, "w", encoding="ascii") as f:
        f.write(content)
    print(f"Generated AutoLISP: {lsp_path}")


def build_import_3d_script():
    scr_path = "cad/autocad/import_3d_enclosure.scr"
    # AutoCAD script to import 3D solid STEP files
    base_step = os.path.abspath("cad/solidworks/CO_Enclosure_Chassis_Base.step").replace("\\", "/")
    front_step = os.path.abspath("cad/solidworks/CO_Enclosure_Front_Cover.step").replace("\\", "/")
    brk_step   = os.path.abspath("cad/solidworks/CO_Enclosure_Wall_Bracket.step").replace("\\", "/")

    content = f"""; AutoCAD Mechanical Script: Import 3D Solid Enclosure Components
; Usage: In AutoCAD Mechanical, type SCRIPT and select this file.

; 1. Set 3D View to Isometric
VPOINT 1,-1,1

; 2. Import Wall Mount Bracket Solid
IMPORT "{brk_step}"

; 3. Import Rear Chassis Base Solid
IMPORT "{base_step}"

; 4. Import Front Housing Cover Solid
IMPORT "{front_step}"

; 5. Set Visual Style to Shaded with Edges
VSMINCURRENT SHADEDWITHEDGES

; 6. Zoom Extents
ZOOM E
"""
    with open(scr_path, "w", encoding="ascii") as f:
        f.write(content)
    print(f"Generated AutoCAD Script: {scr_path}")


if __name__ == "__main__":
    build_drawing()
    build_autolisp_script()
    build_import_3d_script()
    print("\nAll AutoCAD Mechanical deliverables successfully generated in cad/autocad/!")
