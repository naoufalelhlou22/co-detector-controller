import math
import os
import subprocess
import sys

_kicad_py = r"C:\Program Files\KiCad\10.0\bin\python.exe"
_kicad_sp = r"C:\Program Files\KiCad\10.0\bin\Lib\site-packages"
if _kicad_sp not in sys.path and os.path.isdir(_kicad_sp):
    sys.path.insert(0, _kicad_sp)
try:
    import pcbnew
except ImportError:
    if os.path.isfile(_kicad_py) and os.path.normcase(sys.executable) != os.path.normcase(_kicad_py):
        raise SystemExit(subprocess.call([_kicad_py, *sys.argv]))
    raise

proj_dir = r"C:\Users\Mr_X\.gemini\antigravity\scratch\co_detector_controller"
custom_lib = os.path.join(proj_dir, "custom_lib.pretty")
os.makedirs(custom_lib, exist_ok=True)
_seed = os.path.join(custom_lib, "_seed.kicad_mod")
with open(_seed, "w", encoding="utf-8") as f:
    f.write('(footprint "_seed")')


def safe_remove(self, item):
    self.RemoveNative(item)
    item.thisown = 0


pcbnew.FOOTPRINT.Remove = safe_remove

std_lib = r"C:\Program Files\KiCad\10.0\share\kicad\footprints"

W = 70.0
H = 50.0


def xy(x, y):
    return pcbnew.VECTOR2I(pcbnew.FromMM(float(x)), pcbnew.FromMM(float(H - y)))


def vmm(x, y):
    return pcbnew.VECTOR2I(pcbnew.FromMM(float(x)), pcbnew.FromMM(float(y)))


def add_fp_rect(fp, x1, y1, x2, y2, layer, width=0.05):
    pts = [(x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)]
    for i in range(4):
        s = pcbnew.PCB_SHAPE(fp)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetLayer(layer)
        s.SetStart(vmm(pts[i][0], pts[i][1]))
        s.SetEnd(vmm(pts[i + 1][0], pts[i + 1][1]))
        s.SetWidth(pcbnew.FromMM(width))
        fp.Add(s)


def add_fp_circle_poly(fp, r, layer, width=0.05, n=48):
    for i in range(n):
        a1 = 2.0 * math.pi * i / n
        a2 = 2.0 * math.pi * (i + 1) / n
        s = pcbnew.PCB_SHAPE(fp)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetLayer(layer)
        s.SetStart(vmm(r * math.cos(a1), r * math.sin(a1)))
        s.SetEnd(vmm(r * math.cos(a2), r * math.sin(a2)))
        s.SetWidth(pcbnew.FromMM(width))
        fp.Add(s)


def add_fp_line(fp, x1, y1, x2, y2, layer, width=0.15):
    s = pcbnew.PCB_SHAPE(fp)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetLayer(layer)
    s.SetStart(vmm(x1, y1))
    s.SetEnd(vmm(x2, y2))
    s.SetWidth(pcbnew.FromMM(width))
    fp.Add(s)


# 1. Build ESP32-C3-MINI-1.kicad_mod (origin shifted to geometric center of 13.2x16.6mm module)
# In stock ESP32-C6-MINI-1, silkscreen is y in [-11.15, +5.75] (center at y = -2.70).
# Shifting all items by dy = +2.50 puts pads in y_local in [-2.80, +7.80] and antenna in [-8.65, -3.00].
# When placed at (36.0, 41.0), pads sit in y_cartesian in [33.20, 43.80] (strictly below y=44 antenna keepout!)
# and antenna sits in y_cartesian in [44.00, 49.65] (inside x 29..43, y 44..50 keepout!).
fp_esp = pcbnew.FootprintLoad(os.path.join(std_lib, "RF_Module.pretty"), "ESP32-C6-MINI-1")
fp_esp.SetFPID(pcbnew.LIB_ID("custom_lib", "ESP32-C3-MINI-1"))
shift = vmm(0.0, 2.50)
for p in fp_esp.Pads():
    p.SetPosition(p.GetPosition() + shift)
for item in list(fp_esp.GraphicalItems()):
    if item.GetLayer() in [pcbnew.F_CrtYd, pcbnew.B_CrtYd]:
        fp_esp.Remove(item)
    else:
        item.Move(shift)
# Add clean courtyard around the module body (-6.80..+6.80, -8.70..+8.30)
add_fp_rect(fp_esp, -6.80, -8.70, 6.80, 8.30, pcbnew.F_CrtYd, 0.05)
# Pin 1 dot on SilkS
add_fp_line(fp_esp, -6.95, -1.8, -6.95, -1.2, pcbnew.F_SilkS, 0.25)
pcbnew.FootprintSave(custom_lib, fp_esp)

# 2. Build Winsen_ME3-CO_Socket.kicad_mod (D=20.0mm body, 3 THT socket pins for WE, RE, CE)
fp_s1 = pcbnew.FootprintLoad(os.path.join(std_lib, "TestPoint.pretty"), "TestPoint_Pad_D1.5mm")
fp_s1.SetFPID(pcbnew.LIB_ID("custom_lib", "Winsen_ME3-CO_Socket"))
for p in list(fp_s1.Pads()):
    fp_s1.Remove(p)
for item in list(fp_s1.GraphicalItems()):
    fp_s1.Remove(item)
fp_s1.SetAttributes(pcbnew.FP_THROUGH_HOLE)

# 3 socket receptacles inside upper semicircle facing U3:
# Pin 1 = WE (-2.5, -5.5), Pin 2 = RE (0.0, -6.5), Pin 3 = CE (+2.5, -5.5) in local KiCad coords (Y-down, so -Y is up toward U3!)
for num, px, py in [("1", -2.5, -5.5), ("2", 0.0, -6.5), ("3", 2.5, -5.5)]:
    pad = pcbnew.PAD(fp_s1)
    pad.SetNumber(num)
    pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
    pad.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
    pad.SetLayerSet(pcbnew.PAD.PTHMask())
    pad.SetSize(vmm(2.4, 2.4))
    pad.SetDrillSize(vmm(1.4, 1.4))
    pad.SetPosition(vmm(px, py))
    fp_s1.Add(pad)

add_fp_circle_poly(fp_s1, 10.0, pcbnew.F_SilkS, 0.15, 64)
add_fp_circle_poly(fp_s1, 10.0, pcbnew.F_Fab, 0.10, 64)
add_fp_circle_poly(fp_s1, 10.15, pcbnew.F_CrtYd, 0.05, 64)
pcbnew.FootprintSave(custom_lib, fp_s1)

# 3. Build TerminalBlock_2P_P5.08mm_Centered.kicad_mod
fp_tb = pcbnew.FootprintLoad(
    os.path.join(std_lib, "TerminalBlock_Phoenix.pretty"),
    "TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal",
)
fp_tb.SetFPID(pcbnew.LIB_ID("custom_lib", "TerminalBlock_2P_P5.08mm_Centered"))
tb_shift = vmm(-2.54, 0.0)
for p in fp_tb.Pads():
    p.SetPosition(p.GetPosition() + tb_shift)
for item in list(fp_tb.GraphicalItems()):
    if item.GetLayer() in [pcbnew.F_CrtYd, pcbnew.B_CrtYd]:
        fp_tb.Remove(item)
    else:
        item.Move(tb_shift)
# True mechanical courtyard around 2-pin 5.08mm block (-5.2..+5.2 along pins, -4.6..+4.6 across body)
add_fp_rect(fp_tb, -5.25, -4.60, 5.25, 4.60, pcbnew.F_CrtYd, 0.05)
# '+' mark near Pin 1 (-2.54, 0)
add_fp_line(fp_tb, -4.5, -3.6, -3.7, -3.6, pcbnew.F_SilkS, 0.18)
add_fp_line(fp_tb, -4.1, -4.0, -4.1, -3.2, pcbnew.F_SilkS, 0.18)
pcbnew.FootprintSave(custom_lib, fp_tb)

# 4. Build PinHeader_1x04_P2.54mm_Centered.kicad_mod
fp_hdr = pcbnew.FootprintLoad(
    os.path.join(std_lib, "Connector_PinHeader_2.54mm.pretty"),
    "PinHeader_1x04_P2.54mm_Vertical",
)
fp_hdr.SetFPID(pcbnew.LIB_ID("custom_lib", "PinHeader_1x04_P2.54mm_Centered"))
hdr_shift = vmm(0.0, -3.81)
for p in fp_hdr.Pads():
    p.SetPosition(p.GetPosition() + hdr_shift)
for item in list(fp_hdr.GraphicalItems()):
    if item.GetLayer() in [pcbnew.F_CrtYd, pcbnew.B_CrtYd]:
        fp_hdr.Remove(item)
    else:
        item.Move(hdr_shift)
add_fp_rect(fp_hdr, -1.50, -5.30, 1.50, 5.30, pcbnew.F_CrtYd, 0.05)
pcbnew.FootprintSave(custom_lib, fp_hdr)

# 5. Build Buzzer_TDK_PS1240P02BT_Centered.kicad_mod
fp_bz = pcbnew.FootprintLoad(
    os.path.join(std_lib, "Buzzer_Beeper.pretty"),
    "Buzzer_TDK_PS1240P02BT_D12.2mm_H6.5mm",
)
fp_bz.SetFPID(pcbnew.LIB_ID("custom_lib", "Buzzer_TDK_PS1240P02BT_Centered"))
bz_shift = vmm(-2.50, 0.0)
for p in fp_bz.Pads():
    p.SetPosition(p.GetPosition() + bz_shift)
for item in list(fp_bz.GraphicalItems()):
    if item.GetLayer() in [pcbnew.F_CrtYd, pcbnew.B_CrtYd]:
        fp_bz.Remove(item)
    else:
        item.Move(bz_shift)
add_fp_circle_poly(fp_bz, 6.25, pcbnew.F_CrtYd, 0.05, 48)
# '+' polarity symbol near Pin 1
add_fp_line(fp_bz, -4.3, 0.0, -3.5, 0.0, pcbnew.F_SilkS, 0.18)
add_fp_line(fp_bz, -3.9, -0.4, -3.9, 0.4, pcbnew.F_SilkS, 0.18)
pcbnew.FootprintSave(custom_lib, fp_bz)

# 6. Build courtyard-equipped NetTie, TestPoint, Fiducial, MountingHole
for lib_sub, fp_name, new_name, crtyd_r in [
    ("NetTie.pretty", "NetTie-2_SMD_Pad0.5mm", "NetTie-2_SMD_Pad0.5mm_CrtYd", 0.90),
    ("TestPoint.pretty", "TestPoint_Pad_D1.5mm", "TestPoint_Pad_D1.5mm_CrtYd", 0.95),
    ("Fiducial.pretty", "Fiducial_1mm_Mask2mm", "Fiducial_1mm_Mask2mm_CrtYd", 1.15),
    ("MountingHole.pretty", "MountingHole_3.2mm_M3", "MountingHole_3.2mm_M3_CrtYd", 3.10),
]:
    fp_tmp = pcbnew.FootprintLoad(os.path.join(std_lib, lib_sub), fp_name)
    fp_tmp.SetFPID(pcbnew.LIB_ID("custom_lib", new_name))
    for item in list(fp_tmp.GraphicalItems()):
        if item.GetLayer() in [pcbnew.F_CrtYd, pcbnew.B_CrtYd]:
            fp_tmp.Remove(item)
    add_fp_circle_poly(fp_tmp, crtyd_r, pcbnew.F_CrtYd, 0.05, 32)
    pcbnew.FootprintSave(custom_lib, fp_tmp)

if os.path.exists(_seed):
    os.remove(_seed)

print("All custom footprints saved to:", custom_lib)

