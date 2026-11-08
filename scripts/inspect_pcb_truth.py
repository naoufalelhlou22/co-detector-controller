import re

with open('co_detector_controller.kicad_pcb', 'r', encoding='utf-8') as f:
    text = f.read()

# Find lines around layer "Edge.Cuts"
lines = text.splitlines()
print("--- EDGE CUTS LINES IN PCB ---")
for i, line in enumerate(lines):
    if '"Edge.Cuts"' in line and '(25 "Edge.Cuts"' not in line:
        context = lines[max(0, i-5):min(len(lines), i+6)]
        print(f"Around line {i}:")
        print("\n".join(context))
        print("="*40)
