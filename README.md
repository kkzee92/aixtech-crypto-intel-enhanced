# AIxTech crypto intel enhanced: paper-only trading information system v0.6

Enhanced research harness for automated cryptocurrency **information** and paper strategy evaluation.
Builds on the original [zeekiankok92/aixtech-crypto-intel](https://github.com/zeekiankok92/aixtech-crypto-intel) and prior enhancements.

It does not place live orders, does not store exchange secrets, and is not financial advice.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![version](https://img.shields.io/badge/version-0.6.0-blue)
![mode](https://img.shields.io/badge/execution-paper%20only-orange)
![Licence](https://img.shields.io/badge/licence-MIT-green)

## Enhancements in v0.6

- Adaptive RSI periods by volatility tier (longer in low vol, shorter in high) and multi-momentum confirmation across strategies.
- Tighter filters, rising-close consistency for memes, stronger size reduction (30%) and higher confidence floors in high vol.
- Strengthened cyber/data security: additional redaction patterns (JWT-like, hex keys), length-limited sanitization, multi-candle consecutive-jump anomaly scoring.
- Regime classifier with slightly adaptive stress/trend thresholds.
- Updated documentation and versioning.

See [docs/asset-class-strategies.md](docs/asset-class-strategies.md) and [docs/security-architecture.md](docs/security-architecture.md).

## What it does

- Classifies markets into eight asset classes and applies enhanced, adaptive research rules to each.
- Labels regimes (trend/range/stress) with volatility tiers (low/normal/high).
- Scores signals with multi-factor confidence (adjusted for high vol), then a risk gate that can shrink or refuse.
- Applies declared round-trip costs in paper backtests.
- Writes a hash-chained audit log with anomaly notes and sanitization, attests sources, redacts secrets.
- Backtests on synthetic candles only.

| Asset class | Enhanced research rule | Risk cap (base) | Cost |
|---|---|---|---|
| Major | Multi-EMA + adaptive RSI period, stand aside in stress | 8% | 8 bps |
| Large-cap alt | Volume-confirmed breakout with multi-momentum + adaptive vol mult | 4% | 14 bps |
| Stablecoin | Adaptive peg deviation alerts only | 0% | n/a |
| DeFi | Calm-regime trend with adaptive vol filter + momentum | 2% | 22 bps |
| Meme | Qualified burst with vol-adjusted extension, volume accel, consistency | 0.5% | 45 bps |
| L2 | Multi-period relative strength vs benchmark, vol-adjusted | 3% | 16 bps |
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
