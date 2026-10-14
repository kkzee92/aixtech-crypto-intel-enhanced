# Security Policy

This is a research paper-only system. Report issues privately if they involve secrets or sensitive data.

Do not open public issues containing API keys, wallet addresses, or personal data.

Supported branch: `main`.

Version 0.6 adds expanded redaction patterns, length-limited sanitization, multi-candle anomaly scoring, and adaptive risk controls. See docs/security-architecture.md for the control design.

In scope: the `crypto_intel` package, risk gate, audit log, and CI tripwires.
Out of scope: live trading profit claims. This repository cannot place live orders.
