"""Chainlit UI entrypoint for eComBot multi-agent orchestration."""
from __future__ import annotations

import os
import sys
from typing import Any, Dict, List

try:
    import chainlit as cl
except ImportError:  # pragma: no cover
    cl = None

# Allow `chainlit run src/ui/chainlit_app.py` to import project packages.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.agents.orchestrator import create_orchestrator_agent


ORCHESTRATOR = create_orchestrator_agent()


def _render_card(card: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize card payload for UI rendering."""
    return card


if cl:
    @cl.on_chat_start
    async def on_chat_start():
        cl.user_session.set("last_order_id", None)
        await cl.Message(content="eComBot is ready. Ask support or sales questions.").send()


    @cl.on_message
    async def on_message(message: cl.Message):
        user_text = message.content

        with cl.Step(name="Route request", type="run") as route_step:
            result = ORCHESTRATOR.process_user_input(user_text)
            route_step.output = f"route={result.get('route')} agent={result.get('agent')}"

        cards: List[Dict[str, Any]] = result.get("cards", [])
        elements: List[Any] = []
        for index, card in enumerate(cards, start=1):
            elements.append(
                cl.Text(
                    name=f"card_{index}",
                    content=str(_render_card(card)),
                    display="inline",
                )
            )

        reasoning = result.get("reasoning", [])
        if reasoning:
            reasoning_text = "\n".join(
                [f"- [{step.get('type', 'step')}] {step.get('description', '')}" for step in reasoning]
            )
            elements.append(
                cl.Text(name="reasoning", content=reasoning_text, display="side")
            )

        action_buttons = [
            cl.Action(name="show_order_help", value="order_help", payload={"kind": "order"}, label="Order help"),
            cl.Action(name="show_sales_help", value="sales_help", payload={"kind": "sales"}, label="Sales help"),
        ]

        await cl.Message(content=result.get("text", ""), elements=elements, actions=action_buttons).send()

    @cl.action_callback("show_order_help")
    async def show_order_help(_: cl.Action):
        await cl.Message(content="Share your order ID (example: ORD-001) and I can track or cancel it.").send()

    @cl.action_callback("show_sales_help")
    async def show_sales_help(_: cl.Action):
        await cl.Message(content="Tell me your budget and product type, and I will recommend options.").send()
