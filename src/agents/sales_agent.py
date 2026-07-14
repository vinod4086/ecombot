"""Sales agent with ReAct-style recommendation reasoning."""
from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional

from src.tools.product_tools import MOCK_PRODUCTS, check_stock, lookup_product

logger = logging.getLogger(__name__)


class SalesAgent:
    """Sales-focused agent for recommendations and product comparisons."""

    def __init__(self, max_iterations: int = 3):
        self.max_iterations = max_iterations
        self.session_state: Dict[str, Any] = {}

    def process_user_input(self, user_message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Return structured sales response with reasoning steps."""
        context = context or {}
        reasoning: List[Dict[str, str]] = []

        constraints = self._extract_constraints(user_message)
        if context.get("support_summary"):
            constraints["support_context"] = context["support_summary"]
            reasoning.append({
                "type": "observation",
                "description": "Used support-agent result as additional context.",
            })

        rejection_note = self._extract_rejection(user_message)
        if rejection_note:
            reasoning.append({
                "type": "reflection",
                "description": f"User rejected previous option: {rejection_note}",
            })
            self.session_state["last_rejection"] = rejection_note

        reasoning.append({
            "type": "thought",
            "description": f"Extracted constraints: {constraints}",
        })

        candidates = self._find_candidates(constraints)
        reasoning.append({
            "type": "action",
            "description": f"Retrieved {len(candidates)} candidate products from catalog.",
        })

        if not candidates:
            fallback = "I could not find a matching item in the current catalog. Try sharing a broader budget or category."
            return {
                "agent": "sales",
                "text": fallback,
                "reasoning": reasoning,
                "steps": [{"name": "Find candidates", "status": "no_match"}],
                "cards": [],
            }

        ranked = self._rank_candidates(candidates, constraints)
        reasoning.append({
            "type": "observation",
            "description": "Ranked candidates by budget fit and stock availability.",
        })

        best = ranked[0]
        stock_info = check_stock.invoke({"product_id": best["product_id"]})
        reasoning.append({
            "type": "action",
            "description": f"Checked stock for {best['product_id']}.",
        })

        summary = self._compose_summary(best, stock_info, constraints)
        self.session_state["last_recommendation"] = best

        return {
            "agent": "sales",
            "text": summary,
            "reasoning": reasoning,
            "steps": [
                {"name": "Extract constraints", "status": "completed"},
                {"name": "Retrieve candidates", "status": "completed"},
                {"name": "Check stock", "status": "completed"},
            ],
            "cards": [
                {
                    "type": "product",
                    "product_id": best["product_id"],
                    "name": best["name"],
                    "price": best["price"],
                    "category": best["category"],
                    "stock_status": stock_info.get("status", "Unknown"),
                }
            ],
        }

    def _extract_constraints(self, message: str) -> Dict[str, Any]:
        constraints: Dict[str, Any] = {}
        lower = message.lower()

        budget_match = re.search(r"(?:under|below|less than)\s*\$?(\d+)", lower)
        if budget_match:
            constraints["max_budget"] = float(budget_match.group(1))

        category_map = {
            "keyboard": "Keyboards",
            "cable": "Cables",
            "stand": "Accessories",
            "accessory": "Accessories",
            "mouse": "Peripherals",
        }
        for token, category in category_map.items():
            if token in lower:
                constraints["category"] = category
                break

        if "compare" in lower:
            constraints["mode"] = "compare"
        else:
            constraints["mode"] = "recommend"

        return constraints

    def _extract_rejection(self, message: str) -> Optional[str]:
        lower = message.lower()
        rejection_markers = ["too expensive", "doesn't work", "not good", "not suitable", "over my budget"]
        for marker in rejection_markers:
            if marker in lower:
                return marker
        return None

    def _find_candidates(self, constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
        products = list(MOCK_PRODUCTS.values())

        category = constraints.get("category")
        if category:
            products = [p for p in products if p.get("category") == category]

        max_budget = constraints.get("max_budget")
        if max_budget is not None:
            filtered = []
            for product in products:
                numeric_price = float(product["price"].replace("$", ""))
                if numeric_price <= max_budget:
                    filtered.append(product)
            products = filtered

        if products:
            return products

        # RAG-backed fallback: if semantic lookup finds a product mention, include it.
        try:
            from src.rag.retriever import get_retriever

            retriever = get_retriever()
            _, metadata = retriever.retrieve("budget recommendation", n_results=2)
            for meta in metadata:
                product_id = meta.get("product_id")
                if product_id and product_id in MOCK_PRODUCTS:
                    products.append(MOCK_PRODUCTS[product_id])
        except Exception:
            logger.warning("RAG retriever unavailable; falling back to static catalog only.")

        return products

    def _rank_candidates(self, candidates: List[Dict[str, Any]], constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
        max_budget = constraints.get("max_budget")

        def score(product: Dict[str, Any]) -> float:
            price = float(product["price"].replace("$", ""))
            stock = product.get("stock", 0)
            budget_score = 1.0
            if max_budget is not None:
                budget_score = max(0.0, 1.0 - abs(max_budget - price) / max(max_budget, 1.0))
            stock_score = min(stock / 100.0, 1.0)
            return budget_score * 0.7 + stock_score * 0.3

        return sorted(candidates, key=score, reverse=True)

    def _compose_summary(self, product: Dict[str, Any], stock_info: Dict[str, Any], constraints: Dict[str, Any]) -> str:
        budget_hint = ""
        if "max_budget" in constraints:
            budget_hint = f" within your ${int(constraints['max_budget'])} budget"
        return (
            f"I recommend {product['name']} ({product['product_id']}) at {product['price']}{budget_hint}. "
            f"Current stock: {stock_info.get('stock', 'unknown')} ({stock_info.get('status', 'Unknown')})."
        )


def create_sales_agent() -> SalesAgent:
    """Factory for sales agent."""
    return SalesAgent()
