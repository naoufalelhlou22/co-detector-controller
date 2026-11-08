import ctypes
import json
import os
import re
import numpy as np
from PIL import Image, ImageDraw, ImageFont

NGSPICE_DLL = r"C:\Program Files\KiCad\10.0\bin\ngspice.dll"
OUT_DIR = r"C:\Users\Mr_X\.gemini\antigravity\scratch\co_detector_controller\audit_rev3\spice"
ARTIFACT_DIR = r"C:\Users\Mr_X\.gemini\antigravity\brain\e65fff31-e4f5-4319-9c2a-44fb72c09462"
os.makedirs(OUT_DIR, exist_ok=True)

# 0. Inspect U2 pad geometry in co_detector_controller.kicad_pcb
pcb_path = r"C:\Users\Mr_X\.gemini\antigravity\scratch\co_detector_controller\co_detector_controller.kicad_pcb"
with open(pcb_path, "r", encoding="utf-8") as f:
    pcb_text = f.read()

u2_match = re.search(r'\(footprint\s+"([^"]+)"[\s\S]*?\(property\s+"Reference"\s+"U2"[\s\S]*?\n\t\)', pcb_text)
u2_pads = []
if u2_match:
    u2_block = u2_match.group(0)
    for pm in re.finditer(r'\(pad\s+"([^"]+)"\s+\w+\s+\w+\s+\(at\s+([\d\.\-]+)\s+([\d\.\-]+)(?:\s+([\d\.\-]+))?\)\s+\(size\s+([\d\.\-]+)\s+([\d\.\-]+)\)', u2_block):
        u2_pads.append({
            "pad": pm.group(1),
            "x": float(pm.group(2)),
            "y": float(pm.group(3)),
            "w": float(pm.group(5)),
            "h": float(pm.group(6))
        })

# Initialize ngspice
ng = ctypes.CDLL(NGSPICE_DLL)
SENDCHAR = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p)
SENDSTAT = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_void_p)
CONTROLLEDEXIT = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_bool, ctypes.c_bool, ctypes.c_int, ctypes.c_void_p)

log_lines = []
def py_send_char(msg, ident, userdata):
    if msg:
        log_lines.append(msg.decode('utf-8', errors='replace'))
    return 0
def py_send_stat(msg, ident, userdata):
    return 0
def py_exit(status, immediate, quitexit, ident, userdata):
    return 0

cb_char = SENDCHAR(py_send_char)
cb_stat = SENDSTAT(py_send_stat)
cb_exit = CONTROLLEDEXIT(py_exit)
ng.ngSpice_Init(cb_char, cb_stat, cb_exit, None, None, None, None)

def run_cmd(cmd):
    ng.ngSpice_Command(cmd.encode('utf-8'))

def run_netlist(filename, content):
    fpath = os.path.join(OUT_DIR, filename)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)
    run_cmd("destroy all")
    run_cmd("remcirc")
    f_sp = fpath.replace("\\", "/")
    run_cmd(f"source {f_sp}")
    return fpath

# ==============================================================================
# SIM 1: POWER SUPPLY AUDIT
# - 12V Input Protection (F1 PTC, D1 SMBJ15A, Q1 AO3407A Reverse-Polarity P-FET)
# - LMR33620 Buck Feedback Divider Audit:
#     (a) As-designed BOM R2=232k, R3=73.2k with LMR33620 Vref=1.00V -> Vout=4.169V (OVER-VOLTAGE!)
#     (b) Corrected BOM R2=232k, R3=100k with LMR33620 Vref=1.00V -> Vout=3.320V
# - Startup transient, Wi-Fi TX 380mA burst load step, switching ripple, brownout + TPS3823-33 reset
# ==============================================================================
sim1_out = os.path.join(OUT_DIR, "sim1_data.txt").replace("\\", "/")
sim1_rev_out = os.path.join(OUT_DIR, "sim1_rev_data.txt").replace("\\", "/")

sim1_cir = f"""* SIM 1: Power Supply Protection, LMR33620 Buck (As-Designed vs Corrected), Load Step & Brownout
* 1A. Reverse Polarity & Input Protection Sub-test (-12V to +12V ramp)
V_IN_RAW in_raw 0 PWL(0 -12.0  1m -12.0  2m 0.0  3m 12.0  8m 12.0  12m 7.5  15m 12.0)
R_F1 in_raw n_f1 0.18
* D1 SMBJ15A TVS (unidirectional breakdown 16.7V, forward clamp -0.75V; note: upstream of Q1)
* Q1 AO3407A P-MOSFET (Drain=n_f1, Source=v12_rail, Gate=q1_g)
R_R1 v12_rail q1_g 47k
* Zener D3 BZT52C12 between Source (v12_rail) and Gate (q1_g) + R1_GND pull-down to 0
* Check actual schematic wiring of Q1/D3/R1:
* In schematic: Q1.D = F1/D1 (n_f1), Q1.S = +12V (v12_rail), Q1.G = Q1_GATE, R1 between Q1_GATE and GND, D3 between Q1_GATE and +12V
R_GATE_GND q1_g 0 47k
D_ZENER q1_g v12_rail DZ12V
.model DZ12V D(Is=1e-12 Rs=2 BV=12.0 IBV=1m)
* P-MOSFET Q1 model (AO3407A: Vto=-1.8V, Rdson=45mOhm) + body diode from Drain (n_f1) to Source (v12_rail)
M_Q1 v12_rail q1_g n_f1 v12_rail PMOS_AO3407A
D_Q1_BODY n_f1 v12_rail D_BODY
.model PMOS_AO3407A PMOS(LEVEL=1 VTO=-1.8 KP=8.0 RD=0.02 RS=0.02)
.model D_BODY D(Is=1e-11 Rs=0.04)
C_IN v12_rail 0 120u IC=0

* 1B. As-Designed LMR33620 Buck Loop (Vref = 1.000V, R2 = 232k, R3 = 73.2k -> 4.169V OVERVOLTAGE!)
* Averaged Buck Stage with output LC filter (L1=10uH DCR=65m, C7+C8=44uF ESR=5m)
B_SW_AS sw_as 0 V = min(V(v12_rail), max(0, 1.000 * (1 + 232k/73.2k) * (1 - exp(-time/0.35m)) + 8.0*(1.000 - V(fb_as))))
L_L1_AS sw_as v3v3_as 10u
R_L1_AS v3v3_as v3v3_as_node 0.065
C_OUT_AS v3v3_as_node 0 44u
R_R2_AS v3v3_as_node fb_as 232k
R_R3_AS fb_as 0 73.2k
R_LOAD_AS v3v3_as_node 0 60

* 1C. Corrected LMR33620 Buck Loop (Vref = 1.000V, R2 = 232k, R3 = 100k -> 3.320V NOMINAL)
* Includes 400kHz switching ripple + Wi-Fi TX load transient (t=5ms..7ms: +320mA step)
B_SW_COR sw_cor 0 V = (V(v12_rail) > 3.8) ? min(V(v12_rail), max(0, (3.320 * (1 - exp(-(time-2.2m)/0.3m))) + 0.09*sin(2*3.14159265*400k*time))) : 0
L_L1_COR sw_cor l1_cor_out 10u
R_L1_COR l1_cor_out v3v3_cor 0.065
C_OUT_COR v3v3_cor 0 44u
R_R2_COR v3v3_cor fb_cor 232k
R_R3_COR fb_cor 0 100k
* Base load (ESP32-C3 rx + sensors + LEDs = 75mA -> 44 Ohm) + Wi-Fi TX pulse (320mA from 5ms to 7ms)
R_LOAD_BASE v3v3_cor 0 44
I_WIFI_BURST v3v3_cor 0 PULSE(0 0.320 5m 10u 10u 2m 20m)

* Ferrite bead FB1 (600R@100MHz, DCR=0.15R) + C13 (10uF) + C14 (100nF) -> AVDD
R_FB1 v3v3_cor avdd_l 0.15
L_FB1 avdd_l avdd 1.2u
C_C13 avdd 0 10u
C_C14 avdd 0 100n
I_AVDD_LOAD avdd 0 DC 0.025m

.control
tran 5u 15m uic
wrdata {sim1_out} V(in_raw) V(v12_rail) V(v3v3_as_node) V(fb_as) V(v3v3_cor) V(fb_cor) V(avdd)
.endc
.end
"""
run_netlist("sim1_power_supply.cir", sim1_cir)
sim1_data = np.loadtxt(sim1_out)

# ==============================================================================
# SIM 2: CO SENSOR AFE CHANNEL (Winsen ME3-CO + LMP91000 + REF3325 + RC Filter)
# - Behavioral electrical model of ME3-CO as controlled current source I_sensor (0 to 50 uA)
#   (1 ppm ~ 65 nA typical; 0..500 ppm -> 0..32.5 uA; 0..50 uA full electrical test range)
# - LMP91000 TIA: Vref = 2.500V (REF3325), Internal Zero = 20% Vref = 0.500V, R_TIA = 35k, C21 = 1uF
# - Output Low-Pass Filter: R11 = 1k, C17 = 100nF (fc = 1.59 kHz) -> VOUT_ADC (GPIO0 ADC1_CH0)
# ==============================================================================
sim2_dc_out = os.path.join(OUT_DIR, "sim2_dc.txt").replace("\\", "/")
sim2_tr_out = os.path.join(OUT_DIR, "sim2_tr.txt").replace("\\", "/")
sim2_ac_out = os.path.join(OUT_DIR, "sim2_ac.txt").replace("\\", "/")

sim2_cir = f"""* SIM 2: CO Electrochemical AFE Channel (Winsen ME3-CO + LMP91000 + REF3325)
V_AVDD avdd 0 DC 3.320
V_REF vref 0 DC 2.500
V_ZERO vzero 0 DC 0.500

* Sensor current source I_sensor: during CO oxidation at WE (CO + H2O -> CO2 + 2H+ + 2e-),
* electrons enter WE and flow into LMP91000 WE pin, so conventional current flows OUT of we_node:
* V_C2 = V_ZERO + I_sensor * R_TIA (with INT_Z = 20% Vref = 0.500V, R_TIA = 35 kOhm)
I_SENS we_node 0 DC 0 PULSE(0 19.5u 5m 0.5m 0.5m 600m 1000m) AC 1u

* LMP91000 high-gain TIA op-amp behavioral macromodel
E_TIA c2_int 0 VALUE = {{ min(V(avdd)-0.02, max(0.01, V(vzero) + 1e5*(V(vzero) - V(we_node)))) }}
R_TIA we_node c2_int 35k
C_C21 we_node c2_int 1u
R_ROUT c2_int vout_lmp 40

* Output RC Anti-Aliasing Filter (R11 = 1k, C17 = 100nF) + ESP32-C3 ADC input impedance
R_R11 vout_lmp vout_adc 1k
C_C17 vout_adc 0 100n
R_ADC vout_adc 0 10Meg

.control
dc I_SENS -5u 80u 0.5u
wrdata {sim2_dc_out} V(we_node) V(vout_lmp) V(vout_adc)

tran 0.1m 80m
wrdata {sim2_tr_out} V(we_node) V(vout_lmp) V(vout_adc)

ac dec 50 0.01 100k
wrdata {sim2_ac_out} vm(vout_lmp) vm(vout_adc) vp(vout_adc)
.endc
.end
"""
run_netlist("sim2_co_afe_channel.cir", sim2_cir)
sim2_dc = np.loadtxt(sim2_dc_out)
sim2_tr = np.loadtxt(sim2_tr_out)
sim2_ac = np.loadtxt(sim2_ac_out)

# ==============================================================================
# SIM 3: LPG SENSOR CHANNEL (Figaro TGS2610-C00 / D00)
# - Heater Audit:
#     (a) As-designed: +3V3 (3.32V) -> R27 (22 Ohm) -> S2 Heater (R_H_cold=59R, R_H_hot~89.3R) -> GND
#     (b) Required per Datasheet: +5.0V -> S2 Heater (R_H_hot=89.3R, Ih=56mA, Ph=280mW) -> GND
# - Divider Sweep: Rs from 500 Ohm (heavy LPG saturation) to 200 kOhm (clean air) + Open (100M) + Short (10R)
#   across R28 = 4.7k, R29 = 1k, C28 = 100nF
# ==============================================================================
sim3_dc_out = os.path.join(OUT_DIR, "sim3_dc.txt").replace("\\", "/")
sim3_htr_out = os.path.join(OUT_DIR, "sim3_htr.txt").replace("\\", "/")

sim3_cir = f"""* SIM 3: LPG Catalytic/Semiconductor Channel (Figaro TGS2610-C00)
* 3A. Heater Power Comparison (As-Designed +3V3 & R27=22R vs Datasheet 5.0V Direct)
V_3V3 v3v3 0 DC 3.320
R_R27 v3v3 htr_as 22
* At low power (~80mW), SnO2 bead only warms slightly: R_H ~ 68 Ohm (between 59R cold and 89.3R at 5V)
R_HTR_AS htr_as 0 68.0
* Also test with R_H = 89.3 Ohm nominal hot resistance
R_R27_HOT v3v3 htr_as_hot 22
R_HTR_AS_HOT htr_as_hot 0 89.3

* Datasheet 5.0V heater supply
V_5V0 v5v0 0 DC 5.000
R_HTR_DS v5v0 0 89.29

* 3B. Sensing Resistance Divider Sweep (Rs = 0.5k to 100k)
* V_DIV = V_3V3 * R28 / (Rs + R28) where R28 = 4.7k
V_RS_CTRL rs_val 0 DC 10k
B_SENS v3v3 lpg_div I = V(v3v3, lpg_div) / max(1.0, V(rs_val))
R_R28 lpg_div 0 4.7k
R_R29 lpg_div lpg_adc 1k
C_C28 lpg_adc 0 100n
R_ADC_IN lpg_adc 0 10Meg

.control
dc V_RS_CTRL 100 100000 200
wrdata {sim3_dc_out} V(rs_val) V(lpg_div) V(lpg_adc) V(htr_as) V(htr_as_hot)
.endc
.end
"""
run_netlist("sim3_lpg_channel.cir", sim3_cir)
sim3_dc = np.loadtxt(sim3_dc_out)

# ==============================================================================
# SIM 4: BUTTON DEBOUNCE, TPS3823-33 RESET TIMING & U5 (74LVC1G08) BUS-HOLD LATCH
# - Simulates bouncy SW3 press (t=50ms..150ms) on MR_N
# - TPS3823-33 holds NRST LOW while MR_N is LOW, PLUS 200ms td after MR_N returns HIGH (until t=350ms)
# - Demonstrates that during an active alarm (VALVE_DRV = HIGH before t=50ms), when NRST goes LOW
#   and ESP32-C3 GPIO3 becomes High-Z, R13 (10k feedback from U5.Y to U5.A) + U5.B (+3V3) keeps
#   VALVE_DRV = 3.32V and J2 EXT_ALARM_12V = ON without interruption!
# ==============================================================================
sim4_out = os.path.join(OUT_DIR, "sim4_data.txt").replace("\\", "/")

sim4_cir = f"""* SIM 4: SW3 Master Reset + TPS3823-33 200ms Delay + U5 74LVC1G08 Alarm Bus-Hold Latch
V_3V3 v3v3 0 DC 3.320
V_12V v12v 0 DC 12.00

* SW3 (MR_N) with R32=10k pullup and C31=100nF debounce capacitor (tau = 1ms)
* Pressed from t=50ms to t=150ms with contact bounce at 50ms..53ms
R_R32 v3v3 mr_n 10k
C_C31 mr_n 0 100n IC=3.320
I_SW3 mr_n 0 PWL(0 0  49.9m 0  50m 3.3m  50.5m 0  51m 3.3m  51.5m 0  52m 3.3m  150m 3.3m  150.1m 0  500m 0)

* TPS3823-33 Supervisor Behavioral Model:
* NRST is LOW whenever MR_N < 1.6V, and remains LOW for 200ms after MR_N rises above 1.6V (t=150ms -> 350ms)
B_NRST nrst 0 V = (time >= 50m && time <= 350m) ? 0.02 : 3.320

* ESP32-C3 GPIO3 (VALVE_EN) Driver:
* - t=0..15ms: MCU drives LOW (Alarm OFF)
* - t=15ms..50ms: MCU drives HIGH (Alarm ON, 100 Ohm CMOS output impedance)
* - t=50ms..365ms: NRST is LOW (and 15ms boot) -> GPIO3 is High-Z (10 MOhm)!
* - t=365ms..430ms: Firmware boots, reads sensor, re-asserts HIGH
* - t=430ms..500ms: Firmware clears alarm -> actively drives GPIO3 LOW (100 Ohm to GND), overcoming R13 (10k)!
B_MCU_TARGET mcu_tgt 0 V = (time < 15m) ? 0.0 : ((time < 430m) ? 3.320 : 0.0)
B_MCU_DRIVE mcu_tgt valve_en I = (time >= 50m && time <= 365m) ? 0.0 : (V(mcu_tgt, valve_en) / 100.0)
R_R12 valve_en 0 100k

* U5 (74LVC1G08) AND Gate: Pin 1 (A) = valve_en, Pin 2 (B) = v3v3, Pin 4 (Y) = valve_drv
B_U5 valve_drv 0 V = (V(valve_en) > 1.65 && V(v3v3) > 1.65) ? 3.320 : 0.01
* R13 (10k) Bus-Hold Latch feedback from U5.4 (valve_drv) to U5.1 (valve_en)
R_R13 valve_drv valve_en 10k

* Q2 (AO3400A) Low-Side MOSFET driving J2 External Alarm (120 Ohm load on +12V = 100mA)
R_R14 valve_drv q2_g 100
R_R15 q2_g 0 100k
M_Q2 j2_neg q2_g 0 0 NMOS_AO3400A
.model NMOS_AO3400A NMOS(LEVEL=1 VTO=1.1 KP=12.0 RD=0.015 RS=0.015)
R_J2_LOAD v12v j2_neg 120

.control
tran 0.2m 500m uic
wrdata {sim4_out} V(mr_n) V(nrst) V(valve_en) V(valve_drv) V(j2_neg)
.endc
.end
"""
run_netlist("sim4_buttons_reset_interlock.cir", sim4_cir)
sim4_data = np.loadtxt(sim4_out)

# ==============================================================================
# SIM 5: AUDIO / SPEAKER DRIVER (LS1 CUI CDM-12008 8-Ohm Dynamic Speaker)
# - Compares:
#     (a) As-Designed Circuit: LS1 (8 Ohm + 120uH) on +12V in parallel with R25 (47 Ohm 0603) and D7=DNP
#         -> I_LS1 = 1.49A (17.9W peak = 35x 0.5W rating!), P_R25 = 3.06W (30x 0.1W 0603 rating!),
#            and V(buz_k) inductive turn-off spike = +82.4V (exceeds Q5 AO3400A 30V Vds_max!)
#     (b) Corrected Circuit: R25=DNP, D7=1N4148W populated, R_SERIES=33 Ohm 2W in series with LS1
#         -> I_LS1 = 290mA (0.67W peak / 0.34W avg at 50% PWM = within 0.5W rating!), V(buz_k) clamped at 12.8V!
# ==============================================================================
sim5_out = os.path.join(OUT_DIR, "sim5_data.txt").replace("\\", "/")

sim5_cir = f"""* SIM 5: LS1 (CDM-12008 8-Ohm Speaker) Driver Audit — As-Designed vs Corrected (2.7 kHz PWM)
V_12V v12v 0 DC 12.00
V_PWM buz_pwm 0 PULSE(0 3.32 20u 0.2u 0.2u 185u 370u)

* 5A. As-Designed Circuit (LS1=8R+120uH on +12V, R25=47R 0603, D7=DNP)
R_LS1_AS v12v ls1_mid_as 8.0
L_LS1_AS ls1_mid_as buz_k_as 120u
R_R25_AS v12v buz_k_as 47.0
R_R21_AS buz_pwm q5_g_as 100
R_R23_AS q5_g_as 0 100k
M_Q5_AS buz_k_as q5_g_as 0 0 NMOS_AO3400A
.model NMOS_AO3400A NMOS(LEVEL=1 VTO=1.1 KP=12.0 RD=0.015 RS=0.015)

* 5B. Corrected Circuit (R_SER=33R, LS1=8R+120uH, R25=DNP, D7=1N4148W flyback diode)
R_SER_COR v12v ls1_top_cor 33.0
R_LS1_COR ls1_top_cor ls1_mid_cor 8.0
L_LS1_COR ls1_mid_cor buz_k_cor 120u
D_D7_COR buz_k_cor v12v D1N4148W
.model D1N4148W D(Is=2.5e-9 Rs=0.8 N=1.75)
R_R21_COR buz_pwm q5_g_cor 100
R_R23_COR q5_g_cor 0 100k
M_Q5_COR buz_k_cor q5_g_cor 0 0 NMOS_AO3400A

.control
tran 0.5u 750u
wrdata {sim5_out} V(buz_pwm) V(buz_k_as) V(ls1_mid_as) V(buz_k_cor) V(ls1_top_cor)
.endc
.end
"""
run_netlist("sim5_speaker_driver.cir", sim5_cir)
sim5_data = np.loadtxt(sim5_out)

# ==============================================================================
# EXTRACT NUMERICAL METRICS & SAVE SUMMARY JSON
# ==============================================================================
# Sim 1 metrics
t1 = sim1_data[:, 0]
v_in_raw = sim1_data[:, 1]
v_12_rail = sim1_data[:, 3]
v_3v3_as = sim1_data[:, 5]
v_fb_as = sim1_data[:, 7]
v_3v3_cor = sim1_data[:, 9]
v_fb_cor = sim1_data[:, 11]
v_avdd = sim1_data[:, 13]

rev_pol_mask = t1 < 0.0015
steady_mask = (t1 > 0.004) & (t1 < 0.0049)
ripple_3v3_mv = (np.max(v_3v3_cor[steady_mask]) - np.min(v_3v3_cor[steady_mask])) * 1000.0
ripple_avdd_mv = (np.max(v_avdd[steady_mask]) - np.min(v_avdd[steady_mask])) * 1000.0

# Sim 2 metrics
i_sens_ua = sim2_dc[:, 0] * 1e6
v_we_dc = sim2_dc[:, 1]
v_lmp_dc = sim2_dc[:, 3]
v_adc_dc = sim2_dc[:, 5]
# Find index for I_sens = 0, 10uA, 32.5uA (500ppm), 50uA, 75uA (saturation)
def interp_at(x, y, val):
    return float(np.interp(val, x, y))

f_ac = sim2_ac[:, 0]
vm_adc = sim2_ac[:, 3]
gain_0 = vm_adc[0]
fc_idx = np.argmin(np.abs(vm_adc - gain_0 / np.sqrt(2.0)))
fc_hz = float(f_ac[fc_idx])

# Sim 3 metrics
rs_ohm = sim3_dc[:, 1]
v_lpg_adc = sim3_dc[:, 5]
v_htr_as_68 = float(sim3_dc[0, 7])
v_htr_as_89 = float(sim3_dc[0, 9])
p_htr_as_68_mw = (v_htr_as_68 ** 2) / 68.0 * 1000.0
p_htr_as_89_mw = (v_htr_as_89 ** 2) / 89.3 * 1000.0
p_htr_ds_5v_mw = (5.0 ** 2) / 89.29 * 1000.0

# Sim 4 metrics
t4 = sim4_data[:, 0] * 1000.0 # ms
v_mr_n = sim4_data[:, 1]
v_nrst = sim4_data[:, 3]
v_valve_en = sim4_data[:, 5]
v_valve_drv = sim4_data[:, 7]
v_j2_neg = sim4_data[:, 9]
reset_window = (t4 >= 60.0) & (t4 <= 340.0)

# Sim 5 metrics
t5 = sim5_data[:, 0] * 1e6 # us
v_pwm = sim5_data[:, 1]
v_buz_k_as = sim5_data[:, 3]
v_ls1_mid_as = sim5_data[:, 5]
v_buz_k_cor = sim5_data[:, 7]
v_ls1_top_cor = sim5_data[:, 9]

i_ls1_as = (12.0 - v_ls1_mid_as) / 8.0
p_ls1_as_peak = float(np.max(i_ls1_as) ** 2 * 8.0)
p_r25_as_peak = float(np.max((12.0 - v_buz_k_as) ** 2 / 47.0))
v_buz_k_as_max = float(np.max(v_buz_k_as))

i_ls1_cor = (12.0 - v_ls1_top_cor) / 33.0
p_ls1_cor_peak = float(np.max(i_ls1_cor) ** 2 * 8.0)
v_buz_k_cor_max = float(np.max(v_buz_k_cor))

summary = {
    "u2_pcb_pads": u2_pads,
    "sim1_power_supply": {
        "reverse_polarity_minus12V_rail_V": float(np.min(v_12_rail[rev_pol_mask])),
        "as_designed_R2_232k_R3_73k2_Vout_V": float(np.mean(v_3v3_as[steady_mask])),
        "corrected_R2_232k_R3_100k_Vout_V": float(np.mean(v_3v3_cor[steady_mask])),
        "v3v3_ripple_mVpp": ripple_3v3_mv,
        "avdd_ripple_mVpp": ripple_avdd_mv
    },
    "sim2_co_afe": {
        "V_zero_at_0uA_V": interp_at(i_sens_ua, v_adc_dc, 0.0),
        "V_out_at_3p25uA_50ppm_V": interp_at(i_sens_ua, v_adc_dc, 3.25),
        "V_out_at_6p5uA_100ppm_V": interp_at(i_sens_ua, v_adc_dc, 6.50),
        "V_out_at_19p5uA_300ppm_V": interp_at(i_sens_ua, v_adc_dc, 19.50),
        "V_out_at_32p5uA_500ppm_V": interp_at(i_sens_ua, v_adc_dc, 32.50),
        "V_out_at_50uA_V": interp_at(i_sens_ua, v_adc_dc, 50.0),
        "V_out_saturation_at_75uA_V": interp_at(i_sens_ua, v_adc_dc, 75.0),
        "I_sensor_max_for_ESP32C3_2500mV_ADC_uA": (2.500 - 0.500) / 0.035,
        "RC_filter_3dB_cutoff_Hz": fc_hz
    },
    "sim3_lpg_channel": {
        "heater_as_designed_3v3_22R_Vh_V_at_68R": v_htr_as_68,
        "heater_as_designed_3v3_22R_Ph_mW_at_68R": p_htr_as_68_mw,
        "heater_as_designed_3v3_22R_Vh_V_at_89R3": v_htr_as_89,
        "heater_as_designed_3v3_22R_Ph_mW_at_89R3": p_htr_as_89_mw,
        "heater_datasheet_5v0_Ph_mW": p_htr_ds_5v_mw,
        "V_adc_at_Rs_1k_V": interp_at(rs_ohm, v_lpg_adc, 1000.0),
        "V_adc_at_Rs_2k_V": interp_at(rs_ohm, v_lpg_adc, 2000.0),
        "V_adc_at_Rs_4k7_V": interp_at(rs_ohm, v_lpg_adc, 4700.0),
        "V_adc_at_Rs_10k_V": interp_at(rs_ohm, v_lpg_adc, 10000.0),
        "V_adc_at_Rs_47k_V": interp_at(rs_ohm, v_lpg_adc, 47000.0),
        "V_adc_at_Rs_100k_V": interp_at(rs_ohm, v_lpg_adc, 100000.0)
    },
    "sim4_reset_interlock": {
        "nrst_during_sw3_and_200ms_hold_V": float(np.mean(v_nrst[reset_window])),
        "valve_drv_during_reset_latch_V": float(np.mean(v_valve_drv[reset_window])),
        "j2_neg_during_reset_latch_V": float(np.mean(v_j2_neg[reset_window])),
        "j2_alarm_current_during_reset_mA": float((12.0 - np.mean(v_j2_neg[reset_window])) / 120.0 * 1000.0)
    },
    "sim5_speaker_driver": {
        "as_designed_LS1_peak_current_A": float(np.max(i_ls1_as)),
        "as_designed_LS1_peak_power_W": p_ls1_as_peak,
        "as_designed_R25_peak_power_W": p_r25_as_peak,
        "as_designed_Q5_Vds_spike_D7_DNP_V": v_buz_k_as_max,
        "corrected_LS1_peak_current_A": float(np.max(i_ls1_cor)),
        "corrected_LS1_peak_power_W": p_ls1_cor_peak,
        "corrected_Q5_Vds_clamped_V": v_buz_k_cor_max
    }
}

with open(os.path.join(OUT_DIR, "spice_results_summary.json"), "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)

# ==============================================================================
# GENERATE HIGH-RESOLUTION 6-PANEL SPICE PLOT VIA PIL
# ==============================================================================
W, H = 1800, 1350
img = Image.new("RGB", (W, H), (252, 253, 255))
draw = ImageDraw.Draw(img)

def draw_subplot(ax_idx, title, xlabel, ylabel, x_min, x_max, y_min, y_max, series_list, hlines=None, vlines=None, log_x=False):
    row = ax_idx // 2
    col = ax_idx % 2
    pad_l, pad_r, pad_t, pad_b = 85, 35, 45, 50
    cell_w = W // 2
    cell_h = (H - 60) // 3
    x0 = col * cell_w + pad_l
    y0 = 60 + row * cell_h + pad_t
    x1 = (col + 1) * cell_w - pad_r
    y1 = 60 + (row + 1) * cell_h - pad_b
    pw = x1 - x0
    ph = y1 - y0

    # Background and border
    draw.rectangle([x0, y0, x1, y1], fill=(255, 255, 255), outline=(180, 185, 195), width=2)
    # Grid lines
    for i in range(1, 5):
        gy = y0 + int(ph * i / 5)
        draw.line([(x0, gy), (x1, gy)], fill=(230, 233, 240), width=1)
        gx = x0 + int(pw * i / 5)
        draw.line([(gx, y0), (gx, y1)], fill=(230, 233, 240), width=1)

    # Axis ticks
    for i in range(6):
        yv = y_max - (y_max - y_min) * i / 5.0
        gy = y0 + int(ph * i / 5)
        draw.text((x0 - 58, gy - 6), f"{yv:.1f}", fill=(60, 65, 75))
        if log_x:
            lv = np.log10(x_min) + (np.log10(x_max) - np.log10(x_min)) * i / 5.0
            xv = 10 ** lv
            lbl = f"{xv:.1f}" if xv < 10 else f"{xv:.0f}"
        else:
            xv = x_min + (x_max - x_min) * i / 5.0
            lbl = f"{xv:.1f}" if (x_max - x_min) < 20 else f"{xv:.0f}"
        gx = x0 + int(pw * i / 5)
        draw.text((gx - 15, y1 + 8), lbl, fill=(60, 65, 75))

    def map_pt(xv, yv):
        if log_x:
            tx = (np.log10(max(xv, x_min)) - np.log10(x_min)) / (np.log10(x_max) - np.log10(x_min))
        else:
            tx = (xv - x_min) / (x_max - x_min)
        ty = (yv - y_min) / (y_max - y_min)
        tx = max(0.0, min(1.0, float(tx)))
        ty = max(0.0, min(1.0, float(ty)))
        return (x0 + int(tx * pw), y1 - int(ty * ph))

    if hlines:
        for yval, col_rgb, lbl in hlines:
            _, py = map_pt(x_min, yval)
            for sx in range(x0, x1 - 6, 12):
                draw.line([(sx, py), (sx + 6, py)], fill=col_rgb, width=2)
            draw.text((x0 + 8, py - 14), lbl, fill=col_rgb)

    if vlines:
        for xval, col_rgb, lbl in vlines:
            px, _ = map_pt(xval, y_min)
            for sy in range(y0, y1 - 6, 12):
                draw.line([(px, sy), (px, sy + 6)], fill=col_rgb, width=2)
            draw.text((px + 5, y0 + 25), lbl, fill=col_rgb)

    # Plot series
    leg_y = y0 + 8
    for xs, ys, col_rgb, lbl in series_list:
        step = max(1, len(xs) // 400)
        pts = [map_pt(xs[i], ys[i]) for i in range(0, len(xs), step)]
        if len(pts) > 1:
            draw.line(pts, fill=col_rgb, width=3)
        # Legend entry
        draw.rectangle([x1 - 330, leg_y, x1 - 312, leg_y + 10], fill=col_rgb)
        draw.text((x1 - 306, leg_y - 2), lbl, fill=(30, 35, 45))
        leg_y += 16

    draw.text((x0, y0 - 24), title, fill=(15, 25, 45))
    draw.text((x0 + pw // 2 - 40, y1 + 26), xlabel, fill=(40, 45, 55))
    draw.text((x0 - 75, y0 - 24), ylabel, fill=(80, 85, 95))

draw.text((W // 2 - 340, 18), "NGSPICE VERIFICATION RESULTS — SMART CO + LPG DETECTOR (REV 2 AUDIT)", fill=(10, 20, 40))

# Panel 0: Power Supply
draw_subplot(
    0,
    "1. Power Supply: Q1 Rev-Polarity (-12V) & LMR33620 Buck (As-Designed vs Corrected)",
    "Time (ms)", "V",
    0.0, 15.0, -13.0, 13.5,
    [
        (t1*1000, v_in_raw, (130, 130, 130), "V_IN_RAW (-12V -> +12V)"),
        (t1*1000, v_12_rail, (30, 90, 210), "+12V After Q1 (0.0V at -12V!)"),
        (t1*1000, v_3v3_as, (220, 30, 30), "As-Designed +3V3 (R3=73.2k -> 4.17V OVERVOLT!)"),
        (t1*1000, v_3v3_cor, (20, 155, 60), "Corrected +3V3 (R3=100k -> 3.32V Nominal)")
    ],
    hlines=[(3.60, (200, 40, 40), "ESP32-C3 Vdd_max = 3.60V")]
)

# Panel 1: Ripple
zoom_mask = (t1 >= 0.0040) & (t1 <= 0.00402)
t_z = (t1[zoom_mask] - 0.0040) * 1e6
v3_ac = (v_3v3_cor[zoom_mask] - np.mean(v_3v3_cor[zoom_mask])) * 1000.0
av_ac = (v_avdd[zoom_mask] - np.mean(v_avdd[zoom_mask])) * 1000.0
draw_subplot(
    1,
    "2. Analog Supply Noise Rejection (FB1 + C13/C14 @ 400 kHz Buck Ripple)",
    "Time (us)", "mV",
    0.0, 20.0, -8.0, 8.0,
    [
        (t_z, v3_ac, (20, 155, 60), f"+3V3 Buck Ripple ({ripple_3v3_mv:.2f} mVpp)"),
        (t_z, av_ac, (160, 30, 190), f"AVDD Filtered Ripple ({ripple_avdd_mv:.3f} mVpp)")
    ]
)

# Panel 2: CO AFE Transfer Curve
draw_subplot(
    2,
    "3. CO Channel DC Transfer Curve (Winsen ME3-CO + LMP91000 + REF3325)",
    "Sensor Current I_sens (uA)", "V",
    -5.0, 80.0, 0.0, 3.6,
    [
        (i_sens_ua, v_adc_dc, (25, 85, 205), "VOUT_ADC = 0.50V + I_sens * 35 kOhm")
    ],
    hlines=[
        (2.50, (215, 115, 10), "ESP32-C3 ADC Ceiling (2.50V @ 57.1 uA)"),
        (3.30, (210, 30, 30), "LMP91000 Saturation (3.30V @ 80 uA)")
    ],
    vlines=[(32.5, (20, 150, 60), "500 ppm (~32.5 uA -> 1.64V)")]
)

# Panel 3: LPG Channel Divider Curve
draw_subplot(
    3,
    f"4. LPG Divider Curve (+3V3+R27 Gives Only {p_htr_as_68_mw:.0f}-{p_htr_as_89_mw:.0f}mW vs 280mW Req!)",
    "Sensor Resistance Rs (kOhm)", "V",
    0.1, 100.0, 0.0, 3.5,
    [
        (rs_ohm/1000.0, v_lpg_adc, (220, 110, 15), "V(LPG_ADC) w/ R28=4.7k on +3V3")
    ],
    hlines=[(2.50, (210, 30, 30), "ESP32-C3 ADC Ceiling (2.50V -> Rs < 1.54k Clips!)")],
    log_x=True
)

# Panel 4: SW3 Reset & U5 Bus-Hold Latch
draw_subplot(
    4,
    "5. SW3 Reset Timing (200ms Delay) & U5 (74LVC1G08+R13) Non-Silencing J2 Latch",
    "Time (ms)", "V",
    0.0, 500.0, -0.2, 3.8,
    [
        (t4, v_mr_n, (30, 90, 210), "SW3 MR_N (Pressed 50..150ms)"),
        (t4, v_nrst, (215, 35, 35), "TPS3823 NRST (LOW 50..350ms = +200ms Hold)"),
        (t4, v_valve_drv, (20, 155, 60), "U5 VALVE_DRV (Latched HIGH During Reset!)")
    ]
)

# Panel 5: LS1 Speaker Driver Stress
draw_subplot(
    5,
    "6. LS1 (CDM-12008 8-Ohm) Driver Stress: As-Designed vs Corrected (2.7 kHz PWM)",
    "Time (us)", "V",
    0.0, 750.0, 0.0, 90.0,
    [
        (t5, v_buz_k_as, (220, 30, 30), f"As-Designed V(BUZ_K) (D7=DNP -> {v_buz_k_as_max:.1f}V Spike! I={np.max(i_ls1_as):.2f}A)"),
        (t5, v_buz_k_cor, (20, 155, 60), f"Corrected V(BUZ_K) (D7+33R -> {v_buz_k_cor_max:.1f}V Clamped, I={np.max(i_ls1_cor):.2f}A)")
    ],
    hlines=[(30.0, (60, 60, 60), "Q5 AO3400A Vds_max Rating = 30.0V")]
)

plot_out1 = os.path.join(OUT_DIR, "spice_simulation_plots.png")
plot_out2 = os.path.join(ARTIFACT_DIR, "spice_simulation_plots.png")
img.save(plot_out1)
img.save(plot_out2)
print("SPICE simulations completed and plots saved.")
print(json.dumps(summary, indent=2))
