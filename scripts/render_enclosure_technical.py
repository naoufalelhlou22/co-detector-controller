"""
Master Technical Blueprint & Multi-View Engineering Graphic Generator - Rev 4.0
Produces: cad/render_enclosure_technical.png (High-Res 300 DPI 4-View Engineering Blueprint)
Rev 4.0: Figaro TGS2610-C00 LPG Detector with 1100mAh LiPo Battery Pocket (52x36x7.5mm), Zero-Collision Apertures.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os


def draw_rounded_rect(ax, cx, cy, w, h, r, edgecolor='white', facecolor='none', lw=1.5, ls='-', zorder=2, alpha=1.0):
    x0, y0 = cx - w / 2.0, cy - h / 2.0
    rect = patches.FancyBboxPatch(
        (x0, y0), w, h,
        boxstyle=f"round,pad=0,rounding_size={r}",
        edgecolor=edgecolor, facecolor=facecolor,
        linewidth=lw, linestyle=ls, zorder=zorder, alpha=alpha
    )
    ax.add_patch(rect)
    return rect


def generate_technical_blueprint():
    fig = plt.figure(figsize=(19.2, 10.8), dpi=200, facecolor='#0b0f17')
    gs = fig.add_gridspec(2, 2, left=0.06, right=0.96, bottom=0.08, top=0.92, wspace=0.18, hspace=0.22)

    c_blue   = '#38bdf8'
    c_white  = '#f8fafc'
    c_ghost  = '#94a3b8'
    c_accent = '#f59e0b'
    c_pcb    = '#10b981'
    c_red    = '#ef4444'
    c_dim    = '#34d399'

    # =========================================================================
    # VIEW 1: FRONT COVER EXTERIOR (Top-Left)
    # =========================================================================
    ax1 = fig.add_subplot(gs[0, 0], facecolor='#111827')
    ax1.set_title("VIEW A: FRONT COVER (EXTERIOR TOP PLAN - REV 4.0) [SCALE 1:1]", color=c_blue, fontsize=12, fontweight='bold', pad=10)
    ax1.set_xlim(-15, 85)
    ax1.set_ylim(-15, 65)
    ax1.set_aspect('equal')
    ax1.grid(True, color='#1f2937', linestyle='--', linewidth=0.6, alpha=0.7)

    # PCB Origin Datum Marker (0,0)
    ax1.scatter([0], [0], color=c_red, s=60, zorder=10, marker='+')
    ax1.text(-2, -3.5, "DATUM (0,0)\nPCB CORNER", color=c_red, fontsize=7, fontweight='bold', ha='right')

    # Outer squircle: 86.0 x 66.0, R = 8.0, center (35.0, 25.0)
    draw_rounded_rect(ax1, 35.0, 25.0, 86.0, 66.0, 8.0, edgecolor=c_white, facecolor='#1e293b', lw=2.0)
    draw_rounded_rect(ax1, 35.0, 25.0, 82.0, 62.0, 6.0, edgecolor='#475569', lw=1.0)
    draw_rounded_rect(ax1, 35.0, 25.0, 70.0, 50.0, 3.0, edgecolor=c_pcb, lw=1.2, ls='--', alpha=0.8)

    # 1. 0.96" OLED Window: (42.00, 25.00), 25 x 14 mm
    draw_rounded_rect(ax1, 42.00, 25.00, 25.0, 14.0, 1.5, edgecolor=c_blue, facecolor='#0284c7', alpha=0.3, lw=1.8)
    draw_rounded_rect(ax1, 42.00, 25.00, 21.7, 10.8, 0.5, edgecolor='#38bdf8', facecolor='#0369a1', alpha=0.5, lw=1.0)
    ax1.text(42.00, 25.00, "0.96\" OLED\n(42.0, 25.0)", color=c_white, fontsize=7, fontweight='bold', ha='center', va='center')

    # 2. Tactile Buttons SW1 & SW2 at Y = 13.00
    # SW2 (Hush): (35.0, 13.0)
    circle_sw2 = patches.Circle((35.00, 13.00), 2.75, edgecolor='#60a5fa', facecolor='#2563eb', lw=1.5)
    ax1.add_patch(circle_sw2)
    ax1.text(35.00, 13.00, "HUSH", color=c_white, fontsize=6, fontweight='bold', ha='center', va='center')

    # SW1 (Test): (45.0, 13.0)
    circle_sw1 = patches.Circle((45.00, 13.00), 2.75, edgecolor='#60a5fa', facecolor='#2563eb', lw=1.5)
    ax1.add_patch(circle_sw1)
    ax1.text(45.00, 13.00, "TEST", color=c_white, fontsize=6, fontweight='bold', ha='center', va='center')

    # 3. 4 Status LEDs at Y = 4.00
    led_info = [(28.0, c_pcb, 'PWR'), (34.0, '#34d399', 'LPG'), (40.0, c_red, 'ALM'), (46.0, '#60a5fa', 'WIFI')]
    for lx, col, lbl in led_info:
        c_led = patches.Circle((lx, 4.00), 1.1, edgecolor=col, facecolor=col, lw=1.2)
        ax1.add_patch(c_led)
        ax1.text(lx, 1.2, lbl, color=col, fontsize=5.5, fontweight='bold', ha='center')

    # 4. Buzzer Rosette LS1: (60.00, 16.00)
    bz_outer = patches.Circle((60.00, 16.00), 6.1, edgecolor='#64748b', facecolor='none', lw=1.0, ls=':')
    ax1.add_patch(bz_outer)
    bz_center = patches.Circle((60.00, 16.00), 1.25, edgecolor=c_white, facecolor='#475569', lw=1.0)
    ax1.add_patch(bz_center)
    for a in range(0, 360, 60):
        rad = np.radians(a)
        hx = 60.00 + 3.2 * np.cos(rad)
        hy = 16.00 + 3.2 * np.sin(rad)
        ax1.add_patch(patches.Circle((hx, hy), 0.90, edgecolor=c_white, facecolor='#475569', lw=0.8))
    ax1.text(60.00, 22.5, "ROSETTE HORN\n(60.0, 16.0)", color=c_ghost, fontsize=6, ha='center')

    # 5. S2 LPG Convection Chimney: (60.00, 37.00)
    lpg_c = patches.Circle((60.00, 37.00), 5.5, edgecolor=c_accent, facecolor='#78350f', alpha=0.4, lw=1.8)
    ax1.add_patch(lpg_c)
    ax1.text(60.00, 37.00, "LPG CHIMNEY\n(60.0, 37.0)", color=c_accent, fontsize=6.5, fontweight='bold', ha='center', va='center')

    # Dimensions
    ax1.annotate("", xy=(-8.0, 58.0), xytext=(78.0, 58.0), arrowprops=dict(arrowstyle="<->", color=c_dim, lw=1.2))
    ax1.text(35.0, 60.0, "86.00 mm", color=c_dim, fontsize=8, fontweight='bold', ha='center')
    ax1.annotate("", xy=(78.0, -8.0), xytext=(78.0, 58.0), arrowprops=dict(arrowstyle="<->", color=c_dim, lw=1.2))
    ax1.text(82.0, 25.0, "66.00 mm", color=c_dim, fontsize=8, fontweight='bold', va='center', rotation=-90)

    # =========================================================================
    # VIEW 2: LOWER CHASSIS BASE INTERIOR (Top-Right)
    # =========================================================================
    ax2 = fig.add_subplot(gs[0, 1], facecolor='#111827')
    ax2.set_title("VIEW B: LOWER CHASSIS BASE (INTERNAL PLAN) [SCALE 1:1]", color=c_blue, fontsize=12, fontweight='bold', pad=10)
    ax2.set_xlim(-15, 85)
    ax2.set_ylim(-15, 65)
    ax2.set_aspect('equal')
    ax2.grid(True, color='#1f2937', linestyle='--', linewidth=0.6, alpha=0.7)

    # Outer wall and cavity
    draw_rounded_rect(ax2, 35.0, 25.0, 86.0, 66.0, 8.0, edgecolor=c_white, facecolor='#1e293b', lw=2.0)
    draw_rounded_rect(ax2, 35.0, 25.0, 81.2, 61.2, 5.6, edgecolor='#64748b', facecolor='#0f172a', lw=1.2)
    draw_rounded_rect(ax2, 35.0, 25.0, 70.0, 50.0, 3.0, edgecolor=c_pcb, lw=1.0, ls=':', alpha=0.6)

    # Internal Battery Pocket (52 x 36 x 7.5 mm)
    draw_rounded_rect(ax2, 35.0, 25.0, 52.0, 36.0, 3.0, edgecolor=c_accent, facecolor='#78350f', alpha=0.3, lw=1.5)
    ax2.text(35.0, 25.0, "INTERNAL BATTERY BAY\n52 x 36 x 7.5 mm\n(1100mAh LiPo)", color=c_accent, fontsize=7, fontweight='bold', ha='center', va='center')

    # 4x Standoff Bosses H1, H2, H3, H4
    bosses = [("H1", 3.5, 3.5), ("H2", 66.5, 3.5), ("H3", 3.5, 46.5), ("H4", 66.5, 46.5)]
    for bname, bx, by in bosses:
        ax2.add_patch(patches.Circle((bx, by), 3.0, edgecolor=c_white, facecolor='#334155', lw=1.2))
        ax2.add_patch(patches.Circle((bx, by), 1.8, edgecolor=c_accent, facecolor=c_accent, lw=1.0))
        ax2.text(bx + (3.5 if bx < 35 else -3.5), by, f"{bname} M2.5", color=c_accent, fontsize=6.5,
                 fontweight='bold', ha='left' if bx < 35 else 'right', va='center')

    # Left Wall Cutout: J1 (12V IN ONLY)
    ax2.add_patch(patches.Rectangle((-8.0, 32.5), 4.8, 11.0, edgecolor=c_accent, facecolor='#b45309', lw=1.2))
    ax2.text(-10.0, 38.0, "J1 (12V IN)", color=c_accent, fontsize=6.5, fontweight='bold', ha='right', va='center')

    # SW3 (RESET PINHOLE)
    ax2.add_patch(patches.Circle((-5.6, 20.0), 1.25, edgecolor=c_red, facecolor=c_red, lw=1.0))
    ax2.text(-10.0, 20.0, "SW3 (RST)", color=c_red, fontsize=6.5, fontweight='bold', ha='right', va='center')

    # =========================================================================
    # VIEW 3: CROSS-SECTION A-A (Bottom-Left)
    # =========================================================================
    ax3 = fig.add_subplot(gs[1, 0], facecolor='#111827')
    ax3.set_title("SECTION A-A: INTERNAL ELEVATION (Z-STACKUP WITH BATTERY) [SCALE 1:1]", color=c_blue, fontsize=12, fontweight='bold', pad=10)
    ax3.set_xlim(-15, 85)
    ax3.set_ylim(-8, 35)
    ax3.set_aspect('equal')
    ax3.grid(True, color='#1f2937', linestyle='--', linewidth=0.6, alpha=0.7)

    # Base profile: Z = 0 to 12 mm
    ax3.add_patch(patches.Rectangle((-8.0, 0.0), 86.0, 12.0, edgecolor=c_white, facecolor='#1e293b', lw=1.5))
    ax3.add_patch(patches.Rectangle((-5.6, 2.4), 81.2, 9.6, edgecolor='#475569', facecolor='#0f172a', lw=1.0))

    # Lower Battery Bay & Battery Cell: Z = 1.0 to 7.5 mm
    ax3.add_patch(patches.Rectangle((9.0, 1.0), 52.0, 7.5, edgecolor=c_accent, facecolor='#78350f', alpha=0.3, lw=1.2, ls='--'))
    ax3.add_patch(patches.Rectangle((10.0, 1.5), 50.0, 6.5, edgecolor='#f59e0b', facecolor='#d97706', alpha=0.7, lw=1.2))
    ax3.text(35.0, 4.8, "1100mAh LiPo PACK (50 x 34 x 6.5 mm)", color=c_white, fontsize=6.5, fontweight='bold', ha='center', va='center')

    # Cover profile: Z = 12 to 28 mm
    ax3.add_patch(patches.Rectangle((-8.0, 12.0), 86.0, 16.0, edgecolor=c_white, facecolor='#334155', alpha=0.9, lw=1.5))
    ax3.add_patch(patches.Rectangle((-5.6, 12.0), 81.2, 13.6, edgecolor='#475569', facecolor='#0f172a', lw=1.0))

    # Parting Line Indicator
    ax3.axhline(12.0, color='#38bdf8', linestyle='-.', lw=1.2)
    ax3.text(80.0, 12.0, "PARTING LINE (Z=12)", color='#38bdf8', fontsize=7, va='center')

    # PCB Board: Z = 9.5 to 11.1 mm (Mounted on standoffs above battery)
    ax3.add_patch(patches.Rectangle((0.0, 9.5), 70.0, 1.6, edgecolor=c_pcb, facecolor='#065f46', lw=1.5))
    ax3.text(35.0, 10.3, "PCBA 4-LAYER (70x50x1.6 mm)", color=c_white, fontsize=7, fontweight='bold', ha='center', va='center')

    # Standoffs: Z = 2.4 to 9.5 mm
    ax3.add_patch(patches.Rectangle((2.0, 2.4), 3.0, 7.1, edgecolor=c_accent, facecolor=c_accent, lw=1.0))
    ax3.add_patch(patches.Rectangle((65.0, 2.4), 3.0, 7.1, edgecolor=c_accent, facecolor=c_accent, lw=1.0))
    ax3.text(3.5, 6.0, "H1", color='#000', fontsize=6, fontweight='bold', ha='center', va='center')
    ax3.text(66.5, 6.0, "H2", color='#000', fontsize=6, fontweight='bold', ha='center', va='center')

    # OLED Screen Module: Z = 18.0 to 25.6 mm
    ax3.add_patch(patches.Rectangle((29.5, 18.0), 25.0, 7.6, edgecolor='#60a5fa', facecolor='#1e3a8a', alpha=0.7, lw=1.2))
    ax3.text(42.0, 21.8, "0.96\" OLED MODULE", color=c_white, fontsize=6.5, fontweight='bold', ha='center', va='center')

    # Figaro TGS2610 LPG Sensor: Z = 11.1 to 20.3 mm (H = 9.2 mm)
    ax3.add_patch(patches.Rectangle((55.4, 11.1), 9.2, 9.2, edgecolor=c_accent, facecolor='#b45309', alpha=0.7, lw=1.2))
    ax3.text(60.0, 15.7, "TGS2610", color=c_white, fontsize=6, fontweight='bold', ha='center', va='center')

    # Total Depth Dimension: 28.00 mm
    ax3.annotate("", xy=(-11.0, 0.0), xytext=(-11.0, 28.0), arrowprops=dict(arrowstyle="<->", color=c_dim, lw=1.2))
    ax3.text(-13.0, 14.0, "28.00 mm", color=c_dim, fontsize=8, fontweight='bold', va='center', rotation=90)

    # =========================================================================
    # VIEW 4: DETACHABLE WALL BRACKET & BOM (Bottom-Right)
    # =========================================================================
    ax4 = fig.add_subplot(gs[1, 1], facecolor='#111827')
    ax4.set_title("VIEW D: WALL MOUNT BRACKET & SPECIFICATIONS", color=c_blue, fontsize=12, fontweight='bold', pad=10)
    ax4.set_xlim(-15, 85)
    ax4.set_ylim(-15, 65)
    ax4.set_aspect('equal')
    ax4.grid(True, color='#1f2937', linestyle='--', linewidth=0.6, alpha=0.7)

    # Wall Bracket: 76 x 56 mm, R = 6.0
    draw_rounded_rect(ax4, 35.0, 25.0, 76.0, 56.0, 6.0, edgecolor=c_accent, facecolor='#1e293b', lw=1.8)

    # 2x Keyhole Slots (pitch 60 mm)
    for ky in [-5.0, 55.0]:
        ax4.add_patch(patches.Circle((35.0, ky), 4.5, edgecolor=c_white, facecolor='#0f172a', lw=1.2))
        ax4.text(35.0, ky, "KEYHOLE", color=c_ghost, fontsize=5.5, ha='center', va='center')

    # Center Knockout: 22 x 16 mm
    draw_rounded_rect(ax4, 35.0, 25.0, 22.0, 16.0, 3.0, edgecolor='#64748b', facecolor='#0f172a', lw=1.2)
    ax4.text(35.0, 25.0, "CABLE\nENTRY", color=c_ghost, fontsize=6, fontweight='bold', ha='center', va='center')

    # Production Specs Block
    spec_text = (
        "REV 4.0 MANUFACTURING SPECIFICATIONS:\n"
        "• Gas Target: LPG (Propane / Butane) via Figaro TGS2610-C00\n"
        "• Battery Backup: 1100mAh 3.7V LiPo (3.5 - 5.5 Hours Runtime)\n"
        "• Charger: TP4056 Smart CC/CV (Auto Cutoff @ 4.20V)\n"
        "• BMS Protection: DW01A + FS8205A Dual N-MOSFET\n"
        "• Power Path: Instant AO3401A P-MOSFET Switchover\n"
        "• Material: Sabic Cycoloy FR15 (PC/ABS), UL94 V-0\n"
        "• Ingress: IP52 Dust/Splash | Audio: TDK PS1240 85dB"
    )
    ax4.text(-12.0, -12.0, spec_text, color=c_white, fontsize=7.0, linespacing=1.4,
             bbox=dict(boxstyle='round,pad=0.5', facecolor='#0f172a', edgecolor='#334155', alpha=0.9))

    out_file = os.path.abspath("cad/render_enclosure_technical.png")
    plt.savefig(out_file, dpi=200, bbox_inches='tight', facecolor='#0b0f17')
    plt.close()
    print(f"[SUCCESS] Technical multi-view blueprint saved at: {out_file}")


if __name__ == '__main__':
    generate_technical_blueprint()
