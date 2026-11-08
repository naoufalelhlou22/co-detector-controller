// alarm.h — safety state machine (hardware-independent, unit-tested on host)
#pragma once
#include <stdint.h>
#include "co_sensor.h"
#include "lpg_sensor.h"

enum class SysState : uint8_t {
    WARMUP, NORMAL, PRE_ALARM, ALARM_CO, ALARM_LPG, ALARM_DUAL, HUSHED, SELF_TEST, FAULT, RESTORED_ALARM
};
enum class BuzzPattern : uint8_t { OFF, ALARM_CO_T4, ALARM_LPG_T3, TEST, FAULT_CHIRP };

enum FaultBits : uint8_t {
    F_CO = 0x01, F_LPG = 0x02, F_OLED = 0x04, F_J2_OPEN = 0x08, F_AFE = 0x10
};

struct AlarmInputs {
    CoReading co;
    LpgReading lpg;
    bool testEvent = false;
    bool hushEvent = false;
    bool oledOk = true;
    bool j2LoadOk = true;      // VALVE_SENSE continuity check (only meaningful while J2 off)
};

struct AlarmOutputs {
    SysState state = SysState::WARMUP;
    bool red = false, yellow = false, blue = false, j2 = false, buzzer = false;
    BuzzPattern pattern = BuzzPattern::OFF;
    bool hushAccepted = false, hushRejected = false;
    uint8_t faults = 0;
};

// CO decision windows. Values follow the EN 50291-1 response table as commonly cited
// (30 ppm: no alarm < 120 min; 50 ppm: 60-90 min; 100 ppm: 10-40 min; 300 ppm: < 3 min).
// VERIFY against the purchased standard before certification testing.
struct CoPolicy {
    float band_hi = 300.0f; uint32_t t_hi_ms = 60u * 1000u;
    float band_mid = 100.0f; uint32_t t_mid_ms = 20u * 60u * 1000u;
    float band_lo = 50.0f; uint32_t t_lo_ms = 75u * 60u * 1000u;
    float clear_ppm = 30.0f; uint32_t clear_ms = 60u * 1000u;
    float prealarm_ppm = 30.0f;
};
struct LpgPolicy {
    float alarm_lel = 10.0f; uint32_t confirm_ms = 5000;      // set point: VERIFY vs EN 50194-1
    float no_hush_lel = 20.0f;
    float clear_lel = 5.0f; uint32_t clear_ms = 30000;
};

class AlarmController {
public:
    static constexpr uint32_t HUSH_MS = 5u * 60u * 1000u;      // placeholder - VERIFY vs standard
    static constexpr uint32_t TEST_MS = 3000;
    static constexpr uint32_t CHIRP_PERIOD_MS = 45000;
    static constexpr uint32_t RESTORE_MIN_MS = 30000;
    CoPolicy co; LpgPolicy lpg;
    bool selfTestDrivesJ2 = true;

    // latchedAtBoot: VALVE_EN read HIGH before the pin was configured (U5 latch held through reset)
    void begin(bool latchedAtBoot);
    AlarmOutputs step(uint32_t now_ms, uint32_t dt_ms, const AlarmInputs& in);

    // exposed for tests
    uint32_t coTimerHi() const { return tHi_; }

private:
    uint32_t tHi_ = 0, tMid_ = 0, tLo_ = 0, coClear_ = 0;
    bool coAlarm_ = false;
    uint32_t lpgConfirm_ = 0, lpgClear_ = 0;
    bool lpgAlarm_ = false;
    bool hush_ = false; uint32_t hushStart_ = 0;
    bool test_ = false; uint32_t testStart_ = 0;
    bool restored_ = false; uint32_t restoreStart_ = 0; bool restoreInit_ = false;
    uint32_t lastChirp_ = 0;
    static void acc(uint32_t& t, bool cond, uint32_t dt) { if (cond) t += dt; else t = (t > dt) ? t - dt : 0; }
};

