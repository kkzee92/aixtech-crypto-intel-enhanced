# Security architecture (v0.6 enhanced)

Version 0.6 further strengthens the research control plane with expanded redaction patterns (JWT-like, hex private-key style), length-limited sanitization, multi-candle consecutive-jump anomaly scoring, and adaptive regime thresholds. It remains a research design, not a certified security product, and not legal or compliance advice.

## Trust boundaries

```mermaid
flowchart LR
    F[\"Synthetic fixture or injected public ticker\"] --> AT[\"Source attestation + enhanced multi-candle anomaly score\"]
    AT --> S[\"Strategy research rules + regime + adaptive vol overlay\"]
    S --> R[\"Risk gate: class caps, kill switch, drawdown, vol-adjusted size and confidence\"]
    R --> P[\"Paper fill only\"]
    P --> A[\"Hash-chained audit log with length-limited sanitization and redaction\"]
    K[\"Trade or withdrawal keys\"] -.-> X[\"Refused. Never loaded\"]
    RBAC[\"Researcher, auditor, operator\"] --> R
```

The system has no order router. `assert_paper_only` refuses any mode other than `PAPER`. Roles cannot enable live trading. Zero-trust assumption: no component trusts unattested input. All logged details pass through `sanitize_input` (length-limited).

## Roles

| Role | Allowed | Denied |
|---|---|---|
| Researcher | scan, backtest, read audit | place order, withdraw, enable live |
| Auditor | read audit, verify chain, scan, anomaly review | place order, withdraw, enable live |
| Operator | scan, kill switch, read audit | place order, withdraw, enable live |

There is no trader role. Promoting a signal to a broker is a separate, human-approved system with its own controls.

## Data classes and handling

| Field | Class | Handling | Retention / Protection |
|---|---|---|---|
| Symbol, OHLCV | Public market | Synthetic in this repo | Research; no encryption needed for fixtures |
| Funding rate | Public market | Research feature only | Research |
| Source label | Integrity | Must be SYNTHETIC or PUBLIC_READ | Attested via hash |
| Read-only market key | Secret, optional | Name must say read, market, or public. Never logged | Rotate externally; never commit |
| Trade or withdrawal key | Secret | Refused | Never stored |
| Wallet address | Sensitive identifier | Redacted, banned from fixtures | Do not collect |
| Email, NRIC, phone | Personal | Tripwire + redaction | Do not collect |

PDPA note: the tripwire is not a full DLP product. Production deployments require access control, vendor review, encryption at rest for any persistent data, and human DPO oversight. Wallet addresses can be personal data; this repo does not store them.

## Feed integrity and anomaly detection

`anomaly_score` flags large price jumps (>15-25%), volume spikes, staleness (>5-15 min), or consecutive jumps as research notes (score 0-1). High scores are logged and can influence risk notes. `sanitize_input` redacts secrets (including JWT and hex keys), wallets, phones, strips control characters, and length-limits before audit. Source attestation hashes label + body so fixture swaps change the digest. Loader rejects non-SYNTHETIC.

## Threats and controls

| Threat | Control |
|---|---|
| Secret committed | gitleaks CI, expanded redaction patterns (JWT, hex), no key loader, pre-commit style checks |
| Trade key pasted into config | refuse_trade_secret (research) |
| Strategy injection via fixture | SYNTHETIC label required, source attestation, anomaly scoring |
| Stale or jumped public ticker | enhanced multi-candle anomaly score, feed status watch/high |
| Oversized risk on thin assets | Per-class cap, adaptive confidence floor, class cost, stronger vol-adjusted size reduction |
| Runaway loss | Drawdown halt and kill switch |
| Audit tamper | SHA-256 chain over sequence, action, detail; verify function |
| Live-order mistake | No live client; mode guard; RBAC deny; paper-only assertion |
| Personal data in agent context | AGENTS.md ban plus CI tripwire + phone redaction |
| Privilege creep | No role can place an order; least privilege |
| Input injection | Redaction, length-limited sanitization before logging |
| Replay or stale data | Timestamp checks and consecutive-jump detection in anomaly score (research) |

## Incident handling

1. Engage the kill switch. New paper size goes to zero.
2. Freeze the audit chain and record the source attestation digest and any high anomaly scores.
3. If a secret was pasted, rotate it outside this repo, purge it from history, and review CI logs.
4. Do not open a public issue that contains a secret, wallet address, or personal data.
5. A human reviews before the kill switch is cleared. Document the review.
6. Post-incident: update redaction patterns if a new secret form was seen.

## Operating rules and architecture principles

- Market-data credentials, if ever added, stay read-only, separate from any future trade credential, and never logged.
- Logs pass through `sanitize_input` / `redact` before they are stored. Prefer structured logging with classification tags.
- Default deployment is research / paper-only. Promoting a signal to a broker is a separate, human-approved system.
- Zero-trust: attest every input source; verify audit chain on read; assume fixtures can be adversarial.
- Encryption: for any future persistent store, use encryption at rest (e.g., AES-256) and TLS in transit. This research repo uses none because it holds only synthetic data.
- Monitoring: track anomaly scores, kill-switch activations, and failed source attestations.
- Secret management: no secrets in tree; use external managers for any production extension.
- Audit immutability: the hash chain provides research-level integrity; production would add append-only storage and external anchoring.
- Regular review: strategies and risk gates are versioned; changes require human review and test coverage.
- Adaptive risk: high-volatility contexts automatically reduce proposed size and raise confidence floors.

This design prioritizes research integrity, transparency of heuristics, and prevention of accidental live execution or secret leakage.
