"""Master Build & Verification Script for Smart Dual Gas Detector (Stage 5)

Executes the entire hardware generation, routing, DRC validation,
and manufacturing package export pipeline in the exact dependency order.
"""

import os
import subprocess
import sys

_kicad_py = r"C:\Program Files\KiCad\10.0\bin\python.exe"
_py = _kicad_py if os.path.isfile(_kicad_py) else sys.executable
proj_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
scripts_dir = os.path.join(proj_dir, "scripts")

PIPELINE = [
    ("1. 3D Mechanical Models", "build_3d_models.py"),
    ("2. Custom Footprints", "build_custom_fps.py"),
    ("3. 4-Layer Routed PCB", "build_stage4.py"),
    ("4. Schematic & Symbols", "generate_schematic.py"),
    ("5. DRC & Netclass Validation", "verify_stage5.py"),
    ("6. JLCPCB Package Builder", "build_jlcpcb_package.py"),
    ("7. JLCPCB BOM & CPL Parity", "update_jlcpcb_bom_cpl.py"),
    ("8. Manufacturing Stats & Renders", "generate_stage5_manufacturing_and_stats.py"),
    ("9. PCBA Financial Simulation", "calculate_pcba_costs.py"),
]


def run():
    print("=" * 70)
    print("Smart Dual Gas Detector (CO + LPG) - Full Hardware Build Pipeline")
    print("=" * 70)

    for step_num, (desc, script_name) in enumerate(PIPELINE, 1):
        script_path = os.path.join(scripts_dir, script_name)
        print(f"\n[{step_num}/{len(PIPELINE)}] Running {desc} ({script_name})...")
        res = subprocess.run([_py, script_path], cwd=proj_dir)
        if res.returncode != 0:
            print(f"\n[FAILED] Step {step_num} ({script_name}) failed with exit code {res.returncode}")
            sys.exit(res.returncode)

    print("\n" + "=" * 70)
    print("[SUCCESS] All pipeline stages completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    run()
