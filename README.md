# Smart Dual Gas Detector (CO + LPG) Controller

[![KiCad](https://img.shields.io/badge/KiCad-10.0-blue.svg)](https://www.kicad.org/)
[![Hardware](https://img.shields.io/badge/Hardware-Rev%202.0%20(Stage%205)-brightgreen.svg)]()
[![Release](https://img.shields.io/badge/Release-v2.0.0-blue.svg)](https://github.com/naoufalelhlou22/co-detector-controller/releases/tag/v2.0.0)
[![DRC](https://img.shields.io/badge/KiCad%20DRC-0%20Errors-success.svg)]()
[![ERC](https://img.shields.io/badge/KiCad%20ERC-0%20Errors-success.svg)]()
[![JLCPCB Ready](https://img.shields.io/badge/PCBA-JLCPCB%20Ready-orange.svg)](README_JLCPCB.md)

Production-grade, 4-layer smart dual-gas detector hardware platform designed around the **ESP32-C3** Wi-Fi/BLE microcontroller. Integrates precision analog front-ends for simultaneous monitoring of **Carbon Monoxide (CO)** and **Combustible Liquefied Petroleum Gas (LPG)**.

> [!TIP]
> Ready-to-manufacture Gerbers, schematic PDF, BOM, and CPL files are attached directly to the [v2.0.0 Release](https://github.com/naoufalelhlou22/co-detector-controller/releases/tag/v2.0.0).

---

## Features

- **Microcontroller:** ESP32-C3-MINI-1 (RISC-V 32-bit single-core, Wi-Fi 4 + Bluetooth 5 LE).
- **Carbon Monoxide Subsystem (Zone D):**
  - Sensor: **Winsen ME3-CO** (electrochemical cell).
  - Analog Front-End: **TI LMP91000** configurable AFE potentiostat with programmable transimpedance gain (TIA) via $I^2C$.
- **Combustible / LPG Subsystem (Zone F):**
  - Sensor: **Figaro TGS2610-C00** (metal-oxide semiconductor gas sensor).
  - High-side PWM-modulated heater driver and buffered voltage divider analog readout.
- **Power Management (Zone A):**
  - Primary Input: 5V DC via USB-C or screw terminals.
  - 3.3V Step-Down: Low-noise, high-efficiency LDO / buck regulator.
  - Active reverse-polarity, over-voltage, and transient protection.
- **User Interface & Annunciation (Zone C):**
  - Audio: Piezo sounder with transistor buffer for audible emergency alarms.
  - Visual: Status and alarm LEDs (Power, CO Alert, LPG Alert, Fault/WiFi).
  - Input: Tactile switches for Alarm Mute/Hush and Self-Test.
- **Fabrication & Assembly:**
  - 100% single-sided SMT placement (Top side only) for cost-effective PCBA.
  - Verified LCSC part numbers for turn-key assembly via JLCPCB.

---

## Hardware Specifications

| Parameter | Specification |
| :--- | :--- |
| **Dimensions** | 70.0 mm × 50.0 mm |
| **Layer Count** | 4 Layers (Signal Top - GND - 3V3/Power - Signal Bottom) |
| **PCB Thickness** | 1.6 mm |
| **Surface Finish** | ENIG (Electroless Nickel Immersion Gold) recommended |
| **Copper Weight** | 1 oz outer / 1 oz inner |
| **Sensors Installed** | Winsen ME3-CO (CO), Figaro TGS2610 (LPG) |
| **Target Standards** | Designed referencing UL 2034 / EN 50291 acoustic and sensitivity curves |

---

## Repository Structure

```
co_detector_controller/
├── co_detector_controller.kicad_pro    # KiCad 10 project file
├── co_detector_controller.kicad_sch    # Main schematic
├── co_detector_controller.kicad_pcb    # 4-layer routed PCB layout
├── co_detector_symbols.kicad_sym       # Project custom symbol library
├── sym-lib-table                       # Symbol library mapping
├── co_detector_controller_schematic.pdf# High-resolution PDF schematic export
├── README_JLCPCB.md                    # Complete JLCPCB PCBA ordering guide
│
├── fab_jlcpcb/                         # Ready-to-order manufacturing deliverables
│   ├── co_detector_controller_gerbers_jlcpcb.zip # Gerber & Excellon drill archive
│   ├── JLCPCB_BOM.csv                  # Bill of Materials mapped with LCSC part numbers
│   ├── JLCPCB_CPL.csv                  # Centroid / Pick & Place coordinates
│   └── gerbers/                        # Extracted RS-274X layer files
│
├── reports/                            # Automated verification logs
│   ├── drc_stage5.json                 # Design Rules Check report (0 errors, 0 unconnected)
│   ├── erc_report.json                 # Electrical Rules Check report (0 errors)
│   ├── stage5_net_stats.json           # Track, via, and copper plane metrics
│   └── BOM_engineering_master.csv      # Detailed engineering BOM
│
├── audit_rev3/                         # Simulation and firmware verification
│   ├── spice/                          # SPICE netlists and simulation run results
│   ├── run_all_spice_sims.py           # Automated ngspice test runner
│   └── wokwi/                          # Wokwi firmware simulation testbench
│       ├── src/                        # Embedded C++ drivers (pins, power, watchdog)
│       └── test/                       # 18-scenario automated verification testbench
│
├── scripts/                            # KiCad Python automation scripts
│   ├── build_stage4.py                 # Automated PCB placement & routing engine
│   ├── generate_schematic.py           # Schematic generator
│   ├── build_jlcpcb_package.py         # Gerber, BOM, and CPL packager
│   ├── calculate_pcba_costs.py         # JLCPCB assembly cost estimator
│   └── build_3d_models.py              # 3D mechanical model export tool
│
└── 3dmodels/                           # 3D CAD models (VRML / STEP)
```

---

## Manufacturing & Assembly

For complete step-by-step instructions on ordering boards and PCBA through JLCPCB, see the [JLCPCB Ordering Guide](README_JLCPCB.md).

> [!CAUTION]
> Chemical gas sensors (**Winsen ME3-CO** and **Figaro TGS2610**) must **NOT** be passed through the SMT reflow oven. Solder sockets or hand-solder sensors post-reflow.

---

## License

This project is open-source hardware licensed under the [MIT License](LICENSE) (or CERN-OHL-P / user preferred license).

