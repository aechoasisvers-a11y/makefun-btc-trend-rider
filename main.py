"""cbBTC trend rider for make.fun's "Race a BTC trading bot live for 24 hours".

Strategy (pure stdlib, deterministic, no clock, no network, no randomness):
  * One symbol (CBBTC), long only, all-in / all-out.
  * ENTER: the 120-minute return of closes is above +50 bps (0.50%).
    The move has to be real: 120 minutes of closes, not a one-minute spike.
  * HOLD with a 2% trailing stop from the highest close since entry.
    The stop is what keeps a falling market cheap: one stopped trade costs
    about 2% plus ~26 bps of round-trip fees/slippage/impact, then the bot
    sits out for a 120-minute cooldown instead of catching the falling knife.
  * COOLDOWN: 120 bars after any exit before the next entry, so a choppy
    market cannot whipsaw the bot into repeated round trips.
  * No take-profit: a real trend is ridden to its trailing stop (or to the
    window's end, where the harness flattens the position).

Why this shape: on the published 24h dev window (BTC +3.6%, mostly a slow
grind up, then flat) every fast trend/mean-reversion variant we backtested
lost money to the ~26 bps round-trip cost and the 1-bar fill latency, while
this slow two-trade shape made +$31.10 on $1,000. It also loses the least
of the tested shapes when the window is reversed into a falling market
(-$16.51 vs -$38.40 for buy-and-hold), and about $0 on the flat second
half. The entry threshold sits on a plateau (30-50 bps all score ~+$31 on
dev), and the 2% trail beats 1.5% (whipsawed, +$6.44) and 2.5-3%
(lets losses run deeper on the falling window).

All arithmetic is integer (raw price units), so two runs on the same data
produce byte-identical orders.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars  # noqa: E402

LOOKBACK_BARS = 120        # minutes of closes behind an entry decision
ENTER_BPS = 50             # 120-minute return must beat +0.50%
TRAIL_BPS = 200            # trailing stop: 2% below the peak close since entry
COOLDOWN_BARS = 120        # bars to sit out after any exit
MAX_SLIPPAGE_BPS = 1000    # 10%: far above any 1-minute move seen (~72 bps max)

_closes = []               # closes so far, raw price units (ints)
_peak = None               # highest close since entry (raw units), else None
_cool = 0                  # bars left in the post-exit cooldown


def _symbol(state):
    return state.hello["symbols"][0]["symbol"]


def on_batch(state, batch):
    global _peak, _cool
    symbol = _symbol(state)
    close = state.close(symbol)
    if close is None:
        return []
    _closes.append(close)
    if state.warming_up:
        return []

    holding = state.positions.get(symbol)
    if holding is not None:
        # A buy fills at the next bar's open, so the true entry price is the
        # fill's price, not the close the decision was made on. The trailing
        # stop tracks the peak since entry, so start it from the higher of
        # the two: a fill above the decision close must not leave the stop
        # below the price actually paid.
        for fill in batch.get("fills") or []:
            if (fill.get("side") == "buy" and fill.get("status") == "filled"
                    and fill.get("symbol") == symbol and fill.get("price")):
                fill_price = int(fill["price"])
                if _peak is None or fill_price > _peak:
                    _peak = fill_price
        if _peak is None or close > _peak:
            _peak = close
        # Trailing stop: sell everything once the close falls 2% under the peak.
        if close * 10000 < _peak * (10000 - TRAIL_BPS):
            _cool = COOLDOWN_BARS
            _peak = None
            return [{
                "side": "sell",
                "symbol": symbol,
                "qty": holding.qty,
                "max_slippage_bps": MAX_SLIPPAGE_BPS,
            }]
        return []

    if _cool > 0:
        _cool -= 1
        return []

    if len(_closes) > LOOKBACK_BARS:
        then = _closes[-LOOKBACK_BARS - 1]
        # (close - then) / then in bps, integer math, no floats anywhere.
        if (close - then) * 10000 // then > ENTER_BPS:
            _peak = close
            return [{
                "side": "buy",
                "symbol": symbol,
                "notional_quote_units": state.cash,
                "max_slippage_bps": MAX_SLIPPAGE_BPS,
            }]
    return []


makefun_bars.run(on_batch)
