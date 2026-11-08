// buttons.h — SW1 (GPIO10, shared with D8 open-drain LED) and SW2 (GPIO8) handling.
// Time base is MICROSECONDS so the D8/TEST_N RC recovery (SPICE sim4b: 0.78 ms to VIH) can be respected.
#pragma once
#include <stdint.h>

struct ButtonEvents { bool test = false; bool hush = false; };

class Buttons {
public:
    static constexpr uint32_t DEBOUNCE_US = 30000;     // 30 ms stable level
    static constexpr uint32_t D8_PERIOD_US = 50000;    // D8 sampling cycle while lit
    static constexpr uint32_t D8_RELEASE_US = 3000;    // high-Z window per cycle (D8 dark 6 % -> invisible)
    static constexpr uint32_t SETTLE_US = 2000;        // > 0.78 ms measured recovery, with margin
    uint32_t settle_us = SETTLE_US;                    // exposed so the test can demonstrate a too-short window

    // true = GPIO10 must SINK (D8 lit); false = GPIO10 high-Z (open-drain released)
    bool gpio10Sink(uint32_t now_us, bool ledWanted);
    // Feed raw pin levels (true = reads LOW). TEST_N is only accepted when it is a valid sample.
    ButtonEvents update(uint32_t now_us, bool testPinLow, bool hushPinLow);

private:
    bool ledWanted_ = false;
    uint32_t releasedAt_ = 0;
    bool released_ = true;
    bool testStable_ = false, testCand_ = false; uint32_t testSince_ = 0;
    bool hushStable_ = false, hushCand_ = false; uint32_t hushSince_ = 0;
    bool validTestSample(uint32_t now_us) const;
};

