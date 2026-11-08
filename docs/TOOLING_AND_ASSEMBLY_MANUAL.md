# Smart Dual Gas Detector (CO + LPG) - Enclosure Tooling & Assembly Manual
**Engineering Document Ref:** `DOC-MAN-ENC-001`  
**Revision:** 2.0 (Stage 5 Architecture)  
**Applicable Standards:** ISO 20430, ISO 2768-mK, UL 94-V0, UL 2034, EN 50291

---

## 1. Tooling & Injection Mold Specifications

```
                     +---------------------------------------+
                     |         INJECTION MOLD DESIGN         |
                     |  - Steel: 1.2343 / H13 (48-52 HRC)    |
                     |  - 2-Plate Mold with 2 Side Lifters   |
                     |  - Hot Runner Valve Gate (Pin Point)  |
                     +-------------------+-------------------+
                                         |
                                         v
                     +---------------------------------------+
                     |          CAVITY & CORE INSERTS        |
                     |  Cavity 1: Front Housing Bezel        |
                     |  Cavity 2: Rear Chassis Base          |
                     |  Cavity 3: Wall Mounting Bracket      |
                     +-------------------+-------------------+
                                         |
                                         v
                     +---------------------------------------+
                     |           SIDE ACTIONS (SLIDES)       |
                     |  Slide 1: Terminal Cutout J1 (-X)     |
                     |  Slide 2: Terminal Cutout J2 (-X)     |
                     |  Core Pull Angle: 15° Angle Pin       |
                     +---------------------------------------+
```

### 1.1 Mold Parameters

| Parameter | Specification | Notes / Rationale |
| :--- | :--- | :--- |
| **Mold Type** | 2-Plate Family Mold with Side Actions | Cavity 1: Front Bezel, Cavity 2: Rear Chassis |
| **Tool Steel (Cavity/Core)** | **DIN 1.2343 (H13 ESR)** Hardened | 48–52 HRC; high thermal conductivity & polishability |
| **Mold Base** | HASCO / DME Standard (1.1730 steel) | Standard interchangeability for European tool rooms |
| **Gating System** | Hot Runner with Single Valve Pin Gate | Gated on non-cosmetic interior bottom face |
| **Side Pull Slides** | 2x Mechanical Angle-Pin Slides (15°) | Forms horizontal side cutouts for terminal blocks `J1` & `J2` |
| **Ejection System** | $\varnothing 4.0\text{ mm}$ Hardened Ejector Pins | Located directly under the 4 PCB standoff bosses |
| **Cooling Channels** | $\varnothing 8.0\text{ mm}$ Conformal Water Circuits | Balanced flow maintaining core temp within $\pm 2^\circ\text{C}$ |
| **Molding Shrinkage** | **0.45%** (volumetric) | Tailored specifically for flame-retardant PC/ABS |
| **Expected Tool Life** | $\ge 500,000\text{ shots}$ | Class 101 production tooling |

---

## 2. Resin & CMF (Color, Material, Finish) Specifications

### 2.1 Material: Flame-Retardant PC/ABS (UL 94-V0)
- **Trade Names:** Sabic Cycoloy C2950 / Covestro Bayblend FR3010
- **Flammability Rating:** **UL 94-V0** at $1.5\text{ mm}$ thickness (Mandatory for household safety gas detectors)
- **Melt Temperature:** $250^\circ\text{C} - 270^\circ\text{C}$
- **Mold Temperature:** $60^\circ\text{C} - 80^\circ\text{C}$
- **Injection Pressure:** $80 - 120\text{ MPa}$
- **Pre-Drying:** $100^\circ\text{C}$ for $3 - 4\text{ hours}$ (Moisture content $< 0.02\%$)

### 2.2 Surface Texture & Color
- **Front Outer Face:** **Mold-Tech MT-11010 / VDI 24** (Refined micro-spark matte texture, hides finger smudges)
- **Internal Faces:** VDI 30 (Standard EDM finish for clean release)
- **Color:** Clean Architectural Off-White (Pantone Cool Grey 1C / RAL 9003 Signal White)
- **Light Pipe:** Clear Optical Grade Polycarbonate (Makrolon 2807 / Lexan OQ), SPI A-2 diamond polish on lens faces.

---

## 3. Factory Assembly Standard Operating Procedure (SOP)

```
  STEP 1: Brass Inserts      STEP 2: Gaskets & Filters     STEP 3: PCBA Installation    STEP 4: Cover Assembly
 +---------------------+    +-------------------------+    +-----------------------+    +---------------------+
 | Thermal Heat-Set    |    | EPDM Ring on LS1 Buzzer |    | Drop PCB on 4 Bosses  |    | Mate Front Cover    |
 | 4x M2.5x5.7 Inserts | -> | ePTFE Mesh in CO Well   | -> | 4x M2.5x6 Torx Screws | -> | 4x Screws or Snaps  |
 | 280°C, 1.5s Dwell   |    | Light Pipe in Pocket    |    | Torque: 0.35 N*m      |    | Test Acoustic/Gas   |
 +---------------------+    +-------------------------+    +-----------------------+    +---------------------+
```

### Step 1: Heat-Set Brass Insert Installation
1. Place the molded Rear Chassis Base in an alignment fixture.
2. Using a temperature-controlled thermal insertion press fitted with an M2.5 conical tip:
   - **Temperature:** Set to $280^\circ\text{C} \pm 5^\circ\text{C}$.
   - **Part:** 4x Ruthex `RX-M2.5x5.7` knurled brass inserts.
   - **Insert Speed:** Smooth downward stroke ($1.5\text{ s}$ dwell time).
   - **Flushness:** Verify insert top face is flush or recessed $0.1\text{ mm}$ below the boss top surface. Zero melt flashing.

### Step 2: Gaskets, Filters & Light Pipe Insertion
1. **Acoustic Seal:** Place an annular EPDM foam O-ring ($OD = 12.0\text{ mm}, ID = 9.0\text{ mm}, t = 1.5\text{ mm}$) into the cylindrical shroud on the inside of the front cover.
2. **CO Gas Filter:** Ultrasonic weld (or peel-and-stick 3M 9471 adhesive) the hydrophobic ePTFE dust membrane ($16.0\text{ mm} \times 16.0\text{ mm}$) over the inside face of the CO diffusion louvers.
3. **Optical Light Guide:** Snap the 4-channel clear polycarbonate light pipe into the front housing retention clips. Ensure the 4 lower convex lenses align directly with the PCB LED centers.

### Step 3: PCBA Installation
1. Verify that both **Winsen ME3-CO** and **Figaro TGS2610** sensors are installed in their respective sockets/pads.
2. Lower the PCB ($70.0\text{ mm} \times 50.0\text{ mm}$) into the rear chassis base:
   - Ensure the two Phoenix terminal blocks (`J1`, `J2`) fit snugly into the left wall cutouts.
   - Align the 4 PCB mounting holes (`H1..H4`) with the 4 brass insert bosses.
3. Drive 4x **M2.5 $\times$ 6.0 mm Pan-Head Torx (T8)** black stainless steel machine screws:
   - **Torque Limit:** **$0.35\text{ N}\cdot\text{m} \pm 0.05\text{ N}\cdot\text{m}$** using an electric torque screwdriver.

### Step 4: Front Cover Closure & Final Inspection
1. Align the front cover stepped lip over the rear chassis base.
2. Ensure the internal thermal barrier rib seats cleanly into the separation gap between Zone D and Zone F without pinching any component leads.
3. Fasten perimeter screws or engage the 4 snap-tabs with an audible tactile click.

---

## 4. Quality Control & Compliance Verification Tests

| Test Item | Standard | Test Method / Requirement | Pass Criteria |
| :--- | :--- | :--- | :--- |
| **Acoustic Sound Level** | **UL 2034 § 36** | Measure sound pressure level at $3.0\text{ meters}$ in anechoic chamber. | **$\ge 85\text{ dBA}$** continuous / pulsed |
| **Thermal Isolation** | In-House Protocol | Run Figaro TGS2610 at full $280\text{ mW}$ heater power for $24\text{ hours}$. | **$\Delta T \le 0.7^\circ\text{C}$** at CO sensor body |
| **Drop & Shock Resistance** | **UL 2034 § 40** | Drop unit 3 times from $1.0\text{ meter}$ height onto concrete floor. | Zero cracks, no loose parts, normal function |
| **Environmental Ingress** | **IEC 60529** | Talcum powder dust chamber and vertical water drip. | **IP52** (Protected against dust & dripping water) |
| **Flammability** | **UL 94** | 50W vertical flame test on 5 specimens ($t = 1.5\text{ mm}$). | **V-0** (Burning stops within 10s, no flaming drips) |
