# Asset-class strategy notes (v0.7 enhanced)

These rules are research heuristics. Each class has an edge hypothesis, an entry, an invalidation, a horizon, and a size cap. They are not a promise of return. Version 0.7 adds MACD-style EMA momentum confirmation, tighter RSI filters for high-risk classes, and relative volume checks.

Regime labels, from `regime.py` (slightly adaptive thresholds):

- **trend**: eight-bar move of at least ~2.2-2.5% and bar range under the stress band
- **range**: neither stress nor trend
- **stress**: average bar range at least ~3.2-3.5% of price; directional ideas stand aside

Volatility tiers: low / normal / high based on ATR%. Adaptive thresholds tighten or loosen filters accordingly.

## Major

Hypothesis: liquid majors trend with multi-EMA alignment and MACD-style momentum (EMA12-EMA26 positive and rising), plus vol-adjusted RSI (adaptive period). Stand aside in stress. Mean reversion only in range. Cap 8%. Horizon 8 or 20 bars. Research cost 8 bps. Confidence reduced in high vol.

## Large-cap alt

Hypothesis: volume-confirmed breakouts with multi-momentum and MACD confirmation are usable outside stress. Higher volume mult in high vol. Cap 4%. Cost 14 bps.

## Stablecoin

Hypothesis: peg break signal. Adaptive watch/depeg bands. No order. Cap 0%.

## DeFi

Hypothesis: trend in calm non-stress with positive momentum. Adaptive vol limit. Cap 2%. Cost 22 bps.

## Meme

Hypothesis: qualified bursts only; RSI must not be overbought (>78), volume accel, extension limit tighter in high vol, rising closes. Horizon 3 bars. Cap 0.5%. Cost 45 bps.

## L2

Hypothesis: multi-period relative strength vs non-stress benchmark plus relative volume. Excess thresholds vol-adjusted. Cap 3%. Cost 16 bps.

## RWA

Hypothesis: slow trend with momentum; adaptive gap halt. Cap 2%, horizon 24 bars. Cost 12 bps.

## Perpetual

Hypothesis: negative funding with contained adaptive drift, stable funding, non-stress, contained momentum. Cap 2%. Cost 10 bps. Does not model liquidation or funding intervals.

## Still out of scope

- Live order routing, withdrawal, and trade API keys.
- A broker adapter. Separate human-approved system.
- Claims about future returns. Scores describe the synthetic fixture.
- Adaptive parameter optimization via live data; all thresholds are research heuristics.
