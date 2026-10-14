"""Asset-class strategy research rules.

Enhanced multi-factor heuristics with adaptive volatility thresholds for paper research (v0.5).
Not forecasts and not a recommendation to trade. Each class has an entry, an invalidation, regime and vol overlay.
"""

from __future__ import annotations

from statistics import fmean

from crypto_intel.models import AssetClass, Candle, Side, Signal
from crypto_intel.regime import Regime, VolatilityTier, classify, volatility_tier

PLAYBOOK: dict[AssetClass, dict[str, str]] = {
    AssetClass.MAJOR: {
        "hypothesis": "Liquid majors trend with multi-EMA alignment and vol-adjusted RSI, except in stress.",
        "entry": "Fast > mid > slow EMA, RSI in vol-adjusted band (45-70 normal; tighter in high vol).",
        "invalidation": "Stress regime, or RSI stretched beyond vol-adjusted limit.",
        "horizon": "8 bars mean-reversion, 20 bars trend",
    },
    AssetClass.LARGE_CAP_ALT: {
        "hypothesis": "Volume-confirmed breakouts with momentum usable outside stress; higher confirmation in high vol.",
        "entry": "Close above prior 5-bar high, volume > adaptive mult (1.3x normal, 1.5x high), positive momentum.",
        "invalidation": "Stress or missing confirmation.",
        "horizon": "12 bars",
    },
    AssetClass.STABLECOIN: {
        "hypothesis": "The useful signal is a peg break, not direction. Adaptive bands.",
        "entry": "Deviation beyond adaptive watch/depeg thresholds raises alert. No order.",
        "invalidation": "Not applicable. Size stays zero.",
        "horizon": "1 bar monitor",
    },
    AssetClass.DEFI: {
        "hypothesis": "Trend only in calm realised-vol and non-stress. Adaptive vol filter.",
        "entry": "Close above 8-bar EMA, realised vol <= adaptive threshold, not in stress.",
        "invalidation": "Stress or high realised vol.",
        "horizon": "10 bars",
    },
    AssetClass.MEME: {
        "hypothesis": "Most bursts untradeable. Qualified need volume accel and tighter extension in high vol.",
        "entry": "15% 4-bar burst, vol accel > adaptive, extension < adaptive limit.",
        "invalidation": "Thin liquidity or excessive extension.",
        "horizon": "3 bars",
    },
    AssetClass.L2: {
        "hypothesis": "L2 are multi-period relative-strength bets vs non-stress benchmark; excess thresholds vol-adjusted.",
        "entry": "6-bar and 12-bar excess return above adaptive thresholds vs benchmark.",
        "invalidation": "Missing or stressed benchmark.",
        "horizon": "12 bars",
    },
    AssetClass.RWA: {
        "hypothesis": "Tokenised RWA should be slow; adaptive gap halt.",
        "entry": "Close above 8-bar EMA and 5-bar close, gap < adaptive limit.",
        "invalidation": "Gap > adaptive or stress.",
        "horizon": "24 bars",
    },
    AssetClass.PERPETUAL: {
        "hypothesis": "Negative funding with contained adaptive drift, stable funding, non-stress is carry observation.",
        "entry": "Funding <= -5 bps, |drift| < adaptive, funding stable, not stress.",
        "invalidation": "Crowded funding, large drift, or stress.",
        "horizon": "8 bars",
    },
}


def _returns(closes: list[float]) -> list[float]:
    return [closes[i] / closes[i - 1] - 1.0 for i in range(1, len(closes))]


def _ema(values: list[float], span: int) -> float:
    alpha = 2.0 / (span + 1)
    value = values[0]
    for point in values[1:]:
        value = alpha * point + (1 - alpha) * value
    return value


def _rsi(closes: list[float], period: int = 14) -> float:
    changes = _returns(closes[-(period + 1) :])
    gains = [max(change, 0.0) for change in changes]
    losses = [abs(min(change, 0.0)) for change in changes]
    average_loss = fmean(losses) if losses else 0.0
    if average_loss == 0:
        return 100.0
    rs = fmean(gains) / average_loss
    return 100.0 - (100.0 / (1.0 + rs))


def _atr_pct(candles: list[Candle]) -> float:
    ranges = [(c.high - c.low) / c.close for c in candles[-14:] if c.close]
    return fmean(ranges) if ranges else 0.0


def _base(candles: list[Candle], side: Side, confidence: float, reason: str, size: float, bars: int) -> Signal:
    last = candles[-1]
    regime = classify(candles)
    vol = volatility_tier(candles)
    # Slight confidence haircut in high vol
    adj_conf = confidence * 0.95 if vol is VolatilityTier.HIGH else confidence
    return Signal(
        symbol=last.symbol,
        asset_class=last.asset_class,
        side=side,
        confidence=round(max(0.0, min(adj_conf, 1.0)), 4),
        reason=f"{reason}; regime={regime.value}; vol={vol.value}",
        stop_distance_pct=round(max(_atr_pct(candles) * 1.5, 0.01), 4),
        size_fraction=size,
        horizon_bars=bars,
    )


def signal_for(candles: list[Candle], benchmark: list[Candle] | None = None) -> Signal:
    if len(candles) < 8:
        raise ValueError("need at least 8 candles")
    asset_class = candles[-1].asset_class
    closes = [c.close for c in candles]
    regime = classify(candles)
    vol = volatility_tier(candles)
    if asset_class is AssetClass.MAJOR:
        return _major(candles, closes, regime, vol)
    if asset_class is AssetClass.LARGE_CAP_ALT:
        return _breakout(candles, closes, size=0.04, bars=12, regime=regime, vol=vol)
    if asset_class is AssetClass.STABLECOIN:
        return _stable(candles, vol)
    if asset_class is AssetClass.DEFI:
        return _defi(candles, closes, regime, vol)
    if asset_class is AssetClass.MEME:
        return _meme(candles, closes, vol)
    if asset_class is AssetClass.L2:
        return _l2(candles, closes, benchmark, vol)
    if asset_class is AssetClass.RWA:
        return _rwa(candles, closes, regime, vol)
    return _perpetual(candles, closes, vol)


def _major(candles: list[Candle], closes: list[float], regime: Regime, vol: VolatilityTier) -> Signal:
    fast, mid, slow = _ema(closes, 5), _ema(closes, 8), _ema(closes, 13)
    rsi = _rsi(closes)
    rsi_upper = 65 if vol is VolatilityTier.HIGH else 70
    rsi_lower_rev = 28 if vol is VolatilityTier.HIGH else 32
    if regime is Regime.STRESS:
        return _base(candles, Side.FLAT, 0.45, "major stress: stand aside", 0.0, 1)
    if fast > mid > slow and 45 <= rsi <= rsi_upper:
        return _base(candles, Side.LONG, 0.78, "major multi-EMA alignment, RSI not stretched", 0.06, 20)
    if regime is Regime.RANGE and rsi < rsi_lower_rev and closes[-1] > closes[-3]:
        return _base(candles, Side.LONG, 0.65, "major mean-reversion: washed-out RSI in range", 0.03, 8)
    return _base(candles, Side.FLAT, 0.4, "major: no aligned trend or reversion edge", 0.0, 1)


def _breakout(candles: list[Candle], closes: list[float], size: float, bars: int, regime: Regime, vol: VolatilityTier) -> Signal:
    if regime is Regime.STRESS:
        return _base(candles, Side.FLAT, 0.4, "breakout suppressed in stress", 0.0, 1)
    window = closes[-6:-1]
    volume_now = candles[-1].volume
    volume_base = fmean(c.volume for c in candles[-6:-1])
    momentum = closes[-1] / closes[-3] - 1.0
    vol_mult = 1.5 if vol is VolatilityTier.HIGH else 1.3
    if closes[-1] > max(window) and volume_now > volume_base * vol_mult and momentum > 0.01:
        return _base(candles, Side.LONG, 0.74, "volume-confirmed breakout with momentum", size, bars)
    return _base(candles, Side.FLAT, 0.35, "no confirmed breakout with momentum", 0.0, 1)


def _stable(candles: list[Candle], vol: VolatilityTier) -> Signal:
    deviation = abs(candles[-1].close - 1.0)
    watch = 0.0025 if vol is VolatilityTier.HIGH else 0.002
    depeg = 0.006 if vol is VolatilityTier.HIGH else 0.005
    if deviation >= depeg:
        return _base(candles, Side.ALERT, 0.92, f"stablecoin depeg monitor: deviation {deviation:.4f}", 0.0, 1)
    if deviation >= watch:
        return _base(candles, Side.ALERT, 0.7, f"stablecoin watch band: deviation {deviation:.4f}", 0.0, 1)
    return _base(candles, Side.FLAT, 0.8, "stablecoin inside peg band", 0.0, 1)


def _defi(candles: list[Candle], closes: list[float], regime: Regime, vol: VolatilityTier) -> Signal:
    realised = fmean(abs(v) for v in _returns(closes[-8:]))
    vol_limit = 0.05 if vol is VolatilityTier.HIGH else 0.06
    if regime is Regime.STRESS or realised > vol_limit:
        return _base(candles, Side.FLAT, 0.48, "defi volatility regime: stand aside", 0.0, 1)
    if closes[-1] > _ema(closes, 8):
        return _base(candles, Side.LONG, 0.71, "defi trend in calm regime", 0.02, 10)
    return _base(candles, Side.FLAT, 0.4, "defi: no calm trend", 0.0, 1)


def _meme(candles: list[Candle], closes: list[float], vol: VolatilityTier) -> Signal:
    liquidity = fmean(c.volume for c in candles[-5:])
    burst = closes[-1] / closes[-4] - 1.0
    extension = closes[-1] / closes[-8] - 1.0
    vol_accel = candles[-1].volume / max(candles[-2].volume, 1)
    ext_limit = 0.30 if vol is VolatilityTier.HIGH else 0.35
    accel_req = 1.3 if vol is VolatilityTier.HIGH else 1.2
    if liquidity < 1000:
        return _base(candles, Side.FLAT, 0.2, "meme liquidity proxy too thin", 0.0, 1)
    if extension > ext_limit:
        return _base(candles, Side.FLAT, 0.35, "meme chase filter: 8-bar extension too large", 0.0, 1)
    if burst > 0.15 and vol_accel > accel_req:
        return _base(candles, Side.LONG, 0.80, "meme momentum burst with volume accel; hard time stop", 0.005, 3)
    return _base(candles, Side.FLAT, 0.3, "meme: no qualified burst", 0.0, 1)


def _l2(candles: list[Candle], closes: list[float], benchmark: list[Candle] | None, vol: VolatilityTier) -> Signal:
    if not benchmark or len(benchmark) < 12:
        return _base(candles, Side.FLAT, 0.3, "l2 requires a benchmark series", 0.0, 1)
    if classify(benchmark) is Regime.STRESS:
        return _base(candles, Side.FLAT, 0.42, "l2 benchmark in stress", 0.0, 1)
    own6 = closes[-1] / closes[-6] - 1.0
    own12 = closes[-1] / closes[-12] - 1.0
    bench_closes = [c.close for c in benchmark]
    bench6 = bench_closes[-1] / bench_closes[-6] - 1.0
    bench12 = bench_closes[-1] / bench_closes[-12] - 1.0
    thresh6 = 0.035 if vol is VolatilityTier.HIGH else 0.03
    thresh12 = 0.025 if vol is VolatilityTier.HIGH else 0.02
    if own6 - bench6 > thresh6 and own12 - bench12 > thresh12:
        return _base(candles, Side.LONG, 0.73, "l2 multi-period relative strength versus benchmark", 0.03, 12)
    return _base(candles, Side.FLAT, 0.4, "l2 not leading benchmark on multi-period", 0.0, 1)


def _rwa(candles: list[Candle], closes: list[float], regime: Regime, vol: VolatilityTier) -> Signal:
    gap = candles[-1].open / candles[-2].close - 1.0
    gap_limit = 0.07 if vol is VolatilityTier.HIGH else 0.08
    if abs(gap) > gap_limit or regime is Regime.STRESS:
        return _base(candles, Side.FLAT, 0.5, "rwa gap or stress halt", 0.0, 1)
    if closes[-1] > _ema(closes, 8) and closes[-1] > closes[-5]:
        return _base(candles, Side.LONG, 0.69, "rwa slow trend", 0.02, 24)
    return _base(candles, Side.FLAT, 0.4, "rwa: no slow trend", 0.0, 1)


def _perpetual(candles: list[Candle], closes: list[float], vol: VolatilityTier) -> Signal:
    funding = candles[-1].funding_rate
    prev_funding = candles[-2].funding_rate if len(candles) > 1 else funding
    drift = closes[-1] / closes[-6] - 1.0
    funding_stable = abs(funding - prev_funding) < 0.0003
    drift_limit = 0.035 if vol is VolatilityTier.HIGH else 0.04
    if funding >= 0.001:
        return _base(candles, Side.ALERT, 0.7, "perp funding crowded: monitor, no carry", 0.0, 1)
    if funding <= -0.0005 and abs(drift) < drift_limit and funding_stable:
        return _base(candles, Side.LONG, 0.77, "perp funding carry: negative funding, drift contained, stable", 0.02, 8)
    if funding <= -0.0005:
        return _base(candles, Side.FLAT, 0.5, "perp funding attractive but drift or stability not met", 0.0, 1)
    return _base(candles, Side.FLAT, 0.4, "perp: no carry edge", 0.0, 1)
