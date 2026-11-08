import re

with open("scripts/generate_schematic.py", "r") as f:
    text = f.read()

m = re.search(r"BLOCK_LAYOUT\s*=\s*\[(.*?)\]", text, re.DOTALL)
if m:
    items = re.findall(r'\("([^"]+)"', m.group(1))
    print(f"Total components in BLOCK_LAYOUT: {len(items)}")
    print("Components:", items)

# Check pins and labels
m2 = re.search(r"PIN_LABELS\s*=\s*\{(.*?)\n\}", text, re.DOTALL)
if m2:
    print("PIN_LABELS defined for ICs.")
