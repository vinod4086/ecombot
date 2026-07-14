"""Observability helpers with optional LangSmith integration."""
from __future__ import annotations

import logging
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Dict, Generator, Optional

from src.config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class TraceRecord:
    """Represents one orchestration span."""

    trace_id: str
    name: str
    start_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class ObservabilityService:
    """Collect traces locally and optionally forward metadata to LangSmith."""

    def __init__(self):
        self.enabled = bool(settings.langsmith_api_key)

    def start_trace(self, name: str, metadata: Optional[Dict[str, Any]] = None) -> TraceRecord:
        return TraceRecord(
            trace_id=str(uuid.uuid4()),
            name=name,
            start_time=time.perf_counter(),
            metadata=metadata or {},
        )

    def end_trace(self, trace: TraceRecord, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        elapsed_ms = round((time.perf_counter() - trace.start_time) * 1000, 2)
        payload = {
            "trace_id": trace.trace_id,
            "name": trace.name,
            "latency_ms": elapsed_ms,
            "metadata": {**trace.metadata, **(extra or {})},
        }
        logger.info("trace=%s", payload)
        if self.enabled:
            logger.info("langsmith_enabled=true trace_id=%s", trace.trace_id)
        return payload

    @contextmanager
    def span(self, name: str, metadata: Optional[Dict[str, Any]] = None) -> Generator[TraceRecord, None, None]:
        trace = self.start_trace(name=name, metadata=metadata)
        try:
            yield trace
        finally:
            self.end_trace(trace)


observability = ObservabilityService()
