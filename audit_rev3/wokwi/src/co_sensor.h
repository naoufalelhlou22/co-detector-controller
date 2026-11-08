// co_sensor.h — ME3-CO + LMP91000 channel conversion and diagnostics (hardware-independent core)
#pragma once
#include <stdint.h>

enum class CoStatus : uint8_t { OK, WARMUP, FAULT_AFE_I2C, FAULT_NO_CELL, FAULT_UNDERRANGE, OVERRANGE };

struct CoReading {
    float mv = 500.0f;
    float ua = 0.0f;
    float ppm = 0.0f;
    CoStatus status = CoStatus::WARMUP;
};

class CoSensor {
public:
    // Rev2 values: REF3325 2.500 V, LMP91000 INT_Z = 20 % -> 500 mV, RTIA register = 35 k
    static constexpr float VZERO_MV = 500.0f;
    static constexpr float RTIA_KOHM = 35.0f;
    // Winsen ME3-CO datasheet: 0.070 +/- 0.015 uA/ppm. Per-unit value MUST come from gas calibration.
    float sensitivity_ua_per_ppm = 0.070f;
    float zero_offset_mv = 0.0f;               // from clean-air calibration
    static constexpr float ADC_CEIL_MV = 2450.0f;  // ESP32-C3 ADC 12 dB usable ceiling (~2.5 V)
    static constexpr float UNDER_MV = 400.0f;      // < -2.9 uA => reversed / defective cell
    static constexpr uint32_t WARMUP_MS = 60000;

    void setAfeOk(bool ok) { afeOk_ = ok; }
    // Result of the periodic LMP91000 bias-step test (a missing cell cannot be seen in the DC value!)
    void setCellPresenceResult(bool present) { cellPresent_ = present; }
    CoReading convert(uint32_t uptime_ms, float adc_mv) const;
    // Bias-pulse evaluation: deviation (mV) observed at VOUT after a +25 mV bias step
    static bool evaluateBiasPulse(float peak_deviation_mv) { return peak_deviation_mv > 20.0f; }

private:
    bool afeOk_ = true;
    bool cellPresent_ = true;
};

