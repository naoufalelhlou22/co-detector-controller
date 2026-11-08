import json

with open("reports/pcb_exact_components.json", "r") as f:
    comps = json.load(f)

targets = ["H1", "H2", "H3", "H4", "J1", "J2", "J4", "SW1", "SW2", "SW3", "D4", "D5", "D6", "D8", "S1", "S2", "LS1", "U1"]
print(f"{'Ref':6} | {'KiCad (X,Y)':18} | {'CAD (X,Y)':18} | {'Rot':6} | {'BBox WxH':12} | {'Value / Model'}")
print("-" * 90)
for c in comps:
    ref = c["ref"]
    if ref in targets:
        kx, ky = c["x"], c["y"]
        cad_x = round(kx, 2)
        cad_y = round(50.0 - ky, 2)
        rot = c.get("rot", 0.0)
        bw = c.get("bbox_w", 0.0)
        bh = c.get("bbox_h", 0.0)
        val = c.get("val", "")
        models = c.get("models", [])
        m_name = models[0].split("/")[-1] if models else ""
        print(f"{ref:6} | ({kx:6.2f}, {ky:6.2f})    | ({cad_x:6.2f}, {cad_y:6.2f})    | {rot:5.1f} | {bw:5.2f}x{bh:5.2f} | {val} [{m_name}]")
