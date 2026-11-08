# Smart Dual Gas Detector (CO + LPG) - JLCPCB PCBA Package
## Engineering Revision 2.0 (Stage 5 Architecture)

This project folder is fully validated, cleaned, and organized specifically for ordering and automated SMT assembly (**PCBA**) at **JLCPCB**.

---

## 1. Quick Ordering Guide for JLCPCB

### Step 1: Upload Gerbers
1. Go to [JLCPCB.com](https://jlcpcb.com) and click **Order Now**.
2. Upload the Gerber archive from the `fab_jlcpcb/` folder:
   - File: `fab_jlcpcb/co_detector_controller_gerbers_jlcpcb.zip`
3. JLCPCB will automatically detect the dimensions: **70.0 mm × 50.0 mm**.

### Step 2: Set PCB Specifications
- **Layers:** `4 Layers`
- **Dimensions:** `70.0 mm x 50.0 mm`
- **PCB Thickness:** `1.6 mm`
- **Surface Finish:** **`ENIG` (Electroless Nickel Immersion Gold)** *(Recommended for 0.5mm pitch WSON-14 LMP91000 and ESP32 castellated pads)*
- **Copper Weight:** `1 oz` Outer / `1 oz` Inner
- **Solder Mask Color:** `Green` (or customer preference)
- **Silkscreen:** `White`
- **Edge Rails / Tooling Holes:** `Added by JLCPCB`

### Step 3: Enable SMT Assembly (PCBA)
1. Turn on the **PCB Assembly** toggle.
2. **Assembly Side:** Select **`Top Side`** only *(All components are on top side; 0 components on bottom)*.
3. **Tooling Holes:** Select `Added by JLCPCB`.

### Step 4: Upload BOM and CPL (from `fab_jlcpcb/`)
1. In the Assembly upload dialog:
   - **BOM File:** Upload `fab_jlcpcb/JLCPCB_BOM.csv`
   - **CPL / Centroid File:** Upload `fab_jlcpcb/JLCPCB_CPL.csv`
2. JLCPCB's system will automatically match all 43 line items (88 components) using the pre-mapped LCSC part numbers (`Cxxxx`).

### Step 5: DFM & Component Placement Review
- Inspect the interactive 3D placement screen.
- Verify diode cathode bands (`D1..D3, D7`) and IC pin 1 marks (`U1..U6`).
- Confirm order and proceed to checkout.

---

## 2. Post-Assembly Sensor Installation (Manual / Sockets)

> [!WARNING]
> Do NOT send chemical gas sensors through the high-temperature SMT reflow oven ($>240^\circ\text{C}$). They will be irreversibly damaged.

Install the following two sensors manually or via pin sockets after receiving the assembled boards:
1. **`S1`: Winsen ME3-CO** (Electrochemical Carbon Monoxide sensor):
   - Insert into Zone D (bottom-right 3-pin socket / pads).
2. **`S2`: Figaro TGS2610-C00** (Combustible Gas / LPG sensor):
   - Insert into Zone F (top-right 4-pin socket / pads).

---

## 3. Directory Structure

```
co_detector_controller/
├── co_detector_controller_gerbers_jlcpcb.zip  # Ready-to-upload Gerber + Drill package for JLCPCB
├── JLCPCB_BOM.csv                             # Standard JLCPCB SMT BOM with verified LCSC part numbers
├── JLCPCB_CPL.csv                             # Standard JLCPCB Pick & Place (Centroid) coordinates
├── co_detector_controller_schematic.pdf       # Complete electrical schematic PDF
├── BOM.csv                                    # Master engineering BOM with design zones and circuit notes
│
├── co_detector_controller.kicad_pro           # KiCad 10 Project file
├── co_detector_controller.kicad_sch           # KiCad Schematic
├── co_detector_controller.kicad_pcb           # KiCad 4-Layer PCB Layout
├── co_detector_symbols.kicad_sym              # Project symbol library
├── sym-lib-table                              # Symbol library table
│
├── fab_jlcpcb/                                # Extracted fabrication deliverables
│   ├── gerbers/                               # Individual Gerber RS-274X and Excellon drill files
│   ├── raw_pos.csv                            # Raw KiCad position export
│   ├── JLCPCB_BOM.csv
│   └── JLCPCB_CPL.csv
│
├── reports/                                   # Validation and DRC reports
│   ├── drc_stage5.json                        # 0 errors / 0 unconnected DRC report
│   ├── erc_report.json                        # 0 errors ERC report
│   └── stage5_net_stats.json                  # Track lengths, via count, plane stats
│
├── scripts/                                   # Automation and build scripts
│   ├── build_stage4.py                        # Complete PCB layout generator
│   ├── generate_schematic.py                  # Schematic and netlist generator
│   ├── build_jlcpcb_package.py                # Standalone JLCPCB deliverable builder
│   ├── calculate_pcba_costs.py                # Financial and pricing simulation engine
│   └── build_3d_models.py                     # 3D mechanical model generator
│
├── 3dmodels/                                  # WRL / STEP 3D CAD models
└── audit_rev3/                                # Firmware Wokwi testbench & SPICE simulation
```

