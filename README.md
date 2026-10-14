# AIxTech crypto intel enhanced: paper-only trading information system v0.7

Enhanced research harness for automated cryptocurrency **information** and paper strategy evaluation.
Builds on the original [zeekiankok92/aixtech-crypto-intel](https://github.com/zeekiankok92/aixtech-crypto-intel) and prior enhancements (v0.6).

It does not place live orders, does not store exchange secrets, and is not financial advice.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![version](https://img.shields.io/badge/version-0.7.0-blue)
![mode](https://img.shields.io/badge/execution-paper%20only-orange)
![Licence](https://img.shields.io/badge/licence-MIT-green)

## Enhancements in v0.7

- MACD-style EMA momentum confirmation for major and large-cap alt strategies.
- Tighter meme filters (RSI overbought rejection) and relative volume for L2.
- Expanded secret redaction patterns (AWS-style, Slack tokens, base64-like).
- Improved multi-bar anomaly scoring with consistency checks.
- Adaptive thresholds refined across classes; documentation updated.

See [docs/asset-class-strategies.md](docs/asset-class-strategies.md) and [docs/security-architecture.md](docs/security-architecture.md).

## What it does

- Classifies markets into eight asset classes and applies enhanced, adaptive research rules to each.
- Labels regimes (trend/range/stress) with volatility tiers (low/normal/high).
- Scores signals with multi-factor confidence (MACD, RSI, volume, adaptive), then a risk gate that can shrink or refuse.
- Applies declared round-trip costs in paper backtests.
- Writes a hash-chained audit log with enhanced anomaly notes and sanitization, attests sources, redacts secrets.
- Backtests on synthetic candles only.

| Asset class | Enhanced research rule | Risk cap (base) | Cost |
|---|---|---|---|
| Major | Multi-EMA + MACD confirmation + adaptive RSI, stand aside in stress | 8% | 8 bps |
| Large-cap alt | Volume-confirmed breakout with MACD + multi-momentum + adaptive vol mult | 4% | 14 bps |
| Stablecoin | Adaptive peg deviation alerts only | 0% | n/a |
| DeFi | Calm-regime trend with adaptive vol filter + momentum | 2% | 22 bps |
| Meme | Qualified burst with vol-adjusted extension, volume accel, consistency, RSI filter | 0.5% | 45 bps |
| L2 | Multi-period relative strength vs benchmark + relative volume, vol-adjusted | 3% | 16 bps |
| RWA | Slow trend with momentum, adaptive gap/stress halt | 2% | 12 bps |
| Perpetual | Funding carry with adaptive drift, stability, momentum, non-stress | 2% | 10 bps |

## Run

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python scripts/make_fixtures.py
PYTHONPATH=src python -m crypto_intel scan fixtures/candles_synthetic.json
PYTHONPATH=src python -m crypto_intel brief fixtures/candles_synthetic.json
```

## Controls

Paper-only. No live credentials. Class caps, adaptive confidence floors, kill switch, drawdown halt, multi-context anomaly detection, hash-chained audit, PDPA tripwire, gitleaks CI. Zero-trust research design with adaptive risk.

## Honesty

No live exchange connector. Scores describe synthetic fixtures. Not investment advice. Research only.
