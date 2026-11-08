// lpg_sensor.h — TGS2610 divider conversion (S2 SNS+ = +3V3, RL = R28 4.7k, R29 1k to GPIO2)
#pragma once
#include <stdint.h>

enum class LpgStatus : uint8_t { OK, WARMUP, FAULT_OPEN, OVERRANGE };

struct LpgReading {
    float mv = 0.0f;
    float rs_kohm = 0.0f;
    float ratio = 0.0f;        // Rs / R0
    float pct_lel = 0.0f;      // ESTIMATE - requires gas calibration
    LpgStatus status = LpgStatus::WARMUP;
};

class LpgSensor {
public:
    static constexpr float VCC_MV = 3315.0f;
    static constexpr float RL_KOHM = 4.7f;
    static constexpr float OPEN_MV = 20.0f;       // Rs > ~770 k after warm-up => open / heater dead
    static constexpr float CEIL_MV = 2450.0f;     // ADC ceiling (Rs < ~1.65 k) => fail-safe high
    static constexpr uint32_t WARMUP_MS = 180000; // TGS2610 initial action; Figaro recommends longer pre-heat
    // R0 = Rs at the calibration point (e.g. 1800 ppm iso-butane). PLACEHOLDER until calibrated.
    float r0_kohm = 3.0f;
    // Placeholder power-law fit pct_lel = A * ratio^B, ONLY for logic testing (not a datasheet curve)
    float fitA = 9.5f, fitB = -1.6f;

    LpgReading convert(uint32_t since_power_on_ms, float adc_mv) const;
};

