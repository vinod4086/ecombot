"""Turn-based voice loop scaffold for eComBot (Day 11)."""
from __future__ import annotations

import json
import logging
import re
import time
from dataclasses import dataclass
from typing import Callable, Dict, Optional

from src.agents.orchestrator import create_orchestrator_agent

logger = logging.getLogger(__name__)


@dataclass
class VoiceTurnMetrics:
    capture_ms: float
    stt_ms: float
    orchestration_ms: float
    tts_ms: float
    total_ms: float


class VoiceLoop:
    """Simple voice interaction loop with pluggable STT/TTS callables."""

    def __init__(
        self,
        stt_fn: Callable[[bytes], str],
        tts_fn: Callable[[str], None],
        audio_capture_fn: Callable[[], bytes],
    ):
        self.stt_fn = stt_fn
        self.tts_fn = tts_fn
        self.audio_capture_fn = audio_capture_fn
        self.orchestrator = create_orchestrator_agent()

    def run_once(self) -> Dict[str, object]:
        start = time.perf_counter()

        capture_start = time.perf_counter()
        audio = self.audio_capture_fn()
        capture_ms = (time.perf_counter() - capture_start) * 1000

        stt_start = time.perf_counter()
        transcript = self.stt_fn(audio)
        stt_ms = (time.perf_counter() - stt_start) * 1000

        confirmed_transcript = self._confirm_order_id_if_needed(transcript)

        orchestration_start = time.perf_counter()
        result = self.orchestrator.process_user_input(confirmed_transcript)
        orchestration_ms = (time.perf_counter() - orchestration_start) * 1000

        tts_start = time.perf_counter()
        self.tts_fn(result.get("text", ""))
        tts_ms = (time.perf_counter() - tts_start) * 1000

        metrics = VoiceTurnMetrics(
            capture_ms=round(capture_ms, 2),
            stt_ms=round(stt_ms, 2),
            orchestration_ms=round(orchestration_ms, 2),
            tts_ms=round(tts_ms, 2),
            total_ms=round((time.perf_counter() - start) * 1000, 2),
        )

        trace_summary = {
            "transcript": confirmed_transcript,
            "route": result.get("route"),
            "agent": result.get("agent"),
            "metrics": metrics.__dict__,
        }
        logger.info("voice_trace=%s", json.dumps(trace_summary))

        return {
            "result": result,
            "metrics": metrics.__dict__,
        }

    def _confirm_order_id_if_needed(self, transcript: str) -> str:
        match = re.search(r"ord[-\s]?(\d{3,})", transcript.lower())
        if not match:
            return transcript

        order_id = f"ORD-{match.group(1)}"
        prompt = f"I heard order ID {order_id}. Say yes to confirm or say the corrected order ID."
        self.tts_fn(prompt)

        correction_audio = self.audio_capture_fn()
        correction_text = self.stt_fn(correction_audio).strip().lower()

        if correction_text in {"yes", "yeah", "correct"}:
            return transcript.replace(match.group(0), order_id)

        corrected_match = re.search(r"ord[-\s]?(\d{3,})", correction_text)
        if corrected_match:
            corrected_order = f"ORD-{corrected_match.group(1)}"
            return transcript.replace(match.group(0), corrected_order)

        return transcript


# Placeholder adapters for local manual testing

def dummy_capture() -> bytes:
    """Capture adapter for testing without microphone integration."""
    return input("Speak (type text instead): ").encode("utf-8")


def dummy_stt(audio: bytes) -> str:
    """Decode typed input as transcript for local testing."""
    return audio.decode("utf-8")


def dummy_tts(text: str) -> None:
    """Print synthesized speech text for local testing."""
    print(f"BOT(voice): {text}")


def run_demo() -> None:
    loop = VoiceLoop(stt_fn=dummy_stt, tts_fn=dummy_tts, audio_capture_fn=dummy_capture)
    while True:
        output = loop.run_once()
        if output["result"].get("text", "").lower().strip() in {"exit", "quit"}:
            break


if __name__ == "__main__":
    run_demo()
