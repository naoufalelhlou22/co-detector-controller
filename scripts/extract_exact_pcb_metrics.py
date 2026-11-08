import sys
import pcbnew
import json

board = pcbnew.LoadBoard("co_detector_controller.kicad_pcb")

# Board bounding box
bbox = board.GetBoardEdgesBoundingBox()
print("=== BOARD EDGE BOUNDING BOX ===")
print(f"X: {bbox.GetX() / 1e6:.3f} mm to {(bbox.GetX() + bbox.GetWidth()) / 1e6:.3f} mm (Width: {bbox.GetWidth() / 1e6:.3f} mm)")
print(f"Y: {bbox.GetY() / 1e6:.3f} mm to {(bbox.GetY() + bbox.GetHeight()) / 1e6:.3f} mm (Height: {bbox.GetHeight() / 1e6:.3f} mm)")

# Check all footprints
data = []
for fp in board.GetFootprints():
    ref = fp.GetReference()
    val = fp.GetValue()
    pos = fp.GetPosition()
    rot = fp.GetOrientationDegrees()
    layer = fp.GetLayerName()
    
    # Pads bounding box
    fp_bbox = fp.GetBoundingBox(False, False) # without text
    
    x_mm = pos.x / 1e6
    y_mm = pos.y / 1e6
    
    models = []
    for m in fp.Models():
        models.append(m.m_Filename)
        
    data.append({
        "ref": ref,
        "val": val,
        "x": round(x_mm, 3),
        "y": round(y_mm, 3),
        "rot": round(rot, 1),
        "layer": layer,
        "bbox_w": round(fp_bbox.GetWidth() / 1e6, 3),
        "bbox_h": round(fp_bbox.GetHeight() / 1e6, 3),
        "models": models
    })

# Sort by reference
data.sort(key=lambda d: d["ref"])

with open("reports/pcb_exact_components.json", "w") as f:
    json.dump(data, f, indent=2)

print(f"\nExtracted {len(data)} footprints to reports/pcb_exact_components.json")

# Print key user interface and interface components
print("\n=== CRITICAL INTERFACE & UI COMPONENTS ===")
target_refs = [
    'H1', 'H2', 'H3', 'H4', # Mounting Holes
    'J1', 'J2',             # Screw Terminals
    'J3', 'J4',             # Pin Headers (J4 = OLED display header!)
    'SW1', 'SW2', 'SW3',    # Buttons (SW1 = Test, SW2 = Hush, SW3 = Reset)
    'D4', 'D5', 'D6', 'D8', # LEDs
    'LS1',                  # Buzzer / Speaker
    'S1', 'S2',             # Gas Sensors (S1 = Winsen ME3-CO, S2 = Figaro TGS2610)
    'U1'                    # ESP32-C3 MCU
]

for d in data:
    if d["ref"] in target_refs:
        print(f"Ref: {d['ref']:5} | Val: {d['val'][:15]:15} | Pos: ({d['x']:6.2f}, {d['y']:6.2f}) | Rot: {d['rot']:5.1f} | Layer: {d['layer']} | 3D: {d['models']}")
