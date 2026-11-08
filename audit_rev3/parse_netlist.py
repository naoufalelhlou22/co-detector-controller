"""Parse the KiCad-exported Rev2 netlist (multi-line s-expression) and dump real connectivity."""
import re, json, os

BASE = os.path.dirname(os.path.abspath(__file__))
NET = os.path.join(BASE, "netlist", "rev2_netlist.net")
txt = open(NET, encoding="utf-8").read()

def tokenize(s):
    return re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', s)

def parse(tokens):
    stack = [[]]
    for t in tokens:
        if t == "(":
            stack.append([])
        elif t == ")":
            node = stack.pop()
            stack[-1].append(node)
        else:
            stack[-1].append(t.strip('"'))
    return stack[0][0]

tree = parse(tokenize(txt))

def find(node, key):
    return [c for c in node if isinstance(c, list) and c and c[0] == key]

def val(node, key, default=""):
    r = find(node, key)
    return r[0][1] if r and len(r[0]) > 1 else default

comps = {}
for comps_sec in find(tree, "components"):
    for c in find(comps_sec, "comp"):
        ref = val(c, "ref")
        fields = {}
        for fs in find(c, "fields"):
            for fl in find(fs, "field"):
                nm = val(fl, "name")
                fields[nm] = fl[-1] if isinstance(fl[-1], str) else ""
        comps[ref] = {"value": val(c, "value"), "footprint": val(c, "footprint"), "fields": fields, "pins": {}}

nets = {}
for nets_sec in find(tree, "nets"):
    for n in find(nets_sec, "net"):
        name = val(n, "name")
        nodes = []
        for nd in find(n, "node"):
            r, p, fn = val(nd, "ref"), val(nd, "pin"), val(nd, "pinfunction")
            nodes.append([r, p, fn])
            comps.setdefault(r, {"value": "?", "footprint": "", "fields": {}, "pins": {}})["pins"][p] = {"net": name, "func": fn}
        nets[name] = nodes

json.dump({"components": comps, "nets": nets}, open(os.path.join(BASE, "netlist", "connectivity.json"), "w"), indent=1)

def refkey(s):
    return (re.sub(r'\d', '', s), int(re.sub(r'\D', '', s) or 0))

with open(os.path.join(BASE, "netlist", "connectivity.txt"), "w", encoding="utf-8") as f:
    for ref in sorted(comps, key=refkey):
        c = comps[ref]
        pins = ", ".join(f"{p}{('('+v['func']+')') if v['func'] else ''}={v['net']}"
                         for p, v in sorted(c["pins"].items(), key=lambda kv: (len(kv[0]), kv[0])))
        f.write(f"{ref} [{c['value']}] {pins}\n")
    f.write("\n==== NETS ====\n")
    for n, nodes in sorted(nets.items()):
        f.write(f"{n}: " + " ".join(f"{r}.{p}" for r, p, _ in nodes) + "\n")
print(len(comps), "components,", len(nets), "nets")
