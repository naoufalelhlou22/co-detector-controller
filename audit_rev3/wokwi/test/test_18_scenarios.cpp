// test_18_scenarios.cpp — Host-compiled verification of the alarm state machine, sensor conversion,
// button handling, and latch behaviour for all 18 Master-Prompt-required scenarios.
// Compiled with: zig cc -std=c++17 -o test_18.exe test_18_scenarios.cpp ../src/co_sensor.cpp ../src/lpg_sensor.cpp ../src/buttons.cpp ../src/alarm.cpp
// No Arduino.h, no ESP-IDF, no Wokwi needed — pure logic test on the host.

#include <cstdio>
#include <cstdlib>
#include <cmath>
#include <cstring>
#include "../src/co_sensor.h"
#include "../src/lpg_sensor.h"
#include "../src/buttons.h"
#include "../src/alarm.h"
#include "../src/watchdog.h"
#include "../src/power_manager.h"

static int pass_count = 0, fail_count = 0;
#define CHECK(cond, msg) do { \
    if (cond) { pass_count++; } \
    else { fail_count++; printf("  [FAIL] %s (line %d)\n", msg, __LINE__); } \
} while(0)

// Helper: run the alarm controller for `dur_ms` in `dt`-ms steps, with fixed sensor readings.
static AlarmOutputs runFor(AlarmController& ac, uint32_t& now, uint32_t dur_ms, uint32_t dt,
                           const AlarmInputs& in) {
    AlarmOutputs last;
    uint32_t end = now + dur_ms;
    while (now < end) {
        last = ac.step(now, dt, in);
        now += dt;
    }
    return last;
}

// ===================== SCENARIO  1: Normal cold startup =====================
static void scenario_01() {
    printf("S01: Normal cold startup (power-on, warmup -> normal)\n");
    AlarmController ac; ac.begin(false);
    CoSensor co; LpgSensor lpg;
    uint32_t now = 0;

    // During warm-up (< 60 s for CO, < 180 s for LPG)
    AlarmInputs in;
    in.co = co.convert(1000, 500.0f);        // clean air
    in.lpg = lpg.convert(1000, 302.0f);      // cold sensor, Rs ~ 47 kOhm
    auto o = ac.step(now, 100, in);
    CHECK(o.state == SysState::WARMUP, "Initial state = WARMUP");
    CHECK(o.yellow, "Yellow LED on during warmup");
    CHECK(!o.red, "Red LED off during warmup");
    CHECK(!o.buzzer, "Buzzer off during warmup");

    // After 180 s both channels warm
    now = 181000;
    in.co = co.convert(now, 505.0f);
    in.lpg = lpg.convert(now, 302.0f);
    o = ac.step(now, 100, in);
    CHECK(o.state == SysState::NORMAL, "State = NORMAL after warmup");
    CHECK(!o.red && !o.yellow && !o.buzzer, "All indicators off in NORMAL");
}

// ===================== SCENARIO  2: Normal/elevated CO =====================
static void scenario_02() {
    printf("S02: Elevated CO (50 ppm sustained -> alarm after ~75 min accumulator)\n");
    AlarmController ac; ac.begin(false);
    CoSensor co; LpgSensor lpg;
    uint32_t now = 200000; // past warmup

    AlarmInputs in;
    in.co = co.convert(now, 500.0f + 50.0f * 0.070f * 35.0f); // 50 ppm typ -> ~622 mV
    in.lpg = lpg.convert(now, 302.0f);

    // Run for 74 minutes — should NOT alarm yet (EN 50291-1: 60-90 min window)
    auto o = runFor(ac, now, 74u * 60000u, 500, in);
    CHECK(o.state != SysState::ALARM_CO, "Not alarmed at 74 min for 50 ppm");

    // Run 2 more minutes — accumulator should trip
    o = runFor(ac, now, 2u * 60000u, 500, in);
    CHECK(o.state == SysState::ALARM_CO || o.state == SysState::HUSHED, "CO alarm at ~76 min for 50 ppm");
    CHECK(o.red, "Red LED on during CO alarm");
    CHECK(o.j2, "J2 external alarm active");
    CHECK(o.buzzer, "Buzzer active");
}

// ===================== SCENARIO  3: High CO (300 ppm -> alarm within 60 s) =====================
static void scenario_03() {
    printf("S03: High CO 300 ppm -> alarm within policy window\n");
    AlarmController ac; ac.begin(false);
    CoSensor co; LpgSensor lpg;
    uint32_t now = 200000;

    AlarmInputs in;
    float mv = 500.0f + 300.0f * 0.070f * 35.0f; // 1235 mV
    in.co = co.convert(now, mv);
    in.lpg = lpg.convert(now, 302.0f);

    auto o = runFor(ac, now, 61000, 200, in);
    CHECK(o.state == SysState::ALARM_CO, "CO alarm within 61 s at 300 ppm");
    CHECK(o.buzzer && o.j2, "Buzzer + J2 active");
}

// ===================== SCENARIO  4: Normal/elevated LPG =====================
static void scenario_04() {
    printf("S04: LPG alarm (>10%% LEL sustained for 5 s)\n");
    AlarmController ac; ac.begin(false);
    CoSensor co; LpgSensor lpg;
    uint32_t now = 200000;

    // Rs ~ 1.5 kOhm -> V ~ VCC * RL/(Rs+RL) = 3315 * 4.7 / 6.2 = 2513 mV -> high %LEL
    AlarmInputs in;
    in.co = co.convert(now, 502.0f);
    in.lpg = lpg.convert(now, 2200.0f); // Rs ~2.33 kOhm
    CHECK(in.lpg.pct_lel > 10.0f, "LPG reading > 10% LEL");

    auto o = runFor(ac, now, 6000, 200, in);
    CHECK(o.state == SysState::ALARM_LPG, "LPG alarm after 6 s confirmation");
    CHECK(o.j2, "J2 active during LPG alarm");
}

// ===================== SCENARIO  5: Simultaneous CO + LPG =====================
static void scenario_05() {
    printf("S05: Simultaneous CO + LPG alarm -> ALARM_DUAL, hush rejected\n");
    AlarmController ac; ac.begin(false);
    CoSensor co; LpgSensor lpg;
    uint32_t now = 200000;

    AlarmInputs in;
    in.co = co.convert(now, 1235.0f);  // 300 ppm
    in.lpg = lpg.convert(now, 2200.0f);

    auto o = runFor(ac, now, 62000, 200, in);
    CHECK(o.state == SysState::ALARM_DUAL, "ALARM_DUAL state");

    in.hushEvent = true;
    o = ac.step(now, 200, in);
    CHECK(o.hushRejected, "Hush rejected during dual alarm");
    CHECK(o.buzzer, "Buzzer cannot be silenced");
}

// ===================== SCENARIO  6: CO sensor disconnected =====================
static void scenario_06() {
    printf("S06: CO sensor disconnected (open cell)\n");
    AlarmController ac; ac.begin(false);
    CoSensor co; LpgSensor lpg;
    uint32_t now = 200000;

    // Open cell: LMP91000 output = Vzero = 500 mV (same as 0 ppm!)
    // DC reading alone cannot distinguish. Bias-pulse diagnostic detects it.
    co.setCellPresenceResult(false);
    AlarmInputs in;
    in.co = co.convert(now, 500.0f);
    in.lpg = lpg.convert(now, 302.0f);

    CHECK(in.co.status == CoStatus::FAULT_NO_CELL, "Status = FAULT_NO_CELL after bias-pulse fail");

    auto o = ac.step(now, 200, in);
    CHECK(o.state == SysState::FAULT, "State = FAULT");
    CHECK(o.faults & F_CO, "CO fault bit set");
    CHECK(o.yellow, "Yellow LED on for fault");
}

// ===================== SCENARIO  7: LPG sensor disconnected (open circuit) =====================
static void scenario_07() {
    printf("S07: LPG sensor disconnected (Rs -> infinity, V_ADC ~ 0)\n");
    AlarmController ac; ac.begin(false);
    CoSensor co; LpgSensor lpg;
    uint32_t now = 200000;

    AlarmInputs in;
    in.co = co.convert(now, 502.0f);
    in.lpg = lpg.convert(now, 5.0f);  // < 20 mV -> FAULT_OPEN
    CHECK(in.lpg.status == LpgStatus::FAULT_OPEN, "LPG FAULT_OPEN at 5 mV");

    auto o = ac.step(now, 200, in);
    CHECK(o.state == SysState::FAULT, "FAULT state");
    CHECK(o.faults & F_LPG, "LPG fault bit set");
}

// ===================== SCENARIO  8: CO out-of-range (ADC saturation) =====================
static void scenario_08() {
    printf("S08: CO out-of-range (ADC saturation > 2450 mV) -> overrange alarm\n");
    AlarmController ac; ac.begin(false);
    CoSensor co; LpgSensor lpg;
    uint32_t now = 200000;

    AlarmInputs in;
    in.co = co.convert(now, 2600.0f); // saturated
    in.lpg = lpg.convert(now, 302.0f);
    CHECK(in.co.status == CoStatus::OVERRANGE, "OVERRANGE status");
    CHECK(in.co.ppm >= 999.0f, "ppm capped at 999");

    auto o = ac.step(now, 200, in);
    // Overrange triggers immediate CO alarm (fail-safe)
    CHECK(o.state == SysState::ALARM_CO || o.state == SysState::ALARM_DUAL, "Alarm on overrange");
    CHECK(o.j2, "J2 active");
}

// ===================== SCENARIO  9: LPG ADC clipping (Rs very low) =====================
static void scenario_09() {
    printf("S09: LPG ADC clipping (V > 2450 mV, Rs < ~1.65 kOhm)\n");
    AlarmController ac; ac.begin(false);
    CoSensor co; LpgSensor lpg;
    uint32_t now = 200000;

    AlarmInputs in;
    in.co = co.convert(now, 502.0f);
    in.lpg = lpg.convert(now, 2600.0f); // clipped
    CHECK(in.lpg.status == LpgStatus::OVERRANGE, "OVERRANGE status");

    auto o = ac.step(now, 200, in);
    CHECK(o.state == SysState::ALARM_LPG || o.state == SysState::ALARM_DUAL, "Alarm on LPG overrange");
}

// ===================== SCENARIO 10: OLED I2C failure =====================
static void scenario_10() {
    printf("S10: OLED I2C failure (non-blocking, safety loop continues)\n");
    AlarmController ac; ac.begin(false);
    CoSensor co; LpgSensor lpg;
    uint32_t now = 200000;

    AlarmInputs in;
    in.co = co.convert(now, 502.0f);
    in.lpg = lpg.convert(now, 302.0f);
    in.oledOk = false;

    auto o = ac.step(now, 200, in);
    CHECK(o.state == SysState::NORMAL, "State stays NORMAL (OLED failure is not a gas safety fault)");
    CHECK(o.faults & F_OLED, "OLED fault bit set");
    CHECK(o.yellow, "Yellow LED indicates minor fault");
    CHECK(!o.buzzer, "No buzzer chirp for OLED-only fault");
}

// ===================== SCENARIO 11: Button TEST press + self-test =====================
static void scenario_11() {
    printf("S11: SW1 TEST button press -> 3 s self-test cycle\n");
    AlarmController ac; ac.begin(false);
    CoSensor co; LpgSensor lpg;
    uint32_t now = 200000;

    AlarmInputs in;
    in.co = co.convert(now, 502.0f);
    in.lpg = lpg.convert(now, 302.0f);
    in.testEvent = true;

    auto o = ac.step(now, 200, in); now += 200;
    CHECK(o.state == SysState::SELF_TEST, "SELF_TEST state");
    CHECK(o.red && o.yellow && o.buzzer, "Red + Yellow + Buzzer during self-test");
    CHECK(o.j2, "J2 driven during self-test");

    in.testEvent = false;
    o = runFor(ac, now, 3200, 200, in);
    CHECK(o.state == SysState::NORMAL, "Returns to NORMAL after 3 s");
}

// ===================== SCENARIO 12: HUSH during alarm + expiration =====================
static void scenario_12() {
    printf("S12: Hush during non-critical CO alarm (100 ppm), then expiration\n");
    AlarmController ac; ac.begin(false);
    CoSensor co; LpgSensor lpg;
    uint32_t now = 200000;

    // Trigger CO alarm at 100 ppm (non-critical, eligible for Hush)
    // 100 ppm -> ~745 mV; t_mid is 20 min -> run 21 min
    AlarmInputs in;
    in.co = co.convert(now, 500.0f + 100.0f * 0.070f * 35.0f);
    in.lpg = lpg.convert(now, 302.0f);
    runFor(ac, now, 21u * 60000u, 500, in);

    // Hush
    in.hushEvent = true;
    auto o = ac.step(now, 200, in); now += 200;
    CHECK(o.hushAccepted, "Hush accepted");
    CHECK(o.state == SysState::HUSHED, "State = HUSHED");
    CHECK(!o.buzzer, "Buzzer silenced");
    CHECK(o.j2, "J2 stays active while hushed");

    in.hushEvent = false;
    // Run until hush expires (5 min = 300 s)
    o = runFor(ac, now, 301000, 500, in);
    CHECK(o.state == SysState::ALARM_CO, "Alarm resumes after hush expiration");
    CHECK(o.buzzer, "Buzzer resumes");
}

// ===================== SCENARIO 13: Hardware reset (SW3) with active alarm =====================
static void scenario_13() {
    printf("S13: SW3 hardware reset during active alarm -> U5 latch holds J2\n");
    // Pre-reset: alarm active, VALVE_EN = HIGH, J2 = ON.
    // SW3 asserts MR_N -> TPS3823 holds NRST low -> ESP32 resets -> GPIO6 Hi-Z.
    // U5 + R13 latch keeps VALVE_DRV HIGH (proven by SPICE sim4a).
    // After boot: firmware reads GPIO6 = HIGH before configuring it as output.
    AlarmController ac; ac.begin(true);  // latchedAtBoot = true
    CoSensor co; LpgSensor lpg;
    uint32_t now = 0;

    AlarmInputs in;
    in.co = co.convert(now, 502.0f);   // clean air after reset
    in.lpg = lpg.convert(now, 302.0f);

    auto o = ac.step(now, 200, in);
    CHECK(o.state == SysState::RESTORED_ALARM, "RESTORED_ALARM state on boot");
    CHECK(o.j2, "J2 held ON via restored alarm");
    CHECK(o.red, "Red LED on during restored alarm");

    // After sensors warm up and confirm clean air for >= 30 s, alarm clears
    now = 200000;
    in.co = co.convert(now, 502.0f);
    in.lpg = lpg.convert(now, 302.0f);
    o = runFor(ac, now, 35000, 500, in);
    CHECK(o.state == SysState::NORMAL || o.state == SysState::WARMUP, "Alarm cleared after clean-air confirmation");
    CHECK(!o.j2, "J2 released after clear");
}

// ===================== SCENARIO 14: MCU reboot (watchdog reset, clean air) =====================
static void scenario_14() {
    printf("S14: Watchdog reset with no alarm -> boot to WARMUP/NORMAL\n");
    BootContext ctx;
    ctx.cause = ResetCause::EXTERNAL_PIN;
    ctx.valveLatchHigh = false;

    CHECK(ctx.sensorsWarm(), "sensorsWarm() = true for watchdog/SW3 reset");

    AlarmController ac; ac.begin(false);
    CoSensor co; LpgSensor lpg;
    uint32_t now = 0;

    AlarmInputs in;
    in.co = co.convert(now, 502.0f);
    in.lpg = lpg.convert(now, 302.0f);

    auto o = ac.step(now, 200, in);
    CHECK(o.state == SysState::WARMUP, "Starts in WARMUP even with warm sensors (firmware timer resets)");
    CHECK(!o.j2, "J2 off (no latch)");
}

// ===================== SCENARIO 15: Power interruption (brownout) =====================
static void scenario_15() {
    printf("S15: Power interruption -> cold boot, full warmup required\n");
    BootContext ctx;
    ctx.cause = ResetCause::BROWNOUT;
    ctx.valveLatchHigh = false;

    CHECK(!ctx.sensorsWarm(), "sensorsWarm() = false for brownout");

    AlarmController ac; ac.begin(false);
    CoSensor co; LpgSensor lpg;
    uint32_t now = 0;

    AlarmInputs in;
    in.co = co.convert(now, 500.0f);
    in.lpg = lpg.convert(now, 5.0f);   // LPG heater cold, sensor may read open

    auto o = ac.step(now, 200, in);
    CHECK(o.state == SysState::WARMUP, "WARMUP after brownout");
    CHECK(!o.j2, "No false alarm from cold sensor");
}

// ===================== SCENARIO 16: Recovery after alarm -> clean air =====================
static void scenario_16() {
    printf("S16: Recovery: alarm -> clean air -> auto-clear\n");
    AlarmController ac; ac.begin(false);
    CoSensor co; LpgSensor lpg;
    uint32_t now = 200000;

    // Trigger CO alarm
    AlarmInputs in;
    in.co = co.convert(now, 1235.0f);
    in.lpg = lpg.convert(now, 302.0f);
    runFor(ac, now, 62000, 200, in);

    // Switch to clean air
    in.co = co.convert(now, 502.0f);
    auto o = runFor(ac, now, 62000, 200, in);
    CHECK(o.state == SysState::NORMAL || o.state == SysState::PRE_ALARM, "Alarm auto-cleared after clean air hold");
    CHECK(!o.j2, "J2 released");
    CHECK(!o.buzzer, "Buzzer off");
}

// ===================== SCENARIO 17: GPIO10 shared pin (D8 + SW1) =====================
static void scenario_17() {
    printf("S17: GPIO10 shared pin — D8 LED lit, SW1 must still be readable\n");
    Buttons btn;

    // D8 lit (yellow fault LED commanded ON). Pin is sinking current.
    // At t=0: sinking phase. SW1 pressed (pin reads LOW) but sample is invalid during sink.
    uint32_t t = 0;
    bool sink = btn.gpio10Sink(t, true);
    CHECK(sink, "GPIO10 sinking at t=0 (D8 lit)");

    // Advance to release window
    t = 47500; // just past sink phase in 50 ms cycle (D8_PERIOD = 50000, D8_RELEASE = 3000)
    sink = btn.gpio10Sink(t, true);
    CHECK(!sink, "GPIO10 high-Z in release window");

    // Wait for settle (2 ms)
    t += 2500;
    auto ev = btn.update(t, true, false); // SW1 pressed
    // Debounce needs 30 ms, so not yet triggered
    CHECK(!ev.test, "Not triggered yet (debounce pending)");

    // Continue holding SW1 down across multiple D8 PWM cycles (100 ms in 1 ms steps)
    for (int i = 0; i < 100; i++) {
        t += 1000; // 1 ms steps
        btn.gpio10Sink(t, true);
        auto e = btn.update(t, true, false);
        if (e.test) ev.test = true;
    }
    CHECK(ev.test, "SW1 detected through D8 release windows after debounce");
}

// ===================== SCENARIO 18: WDI watchdog kicker =====================
static void scenario_18() {
    printf("S18: WDI kicker — toggles every 500 ms when healthy, stops when unhealthy\n");
    WdiKicker wdi;
    bool v0 = wdi.step(0, true);
    bool v500 = wdi.step(500, true);
    CHECK(v0 != v500, "WDI toggles at 500 ms");

    bool v1000 = wdi.step(1000, true);
    CHECK(v500 != v1000, "WDI toggles again at 1000 ms");

    // Unhealthy: no toggle
    bool v1500 = wdi.step(1500, false);
    CHECK(v1000 == v1500, "WDI does NOT toggle when unhealthy");

    bool v2000 = wdi.step(2000, false);
    CHECK(v1500 == v2000, "Still frozen at 2000 ms");

    // This means TPS3823 watchdog will time out (1.6 s typ) and assert NRST -> hardware reset.
}

int main() {
    printf("=== Smart CO+LPG Detector — 18-Scenario Firmware Verification ===\n\n");
    scenario_01();
    scenario_02();
    scenario_03();
    scenario_04();
    scenario_05();
    scenario_06();
    scenario_07();
    scenario_08();
    scenario_09();
    scenario_10();
    scenario_11();
    scenario_12();
    scenario_13();
    scenario_14();
    scenario_15();
    scenario_16();
    scenario_17();
    scenario_18();

    printf("\n=== RESULTS: %d PASSED, %d FAILED out of %d total ===\n",
           pass_count, fail_count, pass_count + fail_count);
    return fail_count > 0 ? 1 : 0;
}

