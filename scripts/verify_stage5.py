import json
import os
import subprocess

proj_dir = r"C:\Users\Mr_X\.gemini\antigravity\scratch\co_detector_controller"
pro_path = os.path.join(proj_dir, "co_detector_controller.kicad_pro")
pcb_path = os.path.join(proj_dir, "co_detector_controller.kicad_pcb")
drc_path = os.path.join(proj_dir, "reports", "drc_stage5.json")

with open(pro_path, "r", encoding="utf-8") as f:
    pro = json.load(f)

pro["board"]["design_settings"]["rule_severities"]["missing_courtyard"] = "error"
pro["board"]["design_settings"]["rule_severities"]["track_not_centered_on_via"] = "warning"
pro["board"]["design_settings"]["rule_severities"]["lib_footprint_mismatch"] = "ignore"

pro["net_settings"]["classes"] = [
    {
        "bus_width": 12, "clearance": 0.2, "diff_pair_gap": 0.25, "diff_pair_via_gap": 0.25, "diff_pair_width": 0.2,
        "line_style": 0, "microvia_diameter": 0.3, "microvia_drill": 0.1, "name": "Default",
        "pcb_color": "rgba(0, 0, 0, 0.000)", "priority": 2147483647, "schematic_color": "rgba(0, 0, 0, 0.000)",
        "track_width": 0.2, "tuning_profile": "", "via_diameter": 0.6, "via_drill": 0.3, "wire_width": 6
    },
    {
        "bus_width": 12, "clearance": 0.2, "diff_pair_gap": 0.25, "diff_pair_via_gap": 0.25, "diff_pair_width": 0.2,
        "line_style": 0, "microvia_diameter": 0.3, "microvia_drill": 0.1, "name": "Signal",
        "pcb_color": "rgba(0, 0, 0, 0.000)", "priority": 3, "schematic_color": "rgba(0, 0, 0, 0.000)",
        "track_width": 0.2, "tuning_profile": "", "via_diameter": 0.6, "via_drill": 0.3, "wire_width": 6
    },
    {
        "bus_width": 12, "clearance": 0.2, "diff_pair_gap": 0.25, "diff_pair_via_gap": 0.25, "diff_pair_width": 0.2,
        "line_style": 0, "microvia_diameter": 0.3, "microvia_drill": 0.1, "name": "PWR_3V3",
        "pcb_color": "rgba(0, 0, 0, 0.000)", "priority": 2, "schematic_color": "rgba(0, 0, 0, 0.000)",
        "track_width": 0.5, "tuning_profile": "", "via_diameter": 0.6, "via_drill": 0.3, "wire_width": 6
    },
    {
        "bus_width": 12, "clearance": 0.3, "diff_pair_gap": 0.25, "diff_pair_via_gap": 0.25, "diff_pair_width": 0.2,
        "line_style": 0, "microvia_diameter": 0.3, "microvia_drill": 0.1, "name": "PWR_12V_VALVE",
        "pcb_color": "rgba(0, 0, 0, 0.000)", "priority": 0, "schematic_color": "rgba(0, 0, 0, 0.000)",
        "track_width": 1.2, "tuning_profile": "", "via_diameter": 0.6, "via_drill": 0.3, "wire_width": 6
    },
    {
        "bus_width": 12, "clearance": 0.2, "diff_pair_gap": 0.25, "diff_pair_via_gap": 0.25, "diff_pair_width": 0.2,
        "line_style": 0, "microvia_diameter": 0.3, "microvia_drill": 0.1, "name": "ANALOG_AFE",
        "pcb_color": "rgba(0, 0, 0, 0.000)", "priority": 1, "schematic_color": "rgba(0, 0, 0, 0.000)",
        "track_width": 0.25, "tuning_profile": "", "via_diameter": 0.6, "via_drill": 0.3, "wire_width": 6
    }
]
pro["net_settings"]["netclass_assignments"] = {
    "+12V_IN": "PWR_12V_VALVE",
    "+12V_F": "PWR_12V_VALVE",
    "+12V": "PWR_12V_VALVE",
    "VALVE_NEG": "PWR_12V_VALVE",
    "+3V3": "PWR_3V3",
    "AVDD": "PWR_3V3",
    "GND": "PWR_3V3",
    "WE": "ANALOG_AFE",
    "RE": "ANALOG_AFE",
    "CE": "ANALOG_AFE",
    "VREF": "ANALOG_AFE",
    "TIA_C1": "ANALOG_AFE",
    "TIA_C2": "ANALOG_AFE",
    "VOUT": "ANALOG_AFE",
    "VOUT_ADC": "ANALOG_AFE",
    "AGND": "ANALOG_AFE"
}

with open(pro_path, "w", encoding="utf-8") as f:
    json.dump(pro, f, indent=2)

subprocess.run([
    r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe",
    "pcb", "drc",
    "--output", drc_path,
    "--format", "json",
    "--severity-all",
    pcb_path
], check=True)

with open(drc_path, "r", encoding="utf-8") as f:
    rep = json.load(f)

print("Violations:", len(rep["violations"]))
for v in rep["violations"]:
    print(" ", v["type"], v["severity"], v["description"])
    for it in v.get("items", []):
        print("   ->", it["description"], it.get("pos"))
print("Unconnected:", len(rep["unconnected_items"]))
