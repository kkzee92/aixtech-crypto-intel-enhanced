# AIxTech crypto intel enhanced: paper-only trading information system v0.3

Enhanced research harness for automated cryptocurrency **information** and paper strategy evaluation.
Builds on the original [zeekiankok92/aixtech-crypto-intel](https://github.com/zeekiankok92/aixtech-crypto-intel).

It does not place live orders, does not store exchange secrets, and is not financial advice.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![version](https://img.shields.io/badge/version-0.3.0-blue)
![mode](https://img.shields.io/badge/execution-paper%20only-orange)
![Licence](https://img.shields.io/badge/licence-MIT-green)

## Enhancements in v0.3

- Refined multi-factor strategies per asset class with additional indicators (EMA alignment, volume acceleration, relative strength multi-period).
- Volatility- and regime-adjusted risk sizing.
- Strengthened security: expanded secret detection, feed anomaly scoring, enhanced audit chain, input sanitization.
- Improved regime classifier with volatility tiers.
- Updated documentation and playbooks.

See [docs/asset-class-strategies.md](docs/asset-class-strategies.md) and [docs/security-architecture.md](docs/security-architecture.md).

## What it does

- Classifies markets into eight asset classes and applies enhanced research rules to each.
- Labels regimes (trend/range/stress) with volatility context.
- Scores signals with multi-factor confidence, then a risk gate that can shrink or refuse.
- Applies declared round-trip costs in paper backtests.
- Writes a hash-chained audit log with anomaly notes, attests sources, redacts secrets.
- Backtests on synthetic candles only.

| Asset class | Enhanced research rule | Risk cap (base) | Cost |
|---|---|---|---|
| Major | Multi-EMA alignment + RSI zone, stand aside in stress | 8% | 8 bps |
| Large-cap alt | Volume-confirmed breakout with momentum filter | 4% | 14 bps |
| Stablecoin | Peg deviation alerts only | 0% | n/a |
| DeFi | Calm-regime trend with vol filter | 2% | 22 bps |
| Meme | Qualified burst with extension and volume accel filters | 0.5% | 45 bps |
| L2 | Multi-period relative strength vs benchmark | 3% | 16 bps |
| RWA | Slow trend, gap/stress halt, vol-adjusted | 2% | 12 bps |
| Perpetual | Funding carry with drift and funding momentum checks | 2% | 10 bps |

## Run

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python scripts/make_fixtures.py
PYTHONPATH=src python -m crypto_intel scan fixtures/candles_synthetic.json
PYTHONPATH=src python -m crypto_intel brief fixtures/candles_synthetic.json
```

## Controls

Paper-only. No live credentials. Class caps, confidence floors, kill switch, drawdown halt, anomaly detection, hash-chained audit, PDPA tripwire, gitleaks CI.

## Honesty

No live exchange connector. Scores describe synthetic fixtures. Not investment advice.
