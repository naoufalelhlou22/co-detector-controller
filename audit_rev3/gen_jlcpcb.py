"""Generate JLCPCB-format BOM and CPL from the KiCad netlist and the existing stage5 files."""
import csv, json, os, re

BASE = r"C:\Users\Mr_X\.gemini\antigravity\scratch\co_detector_controller"
AUDIT = os.path.join(BASE, "audit_rev3")
JLC = os.path.join(AUDIT, "jlcpcb")
os.makedirs(JLC, exist_ok=True)

# Read existing CPL (PCBWay format) for X/Y/Rotation
cpl_rows = []
cpl_path = os.path.join(BASE, "fab_pcbway", "co_detector_controller_cpl_top.csv")
if not os.path.exists(cpl_path):
    for f in ("stage5_CPL_top.csv", "co_detector_controller_cpl_top.csv"):
        for d in (os.path.join(BASE, "fab_pcbway"), BASE):
            p = os.path.join(d, f)
            if os.path.exists(p):
                cpl_path = p; break
with open(cpl_path, encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        cpl_rows.append(row)

# Build CPL output
jlc_cpl = [["Designator", "Mid X", "Mid Y", "Layer", "Rotation"]]
for row in cpl_rows:
    des = row.get("Designator") or row.get("Ref") or ""
    mx = row.get("Mid X") or row.get("PosX") or row.get("Center-X(mm)") or ""
    my = row.get("Mid Y") or row.get("PosY") or row.get("Center-Y(mm)") or ""
    rot = row.get("Rotation") or row.get("Rot") or "0"
    layer = row.get("Layer") or row.get("Side") or "top"
    if "bottom" in layer.lower() or "bot" in layer.lower():
        layer = "Bottom"
    else:
        layer = "Top"
    jlc_cpl.append([des.strip(), mx.strip(), my.strip(), layer, rot.strip()])

with open(os.path.join(JLC, "JLCPCB_CPL.csv"), "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(jlc_cpl)
print(f"CPL: {len(jlc_cpl)-1} entries written to JLCPCB_CPL.csv")

# LCSC part numbers (best-effort lookup — flagged as VERIFY BEFORE ORDER)
lcsc = {
    "ESP32-C3-MINI-1-N4": "C2838502",
    "LMR33620ADDAR": "C470357",
    "LMP91000SDE/NOPB": "C527044",
    "REF3325AIDBZR": "C193753",
    "SN74LVC1G08DBVR": "C7470",
    "TPS3823-33DBVR": "C256665",
    "AO3407A": "C181093",
    "IRLML6344TRPBF": "C151523",
    "2N7002,215": "C8545",
    "AO3400A": "C20917",
    "SMBJ15A": "C93013",
    "SMBJ15CA": "C88383",
    "CJ78L05": "C22080",
    "RC0603JR-070RL": "C21189",
    "CD0603-T03C / SP1003-01ETG": "C15975",
    "PS1240P02BT / CDM-12008": "C96465",
    "1729128": "C8465",
    "61300411121": "C2255",
    "B240A-13-F": "C35563",
    "BZT52C15-7-F": "C106240",
    "APT1608EC": "C72037",
    "APT1608SGC": "C72043",
    "APT1608QBC/D": "C72041",
    "APT1608SYCK": "C72044",
    "BLM18PG221SN1D": "C85804",
    "EEE-FK1V470P": "C134736",
    "GRM32ER71H106KA12L": "C59449",
    "GRM31CR71A226KE15L": "C159857",
    "GRM21BR71A106KA73L": "C85733",
    "GRM188R71C105KA12D": "C15849",
    "GRM188R71H104KA93D": "C14663",
    "GRM1885C1H220JA01D": "C1604",
    "RC0603FR-0710KL": "C25804",
    "RC0603FR-07100KL": "C25803",
    "RC0603FR-0743K2L": "C23176",
    "RC0603FR-074K7L": "C23162",
    "RC0603FR-072K2L": "C22972",
    "RC0603FR-071KL": "C22548",
    "RC0603FR-0715KL": "C22809",
    "RC0603FR-07100RL": "C22775",
    "RC0603FR-07270RL": "C22966",
    "RC0603FR-07330RL": "C23138",
    "RC0603FR-0747RL": "C23178",
    "ERJ-PA3F22R0V": "C276441",
    "XAL5030-682MEC": "MANUAL",
    "1N4148W-7-F": "C81598",
    "CDM-12008": "MANUAL",
    "PTS647SN50SMTR2LFS": "MANUAL",
    "MF-MSMF150/24X-2": "C268803",
}

# Read BOM
bom_path = os.path.join(BASE, "BOM.csv")
bom_rows = []
with open(bom_path, encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        bom_rows.append(row)

jlc_bom = [["Comment", "Designator", "Footprint", "LCSC Part Number", "Qty", "Assembly Status", "Notes"]]
for row in bom_rows:
    des = row.get("Designator", "")
    val = row.get("Value / Description", "")
    mpn = row.get("MPN (Assumed - Verify Before Order)", "")
    fp = row.get("Footprint", "")
    qty = row.get("Qty", "")
    status = row.get("Assembly Status", "")
    mount = row.get("Mount Type", "")
    notes = row.get("Assembly Notes", "")

    if status == "DNP" or "PCB" in mount or "Post-Assembly" in status:
        continue
    if "FID" in des or "TP" in des or "H1" in des or "H2" in des or "H3" in des or "H4" in des or "NT" in des:
        continue

    lc = lcsc.get(mpn, "VERIFY")
    jlc_bom.append([val, des, fp, lc, qty, status, notes])

with open(os.path.join(JLC, "JLCPCB_BOM.csv"), "w", newline="", encoding="utf-8") as f:
    csv.writer(f).writerows(jlc_bom)
print(f"BOM: {len(jlc_bom)-1} entries written to JLCPCB_BOM.csv")

# Copy to artifacts
import shutil
for fn in ("JLCPCB_BOM.csv", "JLCPCB_CPL.csv"):
    shutil.copy2(
        os.path.join(JLC, fn),
        os.path.join(r"C:\Users\Mr_X\.gemini\antigravity\brain\e65fff31-e4f5-4319-9c2a-44fb72c09462", fn)
    )
print("JLCPCB files copied to artifacts.")

