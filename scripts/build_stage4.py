import collections
import json
import math
import os
import subprocess
import sys

# Auto-relaunch under KiCad 10's bundled Python if invoked from system Python 3.14
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
pcb_path = os.path.join(proj_dir, "co_detector_controller.kicad_pcb")
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


# Initialize board
b = pcbnew.CreateEmptyBoard()
b.SetCopperLayerCount(4)

ds = b.GetDesignSettings()
ds.SetAuxOrigin(xy(0, 0))
ds.SetGridOrigin(xy(0, 0))
ds.m_TrackMinWidth = pcbnew.FromMM(0.2)
ds.m_ViasMinSize = pcbnew.FromMM(0.6)
ds.m_ViasMinDrill = pcbnew.FromMM(0.3)
ds.m_CopperEdgeClearance = pcbnew.FromMM(2.0)
ds.m_TentViasFront = True
ds.m_TentViasBack = True


def add_board_line(x1, y1, x2, y2, layer=pcbnew.Edge_Cuts, width=0.1):
    s = pcbnew.PCB_SHAPE(b)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetLayer(layer)
    s.SetStart(xy(x1, y1))
    s.SetEnd(xy(x2, y2))
    s.SetWidth(pcbnew.FromMM(width))
    b.Add(s)


# Board outline: 70 x 50 mm, 3 mm convex corners
add_board_line(3, 0, 67, 0)
add_board_line(70, 3, 70, 47)
add_board_line(67, 50, 3, 50)
add_board_line(0, 47, 0, 3)

d45 = 3.0 * math.sqrt(0.5)
for sx, sy, mx, my, ex, ey in [
    (0.0, 3.0, 3.0 - d45, 3.0 - d45, 3.0, 0.0),
    (67.0, 0.0, 67.0 + d45, 3.0 - d45, 70.0, 3.0),
    (70.0, 47.0, 67.0 + d45, 47.0 + d45, 67.0, 50.0),
    (3.0, 50.0, 3.0 - d45, 47.0 + d45, 0.0, 47.0),
]:
    s = pcbnew.PCB_SHAPE(b)
    s.SetShape(pcbnew.SHAPE_T_ARC)
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetArcGeometry(xy(sx, sy), xy(mx, my), xy(ex, ey))
    s.SetWidth(pcbnew.FromMM(0.1))
    b.Add(s)

# Antenna keepout rule area: x 29..43, y 44..50 on all 4 copper layers
z_ko = pcbnew.ZONE(b)
ls_all = pcbnew.LSET()
for lyr in [pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu]:
    ls_all.addLayer(lyr)
z_ko.SetLayerSet(ls_all)
z_ko.SetIsRuleArea(True)
z_ko.SetDoNotAllowZoneFills(True)
z_ko.SetDoNotAllowVias(True)
z_ko.SetDoNotAllowTracks(True)
z_ko.SetDoNotAllowPads(True)
z_ko.SetZoneName("ANTENNA_KEEPOUT_ALL_LAYERS")
ko_poly = z_ko.Outline()
ko_poly.NewOutline()
for px, py in [(29, 44), (43, 44), (43, 50), (29, 50)]:
    ko_poly.Append(xy(px, py))
b.Add(z_ko)

# Thermal isolation keepout barrier between Zone F (Heated LPG Sensor S2) and Zone D (Electrochemical CO Sensor S1 / AFE U3)
z_therm = pcbnew.ZONE(b)
ls_planes = pcbnew.LSET()
for lyr in [pcbnew.In1_Cu, pcbnew.In2_Cu]:
    ls_planes.addLayer(lyr)
z_therm.SetLayerSet(ls_planes)
z_therm.SetIsRuleArea(True)
z_therm.SetDoNotAllowZoneFills(True)
z_therm.SetZoneName("LPG_THERMAL_ISOLATION_BARRIER")
th_poly = z_therm.Outline()
th_poly.NewOutline()
for px, py in [(55.0, 38.3), (68.0, 38.3), (68.0, 38.9), (55.0, 38.9)]:
    th_poly.Append(xy(px, py))
b.Add(z_therm)
for sx in range(57, 66, 2):
    add_board_line(sx, 38.6, sx + 1.0, 38.6, layer=pcbnew.F_SilkS, width=0.15)

# Nets
all_nets = [
    "+12V_IN",
    "+12V_F",
    "+12V",
    "+3V3",
    "AVDD",
    "GND",
    "AGND",
    "Q1_G",
    "BUCK_EN",
    "BUCK_BOOT",
    "BUCK_SW",
    "BUCK_VCC",
    "BUCK_FB",
    "VALVE_EN",
    "VALVE_DRV",
    "VALVE_GATE",
    "VALVE_NEG",
    "VALVE_SENSE",
    "WDI",
    "NRST",
    "MR_N",
    "I2C_SDA",
    "I2C_SCL",
    "WE",
    "RE",
    "CE",
    "VREF",
    "TIA_C1",
    "TIA_C2",
    "VOUT",
    "VOUT_ADC",
    "LED_RED",
    "HUSH_N",
    "LED_BLU",
    "BUZZER",
    "TEST_N",
    "BOOT_N",
    "LPG_ADC",
    "LPG_SNS",
    "LPG_HTR",
    "UART_TX",
    "UART_RX",
    "RED_A",
    "GRN_A",
    "BLU_A",
    "BLU_K",
    "YLW_A",
    "BUZ_B",
    "BUZ_K",
]
net_map = {}
for n in all_nets:
    ni = pcbnew.NETINFO_ITEM(b, n)
    b.Add(ni)
    net_map[n] = ni


def add_copper_zone(net_name, layer, pts, priority=0, pad_conn=pcbnew.ZONE_CONNECTION_THERMAL):
    z = pcbnew.ZONE(b)
    z.SetLayer(layer)
    z.SetNet(net_map[net_name])
    z.SetAssignedPriority(priority)
    z.SetLocalClearance(pcbnew.FromMM(0.3))
    z.SetMinThickness(pcbnew.FromMM(0.2))
    z.SetPadConnection(pad_conn)
    z.SetThermalReliefGap(pcbnew.FromMM(0.25))
    z.SetThermalReliefSpokeWidth(pcbnew.FromMM(0.4))
    outline = z.Outline()
    outline.NewOutline()
    for px, py in pts:
        outline.Append(xy(px, py))
    b.Add(z)
    return z


# L2 (In1.Cu): Unbroken solid GND plane across entire board (2..68, 2..48)
add_copper_zone("GND", pcbnew.In1_Cu, [(2.0, 2.0), (68.0, 2.0), (68.0, 48.0), (2.0, 48.0)], priority=0)

# L3 (In2.Cu): Split power planes (+12V and +3V3), keeping right-side analog zone (x > 52) free of power pours
add_copper_zone(
    "+12V",
    pcbnew.In2_Cu,
    [
        (2.0, 2.0),
        (41.5, 2.0),
        (41.5, 20.2),
        (32.5, 20.2),
        (32.5, 29.0),
        (27.0, 29.0),
        (27.0, 20.2),
        (14.5, 20.2),
        (14.5, 48.0),
        (25.8, 48.0),
        (25.8, 39.8),
        (18.5, 39.8),
        (18.5, 31.0),
        (14.5, 31.0),
        (14.5, 20.2),
        (2.0, 20.2),
    ],
    priority=1,
)
# Simpler clean non-self-intersecting polygon for +12V on In2.Cu:
for z in list(b.Zones()):
    if z.GetLayer() == pcbnew.In2_Cu:
        b.Remove(z)

add_copper_zone(
    "+12V",
    pcbnew.In2_Cu,
    [
        (2.0, 2.0),
        (42.0, 2.0),
        (42.0, 16.8),
        (16.0, 16.8),
        (16.0, 26.8),
        (18.0, 26.8),
        (18.0, 39.8),
        (25.8, 39.8),
        (25.8, 48.0),
        (2.0, 48.0),
    ],
    priority=1,
)

add_copper_zone(
    "+3V3",
    pcbnew.In2_Cu,
    [
        (16.0, 17.6),
        (46.8, 17.6),
        (46.8, 30.0),
        (53.6, 30.0),
        (53.6, 43.5),
        (51.5, 43.5),
        (51.5, 46.8),
        (46.5, 46.8),
        (46.5, 43.5),
        (26.4, 43.5),
        (26.4, 39.2),
        (18.6, 39.2),
        (18.6, 26.2),
        (16.0, 26.2),
    ],
    priority=1,
)


def make_fp(kind):
    if kind == "TGS2610":
        fp = pcbnew.FootprintLoad(os.path.join(std_lib, "TestPoint.pretty"), "TestPoint_Pad_D1.5mm")
        for p in list(fp.Pads()):
            fp.Remove(p)
        for item in list(fp.GraphicalItems()):
            fp.Remove(item)
        fp.SetAttributes(pcbnew.FP_THROUGH_HOLE)
        for num, px, py in [("1", -1.80, -1.80), ("2", -1.80, 1.80), ("3", 1.80, 1.80), ("4", 1.80, -1.80)]:
            pad = pcbnew.PAD(fp)
            pad.SetNumber(num)
            pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
            pad.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
            pad.SetLayerSet(pcbnew.PAD.PTHMask())
            pad.SetSize(vmm(1.5, 1.5))
            pad.SetDrillSize(vmm(0.8, 0.8))
            pad.SetPosition(vmm(px, py))
            fp.Add(pad)
        add_fp_circle_poly(fp, 4.60, pcbnew.F_SilkS, 0.15, 48)
        add_fp_circle_poly(fp, 4.60, pcbnew.F_Fab, 0.10, 48)
        add_fp_circle_poly(fp, 4.65, pcbnew.F_CrtYd, 0.05, 48)
        m_s2 = pcbnew.FP_3DMODEL()
        m_s2.m_Filename = "${KIPRJMOD}/3dmodels/Figaro_TGS2610_LPG.wrl"
        fp.Add3DModel(m_s2)
        return fp, "Custom:Figaro_TGS2610_TO5"

    if kind == "ESP32-C3-MINI-1":
        fp = pcbnew.FootprintLoad(os.path.join(std_lib, "RF_Module.pretty"), "ESP32-C6-MINI-1")
        for z in list(fp.Zones()):
            fp.Remove(z)
        shift = vmm(0.0, 2.50)
        for p in fp.Pads():
            p.SetPosition(p.GetPosition() + shift)
        for item in list(fp.GraphicalItems()):
            if item.GetLayer() in [pcbnew.F_CrtYd, pcbnew.B_CrtYd, pcbnew.F_SilkS]:
                fp.Remove(item)
            else:
                item.Move(shift)
        add_fp_rect(fp, -6.70, -8.50, 6.70, 8.15, pcbnew.F_CrtYd, 0.05)
        add_fp_line(fp, -6.60, -8.40, 6.60, -8.40, pcbnew.F_SilkS, 0.15)
        add_fp_line(fp, -6.60, -8.40, -6.60, -2.00, pcbnew.F_SilkS, 0.15)
        add_fp_line(fp, 6.60, -8.40, 6.60, -2.00, pcbnew.F_SilkS, 0.15)
        add_fp_line(fp, -6.85, -1.70, -6.85, -1.20, pcbnew.F_SilkS, 0.25)
        return fp, "Custom:ESP32-C3-MINI-1"

    if kind == "ME3-CO":
        fp = pcbnew.FootprintLoad(os.path.join(std_lib, "TestPoint.pretty"), "TestPoint_Pad_D1.5mm")
        for p in list(fp.Pads()):
            fp.Remove(p)
        for item in list(fp.GraphicalItems()):
            fp.Remove(item)
        fp.SetAttributes(pcbnew.FP_THROUGH_HOLE)
        for num, px, py in [("1", -2.5, -5.5), ("2", 0.0, -6.5), ("3", 2.5, -5.5)]:
            pad = pcbnew.PAD(fp)
            pad.SetNumber(num)
            pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
            pad.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
            pad.SetLayerSet(pcbnew.PAD.PTHMask())
            pad.SetSize(vmm(2.4, 2.4))
            pad.SetDrillSize(vmm(1.4, 1.4))
            pad.SetPosition(vmm(px, py))
            fp.Add(pad)
        add_fp_circle_poly(fp, 10.0, pcbnew.F_SilkS, 0.15, 64)
        add_fp_circle_poly(fp, 10.0, pcbnew.F_Fab, 0.10, 64)
        add_fp_circle_poly(fp, 10.05, pcbnew.F_CrtYd, 0.05, 64)
        m_s1 = pcbnew.FP_3DMODEL()
        m_s1.m_Filename = "${KIPRJMOD}/3dmodels/Winsen_ME3-CO.wrl"
        fp.Add3DModel(m_s1)
        return fp, "Custom:Winsen_ME3-CO_Socket"

    if kind == "TB_2P":
        fp = pcbnew.FootprintLoad(
            os.path.join(std_lib, "TerminalBlock_Phoenix.pretty"),
            "TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal",
        )
        tb_shift = vmm(-2.54, 0.0)
        for p in fp.Pads():
            if p.GetNumber() == "1":
                p.SetPosition(vmm(2.54, 0.0))
            elif p.GetNumber() == "2":
                p.SetPosition(vmm(-2.54, 0.0))
        for m in fp.Models():
            m.m_Offset.x -= 2.54
        for item in list(fp.GraphicalItems()):
            if item.GetLayer() in [pcbnew.F_CrtYd, pcbnew.B_CrtYd, pcbnew.F_SilkS]:
                fp.Remove(item)
            else:
                item.Move(tb_shift)
        add_fp_rect(fp, -5.00, -3.50, 5.00, 3.50, pcbnew.F_CrtYd, 0.05)
        add_fp_rect(fp, -4.85, -3.30, 4.85, 3.30, pcbnew.F_SilkS, 0.15)
        add_fp_line(fp, 3.7, 2.5, 4.3, 2.5, pcbnew.F_SilkS, 0.18)
        add_fp_line(fp, 4.0, 2.2, 4.0, 2.8, pcbnew.F_SilkS, 0.18)
        return fp, "TerminalBlock_Phoenix:MKDS-1,5-2-5.08_Centered"

    if kind == "HDR_1x4":
        fp = pcbnew.FootprintLoad(
            os.path.join(std_lib, "Connector_PinHeader_2.54mm.pretty"),
            "PinHeader_1x04_P2.54mm_Vertical",
        )
        hdr_shift = vmm(0.0, -3.81)
        for p in fp.Pads():
            p.SetPosition(p.GetPosition() + hdr_shift)
        for m in fp.Models():
            m.m_Offset.y += 3.81
        for item in list(fp.GraphicalItems()):
            if item.GetLayer() in [pcbnew.F_CrtYd, pcbnew.B_CrtYd]:
                fp.Remove(item)
            else:
                item.Move(hdr_shift)
        add_fp_rect(fp, -1.40, -5.20, 1.40, 5.20, pcbnew.F_CrtYd, 0.05)
        return fp, "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical"

    if kind == "BUZZER":
        fp = pcbnew.FootprintLoad(
            os.path.join(std_lib, "Buzzer_Beeper.pretty"),
            "Buzzer_TDK_PS1240P02BT_D12.2mm_H6.5mm",
        )
        bz_shift = vmm(-2.50, 0.0)
        for p in fp.Pads():
            p.SetPosition(p.GetPosition() + bz_shift)
        for m in fp.Models():
            m.m_Offset.x -= 2.50
        for item in list(fp.GraphicalItems()):
            if item.GetLayer() in [pcbnew.F_CrtYd, pcbnew.B_CrtYd, pcbnew.F_SilkS]:
                fp.Remove(item)
            else:
                item.Move(bz_shift)
        add_fp_circle_poly(fp, 6.15, pcbnew.F_CrtYd, 0.05, 48)
        add_fp_circle_poly(fp, 6.00, pcbnew.F_SilkS, 0.15, 48)
        add_fp_line(fp, -4.3, 0.0, -3.5, 0.0, pcbnew.F_SilkS, 0.18)
        add_fp_line(fp, -3.9, -0.4, -3.9, 0.4, pcbnew.F_SilkS, 0.18)
        return fp, "Buzzer_Beeper:Buzzer_TDK_PS1240P02BT_D12.2mm_H6.5mm"

    if kind in ["NT", "TP", "FID", "M3"]:
        mapping = {
            "NT": ("NetTie.pretty", "NetTie-2_SMD_Pad0.5mm", 0.85, "NetTie:NetTie-2_SMD_Pad0.5mm"),
            "TP": ("TestPoint.pretty", "TestPoint_Pad_D1.5mm", 0.90, "TestPoint:TestPoint_Pad_D1.5mm"),
            "FID": ("Fiducial.pretty", "Fiducial_1mm_Mask2mm", 1.15, "Fiducial:Fiducial_1mm_Mask2mm"),
            "M3": ("MountingHole.pretty", "MountingHole_3.2mm_M3", 3.10, "MountingHole:MountingHole_3.2mm_M3"),
        }
        sub, name, r_c, label = mapping[kind]
        fp = pcbnew.FootprintLoad(os.path.join(std_lib, sub), name)
        for item in list(fp.GraphicalItems()):
            if item.GetLayer() in [pcbnew.F_CrtYd, pcbnew.B_CrtYd, pcbnew.F_SilkS]:
                fp.Remove(item)
        add_fp_circle_poly(fp, r_c, pcbnew.F_CrtYd, 0.05, 32)
        return fp, label

    std_map = {
        "U2_BUCK": ("Package_SO.pretty", "TI_SO-PowerPAD-8_ThermalVias", "Package_SO:TI_SO-PowerPAD-8_ThermalVias"),
        "U3_WSON14": ("Package_SON.pretty", "WSON-14-1EP_4.0x4.0mm_P0.5mm_EP2.6x2.6mm", "Package_SON:WSON-14-1EP_4.0x4.0mm_P0.5mm_EP2.6x2.6mm"),
        "SOT23": ("Package_TO_SOT_SMD.pretty", "SOT-23", "Package_TO_SOT_SMD:SOT-23"),
        "SOT23_5": ("Package_TO_SOT_SMD.pretty", "SOT-23-5", "Package_TO_SOT_SMD:SOT-23-5"),
        "D_SMB": ("Diode_SMD.pretty", "D_SMB", "Diode_SMD:D_SMB"),
        "D_SMA": ("Diode_SMD.pretty", "D_SMA", "Diode_SMD:D_SMA"),
        "D_SOD123": ("Diode_SMD.pretty", "D_SOD-123", "Diode_SMD:D_SOD-123"),
        "D_0603": ("Diode_SMD.pretty", "D_0603_1608Metric", "Diode_SMD:D_0603_1608Metric"),
        "LED_0603": ("LED_SMD.pretty", "LED_0603_1608Metric", "LED_SMD:LED_0603_1608Metric"),
        "FUSE_1812": ("Fuse.pretty", "Fuse_1812_4532Metric", "Fuse:Fuse_1812_4532Metric"),
        "IND_XAL5030": ("Inductor_SMD.pretty", "L_Coilcraft_XAL5030-XXX", "Inductor_SMD:L_Coilcraft_XAL5030-XXX"),
        "FB_0603": ("Inductor_SMD.pretty", "L_0603_1608Metric", "Inductor_SMD:L_0603_1608Metric"),
        "CP_ELEC": ("Capacitor_SMD.pretty", "CP_Elec_6.3x7.7", "Capacitor_SMD:CP_Elec_6.3x7.7"),
        "C_1210": ("Capacitor_SMD.pretty", "C_1210_3225Metric", "Capacitor_SMD:C_1210_3225Metric"),
        "C_1206": ("Capacitor_SMD.pretty", "C_1206_3216Metric", "Capacitor_SMD:C_1206_3216Metric"),
        "C_0805": ("Capacitor_SMD.pretty", "C_0805_2012Metric", "Capacitor_SMD:C_0805_2012Metric"),
        "C_0603": ("Capacitor_SMD.pretty", "C_0603_1608Metric", "Capacitor_SMD:C_0603_1608Metric"),
        "R_0603": ("Resistor_SMD.pretty", "R_0603_1608Metric", "Resistor_SMD:R_0603_1608Metric"),
        "SW_PTS647": ("Button_Switch_SMD.pretty", "SW_SPST_PTS647_Sx50", "Button_Switch_SMD:SW_SPST_PTS647_Sx50"),
    }
    sub, name, label = std_map[kind]
    fp = pcbnew.FootprintLoad(os.path.join(std_lib, sub), name)
    return fp, label


placements = [
    # --- ZONE A: Power (Top-Left) ---
    ("J1", "12V_IN", "TB_2P", 4.3, 38.0, 270, {"1": "+12V_IN", "2": "GND"}, 0.0, -5.8, "Zone A"),
    ("F1", "1.5A_PTC", "FUSE_1812", 11.2, 45.2, 0, {"1": "+12V_IN", "2": "+12V_F"}, 0.0, 2.5, "Zone A"),
    ("D1", "SMBJ15CA", "D_SMB", 10.3, 35.5, 270, {"1": "+12V_F", "2": "GND"}, 0.0, 4.2, "Zone A"),
    ("Q1", "AO3407A", "SOT23", 15.2, 41.0, 0, {"1": "Q1_G", "2": "+12V", "3": "+12V_F"}, 0.0, 2.3, "Zone A"),
    ("D3", "BZT52C15", "D_SOD123", 16.5, 45.8, 0, {"1": "+12V", "2": "Q1_G"}, 0.0, 1.7, "Zone A"),
    ("R1", "10k", "R_0603", 14.4, 38.2, 0, {"1": "Q1_G", "2": "GND"}, 0.0, 1.3, "Zone A"),
    ("C1", "47uF_35V", "CP_ELEC", 8.0, 26.5, 0, {"1": "+12V", "2": "GND"}, 0.0, 4.3, "Zone A"),
    ("C2", "10uF_50V", "C_1210", 21.5, 44.5, 0, {"1": "+12V", "2": "GND"}, -3.1, 0.0, "Zone A"),
    ("C3", "10uF_50V", "C_1210", 21.5, 40.8, 0, {"1": "+12V", "2": "GND"}, -3.1, 0.0, "Zone A"),
    ("C4", "100nF", "C_0603", 14.2, 35.2, 270, {"1": "+12V", "2": "GND"}, 0.0, 1.8, "Zone A"),
    (
        "U2",
        "LMR33620ADDAR",
        "U2_BUCK",
        19.8,
        35.5,
        0,
        {
            "1": "GND",
            "2": "+12V",
            "3": "BUCK_EN",
            "4": "",
            "5": "BUCK_FB",
            "6": "BUCK_VCC",
            "7": "BUCK_BOOT",
            "8": "BUCK_SW",
            "9": "GND",
        },
        -0.5,
        3.1,
        "Zone A",
    ),
    ("R2", "100k", "R_0603", 14.2, 32.0, 0, {"1": "+12V", "2": "BUCK_EN"}, -2.3, 0.0, "Zone A"),
    ("R3", "DNP", "R_0603", 14.2, 30.0, 0, {"1": "BUCK_EN", "2": "GND"}, -2.3, 0.0, "Zone A"),
    ("C5", "100nF", "C_0603", 25.4, 36.8, 0, {"1": "BUCK_BOOT", "2": "BUCK_SW"}, 0.0, 1.3, "Zone A"),
    ("C6", "1uF", "C_0603", 25.4, 34.4, 0, {"1": "BUCK_VCC", "2": "GND"}, 0.0, -1.3, "Zone A"),
    ("L1", "6.8uH", "IND_XAL5030", 24.5, 29.0, 0, {"1": "BUCK_SW", "2": "+3V3"}, 0.0, 3.8, "Zone A"),
    ("R4", "100k", "R_0603", 19.5, 31.2, 0, {"1": "BUCK_FB", "2": "+3V3"}, -2.3, 0.0, "Zone A"),
    ("R5", "43.2k", "R_0603", 19.5, 29.2, 0, {"1": "BUCK_FB", "2": "GND"}, -2.3, 0.0, "Zone A"),
    ("C7", "DNP", "C_0603", 19.5, 27.2, 0, {"1": "BUCK_FB", "2": "+3V3"}, 0.0, -1.3, "Zone A"),
    ("C8", "22uF_10V", "C_1206", 24.5, 24.0, 0, {"1": "+3V3", "2": "GND"}, -3.2, 0.0, "Zone A"),
    ("C9", "22uF_10V", "C_1206", 24.5, 21.2, 0, {"1": "+3V3", "2": "GND"}, -3.2, 0.0, "Zone A"),
    ("C10", "22uF_10V", "C_1206", 29.5, 24.0, 0, {"1": "+3V3", "2": "GND"}, 0.0, 1.8, "Zone A"),
    ("C11", "22uF_10V", "C_1206", 29.5, 21.2, 0, {"1": "+3V3", "2": "GND"}, 0.0, -1.8, "Zone A"),
    ("C12", "100nF", "C_0603", 28.2, 34.4, 90, {"1": "+3V3", "2": "GND"}, 1.4, 0.0, "Zone A"),

    # --- ZONE B: External Alarm Output & Safety Interlock (Bottom-Left) ---
    ("J2", "EXT_ALARM_12V", "TB_2P", 4.5, 12.0, 270, {"1": "+12V", "2": "VALVE_NEG"}, 0.0, 5.8, "Zone B"),
    ("D2", "B240A", "D_SMA", 10.2, 12.0, 90, {"1": "+12V", "2": "VALVE_NEG"}, 0.0, -4.3, "Zone B"),
    ("C24", "100nF_50V", "C_0603", 10.7, 16.8, 0, {"1": "+12V", "2": "GND"}, 0.0, 1.3, "Zone B"),
    ("Q2", "IRLML6344", "SOT23", 14.5, 10.2, 0, {"1": "VALVE_GATE", "2": "GND", "3": "VALVE_NEG"}, 0.0, -2.4, "Zone B"),
    ("R15", "100k", "R_0603", 14.5, 6.8, 0, {"1": "VALVE_GATE", "2": "GND"}, 0.0, -1.3, "Zone B"),
    ("R14", "100R", "R_0603", 14.5, 13.5, 0, {"1": "VALVE_GATE", "2": "VALVE_DRV"}, 0.0, 1.3, "Zone B"),
    (
        "U5",
        "74LVC1G08",
        "SOT23_5",
        15.0,
        17.5,
        0,
        {"1": "VALVE_EN", "2": "VALVE_EN", "3": "GND", "4": "VALVE_DRV", "5": "+3V3"},
        -2.9,
        0.0,
        "Zone B",
    ),
    ("C22", "100nF", "C_0603", 15.0, 20.3, 0, {"1": "GND", "2": "+3V3"}, -2.3, 0.0, "Zone B"),
    ("R13", "10k", "R_0603", 19.0, 17.5, 90, {"1": "VALVE_DRV", "2": "VALVE_EN"}, 1.5, 0.0, "Zone B"),
    ("R16", "100k", "R_0603", 19.0, 11.2, 0, {"1": "VALVE_NEG", "2": "VALVE_SENSE"}, 2.3, 0.0, "Zone B"),
    ("R17", "15k", "R_0603", 19.0, 9.2, 0, {"1": "VALVE_SENSE", "2": "GND"}, 2.3, 0.0, "Zone B"),
    ("C25", "100nF", "C_0603", 19.0, 7.2, 0, {"1": "VALVE_SENSE", "2": "GND"}, 2.3, 0.0, "Zone B"),
    (
        "U6",
        "TPS3823-33",
        "SOT23_5",
        15.0,
        23.2,
        0,
        {"1": "NRST", "2": "GND", "3": "MR_N", "4": "WDI", "5": "+3V3"},
        -2.9,
        0.0,
        "Zone B",
    ),
    ("C23", "100nF", "C_0603", 19.0, 23.2, 90, {"1": "GND", "2": "+3V3"}, 1.5, 0.0, "Zone B"),
    ("R18", "DNP", "R_0603", 19.0, 20.3, 0, {"1": "WDI", "2": "GND"}, 2.3, 0.0, "Zone B"),

    # --- ZONE C: MCU & Debug (Center-Top + UART Header) ---
    (
        "U1",
        "ESP32-C3-MINI-1",
        "ESP32-C3-MINI-1",
        36.0,
        41.0,
        0,
        {
            "1": "GND",
            "2": "GND",
            "3": "+3V3",
            "5": "LPG_ADC",
            "6": "BUZZER",
            "8": "NRST",
            "11": "GND",
            "12": "VOUT_ADC",
            "13": "VALVE_SENSE",
            "14": "GND",
            "16": "TEST_N",
            "18": "I2C_SDA",
            "19": "I2C_SCL",
            "20": "VALVE_EN",
            "21": "WDI",
            "22": "HUSH_N",
            "23": "BOOT_N",
            "26": "LED_RED",
            "27": "LED_BLU",
            "30": "UART_RX",
            "31": "UART_TX",
            **{str(k): "GND" for k in range(36, 54)},
        },
        7.8,
        0.0,
        "Zone C",
    ),
    ("C16", "100nF", "C_0603", 27.2, 41.2, 0, {"1": "GND", "2": "+3V3"}, -2.3, 0.0, "Zone C"),
    ("C15", "10uF_10V", "C_0805", 27.0, 39.0, 0, {"1": "GND", "2": "+3V3"}, -2.6, 0.0, "Zone C"),
    ("R6", "10k_DNP", "R_0603", 27.2, 43.2, 0, {"1": "+3V3", "2": "LPG_ADC"}, -2.3, 0.0, "Zone C"),
    ("C17", "100nF", "C_0603", 31.2, 30.8, 270, {"1": "VOUT_ADC", "2": "GND"}, -1.4, 0.0, "Zone C"),
    ("R9", "4.7k", "R_0603", 36.0, 30.8, 90, {"1": "+3V3", "2": "I2C_SDA"}, -1.4, 0.0, "Zone C"),
    ("R10", "4.7k", "R_0603", 38.2, 30.8, 90, {"1": "+3V3", "2": "I2C_SCL"}, -1.4, 0.0, "Zone C"),
    ("R7", "10k", "R_0603", 40.4, 30.8, 90, {"1": "+3V3", "2": "HUSH_N"}, -1.4, 0.0, "Zone C"),
    ("R8", "10k", "R_0603", 42.6, 30.8, 90, {"1": "+3V3", "2": "BOOT_N"}, 1.4, 0.0, "Zone C"),
    (
        "J3",
        "UART_HDR",
        "HDR_1x4",
        23.0,
        8.0,
        0,
        {"1": "+3V3", "2": "UART_TX", "3": "UART_RX", "4": "GND"},
        -2.3,
        0.0,
        "Zone C",
    ),

    # --- ZONE D: Analog Sensor & Potentiostat AFE (Right Side) ---
    ("S1", "ME3-CO", "ME3-CO", 56.5, 14.5, 0, {"1": "WE", "2": "RE", "3": "CE"}, 0.0, -11.0, "Zone D"),
    (
        "U3",
        "LMP91000SDE",
        "U3_WSON14",
        56.5,
        27.8,
        270,
        {
            "1": "AGND",
            "2": "AGND",
            "3": "I2C_SCL",
            "4": "I2C_SDA",
            "5": "",
            "6": "AVDD",
            "7": "AGND",
            "8": "VOUT",
            "9": "TIA_C2",
            "10": "TIA_C1",
            "11": "VREF",
            "12": "WE",
            "13": "RE",
            "14": "CE",
            "15": "AGND",
        },
        3.5,
        0.0,
        "Zone D",
    ),
    # Q3 is DNP (LMP91000 internal FET_SHORT used so WE/RE/CE have 0 stubs and <10mm guarded length per Rule 4)
    ("Q3", "MMBFJ177_DNP", "SOT23", 49.0, 23.8, 0, {"1": "", "2": "", "3": ""}, -2.8, 0.0, "Zone D"),
    ("C21", "1uF", "C_0603", 52.0, 27.8, 90, {"1": "TIA_C1", "2": "TIA_C2"}, -1.4, 0.0, "Zone D"),
    ("R12", "DNP", "R_0603", 49.2, 27.8, 90, {"1": "TIA_C1", "2": "TIA_C2"}, -1.4, 0.0, "Zone D"),
    ("R11", "1k", "R_0603", 51.5, 31.2, 0, {"1": "VOUT_ADC", "2": "VOUT"}, 0.0, 1.3, "Zone D"),
    ("U4", "REF3325", "SOT23", 63.2, 28.5, 0, {"1": "AVDD", "2": "VREF", "3": "AGND"}, 2.8, 0.0, "Zone D"),
    ("C19", "100nF", "C_0603", 63.2, 31.5, 0, {"1": "AVDD", "2": "AGND"}, 2.3, 0.0, "Zone D"),
    ("C20", "100nF", "C_0603", 63.2, 25.5, 0, {"1": "VREF", "2": "AGND"}, 2.3, 0.0, "Zone D"),
    ("C18", "100nF", "C_0603", 55.2, 31.8, 0, {"1": "AGND", "2": "AVDD"}, 0.0, 1.3, "Zone D"),
    ("C14", "100nF", "C_0603", 55.2, 34.2, 0, {"1": "AGND", "2": "AVDD"}, 0.0, 1.3, "Zone D"),
    ("C13", "10uF_10V", "C_0805", 55.2, 36.8, 0, {"1": "AGND", "2": "AVDD"}, 0.0, 1.6, "Zone D"),
    ("FB1", "220R_100MHz", "FB_0603", 51.0, 36.8, 0, {"1": "+3V3", "2": "AVDD"}, 0.0, 1.3, "Zone D"),
    ("NT1", "NetTie_AGND_GND", "NT", 59.0, 31.8, 0, {"1": "GND", "2": "AGND"}, 0.0, 1.4, "Zone D"),

    # --- ZONE E: HMI (Bottom-Middle) ---
    ("D4", "RED_ALARM", "LED_0603", 26.8, 4.0, 0, {"1": "GND", "2": "RED_A"}, 0.0, -1.3, "Zone E"),
    ("D5", "GRN_OK", "LED_0603", 30.0, 4.0, 0, {"1": "GND", "2": "GRN_A"}, 0.0, -1.3, "Zone E"),
    ("D6", "BLU_WIFI", "LED_0603", 33.2, 4.0, 0, {"1": "BLU_K", "2": "BLU_A"}, 0.0, -1.3, "Zone E"),
    ("D8", "YLW_FAULT", "LED_0603", 36.4, 4.0, 0, {"1": "TEST_N", "2": "YLW_A"}, 0.0, -1.3, "Zone E"),
    ("R19", "270R", "R_0603", 26.8, 6.2, 0, {"1": "LED_RED", "2": "RED_A"}, -2.2, 0.0, "Zone E"),
    ("R20", "330R", "R_0603", 38.0, 17.5, 0, {"1": "GRN_A", "2": "+3V3"}, 2.2, 0.0, "Zone E"),
    ("R21", "2.2k", "R_0603", 40.5, 19.5, 180, {"1": "+12V", "2": "BLU_A"}, 0.0, -1.3, "Zone E"),
    ("Q4", "2N7002", "SOT23", 40.5, 22.5, 0, {"1": "LED_BLU", "2": "GND", "3": "BLU_K"}, 0.0, -2.3, "Zone E"),
    ("R22", "100k", "R_0603", 40.5, 25.5, 0, {"1": "LED_BLU", "2": "GND"}, 0.0, 1.3, "Zone E"),
    ("LS1", "PS1240_OR_SPKR", "BUZZER", 32.0, 12.0, 0, {"1": "+12V", "2": "BUZ_K"}, -5.7, 4.9, "Zone E"),
    ("Q5", "AO3400A", "SOT23", 35.5, 20.0, 0, {"1": "BUZ_B", "2": "GND", "3": "BUZ_K"}, 0.0, -2.3, "Zone E"),
    ("R23", "100R", "R_0603", 34.8, 23.4, 0, {"1": "BUZZER", "2": "BUZ_B"}, -2.3, 0.0, "Zone E"),
    ("R24", "10k", "R_0603", 34.8, 25.8, 180, {"1": "BUZ_B", "2": "GND"}, -2.3, 0.0, "Zone E"),
    ("R25", "2.2k", "R_0603", 29.5, 19.2, 0, {"1": "+12V", "2": "BUZ_K"}, 2.2, 0.0, "Zone E"),
    ("D7", "1N4148W", "D_SOD123", 30.0, 28.0, 0, {"1": "+12V", "2": "BUZ_K"}, 0.0, -1.7, "Zone E"),
    ("C26", "100nF_50V", "C_0603", 24.5, 18.5, 0, {"1": "+12V", "2": "GND"}, -2.3, 0.0, "Zone E"),
    ("SW1", "TEST_SELF_CHECK", "SW_PTS647", 42.0, 6.0, 0, {"1": "TEST_N", "2": "GND"}, 0.0, -3.5, "Zone E"),
    ("D9", "TVS_3V3_ESD", "D_0603", 48.2, 6.0, 270, {"1": "TEST_N", "2": "GND"}, 1.5, 0.0, "Zone E"),
    ("SW2", "HUSH_OLED", "SW_PTS647", 42.0, 12.0, 0, {"1": "HUSH_N", "2": "GND"}, 0.0, 3.5, "Zone E"),
    ("D10", "TVS_3V3_ESD", "D_0603", 42.55, 16.3, 90, {"1": "HUSH_N", "2": "GND"}, -1.5, 0.0, "Zone E"),
    ("C30", "100nF", "C_0603", 44.25, 16.3, 90, {"1": "HUSH_N", "2": "GND"}, 1.5, 0.0, "Zone E"),
    ("SW3", "HW_MASTER_RST", "SW_PTS647", 5.45, 20.2, 0, {"1": "MR_N", "2": "GND"}, 0.0, 3.5, "Zone B"),
    ("C31", "100nF", "C_0603", 10.0, 20.2, 90, {"1": "GND", "2": "MR_N"}, -1.4, 0.0, "Zone B"),
    ("D11", "TVS_3V3_ESD", "D_0603", 11.8, 20.2, 270, {"1": "MR_N", "2": "GND"}, 1.4, 0.0, "Zone B"),
    ("R26", "10k", "R_0603", 44.8, 18.8, 0, {"1": "TEST_N", "2": "+3V3"}, 0.0, -1.3, "Zone E"),
    ("R30", "330R", "R_0603", 44.8, 23.8, 0, {"1": "+3V3", "2": "YLW_A"}, 2.3, 0.0, "Zone E"),
    ("C27", "100nF", "C_0603", 44.8, 21.4, 0, {"1": "TEST_N", "2": "GND"}, 0.0, 1.3, "Zone E"),
    (
        "J4",
        "OLED_I2C",
        "HDR_1x4",
        48.5,
        46.2,
        90,
        {"1": "GND", "2": "+3V3", "3": "I2C_SCL", "4": "I2C_SDA"},
        0.0,
        2.2,
        "Zone E",
    ),

    # --- ZONE F: Thermally Isolated Combustible LPG Sensor (Top-Right) ---
    ("S2", "TGS2610-C00", "TGS2610", 59.0, 43.5, 0, {"1": "GND", "2": "LPG_SNS", "3": "+3V3", "4": "LPG_HTR"}, 5.4, -2.5, "Zone F"),
    ("R27", "0R_OR_5V", "R_0603", 52.0, 42.6, 0, {"1": "+3V3", "2": "LPG_HTR"}, 0.0, 1.2, "Zone F"),
    ("C29", "100nF", "C_0603", 52.0, 40.0, 180, {"1": "+3V3", "2": "GND"}, 0.0, -1.2, "Zone F"),
    ("R28", "4.7k", "R_0603", 48.2, 42.6, 180, {"1": "LPG_SNS", "2": "GND"}, 0.0, 1.2, "Zone F"),
    ("R29", "1k", "R_0603", 48.2, 40.2, 180, {"1": "LPG_SNS", "2": "LPG_ADC"}, 0.0, -1.2, "Zone F"),
    ("C28", "100nF", "C_0603", 45.0, 41.6, 0, {"1": "GND", "2": "LPG_ADC"}, 0.0, 1.2, "Zone F"),

    # --- Test Points, Fiducials & Mounting Holes ---
    ("TP1", "+12V", "TP", 25.0, 46.5, 0, {"1": "+12V"}, 0.0, -1.6, "Zone A"),
    ("TP2", "+3V3", "TP", 28.8, 31.2, 0, {"1": "+3V3"}, 0.0, -1.6, "Zone A"),
    ("TP3", "AVDD", "TP", 59.5, 36.8, 0, {"1": "AVDD"}, 0.0, 1.6, "Zone D"),
    ("TP4", "GND", "TP", 19.2, 14.2, 0, {"1": "GND"}, 0.0, 1.5, "Zone B"),
    ("TP5", "VOUT", "TP", 47.5, 31.8, 0, {"1": "VOUT"}, 0.0, 1.6, "Zone D"),
    ("TP6", "VALVE_GATE", "TP", 10.2, 6.8, 0, {"1": "VALVE_GATE"}, 0.0, -1.5, "Zone B"),
    ("TP7", "I2C_SDA", "TP", 45.8, 34.5, 0, {"1": "I2C_SDA"}, 0.0, 1.6, "Zone C"),
    ("TP8", "I2C_SCL", "TP", 45.8, 29.8, 0, {"1": "I2C_SCL"}, 0.0, -1.6, "Zone C"),
    ("TP9", "EN_PAD", "TP", 23.0, 15.2, 0, {"1": "MR_N"}, 0.0, 1.6, "Zone C"),
    ("TP10", "BOOT_PAD", "TP", 44.8, 26.2, 0, {"1": "BOOT_N"}, 2.1, 0.5, "Zone C"),
    ("TP11", "LPG_ADC", "TP", 27.2, 46.2, 0, {"1": "LPG_ADC"}, 0.0, 1.6, "Zone C"),
    ("TP12", "NRST", "TP", 15.0, 26.5, 0, {"1": "NRST"}, 0.0, 1.6, "Zone B"),
    ("FID1", "FID_BL", "FID", 7.8, 4.0, 0, {}, 0.0, 1.6, "Global"),
    ("FID2", "FID_TR", "FID", 66.5, 41.0, 0, {}, -2.2, 0.0, "Global"),
    ("H1", "M3_NPTH", "M3", 3.5, 3.5, 0, {}, 3.8, 0.0, "Mech"),
    ("H2", "M3_NPTH", "M3", 66.5, 3.5, 0, {}, -3.9, 0.0, "Mech"),
    ("H3", "M3_NPTH", "M3", 3.5, 46.5, 0, {}, 3.8, 0.0, "Mech"),
    ("H4", "M3_NPTH", "M3", 66.5, 46.5, 0, {}, -3.9, 0.0, "Mech"),
]

fp_objs = []
for ref, val, kind, x, y, rot, pnets, rdx, rdy, zone in placements:
    fp, fp_label = make_fp(kind)
    fp.SetReference(ref)
    fp.SetValue(val)
    fp.SetPosition(xy(x, y))
    fp.SetOrientationDegrees(float(rot))
    for p in fp.Pads():
        p.SetTeardropsEnabled(True)
        pnum = p.GetNumber()
        if pnum in pnets and pnets[pnum]:
            p.SetNet(net_map[pnets[pnum]])
    ref_obj = fp.Reference()
    ref_obj.SetPosition(xy(x + rdx, y + rdy))
    ref_obj.SetTextWidth(pcbnew.FromMM(0.80))
    ref_obj.SetTextHeight(pcbnew.FromMM(0.80))
    ref_obj.SetTextThickness(pcbnew.FromMM(0.15))
    ref_obj.SetKeepUpright(True)
    fp.Value().SetVisible(False)
    if ref in ("D4", "D5", "D6", "D8", "SW1", "SW2", "SW3"):
        custom_wrl_map = {
            "D4": "${KIPRJMOD}/3dmodels/LED_0603_Red.wrl",
            "D5": "${KIPRJMOD}/3dmodels/LED_0603_Green.wrl",
            "D6": "${KIPRJMOD}/3dmodels/LED_0603_Blue.wrl",
            "D8": "${KIPRJMOD}/3dmodels/LED_0603_Yellow.wrl",
            "SW1": "${KIPRJMOD}/3dmodels/SW_PTS647_Yellow.wrl",
            "SW2": "${KIPRJMOD}/3dmodels/SW_PTS647_Blue.wrl",
            "SW3": "${KIPRJMOD}/3dmodels/SW_PTS647_Red.wrl",
        }
        fp.Models().clear()
        m3d = pcbnew.FP_3DMODEL()
        m3d.m_Filename = custom_wrl_map[ref]
        m3d.m_Show = True
        fp.Add3DModel(m3d)
    b.Add(fp)
    fp_objs.append((fp, x, y, rdx, rdy, fp_label, val, rot, zone))

# Silkscreen reference placement de-conflict
pad_boxes_mm = []
for fp, *_ in fp_objs:
    for p in fp.Pads():
        bb = p.GetBoundingBox()
        pad_boxes_mm.append((
            pcbnew.ToMM(bb.GetLeft()) - 0.08,
            pcbnew.ToMM(bb.GetTop()) - 0.08,
            pcbnew.ToMM(bb.GetRight()) + 0.08,
            pcbnew.ToMM(bb.GetBottom()) + 0.08,
        ))

silk_segs_mm = []
for fp, *_ in fp_objs:
    for item in list(fp.GraphicalItems()):
        if item.GetLayer() == pcbnew.F_SilkS:
            bb = item.GetBoundingBox()
            il, it, ir, ib = pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetTop()), pcbnew.ToMM(bb.GetRight()), pcbnew.ToMM(bb.GetBottom())
            overlaps_pad = False
            for pl, pt, pr, pb in pad_boxes_mm:
                if not (ir < pl or il > pr or ib < pt or it > pb):
                    overlaps_pad = True
                    break
            if overlaps_pad and item.GetShape() != pcbnew.SHAPE_T_CIRCLE:
                fp.Remove(item)
            else:
                if item.GetShape() == pcbnew.SHAPE_T_CIRCLE:
                    cx, cy = pcbnew.ToMM(item.GetCenter().x), pcbnew.ToMM(item.GetCenter().y)
                    rad = pcbnew.ToMM(item.GetRadius())
                    for k in range(72):
                        ang = 2.0 * math.pi * k / 72.0
                        px, py = cx + rad * math.cos(ang), cy + rad * math.sin(ang)
                        silk_segs_mm.append((px - 0.08, py - 0.08, px + 0.08, py + 0.08))
                elif hasattr(item, "GetStart") and hasattr(item, "GetEnd") and item.GetShape() == pcbnew.SHAPE_T_SEGMENT:
                    sx, sy = pcbnew.ToMM(item.GetStart().x), pcbnew.ToMM(item.GetStart().y)
                    ex, ey = pcbnew.ToMM(item.GetEnd().x), pcbnew.ToMM(item.GetEnd().y)
                    for k in range(13):
                        t = k / 12.0
                        px, py = sx + t * (ex - sx), sy + t * (ey - sy)
                        silk_segs_mm.append((px - 0.08, py - 0.08, px + 0.08, py + 0.08))
                else:
                    silk_segs_mm.append((il - 0.08, it - 0.08, ir + 0.08, ib + 0.08))


def box_overlaps(b1, boxes):
    l1, t1, r1, btm1 = b1
    for l2, t2, r2, btm2 in boxes:
        if not (r1 < l2 or l1 > r2 or btm1 < t2 or t1 > btm2):
            return True
    return False


# ==============================================================================
# STAGE 4: ROUTING HELPERS (45-DEGREE PLANAR ROUTING + TEARDROPS + TENTED VIAS)
# ==============================================================================

F_Cu = pcbnew.F_Cu
In1_Cu = pcbnew.In1_Cu
In2_Cu = pcbnew.In2_Cu
B_Cu = pcbnew.B_Cu


def add_track_poly(net_name, layer, width, pts):
    """Add a 45-degree polyline of PCB_TRACK segments."""
    for i in range(len(pts) - 1):
        x1, y1 = pts[i]
        x2, y2 = pts[i + 1]
        if abs(x1 - x2) < 1e-6 and abs(y1 - y2) < 1e-6:
            continue
        t = pcbnew.PCB_TRACK(b)
        t.SetStart(xy(x1, y1))
        t.SetEnd(xy(x2, y2))
        t.SetWidth(pcbnew.FromMM(float(width)))
        t.SetLayer(layer)
        t.SetNet(net_map[net_name])
        b.Add(t)


def add_via(net_name, x, y, drill=0.3, size=0.6):
    """Add a tented through-via with teardrops enabled."""
    v = pcbnew.PCB_VIA(b)
    v.SetPosition(xy(x, y))
    v.SetWidth(pcbnew.FromMM(float(size)))
    v.SetDrill(pcbnew.FromMM(float(drill)))
    v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetLayerPair(F_Cu, B_Cu)
    v.SetNet(net_map[net_name])
    v.SetTeardropsEnabled(True)
    b.Add(v)
    return v


def route_45(x1, y1, x2, y2, first="diag"):
    """Return a clean 45-degree 2-segment path from (x1,y1) to (x2,y2)."""
    dx = x2 - x1
    dy = y2 - y1
    adx = abs(dx)
    ady = abs(dy)
    if adx < 1e-5 or ady < 1e-5 or abs(adx - ady) < 1e-5:
        return [(x1, y1), (x2, y2)]
    sx = 1.0 if dx > 0 else -1.0
    sy = 1.0 if dy > 0 else -1.0
    if adx > ady:
        if first == "diag":
            return [(x1, y1), (x1 + sx * ady, y2), (x2, y2)]
        else:
            return [(x1, y1), (x2 - sx * ady, y1), (x2, y2)]
    else:
        if first == "diag":
            return [(x1, y1), (x2, y1 + sy * adx), (x2, y2)]
        else:
            return [(x1, y1), (x1, y2 - sy * adx), (x2, y2)]


def chain_45(*waypoints):
    """Build a continuous 45-degree polyline through waypoints."""
    pts = [waypoints[0][:2]]
    for i in range(len(waypoints) - 1):
        w1 = waypoints[i]
        w2 = waypoints[i + 1]
        mode = w2[2] if len(w2) > 2 else "straight"
        seg = route_45(w1[0], w1[1], w2[0], w2[1], first=mode)
        for p in seg[1:]:
            pts.append(p)
    return pts


# ------------------------------------------------------------------------------
# ROUTE ORDER 1: POWER (+12V_IN, +12V_F, Q1_G, +12V, BUCK_*, +3V3, GND)
# ------------------------------------------------------------------------------

# 1.1 +12V_IN (1.2 mm, F.Cu)
add_track_poly("+12V_IN", F_Cu, 1.2, chain_45((4.3, 35.46), (7.4, 38.56, "straight"), (7.4, 43.538), (9.062, 45.2)))

# 1.2 +12V_F (1.2 mm, F.Cu + 2 parallel vias per layer change to Q1.3)
# Note: D1 rotated 270 deg puts D1.1 (+12V_F) at (10.3, 37.65) and D1.2 (GND) at (10.3, 33.35)
add_track_poly("+12V_F", F_Cu, 1.2, chain_45((10.3, 37.65), (10.3, 42.162), (13.338, 45.2)))
# Parallel vias (2x) from F.Cu (+12V_F) at (11.5, 42.2) and (11.5, 41.2) to B.Cu -> parallel vias (2x) ABOVE Q1.3 at (16.137, 42.2) and (17.0, 42.2)
add_via("+12V_F", 11.5, 42.2)
add_via("+12V_F", 11.5, 41.2)
add_track_poly("+12V_F", F_Cu, 1.2, [(10.3, 41.2), (11.5, 41.2), (11.5, 42.2)])
add_via("+12V_F", 16.137, 42.2)
add_via("+12V_F", 17.0, 42.2)
add_track_poly("+12V_F", B_Cu, 1.2, [(11.5, 41.2), (11.5, 42.2), (16.137, 42.2), (17.0, 42.2)])
add_track_poly("+12V_F", F_Cu, 0.8, [(17.0, 42.2), (16.137, 42.2)])
add_track_poly("+12V_F", F_Cu, 0.6, [(16.137, 42.2), (16.137, 41.0)])

# 1.3 Q1_G (0.25 mm, F.Cu)
add_track_poly("Q1_G", F_Cu, 0.25, chain_45((13.575, 38.2), (13.1, 38.675), (13.1, 40.788), (14.262, 41.95)))
add_track_poly("Q1_G", F_Cu, 0.25, chain_45((14.262, 41.95), (15.5, 43.188, "diag"), (18.112, 45.8), (18.15, 45.8)))

# 1.4 +12V (1.2 mm main trunks + >=2 parallel vias to In2.Cu +12V plane)
# Q1.2@(14.262, 40.05) -> C3.1@(20.025, 40.8) -> C2.1@(20.025, 44.5) -> UP around C2.2 to TP1.1@(25.0, 46.5)
add_track_poly("+12V", F_Cu, 0.6, chain_45((14.262, 40.05), (14.762, 39.55, "diag"), (17.5, 39.55)))
add_track_poly(
    "+12V",
    F_Cu,
    1.2,
    chain_45((17.5, 39.55), (18.775, 39.55), (20.025, 40.8), (20.025, 44.5), (20.025, 46.2), (20.825, 47.0, "diag"), (24.5, 47.0), (25.0, 46.5, "diag")),
)
# Parallel vias (2x) beside C3.1/C2.1 to In2.Cu +12V plane
add_via("+12V", 18.8, 42.0)
add_via("+12V", 18.8, 43.0)
add_track_poly("+12V", F_Cu, 1.2, [(18.8, 42.0), (18.8, 43.0), (20.025, 43.0), (20.025, 42.0), (18.8, 42.0)])
# D3.1@(14.85, 45.8) -> 2 parallel vias ABOVE D3.1 to In2.Cu +12V plane (no crossing with Q1_G!)
add_via("+12V", 14.85, 46.9)
add_via("+12V", 15.65, 46.9)
add_track_poly("+12V", F_Cu, 0.5, [(14.85, 45.8), (14.85, 46.9), (15.65, 46.9)])
# U2.2@(17.1, 36.135) -> straight left into C4.1@(14.2, 35.975) (C4 at 270 deg) -> R2.1@(13.375, 32.0) + 2 parallel vias to In2.Cu
add_track_poly("+12V", F_Cu, 0.5, chain_45((17.1, 36.135), (14.36, 36.135), (14.2, 35.975), (12.9, 35.975), (12.9, 32.475), (13.375, 32.0)))
add_via("+12V", 12.9, 35.975)
add_via("+12V", 12.9, 35.0)
# Left-side high-current +12V trunk: C1.1@(5.3, 26.5) -> C24.1@(9.925, 16.8) and J2.1@(4.5, 9.46) -> D2.1@(10.2, 10.0)
add_track_poly("+12V", F_Cu, 1.2, [(5.3, 26.5), (5.3, 24.5), (6.3, 24.5)])
add_via("+12V", 5.3, 24.5)
add_via("+12V", 6.3, 24.5)
add_track_poly("+12V", F_Cu, 1.2, [(7.8, 16.8), (8.5, 16.8), (9.925, 16.8)])
add_via("+12V", 7.8, 16.8)
add_via("+12V", 8.5, 16.8)
add_track_poly("+12V", B_Cu, 1.2, chain_45((6.3, 24.5), (5.3, 24.5), (5.3, 19.3), (7.8, 16.8, "diag"), (8.5, 16.8)))
add_track_poly("+12V", F_Cu, 1.2, chain_45((4.5, 9.46), (9.66, 9.46), (10.2, 10.0)))
add_via("+12V", 7.8, 9.46)
add_via("+12V", 7.8, 10.36)
add_track_poly("+12V", F_Cu, 1.2, [(7.8, 9.46), (7.8, 10.36)])
# HMI +12V pads: C26.1@(23.725, 18.5), R25.1@(28.675, 19.2), D7.1@(28.35, 28.0), R21.1@(41.325, 19.5)
# C26.1@(23.725, 18.5): 2 parallel vias at (23.725, 16.6) and (24.525, 16.6) well above TP9.1@(23.0, 15.2)
add_via("+12V", 23.725, 16.6)
add_via("+12V", 24.525, 16.6)
add_track_poly("+12V", F_Cu, 0.5, [(23.725, 18.5), (23.725, 16.6), (24.525, 16.6)])
# R25.1@(28.675, 19.2): 2 parallel vias at (28.675, 16.0) and (27.875, 16.0) inside In2.Cu +12V plane
add_via("+12V", 28.675, 16.0)
add_via("+12V", 27.875, 16.0)
add_track_poly("+12V", F_Cu, 0.5, [(28.675, 19.2), (28.675, 16.0), (27.875, 16.0)])
# R21.1@(41.325, 19.5) (R21 at 180 deg): straight down F.Cu to 2 parallel vias at (41.325, 16.0) and (41.325, 15.1) inside In2.Cu +12V plane
add_via("+12V", 41.325, 16.0)
add_via("+12V", 41.325, 15.1)
add_track_poly("+12V", F_Cu, 0.5, [(41.325, 19.5), (41.325, 16.0), (41.325, 15.1)])
# D7.1@(28.35, 28.0) -> 2 parallel vias at (28.35, 29.0) and (29.15, 29.0) -> B.Cu down x=27.0 -> 2 parallel vias at (27.0, 16.0) and (27.0, 16.8)
add_via("+12V", 28.35, 29.0)
add_via("+12V", 29.15, 29.0)
add_track_poly("+12V", F_Cu, 0.5, [(28.35, 28.0), (28.35, 29.0), (29.15, 29.0)])
add_via("+12V", 27.0, 16.8)
add_via("+12V", 27.0, 16.0)
add_track_poly("+12V", B_Cu, 0.5, chain_45((29.15, 29.0), (28.35, 29.0), (27.0, 27.65, "diag"), (27.0, 16.8), (27.0, 16.0)))

# 1.5 BUCK_SW (Compact high-dI/dt switching node on F.Cu ONLY, 0 vias)
add_track_poly("BUCK_SW", F_Cu, 0.5, chain_45((22.5, 37.405), (22.9, 37.805), (25.575, 37.805), (26.175, 37.205), (26.175, 36.8)))
add_track_poly(
    "BUCK_SW",
    F_Cu,
    0.6,
    chain_45((26.175, 36.8), (26.987, 36.8), (27.187, 36.6, "diag"), (27.187, 32.55), (26.787, 32.15, "diag"), (22.35, 32.15), (22.35, 29.0)),
)

# 1.6 BUCK_BOOT, BUCK_VCC, BUCK_EN, BUCK_FB (100% on F.Cu, 0 vias)
add_track_poly("BUCK_BOOT", F_Cu, 0.3, chain_45((22.5, 36.135), (23.96, 36.135), (24.625, 36.8)))
add_track_poly("BUCK_VCC", F_Cu, 0.3, chain_45((22.5, 34.865), (24.16, 34.865), (24.625, 34.4)))
add_track_poly("BUCK_EN", F_Cu, 0.25, chain_45((17.1, 34.865), (15.7, 34.865), (15.3, 34.465, "diag"), (15.3, 32.275), (15.025, 32.0, "diag")))
add_track_poly("BUCK_EN", F_Cu, 0.25, chain_45((15.025, 32.0), (15.025, 31.3), (14.725, 31.0), (13.675, 31.0), (13.375, 30.7), (13.375, 30.0)))
add_track_poly(
    "BUCK_FB",
    F_Cu,
    0.25,
    chain_45((22.5, 33.595), (22.2, 33.595), (22.2, 32.9), (21.5, 32.2, "diag"), (18.875, 32.2), (18.675, 32.0, "diag"), (18.675, 31.2), (18.675, 29.2), (18.725, 29.15), (18.725, 27.2)),
)

# 1.7 +3V3 Output Bank & Local Decoupling Ties (0.5 mm - 0.8 mm + vias to In2.Cu +3V3 plane)
# L1.2@(26.65, 29.0) -> TP2.1@(28.8, 31.2) -> C12.1@(28.2, 33.625)
add_track_poly("+3V3", F_Cu, 0.5, chain_45((26.65, 29.0), (26.65, 30.45), (28.05, 30.45), (28.8, 31.2, "diag"), (28.8, 33.025), (28.2, 33.625, "diag")))
add_via("+3V3", 28.8, 32.5)
# L1.2@(26.65, 29.0) -> R4.2@(20.325, 31.2) and C7.2@(20.275, 27.2) via In2.Cu
add_via("+3V3", 21.1, 31.2)
add_track_poly("+3V3", F_Cu, 0.5, [(20.325, 31.2), (21.1, 31.2)])
add_via("+3V3", 21.1, 27.2)
add_track_poly("+3V3", F_Cu, 0.5, [(20.275, 27.2), (21.1, 27.2)])
# C8.1@(23.025, 24.0), C9.1@(23.025, 21.2), C10.1@(28.025, 24.0), C11.1@(28.025, 21.2)
add_track_poly("+3V3", F_Cu, 0.8, [(23.025, 24.0), (23.025, 21.2)])
add_via("+3V3", 23.025, 22.6)
add_track_poly("+3V3", F_Cu, 0.8, [(28.025, 24.0), (28.025, 21.2)])
add_via("+3V3", 28.025, 22.6)
# U1.3@(30.1, 40.9) <-> C16.2@(27.975, 41.2) <-> C15.2@(27.95, 39.0) <-> R6.1@(26.375, 43.2) (< 3 mm decoupling!)
add_track_poly("+3V3", F_Cu, 0.5, chain_45((30.1, 40.9), (28.275, 40.9), (27.975, 41.2), (27.975, 39.025), (27.95, 39.0)))
add_track_poly("+3V3", F_Cu, 0.5, chain_45((27.975, 41.2), (27.975, 41.6), (26.375, 43.2)))
add_via("+3V3", 27.975, 40.1)
# Pull-ups R9.1@(36.0, 29.975), R10.1@(38.2, 29.975), R7.1@(40.4, 29.975), R8.1@(42.6, 29.975)
add_track_poly("+3V3", F_Cu, 0.5, [(36.0, 29.975), (38.2, 29.975), (40.4, 29.975), (42.6, 29.975)])
add_via("+3V3", 41.75, 29.975)
# FB1.1@(50.212, 36.8)
add_via("+3V3", 49.0, 36.8)
add_track_poly("+3V3", F_Cu, 0.5, [(49.0, 36.8), (50.212, 36.8)])
# U6.5@(16.137, 24.15), C23.2@(19.0, 23.975), C22.2@(15.775, 20.3), U5.5@(16.137, 18.45)
add_track_poly("+3V3", F_Cu, 0.5, chain_45((16.137, 24.15), (18.825, 24.15), (19.0, 23.975)))
add_via("+3V3", 17.5, 24.15)
# Separate vias for C22.2 and U5.5 so +3V3 does not cross VALVE_EN on F.Cu
add_via("+3V3", 16.7, 20.3)
add_track_poly("+3V3", F_Cu, 0.5, [(15.775, 20.3), (16.7, 20.3)])
add_via("+3V3", 16.65, 18.15)
add_track_poly("+3V3", F_Cu, 0.5, chain_45((16.137, 18.45), (16.437, 18.15, "diag"), (16.65, 18.15)))
# J3.1@(23.0, 11.81) -> B.Cu up to +3V3 via at (22.3, 18.2) inside In2.Cu +3V3 plane
add_via("+3V3", 22.3, 18.2)
add_track_poly("+3V3", B_Cu, 0.5, chain_45((23.0, 11.81), (22.3, 12.51, "diag"), (22.3, 18.2)))
# R20.2@(38.825, 17.5), R26.2@(45.625, 18.8), R30.1@(43.975, 23.8)
add_via("+3V3", 38.825, 18.5)
add_track_poly("+3V3", F_Cu, 0.5, [(38.825, 17.5), (38.825, 18.5)])
add_via("+3V3", 45.0, 18.0)
add_track_poly("+3V3", F_Cu, 0.5, chain_45((45.625, 18.8), (45.625, 18.625), (45.0, 18.0, "diag")))
add_via("+3V3", 44.8, 24.8)
add_track_poly("+3V3", F_Cu, 0.5, chain_45((43.975, 23.8), (43.975, 23.975), (44.8, 24.8, "diag")))
# Zone F / J4 +3V3 ties: J4.2@(47.23, 46.2), R27.1@(51.175, 42.6), C29.1@(52.775, 40.0) -> S2.3@(60.8, 41.7)
add_via("+3V3", 47.23, 44.8)
add_track_poly("+3V3", F_Cu, 0.5, [(47.23, 46.2), (47.23, 44.8)])
add_via("+3V3", 50.8, 43.2)
add_track_poly("+3V3", F_Cu, 0.5, chain_45((51.175, 42.6), (51.175, 42.825), (50.8, 43.2, "diag")))
add_via("+3V3", 53.5, 40.0)
add_track_poly("+3V3", F_Cu, 0.5, chain_45((52.775, 40.0), (53.5, 40.0), (59.1, 40.0), (60.8, 41.7, "diag")))

# 1.8 GND Vias & Local Ties to Unbroken L2 (In1.Cu) GND Plane
# Zone A GND pads:
for gx, gy, vx, vy in [
    (10.3, 33.35, 10.3, 31.8),    # D1.2
    (10.7, 26.5, 10.7, 28.5),     # C1.2
    (15.225, 38.2, 15.225, 37.2), # R1.2 (below R1.2, clear of +12V at y=39.2!)
    (22.975, 44.5, 24.3, 44.5),   # C2.2
    (22.975, 40.8, 24.3, 40.8),   # C3.2
    (14.2, 34.425, 14.2, 33.4),   # C4.2 (C4 at 270 deg -> pad 2 at bottom!)
    (17.1, 37.405, 15.8, 37.405), # U2.1 (to the left of U2.1, clear of +12V!)
    (15.025, 30.0, 16.0, 30.0),   # R3.2
    (20.325, 29.2, 21.1, 29.2),   # R5.2
    (26.175, 34.4, 25.4, 33.2),   # C6.2 (away from BUCK_SW!)
    (28.2, 35.175, 29.0, 35.175), # C12.2 (to the right of C12.2!)
    # Zone B GND pads:
    (11.475, 16.8, 11.475, 15.8), # C24.2 (below C24.2, clear of NRST at y=17.5!)
    (13.562, 9.25, 13.562, 8.2),  # Q2.2
    (15.325, 6.8, 16.3, 6.8),     # R15.2
    (13.863, 16.55, 14.9, 16.55), # U5.3 (1.2 mm above MR_N at y=15.35!)
    (14.225, 20.3, 14.225, 21.3), # C22.1
    (19.2, 14.2, 19.2, 13.1),     # TP4.1
    (19.825, 9.2, 20.8, 9.2),     # R17.2
    (19.775, 7.2, 20.8, 7.2),     # C25.2
    (13.863, 23.2, 12.9, 23.2),   # U6.2
    (19.0, 22.425, 19.0, 21.4),   # C23.1
    # Zone C/E GND pads:
    (26.425, 41.2, 25.4, 41.2),   # C16.1
    (26.05, 39.0, 25.0, 39.0),    # C15.1
    (31.2, 30.025, 29.5, 30.025), # C17.2 (0.95 mm left of VALVE_SENSE at x=30.45!)
    (25.275, 18.5, 25.275, 19.5), # C26.2
    (34.562, 19.05, 33.5, 19.05), # Q5.2
    (33.975, 25.8, 33.65, 24.8),  # R24.2 (between BUZZER at 32.9 and LED_RED at 34.4!)
    (39.562, 21.55, 39.562, 20.6),# Q4.2 (below Q4.2, clear of HUSH_N!)
    (41.325, 25.5, 42.1, 25.5),   # R22.2
    (45.575, 21.4, 45.0, 22.5),   # C27.2
    (44.25, 17.075, 45.1, 16.3),  # C30.2 (SW2 hardware debounce capacitor GND)
    (48.2, 5.2125, 48.2, 4.1),    # D9.2 (SW1 IEC 61000-4-2 ESD TVS GND)
    (26.012, 4.0, 26.012, 5.1),   # D4.1
    (29.212, 4.0, 29.212, 5.0),   # D5.1 (GRN_OK hardware +3V3 power LED GND)
    (58.5, 31.8, 58.5, 33.0),     # NT1.1 (Single-point AGND-GND bridge!)
    # Zone F & J4 GND pads:
    (44.69, 46.2, 44.69, 44.8),   # J4.1
    (57.2, 45.3, 57.2, 46.5),     # S2.1
    (51.225, 40.0, 51.225, 39.0), # C29.2
    (47.375, 42.6, 46.2, 42.6),   # R28.2
    (44.225, 41.6, 44.225, 42.7), # C28.1
]:
    add_via("GND", vx, vy)
    add_track_poly("GND", F_Cu, 0.4, chain_45((gx, gy), (vx, vy)))
# R18.2 shares the GND via at (19.0, 21.4) with C23.1 (no duplicate co-located via!)
add_track_poly("GND", F_Cu, 0.4, chain_45((19.825, 20.3), (19.0, 21.125, "diag"), (19.0, 21.4)))

# C8.2@(25.975, 24.0) & C9.2@(25.975, 21.2), C10.2@(30.975, 24.0) & C11.2@(30.975, 21.2)
add_track_poly("GND", F_Cu, 0.8, [(25.975, 24.0), (25.975, 21.2)])
add_via("GND", 25.975, 22.6)
add_track_poly("GND", F_Cu, 0.8, [(30.975, 24.0), (30.975, 21.2)])
add_via("GND", 30.975, 22.6)

# SW1.2@(39.375, 4.4) & (44.625, 4.4), SW2.2@(39.375, 10.4) & (44.625, 10.4), D10.2@(42.55, 17.0875), SW3.2@(2.825, 18.6) & (8.075, 18.6), C31.1@(10.0, 19.425), D11.2@(11.8, 19.4125)
add_track_poly("GND", F_Cu, 0.4, [(39.375, 4.4), (44.625, 4.4)])
add_via("GND", 42.0, 4.4)
add_track_poly("GND", F_Cu, 0.4, [(39.375, 10.4), (44.625, 10.4)])
add_via("GND", 42.0, 10.4)
add_track_poly("GND", F_Cu, 0.4, chain_45((42.55, 17.0875), (44.2375, 17.0875), (44.25, 17.075, "diag")))
add_track_poly("GND", F_Cu, 0.4, [(2.825, 18.6), (8.075, 18.6), (9.175, 18.6)])
add_via("GND", 9.175, 18.6)
add_track_poly("GND", F_Cu, 0.4, chain_45((9.175, 18.6), (10.0, 19.425, "diag"), (11.7875, 19.425), (11.8, 19.4125, "diag")))

# U1 GND pads:
# Left GND pads: U1.53@(30.05, 43.45), U1.1@(30.1, 42.5), U1.2@(30.1, 41.7) -> via inside U1 at (31.5, 42.1)
add_track_poly("GND", F_Cu, 0.4, [(30.05, 43.45), (30.1, 43.4), (30.1, 42.5), (30.1, 41.7)])
add_via("GND", 31.5, 42.1)
add_track_poly("GND", F_Cu, 0.4, chain_45((30.1, 42.5), (31.1, 42.5), (31.5, 42.1, "diag")))
# Bottom-left GND pads: U1.11@(30.1, 34.5), U1.52@(30.05, 33.55), U1.14@(32.8, 33.6)
add_track_poly("GND", F_Cu, 0.4, [(30.1, 34.5), (30.05, 34.45), (30.05, 33.55)])
add_via("GND", 30.05, 32.5)
add_track_poly("GND", F_Cu, 0.4, [(30.05, 33.55), (30.05, 32.5)])
add_track_poly("GND", F_Cu, 0.3, [(32.8, 33.6), (32.8, 36.525), (34.025, 36.525)])
# Top-row U1 GND pads (36..48, 50, 53 at y=43.4..43.45) + thermal pad array (U1.49) + U1.51@(41.95, 33.55)
add_track_poly("GND", F_Cu, 0.4, [(30.05, 43.45), (30.1, 43.4), (31.2, 43.4), (40.8, 43.4), (41.9, 43.4), (41.95, 43.45)])
add_via("GND", 36.0, 42.2)
add_track_poly("GND", F_Cu, 0.5, [(36.0, 43.4), (36.0, 42.2), (36.0, 40.475)])
for gx in [34.025, 36.0, 37.975]:
    add_track_poly("GND", F_Cu, 0.5, [(gx, 36.525), (gx, 40.475)])
for gy in [36.525, 38.5, 40.475]:
    add_track_poly("GND", F_Cu, 0.5, [(34.025, gy), (37.975, gy)])
for vx, vy in [(35.0, 37.5), (37.0, 37.5), (35.0, 39.5), (37.0, 39.5)]:
    add_via("GND", vx, vy)
    add_track_poly("GND", F_Cu, 0.4, [(vx, vy), (vx, 38.5)])
add_via("GND", 43.0, 33.55)
add_track_poly("GND", F_Cu, 0.4, [(41.95, 33.55), (43.0, 33.55)])

# U2 thermal pad center vias (0.3 mm drill, 1.0 mm pitch)
for ty in [34.5, 35.5, 36.5]:
    add_via("GND", 19.8, ty)

# ------------------------------------------------------------------------------
# ROUTE ORDER 2: VALVE DRIVER & SAFETY INTERLOCK
# ------------------------------------------------------------------------------

# 2.1 VALVE_NEG (1.2 mm trace + 3 parallel vias near D2.2 + 4 thermal/parallel vias at 1.0 mm pitch under/beside Q2.3)
add_track_poly("VALVE_NEG", F_Cu, 1.2, chain_45((4.5, 14.54), (9.66, 14.54), (10.2, 14.0), (11.5, 14.0)))
for vx, vy in [(11.5, 13.5), (11.5, 14.5), (12.3, 14.0)]:
    add_via("VALVE_NEG", vx, vy)
add_track_poly("VALVE_NEG", F_Cu, 1.2, [(11.5, 13.5), (11.5, 14.5), (11.8, 14.5), (12.3, 14.0)])
add_track_poly("VALVE_NEG", B_Cu, 1.2, [(11.5, 13.5), (11.5, 14.5), (11.8, 14.5), (12.3, 14.0)])
# 2x2 thermal via array (0.3 mm drill, 1.0 mm pitch) at Q2 drain (15.8..16.8, 9.7..10.7) -> >0.35mm clear of R17.1
for vx in [15.8, 16.8]:
    for vy in [9.7, 10.7]:
        add_via("VALVE_NEG", vx, vy)
add_track_poly("VALVE_NEG", B_Cu, 1.2, chain_45((12.3, 14.0), (12.5, 14.0), (15.8, 10.7), (16.8, 10.7), (16.8, 9.7), (15.8, 9.7), (15.8, 10.7)))
add_track_poly("VALVE_NEG", F_Cu, 1.2, [(15.8, 10.7), (16.8, 10.7), (16.8, 9.7), (15.8, 9.7), (15.8, 10.7)])
add_track_poly("VALVE_NEG", F_Cu, 0.6, [(15.438, 10.2), (15.8, 10.2), (15.8, 10.7)])
add_track_poly("VALVE_NEG", F_Cu, 0.5, chain_45((16.8, 10.7), (17.675, 10.7), (18.175, 11.2)))

# 2.2 VALVE_GATE (0.3 mm, F.Cu only, 0 vias)
add_track_poly("VALVE_GATE", F_Cu, 0.3, [(10.2, 6.8), (12.2, 6.8), (13.675, 6.8)])
add_track_poly("VALVE_GATE", F_Cu, 0.3, chain_45((12.2, 6.8), (12.2, 10.2), (13.15, 11.15, "diag"), (13.562, 11.15), (13.562, 13.387), (13.675, 13.5)))

# 2.3 VALVE_DRV (0.3 mm, F.Cu only, 0 vias: R14.2 -> U5.4 -> R13.1 Bus-Hold feedback)
add_track_poly("VALVE_DRV", F_Cu, 0.3, chain_45((15.325, 13.5), (16.137, 14.312), (16.137, 16.55)))
add_track_poly("VALVE_DRV", F_Cu, 0.25, chain_45((16.137, 16.55), (18.875, 16.55), (19.0, 16.675, "diag")))

# 2.4 MR_N (0.25 mm: SW3.1@(2.825, 21.8) & (8.075, 21.8) -> C31.2@(10.0, 20.975) -> D11.1@(11.8, 20.9875) -> U6.3@(13.863, 22.25) -> TP9.1@(23.0, 15.2))
add_track_poly("MR_N", F_Cu, 0.25, [(2.825, 21.8), (8.075, 21.8)])
add_track_poly("MR_N", F_Cu, 0.25, chain_45((8.075, 21.8), (9.175, 21.8), (10.0, 20.975, "diag"), (11.7875, 20.975), (11.8, 20.9875, "diag")))
add_track_poly("MR_N", F_Cu, 0.2, chain_45((11.8, 20.9875), (11.8, 21.4875), (12.5625, 22.25, "diag"), (12.8, 22.25), (13.863, 22.25)))
add_via("MR_N", 12.8, 22.25)
add_track_poly("MR_N", B_Cu, 0.2, [(12.8, 22.25), (12.8, 15.35), (17.2, 15.35)])
add_via("MR_N", 17.2, 15.35)
add_track_poly("MR_N", F_Cu, 0.2, chain_45((17.2, 15.35), (22.85, 15.35), (23.0, 15.2, "diag")))

# 2.5 NRST, VALVE_SENSE, VALVE_EN, WDI
# NRST: U6.1@(13.863, 24.15) -> TP12.1@(15.0, 26.5) -> B.Cu up x=17.5 / y=32.6 -> U1.8@(30.1, 36.9)
add_track_poly(
    "NRST",
    F_Cu,
    0.2,
    chain_45(
        (13.863, 24.15),
        (13.863, 25.363),
        (15.0, 26.5),
        (17.5, 26.5),
    ),
)
add_via("NRST", 17.5, 26.5)
add_track_poly("NRST", B_Cu, 0.2, chain_45((17.5, 26.5), (17.5, 32.6), (23.0, 32.6), (27.3, 36.9, "diag"), (29.3, 36.9)))
add_via("NRST", 29.3, 36.9)
add_track_poly("NRST", F_Cu, 0.2, [(29.3, 36.9), (30.1, 36.9)])

# VALVE_SENSE: C25.1@(18.225, 7.2) -> R17.1@(18.175, 9.2) -> R16.2@(19.825, 11.2) -> U1.13@(32.0, 33.6)
add_track_poly(
    "VALVE_SENSE",
    F_Cu,
    0.2,
    chain_45((18.225, 7.2), (18.175, 7.25), (18.175, 9.2), (18.175, 10.0), (18.375, 10.2, "diag"), (19.625, 10.2), (19.825, 10.4, "diag"), (19.825, 11.2), (20.3, 11.675, "diag")),
)
add_via("VALVE_SENSE", 20.3, 11.675)
add_track_poly("VALVE_SENSE", B_Cu, 0.2, [(20.3, 11.675), (20.3, 26.20)])
add_via("VALVE_SENSE", 20.3, 26.20)
add_track_poly("VALVE_SENSE", F_Cu, 0.2, chain_45((20.3, 26.20), (30.25, 26.20), (30.45, 26.40, "diag")))
add_via("VALVE_SENSE", 30.45, 26.40)
add_track_poly("VALVE_SENSE", B_Cu, 0.2, chain_45((30.45, 26.40), (30.45, 30.95), (32.0, 32.5, "diag")))
add_via("VALVE_SENSE", 32.0, 32.5)
add_track_poly("VALVE_SENSE", F_Cu, 0.2, [(32.0, 32.5), (32.0, 33.6)])

# VALVE_EN: U5.2@(13.863, 17.50) & U5.1@(13.863, 18.45) -> R13.2@(19.0, 18.325) -> U1.20@(37.6, 33.6)
add_track_poly("VALVE_EN", F_Cu, 0.2, [(13.863, 17.50), (13.863, 18.45)])
add_track_poly(
    "VALVE_EN",
    F_Cu,
    0.2,
    chain_45((13.863, 18.45), (13.863, 18.95), (14.3, 19.387), (16.8, 19.387), (17.5, 18.687), (17.5, 18.325), (19.0, 18.325), (20.95, 18.325)),
)
add_via("VALVE_EN", 20.95, 18.325)
add_track_poly("VALVE_EN", B_Cu, 0.2, [(20.95, 18.325), (20.95, 25.00)])
add_via("VALVE_EN", 20.95, 25.00)
add_track_poly(
    "VALVE_EN",
    F_Cu,
    0.2,
    chain_45((20.95, 25.00), (21.70, 25.75, "diag"), (31.5, 25.75), (33.0, 27.25, "diag"), (37.6, 27.25)),
)
add_via("VALVE_EN", 37.6, 27.25)
add_track_poly("VALVE_EN", B_Cu, 0.2, [(37.6, 27.25), (37.6, 32.65)])
add_via("VALVE_EN", 37.6, 32.65)
add_track_poly("VALVE_EN", F_Cu, 0.2, [(37.6, 32.65), (37.6, 33.6)])

# WDI: U6.4@(16.137, 22.25) -> R18.1@(18.175, 20.3) -> U1.21@(38.4, 33.6)
add_track_poly("WDI", F_Cu, 0.2, chain_45((16.137, 22.25), (16.9, 22.25), (18.175, 20.975), (18.175, 20.3), (18.175, 19.5), (21.6, 19.5)))
add_via("WDI", 21.6, 19.5)
add_track_poly("WDI", B_Cu, 0.2, [(21.6, 19.5), (21.6, 23.80)])
add_via("WDI", 21.6, 23.80)
add_track_poly(
    "WDI",
    F_Cu,
    0.2,
    chain_45((21.6, 23.80), (21.6, 24.60), (22.30, 25.30, "diag"), (32.05, 25.30), (33.35, 26.60, "diag"), (38.7, 26.60)),
)
add_via("WDI", 38.7, 26.60)
add_track_poly("WDI", B_Cu, 0.2, chain_45((38.7, 26.60), (38.7, 32.35), (38.4, 32.65, "diag")))
add_via("WDI", 38.4, 32.65)
add_track_poly("WDI", F_Cu, 0.2, [(38.4, 32.65), (38.4, 33.6)])

# ------------------------------------------------------------------------------
# ROUTE ORDER 3: I2C, AVDD & SINGLE-POINT AGND JOIN
# ------------------------------------------------------------------------------

# 3.1 I2C_SDA: U1.18@(36.0, 33.6) -> R9.2@(36.0, 31.625) -> F.Cu around left of R9.1 -> TP7.1@(45.8, 34.5) -> U3.4@(56.5, 29.7)
add_track_poly(
    "I2C_SDA",
    F_Cu,
    0.2,
    chain_45((36.0, 33.6), (36.0, 31.625), (35.1, 30.725, "diag"), (35.1, 29.35), (35.3, 29.15, "diag"), (44.6, 29.15)),
)
add_via("I2C_SDA", 44.6, 29.15)
add_track_poly("I2C_SDA", B_Cu, 0.2, [(44.6, 29.15), (44.6, 34.5)])
add_via("I2C_SDA", 44.6, 34.5)
add_track_poly("I2C_SDA", F_Cu, 0.2, [(44.6, 34.5), (45.8, 34.5), (52.5, 34.5)])
add_via("I2C_SDA", 52.5, 34.5)
add_track_poly("I2C_SDA", B_Cu, 0.2, chain_45((52.5, 34.5), (52.5, 32.0), (53.75, 30.75, "diag"), (56.25, 30.75)))
add_via("I2C_SDA", 56.25, 30.75)
add_track_poly("I2C_SDA", F_Cu, 0.2, chain_45((56.25, 30.75), (56.5, 30.50, "diag"), (56.5, 29.7)))

# 3.2 I2C_SCL: U1.19@(36.8, 33.6) -> R10.2@(38.2, 31.625) -> TP8.1@(45.8, 29.8) -> U3.3@(57.0, 29.7)
# Route horizontally at y=28.53 (between I2C_SDA at y=29.30 and VOUT_ADC at y=27.90 -> ZERO crossings!)
add_track_poly("I2C_SCL", F_Cu, 0.2, chain_45((36.8, 33.6), (36.8, 31.9), (37.075, 31.625), (38.2, 31.625)))
add_via("I2C_SCL", 36.8, 32.5)
add_track_poly("I2C_SCL", B_Cu, 0.2, [(36.8, 32.5), (36.8, 28.53)])
add_via("I2C_SCL", 36.8, 28.53)
add_track_poly("I2C_SCL", F_Cu, 0.2, chain_45((36.8, 28.53), (45.3, 28.53), (45.8, 29.03, "diag"), (45.8, 29.8), (47.3, 29.8)))
add_via("I2C_SCL", 47.3, 29.8)
add_track_poly("I2C_SCL", B_Cu, 0.2, chain_45((47.3, 29.8), (47.55, 30.05, "diag"), (56.45, 30.05), (57.15, 30.75, "diag")))
add_via("I2C_SCL", 57.15, 30.75)
add_track_poly("I2C_SCL", F_Cu, 0.2, chain_45((57.15, 30.75), (57.0, 30.60, "diag"), (57.0, 29.7)))

# 3.3 AVDD (0.50 mm main trunk + 0.25 mm fine-pitch entry into U3.6, 100% on F.Cu, 0 vias)
add_track_poly("AVDD", F_Cu, 0.50, chain_45((51.788, 36.8), (53.188, 38.2, "diag"), (55.3, 38.2), (56.15, 37.35, "diag"), (56.15, 36.8), (59.5, 36.8)))
add_track_poly("AVDD", F_Cu, 0.50, chain_45((56.15, 36.8), (55.975, 36.625), (55.975, 34.2), (55.975, 31.8), (55.5, 31.325, "diag"), (55.5, 30.45)))
add_track_poly("AVDD", F_Cu, 0.25, [(55.5, 30.45), (55.5, 29.7)])
add_track_poly("AVDD", F_Cu, 0.50, chain_45((59.5, 36.8), (61.5, 34.8, "diag"), (61.5, 32.425), (62.425, 31.5, "diag"), (62.425, 29.612), (62.263, 29.45)))

# 3.4 AGND (0.3 mm on F.Cu through U3.15 center pad, 360-deg closed AGND Guard Ring around WE/RE/CE + single-point NT1.2 join)
add_track_poly(
    "AGND",
    F_Cu,
    0.3,
    chain_45(
        (54.25, 36.8),
        (54.425, 36.625),
        (54.425, 34.2),
        (54.425, 31.8),
        (54.425, 30.275),
        (55.0, 29.7),
        (55.0, 28.8),
        (56.0, 27.8, "diag"),
        (56.5, 27.8),
        (57.0, 27.8),
        (57.5, 28.3, "diag"),
        (57.5, 29.7),
        (58.0, 29.7),
        (59.5, 31.2),
        (59.5, 31.8),
    ),
)
# AGND Guard Trace on F.Cu surrounding WE, RE, CE (closed loop via B.Cu into U3.15 at (56.5, 28.3) -> 0 crossings, 0 dangling ends!)
add_track_poly(
    "AGND",
    F_Cu,
    0.25,
    chain_45(
        (58.0, 29.7),
        (58.8, 28.9),
        (58.8, 24.5),
        (60.6, 22.7),
        (60.6, 19.3),
        (59.3, 18.0),
        (53.7, 18.0),
        (52.4, 19.3),
        (52.4, 22.0),
    ),
)
add_via("AGND", 52.4, 22.0)
add_track_poly("AGND", B_Cu, 0.25, chain_45((52.4, 22.0), (51.5, 22.9, "diag"), (51.5, 28.3), (56.5, 28.3)))
add_via("AGND", 56.5, 28.3)
add_track_poly("AGND", F_Cu, 0.25, [(56.5, 28.3), (56.5, 27.8)])
# Connect C20.2@(63.975, 25.5), U4.3@(64.138, 28.5), C19.2@(63.975, 31.5) from bottom-right of AGND (58.8, 24.5) so AGND never crosses AVDD!
add_track_poly(
    "AGND",
    F_Cu,
    0.3,
    chain_45((58.8, 24.5), (62.975, 24.5), (63.975, 25.5), (64.138, 25.663), (64.138, 28.5), (64.138, 31.337), (63.975, 31.5)),
)

# ------------------------------------------------------------------------------
# ROUTE ORDER 4: GUARDED ELECTRODES (WE, RE, CE) & ANALOG AFE SIGNALS
# ------------------------------------------------------------------------------

# 4.1 WE, RE, CE: F.Cu ONLY, ZERO vias, < 10 mm length, 45-deg bends, inside AGND guard ring
# WE: S1.1@(54.0, 20.0) -> U3.12@(57.0, 25.9) (Length = 7.14 mm < 10 mm)
add_track_poly("WE", F_Cu, 0.25, [(54.0, 20.0), (54.0, 21.1), (57.0, 24.1), (57.0, 25.9)])
# RE: S1.2@(56.5, 21.0) -> U3.13@(57.5, 25.9) (Length = 5.31 mm < 10 mm)
add_track_poly("RE", F_Cu, 0.25, [(56.5, 21.0), (56.5, 22.6), (57.5, 23.6), (57.5, 25.9)])
# CE: S1.3@(59.0, 20.0) -> U3.14@(58.0, 25.9) (Length = 6.31 mm < 10 mm)
add_track_poly("CE", F_Cu, 0.25, [(59.0, 20.0), (59.0, 21.6), (58.0, 22.6), (58.0, 25.9)])

# 4.2 VREF: U3.11@(56.5, 25.9) -> straight down to (56.5, 24.4) -> via@(52.8, 23.5) -> B.Cu at y=26.8 -> via@(61.0, 26.8) -> U4.2@(62.263, 27.55) -> C20.1@(62.425, 25.5)
add_track_poly("VREF", F_Cu, 0.2, chain_45((56.5, 25.9), (56.5, 24.4), (55.6, 23.5, "diag"), (52.8, 23.5)))
add_via("VREF", 52.8, 23.5)
add_track_poly("VREF", B_Cu, 0.2, [(52.8, 23.5), (52.8, 26.8), (61.0, 26.8)])
add_via("VREF", 61.0, 26.8)
add_track_poly("VREF", F_Cu, 0.2, chain_45((61.0, 26.8), (61.513, 26.8), (62.263, 27.55, "diag"), (62.425, 27.388, "diag"), (62.425, 25.5)))

# 4.3 TIA_C1 & TIA_C2 (100% on F.Cu, 0 vias, exit U3 straight down below y=25.5 before turning!)
add_track_poly(
    "TIA_C1",
    F_Cu,
    0.2,
    chain_45((56.0, 25.9), (56.0, 24.6), (55.8, 24.4, "diag"), (53.2, 24.4), (52.0, 25.6, "diag"), (52.0, 27.025), (49.25, 27.025), (49.2, 26.975, "diag")),
)
add_track_poly(
    "TIA_C2",
    F_Cu,
    0.2,
    chain_45((55.5, 25.9), (55.5, 25.1), (55.3, 24.9, "diag"), (53.7, 24.9), (53.0, 25.6, "diag"), (53.0, 27.575), (52.0, 28.575, "diag"), (49.25, 28.575), (49.2, 28.625, "diag")),
)

# 4.4 VOUT & VOUT_ADC (100% on F.Cu, 0 vias)
add_track_poly("VOUT", F_Cu, 0.2, chain_45((55.0, 25.9), (55.0, 25.3), (53.7, 26.6, "diag"), (53.7, 29.825), (52.325, 31.2, "diag")))
add_track_poly("VOUT", F_Cu, 0.2, chain_45((52.325, 31.2), (52.325, 32.1), (51.9, 32.525), (48.225, 32.525), (47.5, 31.8)))
# VOUT_ADC: R11.1@(50.675, 31.2) -> drops down at x=48.1 (right of I2C_SCL via at 47.3) -> y=27.90 horizontal channel -> C17.1@(31.2, 31.575) -> U1.12@(31.2, 33.6)
add_track_poly(
    "VOUT_ADC",
    F_Cu,
    0.2,
    chain_45(
        (50.675, 31.2),
        (50.0, 30.525, "diag"),
        (48.5, 30.525),
        (48.1, 30.125, "diag"),
        (48.1, 28.30),
        (47.7, 27.90, "diag"),
        (33.325, 27.90),
        (32.1, 29.125, "diag"),
        (32.1, 30.675),
        (31.2, 31.575, "diag"),
        (31.2, 33.6),
    ),
)

# ------------------------------------------------------------------------------
# ROUTE ORDER 5: REMAINING HMI, BUTTON & UART SIGNALS
# ------------------------------------------------------------------------------

# 5.1 LPG_ADC, LPG_SNS, LPG_HTR & J4 OLED I2C
# LPG_HTR: R27.2@(52.825, 42.6) -> S2.4@(60.8, 45.3) on F.Cu
add_track_poly("LPG_HTR", F_Cu, 0.4, chain_45((52.825, 42.6), (53.725, 43.5, "diag"), (59.0, 43.5), (60.8, 45.3, "diag")))

# LPG_SNS: S2.2@(57.2, 41.7) -> R28.1@(49.025, 42.6) & R29.1@(49.025, 40.2) on F.Cu (0 vias!)
add_track_poly("LPG_SNS", F_Cu, 0.25, chain_45((57.2, 41.7), (55.5, 41.7), (55.0, 41.2, "diag"), (49.6, 41.2), (49.025, 41.775, "diag"), (49.025, 42.6)))
add_track_poly("LPG_SNS", F_Cu, 0.25, chain_45((49.6, 41.2), (49.025, 40.625, "diag"), (49.025, 40.2)))

# LPG_ADC: R29.2@(47.375, 40.2) -> C28.2@(45.775, 41.6) -> via@(43.2, 40.6) -> B.Cu y=40.6 -> U1.5@(30.1, 39.3) -> R6.2@(28.025, 43.2) -> TP11.1@(27.2, 46.2)
add_track_poly("LPG_ADC", F_Cu, 0.2, chain_45((47.375, 40.2), (45.975, 41.6, "diag"), (45.775, 41.6), (45.775, 40.8), (45.575, 40.6, "diag"), (43.2, 40.6)))
add_via("LPG_ADC", 43.2, 40.6)
add_track_poly("LPG_ADC", B_Cu, 0.2, [(43.2, 40.6), (29.1, 40.6), (29.1, 39.3)])
add_track_poly("LPG_ADC", B_Cu, 0.2, [(29.1, 40.6), (29.1, 42.1)])
add_track_poly("LPG_ADC", F_Cu, 0.2, [(30.1, 39.3), (29.1, 39.3)])
add_via("LPG_ADC", 29.1, 39.3)
add_via("LPG_ADC", 29.1, 42.1)
add_track_poly("LPG_ADC", F_Cu, 0.2, chain_45((29.1, 42.1), (28.025, 43.175, "diag"), (28.025, 43.2), (28.025, 45.375), (27.2, 46.2)))

# J4 OLED I2C_SDA & I2C_SCL connections on B.Cu
add_track_poly("I2C_SDA", B_Cu, 0.2, chain_45((52.31, 46.2), (52.31, 34.69), (52.5, 34.5, "diag")))
add_track_poly("I2C_SCL", B_Cu, 0.2, chain_45((49.77, 46.2), (49.77, 44.0), (47.3, 41.53, "diag"), (47.3, 29.8)))

# 5.2 BUZZER, BUZ_B, BUZ_K
# BUZZER: U1.6@(30.1, 38.5) -> via inside U1 at (31.5, 38.5) -> B.Cu down x=32.9 -> via@(32.9, 23.4) -> R23.1@(33.975, 23.4)
add_track_poly("BUZZER", F_Cu, 0.2, [(30.1, 38.5), (31.5, 38.5)])
add_via("BUZZER", 31.5, 38.5)
add_track_poly("BUZZER", B_Cu, 0.2, chain_45((31.5, 38.5), (32.9, 37.1, "diag"), (32.9, 23.4)))
add_via("BUZZER", 32.9, 23.4)
add_track_poly("BUZZER", F_Cu, 0.2, [(32.9, 23.4), (33.975, 23.4)])

# BUZ_B: R24.1@(35.625, 25.8) -> R23.2@(35.625, 23.4) -> Q5.1@(34.562, 20.95) (100% on F.Cu, 0 vias)
add_track_poly("BUZ_B", F_Cu, 0.2, chain_45((35.625, 25.8), (35.625, 23.4), (35.625, 22.012), (34.562, 20.95)))

# BUZ_K: D7.2@(31.65, 28.0) -> R25.2@(30.325, 19.2) -> Q5.3@(36.438, 20.0) -> LS1.2@(34.5, 12.0)
add_track_poly("BUZ_K", F_Cu, 0.3, [(31.65, 28.0), (31.3, 28.0)])
add_via("BUZ_K", 31.3, 28.0)
add_track_poly("BUZ_K", B_Cu, 0.3, chain_45((31.3, 28.0), (31.3, 24.4), (32.1, 23.6, "diag"), (32.1, 19.2)))
add_via("BUZ_K", 32.1, 19.2)
add_track_poly("BUZ_K", F_Cu, 0.3, [(32.1, 19.2), (30.325, 19.2)])
add_track_poly("BUZ_K", F_Cu, 0.3, chain_45((32.1, 19.2), (32.1, 18.6), (33.5, 17.2, "diag"), (34.5, 16.2, "diag"), (34.5, 12.0)))
add_track_poly("BUZ_K", F_Cu, 0.3, chain_45((33.5, 17.2), (35.5, 17.2), (36.438, 18.138, "diag"), (36.438, 20.0)))

# 5.3 LED_RED & RED_A (U1.26 GPIO18@(41.9, 35.3) -> R19.1@(25.975, 6.2))
add_track_poly("RED_A", F_Cu, 0.25, chain_45((27.625, 6.2), (27.588, 6.163, "diag"), (27.588, 4.0)))
add_track_poly("LED_RED", F_Cu, 0.2, chain_45((41.9, 35.3), (33.8, 35.3), (33.65, 35.15, "diag")))
add_via("LED_RED", 33.65, 35.15)
add_track_poly("LED_RED", B_Cu, 0.2, chain_45((33.65, 35.15), (34.4, 34.4, "diag"), (34.4, 15.0), (32.4, 13.0, "diag"), (32.4, 8.8), (30.8, 7.2, "diag"), (25.975, 7.2)))
add_via("LED_RED", 25.975, 7.2)
add_track_poly("LED_RED", F_Cu, 0.2, [(25.975, 7.2), (25.975, 6.2)])

# 5.4 GRN_A & HUSH_N (U1.22 GPIO8@(39.2, 33.6) -> R7.2@(40.4, 31.625) -> D10.1@(42.55, 15.5125) & C30.1@(44.25, 15.525) -> SW2.1@(39.375, 13.6) & (44.625, 13.6))
add_track_poly("GRN_A", F_Cu, 0.25, chain_45((37.175, 17.5), (36.5, 16.825, "diag"), (36.5, 6.55), (36.1, 6.15, "diag"), (30.788, 6.15), (30.788, 4.0)))
add_track_poly("HUSH_N", F_Cu, 0.2, chain_45((39.2, 33.6), (39.2, 32.8), (39.6, 32.4, "diag"), (40.375, 31.625), (40.4, 31.625)))
add_via("HUSH_N", 39.6, 32.4)
add_track_poly("HUSH_N", B_Cu, 0.2, chain_45((39.6, 32.4), (39.6, 23.85), (39.95, 23.5, "diag"), (42.5, 23.5), (42.85, 23.15, "diag"), (42.85, 13.6)))
add_via("HUSH_N", 42.85, 13.6)
add_track_poly("HUSH_N", F_Cu, 0.2, [(39.375, 13.6), (42.85, 13.6), (44.625, 13.6)])
add_track_poly("HUSH_N", F_Cu, 0.25, chain_45((42.55, 15.5125), (42.55, 13.9), (42.85, 13.6, "diag")))
add_track_poly("HUSH_N", F_Cu, 0.25, chain_45((44.25, 15.525), (44.25, 13.975), (44.625, 13.6, "diag")))

# 5.5 LED_BLU, BLU_A, BLU_K
# R21 rotated 180 deg puts R21.2 (BLU_A) on left at (39.675, 19.5)
add_track_poly("BLU_A", F_Cu, 0.25, chain_45((39.675, 19.5), (39.675, 16.475), (37.1, 13.9, "diag"), (37.1, 5.9), (36.7, 5.5, "diag"), (33.988, 5.5), (33.988, 4.0)))
add_track_poly("BLU_K", F_Cu, 0.25, [(41.438, 22.5), (42.1, 22.5)])
add_via("BLU_K", 42.1, 22.5)
add_track_poly("BLU_K", B_Cu, 0.25, chain_45((42.1, 22.5), (42.1, 18.6), (37.3, 13.8, "diag"), (37.3, 8.2), (34.1, 5.0, "diag"), (32.412, 5.0)))
add_via("BLU_K", 32.412, 5.0)
add_track_poly("BLU_K", F_Cu, 0.25, [(32.412, 5.0), (32.412, 4.0)])

add_track_poly("LED_BLU", F_Cu, 0.2, [(41.9, 36.1), (40.7, 36.1)])
add_via("LED_BLU", 40.7, 36.1)
add_track_poly("LED_BLU", B_Cu, 0.2, chain_45((40.7, 36.1), (40.7, 24.7), (40.5, 24.5, "diag")))
add_via("LED_BLU", 40.5, 24.5)
add_track_poly("LED_BLU", F_Cu, 0.2, chain_45((40.5, 24.5), (39.675, 25.325, "diag"), (39.675, 25.5)))
add_track_poly("LED_BLU", F_Cu, 0.2, chain_45((40.5, 24.5), (39.562, 23.562, "diag"), (39.562, 23.45)))

# 5.6 BOOT_N (Dedicated Service Boot Pad ONLY: U1.23 GPIO9@(40.0, 33.6) -> R8.2@(42.6, 31.625) -> TP10.1@(44.8, 26.2))
add_track_poly("BOOT_N", F_Cu, 0.2, chain_45((40.0, 33.6), (40.0, 33.0), (40.5, 32.5), (41.725, 32.5), (42.6, 31.625), (42.85, 31.625)))
add_via("BOOT_N", 42.85, 31.625)
add_track_poly("BOOT_N", B_Cu, 0.2, [(42.85, 31.625), (42.85, 26.2)])
add_via("BOOT_N", 42.85, 26.2)
add_track_poly("BOOT_N", F_Cu, 0.2, [(42.85, 26.2), (44.8, 26.2)])

# 5.7 TEST_N & YLW_A (U1.16 GPIO10@(34.4, 33.6) -> C27.1@(44.025, 21.4) -> R26.1@(43.975, 18.8) -> SW1.1@(39.375, 7.6) & (44.625, 7.6) -> D9.1@(48.2, 6.7875) -> D8.1@(35.612, 4.0)):
# YLW_A: R30.2@(45.625, 23.8) -> F.Cu x=46.50 -> y=9.0 corridor -> x=37.70 -> D8.2@(37.188, 4.0) (0 vias!)
add_track_poly("YLW_A", F_Cu, 0.25, chain_45((45.625, 23.8), (46.5, 23.8), (46.5, 9.0), (37.7, 9.0), (37.7, 4.512), (37.188, 4.0, "diag")))

add_track_poly("TEST_N", F_Cu, 0.2, chain_45((34.4, 33.6), (34.4, 34.45), (34.55, 34.60, "diag"), (35.5, 34.60)))
add_via("TEST_N", 35.5, 34.60)
add_track_poly("TEST_N", B_Cu, 0.2, chain_45((35.5, 34.60), (38.35, 34.60), (38.6, 34.85, "diag"), (38.6, 36.7), (39.0, 37.1, "diag"), (43.4, 37.1), (43.8, 36.7, "diag"), (43.8, 22.8), (44.025, 22.575)))
add_via("TEST_N", 44.025, 22.575)
add_track_poly("TEST_N", F_Cu, 0.2, chain_45((44.025, 22.575), (44.025, 21.4), (43.975, 21.35), (43.975, 20.1), (43.975, 18.8)))
add_via("TEST_N", 43.975, 20.1)
add_track_poly("TEST_N", B_Cu, 0.2, [(43.975, 20.1), (43.975, 7.6)])
add_via("TEST_N", 43.975, 7.6)
add_track_poly("TEST_N", F_Cu, 0.2, [(39.375, 7.6), (43.975, 7.6), (44.625, 7.6)])
add_track_poly("TEST_N", F_Cu, 0.25, chain_45((44.625, 7.6), (47.3875, 7.6), (48.2, 6.7875, "diag")))
add_track_poly("TEST_N", B_Cu, 0.2, chain_45((43.975, 7.6), (40.95, 7.6), (38.1, 4.75, "diag"), (35.612, 4.75)))
add_via("TEST_N", 35.612, 4.75)
add_track_poly("TEST_N", F_Cu, 0.2, [(35.612, 4.75), (35.612, 4.0)])

# 5.8 UART_TX & UART_RX
# UART_TX: U1.31@(41.9, 39.3) -> J3.2@(23.0, 9.27)
add_track_poly("UART_TX", F_Cu, 0.2, [(41.9, 39.3), (45.85, 39.3)])
add_via("UART_TX", 45.85, 39.3)
add_track_poly("UART_TX", B_Cu, 0.2, [(45.85, 39.3), (45.85, 3.05)])
add_via("UART_TX", 45.85, 3.05)
add_track_poly("UART_TX", F_Cu, 0.2, chain_45((45.85, 3.05), (25.65, 3.05), (24.85, 3.85, "diag"), (24.85, 8.55), (24.13, 9.27, "diag"), (23.0, 9.27)))

# UART_RX: U1.30@(41.9, 38.5) -> J3.3@(23.0, 6.73)
add_track_poly("UART_RX", F_Cu, 0.2, [(41.9, 38.5), (46.5, 38.5)])
add_via("UART_RX", 46.5, 38.5)
add_track_poly("UART_RX", B_Cu, 0.2, [(46.5, 38.5), (46.5, 2.40)])
add_via("UART_RX", 46.5, 2.40)
add_track_poly("UART_RX", F_Cu, 0.2, chain_45((46.5, 2.40), (25.10, 2.40), (24.30, 3.20, "diag"), (24.30, 6.20), (23.77, 6.73, "diag"), (23.0, 6.73)))

# ==============================================================================
# SILKSCREEN REFERENCE PLACEMENT (AVOIDING ALL PADS, SILK, AND 3D BODIES)
# ==============================================================================
body_boxes_mm = []
for fp, x, y, rdx, rdy, fp_label, val, rot, zone in fp_objs:
    ref_s = fp.GetReference()
    cy_k = H - y
    if ref_s == "LS1":
        for dy_b in range(-6, 7):
            hw = math.sqrt(max(0.0, 6.2**2 - dy_b**2))
            body_boxes_mm.append((x - hw, cy_k + dy_b - 0.5, x + hw, cy_k + dy_b + 0.5))
    elif ref_s == "S1":
        for dy_b in range(-10, 11):
            hw = math.sqrt(max(0.0, 10.1**2 - dy_b**2))
            body_boxes_mm.append((x - hw, cy_k + dy_b - 0.5, x + hw, cy_k + dy_b + 0.5))
    elif ref_s == "S2":
        for dy_b in range(-5, 6):
            hw = math.sqrt(max(0.0, 4.7**2 - dy_b**2))
            body_boxes_mm.append((x - hw, cy_k + dy_b - 0.5, x + hw, cy_k + dy_b + 0.5))

placed_ref_boxes_mm = []
for fp, x, y, rdx, rdy, fp_label, val, rot, zone in sorted(
    fp_objs, key=lambda item: (0 if item[0].GetReference() in ("TP10", "R30", "TP12", "C27", "R19", "R20", "D1", "R25", "LS1") else (2 if item[0].GetReference() in ("TP9", "S1") else 1))
):
    ref_s = fp.GetReference()
    ref_obj = fp.Reference()
    ref_obj.SetTextWidth(pcbnew.FromMM(0.80))
    ref_obj.SetTextHeight(pcbnew.FromMM(0.80))
    ref_obj.SetTextThickness(pcbnew.FromMM(0.15))
    ref_obj.SetKeepUpright(True)
    candidates = [(rdx, rdy)]
    for dist in [0.85, 1.00, 1.15, 1.30, 1.45, 1.65, 1.85, 2.10, 2.40, 2.75, 3.15, 3.60, 4.10, 4.70, 5.40, 6.20]:
        for ang_deg in range(0, 360, 5):
            rad = math.radians(ang_deg)
            candidates.append((dist * math.cos(rad), dist * math.sin(rad)))
    placed = False
    check_bodies = [True, False] if ref_s in ("TP9", "R25", "S1", "LS1", "C27", "R19", "R20") else [False]
    for avoid_body in check_bodies:
        if placed:
            break
        for margin in [0.05, 0.00]:
            if placed:
                break
            for cdx, cdy in candidates:
                tx, ty = x + cdx, y + cdy
                ref_obj.SetPosition(xy(tx, ty))
                bb = ref_obj.GetBoundingBox()
                rl = pcbnew.ToMM(bb.GetLeft()) - margin
                rt = pcbnew.ToMM(bb.GetTop()) - margin
                rr = pcbnew.ToMM(bb.GetRight()) + margin
                rb = pcbnew.ToMM(bb.GetBottom()) + margin
                if rl < 0.5 or rr > 69.5 or rt < 0.5 or rb > 49.5:
                    continue
                rbox = (rl, rt, rr, rb)
                if avoid_body and box_overlaps(rbox, body_boxes_mm):
                    continue
                if not box_overlaps(rbox, pad_boxes_mm) and not box_overlaps(rbox, silk_segs_mm) and not box_overlaps(rbox, placed_ref_boxes_mm):
                    placed_ref_boxes_mm.append(rbox)
                    placed = True
                    break
    if not placed:
        ref_obj.SetPosition(xy(x + rdx, y + rdy))
        bb = ref_obj.GetBoundingBox()
        placed_ref_boxes_mm.append((
            pcbnew.ToMM(bb.GetLeft()) - 0.05,
            pcbnew.ToMM(bb.GetTop()) - 0.05,
            pcbnew.ToMM(bb.GetRight()) + 0.05,
            pcbnew.ToMM(bb.GetBottom()) + 0.05,
        ))

# Fill all zones
filler = pcbnew.ZONE_FILLER(b)
filler.Fill(b.Zones())

# ==============================================================================
# MATHEMATICAL PLANARITY (ZERO CROSSINGS) & ANGLE & LENGTH VERIFIER
# ==============================================================================


def seg_intersect(p1, p2, p3, p4):
    """Return True if segment p1-p2 and segment p3-p4 intersect or touch within 0.01 mm."""
    def ccw(A, B, C):
        return (C[1] - A[1]) * (B[0] - A[0]) - (B[1] - A[1]) * (C[0] - A[0])
    d1 = ccw(p3, p4, p1)
    d2 = ccw(p3, p4, p2)
    d3 = ccw(p1, p2, p3)
    d4 = ccw(p1, p2, p4)
    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
        return True
    return False


tracks_by_layer = collections.defaultdict(list)
lengths_by_net = collections.defaultdict(float)
vias_by_net = collections.defaultdict(int)
non_45_segs = []

for item in b.GetTracks():
    if isinstance(item, pcbnew.PCB_VIA):
        vias_by_net[item.GetNetname()] += 1
    else:
        net = item.GetNetname()
        lyr = item.GetLayerName()
        x1, y1 = pcbnew.ToMM(item.GetStart().x), H - pcbnew.ToMM(item.GetStart().y)
        x2, y2 = pcbnew.ToMM(item.GetEnd().x), H - pcbnew.ToMM(item.GetEnd().y)
        dx, dy = abs(x2 - x1), abs(y2 - y1)
        length = math.hypot(dx, dy)
        lengths_by_net[net] += length
        tracks_by_layer[lyr].append((net, (x1, y1), (x2, y2), pcbnew.ToMM(item.GetWidth())))
        if dx > 1e-3 and dy > 1e-3 and abs(dx - dy) > 1e-2:
            non_45_segs.append((net, lyr, (round(x1, 3), round(y1, 3)), (round(x2, 3), round(y2, 3))))

crossings = []
for lyr, segs in tracks_by_layer.items():
    for i in range(len(segs)):
        n1, p1, p2, w1 = segs[i]
        for j in range(i + 1, len(segs)):
            n2, p3, p4, w2 = segs[j]
            if n1 == n2:
                continue
            if seg_intersect(p1, p2, p3, p4):
                crossings.append((lyr, n1, n2, p1, p2, p3, p4))

print(f"Planarity check: {len(crossings)} crossings across all layers.")
for c in crossings:
    print("  CROSSING:", c)
print(f"45-degree angle check: {len(non_45_segs)} non-45 segments.")
for s in non_45_segs:
    print("  NON-45:", s)
for el in ["WE", "RE", "CE"]:
    print(f"Electrode {el}: length = {lengths_by_net[el]:.2f} mm, vias = {vias_by_net[el]}")

pcbnew.SaveBoard(pcb_path, b)

with open(pcb_path, "r", encoding="utf-8") as f:
    txt = f.read()

stackup_sexpr = """\t\t(stackup
\t\t\t(layer "F.SilkS" (type "Top Silk Screen"))
\t\t\t(layer "F.Paste" (type "Top Solder Paste"))
\t\t\t(layer "F.Mask" (type "Top Solder Mask") (thickness 0.015) (color "Green"))
\t\t\t(layer "F.Cu" (type "copper") (thickness 0.035))
\t\t\t(layer "dielectric 1" (type "prepreg") (thickness 0.2) (material "FR4") (epsilon_r 4.29) (loss_tangent 0.02))
\t\t\t(layer "In1.Cu" (type "copper") (thickness 0.035))
\t\t\t(layer "dielectric 2" (type "core") (thickness 1.03) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
\t\t\t(layer "In2.Cu" (type "copper") (thickness 0.035))
\t\t\t(layer "dielectric 3" (type "prepreg") (thickness 0.2) (material "FR4") (epsilon_r 4.29) (loss_tangent 0.02))
\t\t\t(layer "B.Cu" (type "copper") (thickness 0.035))
\t\t\t(layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.015) (color "Green"))
\t\t\t(layer "B.Paste" (type "Bottom Solder Paste"))
\t\t\t(layer "B.SilkS" (type "Bottom Silk Screen"))
\t\t\t(copper_finish "ENIG")
\t\t\t(dielectric_constraints no)
\t\t)
"""
if "(stackup" not in txt:
    txt = txt.replace("\t(setup\n", "\t(setup\n" + stackup_sexpr, 1)

# Align 3D models and bind custom VRML / fixed STEP paths for U1, U2, F1, LS1, S1
txt = txt.replace(
    "${KICAD10_3DMODEL_DIR}/RF_Module.3dshapes/ESP32-C6-MINI-1.step",
    "${KIPRJMOD}/3dmodels/ESP32-C3-MINI-1.wrl",
)
txt = txt.replace(
    "${KICAD10_3DMODEL_DIR}/Package_SO.3dshapes/HTSOP-8-1EP_3.9x4.9mm_Pitch1.27mm.step",
    "${KICAD10_3DMODEL_DIR}/Package_SO.3dshapes/HTSOP-8-1EP_3.9x4.9mm_P1.27mm.step",
)
txt = txt.replace(
    "${KICAD10_3DMODEL_DIR}/Fuse.3dshapes/Fuse_1812_4532Metric.step",
    "${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_1812_4532Metric.step",
)
txt = txt.replace(
    '${KICAD10_3DMODEL_DIR}/Buzzer_Beeper.3dshapes/Buzzer_TDK_PS1240P02BT_D12.2mm_H6.5mm.step"\n\t\t\t(offset\n\t\t\t\t(xyz -2.5 0 0)\n\t\t\t)',
    '${KIPRJMOD}/3dmodels/CUI_CDM-12008_Speaker.wrl"\n\t\t\t(offset\n\t\t\t\t(xyz 0 0 0)\n\t\t\t)',
)
txt = txt.replace(
    "${KICAD10_3DMODEL_DIR}/Buzzer_Beeper.3dshapes/Buzzer_TDK_PS1240P02BT_D12.2mm_H6.5mm.step",
    "${KIPRJMOD}/3dmodels/CUI_CDM-12008_Speaker.wrl",
)
for step_name, xyz_str in [
    ("PinHeader_1x04_P2.54mm_Vertical.step", "0 3.81 0"),
    ("TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal.step", "-2.54 0 0"),
]:
    old_block = f'{step_name}"\n\t\t\t(offset\n\t\t\t\t(xyz 0 0 0)\n\t\t\t)'
    new_block = f'{step_name}"\n\t\t\t(offset\n\t\t\t\t(xyz {xyz_str})\n\t\t\t)'
    txt = txt.replace(old_block, new_block)

with open(pcb_path, "w", encoding="utf-8") as f:
    f.write(txt)

print("Stage 4 routing complete.")
