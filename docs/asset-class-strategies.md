# Asset-class strategy notes (v0.3 enhanced)

These rules are research heuristics. Each class has an edge hypothesis, an entry, an invalidation, a horizon, and a size cap. They are not a promise of return. Version 0.3 adds multi-factor refinements and volatility context.

Regime labels, from `regime.py`:

- **trend**: eight-bar move of at least 2.5% and bar range under the stress band
- **range**: neither stress nor trend
- **stress**: average bar range at least 3.5% of price; directional ideas stand aside

Volatility tiers: low / normal / high based on ATR%.

## Major

Hypothesis: liquid majors trend often enough that multi-EMA alignment (fast > mid > slow) is usable, unless RSI is stretched or the book is in stress. Mean reversion is allowed only in a range regime. Cap 8%. Horizon 8 or 20 bars. Research cost 8 bps round trip.

## Large-cap alt

Hypothesis: breakouts without volume and momentum are noise, and stress-regime breakouts are gap risk. Entry needs a close above the prior five-bar high, volume at least 1.3 times the recent average, positive short momentum, and a non-stress regime. Cap 4%. Cost 14 bps.

## Stablecoin

Hypothesis: the useful signal is a peg break. Deviation of 20 bps is a watch alert. Deviation of 50 bps or more is a depeg alert. Risk gate forces size to zero. Cost assumption is unused because no order is allowed.

## DeFi

Hypothesis: trend signals in high realised-volatility or stress regimes are mostly gap risk. Stand aside if mean absolute return over 8 bars exceeds 6% or the regime is stress. Cap 2%. Cost 22 bps.

## Meme

Hypothesis: most bursts are untradeable. A long is allowed only after a 15% four-bar burst, volume acceleration > 1.2x, a volume floor, and an eight-bar extension that is still under 35%. Horizon is 3 bars. Cap 0.5%. Cost 45 bps.

## L2

Hypothesis: L2 tokens are bets on multi-period relative strength versus a benchmark. No benchmark, or a benchmark in stress, means no trade. Cap 3%. Cost 16 bps.

## RWA

Hypothesis: tokenised real-world assets should be slow. An open-to-prior-close gap above 8%, or a stress regime, halts the idea. Cap 2%, horizon 24 bars. Cost 12 bps.

## Perpetual

Hypothesis: negative funding with contained spot drift and stable funding is a carry observation. Funding at or above 10 bps is a crowded-funding alert, not a short. Drift outside 4% or unstable funding blocks the carry. Cap 2%. Cost 10 bps. This does not model liquidation, funding intervals, or exchange risk.

## Still out of scope

- Live order routing, withdrawal, and trade API keys.
- A broker adapter. That would be a separate human-approved system.
- Claims about future returns. Scores describe the synthetic fixture.
