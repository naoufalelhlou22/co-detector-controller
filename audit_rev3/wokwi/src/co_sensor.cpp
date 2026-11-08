#include "co_sensor.h"

CoReading CoSensor::convert(uint32_t uptime_ms, float adc_mv) const {
    CoReading r;
    r.mv = adc_mv;
    if (!afeOk_) { r.status = CoStatus::FAULT_AFE_I2C; return r; }
    if (!cellPresent_) { r.status = CoStatus::FAULT_NO_CELL; return r; }
    if (adc_mv < UNDER_MV) { r.status = CoStatus::FAULT_UNDERRANGE; return r; }
    float d = adc_mv - VZERO_MV - zero_offset_mv;
    if (d < 0.0f) d = 0.0f;
    r.ua = d / RTIA_KOHM;                       // mV / kOhm = uA
    r.ppm = r.ua / sensitivity_ua_per_ppm;
    if (adc_mv >= ADC_CEIL_MV) { r.status = CoStatus::OVERRANGE; r.ppm = 999.0f; return r; }  // fail-safe high
    r.status = (uptime_ms < WARMUP_MS) ? CoStatus::WARMUP : CoStatus::OK;
    return r;
}

