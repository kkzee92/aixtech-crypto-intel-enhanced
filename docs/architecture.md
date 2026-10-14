# Architecture (v0.6)

```mermaid
flowchart LR
    FX["fixtures/candles_synthetic.json"] --> M["market.py"]
    M --> RG["regime.py (adaptive vol tier + thresholds)"]
    M --> ST["strategies.py multi-factor adaptive rules per asset class"]
    RG --> ST
    ST --> RK["risk.py (vol-adjusted size and confidence)"]
    CS["costs.py"] --> EN["engine.py paper fill"]
    RK --> EN
    EN --> AU["security.py audit chain + multi-candle anomaly + expanded redaction"]
    PS["posture.py attestation and RBAC"] --> CLI["cli.py"]
    EN --> CLI
```

Runtime dependencies are the Python standard library. See security-architecture.md and asset-class-strategies.md.
