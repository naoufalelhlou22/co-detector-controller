"""
High-Precision Binary STL Mesh Generator for Smart Dual Gas Detector Enclosure
Generates:
  1. cad/stl/co_detector_rear_chassis.stl
  2. cad/stl/co_detector_front_cover.stl
  3. cad/stl/co_detector_wall_bracket.stl
  4. cad/stl/co_detector_light_pipe.stl
  5. cad/stl/co_detector_test_button.stl
"""

import math
import struct
import os

class STLMesh:
    def __init__(self, name="solid"):
        self.name = name
        self.triangles = [] # list of ((nx, ny, nz), (v1x, v1y, v1z), (v2x, v2y, v2z), (v3x, v3y, v3z))

    def add_triangle(self, p1, p2, p3):
        # Calculate normal vector
        ax, ay, az = p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]
        bx, by, bz = p3[0] - p1[0], p3[1] - p1[1], p3[2] - p1[2]
        nx = ay * bz - az * by
        ny = az * bx - ax * bz
        nz = ax * by - ay * bx
        length = math.sqrt(nx*nx + ny*ny + nz*nz)
        if length > 1e-9:
            normal = (nx/length, ny/length, nz/length)
        else:
            normal = (0.0, 0.0, 1.0)
        self.triangles.append((normal, p1, p2, p3))

    def add_quad(self, p1, p2, p3, p4):
        # p1 -> p2 -> p3 -> p4 counter-clockwise
        self.add_triangle(p1, p2, p3)
        self.add_triangle(p1, p3, p4)

    def add_box(self, x0, y0, z0, x1, y1, z1):
        # 6 faces
        # Bottom (z0)
        self.add_quad((x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0))
        # Top (z1)
        self.add_quad((x0, y0, z1), (x0, y1, z1), (x1, y1, z1), (x1, y0, z1))
        # Front (y0)
        self.add_quad((x0, y0, z0), (x0, y0, z1), (x1, y0, z1), (x1, y0, z0))
        # Back (y1)
        self.add_quad((x1, y1, z0), (x1, y1, z1), (x0, y1, z1), (x0, y1, z0))
        # Left (x0)
        self.add_quad((x0, y1, z0), (x0, y1, z1), (x0, y0, z1), (x0, y0, z0))
        # Right (x1)
        self.add_quad((x1, y0, z0), (x1, y0, z1), (x1, y1, z1), (x1, y1, z0))

    def add_cylinder(self, cx, cy, z0, z1, radius, segments=32):
        d_theta = 2 * math.pi / segments
        pts_bot = [(cx + radius * math.cos(i * d_theta), cy + radius * math.sin(i * d_theta), z0) for i in range(segments)]
        pts_top = [(cx + radius * math.cos(i * d_theta), cy + radius * math.sin(i * d_theta), z1) for i in range(segments)]
        c_bot = (cx, cy, z0)
        c_top = (cx, cy, z1)

        for i in range(segments):
            next_i = (i + 1) % segments
            # Side quad
            self.add_quad(pts_bot[i], pts_bot[next_i], pts_top[next_i], pts_top[i])
            # Bottom fan
            self.add_triangle(c_bot, pts_bot[next_i], pts_bot[i])
            # Top fan
            self.add_triangle(c_top, pts_top[i], pts_top[next_i])

    def add_hollow_cylinder(self, cx, cy, z0, z1, r_outer, r_inner, segments=32):
        d_theta = 2 * math.pi / segments
        outer_bot = [(cx + r_outer * math.cos(i * d_theta), cy + r_outer * math.sin(i * d_theta), z0) for i in range(segments)]
        outer_top = [(cx + r_outer * math.cos(i * d_theta), cy + r_outer * math.sin(i * d_theta), z1) for i in range(segments)]
        inner_bot = [(cx + r_inner * math.cos(i * d_theta), cy + r_inner * math.sin(i * d_theta), z0) for i in range(segments)]
        inner_top = [(cx + r_inner * math.cos(i * d_theta), cy + r_inner * math.sin(i * d_theta), z1) for i in range(segments)]

        for i in range(segments):
            next_i = (i + 1) % segments
            # Outer wall
            self.add_quad(outer_bot[i], outer_bot[next_i], outer_top[next_i], outer_top[i])
            # Inner wall
            self.add_quad(inner_bot[next_i], inner_bot[i], inner_top[i], inner_top[next_i])
            # Bottom rim
            self.add_quad(inner_bot[i], inner_bot[next_i], outer_bot[next_i], outer_bot[i])
            # Top rim
            self.add_quad(inner_top[next_i], inner_top[i], outer_top[i], outer_top[next_i])

    def add_rounded_box_shell(self, cx, cy, length, width, h, wall, r, segments=16):
        # Generates a hollow enclosure shell with base floor and vertical curved walls
        hw = length / 2
        hh = width / 2
        ihw = hw - wall
        ihh = hh - wall
        ir = max(0.5, r - wall)

        # Base floor
        self.add_box(cx - hw, cy - hh, 0, cx + hw, cy + hh, wall)

        # 4 straight wall segments
        # Bottom wall (-Y)
        self.add_box(cx - hw + r, cy - hh, wall, cx + hw - r, cy - hh + wall, h)
        # Top wall (+Y)
        self.add_box(cx - hw + r, cy + hh - wall, wall, cx + hw - r, cy + hh, h)
        # Left wall (-X)
        self.add_box(cx - hw, cy - hh + r, wall, cx - hw + wall, cy + hh - r, h)
        # Right wall (+X)
        self.add_box(cx + hw - wall, cy - hh + r, wall, cx + hw, cy + hh - r, h)

        # 4 corner quadrants
        corners = [
            (cx + hw - r, cy + hh - r, 0),        # Top-Right: 0 to 90
            (cx - hw + r, cy + hh - r, math.pi/2),# Top-Left: 90 to 180
            (cx - hw + r, cy - hh + r, math.pi),  # Bottom-Left: 180 to 270
            (cx + hw - r, cy - hh + r, 3*math.pi/2) # Bottom-Right: 270 to 360
        ]
        for ccx, ccy, start_ang in corners:
            d_theta = (math.pi / 2) / segments
            for i in range(segments):
                a1 = start_ang + i * d_theta
                a2 = start_ang + (i + 1) * d_theta
                ob1 = (ccx + r * math.cos(a1), ccy + r * math.sin(a1), wall)
                ob2 = (ccx + r * math.cos(a2), ccy + r * math.sin(a2), wall)
                ot1 = (ob1[0], ob1[1], h)
                ot2 = (ob2[0], ob2[1], h)
                ib1 = (ccx + ir * math.cos(a1), ccy + ir * math.sin(a1), wall)
                ib2 = (ccx + ir * math.cos(a2), ccy + ir * math.sin(a2), wall)
                it1 = (ib1[0], ib1[1], h)
                it2 = (ib2[0], ib2[1], h)
                # Outer face
                self.add_quad(ob1, ob2, ot2, ot1)
                # Inner face
                self.add_quad(ib2, ib1, it1, it2)
                # Top rim
                self.add_quad(it1, it2, ot2, ot1)

    def write_binary(self, filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            # 80-byte header
            header = f"Smart Dual Gas Detector CAD Part - {self.name}".encode('ascii')[:80]
            header = header.ljust(80, b'\0')
            f.write(header)
            # Triangle count
            f.write(struct.pack('<I', len(self.triangles)))
            # Triangles
            for normal, p1, p2, p3 in self.triangles:
                f.write(struct.pack('<3f', *normal))
                f.write(struct.pack('<3f', *p1))
                f.write(struct.pack('<3f', *p2))
                f.write(struct.pack('<3f', *p3))
                f.write(struct.pack('<H', 0))
        print(f"Generated STL: {filepath} ({len(self.triangles)} triangles, {os.path.getsize(filepath):,} bytes)")


def build_rear_chassis():
    m = STLMesh("rear_chassis_base")
    # Base shell: 92 x 72 x 10mm, wall = 2.2mm, R = 10mm
    m.add_rounded_box_shell(0, 0, 92.0, 72.0, 10.0, 2.2, 10.0)
    
    # 4x PCB Mounting Bosses (at +/-31.5, +/-21.5), standoff height = 4.5mm (Z from 2.2 to 6.7)
    boss_coords = [(-31.5, -21.5), (31.5, -21.5), (-31.5, 21.5), (31.5, 21.5)]
    for bx, by in boss_coords:
        m.add_hollow_cylinder(bx, by, 2.2, 6.7, 2.75, 1.80, segments=24) # OD=5.5, ID=3.6
        # 3x Gusset ribs
        for ang in [0, 120, 240]:
            rad = math.radians(ang)
            gx = bx + 4.2 * math.cos(rad)
            gy = by + 4.2 * math.sin(rad)
            m.add_box(min(bx, gx) - 0.6, min(by, gy) - 0.6, 2.2, max(bx, gx) + 0.6, max(by, gy) + 0.6, 5.2)

    # 4x Bayonet docking lugs on bottom
    for lx, ly in [(-30, -20), (30, -20), (-30, 20), (30, 20)]:
        m.add_cylinder(lx, ly, -2.5, 0.0, 3.2, segments=20)
        m.add_cylinder(lx, ly, -4.2, -2.5, 4.4, segments=20)

    m.write_binary("cad/stl/co_detector_rear_chassis.stl")


def build_front_cover():
    m = STLMesh("front_housing_cover")
    # Inverted front cover shell: 92 x 72 x 18mm, wall = 2.2mm, R = 10mm
    m.add_rounded_box_shell(0, 0, 92.0, 72.0, 18.0, 2.2, 10.0)

    # Ceiling top cap
    m.add_box(-44.0, -34.0, 15.8, 44.0, 34.0, 18.0)

    # Acoustic Shroud for LS1 Buzzer (at -3.0, 13.0, from Z=10 to Z=15.8)
    m.add_hollow_cylinder(-3.0, 13.0, 10.0, 15.8, 7.0, 5.5, segments=24)

    # Internal Thermal & Gas Barrier Rib (at X = 17.0, spanning Y from -33 to +33, from Z=6 to Z=15.8)
    m.add_box(16.3, -33.0, 6.0, 17.7, 33.0, 15.8)

    # Sensor well support rim for Winsen ME3-CO (at 21.5, 10.5)
    m.add_hollow_cylinder(21.5, 10.5, 13.0, 15.8, 10.5, 9.5, segments=24)

    m.write_binary("cad/stl/co_detector_front_cover.stl")


def build_wall_bracket():
    m = STLMesh("wall_mount_bracket")
    # Base plate: 86 x 66 x 3mm, R = 8mm
    m.add_box(-43.0, -33.0, 0, 43.0, 33.0, 3.0)

    # Central wire pass-through rim
    m.add_hollow_cylinder(0, 0, 0, 4.5, 16.0, 12.0, segments=32)

    # Bubble level alignment socket
    m.add_hollow_cylinder(0, 22.0, 0, 4.0, 4.8, 4.0, segments=20)

    # 4x Sliding lock wedges
    for lx, ly in [(-30, -20), (30, -20), (-30, 20), (30, 20)]:
        m.add_hollow_cylinder(lx, ly, 3.0, 6.0, 5.0, 3.5, segments=20)

    m.write_binary("cad/stl/co_detector_wall_bracket.stl")


def build_light_pipe():
    m = STLMesh("optical_light_pipe_4ch")
    # Common runner bar
    m.add_box(-9.5, 19.7, 5.0, 2.7, 22.3, 7.2)
    # 4 cylindrical light guides
    led_x = [-8.20, -5.00, -1.80, 1.40]
    for lx in led_x:
        m.add_cylinder(lx, 21.0, 0.0, 7.2, 1.0, segments=20)
        # Convex gathering lens on bottom
        m.add_cylinder(lx, 21.0, -0.4, 0.0, 1.15, segments=20)

    m.write_binary("cad/stl/co_detector_light_pipe.stl")


def build_test_button():
    m = STLMesh("button_actuator_cap")
    # Tactile button cap: 17.0 x 11.0 x 2.5mm
    m.add_box(-1.5, 10.5, 0.0, 15.5, 21.5, 2.5)
    # Plunger contacting SW1 (at 7.0, 19.0)
    m.add_cylinder(7.0, 19.0, -3.5, 0.0, 1.5, segments=16)
    # Plunger contacting SW2 (at 7.0, 13.0)
    m.add_cylinder(7.0, 13.0, -3.5, 0.0, 1.5, segments=16)

    m.write_binary("cad/stl/co_detector_test_button.stl")


if __name__ == "__main__":
    build_rear_chassis()
    build_front_cover()
    build_wall_bracket()
    build_light_pipe()
    build_test_button()
    print("All 5 enclosure STL models successfully generated in cad/stl/!")

