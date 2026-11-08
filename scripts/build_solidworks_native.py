"""
SolidWorks 2026 Native Parametric CAD Automation Engine
Builds native .SLDPRT parts and .SLDASM assembly matching KiCad datum:
  1. cad/solidworks/CO_Enclosure_Chassis_Base.SLDPRT (.step)
  2. cad/solidworks/CO_Enclosure_Front_Cover.SLDPRT (.step)
  3. cad/solidworks/CO_Enclosure_Wall_Bracket.SLDPRT (.step)
  4. cad/solidworks/CO_Enclosure_Assembly.SLDASM (.step)
"""

import os
import math
import time
import win32com.client

def run_solidworks_builder():
    print("[1/5] Connecting to SolidWorks 2026 COM API...")
    try:
        sw = win32com.client.Dispatch('SldWorks.Application')
        sw.Visible = True
    except Exception as e:
        print(f"[ERROR] Failed to attach to SolidWorks: {e}")
        return False

    part_template = sw.GetDocumentTemplate(1, '', 0, 0, 0) # swDocPART = 1
    asm_template  = sw.GetDocumentTemplate(2, '', 0, 0, 0) # swDocASSEMBLY = 2

    out_dir = os.path.abspath("cad/solidworks")
    os.makedirs(out_dir, exist_ok=True)

    # --------------------------------------------------------------------------
    # PART 1: CHASSIS BASE
    # --------------------------------------------------------------------------
    print("[2/5] Modeling CO_Enclosure_Chassis_Base...")
    doc = sw.NewDocument(part_template, 0, 0, 0)
    if not doc:
        print("[ERROR] Could not create new Part document")
        return False

    # Outer squircle extrusion: 86mm x 66mm x 12mm
    doc.SelectByID("Top Plane", "PLANE", 0, 0, 0)
    doc.SketchManager.InsertSketch(True)
    doc.SketchManager.CreateCenterRectangle(0, 0, 0, 0.043, 0.033, 0)
    doc.SketchManager.InsertSketch(True)
    doc.FeatureManager.FeatureExtrusion2(
        True, False, False, 0, 0, 0.012, 0, False, False, False, False,
        0, 0, False, False, False, False, True, True, True, 0, 0, False
    )

    # Cut cavity: 81.2mm x 61.2mm x 9.6mm deep (leaves 2.4mm floor and 2.4mm walls)
    doc.SelectByID("", "FACE", 0, 0, 0.012)
    doc.SketchManager.InsertSketch(True)
    doc.SketchManager.CreateCenterRectangle(0, 0, 0, 0.0406, 0.0306, 0)
    doc.SketchManager.InsertSketch(True)
    doc.FeatureManager.FeatureCut4(
        True, False, False, 0, 0, 0.0096, 0, False, False, False, False,
        0, 0, False, False, False, False, False, True, True, True, True,
        False, 0, 0, False, False
    )

    # 4x Standoff Bosses H1, H2, H3, H4 (OD=6.0mm, H=4.5mm from floor Z=2.4mm to Z=6.9mm)
    # PCB datum offset: PCB center is (35.0, 25.0) mm.
    # Center relative coords: dx = (x - 35.0)/1000, dy = (y - 25.0)/1000
    doc.SelectByID("", "FACE", 0, 0, 0.0024)
    doc.SketchManager.InsertSketch(True)
    bosses = [
        (3.50, 3.50),
        (66.50, 3.50),
        (3.50, 46.50),
        (66.50, 46.50)
    ]
    for bx, by in bosses:
        dx = (bx - 35.0) / 1000.0
        dy = (by - 25.0) / 1000.0
        doc.SketchManager.CreateCircleByRadius(dx, dy, 0, 0.003) # OD 6mm
    doc.SketchManager.InsertSketch(True)
    doc.FeatureManager.FeatureExtrusion2(
        True, False, False, 0, 0, 0.0045, 0, False, False, False, False,
        0, 0, False, False, False, False, True, True, True, 0, 0, False
    )

    # Cut insert pilot holes (ID=3.6mm, depth 4.5mm)
    doc.SelectByID("", "FACE", 0, 0, 0.0069)
    doc.SketchManager.InsertSketch(True)
    for bx, by in bosses:
        dx = (bx - 35.0) / 1000.0
        dy = (by - 25.0) / 1000.0
        doc.SketchManager.CreateCircleByRadius(dx, dy, 0, 0.0018) # ID 3.6mm
    doc.SketchManager.InsertSketch(True)
    doc.FeatureManager.FeatureCut4(
        True, False, False, 0, 0, 0.0045, 0, False, False, False, False,
        0, 0, False, False, False, False, False, True, True, True, True,
        False, 0, 0, False, False
    )

    # Save Base PRT and STEP
    base_prt = os.path.join(out_dir, "CO_Enclosure_Chassis_Base.SLDPRT")
    base_stp = os.path.join(out_dir, "CO_Enclosure_Chassis_Base.step")
    doc.SaveAs(base_prt)
    doc.SaveAs(base_stp)
    sw.CloseDoc(doc.GetTitle)
    print(f"  [SAVED] {base_prt}")
    print(f"  [SAVED] {base_stp}")

    # --------------------------------------------------------------------------
    # PART 2: FRONT COVER
    # --------------------------------------------------------------------------
    print("[3/5] Modeling CO_Enclosure_Front_Cover...")
    doc = sw.NewDocument(part_template, 0, 0, 0)

    # Outer body: 86mm x 66mm x 16mm
    doc.SelectByID("Top Plane", "PLANE", 0, 0, 0)
    doc.SketchManager.InsertSketch(True)
    doc.SketchManager.CreateCenterRectangle(0, 0, 0, 0.043, 0.033, 0)
    doc.SketchManager.InsertSketch(True)
    doc.FeatureManager.FeatureExtrusion2(
        True, False, False, 0, 0, 0.016, 0, False, False, False, False,
        0, 0, False, False, False, False, True, True, True, 0, 0, False
    )

    # Internal cavity cut: 81.2mm x 61.2mm x 13.6mm deep (Z from 0 to 13.6mm, 2.4mm top face)
    doc.SelectByID("", "FACE", 0, 0, 0)
    doc.SketchManager.InsertSketch(True)
    doc.SketchManager.CreateCenterRectangle(0, 0, 0, 0.0406, 0.0306, 0)
    doc.SketchManager.InsertSketch(True)
    doc.FeatureManager.FeatureCut4(
        True, False, False, 0, 0, 0.0136, 0, False, False, False, False,
        0, 0, False, False, False, False, False, True, True, True, True,
        False, 0, 0, False, False
    )

    # Cut feature apertures on Front Top Face (Z = 0.016m)
    doc.SelectByID("", "FACE", 0, 0, 0.016)
    doc.SketchManager.InsertSketch(True)

    # 1. OLED Display Bezel Window: 25.0 x 14.0 mm at CAD (48.50, 32.50)
    oled_dx = (48.50 - 35.0) / 1000.0
    oled_dy = (32.50 - 25.0) / 1000.0
    doc.SketchManager.CreateCenterRectangle(oled_dx, oled_dy, 0, oled_dx + 0.0125, oled_dy + 0.007, 0)

    # 2. Tactile Button SW2 (HUSH) at CAD (42.00, 12.00): Dia 5.5mm
    sw2_dx = (42.00 - 35.0) / 1000.0
    sw2_dy = (12.00 - 25.0) / 1000.0
    doc.SketchManager.CreateCircleByRadius(sw2_dx, sw2_dy, 0, 0.00275)

    # 3. Tactile Button SW1 (TEST) at CAD (42.00, 6.00): Dia 5.5mm
    sw1_dx = (42.00 - 35.0) / 1000.0
    sw1_dy = (6.00 - 25.0) / 1000.0
    doc.SketchManager.CreateCircleByRadius(sw1_dx, sw1_dy, 0, 0.00275)

    # 4. Buzzer Rosette LS1 at CAD (32.00, 12.00): 7 holes
    bz_dx = (32.00 - 35.0) / 1000.0
    bz_dy = (12.00 - 25.0) / 1000.0
    doc.SketchManager.CreateCircleByRadius(bz_dx, bz_dy, 0, 0.00125) # center hole 2.5mm
    for a in range(0, 360, 60):
        rad = math.radians(a)
        doc.SketchManager.CreateCircleByRadius(bz_dx + 0.0032*math.cos(rad), bz_dy + 0.0032*math.sin(rad), 0, 0.0010)

    # 5. S1 CO Sensor Diffusion Well at CAD (56.50, 14.50): Dia 20.5mm
    co_dx = (56.50 - 35.0) / 1000.0
    co_dy = (14.50 - 25.0) / 1000.0
    doc.SketchManager.CreateCircleByRadius(co_dx, co_dy, 0, 0.01025)

    # 6. S2 LPG Chimney Vent at CAD (59.00, 43.50): Dia 10.5mm
    lpg_dx = (59.00 - 35.0) / 1000.0
    lpg_dy = (43.50 - 25.0) / 1000.0
    doc.SketchManager.CreateCircleByRadius(lpg_dx, lpg_dy, 0, 0.00525)

    # 7. 4-LED Light Pipe Apertures at CAD Y = 4.00 mm
    for lx in [26.80, 30.00, 33.20, 36.40]:
        ldx = (lx - 35.0) / 1000.0
        ldy = (4.00 - 25.0) / 1000.0
        doc.SketchManager.CreateCircleByRadius(ldx, ldy, 0, 0.0010)

    doc.SketchManager.InsertSketch(True)
    doc.FeatureManager.FeatureCut4(
        True, False, False, 0, 0, 0.0024, 0, False, False, False, False,
        0, 0, False, False, False, False, False, True, True, True, True,
        False, 0, 0, False, False
    )

    # Save Cover PRT and STEP
    cover_prt = os.path.join(out_dir, "CO_Enclosure_Front_Cover.SLDPRT")
    cover_stp = os.path.join(out_dir, "CO_Enclosure_Front_Cover.step")
    doc.SaveAs(cover_prt)
    doc.SaveAs(cover_stp)
    sw.CloseDoc(doc.GetTitle)
    print(f"  [SAVED] {cover_prt}")
    print(f"  [SAVED] {cover_stp}")

    # --------------------------------------------------------------------------
    # PART 3: WALL BRACKET
    # --------------------------------------------------------------------------
    print("[4/5] Modeling CO_Enclosure_Wall_Bracket...")
    doc = sw.NewDocument(part_template, 0, 0, 0)
    doc.SelectByID("Top Plane", "PLANE", 0, 0, 0)
    doc.SketchManager.InsertSketch(True)
    doc.SketchManager.CreateCenterRectangle(0, 0, 0, 0.038, 0.028, 0)
    doc.SketchManager.InsertSketch(True)
    doc.FeatureManager.FeatureExtrusion2(
        True, False, False, 0, 0, 0.0035, 0, False, False, False, False,
        0, 0, False, False, False, False, True, True, True, 0, 0, False
    )

    # Cut 2x Keyhole Slots (pitch 60.0mm) & Center Pass-through
    doc.SelectByID("", "FACE", 0, 0, 0.0035)
    doc.SketchManager.InsertSketch(True)
    doc.SketchManager.CreateCircleByRadius(0, -0.030, 0, 0.0045)
    doc.SketchManager.CreateCircleByRadius(0,  0.030, 0, 0.0045)
    doc.SketchManager.CreateCenterRectangle(0, 0, 0, 0.011, 0.008, 0)
    doc.SketchManager.InsertSketch(True)
    doc.FeatureManager.FeatureCut4(
        True, False, False, 0, 0, 0.0035, 0, False, False, False, False,
        0, 0, False, False, False, False, False, True, True, True, True,
        False, 0, 0, False, False
    )

    bracket_prt = os.path.join(out_dir, "CO_Enclosure_Wall_Bracket.SLDPRT")
    bracket_stp = os.path.join(out_dir, "CO_Enclosure_Wall_Bracket.step")
    doc.SaveAs(bracket_prt)
    doc.SaveAs(bracket_stp)
    sw.CloseDoc(doc.GetTitle)
    print(f"  [SAVED] {bracket_prt}")
    print(f"  [SAVED] {bracket_stp}")

    # --------------------------------------------------------------------------
    # PART 4: COMPLETE ASSEMBLY (Mated enclosure, no PCBA)
    # --------------------------------------------------------------------------
    print("[5/5] Building CO_Enclosure_Assembly...")
    asm_doc = sw.NewDocument(asm_template, 0, 0, 0)
    if asm_doc:
        # Add components into assembly
        comp_base = asm_doc.AddComponent5(base_prt, 0, "", False, "", 0, 0, 0)
        comp_cover = asm_doc.AddComponent5(cover_prt, 0, "", False, "", 0, 0, 0.012)
        comp_bracket = asm_doc.AddComponent5(bracket_prt, 0, "", False, "", 0, 0, -0.0035)

        asm_file = os.path.join(out_dir, "CO_Enclosure_Assembly.SLDASM")
        asm_stp  = os.path.join(out_dir, "CO_Enclosure_Assembly.step")
        asm_doc.SaveAs(asm_file)
        asm_doc.SaveAs(asm_stp)
        sw.CloseDoc(asm_doc.GetTitle)
        print(f"  [SAVED] {asm_file}")
        print(f"  [SAVED] {asm_stp}")

    print("\n[COMPLETE] SolidWorks 2026 Native Models & STEP Files Generated Successfully!")
    return True

if __name__ == '__main__':
    run_solidworks_builder()
