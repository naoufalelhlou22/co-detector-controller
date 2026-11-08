#include "buttons.h"

bool Buttons::gpio10Sink(uint32_t now_us, bool ledWanted) {
    ledWanted_ = ledWanted;
    bool sink = ledWanted && ((now_us % D8_PERIOD_US) < (D8_PERIOD_US - D8_RELEASE_US));
    if (!sink && !released_) { released_ = true; releasedAt_ = now_us; }
    if (sink) released_ = false;
    return sink;
}

bool Buttons::validTestSample(uint32_t now_us) const {
    return released_ && (now_us - releasedAt_) >= settle_us;
}

static bool debounce(bool raw, bool& cand, bool& stable, uint32_t& since, uint32_t now, uint32_t db) {
    if (raw != cand) { cand = raw; since = now; }
    if (cand != stable && (now - since) >= db) {
        stable = cand;
        return stable;  // rising edge of "pressed"
    }
    return false;
}

ButtonEvents Buttons::update(uint32_t now_us, bool testPinLow, bool hushPinLow) {
    ButtonEvents ev;
    if (validTestSample(now_us)) {
        ev.test = debounce(testPinLow, testCand_, testStable_, testSince_, now_us, DEBOUNCE_US);
    }
    // During sink phase (!released_ or not yet settled), we simply skip sampling TEST_N.
    // testSince_ is preserved so that sustained depression across PWM strobe cycles debounces correctly.
    ev.hush = debounce(hushPinLow, hushCand_, hushStable_, hushSince_, now_us, DEBOUNCE_US);
    return ev;
}

