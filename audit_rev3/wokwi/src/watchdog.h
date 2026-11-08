// watchdog.h — TPS3823 WDI kicker. Kicks only when the main loop reports every subsystem alive.
// TPS3823 timeout: 1.6 s typical (datasheet min/max range must be respected -> kick every <= 500 ms).
#pragma once
#include <stdint.h>

class WdiKicker {
public:
    static constexpr uint32_t KICK_PERIOD_MS = 500;
    // returns the WDI level to drive
    bool step(uint32_t now_ms, bool loopHealthy) {
        if (loopHealthy && (now_ms - last_) >= KICK_PERIOD_MS) { level_ = !level_; last_ = now_ms; }
        return level_;
    }
private:
    uint32_t last_ = 0;
    bool level_ = false;
};

