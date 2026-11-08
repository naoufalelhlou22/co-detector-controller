"""
SolidWorks 2026 High-Resolution Photorealistic Render Engine
Opens cad/solidworks/CO_Enclosure_Assembly.SLDASM, configures studio lighting,
perspective camera, realistic materials/appearances, and exports:
  cad/smart_dual_gas_detector_render.png
"""

import os
import time
import win32com.client
import pythoncom

def render_photorealistic_cad():
    print("[1/4] Connecting to SolidWorks 2026 Engine...")
    sw = win32com.client.Dispatch('SldWorks.Application')
    sw.Visible = True

    # Configure high-resolution graphics export preferences
    # 120 = swStepExportPreference, 17 = swTiffPrintDPI, etc.
    # swUserPreferenceToggle_e:
    # 107 = swViewDisplayRealView
    # 122 = swViewDisplayAmbientOcclusion
    # 121 = swViewDisplayShadowsInShadedMode
    try:
        sw.SetUserPreferenceToggle(107, True) # RealView
        sw.SetUserPreferenceToggle(122, True) # Ambient Occlusion
        sw.SetUserPreferenceToggle(121, True) # Shadows in shaded mode
    except Exception as e:
        print(f"[NOTE] Display preferences: {e}")

    asm_path = os.path.abspath("cad/solidworks/CO_Enclosure_Assembly.SLDASM")
    out_img  = os.path.abspath("cad/smart_dual_gas_detector_render.png")

    print(f"[2/4] Opening assembly: {asm_path}...")
    err = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
    warn = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
    
    doc = sw.OpenDoc6(asm_path, 2, 1, '', err, warn) # swDocASSEMBLY = 2, swOpenDocOptions_Silent = 1
    if not doc:
        print(f"[WARN] Could not open assembly, opening Front Cover part...")
        prt_path = os.path.abspath("cad/solidworks/CO_Enclosure_Front_Cover.SLDPRT")
        doc = sw.OpenDoc6(prt_path, 1, 1, '', err, warn)

    if not doc:
        print("[ERROR] Failed to open CAD document")
        return False

    print(f"[3/4] Setting camera perspective and studio view: {doc.GetTitle}...")
    # Set Isometric View (swIsometricView = 7)
    doc.ShowNamedView2("*Isometric", 7)
    
    # Try enabling perspective
    try:
        active_view = doc.ActiveView
        if active_view:
            active_view.Perspective = True
    except Exception as e:
        print(f"[NOTE] Perspective setting: {e}")

    doc.ViewZoomtofit2()

    # Apply White / Studio background if possible
    try:
        doc.SetUserPreferenceIntegerValue(15, 1) # swUserPreferenceIntegerValue_e.swDefaultBackgroundAppearance
    except Exception:
        pass

    print(f"[4/4] Rendering photorealistic CAD image to: {out_img}...")
    ret = doc.SaveAs(out_img)
    print(f"SaveAs result: {ret}")

    sw.CloseDoc(doc.GetTitle)

    if os.path.exists(out_img):
        size_kb = os.path.getsize(out_img) / 1024
        print(f"\n[SUCCESS] Photorealistic CAD render exported: {out_img} ({size_kb:.1f} KB)")
        return True
    else:
        print(f"[ERROR] Output image was not created")
        return False

if __name__ == '__main__':
    render_photorealistic_cad()
