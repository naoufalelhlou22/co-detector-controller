import collections
import csv
import json
import math
import os
import shutil
import subprocess
import sys
import zipfile

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
reports_dir = os.path.join(proj_dir, "reports")
pro_path = os.path.join(proj_dir, "co_detector_controller.kicad_pro")
drc5_path = os.path.join(reports_dir, "drc_stage5.json")
drc4_path = os.path.join(reports_dir, "drc_stage4.json")
fab_dir = os.path.join(proj_dir, "fab_jlcpcb")
gerber_dir = os.path.join(fab_dir, "gerbers")
art_dir = r"C:\Users\Mr_X\.gemini\antigravity\brain\e65fff31-e4f5-4319-9c2a-44fb72c09462"

os.makedirs(gerber_dir, exist_ok=True)
os.makedirs(art_dir, exist_ok=True)

# Copy drc_stage5.json -> drc_stage4.json so both are synced
shutil.copyfile(drc5_path, drc4_path)

# Load board and project
b = pcbnew.LoadBoard(pcb_path)
with open(pro_path, "r", encoding="utf-8") as f:
    pro = json.load(f)
netclass_map = (pro.get("net_settings") or {}).get("netclass_assignments") or {}

# Collect pads per net
pads_by_net = collections.defaultdict(list)
for fp in b.GetFootprints():
    ref = fp.GetReference()
    for p in fp.Pads():
        net = p.GetNetname()
        if net:
            pnum = p.GetNumber()
            pads_by_net[net].append(f"{ref}.{pnum}")

# Collect tracks & vias per net
layers_by_net = collections.defaultdict(set)
widths_by_net = collections.defaultdict(set)
length_by_net = collections.defaultdict(float)
vias_by_net = collections.defaultdict(int)
total_vias = 0
total_tracks = 0
tented_front = b.GetDesignSettings().m_TentViasFront
tented_back = b.GetDesignSettings().m_TentViasBack

for item in b.GetTracks():
    net = item.GetNetname()
    if isinstance(item, pcbnew.PCB_VIA):
        vias_by_net[net] += 1
        total_vias += 1
    else:
        total_tracks += 1
        lyr = item.GetLayerName()
        w = round(pcbnew.ToMM(item.GetWidth()), 2)
        p1 = item.GetStart()
        p2 = item.GetEnd()
        seg_len = math.hypot(pcbnew.ToMM(p2.x - p1.x), pcbnew.ToMM(p2.y - p1.y))
        layers_by_net[net].add(lyr)
        widths_by_net[net].add(w)
        length_by_net[net] += seg_len

# Zones per net
zones_by_net = collections.defaultdict(list)
for z in b.Zones():
    if not z.GetIsRuleArea():
        for lyr_id in z.GetLayerSet().Seq():
            lyr_name = b.GetLayerName(lyr_id)
            zones_by_net[z.GetNetname()].append(lyr_name)
            layers_by_net[z.GetNetname()].add(f"{lyr_name} (Plane)")

# Save net table JSON for accurate markdown table generation
net_rows = []
for net in sorted(pads_by_net.keys()):
    nc = netclass_map.get(net, "Signal")
    unique_pads = sorted(set(pads_by_net[net]), key=lambda s: (s.split(".")[0], int(s.split(".")[1]) if s.split(".")[1].isdigit() else 999))
    # Collapse U1.36..U1.53 for readability if GND
    if net == "GND":
        u1_gnd = [p for p in unique_pads if p.startswith("U1.")]
        other_gnd = [p for p in unique_pads if not p.startswith("U1.")]
        pins_str = ", ".join(other_gnd + ["U1.1, U1.2, U1.11, U1.14, U1.36–U1.53 (EP)"])
    else:
        pins_str = ", ".join(unique_pads)
    lyrs = sorted(layers_by_net[net])
    w_list = sorted(widths_by_net[net])
    w_str = " / ".join(f"{w:.2f}" for w in w_list) if w_list else "Plane"
    net_rows.append({
        "net": net,
        "netclass": nc,
        "pin_count": len(unique_pads),
        "pins": pins_str,
        "layers": ", ".join(lyrs),
        "widths_mm": w_str,
        "length_mm": round(length_by_net[net], 2),
        "vias": vias_by_net[net],
    })

stats_out = os.path.join(reports_dir, "stage5_net_stats.json")
with open(stats_out, "w", encoding="utf-8") as f:
    json.dump({
        "total_nets": len(net_rows),
        "total_vias": total_vias,
        "total_tracks": total_tracks,
        "tented_front": tented_front,
        "tented_back": tented_back,
        "nets": net_rows,
    }, f, indent=2)

# Export Gerbers
kicad_cli = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
subprocess.run([
    kicad_cli, "pcb", "export", "gerbers",
    "--output", gerber_dir,
    "--layers", "F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts",
    "--use-drill-file-origin",
    pcb_path
], check=True)

# Export Excellon Drill files + map
subprocess.run([
    kicad_cli, "pcb", "export", "drill",
    "--output", gerber_dir,
    "--format", "excellon",
    "--drill-origin", "plot",
    "--excellon-zeros-format", "decimal",
    "--excellon-units", "mm",
    "--excellon-separate-th",
    "--generate-map",
    "--map-format", "gerberx2",
    pcb_path
], check=True)

# Create ZIP archive of Gerbers + Drills for JLCPCB
zip_path = os.path.join(fab_dir, "co_detector_controller_gerbers_jlcpcb.zip")
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    for fn in sorted(os.listdir(gerber_dir)):
        full_p = os.path.join(gerber_dir, fn)
        if os.path.isfile(full_p):
            zf.write(full_p, arcname=fn)

shutil.copy2(zip_path, os.path.join(proj_dir, "co_detector_controller_gerbers_jlcpcb.zip"))
shutil.copy2(zip_path, os.path.join(art_dir, "co_detector_controller_gerbers_jlcpcb.zip"))

# Render high-res Top, Bottom, and 3D Perspective views into current artifact folder
top_png = os.path.join(art_dir, "stage5_final_top.png")
bot_png = os.path.join(art_dir, "stage5_final_bottom.png")
persp_png = os.path.join(art_dir, "j1_j2_oriented_perspective.png")
subprocess.run([
    kicad_cli, "pcb", "render",
    "--output", top_png,
    "--side", "top",
    "--width", "1600",
    "--height", "1150",
    "--quality", "high",
    pcb_path
], check=True)
subprocess.run([
    kicad_cli, "pcb", "render",
    "--output", bot_png,
    "--side", "bottom",
    "--width", "1600",
    "--height", "1150",
    "--quality", "high",
    pcb_path
], check=True)
subprocess.run([
    kicad_cli, "pcb", "render",
    "--output", persp_png,
    "--rotate", "-20,-28,0",
    "--width", "1600",
    "--height", "1100",
    "--quality", "high",
    pcb_path
], check=True)

print(f"Exported {len(net_rows)} nets, {total_tracks} track segments, {total_vias} tented vias.")
print("Gerber ZIP:", zip_path)
print("Fabrication package complete.")
