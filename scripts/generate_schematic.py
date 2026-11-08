import collections
import os
import subprocess
import sys
import uuid

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

# Pin function names for multi-pin ICs and specialized parts
PIN_LABELS = {
    "U1": {
        "1": "GND",
        "3": "3V3",
        "4": "NC_4",
        "5": "IO2_LPG_ADC",
        "6": "IO3_BUZZER",
        "7": "NC_7",
        "8": "EN_NRST",
        "9": "NC_9",
        "10": "NC_10",
        "12": "IO0_VOUT_ADC",
        "13": "IO1_VALVE_SNS",
        "15": "NC_15",
        "16": "IO10_TEST_N",
        "17": "NC_17",
        "18": "IO4_SDA",
        "19": "IO5_SCL",
        "20": "IO6_VALVE_EN",
        "21": "IO7_WDI",
        "22": "IO8_HUSH_N",
        "23": "IO9_BOOT_N",
        "24": "NC_24",
        "25": "NC_25",
        "26": "IO18_LED_RED",
        "27": "IO19_LED_BLU",
        "28": "NC_28",
        "29": "NC_29",
        "30": "RXD0",
        "31": "TXD0",
        "32": "NC_32",
        "33": "NC_33",
        "34": "NC_34",
        "35": "NC_35",
    },
    "U2": {
        "1": "PGND",
        "2": "VIN",
        "3": "EN",
        "4": "PG",
        "5": "FB",
        "6": "VCC",
        "7": "BOOT",
        "8": "SW",
        "9": "EP",
    },
    "U3": {
        "1": "DGND",
        "2": "MENB",
        "3": "SCL",
        "4": "SDA",
        "5": "NC",
        "6": "VDD",
        "7": "AGND",
        "8": "VOUT",
        "9": "C2",
        "10": "C1",
        "11": "VREF",
        "12": "WE",
        "13": "RE",
        "14": "CE",
        "15": "EP",
    },
    "U4": {
        "1": "IN",
        "2": "OUT",
        "3": "GND",
    },
    "U5": {
        "1": "A",
        "2": "B",
        "3": "GND",
        "4": "Y",
        "5": "VCC",
    },
    "U6": {
        "1": "~{RESET}",
        "2": "GND",
        "3": "~{MR}",
        "4": "WDI",
        "5": "VDD",
    },
    "S1": {
        "1": "WE",
        "2": "RE",
        "3": "CE",
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
    "J2": {
        "1": "EXT_ALM+",
        "2": "EXT_ALM-",
    },
    "J3": {
        "1": "3V3",
        "2": "TX",
        "3": "RX",
        "4": "GND",
    },
    "J4": {
        "1": "GND",
        "2": "3V3",
        "3": "SCL",
        "4": "SDA",
    },
    "Q1": {"1": "G", "2": "S", "3": "D"},
    "Q2": {"1": "G", "2": "S", "3": "D"},
    "Q3": {"1": "D", "2": "S", "3": "G"},
    "Q4": {"1": "G", "2": "S", "3": "D"},
    "Q5": {"1": "G", "2": "S", "3": "D"},
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
            vis_conns.append((pnum, lx, ly, side, pad_nets[pnum]))
        ref_y = 5.08
        val_y = -5.08

    else:
        lbls = PIN_LABELS.get(ref, {})
        if ref == "U1":
            left_pins = ["3", "8", "12", "13", "18", "19", "23", "26", "30", "31", "1"]
            right_pins = ["20", "21", "16", "22", "27", "6", "5", "4", "7", "9", "10", "15", "17", "24", "25", "28", "29", "32", "33", "34", "35"]
            stacked_on_1 = [p for p in all_pin_nums if p not in left_pins and p not in right_pins]
        elif ref == "U2":
            left_pins = ["2", "3", "6", "1"]
            right_pins = ["7", "8", "5", "4"]
            stacked_on_1 = ["9"]
        elif ref == "U3":
            left_pins = ["14", "13", "12", "11", "10", "9", "6", "1"]
            right_pins = ["8", "4", "3", "2", "7", "5"]
            stacked_on_1 = ["15"]
        else:
            half = (len(all_pin_nums) + 1) // 2
            left_pins = all_pin_nums[:half]
            right_pins = all_pin_nums[half:]
            stacked_on_1 = []

        max_rows = max(len(left_pins), len(right_pins))
        half_h = max((max_rows * 2.54) / 2.0 + 1.27, 5.08)
        half_h = round(half_h / 1.27) * 1.27
        box_w = 10.16 if ref in ("U1", "U2", "U3") else 6.35
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
            vis_conns.append((pnum, -pin_x, ly, "L", pad_nets[pnum]))
            if pnum == "1":
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
            vis_conns.append((pnum, pin_x, ly, "R", pad_nets[pnum]))

        for pnum in stacked_on_1:
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


BLOCK_LAYOUT = [
    # --- BLOCK 1 (Top-Left): 12V Input Protection & 3.3V Buck Regulator ---
    ("J1", 50.80, 45.72),
    ("F1", 50.80, 63.50),
    ("D1", 50.80, 81.28),
    ("Q1", 50.80, 101.60),
    ("D3", 50.80, 121.92),
    ("R1", 50.80, 139.70),
    ("C1", 50.80, 157.48),
    ("C2", 50.80, 175.26),
    ("C3", 50.80, 193.04),
    ("C4", 50.80, 210.82),
    ("U2", 139.70, 68.58),
    ("R2", 139.70, 104.14),
    ("R3", 139.70, 121.92),
    ("C5", 139.70, 139.70),
    ("C6", 139.70, 157.48),
    ("D7", 139.70, 175.26),
    ("L1", 139.70, 193.04),
    ("R4", 139.70, 210.82),
    ("R5", 139.70, 228.60),
    ("C7", 228.60, 45.72),
    ("C8", 228.60, 63.50),
    ("C9", 228.60, 81.28),
    ("C10", 228.60, 99.06),
    ("C11", 228.60, 116.84),
    ("C12", 228.60, 134.62),
    ("TP1", 228.60, 154.94),
    ("TP2", 228.60, 170.18),
    ("TP11", 228.60, 185.42),
    ("TP12", 228.60, 200.66),

    # --- BLOCK 2 (Bottom-Left): Watchdog, Safety Interlock & 12V Solenoid Valve Driver ---
    ("U6", 50.80, 312.42),
    ("C23", 50.80, 342.90),
    ("R18", 50.80, 360.68),
    ("U5", 50.80, 386.08),
    ("C22", 50.80, 416.56),
    ("R13", 50.80, 434.34),
    ("R14", 50.80, 452.12),
    ("R15", 50.80, 469.90),
    ("Q2", 139.70, 312.42),
    ("D2", 139.70, 335.28),
    ("C24", 139.70, 353.06),
    ("J2", 139.70, 370.84),
    ("R16", 139.70, 391.16),
    ("R17", 139.70, 408.94),
    ("C25", 139.70, 426.72),
    ("TP4", 139.70, 447.04),
    ("TP6", 139.70, 462.28),
    ("TP9", 139.70, 477.52),
    ("SW3", 139.70, 495.30),
    ("C31", 139.70, 513.08),
    ("D11", 139.70, 530.86),

    # --- BLOCK 3 (Top-Right): Winsen ME3-CO Sensor, LMP91000 AFE & Figaro TGS2610-C00 LPG Sensor ---
    ("S1", 469.90, 55.88),
    ("Q3", 469.90, 83.82),
    ("R12", 469.90, 106.68),
    ("C21", 469.90, 124.46),
    ("U3", 469.90, 165.10),
    ("R11", 469.90, 210.82),
    ("C18", 469.90, 228.60),
    ("FB1", 571.50, 45.72),
    ("C13", 571.50, 63.50),
    ("C14", 571.50, 81.28),
    ("U4", 571.50, 104.14),
    ("C19", 571.50, 127.00),
    ("C20", 571.50, 144.78),
    ("NT1", 571.50, 165.10),
    ("TP3", 571.50, 185.42),
    ("TP5", 571.50, 200.66),
    ("TP7", 571.50, 215.90),
    ("TP8", 571.50, 231.14),
    ("S2", 685.80, 55.88),
    ("R27", 685.80, 86.36),
    ("C29", 685.80, 104.14),
    ("R28", 685.80, 121.92),
    ("R29", 685.80, 139.70),
    ("C28", 685.80, 157.48),
    ("J4", 685.80, 185.42),

    # --- BLOCK 4 (Bottom-Right): ESP32-C3-MINI-1 MCU, Buzzer, LEDs, Buttons & UART ---
    ("U1", 469.90, 355.60),
    ("C15", 469.90, 439.42),
    ("C16", 469.90, 457.20),
    ("R6", 469.90, 474.98),
    ("C17", 469.90, 492.76),
    ("J3", 469.90, 518.16),
    ("R7", 584.20, 299.72),
    ("R8", 584.20, 317.50),
    ("R9", 584.20, 335.28),
    ("R10", 584.20, 353.06),
    ("SW1", 584.20, 370.84),
    ("SW2", 584.20, 388.62),
    ("C26", 584.20, 406.40),
    ("C27", 584.20, 424.18),
    ("D4", 584.20, 441.96),
    ("R19", 584.20, 459.74),
    ("D5", 584.20, 477.52),
    ("R20", 584.20, 495.30),
    ("D6", 584.20, 513.08),
    ("R25", 584.20, 530.86),
    ("D8", 584.20, 548.64),
    ("Q4", 685.80, 304.80),
    ("R21", 685.80, 327.66),
    ("R22", 685.80, 345.44),
    ("R26", 685.80, 363.22),
    ("Q5", 685.80, 386.08),
    ("R23", 685.80, 408.94),
    ("R24", 685.80, 426.72),
    ("LS1", 685.80, 447.04),
    ("TP10", 685.80, 467.36),
    ("R30", 685.80, 485.14),
    ("H1", 685.80, 502.92),
    ("H2", 685.80, 518.16),
    ("H3", 685.80, 533.40),
    ("H4", 685.80, 548.64),
    ("C30", 736.60, 467.36),
    ("D9", 736.60, 431.80),
    ("D10", 736.60, 449.58),
    ("FID1", 736.60, 485.14),
    ("FID2", 736.60, 500.38),
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
    (15.24, 25.40, 274.32, 248.92, "BLOCK 1: 12V INPUT PROTECTION & 3.3V 2A SYNCHRONOUS BUCK CONVERTER (LMR33620ADDAR)"),
    (15.24, 279.40, 274.32, 502.92, "BLOCK 2: HARDWARE WATCHDOG (TPS3823-33), SAFETY INTERLOCK (74LVC1G08) & 12V EXTERNAL ALARM OUTPUT (J2)"),
    (419.10, 25.40, 777.24, 254.00, "BLOCK 3: DUAL GAS SENSORS — CO (ME3-CO + LMP91000 AFE) & LPG (FIGARO TGS2610-C00) + I2C OLED (J4)"),
    (419.10, 274.32, 777.24, 553.72, "BLOCK 4: ESP32-C3-MINI-1 WIRELESS MCU, DYNAMIC AUDIO SPEAKER (CDM-12008), LEDS, BUTTONS & UART"),
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
\t\t(title "CO Detector & Automatic 12V Gas Shut-Off Valve Controller")
\t\t(date "2026-11-07")
\t\t(rev "1.0")
\t\t(company "Antigravity Hardware Engineering")
\t\t(comment 1 "MCU: ESP32-C3-MINI-1 | AFE: LMP91000SDE + REF3325 + Winsen ME3-CO")
\t\t(comment 2 "Power: 12V Protected Input + LMR33620ADDAR 3.3V Buck | Safety: TPS3823-33 + 74LVC1G08 + IRLML6344")
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

print("Generated schematic:", sch_path)
