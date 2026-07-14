"""Output guardrails for PII and off-topic checks."""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class OutputGuardDecision:
    """Structured post-generation safety decision."""

    allowed: bool
    reason: str
    action: str
    sanitized_text: str


class OutputGuard:
    """Detect simple leakage and redact sensitive output."""

    _EMAIL = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+")
    _PHONE = re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b")
    _SSN = re.compile(r"\\b\\d{3}-\\d{2}-\\d{4}\\b")

    _OFF_TOPIC = [
        "build a bomb",
        "malware",
        "credit card dump",
    ]

    def evaluate(self, response_text: str) -> OutputGuardDecision:
        """Return pass/block/redact decision for model output."""
        if not response_text:
            return OutputGuardDecision(True, "empty_response", "pass", "")

        lower_text = response_text.lower()
        for marker in self._OFF_TOPIC:
            if marker in lower_text:
                return OutputGuardDecision(False, "unsafe_topic", "block", "")

        sanitized = response_text
        redacted = False

        if self._EMAIL.search(sanitized):
            sanitized = self._EMAIL.sub("[redacted_email]", sanitized)
            redacted = True
        if self._PHONE.search(sanitized):
            sanitized = self._PHONE.sub("[redacted_phone]", sanitized)
            redacted = True
        if self._SSN.search(sanitized):
            sanitized = self._SSN.sub("[redacted_ssn]", sanitized)
            redacted = True

        if redacted:
            return OutputGuardDecision(True, "pii_redacted", "redact", sanitized)

        return OutputGuardDecision(True, "safe", "pass", response_text)
