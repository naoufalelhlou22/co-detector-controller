import math
import os

proj_dir = r"C:\Users\Mr_X\.gemini\antigravity\scratch\co_detector_controller"
models_dir = os.path.join(proj_dir, "3dmodels")
os.makedirs(models_dir, exist_ok=True)


U = 1.0 / 2.54  # KiCad VRML native unit is 0.1 inch (2.54 mm)


def vrml_cylinder_z(r: float, z0: float, z1: float, n: int = 48) -> str:
    """Return an IndexedFaceSet cylinder along the Z axis from z0 to z1 with radius r (in mm)."""
    r_u, z0_u, z1_u = r * U, z0 * U, z1 * U
    pts = []
    # Bottom ring: 0 .. n-1, Top ring: n .. 2n-1, Bottom center: 2n, Top center: 2n+1
    for z in (z0_u, z1_u):
        for i in range(n):
            ang = 2.0 * math.pi * i / n
            pts.append(f"{r_u * math.cos(ang):.5f} {r_u * math.sin(ang):.5f} {z:.5f}")
    pts.append(f"0.00000 0.00000 {z0_u:.5f}")
    pts.append(f"0.00000 0.00000 {z1_u:.5f}")

    faces = []
    # Side quads
    for i in range(n):
        nxt = (i + 1) % n
        faces.append(f"{i}, {nxt}, {n + nxt}, {n + i}, -1")
    # Top cap
    for i in range(n):
        nxt = (i + 1) % n
        faces.append(f"{2 * n + 1}, {n + i}, {n + nxt}, -1")
    # Bottom cap
    for i in range(n):
        nxt = (i + 1) % n
        faces.append(f"{2 * n}, {nxt}, {i}, -1")

    return f"""IndexedFaceSet {{
        solid FALSE
        coord Coordinate {{ point [ {", ".join(pts)} ] }}
        coordIndex [ {", ".join(faces)} ]
    }}"""


def vrml_box(x0: float, y0: float, z0: float, x1: float, y1: float, z1: float) -> str:
    """Return an IndexedFaceSet axis-aligned box from (x0,y0,z0) to (x1,y1,z1) in mm."""
    x0, y0, z0, x1, y1, z1 = x0 * U, y0 * U, z0 * U, x1 * U, y1 * U, z1 * U
    pts = [
        f"{x0:.5f} {y0:.5f} {z0:.5f}",
        f"{x1:.5f} {y0:.5f} {z0:.5f}",
        f"{x1:.5f} {y1:.5f} {z0:.5f}",
        f"{x0:.5f} {y1:.5f} {z0:.5f}",
        f"{x0:.5f} {y0:.5f} {z1:.5f}",
        f"{x1:.5f} {y0:.5f} {z1:.5f}",
        f"{x1:.5f} {y1:.5f} {z1:.5f}",
        f"{x0:.5f} {y1:.5f} {z1:.5f}",
    ]
    faces = [
        "0, 2, 1, -1", "0, 3, 2, -1",  # Bottom
        "4, 5, 6, -1", "4, 6, 7, -1",  # Top
        "0, 1, 5, -1", "0, 5, 4, -1",  # Front
        "1, 2, 6, -1", "1, 6, 5, -1",  # Right
        "2, 3, 7, -1", "2, 7, 6, -1",  # Back
        "3, 0, 4, -1", "3, 4, 7, -1",  # Left
    ]
    return f"""IndexedFaceSet {{
        solid FALSE
        coord Coordinate {{ point [ {", ".join(pts)} ] }}
        coordIndex [ {", ".join(faces)} ]
    }}"""


# 1. ESP32-C3-MINI-1.wrl (13.2 x 16.6 x 2.4 mm RF MCU Module)
esp_wrl = f"""#VRML V2.0 utf8
Transform {{
    children [
        # Dark module PCB substrate (13.2 x 16.5 x 0.8 mm)
        Shape {{
            appearance Appearance {{
                material Material {{
                    diffuseColor 0.10 0.12 0.10
                    specularColor 0.20 0.20 0.20
                    shininess 0.3
                }}
            }}
            geometry {vrml_box(-6.60, -8.10, 0.05, 6.60, 8.40, 0.85)}
        }}
        # Brushed Stainless Steel RF Shield Can (11.8 x 9.6 x 1.6 mm)
        Shape {{
            appearance Appearance {{
                material Material {{
                    diffuseColor 0.78 0.80 0.82
                    specularColor 0.92 0.94 0.96
                    ambientIntensity 0.4
                    shininess 0.8
                }}
            }}
            geometry {vrml_box(-5.90, -7.60, 0.85, 5.90, 2.00, 2.45)}
        }}
        # Dark laser-etched label plate on top of RF shield can
        Shape {{
            appearance Appearance {{
                material Material {{
                    diffuseColor 0.35 0.37 0.40
                    specularColor 0.50 0.50 0.50
                    shininess 0.4
                }}
            }}
            geometry {vrml_box(-4.20, -6.00, 2.45, 4.20, 0.40, 2.48)}
        }}
        # Gold PCB Meander Antenna on top section (y in 2.0 .. 8.4 mm)
        Shape {{
            appearance Appearance {{
                material Material {{
                    diffuseColor 0.85 0.68 0.15
                    specularColor 0.95 0.85 0.35
                    shininess 0.7
                }}
            }}
            geometry {vrml_box(-5.60, 7.20, 0.85, 5.60, 7.80, 0.90)}
        }}
        Shape {{
            appearance Appearance {{
                material Material {{
                    diffuseColor 0.85 0.68 0.15
                    specularColor 0.95 0.85 0.35
                    shininess 0.7
                }}
            }}
            geometry {vrml_box(-5.60, 5.20, 0.85, 5.60, 5.80, 0.90)}
        }}
        Shape {{
            appearance Appearance {{
                material Material {{
                    diffuseColor 0.85 0.68 0.15
                    specularColor 0.95 0.85 0.35
                    shininess 0.7
                }}
            }}
            geometry {vrml_box(-5.60, 3.20, 0.85, 3.50, 3.80, 0.90)}
        }}
        Shape {{
            appearance Appearance {{
                material Material {{
                    diffuseColor 0.85 0.68 0.15
                    specularColor 0.95 0.85 0.35
                    shininess 0.7
                }}
            }}
            geometry {vrml_box(-5.60, 3.20, 0.85, -4.90, 7.80, 0.90)}
        }}
        Shape {{
            appearance Appearance {{
                material Material {{
                    diffuseColor 0.85 0.68 0.15
                    specularColor 0.95 0.85 0.35
                    shininess 0.7
                }}
            }}
            geometry {vrml_box(4.90, 5.20, 0.85, 5.60, 7.80, 0.90)}
        }}
        Shape {{
            appearance Appearance {{
                material Material {{
                    diffuseColor 0.85 0.68 0.15
                    specularColor 0.95 0.85 0.35
                    shininess 0.7
                }}
            }}
            geometry {vrml_box(-1.50, 2.00, 0.85, -0.80, 5.80, 0.90)}
        }}
    ]
}}
"""
with open(os.path.join(models_dir, "ESP32-C3-MINI-1.wrl"), "w", encoding="utf-8") as f:
    f.write(esp_wrl)


# 2. Winsen_ME3-CO.wrl (D=20.0mm x H=15.0mm Electrochemical CO Sensor in 3 Mill-Max Sockets)
me3_wrl = f"""#VRML V2.0 utf8
Transform {{
    children [
        # 3 Gold Mill-Max Socket Shoulders at (-2.5, 5.5), (0.0, 6.5), (2.5, 5.5)
        Transform {{
            translation {-2.5 * U:.5f} {5.5 * U:.5f} 0
            children [
                Shape {{
                    appearance Appearance {{ material Material {{ diffuseColor 0.85 0.68 0.15 specularColor 0.95 0.85 0.35 shininess 0.7 }} }}
                    geometry {vrml_cylinder_z(1.15, -2.5, 2.2, 24)}
                }}
            ]
        }}
        Transform {{
            translation 0.0 {6.5 * U:.5f} 0
            children [
                Shape {{
                    appearance Appearance {{ material Material {{ diffuseColor 0.85 0.68 0.15 specularColor 0.95 0.85 0.35 shininess 0.7 }} }}
                    geometry {vrml_cylinder_z(1.15, -2.5, 2.2, 24)}
                }}
            ]
        }}
        Transform {{
            translation {2.5 * U:.5f} {5.5 * U:.5f} 0
            children [
                Shape {{
                    appearance Appearance {{ material Material {{ diffuseColor 0.85 0.68 0.15 specularColor 0.95 0.85 0.35 shininess 0.7 }} }}
                    geometry {vrml_cylinder_z(1.15, -2.5, 2.2, 24)}
                }}
            ]
        }}
        # Winsen ME3-CO Main Cylindrical Body (Industrial Amber/Orange Cap, D=19.6mm, z=2.0..14.5mm)
        Shape {{
            appearance Appearance {{
                material Material {{
                    diffuseColor 0.88 0.36 0.08
                    specularColor 0.35 0.35 0.35
                    shininess 0.45
                }}
            }}
            geometry {vrml_cylinder_z(9.80, 2.0, 14.5, 64)}
        }}
        # Top Flange Ring (D=20.0mm, z=12.5..14.8mm)
        Shape {{
            appearance Appearance {{
                material Material {{
                    diffuseColor 0.92 0.42 0.10
                    specularColor 0.40 0.40 0.40
                    shininess 0.5
                }}
            }}
            geometry {vrml_cylinder_z(10.00, 12.5, 14.8, 64)}
        }}
        # Top Circular Gas Diffusion Stainless Mesh Grille (D=13.6mm, z=14.5..15.0mm)
        Shape {{
            appearance Appearance {{
                material Material {{
                    diffuseColor 0.28 0.30 0.32
                    specularColor 0.70 0.72 0.75
                    shininess 0.6
                }}
            }}
            geometry {vrml_cylinder_z(6.80, 14.5, 15.0, 48)}
        }}
        # Inner Silver Sensing Membrane Ring (D=10.0mm, z=14.9..15.1mm)
        Shape {{
            appearance Appearance {{
                material Material {{
                    diffuseColor 0.72 0.75 0.78
                    specularColor 0.90 0.90 0.92
                    shininess 0.75
                }}
            }}
            geometry {vrml_cylinder_z(5.00, 14.9, 15.1, 48)}
        }}
    ]
}}
"""
with open(os.path.join(models_dir, "Winsen_ME3-CO.wrl"), "w", encoding="utf-8") as f:
    f.write(me3_wrl)


# 3. CUI_CDM-12008_Speaker.wrl (D=12.0mm x H=5.5mm Dynamic Mylar Audio Speaker)
spk_wrl = f"""#VRML V2.0 utf8
Transform {{
    children [
        # Matte Black ABS Acoustic Speaker Housing (D=12.0mm, z=0.0..5.2mm)
        Shape {{
            appearance Appearance {{
                material Material {{
                    diffuseColor 0.12 0.13 0.15
                    specularColor 0.30 0.30 0.32
                    shininess 0.4
                }}
            }}
            geometry {vrml_cylinder_z(6.00, 0.0, 5.2, 64)}
        }}
        # Brushed Aluminum Outer Speaker Bezel Ring (D=11.4mm, z=5.0..5.5mm)
        Shape {{
            appearance Appearance {{
                material Material {{
                    diffuseColor 0.75 0.78 0.80
                    specularColor 0.90 0.92 0.95
                    shininess 0.8
                }}
            }}
            geometry {vrml_cylinder_z(5.70, 5.0, 5.5, 64)}
        }}
        # Dark Mylar Speaker Diaphragm Cone (D=9.8mm, z=5.1..5.55mm)
        Shape {{
            appearance Appearance {{
                material Material {{
                    diffuseColor 0.20 0.22 0.25
                    specularColor 0.55 0.55 0.60
                    shininess 0.65
                }}
            }}
            geometry {vrml_cylinder_z(4.90, 5.1, 5.55, 64)}
        }}
        # Silver Voice-Coil Center Dust Dome (D=4.8mm, z=5.4..5.8mm)
        Shape {{
            appearance Appearance {{
                material Material {{
                    diffuseColor 0.82 0.84 0.88
                    specularColor 0.95 0.95 0.98
                    shininess 0.85
                }}
            }}
            geometry {vrml_cylinder_z(2.40, 5.4, 5.8, 48)}
        }}
        # Protective Speaker Grille Cross-Bars across the top
        Shape {{
            appearance Appearance {{
                material Material {{
                    diffuseColor 0.12 0.13 0.15
                    specularColor 0.30 0.30 0.32
                    shininess 0.4
                }}
            }}
            geometry {vrml_box(-5.60, -0.45, 5.50, 5.60, 0.45, 5.95)}
        }}
        Shape {{
            appearance Appearance {{
                material Material {{
                    diffuseColor 0.12 0.13 0.15
                    specularColor 0.30 0.30 0.32
                    shininess 0.4
                }}
            }}
            geometry {vrml_box(-0.45, -5.60, 5.50, 0.45, 5.60, 5.95)}
        }}
    ]
}}
"""
with open(os.path.join(models_dir, "CUI_CDM-12008_Speaker.wrl"), "w", encoding="utf-8") as f:
    f.write(spk_wrl)


# 4. Figaro_TGS2610_LPG.wrl (D=9.2mm x H=7.8mm TO-5-4 Stainless-Steel Flameproof Mesh LPG Sensor)
lpg_wrl = f"""#VRML V2.0 utf8
Transform {{
    children [
        # 4 Gold Leads at (+-1.80, +-1.80)
        Transform {{
            translation {-1.80 * U:.5f} {-1.80 * U:.5f} 0
            children [
                Shape {{
                    appearance Appearance {{ material Material {{ diffuseColor 0.85 0.68 0.15 specularColor 0.95 0.85 0.35 shininess 0.7 }} }}
                    geometry {vrml_cylinder_z(0.35, -2.5, 1.5, 16)}
                }}
            ]
        }}
        Transform {{
            translation {-1.80 * U:.5f} {1.80 * U:.5f} 0
            children [
                Shape {{
                    appearance Appearance {{ material Material {{ diffuseColor 0.85 0.68 0.15 specularColor 0.95 0.85 0.35 shininess 0.7 }} }}
                    geometry {vrml_cylinder_z(0.35, -2.5, 1.5, 16)}
                }}
            ]
        }}
        Transform {{
            translation {1.80 * U:.5f} {-1.80 * U:.5f} 0
            children [
                Shape {{
                    appearance Appearance {{ material Material {{ diffuseColor 0.85 0.68 0.15 specularColor 0.95 0.85 0.35 shininess 0.7 }} }}
                    geometry {vrml_cylinder_z(0.35, -2.5, 1.5, 16)}
                }}
            ]
        }}
        Transform {{
            translation {1.80 * U:.5f} {1.80 * U:.5f} 0
            children [
                Shape {{
                    appearance Appearance {{ material Material {{ diffuseColor 0.85 0.68 0.15 specularColor 0.95 0.85 0.35 shininess 0.7 }} }}
                    geometry {vrml_cylinder_z(0.35, -2.5, 1.5, 16)}
                }}
            ]
        }}
        # Nickel-Plated TO-5 Base Flange Ring (D=9.2mm, z=1.0..2.2mm)
        Shape {{
            appearance Appearance {{
                material Material {{
                    diffuseColor 0.76 0.78 0.82
                    specularColor 0.92 0.94 0.96
                    shininess 0.85
                }}
            }}
            geometry {vrml_cylinder_z(4.60, 1.0, 2.2, 48)}
        }}
        # Brushed Stainless Steel Body Cylinder (D=8.3mm, z=2.0..7.5mm)
        Shape {{
            appearance Appearance {{
                material Material {{
                    diffuseColor 0.68 0.72 0.76
                    specularColor 0.88 0.90 0.94
                    shininess 0.80
                }}
            }}
            geometry {vrml_cylinder_z(4.15, 2.0, 7.5, 48)}
        }}
        # Double-Layer SUS316 Flame Arrestor Top Mesh Dome (D=7.2mm, z=7.4..7.9mm)
        Shape {{
            appearance Appearance {{
                material Material {{
                    diffuseColor 0.32 0.35 0.38
                    specularColor 0.65 0.68 0.72
                    shininess 0.55
                }}
            }}
            geometry {vrml_cylinder_z(3.60, 7.4, 7.9, 48)}
        }}
    ]
}}
"""
with open(os.path.join(models_dir, "Figaro_TGS2610_LPG.wrl"), "w", encoding="utf-8") as f:
    f.write(lpg_wrl)


# 5. Color-Coded 0603 SMD Status LEDs (Red, Green, Blue, Amber/Yellow)
def write_led_0603_wrl(fname: str, r: float, g: float, b: float, er: float, eg: float, eb: float) -> None:
    wrl = f"""#VRML V2.0 utf8
Transform {{
    children [
        # Left & Right Tin/Silver End Terminals (1.6 x 0.8 mm 0603 package)
        Shape {{
            appearance Appearance {{ material Material {{ diffuseColor 0.82 0.84 0.86 specularColor 0.92 0.94 0.96 shininess 0.8 }} }}
            geometry {vrml_box(-0.80, -0.40, 0.00, -0.45, 0.40, 0.35)}
        }}
        Shape {{
            appearance Appearance {{ material Material {{ diffuseColor 0.82 0.84 0.86 specularColor 0.92 0.94 0.96 shininess 0.8 }} }}
            geometry {vrml_box(0.45, -0.40, 0.00, 0.80, 0.40, 0.35)}
        }}
        # White Ceramic Substrate Body
        Shape {{
            appearance Appearance {{ material Material {{ diffuseColor 0.92 0.92 0.90 specularColor 0.40 0.40 0.40 shininess 0.3 }} }}
            geometry {vrml_box(-0.46, -0.40, 0.02, 0.46, 0.40, 0.32)}
        }}
        # Colored Translucent/Glowing Epoxy Lens Dome
        Shape {{
            appearance Appearance {{
                material Material {{
                    diffuseColor {r:.2f} {g:.2f} {b:.2f}
                    emissiveColor {er:.2f} {eg:.2f} {eb:.2f}
                    specularColor 0.90 0.90 0.90
                    shininess 0.85
                }}
            }}
            geometry {vrml_box(-0.42, -0.36, 0.30, 0.42, 0.36, 0.72)}
        }}
    ]
}}
"""
    with open(os.path.join(models_dir, fname), "w", encoding="utf-8") as f_out:
        f_out.write(wrl)


write_led_0603_wrl("LED_0603_Red.wrl", 0.95, 0.10, 0.10, 0.45, 0.02, 0.02)
write_led_0603_wrl("LED_0603_Green.wrl", 0.10, 0.88, 0.20, 0.02, 0.38, 0.05)
write_led_0603_wrl("LED_0603_Blue.wrl", 0.12, 0.45, 0.98, 0.03, 0.15, 0.48)
write_led_0603_wrl("LED_0603_Yellow.wrl", 0.98, 0.72, 0.05, 0.48, 0.32, 0.01)


# 6. Color-Coded C&K PTS647 4.5x4.5x5.0mm Tactile Switches (Yellow=TEST, Blue=HUSH/BOOT, Red=HW_RESET)
def write_pts647_wrl(fname: str, r: float, g: float, b: float) -> None:
    wrl = f"""#VRML V2.0 utf8
Transform {{
    children [
        # 4 Silver Gull-Wing SMD Leads at (+-2.625, +-1.60 mm)
        Shape {{
            appearance Appearance {{ material Material {{ diffuseColor 0.82 0.84 0.86 specularColor 0.92 0.94 0.96 shininess 0.8 }} }}
            geometry {vrml_box(-3.10, 1.15, 0.00, 3.10, 2.05, 0.35)}
        }}
        Shape {{
            appearance Appearance {{ material Material {{ diffuseColor 0.82 0.84 0.86 specularColor 0.92 0.94 0.96 shininess 0.8 }} }}
            geometry {vrml_box(-3.10, -2.05, 0.00, 3.10, -1.15, 0.35)}
        }}
        # Dark LCP Molded Switch Housing (4.5 x 4.5 x 2.6 mm)
        Shape {{
            appearance Appearance {{ material Material {{ diffuseColor 0.14 0.15 0.17 specularColor 0.28 0.28 0.30 shininess 0.35 }} }}
            geometry {vrml_box(-2.25, -2.25, 0.05, 2.25, 2.25, 2.60)}
        }}
        # Brushed Stainless-Steel Top Frame Cover (4.3 x 4.3 mm, z=2.60..2.85 mm)
        Shape {{
            appearance Appearance {{ material Material {{ diffuseColor 0.78 0.80 0.84 specularColor 0.92 0.94 0.96 shininess 0.85 }} }}
            geometry {vrml_box(-2.15, -2.15, 2.60, 2.15, 2.15, 2.85)}
        }}
        # Color-Coded Cylindrical Tactile Actuator Plunger (D=2.5 mm, z=2.80..5.00 mm)
        Shape {{
            appearance Appearance {{
                material Material {{
                    diffuseColor {r:.2f} {g:.2f} {b:.2f}
                    specularColor 0.65 0.65 0.65
                    shininess 0.60
                }}
            }}
            geometry {vrml_cylinder_z(1.25, 2.80, 5.00, 48)}
        }}
    ]
}}
"""
    with open(os.path.join(models_dir, fname), "w", encoding="utf-8") as f_out:
        f_out.write(wrl)


write_pts647_wrl("SW_PTS647_Yellow.wrl", 0.95, 0.70, 0.05)
write_pts647_wrl("SW_PTS647_Blue.wrl", 0.12, 0.48, 0.95)
write_pts647_wrl("SW_PTS647_Red.wrl", 0.90, 0.12, 0.12)

print("Generated 3D VRML models in:", models_dir)


