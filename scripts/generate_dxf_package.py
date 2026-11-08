"""
Generate 2D Engineering DXF profiles for SolidWorks sketch import.
Profiles:
1. front_face_ui_cutouts.dxf (LEDs, speaker grill, vents, button)
2. pcb_mounting_boss_pattern.dxf (M2.5 bosses, board keepout, terminals)
3. wall_bracket_drilling_template.dxf (EU/US gang box keyholes, cable pass)
"""

import math
import os

class SimpleDXF:
    def __init__(self, filename):
        self.filename = filename
        self.entities = []

    def add_line(self, x1, y1, x2, y2, layer="0"):
        self.entities.append(f"0\nLINE\n8\n{layer}\n10\n{x1:.4f}\n20\n{y1:.4f}\n30\n0.0\n11\n{x2:.4f}\n21\n{y2:.4f}\n31\n0.0")

    def add_circle(self, cx, cy, r, layer="0"):
        self.entities.append(f"0\nCIRCLE\n8\n{layer}\n10\n{cx:.4f}\n20\n{cy:.4f}\n30\n0.0\n40\n{r:.4f}")

    def add_arc(self, cx, cy, r, start_ang, end_ang, layer="0"):
        self.entities.append(f"0\nARC\n8\n{layer}\n10\n{cx:.4f}\n20\n{cy:.4f}\n30\n0.0\n40\n{r:.4f}\n50\n{start_ang:.4f}\n51\n{end_ang:.4f}")

    def add_rect(self, x_min, y_min, x_max, y_max, layer="0"):
        self.add_line(x_min, y_min, x_max, y_min, layer)
        self.add_line(x_max, y_min, x_max, y_max, layer)
        self.add_line(x_max, y_max, x_min, y_max, layer)
        self.add_line(x_min, y_max, x_min, y_min, layer)

    def add_rounded_rect(self, cx, cy, w, h, r, layer="0"):
        x1 = cx - w/2 + r
        x2 = cx + w/2 - r
        y1 = cy - h/2 + r
        y2 = cy + h/2 - r
        # 4 straight segments
        self.add_line(x1, cy - h/2, x2, cy - h/2, layer)
        self.add_line(cx + w/2, y1, cx + w/2, y2, layer)
        self.add_line(x2, cy + h/2, x1, cy + h/2, layer)
        self.add_line(cx - w/2, y2, cx - w/2, y1, layer)
        # 4 corner arcs
        self.add_arc(x2, y1, r, 270, 360, layer)
        self.add_arc(x2, y2, r, 0, 90, layer)
        self.add_arc(x1, y2, r, 90, 180, layer)
        self.add_arc(x1, y1, r, 180, 270, layer)

    def save(self):
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        with open(self.filename, 'w', encoding='ascii') as f:
            f.write("0\nSECTION\n2\nHEADER\n0\nENDSEC\n")
            f.write("0\nSECTION\n2\nTABLES\n0\nTABLE\n2\nLAYER\n0\nLAYER\n2\n0\n70\n0\n62\n7\n6\nCONTINUOUS\n0\nENDTAB\n0\nENDSEC\n")
            f.write("0\nSECTION\n2\nENTITIES\n")
            for ent in self.entities:
                f.write(ent + "\n")
            f.write("0\nENDSEC\n0\nEOF\n")
        print(f"Generated: {self.filename}")


def generate_front_cutouts():
    dxf = SimpleDXF("cad/dxf/front_face_ui_cutouts.dxf")
    # Outer enclosure perimeter (92 x 72, R10)
    dxf.add_rounded_rect(0, 0, 92.0, 72.0, 10.0, layer="OUTLINE")
    # PCB keepout envelope (70 x 50)
    dxf.add_rect(-35.0, -25.0, 35.0, 25.0, layer="PCB_KEEPOUT")
    
    # 1. Acoustic horn grill (LS1 at -3.0, 13.0)
    ls1_x, ls1_y = -3.0, 13.0
    dxf.add_circle(ls1_x, ls1_y, 1.6, layer="ACOUSTIC_GRILL") # Center hole
    for a in range(0, 360, 60):
        rad = math.radians(a)
        hx = ls1_x + 3.6 * math.cos(rad)
        hy = ls1_y + 3.6 * math.sin(rad)
        dxf.add_circle(hx, hy, 1.1, layer="ACOUSTIC_GRILL")
    # Outer acoustic boundary reference
    dxf.add_circle(ls1_x, ls1_y, 6.1, layer="CONSTRUCTION")

    # 2. Status LED cluster (D4, D5, D6, D8)
    led_x = [-8.20, -5.00, -1.80, 1.40]
    led_y = 21.0
    for lx in led_x:
        dxf.add_circle(lx, led_y, 1.0, layer="LIGHT_PIPE")
    # Light pipe housing pocket
    dxf.add_rounded_rect((led_x[0] + led_x[3])/2, led_y, 14.0, 3.8, 1.2, layer="LIGHT_PIPE_POCKET")

    # 3. Test/Mute button aperture (at 7.0, 16.0)
    dxf.add_rounded_rect(7.0, 16.0, 18.0, 12.0, 2.5, layer="BUTTON_CUTOUT")

    # 4. CO sensor diffusion well (S1 at 21.5, 10.5)
    s1_x, s1_y = 21.5, 10.5
    dxf.add_circle(s1_x, s1_y, 10.0, layer="CONSTRUCTION") # ME3-CO boundary
    for dy in [-6.0, -3.0, 0.0, 3.0, 6.0]:
        dxf.add_rounded_rect(s1_x, s1_y + dy, 14.0, 1.2, 0.6, layer="CO_DIFFUSION_LOUVERS")

    # 5. LPG sensor chimney exhaust (S2 at 24.0, -18.5)
    s2_x, s2_y = 24.0, -18.5
    dxf.add_circle(s2_x, s2_y, 4.6, layer="CONSTRUCTION") # TGS2610 boundary
    for dx in [-8.0, -4.0, 0.0, 4.0, 8.0]:
        dxf.add_rounded_rect(s2_x + dx, 32.0, 2.0, 5.0, 1.0, layer="LPG_EXHAUST_VENTS")

    dxf.save()


def generate_pcb_boss_pattern():
    dxf = SimpleDXF("cad/dxf/pcb_mounting_boss_pattern.dxf")
    # Outer housing internal wall (87.6 x 67.6, R7.8)
    dxf.add_rounded_rect(0, 0, 87.6, 67.6, 7.8, layer="HOUSING_INNER_WALL")
    # PCB 70x50 outline
    dxf.add_rect(-35.0, -25.0, 35.0, 25.0, layer="PCB_OUTLINE")

    # 4x Boss locations with insert pilot hole and outer boss diameter
    boss_coords = [(-31.5, -21.5), (31.5, -21.5), (-31.5, 21.5), (31.5, 21.5)]
    for bx, by in boss_coords:
        dxf.add_circle(bx, by, 2.75, layer="BOSS_OD") # OD = 5.5mm
        dxf.add_circle(bx, by, 1.80, layer="INSERT_HOLE") # ID = 3.6mm for M2.5
        # Gusset reinforcement lines
        for ang in [0, 120, 240]:
            rad = math.radians(ang)
            gx = bx + 4.5 * math.cos(rad)
            gy = by + 4.5 * math.sin(rad)
            dxf.add_line(bx, by, gx, gy, layer="GUSSET_RIBS")

    # Terminal block cutouts on left wall
    dxf.add_rect(-46.0, -19.0, -43.8, -7.0, layer="TERMINAL_J1")
    dxf.add_rect(-46.0, 7.0, -43.8, 19.0, layer="TERMINAL_J2")

    # Thermal barrier rib footprint (X = 17.0)
    dxf.add_rect(16.3, -32.0, 17.7, 32.0, layer="THERMAL_BARRIER_RIB")

    dxf.save()


def generate_wall_bracket():
    dxf = SimpleDXF("cad/dxf/wall_bracket_drilling_template.dxf")
    # Bracket plate (86 x 66, R8)
    dxf.add_rounded_rect(0, 0, 86.0, 66.0, 8.0, layer="BRACKET_OUTLINE")

    # 1. EU Standard 60mm Junction Box Keyholes
    for kx in [-30.0, 30.0]:
        dxf.add_circle(kx, 0.0, 4.5, layer="EU_60MM_KEYHOLE")
        dxf.add_circle(kx, 4.5, 2.25, layer="EU_60MM_KEYHOLE")
        dxf.add_line(kx - 2.25, 0.0, kx - 2.25, 4.5, layer="EU_60MM_KEYHOLE")
        dxf.add_line(kx + 2.25, 0.0, kx + 2.25, 4.5, layer="EU_60MM_KEYHOLE")

    # 2. US Standard 83.5mm Gang Box Keyholes
    for ky in [-41.75, 41.75]:
        dxf.add_circle(0.0, ky, 4.5, layer="US_83_5MM_KEYHOLE")
        dxf.add_circle(4.5, ky, 2.25, layer="US_83_5MM_KEYHOLE")
        dxf.add_line(0.0, ky - 2.25, 4.5, ky - 2.25, layer="US_83_5MM_KEYHOLE")
        dxf.add_line(0.0, ky + 2.25, 4.5, ky + 2.25, layer="US_83_5MM_KEYHOLE")

    # 3. Central Wire Pass-Through (34 x 22, R4)
    dxf.add_rounded_rect(0, 0, 34.0, 22.0, 4.0, layer="WIRE_PASS_THROUGH")

    # 4. Bubble Level Vial Pocket (dia 8.4mm)
    dxf.add_circle(0, 22.0, 4.2, layer="BUBBLE_LEVEL_POCKET")

    # 5. 4x Bayonet Slide Tabs
    for tx, ty in [(-30, -20), (30, -20), (-30, 20), (30, 20)]:
        dxf.add_circle(tx, ty, 3.2, layer="BAYONET_LUG_LOCATORS")

    dxf.save()


if __name__ == "__main__":
    generate_front_cutouts()
    generate_pcb_boss_pattern()
    generate_wall_bracket()
    print("All DXF templates successfully generated in cad/dxf/!")

