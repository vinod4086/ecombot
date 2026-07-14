"""Orchestrator agent for routing support and sales requests."""
from __future__ import annotations

import logging
import re
from typing import Any, Dict, List

from src.agents.sales_agent import create_sales_agent
from src.agents.support_agent import create_support_agent
from src.guards.input_guard import InputGuard
from src.guards.output_guard import OutputGuard
from src.services.observability import observability

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """Entry-point agent that routes each message to the right specialist."""

    def __init__(self):
        self.support_agent = create_support_agent()
        self.sales_agent = create_sales_agent()
        self.input_guard = InputGuard()
        self.output_guard = OutputGuard()

    def process_user_input(self, user_message: str) -> Dict[str, Any]:
        """Process message with guardrails, routing, and output normalization."""
        with observability.span("orchestrator_turn", {"message": user_message}) as trace:
            guard_decision = self.input_guard.evaluate(user_message)
            if not guard_decision.allowed and guard_decision.action == "block":
                blocked_text = "I cannot process that request because it appears unsafe. Please rephrase your request."
                return self._finalize(
                    route="blocked",
                    text=blocked_text,
                    payload={"guard": guard_decision.__dict__, "cards": [], "steps": []},
                    trace_id=trace.trace_id,
                )

            if guard_decision.action == "redact":
                user_message = self.input_guard.sanitize(user_message)

            route = self._classify_route(user_message)
            logger.info("routing_decision route=%s message=%s", route, user_message)

            if route == "support":
                payload = self._run_support(user_message)
            elif route == "sales":
                payload = self._run_sales(user_message)
            elif route == "mixed":
                payload = self._run_mixed(user_message)
            else:
                payload = {
                    "agent": "orchestrator",
                    "text": "I can help with order support, cancellations, returns, product comparisons, and recommendations.",
                    "cards": [],
                    "steps": [{"name": "Self-answer", "status": "completed"}],
                }

            return self._finalize(route=route, text=payload.get("text", ""), payload=payload, trace_id=trace.trace_id)

    def _finalize(self, route: str, text: str, payload: Dict[str, Any], trace_id: str) -> Dict[str, Any]:
        output_decision = self.output_guard.evaluate(text)
        if not output_decision.allowed:
            text = "I cannot provide that response safely. Please ask an e-commerce support or shopping question."
        elif output_decision.action == "redact":
            text = output_decision.sanitized_text

        return {
            "route": route,
            "agent": payload.get("agent", "orchestrator"),
            "text": text,
            "cards": payload.get("cards", []),
            "steps": payload.get("steps", []),
            "reasoning": payload.get("reasoning", []),
            "trace_id": trace_id,
            "guard": payload.get("guard", {}),
        }

    def _classify_route(self, message: str) -> str:
        lower = message.lower()

        support_tokens = ["order", "delivery", "return", "refund", "cancel", "issue", "complaint"]
        sales_tokens = ["recommend", "compare", "buy", "budget", "best", "spec", "product"]

        support_hits = sum(1 for token in support_tokens if token in lower)
        sales_hits = sum(1 for token in sales_tokens if token in lower)

        if support_hits and sales_hits:
            return "mixed"
        if support_hits:
            return "support"
        if sales_hits:
            return "sales"
        return "self"

    def _run_support(self, message: str) -> Dict[str, Any]:
        text = self.support_agent.process_user_input(message)
        card = self._extract_order_card(text, message)
        return {
            "agent": "support",
            "text": text,
            "cards": [card] if card else [],
            "steps": [{"name": "Support agent", "status": "completed"}],
        }

    def _run_sales(self, message: str) -> Dict[str, Any]:
        return self.sales_agent.process_user_input(message)

    def _run_mixed(self, message: str) -> Dict[str, Any]:
        support_payload = self._run_support(message)
        sales_payload = self.sales_agent.process_user_input(
            message,
            context={"support_summary": support_payload.get("text", "")},
        )

        text = (
            f"Support update: {support_payload.get('text', '')}\n"
            f"Sales suggestion: {sales_payload.get('text', '')}"
        )
        steps: List[Dict[str, str]] = [
            {"name": "Plan mixed request", "status": "completed"},
            {"name": "Support sub-task", "status": "completed"},
            {"name": "Sales sub-task", "status": "completed"},
        ]
        cards = support_payload.get("cards", []) + sales_payload.get("cards", [])
        reasoning = sales_payload.get("reasoning", [])

        return {
            "agent": "orchestrator",
            "text": text,
            "cards": cards,
            "steps": steps,
            "reasoning": reasoning,
        }

    def _extract_order_card(self, text: str, message: str) -> Dict[str, str] | None:
        order_match = re.search(r"ORD-\d+", message.upper())
        if not order_match:
            return None
        order_id = order_match.group(0)

        status = "Unknown"
        if "shipped" in text.lower():
            status = "Shipped"
        elif "processing" in text.lower():
            status = "Processing"
        elif "cancelled" in text.lower():
            status = "Cancelled"

        return {
            "type": "order",
            "order_id": order_id,
            "status": status,
            "summary": text,
        }


def create_orchestrator_agent() -> OrchestratorAgent:
    """Factory for orchestrator agent."""
    return OrchestratorAgent()
