# Smart Dual Gas Detector (CO + LPG) - Tooling & Production Assembly Manual
**Revision:** 3.0 (Ground-Truth PCBA Aligned)  
**Document ID:** AGY-DOC-PROD-301  
**Target Manufacturing Process:** Automated Multi-Cavity Plastic Injection Molding & SMT Integration  

---

## 1. Tooling Specifications (Injection Mold Design)

| Mold Parameter | Engineering Value | Notes |
| :--- | :--- | :--- |
| **Resin Material** | Sabic Cycoloy FR15 (PC/ABS blend) | Flame-retardant UL94 V-0, high impact toughness |
| **Mold Steel (Cavity/Core)**| DIN 1.2343 (AISI H11 ESR) hardened to 50-52 HRC | High polishability & wear resistance |
| **Number of Cavities** | 2 + 2 Family Mold (Base, Cover, Bracket, Lens) | Balanced hot-runner system with submarine gates |
| **Nominal Wall Thickness** | $2.40\text{ mm} \pm 0.10\text{ mm}$ uniform | Prevents sink marks, warpage, and internal voids |
| **Draft Angles** | $1.5^\circ$ nominal on all vertical shutoff surfaces | $0.5^\circ$ minimum on shallow internal ribs |
| **Shrinkage Factor** | $0.5\% - 0.7\%$ ($0.005 - 0.007\text{ mm/mm}$) | Compensated in primary tooling electrode EDM |
| **Surface Finish** | VDI 27 (Exterior Matte) / SPI-A2 (Light Pipes) | Glare reduction on front face; mirror finish on optics |

---

## 2. Fastening & Mechanical Assembly Sequence

```mermaid
flowchart TD
    Step1["1. Install 4x Ruthex M2.5 Brass Inserts into Lower Base Bosses (210°C Heat Stake)"]
    Step2["2. Seat 0.96-inch OLED PMMA Protective Lens into Front Cover Bezel Shelf (UV Cured)"]
    Step3["3. Drop PCBA into Lower Chassis Base (Locating onto 4x H1..H4 Alignment Bosses)"]
    Step4["4. Fasten PCBA with 4x M2.5 x 6mm Stainless Steel Pan Head Screws (0.35 Nm)"]
    Step5["5. Insert Tactile Button Plungers & 4-Channel Optical Light Pipe into Front Cover"]
    Step6["6. Mate Front Cover Tongue into Base Groove (Perimeter Tongue-and-Groove Seal)"]
    Step7["7. Drive 4x M3 x 16mm Countersunk Housing Machine Screws from Rear Face (0.5 Nm)"]
    Step8["8. Slide Enclosure onto Pre-Mounted Wall Bracket (Audible Snap Latch Engagement)"]

    Step1 --> Step2 --> Step3 --> Step4 --> Step5 --> Step6 --> Step7 --> Step8
```

---

## 3. Ground-Truth PCBA Interface Alignment Table

| Enclosure Aperture | Connected PCB Component | CAD Center $(X, Y)$ [mm] | Clearance |
| :--- | :--- | :--- | :--- |
| **OLED Bezel Window** | J4 Header / 0.96" OLED Module | $(48.50, 32.50)$ | $25.0 \times 14.0\text{ mm}$ ($+0.5\text{ mm}$ float) |
| **SW2 Button (Hush)** | PTS647 Tactile Switch | $(42.00, 12.00)$ | $\varnothing 5.5\text{ mm}$ ($+0.5\text{ mm}$ stem radial) |
| **SW1 Button (Test)** | PTS647 Tactile Switch | $(42.00, 6.00)$ | $\varnothing 5.5\text{ mm}$ ($+0.5\text{ mm}$ stem radial) |
| **Optical Status LEDs**| D4, D5, D6, D8 (Alarm/Pwr/WiFi/Flt)| $Y = 4.00, X \in [26.8..36.4]$ | 4x $\varnothing 2.0\text{ mm}$ light guide ports |
| **Acoustic Rosette Horn**| LS1 Piezo Buzzer 85dB | $(32.00, 12.00)$ | 7-hole radial acoustic port array |
| **CO Diffusion Grille** | Winsen ME3-CO Electrochemical Cell | $(56.50, 14.50)$ | Concentric louvers $\varnothing 20.5\text{ mm}$ |
| **LPG Thermal Chimney**| Figaro TGS2610-C00 Sensor | $(59.00, 43.50)$ | Upward natural convection venting slots |
| **Terminal J1 Cutout** | 12V DC Power Screw Terminal | Left Wall $(Y = 38.00)$ | $12.0 \times 10.5\text{ mm}$ split opening |
| **Terminal J2 Cutout** | External Relay Alarm Terminal | Left Wall $(Y = 12.00)$ | $12.0 \times 10.5\text{ mm}$ split opening |
| **Reset SW3 Pinhole** | Hardware Master Reset Switch | Left Wall $(Y = 20.20)$ | $\varnothing 2.5\text{ mm}$ recessed access |
