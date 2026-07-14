"""Product management tools for eComBot - Day 04 implementation"""
from typing import Dict, Any, List
import re
from langchain.tools import tool
import logging

logger = logging.getLogger(__name__)

PRODUCT_ID_PATTERN = re.compile(r"^PRD-\d{3}$")

# Mock products database
MOCK_PRODUCTS = {
    "PRD-101": {
        "product_id": "PRD-101",
        "name": "Laptop Stand",
        "description": "Adjustable aluminum laptop stand",
        "price": "$45.99",
        "stock": 45,
        "category": "Accessories",
    },
    "PRD-102": {
        "product_id": "PRD-102",
        "name": "USB-C Cable",
        "description": "High-speed USB-C charging and data cable",
        "price": "$6.49",
        "stock": 150,
        "category": "Cables",
    },
    "PRD-103": {
        "product_id": "PRD-103",
        "name": "Mechanical Keyboard",
        "description": "RGB Mechanical Keyboard with Cherry MX switches",
        "price": "$129.99",
        "stock": 12,
        "category": "Keyboards",
    },
}


@tool
def lookup_product(product_name: str) -> Dict[str, Any]:
    """
    Look up a product by name or partial name.
    
    Args:
        product_name: The name or partial name of the product
        
    Returns:
        Product details or error message
    """
    logger.info(f"Looking up product: {product_name}")
    
    if not product_name or not isinstance(product_name, str):
        return {"error": "Invalid product name provided."}
    
    product_name_lower = product_name.lower()
    
    # Search for product by name
    for product_id, product in MOCK_PRODUCTS.items():
        if product_name_lower in product["name"].lower():
            logger.info(f"Found product: {product['name']}")
            return product
    
    # Product not found
    return {"error": f"Product '{product_name}' not found in our catalog."}


@tool
def check_stock(product_id: str) -> Dict[str, Any]:
    """
    Check stock availability for a product.
    
    Args:
        product_id: The product ID (e.g., "PRD-101")
        
    Returns:
        Stock information or error message
    """
    logger.info(f"Checking stock for product: {product_id}")
    
    if not product_id or not isinstance(product_id, str):
        return {"error": "Invalid product ID provided."}

    product_id = product_id.strip().upper()
    if not PRODUCT_ID_PATTERN.match(product_id):
        return {"error": "Invalid product ID format. Expected PRD-101 style value."}
    
    if product_id in MOCK_PRODUCTS:
        product = MOCK_PRODUCTS[product_id]
        stock_status = "In Stock" if product["stock"] > 0 else "Out of Stock"
        return {
            "product_id": product_id,
            "product_name": product["name"],
            "stock": product["stock"],
            "status": stock_status,
        }
    
    return {"error": f"Product {product_id} not found."}
