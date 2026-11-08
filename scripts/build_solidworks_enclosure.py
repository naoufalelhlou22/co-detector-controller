"""
Automated SolidWorks 3D Solid Modeler for Smart Dual Gas Detector Enclosure (Without PCBA)
Generates native SolidWorks parts (.SLDPRT), assembly (.SLDASM), and solid STEP files (.step):
  1. CO_Enclosure_Chassis_Base (.SLDPRT & .step)
  2. CO_Enclosure_Front_Cover (.SLDPRT & .step)
  3. CO_Enclosure_Wall_Bracket (.SLDPRT & .step)
  4. CO_Enclosure_Assembly (.SLDASM & .step)
"""

import win32com.client
import os
import math

PART_TMPL = r"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\Part.PRTDOT"
ASM_TMPL  = r"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\Assembly.ASMDOT"
OUT_DIR   = os.path.abspath("cad/solidworks")

def draw_squircle_sketch(sk_mgr, w_half, h_half, r):
    sk_mgr.CreateLine(-w_half + r, -h_half, 0, w_half - r, -h_half, 0)
    sk_mgr.CreateLine(w_half, -h_half + r, 0, w_half, h_half - r, 0)
    sk_mgr.CreateLine(w_half - r, h_half, 0, -w_half + r, h_half, 0)
    sk_mgr.CreateLine(-w_half, h_half - r, 0, -w_half, -h_half + r, 0)

    sk_mgr.CreateArc(w_half - r, -h_half + r, 0, w_half, -h_half + r, 0, w_half - r, -h_half, 0, 1)
    sk_mgr.CreateArc(w_half - r, h_half - r, 0, w_half - r, h_half, 0, w_half, h_half - r, 0, 1)
    sk_mgr.CreateArc(-w_half + r, h_half - r, 0, -w_half, h_half - r, 0, -w_half + r, h_half, 0, 1)
    sk_mgr.CreateArc(-w_half + r, -h_half + r, 0, -w_half + r, -h_half, 0, -w_half, -h_half + r, 0, 1)


# ==============================================================================
# 1. REAR CHASSIS BASE
# ==============================================================================
def build_rear_chassis(sw):
    print(">>> Building CO_Enclosure_Chassis_Base...")
    doc = sw.NewDocument(PART_TMPL, 0, 0.0, 0.0)
    sk_mgr = doc.SketchManager
    feat_mgr = doc.FeatureManager

    # Outer squircle: 92mm x 72mm x 10mm height, R10
    doc.SelectByID("Top Plane", "PLANE", 0.0, 0.0, 0.0)
    sk_mgr.InsertSketch(True)
    draw_squircle_sketch(sk_mgr, 0.092 / 2, 0.072 / 2, 0.010)

    feat_mgr.FeatureExtrusion2(
        True, False, False, 0, 0,
        0.010, 0.0, False, False, False, False,
        0.0, 0.0, False, False, False, False,
        True, True, True, 0, 0, False
    )
    doc.ClearSelection2(True)

    # Shell 2.2mm uniform wall (remove top face at Z = 10mm)
    doc.SelectByID("", "FACE", 0.0, 0.0, 0.010)
    doc.InsertFeatureShell(0.0022, False)
    doc.ClearSelection2(True)

    # 4x PCB Mounting Bosses at (+/-31.5, +/-21.5)
    doc.SelectByID("", "FACE", 0.0, 0.0, 0.0022)
    sk_mgr.InsertSketch(True)
    boss_coords = [(-0.0315, -0.0215), (0.0315, -0.0215), (-0.0315, 0.0215), (0.0315, 0.0215)]
    for bx, by in boss_coords:
        sk_mgr.CreateCircleByRadius(bx, by, 0.0, 0.00275) # OD 5.5mm
        sk_mgr.CreateCircleByRadius(bx, by, 0.0, 0.00180) # ID 3.6mm for M2.5 insert

    feat_mgr.FeatureExtrusion2(
        True, False, False, 0, 0,
        0.0045, 0.0, False, False, False, False,
        0.0, 0.0, False, False, False, False,
        True, True, True, 0, 0, False
    )
    doc.ClearSelection2(True)

    # Cutout J1 and J2 for Terminal Blocks on Left Wall (-X)
    doc.SelectByID("Right Plane", "PLANE", 0.0, 0.0, 0.0)
    sk_mgr.InsertSketch(True)
    # J1: Y = -13mm, Width = 12mm, Height = 9mm
    sk_mgr.CreateCenterRectangle(-0.013, 0.0065, 0.0, 0.006, 0.0045, 0.0)
    # J2: Y = +13mm, Width = 12mm, Height = 9mm
    sk_mgr.CreateCenterRectangle(0.013, 0.0065, 0.0, 0.006, 0.0045, 0.0)

    feat_mgr.FeatureCut4(
        True, False, False, 1, 0, 0.05, 0.05,
        False, False, False, False, 0.0, 0.0,
        False, False, False, False, False,
        True, True, True, True, False, 0.0, 0.0, False, False
    )
    doc.ClearSelection2(True)

    # Bottom draft slots for LPG sensor convection
    doc.SelectByID("Top Plane", "PLANE", 0.0, 0.0, 0.0)
    sk_mgr.InsertSketch(True)
    for i in range(-2, 3):
        sx = 0.024 + i * 0.0045
        sk_mgr.CreateCenterRectangle(sx, -0.0185, 0.0, 0.001, 0.007, 0.0)

    feat_mgr.FeatureCut4(
        True, False, False, 0, 0, 0.003, 0.0,
        False, False, False, False, 0.0, 0.0,
        False, False, False, False, False,
        True, True, True, True, False, 0.0, 0.0, False, False
    )
    doc.ClearSelection2(True)

    # Save
    prt_path = os.path.join(OUT_DIR, "CO_Enclosure_Chassis_Base.SLDPRT")
    stp_path = os.path.join(OUT_DIR, "CO_Enclosure_Chassis_Base.step")
    doc.SaveAs3(prt_path, 0, 2)
    doc.SaveAs3(stp_path, 0, 2)
    title = doc.GetTitle
    sw.CloseDoc(title)
    print(f"  Saved: {prt_path}")
    print(f"  Saved: {stp_path}")


# ==============================================================================
# 2. FRONT HOUSING COVER
# ==============================================================================
def build_front_cover(sw):
    print(">>> Building CO_Enclosure_Front_Cover...")
    doc = sw.NewDocument(PART_TMPL, 0, 0.0, 0.0)
    sk_mgr = doc.SketchManager
    feat_mgr = doc.FeatureManager

    # Outer squircle: 92mm x 72mm x 18mm height, R10
    doc.SelectByID("Top Plane", "PLANE", 0.0, 0.0, 0.0)
    sk_mgr.InsertSketch(True)
    draw_squircle_sketch(sk_mgr, 0.092 / 2, 0.072 / 2, 0.010)

    feat_mgr.FeatureExtrusion2(
        True, False, False, 0, 0,
        0.018, 0.0, False, False, False, False,
        0.0, 0.0, False, False, False, False,
        True, True, True, 0, 0, False
    )
    doc.ClearSelection2(True)

    # Shell 2.2mm wall thickness (removing bottom face at Z = 0)
    doc.SelectByID("", "FACE", 0.0, 0.0, 0.0)
    doc.InsertFeatureShell(0.0022, False)
    doc.ClearSelection2(True)

    # Internal Acoustic Shroud Cylinder for LS1 Buzzer (at -3.0mm, 13.0mm)
    doc.SelectByID("", "FACE", 0.0, 0.0, 0.018 - 0.0022)
    sk_mgr.InsertSketch(True)
    sk_mgr.CreateCircleByRadius(-0.003, 0.013, 0.0, 0.0070) # OD 14mm
    sk_mgr.CreateCircleByRadius(-0.003, 0.013, 0.0, 0.0055) # ID 11mm

    feat_mgr.FeatureExtrusion2(
        True, False, True, 0, 0, # Extrude downward into cavity
        0.006, 0.0, False, False, False, False,
        0.0, 0.0, False, False, False, False,
        True, True, True, 0, 0, False
    )
    doc.ClearSelection2(True)

    # Internal Thermal Barrier Rib at X = 17.0mm
    doc.SelectByID("", "FACE", 0.0, 0.0, 0.018 - 0.0022)
    sk_mgr.InsertSketch(True)
    sk_mgr.CreateCenterRectangle(0.017, 0.0, 0.0, 0.0007, 0.033, 0.0) # 1.4mm thick rib

    feat_mgr.FeatureExtrusion2(
        True, False, True, 0, 0,
        0.011, 0.0, False, False, False, False,
        0.0, 0.0, False, False, False, False,
        True, True, True, 0, 0, False
    )
    doc.ClearSelection2(True)

    # Cut Features on Top Face (Z = 18mm):
    doc.SelectByID("", "FACE", 0.0, 0.0, 0.018)
    sk_mgr.InsertSketch(True)

    # 1. Acoustic Rosette Horn (LS1 at -3.0, 13.0)
    sk_mgr.CreateCircleByRadius(-0.003, 0.013, 0.0, 0.0016) # Center dia 3.2mm
    for a in range(0, 360, 60):
        rad = math.radians(a)
        hx = -0.003 + 0.0036 * math.cos(rad)
        hy =  0.013 + 0.0036 * math.sin(rad)
        sk_mgr.CreateCircleByRadius(hx, hy, 0.0, 0.0011) # 6 satellite dia 2.2mm

    # 2. Status LED Light Pipe Window (at -3.4, 21.0)
    sk_mgr.CreateCenterRectangle(-0.0034, 0.021, 0.0, 0.007, 0.0019, 0.0)

    # 3. Test/Hush Button Cutout (at 7.0, 16.0)
    sk_mgr.CreateCenterRectangle(0.007, 0.016, 0.0, 0.009, 0.006, 0.0)

    # 4. CO Sensor Diffusion Slots (at 21.5, 10.5)
    for dy in [-0.006, -0.003, 0.0, 0.003, 0.006]:
        sk_mgr.CreateCenterRectangle(0.0215, 0.0105 + dy, 0.0, 0.007, 0.0006, 0.0)

    # 5. LPG Exhaust Vents (at 24.0, 32.0)
    for dx in [-0.008, -0.004, 0.0, 0.004, 0.008]:
        sk_mgr.CreateCenterRectangle(0.024 + dx, 0.032, 0.0, 0.001, 0.0025, 0.0)

    # Cut through outer top wall (2.2mm deep)
    feat_mgr.FeatureCut4(
        True, False, False, 0, 0, 0.003, 0.0,
        False, False, False, False, 0.0, 0.0,
        False, False, False, False, False,
        True, True, True, True, False, 0.0, 0.0, False, False
    )
    doc.ClearSelection2(True)

    # Save
    prt_path = os.path.join(OUT_DIR, "CO_Enclosure_Front_Cover.SLDPRT")
    stp_path = os.path.join(OUT_DIR, "CO_Enclosure_Front_Cover.step")
    doc.SaveAs3(prt_path, 0, 2)
    doc.SaveAs3(stp_path, 0, 2)
    title = doc.GetTitle
    sw.CloseDoc(title)
    print(f"  Saved: {prt_path}")
    print(f"  Saved: {stp_path}")


# ==============================================================================
# 3. WALL MOUNT BRACKET
# ==============================================================================
def build_wall_bracket(sw):
    print(">>> Building CO_Enclosure_Wall_Bracket...")
    doc = sw.NewDocument(PART_TMPL, 0, 0.0, 0.0)
    sk_mgr = doc.SketchManager
    feat_mgr = doc.FeatureManager

    # Base plate: 86mm x 66mm x 3mm height, R8
    doc.SelectByID("Top Plane", "PLANE", 0.0, 0.0, 0.0)
    sk_mgr.InsertSketch(True)
    draw_squircle_sketch(sk_mgr, 0.086 / 2, 0.066 / 2, 0.008)

    feat_mgr.FeatureExtrusion2(
        True, False, False, 0, 0,
        0.003, 0.0, False, False, False, False,
        0.0, 0.0, False, False, False, False,
        True, True, True, 0, 0, False
    )
    doc.ClearSelection2(True)

    # Features cut through bracket:
    doc.SelectByID("", "FACE", 0.0, 0.0, 0.003)
    sk_mgr.InsertSketch(True)

    # 1. Central Wire Pass-Through (34mm x 22mm)
    sk_mgr.CreateCenterRectangle(0.0, 0.0, 0.0, 0.017, 0.011, 0.0)

    # 2. EU 60mm Keyholes (at +/-30mm, Y = 0)
    for kx in [-0.030, 0.030]:
        sk_mgr.CreateCircleByRadius(kx, 0.0, 0.0, 0.0045) # Entry hole dia 9mm
        sk_mgr.CreateCenterRectangle(kx, 0.0025, 0.0, 0.00225, 0.0025, 0.0)

    # 3. US 83.5mm Keyholes (at X = 0, Y = +/-41.75mm)
    for ky in [-0.04175, 0.04175]:
        sk_mgr.CreateCircleByRadius(0.0, ky, 0.0, 0.0045)
        sk_mgr.CreateCenterRectangle(0.0025, ky, 0.0, 0.0025, 0.00225, 0.0)

    # Cut through plate
    feat_mgr.FeatureCut4(
        True, False, False, 0, 0, 0.004, 0.0,
        False, False, False, False, 0.0, 0.0,
        False, False, False, False, False,
        True, True, True, True, False, 0.0, 0.0, False, False
    )
    doc.ClearSelection2(True)

    # 4x Bayonet Sliding Wedge Tabs (Z from 3mm to 6mm)
    doc.SelectByID("", "FACE", 0.0, 0.0, 0.003)
    sk_mgr.InsertSketch(True)
    tab_coords = [(-0.030, -0.020), (0.030, -0.020), (-0.030, 0.020), (0.030, 0.020)]
    for tx, ty in tab_coords:
        sk_mgr.CreateCircleByRadius(tx, ty, 0.0, 0.0032)

    feat_mgr.FeatureExtrusion2(
        True, False, False, 0, 0,
        0.003, 0.0, False, False, False, False,
        0.0, 0.0, False, False, False, False,
        True, True, True, 0, 0, False
    )
    doc.ClearSelection2(True)

    # Save
    prt_path = os.path.join(OUT_DIR, "CO_Enclosure_Wall_Bracket.SLDPRT")
    stp_path = os.path.join(OUT_DIR, "CO_Enclosure_Wall_Bracket.step")
    doc.SaveAs3(prt_path, 0, 2)
    doc.SaveAs3(stp_path, 0, 2)
    title = doc.GetTitle
    sw.CloseDoc(title)
    print(f"  Saved: {prt_path}")
    print(f"  Saved: {stp_path}")


# ==============================================================================
# 4. ENCLOSURE ASSEMBLY (WITHOUT PCBA)
# ==============================================================================
def build_enclosure_assembly(sw):
    print(">>> Building CO_Enclosure_Assembly (Pure Enclosure, No PCBA)...")
    doc = sw.NewDocument(ASM_TMPL, 0, 0.0, 0.0)
    if not doc:
        print("  Warning: Assembly template not found, skipping SLDASM build.")
        return

    base_prt = os.path.join(OUT_DIR, "CO_Enclosure_Chassis_Base.SLDPRT")
    front_prt = os.path.join(OUT_DIR, "CO_Enclosure_Front_Cover.SLDPRT")
    brk_prt   = os.path.join(OUT_DIR, "CO_Enclosure_Wall_Bracket.SLDPRT")

    # Insert Components
    # Base Chassis at origin
    comp1 = doc.AddComponent5(base_prt, 0, "", False, "", 0.0, 0.0, 0.0)
    # Front Cover on top of base (offset Z = 10mm)
    comp2 = doc.AddComponent5(front_prt, 0, "", False, "", 0.0, 0.0, 0.010)
    # Wall Bracket underneath base (offset Z = -3mm)
    comp3 = doc.AddComponent5(brk_prt, 0, "", False, "", 0.0, 0.0, -0.003)

    # Force full rebuild so assembly geometry evaluates into the solid STEP tree
    doc.ForceRebuild3(False)
    doc.ViewZoomtofit2()

    asm_path = os.path.join(OUT_DIR, "CO_Enclosure_Assembly.SLDASM")
    stp_path = os.path.join(OUT_DIR, "CO_Enclosure_Assembly.step")
    doc.SaveAs3(asm_path, 0, 2)
    doc.SaveAs3(stp_path, 0, 2)
    title = doc.GetTitle
    sw.CloseDoc(title)
    print(f"  Saved: {asm_path}")
    print(f"  Saved: {stp_path}")


def main():
    print("Connecting to SolidWorks COM API...")
    sw = win32com.client.Dispatch("SldWorks.Application")
    os.makedirs(OUT_DIR, exist_ok=True)

    build_rear_chassis(sw)
    build_front_cover(sw)
    build_wall_bracket(sw)
    build_enclosure_assembly(sw)

    print("\nALL SOLIDWORKS ENCLOSURE 3D MODELS (WITHOUT PCBA) GENERATED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
