import csv

# BOM unit costs based on LCSC catalog prices (1-10 pcs / 100 pcs tiers in USD)
# Structure: ref_group: (Comment, Qty, LCSC_ID, Part_Type, Unit_Cost_Prototype, Unit_Cost_100pcs)
bom_pricing = [
    # ICs
    ("U1", "ESP32-C3-MINI-1-N4 (Espressif)", 1, "C2838502", "Extended", 1.95, 1.65),
    ("U2", "LMR33620ADDAR Buck 2A (TI)", 1, "C470357", "Extended", 1.55, 1.25),
    ("U3", "LMP91000SDE AFE (TI)", 1, "C527044", "Extended", 2.20, 1.85),
    ("U4", "REF3325AIDBZR 2.5V (TI)", 1, "C193753", "Extended", 0.95, 0.75),
    ("U5", "SN74LVC1G08 Logic Gate (TI)", 1, "C7470", "Basic", 0.08, 0.05),
    ("U6", "TPS3823-33DBVR WDT/Supervisor (TI)", 1, "C256665", "Extended", 0.85, 0.68),
    
    # MOSFETs
    ("Q1", "AO3407A P-MOS -30V", 1, "C181093", "Basic", 0.05, 0.035),
    ("Q2", "IRLML6344TRPBF N-MOS 30V 5A", 1, "C151523", "Extended", 0.12, 0.08),
    ("Q4", "2N7002 N-MOS 60V", 1, "C8545", "Basic", 0.03, 0.018),
    ("Q5", "AO3400A N-MOS 30V 5.7A", 1, "C20917", "Basic", 0.05, 0.032),

    # Diodes & Protection
    ("D1", "SMBJ15CA Bidirectional TVS 600W", 1, "C88383", "Extended", 0.18, 0.12),
    ("D2", "B240A-13-F Schottky 40V 2A", 1, "C35563", "Basic", 0.06, 0.04),
    ("D3", "BZT52C15-7-F Zener 15V SOD-123", 1, "C106240", "Basic", 0.025, 0.015),
    ("D7", "1N4148W-7-F Fast Diode SOD-123", 1, "C81598", "Basic", 0.015, 0.008),
    ("D4", "Red LED 0603", 1, "C72037", "Basic", 0.018, 0.010),
    ("D5", "Green LED 0603", 1, "C72043", "Basic", 0.018, 0.010),
    ("D6", "Blue LED 0603", 1, "C72041", "Basic", 0.022, 0.012),
    ("D8", "Yellow LED 0603", 1, "C72044", "Basic", 0.018, 0.010),
    ("D9,D10,D11", "TVS Diode 3.3V 0603 (ESD)", 3, "C15975", "Basic", 0.035, 0.022),
    ("F1", "PTC Resettable Fuse 1.5A 1812", 1, "C268803", "Extended", 0.14, 0.095),
    ("FB1", "Ferrite Bead 220R 100MHz 0603", 1, "C85804", "Basic", 0.012, 0.007),

    # Capacitors
    ("C1", "47uF 35V SMD Electrolytic 6.3x7.7", 1, "C134736", "Extended", 0.12, 0.085),
    ("C2,C3", "10uF 50V X7R 1210", 2, "C59449", "Extended", 0.15, 0.11),
    ("C6,C21", "1uF 16V X7R 0603", 2, "C15849", "Basic", 0.008, 0.005),
    ("C8,C9,C10,C11", "22uF 10V X7R 1206", 4, "C159857", "Extended", 0.045, 0.032),
    ("C13,C15", "10uF 10V X7R 0805", 2, "C85733", "Basic", 0.018, 0.012),
    ("C4,C5,C12,C14,C16..C31", "100nF 50V X7R 0603", 19, "C14663", "Basic", 0.004, 0.0025),

    # Resistors (all 0603 Basic)
    ("R1,R7,R8,R13,R24,R26", "10k 1% 0603", 6, "C25804", "Basic", 0.003, 0.0018),
    ("R2,R4,R15,R16,R22", "100k 1% 0603", 5, "C25803", "Basic", 0.003, 0.0018),
    ("R5", "43.2k 1% 0603", 1, "C23176", "Basic", 0.004, 0.0022),
    ("R9,R10,R28", "4.7k 1% 0603", 3, "C23162", "Basic", 0.003, 0.0018),
    ("R11,R29", "1k 1% 0603", 2, "C22548", "Basic", 0.003, 0.0018),
    ("R14,R23", "100R 1% 0603", 2, "C22775", "Basic", 0.003, 0.0018),
    ("R17", "15k 1% 0603", 1, "C22809", "Basic", 0.003, 0.0018),
    ("R19", "270R 1% 0603", 1, "C22966", "Basic", 0.003, 0.0018),
    ("R20,R30", "330R 1% 0603", 2, "C23138", "Basic", 0.003, 0.0018),
    ("R21,R25", "2.2k 1% 0603", 2, "C22972", "Basic", 0.003, 0.0018),
    ("R27", "0R Jumper 0603", 1, "C21189", "Basic", 0.002, 0.0012),

    # Inductor & Electromechanical
    ("L1", "6.8uH 2.5A Power Inductor 5040/5030", 1, "C150244", "Extended", 0.22, 0.16),
    ("SW1,SW2,SW3", "Tact Switch 4.5x4.5mm SMD", 3, "C318884", "Extended", 0.06, 0.04),
    
    # Connectors & Sounder (THT assembled or hand solder)
    ("J1,J2", "Screw Terminal 5.08mm 2-Pin", 2, "C8465", "Extended", 0.18, 0.12),
    ("J3,J4", "Pin Header 1x4 2.54mm", 2, "C2255", "Basic", 0.04, 0.025),
    ("LS1", "TDK Buzzer PS1240P02BT (12V)", 1, "C96465", "Extended", 0.38, 0.28),
]

# Calculate total components and BOM cost per board
total_pcs = sum(item[2] for item in bom_pricing)
bom_cost_proto = sum(item[2] * item[5] for item in bom_pricing)
bom_cost_100 = sum(item[2] * item[6] for item in bom_pricing)

extended_parts = [item for item in bom_pricing if item[4] == "Extended"]
basic_parts = [item for item in bom_pricing if item[4] == "Basic"]

print(f"Total Assembled Components per Board: {total_pcs} pcs")
print(f"Unique Part Types: {len(bom_pricing)}")
print(f"  - Basic Parts: {len(basic_parts)} (Feeder Fee: $0.00)")
print(f"  - Extended Parts: {len(extended_parts)} (Feeder Fee: $3.00 each = ${len(extended_parts)*3.00:.2f})")
print(f"BOM Cost per Board (Prototype): ${bom_cost_proto:.2f}")
print(f"BOM Cost per Board (100 pcs):   ${bom_cost_100:.2f}")

# Gas sensors (procured separately / inserted post-reflow)
sensor_co_me3 = 14.50   # Winsen ME3-CO
sensor_lpg_figaro = 9.80 # Figaro TGS2610-C00
sensors_total = sensor_co_me3 + sensor_lpg_figaro
print(f"Sensors Cost per Unit (Winsen ME3-CO + Figaro TGS2610): ${sensors_total:.2f}")

# Simulation of JLCPCB PCBA order for 5, 10, 30, 50, 100 boards
print("\n" + "="*80)
print("JLCPCB PCBA COST SIMULATION MATRIX (ENIG 4-Layer, Top-Side SMT)")
print("="*80)

scenarios = [
    {"qty": 5, "pcb_fab": 22.00, "pcb_enig": 18.00, "setup": 8.00, "stencil": 1.50, "ext_feeder_rate": 3.00},
    {"qty": 10, "pcb_fab": 28.00, "pcb_enig": 22.00, "setup": 8.00, "stencil": 1.50, "ext_feeder_rate": 3.00},
    {"qty": 30, "pcb_fab": 42.00, "pcb_enig": 28.00, "setup": 8.00, "stencil": 1.50, "ext_feeder_rate": 3.00},
    {"qty": 50, "pcb_fab": 58.00, "pcb_enig": 35.00, "setup": 8.00, "stencil": 1.50, "ext_feeder_rate": 3.00},
    {"qty": 100, "pcb_fab": 85.00, "pcb_enig": 48.00, "setup": 8.00, "stencil": 1.50, "ext_feeder_rate": 3.00},
]

for sc in scenarios:
    q = sc["qty"]
    # PCB bare boards (4-layer 70x50mm ENIG)
    pcb_total = sc["pcb_fab"] + sc["pcb_enig"]
    
    # SMT Engineering & Setup
    smt_setup = sc["setup"]
    stencil = sc["stencil"]
    # Extended feeder loading fee: $3 per extended part (one-off per batch)
    feeder_fees = len(extended_parts) * sc["ext_feeder_rate"]
    
    # Placement fee: ~$0.004 per SMD part
    placement_fees = q * total_pcs * 0.0035
    
    # SMT labor total
    smt_labor_total = smt_setup + stencil + feeder_fees + placement_fees
    
    # Components cost (interpolating between proto and 100pcs tier)
    tier_bom_unit = bom_cost_proto if q <= 10 else (bom_cost_proto * 0.9 if q <= 50 else bom_cost_100)
    components_total = q * tier_bom_unit
    
    # Total PCBA (without gas sensors)
    pcba_subtotal = pcb_total + smt_labor_total + components_total
    unit_pcba_cost = pcba_subtotal / q
    
    # Total with Gas Sensors
    total_with_sensors = pcba_subtotal + (q * sensors_total)
    unit_complete_cost = total_with_sensors / q
    
    print(f"\n--- BATCH QUANTITY: {q} BOARDS ---")
    print(f"  1. Bare PCB Fabrication (4-Layer 70x50mm ENIG): ${pcb_total:.2f} (${pcb_total/q:.2f}/board)")
    print(f"  2. SMT Setup & Stencil:                          ${smt_setup + stencil:.2f}")
    print(f"  3. Extended Part Feeder Fees ({len(extended_parts)} parts @ $3): ${feeder_fees:.2f}")
    print(f"  4. SMT Placement Fees ({q} x {total_pcs} parts):          ${placement_fees:.2f}")
    print(f"     -> Subtotal SMT Labor & Setup:                ${smt_labor_total:.2f} (${smt_labor_total/q:.2f}/board)")
    print(f"  5. On-Board Components (ICs, Passives, etc.):    ${components_total:.2f} (${tier_bom_unit:.2f}/board)")
    print(f"  ================================================================")
    print(f"  TOTAL PCBA (Board + SMT + Components):           ${pcba_subtotal:.2f}")
    print(f"  >>> UNIT PCBA COST (excl. Gas Sensors):          ${unit_pcba_cost:.2f} / unit <<<")
    print(f"  6. Gas Sensors (Winsen ME3-CO + Figaro TGS2610): ${q * sensors_total:.2f} (${sensors_total:.2f}/unit)")
    print(f"  >>> COMPLETE UNIT COST (Ready-to-Run Device):     ${unit_complete_cost:.2f} / unit <<<")

