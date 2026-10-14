# Asset-class strategy notes (v0.6 enhanced)

These rules are research heuristics. Each class has an edge hypothesis, an entry, an invalidation, a horizon, and a size cap. They are not a promise of return. Version 0.6 adds adaptive RSI periods by volatility tier, multi-momentum confirmation, and further tightening of filters.

Regime labels, from `regime.py` (slightly adaptive thresholds):

- **trend**: eight-bar move of at least ~2.2-2.5% and bar range under the stress band
- **range**: neither stress nor trend
- **stress**: average bar range at least ~3.2-3.5% of price; directional ideas stand aside

Volatility tiers: low / normal / high based on ATR%. Adaptive thresholds tighten or loosen filters accordingly (e.g., higher volume confirmation and tighter extension limits in high vol; longer RSI period in low vol; size reduction and higher confidence floors in risk gate).

## Major

Hypothesis: liquid majors trend often enough that multi-EMA alignment (fast > mid > slow) with vol-adjusted RSI (adaptive period: 16 low / 14 normal / 12 high) is usable, unless RSI is stretched or the book is in stress. Mean reversion is allowed only in a range regime. Cap 8%. Horizon 8 or 20 bars. Research cost 8 bps round trip. Confidence reduced in high vol. RSI bands tighten in high vol.

## Large-cap alt

Hypothesis: breakouts without volume and multi-momentum are noise, and stress-regime breakouts are gap risk. Entry needs a close above the prior five-bar high, volume at least adaptive multiple (1.3x normal, 1.6x high), positive short and medium momentum, and a non-stress regime. Cap 4%. Cost 14 bps.

## Stablecoin

Hypothesis: the useful signal is a peg break. Adaptive watch/depeg bands based on vol (higher in high vol). Deviation of ~20-28 bps is a watch alert. Deviation of ~50-65 bps or more is a depeg alert. Risk gate forces size to zero. Cost assumption is unused because no order is allowed.

## DeFi

Hypothesis: trend signals in high realised-volatility or stress regimes are mostly gap risk. Stand aside if mean absolute return over 8 bars exceeds adaptive threshold (~4.8-6%) or the regime is stress. Positive momentum required. Cap 2%. Cost 22 bps.

## Meme

Hypothesis: most bursts are untradeable. A long is allowed only after a 15% four-bar burst, volume acceleration > adaptive (1.2-1.35), a volume floor, rising closes, and an eight-bar extension that is still under adaptive ~28-35%. Horizon is 3 bars. Cap 0.5%. Cost 45 bps.

## L2

Hypothesis: L2 tokens are bets on multi-period relative strength versus a benchmark. No benchmark, or a benchmark in stress, means no trade. Excess thresholds are vol-adjusted (higher in high vol). Cap 3%. Cost 16 bps.

## RWA

Hypothesis: tokenised real-world assets should be slow. An open-to-prior-close gap above adaptive ~6.5-8%, or a stress regime, halts the idea. Positive slow momentum required. Cap 2%, horizon 24 bars. Cost 12 bps.

## Perpetual

Hypothesis: negative funding with contained spot drift (adaptive 3.2-4%), stable funding, contained momentum, and non-stress is a carry observation. Funding at or above 10 bps is a crowded-funding alert, not a short. Drift outside adaptive or unstable funding or stress or large momentum blocks the carry. Cap 2%. Cost 10 bps. This does not model liquidation, funding intervals, or exchange risk.

## Still out of scope

- Live order routing, withdrawal, and trade API keys.
- A broker adapter. That would be a separate human-approved system.
- Claims about future returns. Scores describe the synthetic fixture.
- Adaptive parameter optimization via live data; all thresholds are research heuristics.
