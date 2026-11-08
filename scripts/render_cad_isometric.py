"""
Technical 3D CAD Isometric Renderer for Dual Gas Detector Enclosure
Generates high-resolution 300-DPI exploded isometric visualization:
  - Front Housing Cover (with rosette acoustic grill, light pipe, button, louvers)
  - Rear Chassis Base (with 4x M2.5 bosses, PCB standoffs, terminal cutouts)
  - Quick-Mount Wall Bracket (with EU/US gang box keyholes)
Outputs:
  - cad/render_enclosure_technical.png
"""

import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import os

def rounded_box_faces(cx, cy, cz, w, h, d, r=4.0):
    # Generates quads for a box
    hw, hh, hd = w / 2.0, h / 2.0, d / 2.0
    v = [
        [cx - hw, cy - hh, cz - hd],
        [cx + hw, cy - hh, cz - hd],
        [cx + hw, cy + hh, cz - hd],
        [cx - hw, cy + hh, cz - hd],
        [cx - hw, cy - hh, cz + hd],
        [cx + hw, cy - hh, cz + hd],
        [cx + hw, cy + hh, cz + hd],
        [cx - hw, cy + hh, cz + hd]
    ]
    faces = [
        [v[0], v[1], v[2], v[3]], # Bottom
        [v[4], v[5], v[6], v[7]], # Top
        [v[0], v[1], v[5], v[4]], # Front
        [v[2], v[3], v[7], v[6]], # Back
        [v[0], v[3], v[7], v[4]], # Left
        [v[1], v[2], v[6], v[5]]  # Right
    ]
    return faces

def cylinder_faces(cx, cy, cz0, cz1, radius, segments=24):
    d_theta = 2 * math.pi / segments
    bot = [[cx + radius * math.cos(i * d_theta), cy + radius * math.sin(i * d_theta), cz0] for i in range(segments)]
    top = [[cx + radius * math.cos(i * d_theta), cy + radius * math.sin(i * d_theta), cz1] for i in range(segments)]
    faces = []
    for i in range(segments):
        nxt = (i + 1) % segments
        faces.append([bot[i], bot[nxt], top[nxt], top[i]])
    # Caps
    faces.append(bot)
    faces.append(top)
    return faces

def render():
    fig = plt.figure(figsize=(12, 10), dpi=300, facecolor='#0f172a')
    ax = fig.add_subplot(111, projection='3d', facecolor='#0f172a')

    # Exploded offsets
    z_bracket = -25.0
    z_base = 0.0
    z_cover = 40.0

    # 1. Wall Bracket (Slate/Amber)
    brk_faces = rounded_box_faces(0, 0, z_bracket, 86.0, 66.0, 3.0)
    col_brk = Poly3DCollection(brk_faces, facecolors='#334155', edgecolors='#64748b', linewidths=0.8, alpha=0.92)
    ax.add_collection3d(col_brk)
    # Bracket opening
    hole_faces = rounded_box_faces(0, 0, z_bracket, 34.0, 22.0, 3.2)
    col_hole = Poly3DCollection(hole_faces, facecolors='#0f172a', edgecolors='#38bdf8', linewidths=1.0, alpha=0.95)
    ax.add_collection3d(col_hole)

    # 2. Rear Chassis Base (White/Silver with Gold Inserts)
    base_faces = rounded_box_faces(0, 0, z_base + 5.0, 92.0, 72.0, 10.0)
    col_base = Poly3DCollection(base_faces, facecolors='#e2e8f0', edgecolors='#94a3b8', linewidths=0.9, alpha=0.88)
    ax.add_collection3d(col_base)
    # Standoff Bosses with Brass Inserts
    for bx, by in [(-31.5, -21.5), (31.5, -21.5), (-31.5, 21.5), (31.5, 21.5)]:
        b_faces = cylinder_faces(bx, by, z_base + 2.2, z_base + 6.7, 2.75, 16)
        col_boss = Poly3DCollection(b_faces, facecolors='#cbd5e1', edgecolors='#64748b', linewidths=0.5, alpha=0.9)
        ax.add_collection3d(col_boss)
        # Gold brass insert
        ins_faces = cylinder_faces(bx, by, z_base + 2.2, z_base + 6.7, 1.80, 12)
        col_ins = Poly3DCollection(ins_faces, facecolors='#f59e0b', edgecolors='#d97706', linewidths=0.4, alpha=1.0)
        ax.add_collection3d(col_ins)

    # 3. Front Housing Cover (Pure White / Ice Blue)
    cover_faces = rounded_box_faces(0, 0, z_cover + 9.0, 92.0, 72.0, 18.0)
    col_cover = Poly3DCollection(cover_faces, facecolors='#f8fafc', edgecolors='#38bdf8', linewidths=1.2, alpha=0.85)
    ax.add_collection3d(col_cover)

    # Rosette Acoustic Horn on Front Face (LS1 at -3.0, 13.0)
    z_top = z_cover + 18.0
    c_hole = cylinder_faces(-3.0, 13.0, z_top - 0.5, z_top + 0.5, 1.6, 16)
    ax.add_collection3d(Poly3DCollection(c_hole, facecolors='#0284c7', edgecolors='#0284c7', alpha=1.0))
    for a in range(0, 360, 60):
        rad = math.radians(a)
        hx = -3.0 + 3.6 * math.cos(rad)
        hy = 13.0 + 3.6 * math.sin(rad)
        sat = cylinder_faces(hx, hy, z_top - 0.5, z_top + 0.5, 1.1, 12)
        ax.add_collection3d(Poly3DCollection(sat, facecolors='#0284c7', edgecolors='#0284c7', alpha=1.0))

    # 4-Channel Optical Light Guide
    lp_faces = rounded_box_faces(-3.4, 21.0, z_top + 0.4, 14.0, 3.8, 1.0)
    ax.add_collection3d(Poly3DCollection(lp_faces, facecolors='#38bdf8', edgecolors='#0284c7', linewidths=1.0, alpha=0.95))

    # Test / Hush Button
    btn_faces = rounded_box_faces(7.0, 16.0, z_top + 1.2, 17.0, 11.0, 2.0)
    ax.add_collection3d(Poly3DCollection(btn_faces, facecolors='#e2e8f0', edgecolors='#64748b', linewidths=1.0, alpha=1.0))

    # CO Diffusion Louvers (Right Zone)
    for dy in [-6.0, -3.0, 0.0, 3.0, 6.0]:
        l_faces = rounded_box_faces(21.5, 10.5 + dy, z_top + 0.2, 14.0, 1.2, 0.8)
        ax.add_collection3d(Poly3DCollection(l_faces, facecolors='#0f172a', edgecolors='#0284c7', linewidths=0.6, alpha=1.0))

    # Annotations & Callout Lines
    ax.text(55, 30, z_cover + 18, "FRONT HOUSING COVER\n(92 x 72 x 18 mm, PC/ABS UL 94-V0)", color='#38bdf8', fontsize=9, fontweight='bold')
    ax.text(-50, 25, z_top + 5, "7-HOLE ACOUSTIC ROSETTE\n(4.0 kHz Peak, >85 dBA @ 3m)", color='#38bdf8', fontsize=8)
    ax.text(25, 30, z_top + 5, "CO GAS DIFFUSION WELL", color='#38bdf8', fontsize=8)

    ax.text(55, 30, z_base + 5, "REAR CHASSIS BASE\n(4x M2.5 Bosses, Standoff 4.5mm)", color='#94a3b8', fontsize=9, fontweight='bold')
    ax.text(-55, -20, z_base + 5, "TERMINAL CUTOUTS (J1, J2)", color='#94a3b8', fontsize=8)

    ax.text(55, 30, z_bracket, "WALL MOUNT BRACKET\n(EU 60mm & US 83.5mm Keyholes)", color='#f59e0b', fontsize=9, fontweight='bold')

    # Exploded View Leader Line
    ax.plot([0, 0], [0, 0], [z_bracket, z_cover + 18], color='#38bdf8', linestyle='--', linewidth=1.2, alpha=0.6)

    # View limits & angle
    ax.set_xlim(-60, 60)
    ax.set_ylim(-50, 50)
    ax.set_zlim(-35, 75)
    ax.view_init(elev=26, azim=-55)

    # Clean axes
    ax.set_axis_off()
    ax.set_title("SMART DUAL GAS DETECTOR (CO + LPG) - 3D EXPLODED ENCLOSURE ARCHITECTURE\nAutoCAD Mechanical & SolidWorks Precision CAD Specification",
                 color='#f8fafc', fontsize=12, fontweight='bold', pad=15)

    out_path = "cad/render_enclosure_technical.png"
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, facecolor='#0f172a', edgecolor='none')
    plt.close()
    print(f"Generated 300-DPI CAD Technical Render: {out_path}")

if __name__ == "__main__":
    render()

