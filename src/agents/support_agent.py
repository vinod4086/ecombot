"""Support agent implementation for eComBot - Core agent logic across all days"""
import logging
import re
from typing import Optional, Dict, Any
from langchain.tools import tool
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import BaseTool
from src.config.settings import settings
from src.tools.order_tools import get_order_status, cancel_order
from src.tools.product_tools import lookup_product, check_stock

logger = logging.getLogger(__name__)


class SupportAgent:
    """E-commerce support agent with tool calling and session state support"""

    def __init__(self, instruction: str = "", use_tools: bool = True, route_hint: str = "fast-faq"):
        """
        Initialize the support agent.
        
        Args:
            instruction: System instruction/prompt for the agent
            use_tools: Whether to enable tool calling
            route_hint: Routing hint for LLM gateway (Day 07: fast-faq or deep-support)
        """
        self.instruction = instruction or self._load_default_instruction()
        self.use_tools = use_tools
        self.route_hint = route_hint
        self.tools = self._get_tools() if use_tools else []
        self.session_state = {}  # Day 03: In-memory session state

    def _load_default_instruction(self) -> str:
        """Load default instruction from file"""
        try:
            with open("src/agents/support_instructions_v1.txt", "r") as f:
                return f.read()
        except FileNotFoundError:
            return self._get_default_instruction()

    def _get_default_instruction(self) -> str:
        """Get inline default instruction"""
        return """You are a helpful e-commerce support assistant for an electronics retailer. 
Your role is to assist customers with their orders, answer product questions, and help resolve any issues.

Guidelines:
- Always be professional and courteous
- Focus on e-commerce topics only
- Do not invent product information
- Ask for clarification when needed
- Use tools to retrieve order and product information when appropriate"""

    def _get_tools(self) -> list:
        """Get list of available tools for the agent"""
        return [
            get_order_status,
            cancel_order,
            lookup_product,
            check_stock,
        ]

    def update_session_state(self, key: str, value: Any) -> None:
        """
        Day 03: Store data in session state for multi-turn continuity.
        
        Args:
            key: State key (e.g., "customer_name", "last_order_id")
            value: Value to store
        """
        self.session_state[key] = value
        logger.info(f"Session state updated: {key} = {value}")

    def get_session_state(self, key: str, default: Any = None) -> Any:
        """
        Retrieve data from session state.
        
        Args:
            key: State key
            default: Default value if key not found
            
        Returns:
            The stored value or default
        """
        return self.session_state.get(key, default)

    def clear_session_state(self) -> None:
        """Clear all session state"""
        self.session_state.clear()
        logger.info("Session state cleared")

    def process_user_input(self, user_message: str) -> str:
        """
        Process user input and generate response.
        
        Args:
            user_message: The user's message
            
        Returns:
            The agent's response
        """
        logger.info(f"Processing user input: {user_message}")
        
        # Day 03: Extract and store customer name if provided
        if "my name is" in user_message.lower():
            parts = user_message.lower().split("my name is")
            if len(parts) > 1:
                name = parts[1].strip().replace(".", "").strip()
                self.update_session_state("customer_name", name)
        
        # Build the system prompt with session context
        system_prompt = self._build_system_prompt()
        
        # Day 07: Include routing hint for LiteLLM gateway
        routing_metadata = {"route_hint": self.route_hint}
        
        # For this implementation, we'll create a mock response
        # In production, this would call the LLM
        response = self._generate_response(user_message, system_prompt)
        
        return response

    def _build_system_prompt(self) -> str:
        """
        Build the system prompt with session context and instructions.
        
        Day 03: Include session state in the prompt for context awareness.
        """
        system_prompt = self.instruction
        
        # Add session context if available
        customer_name = self.get_session_state("customer_name")
        if customer_name:
            system_prompt += f"\n\nNote: The customer's name is {customer_name}. Use this to personalize your responses."
        
        last_order_id = self.get_session_state("last_order_id")
        if last_order_id:
            system_prompt += f"\n\nNote: The customer recently inquired about order {last_order_id}."
        
        return system_prompt

    def _generate_response(self, user_message: str, system_prompt: str) -> str:
        """
        Generate response (mock implementation for testing).
        
        In production, this would call the LLM via LiteLLM gateway.
        """
        # Mock responses for testing
        message_lower = user_message.lower()
        
        if "cancel" in message_lower and "ord-" in message_lower:
            order_id = self._extract_order_id(user_message)
            if not order_id:
                return "Please share a valid order ID in the format ORD-001 before I can process cancellation."

            pending = self.get_session_state("pending_cancellation")
            if pending == order_id and ("yes" in message_lower or "confirm" in message_lower):
                result = cancel_order.invoke({"order_id": order_id})
                self.update_session_state("pending_cancellation", None)
                if "error" in result:
                    return result["error"]
                return result["message"]

            self.update_session_state("pending_cancellation", order_id)
            return (
                f"I can cancel {order_id}, but this action is destructive. "
                f"Please reply with 'yes confirm {order_id}' to proceed."
            )

        if "order" in message_lower:
            # Extract order ID if present
            if "ord-" in message_lower:
                order_id = self._extract_order_id(user_message)
                
                if order_id:
                    result = get_order_status.invoke({"order_id": order_id})
                    self.update_session_state("last_order_id", order_id)
                    if "error" in result:
                        return result["error"]
                    return f"Order {order_id} status: {result['status']}, ETA: {result['eta']}, Carrier: {result['carrier']}"
            
            customer_name = self.get_session_state("customer_name", "")
            greeting = f"{customer_name.title()}, " if customer_name else ""
            return f"{greeting}I'd be happy to help you track your order. Could you please provide your order ID? It typically starts with 'ORD-'"
        
        elif "product" in message_lower or "price" in message_lower or "stock" in message_lower:
            return "I can help you find information about our products. What product are you interested in?"
        
        elif "hi" in message_lower or "hello" in message_lower or "greet" in message_lower:
            customer_name = self.get_session_state("customer_name", "")
            greeting = f"Hello {customer_name.title()}!" if customer_name else "Hello!"
            return f"{greeting} Welcome to our e-commerce support. How can I help you today?"
        
        else:
            customer_name = self.get_session_state("customer_name", "")
            name_part = f"{customer_name.title()}, " if customer_name else ""
            return f"{name_part}I'm here to help with orders, products, and general support. How can I assist you?"

    def _extract_order_id(self, text: str) -> Optional[str]:
        """Extract and normalize order ID from free text."""
        match = re.search(r"ORD-\d{3}", text.upper())
        if not match:
            return None
        return match.group(0)


def create_support_agent(
    instruction: Optional[str] = None,
    instruction_file: Optional[str] = None,
    use_tools: bool = True,
    route_hint: str = "fast-faq",
) -> SupportAgent:
    """
    Factory function to create a support agent with optional custom instruction.
    
    Args:
        instruction: Direct instruction string
        instruction_file: Path to instruction file
        use_tools: Enable tool calling
        route_hint: Routing hint for LiteLLM
        
    Returns:
        Configured SupportAgent instance
    """
    if instruction_file:
        with open(instruction_file, "r") as f:
            instruction = f.read()
    
    return SupportAgent(instruction=instruction, use_tools=use_tools, route_hint=route_hint)
