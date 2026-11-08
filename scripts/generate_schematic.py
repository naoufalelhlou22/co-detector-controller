import collections
import os
import subprocess
import sys
import uuid

# Auto-relaunch under KiCad 10's bundled Python if invoked from system Python
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
sch_path = os.path.join(proj_dir, "co_detector_controller.kicad_sch")
sym_lib_path = os.path.join(proj_dir, "co_detector_symbols.kicad_sym")
sym_table_path = os.path.join(proj_dir, "sym-lib-table")
fp_table_path = os.path.join(proj_dir, "fp-lib-table")
custom_pretty_dir = os.path.join(proj_dir, "custom_lib.pretty")
std_fp_dir = r"C:\Program Files\KiCad\10.0\share\kicad\footprints"
os.makedirs(custom_pretty_dir, exist_ok=True)


def det_uuid(tag: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"co_detector_controller.{tag}"))


root_sch_uuid = det_uuid("root_schematic")

# Initialize KiCad footprint IO plugin
_ = pcbnew.FootprintLoad(os.path.join(std_fp_dir, "Resistor_SMD.pretty"), "R_0603_1608Metric")

# Pin function names for multi-pin ICs and specialized parts (Rev 4.0)
PIN_LABELS = {
    "U1": {
        "1": "GND",
        "2": "GND",
        "3": "+3V3",
        "4": "NC_4",
        "5": "IO2_LPG_ADC",
        "6": "IO3_BUZZER",
        "7": "NC_7",
        "8": "EN_NRST",
        "9": "NC_9",
        "10": "NC_10",
        "11": "GND",
        "12": "IO0_VBAT_ADC",
        "13": "IO1_LED_OK",
        "14": "GND",
        "15": "NC_15",
        "16": "IO10_TEST_N",
        "17": "NC_17",
        "18": "IO4_SDA",
        "19": "IO5_SCL",
        "20": "IO6_LED_ALM",
        "21": "IO7_WDI",
        "22": "IO8_HUSH_N",
        "23": "IO9_LED_WIFI",
        "24": "NC_24",
        "25": "IO19_RXD0",
        "26": "IO18_TXD0",
        "27": "NC_27",
        "28": "NC_28",
        "29": "NC_29",
        "30": "NC_30",
        "31": "NC_31",
        "32": "NC_32",
        "33": "GND",
        "34": "NC_34",
        "35": "NC_35",
    },
    "U2": {
        "1": "GND",
        "2": "VIN",
        "3": "EN",
        "4": "NC",
        "5": "FB",
        "6": "VCC",
        "7": "BOOT",
        "8": "SW",
        "9": "EP",
    },
    "U5": {
        "1": "~{MR}",
        "2": "GND",
        "3": "WDI",
        "4": "VDD",
        "5": "~{RESET}",
    },
    "U7": {
        "1": "TEMP",
        "2": "PROG",
        "3": "GND",
        "4": "VCC",
        "5": "BAT",
        "6": "STDBY",
        "7": "CHRG",
        "8": "CE",
        "9": "EP",
    },
    "U8": {
        "1": "OD",
        "2": "CS",
        "3": "OC",
        "4": "TD",
        "5": "VCC",
        "6": "GND",
    },
    "U9": {
        "1": "VIN",
        "2": "GND",
        "3": "EN",
        "4": "NC",
        "5": "VOUT",
    },
    "S2": {
        "1": "HTR-",
        "2": "SNS-",
        "3": "SNS+",
        "4": "HTR+",
    },
    "J1": {
        "1": "+12V_IN",
        "2": "GND",
    },
    "J3": {
        "1": "GND",
        "2": "+3V3",
        "3": "TX",
        "4": "RX",
    },
    "J4": {
        "1": "GND",
        "2": "+3V3",
        "3": "SCL",
        "4": "SDA",
    },
    "J_BAT": {
        "1": "VBAT",
        "2": "BAT_PROT",
    },
    "Q1": {"1": "G", "2": "S", "3": "D"},
    "Q4": {
        "1": "D12",
        "2": "S1",
        "3": "S1",
        "4": "G1",
        "5": "G2",
        "6": "S2",
        "7": "S2",
        "8": "D12",
    },
    "Q5": {"1": "G", "2": "S", "3": "D"},
    "Q6": {"1": "B", "2": "E", "3": "C"},
    "SW1": {"1": "TEST_N", "2": "GND", "3": "TEST_N", "4": "GND"},
    "SW2": {"1": "HUSH_N", "2": "GND", "3": "HUSH_N", "4": "GND"},
    "SW3": {"1": "MR_N", "2": "GND", "3": "MR_N", "4": "GND"},
}

# Map each footprint item name to its standard KiCad 10 library nickname
STD_FP_LIB_MAP = {
    "R_0603_1608Metric": ("Resistor_SMD", "R_0603_1608Metric"),
    "C_0603_1608Metric": ("Capacitor_SMD", "C_0603_1608Metric"),
    "C_0805_2012Metric": ("Capacitor_SMD", "C_0805_2012Metric"),
    "C_1206_3216Metric": ("Capacitor_SMD", "C_1206_3216Metric"),
    "C_1210_3225Metric": ("Capacitor_SMD", "C_1210_3225Metric"),
    "CP_Elec_6.3x7.7": ("Capacitor_SMD", "CP_Elec_6.3x7.7"),
    "D_SMB": ("Diode_SMD", "D_SMB"),
    "D_SMA": ("Diode_SMD", "D_SMA"),
    "D_SOD-123": ("Diode_SMD", "D_SOD-123"),
    "D_0603_1608Metric": ("Diode_SMD", "D_0603_1608Metric"),
    "LED_0603_1608Metric": ("LED_SMD", "LED_0603_1608Metric"),
    "Fuse_1812_4532Metric": ("Fuse", "Fuse_1812_4532Metric"),
    "L_Coilcraft_XAL5030-XXX": ("Inductor_SMD", "L_Coilcraft_XAL5030-XXX"),
    "L_0603_1608Metric": ("Inductor_SMD", "L_0603_1608Metric"),
    "SOT-23": ("Package_TO_SOT_SMD", "SOT-23"),
    "SOT-23-5": ("Package_TO_SOT_SMD", "SOT-23-5"),
    "SW_SPST_PTS647_Sx50": ("Button_Switch_SMD", "SW_SPST_PTS647_Sx50"),
    "Buzzer_TDK_PS1240P02BT_D12.2mm_H6.5mm": ("Buzzer_Beeper", "Buzzer_TDK_PS1240P02BT_D12.2mm_H6.5mm"),
    "PinHeader_1x04_P2.54mm_Vertical": ("Connector_PinHeader_2.54mm", "PinHeader_1x04_P2.54mm_Vertical"),
    "TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal": (
        "TerminalBlock_Phoenix",
        "TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal",
    ),
    "NetTie-2_SMD_Pad0.5mm": ("NetTie", "NetTie-2_SMD_Pad0.5mm"),
    "TestPoint_Pad_D1.5mm": ("TestPoint", "TestPoint_Pad_D1.5mm"),
    "MountingHole_3.2mm_M3": ("MountingHole", "MountingHole_3.2mm_M3"),
    "Fiducial_1mm_Mask2mm": ("Fiducial", "Fiducial_1mm_Mask2mm"),
    "ESP32-C6-MINI-1": ("RF_Module", "ESP32-C6-MINI-1"),
    "ESP32-C3-MINI-1": ("RF_Module", "ESP32-C6-MINI-1"),
    "Winsen_ME3-CO_Socket": ("TestPoint", "TestPoint_Pad_D1.5mm"),
    "Figaro_TGS2610_TO5": ("TestPoint", "TestPoint_Pad_D1.5mm"),
    "TI_SO-PowerPAD-8_ThermalVias": ("Package_SO", "TI_SO-PowerPAD-8_ThermalVias"),
    "SOIC-8_3.9x4.9mm_P1.27mm": ("Package_SO", "SOIC-8_3.9x4.9mm_P1.27mm"),
    "SOT-23-6": ("Package_TO_SOT_SMD", "SOT-23-6"),
    "JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal": ("Connector_JST", "JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal"),
    "MKDS-1,5-2-5.08_Centered": ("TerminalBlock_Phoenix", "TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal"),
    "WSON-14-1EP_4.0x4.0mm_P0.5mm_EP2.6x2.6mm": (
        "Package_SON",
        "WSON-14-1EP_4.0x4.0mm_P0.5mm_EP2.6x2.6mm",
    ),
}

# Load PCB and link footprint paths + library nicknames + unconnected pad net names
b = pcbnew.LoadBoard(pcb_path)
fps_by_ref = {}

for fp in b.GetFootprints():
    ref = fp.GetReference()
    sym_uuid = det_uuid(f"sym.{ref}")
    fp.SetPath(pcbnew.KIID_PATH(f"/{sym_uuid}"))

    raw_fpid = fp.GetFPIDAsString()
    fp_item = raw_fpid.split(":")[-1] if ":" in raw_fpid else raw_fpid
    if fp_item.startswith(f"{ref}_"):
        fp_item = fp_item[len(ref) + 1 :]
    lib_nick, std_item = STD_FP_LIB_MAP[fp_item]
    fp.SetFPID(pcbnew.LIB_ID(lib_nick, std_item))

    # Synchronize unconnected pad net names with KiCad's schematic netlist convention
    lbls = PIN_LABELS.get(ref, {})
    for p in fp.Pads():
        pnum = p.GetNumber()
        if not pnum:
            continue
        net_name = p.GetNetname()
        if not net_name or net_name.startswith("unconnected-("):
            pname = lbls.get(pnum, f"P{pnum}")
            unc_net_name = f"unconnected-({ref}-{pname}-Pad{pnum})"
            ni = b.FindNet(unc_net_name)
            if not ni:
                ni = pcbnew.NETINFO_ITEM(b, unc_net_name)
                b.Add(ni)
            p.SetNet(ni)

    fps_by_ref[ref] = fp

pcbnew.SaveBoard(pcb_path, b)

if os.path.exists(fp_table_path):
    os.remove(fp_table_path)

# Write project sym-lib-table
with open(sym_table_path, "w", encoding="utf-8") as f:
    f.write(
        """(sym_lib_table
  (version 7)
  (lib (name "CO_Detector")(type "KiCad")(uri "${KIPRJMOD}/co_detector_symbols.kicad_sym")(options "")(descr "CO Detector Controller Symbols"))
)
"""
    )


def build_lib_symbol_and_pins(ref: str, fp):
    sym_item = f"{ref}_SYM"
    lib_name = f"CO_Detector:{sym_item}"
    val = fp.GetValue()
    fpid_str = fp.GetFPIDAsString()
    in_bom_str = "no" if bool(fp.GetAttributes() & pcbnew.FP_EXCLUDE_FROM_BOM) else "yes"
    ds_str = "https://www.ckswitches.com/media/2567/pts647.pdf" if ref in ("SW1", "SW2", "SW3") else ""

    pad_nets = collections.OrderedDict()
    for p in fp.Pads():
        pnum = p.GetNumber()
        if not pnum:
            continue
        if pnum not in pad_nets:
            net_n = p.GetNetname()
            if net_n.startswith("unconnected-("):
                net_n = ""
            pad_nets[pnum] = net_n

    all_pin_nums = list(pad_nets.keys())
    pin_defs = []
    vis_conns = []
    gfx = []

    if len(all_pin_nums) == 0:
        gfx.append(
            """\t\t\t\t(circle
\t\t\t\t\t(center 0 0)
\t\t\t\t\t(radius 1.27)
\t\t\t\t\t(stroke (width 0.254) (type default))
\t\t\t\t\t(fill (type none))
\t\t\t\t)"""
        )
        ref_y = 2.54
        val_y = -2.54

    elif len(all_pin_nums) == 1:
        pnum = all_pin_nums[0]
        net = pad_nets[pnum]
        gfx.append(
            """\t\t\t\t(circle
\t\t\t\t\t(center 1.27 0)
\t\t\t\t\t(radius 1.27)
\t\t\t\t\t(stroke (width 0.254) (type default))
\t\t\t\t\t(fill (type none))
\t\t\t\t)"""
        )
        pin_defs.append(
            f"""\t\t\t\t(pin passive line
\t\t\t\t\t(at -2.54 0 0)
\t\t\t\t\t(length 2.54)
\t\t\t\t\t(name "TP" (effects (font (size 1.0 1.0)) (hide yes)))
\t\t\t\t\t(number "{pnum}" (effects (font (size 1.0 1.0)) (hide yes)))
\t\t\t\t)"""
        )
        vis_conns.append((pnum, -2.54, 0.0, "L", net))
        ref_y = 2.54
        val_y = -2.54

    elif len(all_pin_nums) == 2:
        p1, p2 = all_pin_nums[0], all_pin_nums[1]
        n1, n2 = pad_nets[p1], pad_nets[p2]
        if ref.startswith("C"):
            gfx.append(
                """\t\t\t\t(polyline
\t\t\t\t\t(pts (xy -0.635 -2.032) (xy -0.635 2.032))
\t\t\t\t\t(stroke (width 0.35) (type default))
\t\t\t\t\t(fill (type none))
\t\t\t\t)
\t\t\t\t(polyline
\t\t\t\t\t(pts (xy 0.635 -2.032) (xy 0.635 2.032))
\t\t\t\t\t(stroke (width 0.35) (type default))
\t\t\t\t\t(fill (type none))
\t\t\t\t)
\t\t\t\t(polyline
\t\t\t\t\t(pts (xy -2.54 0) (xy -0.635 0))
\t\t\t\t\t(stroke (width 0.254) (type default))
\t\t\t\t\t(fill (type none))
\t\t\t\t)
\t\t\t\t(polyline
\t\t\t\t\t(pts (xy 0.635 0) (xy 2.54 0))
\t\t\t\t\t(stroke (width 0.254) (type default))
\t\t\t\t\t(fill (type none))
\t\t\t\t)"""
            )
        elif ref.startswith("D"):
            gfx.append(
                """\t\t\t\t(polyline
\t\t\t\t\t(pts (xy 1.27 -1.27) (xy 1.27 1.27) (xy -1.27 0) (xy 1.27 -1.27))
\t\t\t\t\t(stroke (width 0.254) (type default))
\t\t\t\t\t(fill (type none))
\t\t\t\t)
\t\t\t\t(polyline
\t\t\t\t\t(pts (xy -1.27 -1.27) (xy -1.27 1.27))
\t\t\t\t\t(stroke (width 0.3) (type default))
\t\t\t\t\t(fill (type none))
\t\t\t\t)
\t\t\t\t(polyline
\t\t\t\t\t(pts (xy -2.54 0) (xy 2.54 0))
\t\t\t\t\t(stroke (width 0.2) (type default))
\t\t\t\t\t(fill (type none))
\t\t\t\t)"""
            )
        else:
            gfx.append(
                """\t\t\t\t(rectangle
\t\t\t\t\t(start -2.54 1.27)
\t\t\t\t\t(end 2.54 -1.27)
\t\t\t\t\t(stroke (width 0.254) (type default))
\t\t\t\t\t(fill (type background))
\t\t\t\t)"""
            )
        pin_defs.append(
            f"""\t\t\t\t(pin passive line
\t\t\t\t\t(at -5.08 0 0)
\t\t\t\t\t(length 2.54)
\t\t\t\t\t(name "{PIN_LABELS.get(ref, {}).get(p1, '~')}" (effects (font (size 0.9 0.9)) (hide yes)))
\t\t\t\t\t(number "{p1}" (effects (font (size 0.9 0.9))))
\t\t\t\t)"""
        )
        pin_defs.append(
            f"""\t\t\t\t(pin passive line
\t\t\t\t\t(at 5.08 0 180)
\t\t\t\t\t(length 2.54)
\t\t\t\t\t(name "{PIN_LABELS.get(ref, {}).get(p2, '~')}" (effects (font (size 0.9 0.9)) (hide yes)))
\t\t\t\t\t(number "{p2}" (effects (font (size 0.9 0.9))))
\t\t\t\t)"""
        )
        vis_conns.append((p1, -5.08, 0.0, "L", n1))
        vis_conns.append((p2, 5.08, 0.0, "R", n2))
        ref_y = 2.54
        val_y = -2.54

    elif len(all_pin_nums) == 3:
        gfx.append(
            """\t\t\t\t(rectangle
\t\t\t\t\t(start -3.81 3.81)
\t\t\t\t\t(end 3.81 -3.81)
\t\t\t\t\t(stroke (width 0.254) (type default))
\t\t\t\t\t(fill (type background))
\t\t\t\t)"""
        )
        lbls = PIN_LABELS.get(ref, {})
        coords = [
            ("1", -6.35, 0.0, 0, "L"),
            ("3", 6.35, 2.54, 180, "R"),
            ("2", 6.35, -2.54, 180, "R"),
        ]
        for pnum, lx, ly, ang, side in coords:
            pname = lbls.get(pnum, pnum)
            pin_defs.append(
                f"""\t\t\t\t(pin passive line
\t\t\t\t\t(at {lx} {ly} {ang})
\t\t\t\t\t(length 2.54)
\t\t\t\t\t(name "{pname}" (effects (font (size 1.0 1.0))))
\t\t\t\t\t(number "{pnum}" (effects (font (size 0.9 0.9))))
\t\t\t\t)"""
            )
            vis_conns.append((pnum, lx, ly, side, pad_nets.get(pnum, "")))
        ref_y = 5.08
        val_y = -5.08

    else:
        lbls = PIN_LABELS.get(ref, {})
        if ref == "U1":
            left_pins = ["3", "8", "12", "13", "18", "19", "23", "25", "26", "1"]
            right_pins = ["5", "6", "16", "20", "21", "22", "4", "7", "9", "10", "15", "17", "24", "27", "28", "29", "30", "31", "32", "34", "35"]
            stacked_on_1 = [p for p in all_pin_nums if p in ["2", "11", "14", "33"]]
        elif ref == "U2":
            left_pins = ["2", "3", "6", "1"]
            right_pins = ["7", "8", "5", "4"]
            stacked_on_1 = ["9"] if "9" in all_pin_nums else []
        elif ref == "U7":
            left_pins = ["4", "8", "2", "1", "3"]
            right_pins = ["5", "6", "7"]
            stacked_on_1 = ["9"] if "9" in all_pin_nums else []
        elif ref == "U8":
            left_pins = ["5", "6", "2"]
            right_pins = ["1", "3", "4"]
            stacked_on_1 = []
        elif ref == "U9":
            left_pins = ["1", "3", "2"]
            right_pins = ["5", "4"]
            stacked_on_1 = []
        elif ref == "Q4":
            left_pins = ["4", "5", "2", "3", "6", "7"]
            right_pins = ["1", "8"]
            stacked_on_1 = []
        elif ref == "S2":
            left_pins = ["3", "4"]
            right_pins = ["2", "1"]
            stacked_on_1 = []
        elif ref in ("J3", "J4"):
            left_pins = ["1", "2"]
            right_pins = ["3", "4"]
            stacked_on_1 = []
        else:
            half = (len(all_pin_nums) + 1) // 2
            left_pins = all_pin_nums[:half]
            right_pins = all_pin_nums[half:]
            stacked_on_1 = []

        max_rows = max(len(left_pins), len(right_pins))
        half_h = max((max_rows * 2.54) / 2.0 + 1.27, 5.08)
        half_h = round(half_h / 1.27) * 1.27
        box_w = 12.7 if ref == "U1" else (8.89 if ref in ("U2", "U7", "Q4") else 6.35)
        pin_x = box_w + 2.54

        gfx.append(
            f"""\t\t\t\t(rectangle
\t\t\t\t\t(start {-box_w} {half_h})
\t\t\t\t\t(end {box_w} {-half_h})
\t\t\t\t\t(stroke (width 0.254) (type default))
\t\t\t\t\t(fill (type background))
\t\t\t\t)"""
        )

        top_y = round(((max_rows - 1) * 2.54) / 2.0 / 2.54) * 2.54
        gnd_anchor_coord = None

        for idx, pnum in enumerate(left_pins):
            ly = round((top_y - idx * 2.54), 2)
            pname = lbls.get(pnum, f"P{pnum}")
            pin_defs.append(
                f"""\t\t\t\t(pin passive line
\t\t\t\t\t(at {-pin_x} {ly} 0)
\t\t\t\t\t(length 2.54)
\t\t\t\t\t(name "{pname}" (effects (font (size 1.0 1.0))))
\t\t\t\t\t(number "{pnum}" (effects (font (size 0.9 0.9))))
\t\t\t\t)"""
            )
            vis_conns.append((pnum, -pin_x, ly, "L", pad_nets.get(pnum, "")))
            if pnum in ("1", "3"):
                gnd_anchor_coord = (-pin_x, ly, 0)

        for idx, pnum in enumerate(right_pins):
            ly = round((top_y - idx * 2.54), 2)
            pname = lbls.get(pnum, f"P{pnum}")
            pin_defs.append(
                f"""\t\t\t\t(pin passive line
\t\t\t\t\t(at {pin_x} {ly} 180)
\t\t\t\t\t(length 2.54)
\t\t\t\t\t(name "{pname}" (effects (font (size 1.0 1.0))))
\t\t\t\t\t(number "{pnum}" (effects (font (size 0.9 0.9))))
\t\t\t\t)"""
            )
            vis_conns.append((pnum, pin_x, ly, "R", pad_nets.get(pnum, "")))

        for pnum in stacked_on_1:
            if gnd_anchor_coord:
                ax, ay, aang = gnd_anchor_coord
                pin_defs.append(
                    f"""\t\t\t\t(pin passive line
\t\t\t\t\t(at {ax} {ay} {aang})
\t\t\t\t\t(length 2.54)
\t\t\t\t\t(hide yes)
\t\t\t\t\t(name "GND" (effects (font (size 1.0 1.0))))
\t\t\t\t\t(number "{pnum}" (effects (font (size 0.9 0.9))))
\t\t\t\t)"""
                )

        ref_y = half_h + 1.27
        val_y = -half_h - 1.27

    def make_sym_block(header_name: str) -> str:
        return f"""\t\t(symbol "{header_name}"
\t\t\t(pin_names (offset 1.016))
\t\t\t(exclude_from_sim no)
\t\t\t(in_bom {in_bom_str})
\t\t\t(on_board yes)
\t\t\t(duplicate_pin_numbers_are_jumpers no)
\t\t\t(property "Reference" "{ref}"
\t\t\t\t(at 0 {ref_y:.2f} 0)
\t\t\t\t(effects (font (size 1.27 1.27)))
\t\t\t)
\t\t\t(property "Value" "{val}"
\t\t\t\t(at 0 {val_y:.2f} 0)
\t\t\t\t(effects (font (size 1.1 1.1)))
\t\t\t)
\t\t\t(property "Footprint" "{fpid_str}"
\t\t\t\t(at 0 0 0)
\t\t\t\t(effects (font (size 1.0 1.0)) (hide yes))
\t\t\t)
\t\t\t(property "Datasheet" "{ds_str}"
\t\t\t\t(at 0 0 0)
\t\t\t\t(effects (font (size 1.0 1.0)) (hide yes))
\t\t\t)
\t\t\t(symbol "{sym_item}_0_1"
{chr(10).join(gfx)}
\t\t\t)
\t\t\t(symbol "{sym_item}_1_1"
{chr(10).join(pin_defs)}
\t\t\t)
\t\t\t(embedded_fonts no)
\t\t)"""

    return lib_name, make_sym_block(lib_name), make_sym_block(sym_item), vis_conns, all_pin_nums, ref_y, val_y, in_bom_str, ds_str


def snap(v: float) -> float:
    return round(round(v / 2.54) * 2.54, 2)


# REV 4.0 FUNCTIONAL BLOCK SCHEMATIC LAYOUT
BLOCK_LAYOUT = [
    # --- BLOCK 1: 12V DC Input Protection & TPS54302 Buck Regulator (12V -> 5V) ---
    ("J1", 45.72, 50.80),
    ("F1", 45.72, 73.66),
    ("D1", 45.72, 96.52),
    ("Q1", 45.72, 119.38),
    ("D3", 45.72, 142.24),
    ("R1", 45.72, 165.10),
    ("C2", 45.72, 187.96),
    ("C3", 45.72, 210.82),

    ("U2", 137.16, 76.20),
    ("R2", 137.16, 114.30),
    ("C5", 137.16, 137.16),
    ("C6", 137.16, 160.02),
    ("L1", 137.16, 182.88),
    ("R4", 137.16, 205.74),
    ("R5", 137.16, 228.60),

    ("C8", 218.44, 63.50),
    ("C9", 218.44, 88.90),
    ("TP1", 218.44, 127.00),
    ("TP2", 218.44, 152.40),

    # --- BLOCK 2: Battery Charger (TP4056), BMS (DW01A+FS8205A), Power-Path & LDO & Watchdog ---
    ("U7", 45.72, 325.12),
    ("R_PROG", 45.72, 365.76),
    ("C_CHG1", 45.72, 396.24),
    ("C_CHG2", 45.72, 426.72),

    ("J_BAT", 127.00, 325.12),
    ("U8", 127.00, 365.76),
    ("Q4", 127.00, 416.56),
    ("R_PROT", 127.00, 467.36),
    ("C_PROT", 127.00, 497.84),

    ("Q5", 208.28, 325.12),
    ("D2", 208.28, 355.60),
    ("R_PULL", 208.28, 386.08),
    ("R_B1", 208.28, 421.64),
    ("R_B2", 208.28, 452.12),
    ("C_B", 208.28, 482.60),
    ("TP3", 208.28, 513.08),

    ("U9", 289.56, 325.12),
    ("C10", 289.56, 365.76),
    ("C11", 289.56, 396.24),
    ("TP4", 289.56, 426.72),
    ("U5", 289.56, 467.36),
    ("C22", 289.56, 502.92),
    ("R13", 289.56, 528.32),
    ("R14", 289.56, 553.72),
    ("SW3", 289.56, 579.12),

    # --- BLOCK 3: Figaro TGS2610-C00 LPG Combustible Gas Sensor & I2C OLED Display ---
    ("S2", 469.90, 66.04),
    ("R27", 469.90, 114.30),
    ("C29", 469.90, 139.70),
    ("R28", 469.90, 165.10),
    ("R29", 469.90, 190.50),
    ("C28", 469.90, 215.90),

    ("J4", 629.92, 88.90),
    ("R7", 629.92, 139.70),
    ("R8", 629.92, 165.10),

    # --- BLOCK 4: ESP32-C3-MINI-1 Wireless MCU, Buzzer, LEDs, Buttons & UART ---
    ("U1", 469.90, 370.84),
    ("C15", 469.90, 467.36),
    ("C16", 469.90, 492.76),
    ("R6", 469.90, 518.16),
    ("C17", 469.90, 543.56),
    ("J3", 469.90, 574.04),

    ("LS1", 579.12, 320.04),
    ("Q6", 579.12, 355.60),
    ("SW1", 579.12, 396.24),
    ("C27", 579.12, 426.72),
    ("SW2", 579.12, 462.28),
    ("C26", 579.12, 492.76),

    ("D4", 665.48, 320.04),
    ("R19", 665.48, 345.44),
    ("D5", 665.48, 375.92),
    ("R20", 665.48, 401.32),
    ("D6", 665.48, 431.80),
    ("R25", 665.48, 457.20),
    ("D7", 665.48, 487.68),
    ("R26", 665.48, 513.08),

    ("H1", 741.68, 320.04),
    ("H2", 741.68, 350.52),
    ("H3", 741.68, 381.00),
    ("H4", 741.68, 411.48),
    ("FID1", 741.68, 452.12),
    ("FID2", 741.68, 482.60),
]

lib_symbols_sch_list = []
lib_symbols_ext_list = []
placed_symbols_list = []
wires_and_labels_list = []

for ref, sx_raw, sy_raw in BLOCK_LAYOUT:
    sx = snap(sx_raw)
    sy = snap(sy_raw)
    fp = fps_by_ref[ref]
    lib_name, sym_sch_sexpr, sym_ext_sexpr, vis_conns, all_pin_nums, ref_y, val_y, in_bom_str, ds_str = build_lib_symbol_and_pins(ref, fp)
    lib_symbols_sch_list.append(sym_sch_sexpr)
    lib_symbols_ext_list.append(sym_ext_sexpr)

    sym_uuid = det_uuid(f"sym.{ref}")
    pin_entries = []
    for pnum in all_pin_nums:
        p_uuid = det_uuid(f"sym.{ref}.pin.{pnum}")
        pin_entries.append(f'\t\t(pin "{pnum}"\n\t\t\t(uuid "{p_uuid}")\n\t\t)')

    placed_symbols_list.append(
        f"""\t(symbol
\t\t(lib_id "{lib_name}")
\t\t(at {sx:.2f} {sy:.2f} 0)
\t\t(unit 1)
\t\t(exclude_from_sim no)
\t\t(in_bom {in_bom_str})
\t\t(on_board yes)
\t\t(dnp no)
\t\t(uuid "{sym_uuid}")
\t\t(property "Reference" "{ref}"
\t\t\t(at {sx:.2f} {sy - ref_y:.2f} 0)
\t\t\t(effects (font (size 1.27 1.27)))
\t\t)
\t\t(property "Value" "{fp.GetValue()}"
\t\t\t(at {sx:.2f} {sy - val_y:.2f} 0)
\t\t\t(effects (font (size 1.1 1.1)))
\t\t)
\t\t(property "Footprint" "{fp.GetFPIDAsString()}"
\t\t\t(at {sx:.2f} {sy:.2f} 0)
\t\t\t(effects (font (size 1.0 1.0)) (hide yes))
\t\t)
\t\t(property "Datasheet" "{ds_str}"
\t\t\t(at {sx:.2f} {sy:.2f} 0)
\t\t\t(effects (font (size 1.0 1.0)) (hide yes))
\t\t)
{chr(10).join(pin_entries)}
\t\t(instances
\t\t\t(project "co_detector_controller"
\t\t\t\t(path "/{root_sch_uuid}"
\t\t\t\t\t(reference "{ref}")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)"""
    )

    for pnum, lx, ly, side, net in vis_conns:
        px = round(sx + lx, 2)
        py = round(sy - ly, 2)
        if not net:
            nc_uuid = det_uuid(f"nc.{ref}.{pnum}")
            wires_and_labels_list.append(
                f"""\t(no_connect
\t\t(at {px:.2f} {py:.2f})
\t\t(uuid "{nc_uuid}")
\t)"""
            )
        else:
            stub_len = 5.08
            wx = round(px - stub_len if side == "L" else px + stub_len, 2)
            wy = py
            w_uuid = det_uuid(f"wire.{ref}.{pnum}")
            l_uuid = det_uuid(f"glabel.{ref}.{pnum}")
            lbl_ang = 180 if side == "L" else 0
            lbl_just = "right" if side == "L" else "left"
            wires_and_labels_list.append(
                f"""\t(wire
\t\t(pts (xy {px:.2f} {py:.2f}) (xy {wx:.2f} {wy:.2f}))
\t\t(stroke (width 0) (type solid))
\t\t(uuid "{w_uuid}")
\t)
\t(global_label "{net}"
\t\t(shape passive)
\t\t(at {wx:.2f} {wy:.2f} {lbl_ang})
\t\t(effects (font (size 1.0 1.0)) (justify {lbl_just}))
\t\t(uuid "{l_uuid}")
\t\t(property "Intersheetrefs" "${{INTERSHEET_REFS}}"
\t\t\t(at {wx:.2f} {wy:.2f} 0)
\t\t\t(effects (font (size 1.0 1.0)) (hide yes))
\t\t)
\t)"""
            )

with open(sym_lib_path, "w", encoding="utf-8") as f:
    f.write(
        f"""(kicad_symbol_lib
\t(version 20250114)
\t(generator "kicad_symbol_editor")
\t(generator_version "10.0")
{chr(10).join(lib_symbols_ext_list)}
)
"""
    )

block_boxes = [
    (15.24, 25.40, 260.00, 254.00, "BLOCK 1: 12V DC INPUT PROTECTION & 5V 3A SYNCHRONOUS BUCK REGULATOR (TPS54302)"),
    (15.24, 279.40, 360.00, 605.00, "BLOCK 2: SMART LI-ION CHARGER (TP4056), DW01A BMS, POWER-PATH SWITCH & ME6211 3.3V LDO"),
    (419.10, 25.40, 777.24, 254.00, "BLOCK 3: FIGARO TGS2610-C00 LPG GAS SENSOR AFE & 0.96-INCH I2C OLED DISPLAY (J4)"),
    (419.10, 279.40, 777.24, 605.00, "BLOCK 4: ESP32-C3-MINI-1 WIRELESS MCU, 85dB PIEZO ALARM (LS1), STATUS LEDS & USER CONTROLS"),
]
graphics_list = []
for idx, (x1, y1, x2, y2, title) in enumerate(block_boxes):
    r_uuid = det_uuid(f"box.{idx}")
    t_uuid = det_uuid(f"title.{idx}")
    graphics_list.append(
        f"""\t(rectangle
\t\t(start {x1:.2f} {y1:.2f})
\t\t(end {x2:.2f} {y2:.2f})
\t\t(stroke (width 0.3) (type dash))
\t\t(fill (type none))
\t\t(uuid "{r_uuid}")
\t)
\t(text "{title}"
\t\t(exclude_from_sim no)
\t\t(at {x1 + 5.08:.2f} {y1 + 7.62:.2f} 0)
\t\t(effects (font (size 2.54 2.54) bold) (justify left bottom))
\t\t(uuid "{t_uuid}")
\t)"""
    )

sch_content = f"""(kicad_sch
\t(version 20250114)
\t(generator "eeschema")
\t(generator_version "10.0")
\t(uuid "{root_sch_uuid}")
\t(paper "A1")
\t(title_block
\t\t(title "Smart LPG Gas Detector & Autonomous Li-ion Battery Backup Controller")
\t\t(date "2026-11-08")
\t\t(rev "4.0")
\t\t(company "Antigravity Hardware Engineering")
\t\t(comment 1 "MCU: ESP32-C3-MINI-1 | Sensor: Figaro TGS2610-C00 LPG Combustible Gas")
\t\t(comment 2 "Power: 12V Protected Input + TPS54302 Buck + TP4056 Auto-Cutoff Charger + DW01A BMS")
\t)
\t(lib_symbols
{chr(10).join(lib_symbols_sch_list)}
\t)
{chr(10).join(graphics_list)}
{chr(10).join(wires_and_labels_list)}
{chr(10).join(placed_symbols_list)}
\t(sheet_instances
\t\t(path "/"
\t\t\t(page "1")
\t\t)
\t)
\t(embedded_fonts no)
)
"""

with open(sch_path, "w", encoding="utf-8") as f:
    f.write(sch_content)

print("[SUCCESS] Generated Rev 4.0 schematic:", sch_path)
