// pins.h — GPIO map taken verbatim from the Rev2 KiCad netlist export
// (audit_rev3/netlist/connectivity.txt, symbol U1 ESP32-C3-MINI-1).
#pragma once

namespace pins {
constexpr int VOUT_ADC    = 0;   // U1.12  ADC1_CH0  <- LMP91000 VOUT via R11/C17
constexpr int VALVE_SENSE = 1;   // U1.13  ADC1_CH1  <- J2 continuity divider R16/R17
constexpr int LPG_ADC     = 2;   // U1.5   ADC1_CH2  <- TGS2610 divider  (STRAPPING PIN! see audit H-02)
constexpr int BUZZER      = 3;   // U1.6   -> R23 -> Q5 gate (LS1)
constexpr int I2C_SDA     = 4;   // U1.18  OLED J4 + LMP91000 (0x48)
constexpr int I2C_SCL     = 5;   // U1.19
constexpr int VALVE_EN    = 6;   // U1.20  -> U5 A=B (bus-hold latch with R13) -> Q2 -> J2
constexpr int WDI         = 7;   // U1.21  -> TPS3823 WDI (watchdog ACTIVE once driven)
constexpr int HUSH_N      = 8;   // U1.22  SW2, R7 pull-up (strapping pin, high = OK)
constexpr int BOOT_N      = 9;   // U1.23  TP10 service pad only
constexpr int TEST_N_D8   = 10;  // U1.16  SW1 to GND  AND  D8 (yellow) cathode -> OPEN-DRAIN ONLY
constexpr int LED_RED     = 18;  // U1.26  D4 via R19 (USB D-; no USB used on this board)
constexpr int LED_BLU     = 19;  // U1.27  Q4 -> D6 (USB D+; ROM enables D+ pull-up at boot -> D6 glows until init)
// GPIO20/21 = UART0 on J3. LMP91000 MENB is hard-wired to AGND (always enabled) - no GPIO.
}  // namespace pins

