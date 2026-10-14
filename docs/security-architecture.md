# Security architecture (v0.7 enhanced)

Version 0.7 further strengthens the research control plane with expanded secret patterns (AWS-style keys, Slack tokens, longer base64-like), improved multi-bar anomaly scoring with consistency, and refined sanitization. It remains a research design, not a certified security product, and not legal or compliance advice.

## Trust boundaries

```mermaid
flowchart LR
    F[\"Synthetic fixture or injected public ticker\"] --> AT[\"Source attestation + enhanced multi-candle anomaly score + consistency\"]
    AT --> S[\"Strategy research rules + regime + adaptive vol + MACD overlay\"]
    S --> R[\"Risk gate: class caps, kill switch, drawdown, vol-adjusted size and confidence\"]
    R --> P[\"Paper fill only\"]
    P --> A[\"Hash-chained audit log with length-limited sanitization and expanded redaction\"]
    K[\"Trade or withdrawal keys\"] -.-> X[\"Refused. Never loaded\"]
    RBAC[\"Researcher, auditor, operator\"] --> R
```

The system has no order router. `assert_paper_only` refuses any mode other than `PAPER`. Roles cannot enable live trading. Zero-trust: attest every input; all logged details pass through `sanitize_input`.

## Roles

| Role | Allowed | Denied |
|---|---|---|
| Researcher | scan, backtest, read audit | place order, withdraw, enable live |
| Auditor | read audit, verify chain, scan, anomaly review | place order, withdraw, enable live |
| Operator | scan, kill switch, read audit | place order, withdraw, enable live |

No trader role. Promoting a signal to a broker is a separate, human-approved system.

## Data classes and handling

| Field | Class | Handling | Retention / Protection |
|---|---|---|---|
| Symbol, OHLCV | Public market | Synthetic in this repo | Research |
| Funding rate | Public market | Research feature only | Research |
| Source label | Integrity | Must be SYNTHETIC or PUBLIC_READ | Attested via hash |
| Read-only market key | Secret, optional | Name must say read/market/public. Never logged | Rotate externally |
| Trade or withdrawal key | Secret | Refused | Never stored |
| Wallet address | Sensitive identifier | Redacted, banned from fixtures | Do not collect |
| Email, NRIC, phone | Personal | Tripwire + redaction | Do not collect |

PDPA note: tripwire is not full DLP. Production needs access control, encryption at rest, human DPO oversight.

## Feed integrity and anomaly detection

`anomaly_score` flags large jumps, volume spikes, staleness, consecutive jumps, and low consistency as research notes (0-1). High scores logged. `sanitize_input` redacts expanded secrets (JWT, hex, AWS, Slack), wallets, phones, strips controls, length-limits. Source attestation hashes label + body. Loader rejects non-SYNTHETIC.

## Threats and controls

| Threat | Control |
|---|---|
| Secret committed | gitleaks CI, expanded redaction (JWT, hex, AWS AKIA, Slack xox, base64-like), no key loader |
| Trade key pasted | refuse_trade_secret (research) |
| Strategy injection via fixture | SYNTHETIC required, source attestation, anomaly scoring |
| Stale or jumped ticker | enhanced multi-candle anomaly + consistency |
| Oversized risk | Per-class cap, adaptive confidence floor, vol-adjusted size reduction |
| Runaway loss | Drawdown halt and kill switch |
| Audit tamper | SHA-256 chain; verify function |
| Live-order mistake | No live client; mode guard; RBAC deny; paper-only |
| Personal data | AGENTS.md ban + CI tripwire + redaction |
| Privilege creep | No role can place an order |
| Input injection | Redaction, length-limited sanitization |
| Replay or stale data | Timestamp and consecutive-jump + consistency detection |

## Incident handling

1. Engage kill switch. New paper size to zero.
2. Freeze audit chain; record attestation digest and high anomaly scores.
3. If secret pasted, rotate outside repo, purge history, review CI.
4. Do not open public issue with secret, wallet, or personal data.
5. Human review before clearing kill switch. Document it.
6. Post-incident: update redaction patterns if new secret form seen.

## Operating rules and architecture principles

- Market-data credentials (if added) stay read-only, separate from trade credentials, never logged.
- Logs through `sanitize_input` / `redact`. Prefer structured logging.
- Default is research / paper-only. Broker promotion is separate human-approved system.
- Zero-trust: attest inputs; verify audit chain; assume adversarial fixtures.
- Encryption: future persistent stores use AES-256 at rest + TLS. This repo holds only synthetic data.
- Monitoring: anomaly scores, kill-switch activations, failed attestations.
- Secret management: none in tree; external managers for production extensions.
- Audit immutability: hash chain is research-level; production adds append-only + external anchoring.
- Regular review: strategies and risk gates versioned; human review + tests required.
- Adaptive risk: high-vol contexts reduce size and raise confidence floors.

This design prioritizes research integrity, heuristic transparency, and prevention of accidental live execution or secret leakage.
