#include "lpg_sensor.h"
#include <math.h>

LpgReading LpgSensor::convert(uint32_t since_power_on_ms, float adc_mv) const {
    LpgReading r;
    r.mv = adc_mv;
    bool warm = since_power_on_ms < WARMUP_MS;
    if (adc_mv >= CEIL_MV) {           // very low Rs or short -> treat as gas present (fail-safe)
        r.status = warm ? LpgStatus::WARMUP : LpgStatus::OVERRANGE;
        r.pct_lel = warm ? 0.0f : 100.0f;
        return r;
    }
    if (adc_mv < OPEN_MV) {
        r.status = warm ? LpgStatus::WARMUP : LpgStatus::FAULT_OPEN;
        return r;
    }
    r.rs_kohm = RL_KOHM * (VCC_MV - adc_mv) / adc_mv;
    r.ratio = r.rs_kohm / r0_kohm;
    r.pct_lel = fitA * powf(r.ratio, fitB);
    if (r.pct_lel > 100.0f) r.pct_lel = 100.0f;
    r.status = warm ? LpgStatus::WARMUP : LpgStatus::OK;
    return r;
}

