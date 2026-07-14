"""Input guardrails for prompt-injection and unsafe requests."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List


@dataclass
class GuardDecision:
    """Structured guardrail decision for upstream components."""

    allowed: bool
    reason: str
    action: str


class InputGuard:
    """Detect simple prompt injection and role-escalation patterns."""

    _BLOCK_PATTERNS: List[re.Pattern] = [
        re.compile(r"ignore\s+all\s+previous\s+instructions", re.IGNORECASE),
        re.compile(r"show\s+me\s+your\s+system\s+prompt", re.IGNORECASE),
        re.compile(r"reveal\s+your\s+system\s+prompt", re.IGNORECASE),
        re.compile(r"you\s+are\s+now", re.IGNORECASE),
        re.compile(r"act\s+as\s+an?\s+admin", re.IGNORECASE),
        re.compile(r"reveal\s+(?:your\s+)?hidden\s+instructions", re.IGNORECASE),
    ]

    _REDACT_PATTERNS: List[re.Pattern] = [
        re.compile(r"system\s+prompt", re.IGNORECASE),
    ]

    def evaluate(self, user_message: str) -> GuardDecision:
        """Return pass/block/redact decision for an inbound message."""
        if not user_message or not user_message.strip():
            return GuardDecision(False, "empty_message", "block")

        for pattern in self._BLOCK_PATTERNS:
            if pattern.search(user_message):
                return GuardDecision(False, "prompt_injection_detected", "block")

        for pattern in self._REDACT_PATTERNS:
            if pattern.search(user_message):
                return GuardDecision(True, "sensitive_prompt_reference", "redact")

        return GuardDecision(True, "safe", "pass")

    def sanitize(self, user_message: str) -> str:
        """Apply lightweight redaction when decision action is redact."""
        sanitized = user_message
        sanitized = re.sub(r"system\s+prompt", "internal instructions", sanitized, flags=re.IGNORECASE)
        return sanitized
