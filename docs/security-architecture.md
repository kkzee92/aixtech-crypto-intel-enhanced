# Security architecture (v0.3 enhanced)

Version 0.3 extends the control plane with anomaly scoring and expanded detection. It is still a research design, not a certified security product and not legal advice.

## Trust boundaries

Synthetic fixture or injected public ticker -> Source attestation -> Strategy research rules plus regime and volatility overlay -> Risk gate: class caps, kill switch, drawdown, vol notes -> Paper fill only -> Hash-chained audit log with redaction and anomaly notes.

Trade or withdrawal keys are refused. Never loaded. Roles cannot enable live trading.

## Roles

| Role | Allowed | Denied |
|---|---|---|
| Researcher | scan, backtest, read audit | place order, withdraw, enable live |
| Auditor | read audit, verify chain, scan | place order, withdraw, enable live |
| Operator | scan, kill switch, read audit | place order, withdraw, enable live |

There is no trader role. Promoting a signal to a broker is a separate system.

## Data classes

| Field | Class | Handling |
|---|---|---|
| Symbol, OHLCV | Public market | Synthetic in this repo |
| Funding rate | Public market | Research feature only |
| Source label | Integrity | Must be SYNTHETIC or PUBLIC_READ |
| Read-only market key | Secret, optional | Name must say read, market, or public. Never logged |
| Trade or withdrawal key | Secret | Refused |
| Wallet address | Sensitive identifier | Redacted, banned from fixtures |
| Email, NRIC, phone | Personal | Tripwire |

## Feed integrity

`anomaly_score` flags large price jumps or volume spikes as research notes. `feed_status` (inherited concept) flags non-positive price, stale prints, or jumps. Tests inject the payload. The default path does not open a socket.

## Threats and controls

| Threat | Control |
|---|---|
| Secret committed | gitleaks CI, expanded redaction patterns, no key loader |
| Trade key pasted into config | `refuse_trade_secret` |
| Strategy injection via fixture | SYNTHETIC label required, source attestation |
| Stale or jumped public ticker | anomaly score and feed status |
| Oversized risk on thin assets | Per-class cap, confidence floor, class cost, vol notes |
| Runaway loss | Drawdown halt and kill switch |
| Audit tamper | SHA-256 chain over sequence, action, detail |
| Live-order mistake | No live client; mode guard; RBAC deny |
| Personal data in agent context | Ban plus CI tripwire |
| Privilege creep | No role can place an order |

## Incident handling

1. Engage the kill switch. New paper size goes to zero.
2. Freeze the audit chain and record the source attestation digest.
3. If a secret was pasted, rotate it outside this repo and purge it from history.
4. Do not open a public issue that contains a secret or a wallet address.
5. A human reviews before the kill switch is cleared.

## Operating rules

- Market-data credentials, if ever added, stay read-only and separate from any future trade credential.
- Logs pass through `redact` before they are stored.
- Default deployment is research. Promoting a signal to a broker is a separate, human-approved system.
