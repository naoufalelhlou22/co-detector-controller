#include "alarm.h"

void AlarmController::begin(bool latchedAtBoot) {
    *this = AlarmController();
    restored_ = latchedAtBoot;
}

AlarmOutputs AlarmController::step(uint32_t now, uint32_t dt, const AlarmInputs& in) {
    AlarmOutputs o;
    if (restored_ && !restoreInit_) { restoreStart_ = now; restoreInit_ = true; }

    // ---------------- faults ----------------
    bool coFault = in.co.status == CoStatus::FAULT_NO_CELL || in.co.status == CoStatus::FAULT_UNDERRANGE ||
                   in.co.status == CoStatus::FAULT_AFE_I2C;
    bool lpgFault = in.lpg.status == LpgStatus::FAULT_OPEN;
    if (coFault) o.faults |= F_CO;
    if (in.co.status == CoStatus::FAULT_AFE_I2C) o.faults |= F_AFE;
    if (lpgFault) o.faults |= F_LPG;
    if (!in.oledOk) o.faults |= F_OLED;
    if (!in.j2LoadOk) o.faults |= F_J2_OPEN;

    // ---------------- CO (time-weighted) ----------------
    bool coValid = in.co.status == CoStatus::OK || in.co.status == CoStatus::OVERRANGE;
    float ppm = coValid ? in.co.ppm : 0.0f;
    acc(tHi_, ppm >= co.band_hi, dt);
    acc(tMid_, ppm >= co.band_mid, dt);
    acc(tLo_, ppm >= co.band_lo, dt);
    if (in.co.status == CoStatus::OVERRANGE || tHi_ >= co.t_hi_ms || tMid_ >= co.t_mid_ms || tLo_ >= co.t_lo_ms)
        coAlarm_ = true;
    if (coAlarm_) {
        coClear_ = (ppm < co.clear_ppm) ? coClear_ + dt : 0;
        if (coClear_ >= co.clear_ms) { coAlarm_ = false; tHi_ = tMid_ = tLo_ = 0; coClear_ = 0; }
    }

    // ---------------- LPG ----------------
    bool lpgValid = in.lpg.status == LpgStatus::OK || in.lpg.status == LpgStatus::OVERRANGE;
    float lel = lpgValid ? in.lpg.pct_lel : 0.0f;
    lpgConfirm_ = (lel >= lpg.alarm_lel) ? lpgConfirm_ + dt : 0;
    if (lpgConfirm_ >= lpg.confirm_ms || in.lpg.status == LpgStatus::OVERRANGE) lpgAlarm_ = true;
    if (lpgAlarm_) {
        lpgClear_ = (lel < lpg.clear_lel) ? lpgClear_ + dt : 0;
        if (lpgClear_ >= lpg.clear_ms) { lpgAlarm_ = false; lpgClear_ = 0; }
    }

    // ---------------- restored alarm after SW3 / watchdog reset ----------------
    bool anyAlarm = coAlarm_ || lpgAlarm_;
    if (restored_) {
        bool sensorsValid = coValid && (lpgValid || in.lpg.status == LpgStatus::WARMUP);
        if ((now - restoreStart_) >= RESTORE_MIN_MS && sensorsValid && !anyAlarm &&
            ppm < co.clear_ppm && lel < lpg.clear_lel)
            restored_ = false;
    }

    // ---------------- hush ----------------
    bool critical = (coAlarm_ && lpgAlarm_) || ppm >= co.band_hi || lel >= lpg.no_hush_lel ||
                    in.co.status == CoStatus::OVERRANGE || in.lpg.status == LpgStatus::OVERRANGE;
    if (in.hushEvent) {
        if (anyAlarm && !critical) { hush_ = true; hushStart_ = now; o.hushAccepted = true; }
        else if (anyAlarm) o.hushRejected = true;
    }
    if (hush_ && ((now - hushStart_) >= HUSH_MS || critical || !anyAlarm)) hush_ = false;

    // ---------------- self test (electronic only - does NOT prove gas response) ----------------
    if (in.testEvent && !anyAlarm && !restored_) { test_ = true; testStart_ = now; }
    if (test_ && (now - testStart_) >= TEST_MS) test_ = false;

    // ---------------- outputs ----------------
    if (anyAlarm || restored_) {
        o.state = (coAlarm_ && lpgAlarm_) ? SysState::ALARM_DUAL
                : coAlarm_ ? (hush_ ? SysState::HUSHED : SysState::ALARM_CO)
                : lpgAlarm_ ? (hush_ ? SysState::HUSHED : SysState::ALARM_LPG)
                : SysState::RESTORED_ALARM;
        o.red = true;
        o.j2 = true;                      // external output is never hushed
        o.buzzer = !hush_;
        o.pattern = !o.buzzer ? BuzzPattern::OFF : (lpgAlarm_ && !coAlarm_) ? BuzzPattern::ALARM_LPG_T3 : BuzzPattern::ALARM_CO_T4;
    } else if (test_) {
        o.state = SysState::SELF_TEST;
        o.red = o.yellow = o.buzzer = true;
        o.j2 = selfTestDrivesJ2;
        o.pattern = BuzzPattern::TEST;
    } else if (o.faults & (F_CO | F_LPG | F_AFE)) {
        o.state = SysState::FAULT;
        o.yellow = true;
        if (now - lastChirp_ >= CHIRP_PERIOD_MS || lastChirp_ == 0) { lastChirp_ = now ? now : 1; o.buzzer = true; o.pattern = BuzzPattern::FAULT_CHIRP; }
    } else if (in.co.status == CoStatus::WARMUP || in.lpg.status == LpgStatus::WARMUP) {
        o.state = SysState::WARMUP;
        o.yellow = true;
    } else if (ppm >= co.prealarm_ppm || lel >= lpg.clear_lel) {
        o.state = SysState::PRE_ALARM;
        o.red = ((now / 1000) % 2) == 0;  // slow red blink
    } else {
        o.state = SysState::NORMAL;
    }
    if (o.faults & (F_OLED | F_J2_OPEN)) o.yellow = true;   // minor faults: indicate, no chirp
    return o;
}

