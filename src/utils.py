"""Utility module for eComBot - Helpers and common functions"""

import os
import logging
from pathlib import Path
from typing import Dict, Any

# Configure logging
def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Setup application logging"""
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger("ecombot")


# File utilities
def load_instruction_file(filepath: str) -> str:
    """Load instruction from file"""
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Instruction file not found: {filepath}")


def ensure_data_files():
    """Ensure required data files exist"""
    required_files = [
        "data/products.json",
        "data/faq.json",
        "src/agents/support_instructions_v1.txt",
        "src/agents/support_instructions_v2.txt",
        "src/agents/support_instructions_v3.txt",
    ]
    
    for filepath in required_files:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Required file missing: {filepath}")


# Mock data utilities
def get_mock_order_data() -> Dict[str, Any]:
    """Get mock order data"""
    return {
        "ORD-001": {
            "order_id": "ORD-001",
            "status": "Shipped",
            "eta": "2026-06-05",
            "carrier": "BlueDart",
        },
        "ORD-002": {
            "order_id": "ORD-002",
            "status": "Processing",
            "eta": "2026-06-07",
            "carrier": "DTDC",
        },
        "ORD-003": {
            "order_id": "ORD-003",
            "status": "Delivered",
            "eta": "2026-05-28",
            "carrier": "FedEx",
        },
    }


def get_mock_product_data() -> Dict[str, Any]:
    """Get mock product data"""
    return {
        "PRD-101": {"name": "Laptop Stand", "price": "$45.99", "stock": 45},
        "PRD-102": {"name": "USB-C Cable", "price": "$6.49", "stock": 150},
        "PRD-103": {"name": "Mechanical Keyboard", "price": "$129.99", "stock": 12},
        "PRD-104": {"name": "Wireless Mouse", "price": "$34.99", "stock": 85},
        "PRD-105": {"name": "USB Hub", "price": "$25.99", "stock": 60},
    }


# Validation utilities
def validate_order_id(order_id: str) -> bool:
    """Validate order ID format"""
    if not order_id:
        return False
    return order_id.upper().startswith("ORD-") and len(order_id) >= 6


def validate_product_id(product_id: str) -> bool:
    """Validate product ID format"""
    if not product_id:
        return False
    return product_id.upper().startswith("PRD-") and len(product_id) >= 6


def sanitize_input(user_input: str, max_length: int = 1000) -> str:
    """Sanitize user input"""
    if not user_input:
        return ""
    
    # Strip whitespace
    sanitized = user_input.strip()
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


# Response formatting
def format_tool_result(tool_name: str, result: Dict[str, Any]) -> str:
    """Format tool result for display"""
    if "error" in result:
        return f"Error calling {tool_name}: {result['error']}"
    
    # Format based on tool type
    if tool_name == "get_order_status":
        return (f"Order {result.get('order_id')}: {result.get('status')} "
                f"(ETA: {result.get('eta')}, Carrier: {result.get('carrier')})")
    
    elif tool_name == "check_stock":
        return (f"{result.get('product_name')}: "
                f"{result.get('status')} ({result.get('stock')} units)")
    
    return str(result)


# Session utilities
def serialize_session(session_data: Dict[str, Any]) -> str:
    """Serialize session data to string"""
    import json
    return json.dumps(session_data)


def deserialize_session(session_str: str) -> Dict[str, Any]:
    """Deserialize session data from string"""
    import json
    try:
        return json.loads(session_str)
    except json.JSONDecodeError:
        return {}


# Status checks
def check_environment() -> Dict[str, bool]:
    """Check if all required components are available"""
    checks = {
        "env_file": os.path.exists(".env"),
        "data_files": all(os.path.exists(f) for f in [
            "data/products.json", "data/faq.json"
        ]),
        "source_files": all(os.path.exists(f) for f in [
            "src/agents/support_agent.py",
            "src/tools/order_tools.py",
            "src/config/settings.py",
        ]),
    }
    return checks


def print_environment_check():
    """Print environment check results"""
    checks = check_environment()
    print("\nEnvironment Check:")
    print("-" * 40)
    for check_name, result in checks.items():
        status = "✓" if result else "✗"
        print(f"{status} {check_name}")
    print("-" * 40)


if __name__ == "__main__":
    setup_logging("INFO")
    print_environment_check()
