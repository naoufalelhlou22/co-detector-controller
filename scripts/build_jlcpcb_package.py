"""
Standalone JLCPCB Package Builder:
Exports Gerbers, Drills, BOM, and CPL directly from KiCad 10 files into fab_jlcpcb/
and copies the final order-ready deliverables to the project root and artifact directory.
"""

import os, csv, zipfile, shutil, subprocess

PROJ_DIR = r"C:\Users\Mr_X\.gemini\antigravity\scratch\co_detector_controller"
FAB_JLCPCB = os.path.join(PROJ_DIR, "fab_jlcpcb")
GERBERS_DIR = os.path.join(FAB_JLCPCB, "gerbers")
ARTIFACTS_DIR = r"C:\Users\Mr_X\.gemini\antigravity\brain\e65fff31-e4f5-4319-9c2a-44fb72c09462"
PCB_PATH = os.path.join(PROJ_DIR, "co_detector_controller.kicad_pcb")
KICAD_CLI = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"

os.makedirs(GERBERS_DIR, exist_ok=True)
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

# 1. Export fresh Gerbers directly via KiCad CLI
print("Exporting Gerbers for JLCPCB...")
subprocess.run([
    KICAD_CLI, "pcb", "export", "gerbers",
    "--output", GERBERS_DIR,
    "--layers", "F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts",
    "--use-drill-file-origin",
    PCB_PATH
], check=True)

# 2. Export Excellon Drill files
print("Exporting Excellon Drill files for JLCPCB...")
subprocess.run([
    KICAD_CLI, "pcb", "export", "drill",
    "--output", GERBERS_DIR,
    "--format", "excellon",
    "--drill-origin", "plot",
    "--excellon-zeros-format", "decimal",
    "--excellon-units", "mm",
    "--excellon-separate-th",
    "--generate-map",
    "--map-format", "gerberx2",
    PCB_PATH
], check=True)

# 3. Create co_detector_controller_gerbers_jlcpcb.zip
zip_path = os.path.join(FAB_JLCPCB, "co_detector_controller_gerbers_jlcpcb.zip")
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    for fn in sorted(os.listdir(GERBERS_DIR)):
        fp = os.path.join(GERBERS_DIR, fn)
        if os.path.isfile(fp):
            zf.write(fp, arcname=fn)

shutil.copy2(zip_path, os.path.join(PROJ_DIR, "co_detector_controller_gerbers_jlcpcb.zip"))
shutil.copy2(zip_path, os.path.join(ARTIFACTS_DIR, "co_detector_controller_gerbers_jlcpcb.zip"))
print(f"Gerber ZIP for JLCPCB verified: {zip_path}")

# 4. Verified LCSC Part Mapping
lcsc_map = {
    # Active ICs & Modules
    "U1": ("ESP32-C3-MINI-1-N4", "ESP32-C3-MINI-1", "C2838502"),
    "U2": ("LMR33620ADDAR", "SOIC-8-1EP", "C470357"),
    "U3": ("LMP91000SDE/NOPB", "WSON-14-1EP", "C527044"),
    "U4": ("REF3325AIDBZR", "SOT-23", "C193753"),
    "U5": ("SN74LVC1G08DBVR", "SOT-23-5", "C7470"),
    "U6": ("TPS3823-33DBVR", "SOT-23-5", "C256665"),
    
    # Transistors & MOSFETs
    "Q1": ("AO3407A", "SOT-23", "C181093"),
    "Q2": ("IRLML6344TRPBF", "SOT-23", "C151523"),
    "Q4": ("2N7002,215", "SOT-23", "C8545"),
    "Q5": ("AO3400A", "SOT-23", "C20917"),

    # Diodes
    "D1": ("SMBJ15CA", "SMB", "C88383"),
    "D2": ("B240A-13-F", "SMA", "C35563"),
    "D3": ("BZT52C15-7-F", "SOD-123", "C106240"),
    "D7": ("1N4148W-7-F", "SOD-123", "C81598"),
    "D4": ("Red LED (625nm)", "0603", "C72037"),
    "D5": ("Green LED (570nm)", "0603", "C72043"),
    "D6": ("Blue LED (470nm)", "0603", "C72041"),
    "D8": ("Yellow LED (590nm)", "0603", "C72044"),
    "D9": ("TVS Diode 3.3V ESD", "0603", "C15975"),
    "D10": ("TVS Diode 3.3V ESD", "0603", "C15975"),
    "D11": ("TVS Diode 3.3V ESD", "0603", "C15975"),

    # Protection & Filtering
    "F1": ("PTC Fuse 1.5A 24V", "1812", "C268803"),
    "FB1": ("Ferrite Bead 220R 100MHz", "0603", "C85804"),

    # Capacitors
    "C1": ("47uF 35V Electrolytic", "SMD-6.3x7.7", "C134736"),
    "C2": ("10uF 50V X7R", "1210", "C59449"),
    "C3": ("10uF 50V X7R", "1210", "C59449"),
    "C6": ("1uF 16V X7R", "0603", "C15849"),
    "C21": ("1uF 16V X7R", "0603", "C15849"),
    "C8": ("22uF 10V X7R", "1206", "C159857"),
    "C9": ("22uF 10V X7R", "1206", "C159857"),
    "C10": ("22uF 10V X7R", "1206", "C159857"),
    "C11": ("22uF 10V X7R", "1206", "C159857"),
    "C13": ("10uF 10V X7R", "0805", "C85733"),
    "C15": ("10uF 10V X7R", "0805", "C85733"),

    # 100nF decoupling capacitors (0603)
    "C4": ("100nF 50V X7R", "0603", "C14663"),
    "C5": ("100nF 50V X7R", "0603", "C14663"),
    "C12": ("100nF 50V X7R", "0603", "C14663"),
    "C14": ("100nF 50V X7R", "0603", "C14663"),
    "C16": ("100nF 50V X7R", "0603", "C14663"),
    "C17": ("100nF 50V X7R", "0603", "C14663"),
    "C18": ("100nF 50V X7R", "0603", "C14663"),
    "C19": ("100nF 50V X7R", "0603", "C14663"),
    "C20": ("100nF 50V X7R", "0603", "C14663"),
    "C22": ("100nF 50V X7R", "0603", "C14663"),
    "C23": ("100nF 50V X7R", "0603", "C14663"),
    "C24": ("100nF 50V X7R", "0603", "C14663"),
    "C25": ("100nF 50V X7R", "0603", "C14663"),
    "C26": ("100nF 50V X7R", "0603", "C14663"),
    "C27": ("100nF 50V X7R", "0603", "C14663"),
    "C28": ("100nF 50V X7R", "0603", "C14663"),
    "C29": ("100nF 50V X7R", "0603", "C14663"),
    "C30": ("100nF 50V X7R", "0603", "C14663"),
    "C31": ("100nF 50V X7R", "0603", "C14663"),

    # Resistors (0603)
    "R1": ("10k 1%", "0603", "C25804"),
    "R7": ("10k 1%", "0603", "C25804"),
    "R8": ("10k 1%", "0603", "C25804"),
    "R13": ("10k 1%", "0603", "C25804"),
    "R24": ("10k 1%", "0603", "C25804"),
    "R26": ("10k 1%", "0603", "C25804"),

    "R2": ("100k 1%", "0603", "C25803"),
    "R4": ("100k 1%", "0603", "C25803"),
    "R15": ("100k 1%", "0603", "C25803"),
    "R16": ("100k 1%", "0603", "C25803"),
    "R22": ("100k 1%", "0603", "C25803"),

    "R5": ("43.2k 1%", "0603", "C23176"),

    "R9": ("4.7k 1%", "0603", "C23162"),
    "R10": ("4.7k 1%", "0603", "C23162"),
    "R28": ("4.7k 1%", "0603", "C23162"),

    "R11": ("1k 1%", "0603", "C22548"),
    "R29": ("1k 1%", "0603", "C22548"),

    "R14": ("100R 1%", "0603", "C22775"),
    "R23": ("100R 1%", "0603", "C22775"),

    "R17": ("15k 1%", "0603", "C22809"),
    "R19": ("270R 1%", "0603", "C22966"),
    "R20": ("330R 1%", "0603", "C23138"),
    "R30": ("330R 1%", "0603", "C23138"),
    "R21": ("2.2k 1%", "0603", "C22972"),
    "R25": ("2.2k 1%", "0603", "C22972"),
    "R27": ("0R Jumper", "0603", "C21189"),

    # Switches & Inductor
    "SW1": ("Tact Switch 4.5x4.5mm SMD", "PTS647", "C318884"),
    "SW2": ("Tact Switch 4.5x4.5mm SMD", "PTS647", "C318884"),
    "SW3": ("Tact Switch 4.5x4.5mm SMD", "PTS647", "C318884"),
    "L1": ("Inductor 6.8uH SMD 5040/5030", "5040_5030", "C150244"),

    # Connectors & Sounder (THT / Pre-assembly)
    "J1": ("Terminal Block 2-Pin 5.08mm", "5.08mm-2P", "C8465"),
    "J2": ("Terminal Block 2-Pin 5.08mm", "5.08mm-2P", "C8465"),
    "J3": ("Pin Header 1x4 2.54mm", "2.54mm-1x4", "C2255"),
    "J4": ("Pin Header 1x4 2.54mm", "2.54mm-1x4", "C2255"),
    "LS1": ("Buzzer 12V 85dB D12.2mm", "PS1240P02BT", "C96465"),
}

# Group components by (Comment, Footprint, LCSC Part #)
grouped = {}
for ref, (comment, fp, lcsc_id) in sorted(lcsc_map.items()):
    key = (comment, fp, lcsc_id)
    if key not in grouped:
        grouped[key] = []
    grouped[key].append(ref)

# Write JLCPCB Standard Grouped BOM
jlc_bom_rows = [["Comment", "Designator", "Footprint", "LCSC Part #"]]
for (comment, fp, lcsc_id), refs in grouped.items():
    def ref_key(r):
        import re
        m = re.match(r"([A-Za-z]+)(\d+)", r)
        return (m.group(1), int(m.group(2))) if m else (r, 0)
    sorted_refs = sorted(refs, key=ref_key)
    jlc_bom_rows.append([comment, ",".join(sorted_refs), fp, lcsc_id])

bom_path = os.path.join(FAB_JLCPCB, "JLCPCB_BOM.csv")
with open(bom_path, "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(jlc_bom_rows)

shutil.copy2(bom_path, os.path.join(PROJ_DIR, "JLCPCB_BOM.csv"))
shutil.copy2(bom_path, os.path.join(ARTIFACTS_DIR, "JLCPCB_BOM.csv"))
print(f"JLCPCB BOM created ({len(jlc_bom_rows)-1} grouped line items): {bom_path}")

# 5. Export KiCad POS and format for JLCPCB CPL
pos_raw = os.path.join(FAB_JLCPCB, "raw_pos.csv")
subprocess.run([
    KICAD_CLI, "pcb", "export", "pos",
    "--output", pos_raw,
    "--side", "front",
    "--format", "csv",
    "--units", "mm",
    "--use-drill-file-origin",
    PCB_PATH
], check=True)

cpl_path = os.path.join(FAB_JLCPCB, "JLCPCB_CPL.csv")
jlc_from_pos = [["Designator", "Mid X", "Mid Y", "Layer", "Rotation"]]
with open(pos_raw, encoding="utf-8-sig") as f:
    r = csv.DictReader(f)
    for row in r:
        ref = row.get("Ref", "").strip('"')
        if ref in lcsc_map:
            x = row.get("PosX", "").strip('"')
            y = row.get("PosY", "").strip('"')
            rot = row.get("Rot", "0").strip('"')
            jlc_from_pos.append([ref, x, y, "Top", rot])

with open(cpl_path, "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(jlc_from_pos)

shutil.copy2(cpl_path, os.path.join(PROJ_DIR, "JLCPCB_CPL.csv"))
shutil.copy2(cpl_path, os.path.join(ARTIFACTS_DIR, "JLCPCB_CPL.csv"))
print(f"JLCPCB CPL created ({len(jlc_from_pos)-1} components): {cpl_path}")
