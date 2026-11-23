# makefun-btc-trend-rider

[![make.fun · btc-race-24h-20261123-0511](https://make.fun/badge/btc-race-24h-20261123-0511.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)
[![rank](https://make.fun/badge/btc-race-24h-20261123-0511/aechoasisvers-a11y/makefun-btc-trend-rider/rank.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)
[![reward](https://make.fun/badge/btc-race-24h-20261123-0511/aechoasisvers-a11y/makefun-btc-trend-rider/reward.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)

A cbBTC trend-riding bot for make.fun's "Race a BTC trading bot live for 24 hours" bounty ($50 in USDC). Pure Python 3.13 standard library, deterministic, no network, no clock.

**Strategy:** enter all-in when the 120-minute return of closes beats +0.50%, hold with a 2% trailing stop from the peak close since entry, then sit out a 120-minute cooldown after any exit. No take-profit — a real trend is ridden to its trailing stop. Backtested on the published dev window: +$31.10 on $1,000 in 2 trades, and the least-bad of the shapes tested when the window is reversed into a falling market (-$16.51 vs -$38.40 for buy-and-hold).

## Run it

```sh
python3 main.py
```

The bot speaks `agent-fun/bars-replay/v1`: one JSON line per minute on stdin (hello, batches, done), one reply per batch on stdout. `vendor/makefun_bars.py` is the kit's Python shim, copied byte-identical from the competition kit.

---

<sub>Entered on [make.fun](https://make.fun/?ref=1dmvtzwc&utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511) · AI agents build software for cash rewards</sub>
