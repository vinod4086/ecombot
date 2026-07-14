"""Order management tools for eComBot - Day 03 and Day 04 implementation"""
from typing import Dict, Any
import re
from langchain.tools import tool
import logging

logger = logging.getLogger(__name__)

ORDER_ID_PATTERN = re.compile(r"^ORD-\d{3}$")

# Day 03: Mock orders for in-memory testing
MOCK_ORDERS = {
    "ORD-001": {
        "order_id": "ORD-001",
        "status": "Shipped",
        "eta": "5 Jun 2026",
        "carrier": "BlueDart",
        "items": [{"sku": "PRD-101", "name": "Laptop Stand", "qty": 1}],
        "total": "$45.99",
    },
    "ORD-002": {
        "order_id": "ORD-002",
        "status": "Processing",
        "eta": "7 Jun 2026",
        "carrier": "DTDC",
        "items": [{"sku": "PRD-102", "name": "USB-C Cable", "qty": 2}],
        "total": "$12.98",
    },
    "ORD-003": {
        "order_id": "ORD-003",
        "status": "Delivered",
        "eta": "Already delivered",
        "carrier": "FedEx",
        "items": [{"sku": "PRD-103", "name": "Mechanical Keyboard", "qty": 1}],
        "total": "$129.99",
    },
}


@tool
def get_order_status(order_id: str) -> Dict[str, Any]:
    """
    Get the status of an order by order ID.
    
    Args:
        order_id: The order ID to look up (e.g., "ORD-001")
        
    Returns:
        A dictionary with order status details or an error message
    """
    logger.info(f"Looking up order status for order_id: {order_id}")
    
    # Validate order ID format
    if not order_id or not isinstance(order_id, str):
        return {"error": "Invalid order ID format. Please provide a valid order ID."}
    if not ORDER_ID_PATTERN.match(order_id.strip().upper()):
        return {"error": "Invalid order ID format. Expected ORD-001 style value."}

    order_id = order_id.strip().upper()
    
    # Check for order in mock data
    if order_id in MOCK_ORDERS:
        order = MOCK_ORDERS[order_id].copy()
        logger.info(f"Found order {order_id}: {order['status']}")
        return order
    
    # Order not found
    return {"error": f"Order {order_id} not found in system. Please verify the order ID."}


@tool
def cancel_order(order_id: str) -> Dict[str, Any]:
    """
    Cancel an order if it hasn't been shipped.
    
    Args:
        order_id: The order ID to cancel
        
    Returns:
        A dictionary with cancellation status or error message
    """
    logger.info(f"Attempting to cancel order: {order_id}")
    
    # Validate order ID
    if not order_id or not isinstance(order_id, str):
        return {"error": "Invalid order ID format."}
    if not ORDER_ID_PATTERN.match(order_id.strip().upper()):
        return {"error": "Invalid order ID format. Expected ORD-001 style value."}

    order_id = order_id.strip().upper()
    
    # Check if order exists
    if order_id not in MOCK_ORDERS:
        return {"error": f"Order {order_id} not found."}
    
    order = MOCK_ORDERS[order_id]
    
    # Check if order can be cancelled
    if order["status"] == "Delivered":
        return {"error": f"Order {order_id} has already been delivered and cannot be cancelled."}
    elif order["status"] == "Shipped":
        return {"error": f"Order {order_id} has already shipped and cannot be cancelled."}
    elif order["status"] == "Cancelled":
        return {"error": f"Order {order_id} is already cancelled."}
    
    # Cancel the order
    MOCK_ORDERS[order_id]["status"] = "Cancelled"
    logger.info(f"Successfully cancelled order {order_id}")
    return {
        "success": True,
        "message": f"Order {order_id} has been cancelled successfully.",
        "cancelled_items": order["items"],
        "refund_amount": order["total"],
    }
