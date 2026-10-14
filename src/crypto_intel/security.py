"""Cyber and data-security controls for the information system.

Enhanced research control plane (v0.7). Not a certified security product.
Adds expanded secret patterns, improved multi-bar anomaly scoring with consistency, and stricter sanitization.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from crypto_intel.models import AuditEvent, ExecutionMode

# Expanded patterns for better secret and sensitive data detection
SECRET_PATTERNS = (
    re.compile(r"(?i)(api[_-]?key|secret|password|token|private[_-]?key|mnemonic|seed)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{8,}"),
    re.compile(r"\b(?:sk|pk)_(?:live|test)_[A-Za-z0-9]{8,}\b"),
    re.compile(r"\b[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    re.compile(r"\b(?:mnemonic|seed phrase|private key|wallet private)\b", re.IGNORECASE),
    re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),  # JWT-like
    re.compile(r"\b[0-9a-fA-F]{64}\b"),  # hex private key style
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),  # AWS access key style
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"),  # Slack token style
    re.compile(r"\b[A-Za-z0-9+/]{40,}={0,2}\b"),  # longer base64-like
)

WALLET_PATTERN = re.compile(r"\b0x[a-fA-F0-9]{40}\b")
PHONE_PATTERN = re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")


@dataclass(frozen=True)
class DataClassification:
    field: str
    level: str
    retention: str


CLASSIFICATION = (
    DataClassification("symbol", "public", "research retention"),
    DataClassification("ohlcv", "public-market", "research retention"),
    DataClassification("exchange_api_key", "secret", "never stored"),
    DataClassification("wallet_address", "sensitive-identifier", "do not fixture"),
    DataClassification("account_email", "personal", "do not collect"),
    DataClassification("funding_rate", "public-market", "research retention"),
    DataClassification("phone", "personal", "do not collect"),
)


def redact(text: str) -> str:
    cleaned = text
    for pattern in SECRET_PATTERNS:
        cleaned = pattern.sub("[REDACTED]", cleaned)
    cleaned = WALLET_PATTERN.sub("[WALLET]", cleaned)
    cleaned = PHONE_PATTERN.sub("[PHONE]", cleaned)
    return cleaned


def contains_secret(text: str) -> bool:
    return (
        any(pattern.search(text) for pattern in SECRET_PATTERNS)
        or bool(WALLET_PATTERN.search(text))
        or bool(PHONE_PATTERN.search(text))
    )


def assert_paper_only(mode: ExecutionMode) -> None:
    if mode is not ExecutionMode.PAPER:
        raise PermissionError("live execution is disabled; this system is paper-only")


def hash_event(previous_hash: str, sequence: int, action: str, detail: str) -> str:
    material = f"{previous_hash}|{sequence}|{action}|{detail}".encode()
    return hashlib.sha256(material).hexdigest()


def anomaly_score(price_change_pct: float, volume_ratio: float, staleness_minutes: float = 0.0, consecutive_jumps: int = 0, consistency: float = 1.0) -> float:
    """Enhanced research anomaly score for feed integrity with multi-candle context and consistency. Not a production detector."""
    score = 0.0
    if abs(price_change_pct) > 0.25:
        score += 0.6
    elif abs(price_change_pct) > 0.15:
        score += 0.3
    if volume_ratio > 5.0:
        score += 0.4
    elif volume_ratio > 3.0:
        score += 0.2
    if staleness_minutes > 15:
        score += 0.3
    elif staleness_minutes > 5:
        score += 0.1
    if consecutive_jumps >= 2:
        score += 0.25
    if consistency < 0.6:
        score += 0.2
    return min(score, 1.0)


def sanitize_input(text: str, max_len: int = 2000) -> str:
    """Research sanitization: redact, strip control characters, and length-limit. Not a full sanitizer."""
    cleaned = redact(text)
    cleaned = re.sub(r"[\x00-\x1F\x7F]", "", cleaned)
    return cleaned[:max_len]


class AuditLog:
    """Append-only hash chain. Tampering changes the next digest."""

    def __init__(self) -> None:
        self.events: list[AuditEvent] = []
        self._previous = "GENESIS"

    def append(self, action: str, detail: str) -> AuditEvent:
        safe_detail = sanitize_input(detail)
        sequence = len(self.events) + 1
        digest = hash_event(self._previous, sequence, action, safe_detail)
        event = AuditEvent(sequence, action, safe_detail, self._previous, digest)
        self.events.append(event)
        self._previous = digest
        return event

    def verify(self) -> bool:
        previous = "GENESIS"
        for event in self.events:
            expected = hash_event(previous, event.sequence, event.action, event.detail)
            if event.previous_hash != previous or event.digest != expected:
                return False
            previous = event.digest
        return True
