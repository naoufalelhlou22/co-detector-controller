// power_manager.h — reset-reason handling. The TGS2610 heater and the LMP91000 stay powered across an
// MCU reset (SW3 / watchdog), so sensor warm-up is only required after a real power-on.
#pragma once
#include <stdint.h>

enum class ResetCause : uint8_t { POWER_ON, EXTERNAL_PIN /*SW3 or TPS3823 WDT*/, SOFTWARE, BROWNOUT };

struct BootContext {
    ResetCause cause = ResetCause::POWER_ON;
    bool valveLatchHigh = false;      // VALVE_EN level sampled BEFORE pinMode(OUTPUT)
    bool sensorsWarm() const { return cause == ResetCause::EXTERNAL_PIN || cause == ResetCause::SOFTWARE; }
};

