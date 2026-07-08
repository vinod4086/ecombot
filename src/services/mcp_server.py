"""FastMCP server implementation for eComBot external integrations - Day 08"""
import json
import logging
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
import uvicorn

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="eComBot MCP Server", version="1.0.0")

# Mock data for orders and inventory
MOCK_ORDERS = {
    "ORD-001": {
        "order_id": "ORD-001",
        "customer_name": "Priya",
        "status": "Shipped",
        "eta": "2026-06-05",
        "carrier": "BlueDart",
        "items": [{"sku": "PRD-101", "name": "Laptop Stand", "qty": 1}],
        "total": "$45.99",
    },
    "ORD-002": {
        "order_id": "ORD-002",
        "customer_name": "Rajesh",
        "status": "Processing",
        "eta": "2026-06-07",
        "carrier": "DTDC",
        "items": [{"sku": "PRD-102", "name": "USB-C Cable", "qty": 2}],
        "total": "$12.98",
    },
}

MOCK_INVENTORY = {
    "PRD-101": {
        "product_id": "PRD-101",
        "name": "Laptop Stand",
        "stock": 45,
        "status": "In Stock",
        "variants": ["Black", "Silver", "Gold"],
    },
    "PRD-102": {
        "product_id": "PRD-102",
        "name": "USB-C Cable",
        "stock": 150,
        "status": "In Stock",
        "variants": ["3ft", "6ft", "10ft"],
    },
    "PRD-103": {
        "product_id": "PRD-103",
        "name": "Mechanical Keyboard",
        "stock": 0,
        "status": "Out of Stock",
        "variants": ["RGB", "Brown Switches", "Blue Switches"],
    },
}


class MCPTools:
    """MCP tool implementations for eComBot"""

    @staticmethod
    def get_order_status(order_id: str) -> Dict[str, Any]:
        """Get order status by order ID"""
        if not order_id:
            return {"error": "Order ID is required"}

        if order_id not in MOCK_ORDERS:
            return {"error": f"Order {order_id} not found"}

        return MOCK_ORDERS[order_id]

    @staticmethod
    def get_order_details(order_id: str) -> Dict[str, Any]:
        """Get detailed order information"""
        if not order_id:
            return {"error": "Order ID is required"}

        if order_id not in MOCK_ORDERS:
            return {"error": f"Order {order_id} not found"}

        order = MOCK_ORDERS[order_id]
        return {
            "order_id": order["order_id"],
            "customer": order["customer_name"],
            "status": order["status"],
            "eta": order["eta"],
            "carrier": order["carrier"],
            "items": order["items"],
            "total": order["total"],
            "tracking_available": order["status"] in ["Shipped", "Delivered"],
        }

    @staticmethod
    def cancel_order(order_id: str) -> Dict[str, Any]:
        """Cancel an order"""
        if not order_id:
            return {"error": "Order ID is required"}

        if order_id not in MOCK_ORDERS:
            return {"error": f"Order {order_id} not found"}

        order = MOCK_ORDERS[order_id]

        if order["status"] == "Delivered":
            return {"error": "Cannot cancel delivered orders"}
        elif order["status"] == "Shipped":
            return {"error": "Cannot cancel shipped orders"}

        order["status"] = "Cancelled"
        return {
            "success": True,
            "message": f"Order {order_id} cancelled successfully",
            "refund_amount": order["total"],
        }

    @staticmethod
    def check_stock(product_id: str) -> Dict[str, Any]:
        """Check stock availability"""
        if not product_id:
            return {"error": "Product ID is required"}

        if product_id not in MOCK_INVENTORY:
            return {"error": f"Product {product_id} not found"}

        product = MOCK_INVENTORY[product_id]
        return {
            "product_id": product_id,
            "name": product["name"],
            "stock": product["stock"],
            "status": product["status"],
        }

    @staticmethod
    def list_variants(product_id: str) -> Dict[str, Any]:
        """List product variants"""
        if not product_id:
            return {"error": "Product ID is required"}

        if product_id not in MOCK_INVENTORY:
            return {"error": f"Product {product_id} not found"}

        product = MOCK_INVENTORY[product_id]
        return {
            "product_id": product_id,
            "name": product["name"],
            "variants": product["variants"],
        }


# Initialize tools
tools = MCPTools()


# FastAPI endpoints for tools
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "eComBot MCP Server"}


@app.post("/tools/get_order_status")
def get_order_status(order_id: str):
    """Get order status tool endpoint"""
    result = tools.get_order_status(order_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@app.post("/tools/get_order_details")
def get_order_details(order_id: str):
    """Get order details tool endpoint"""
    result = tools.get_order_details(order_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@app.post("/tools/cancel_order")
def cancel_order(order_id: str):
    """Cancel order tool endpoint"""
    result = tools.cancel_order(order_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.post("/tools/check_stock")
def check_stock(product_id: str):
    """Check stock tool endpoint"""
    result = tools.check_stock(product_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@app.post("/tools/list_variants")
def list_variants(product_id: str):
    """List variants tool endpoint"""
    result = tools.list_variants(product_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@app.get("/tools")
def list_tools():
    """List all available tools"""
    return {
        "tools": [
            {
                "name": "get_order_status",
                "description": "Get the status of an order",
                "parameters": {"order_id": "str"},
            },
            {
                "name": "get_order_details",
                "description": "Get detailed order information",
                "parameters": {"order_id": "str"},
            },
            {
                "name": "cancel_order",
                "description": "Cancel an order if possible",
                "parameters": {"order_id": "str"},
            },
            {
                "name": "check_stock",
                "description": "Check product stock availability",
                "parameters": {"product_id": "str"},
            },
            {
                "name": "list_variants",
                "description": "List product variants",
                "parameters": {"product_id": "str"},
            },
        ]
    }


def run_server(host: str = "0.0.0.0", port: int = 8001):
    """Run the MCP server"""
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    run_server()
