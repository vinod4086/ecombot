"""Main runner script for eComBot"""
import logging
import argparse
import os
import sys

# Allow running as `python scripts/run.py` by adding repo root to sys.path.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.agents.orchestrator import create_orchestrator_agent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def interactive_mode(agent):
    """Interactive conversation mode"""
    logger.info("Entering interactive mode. Type 'exit' to quit.\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ["exit", "quit"]:
                logger.info("Exiting...")
                break
            
            if not user_input:
                continue
            
            response = agent.process_user_input(user_input)
            print(f"Agent ({response.get('agent', 'orchestrator')}): {response.get('text', '')}\n")
        except KeyboardInterrupt:
            logger.info("\nExiting...")
            break
        except Exception as e:
            logger.error(f"Error: {e}")


def batch_mode(agent, queries):
    """Process a batch of queries"""
    for query in queries:
        logger.info(f"Query: {query}")
        response = agent.process_user_input(query)
        logger.info(
            "Response: route=%s agent=%s text=%s\n",
            response.get("route"),
            response.get("agent"),
            response.get("text"),
        )


def main():
    parser = argparse.ArgumentParser(description="eComBot Interactive Agent")
    parser.add_argument(
        "--mode",
        choices=["interactive", "batch"],
        default="interactive",
        help="Execution mode"
    )
    parser.add_argument(
        "--queries",
        nargs="+",
        help="Queries for batch mode"
    )
    args = parser.parse_args()

    # Create orchestrator agent as primary entrypoint (Day 09+)
    agent = create_orchestrator_agent()

    if args.mode == "interactive":
        interactive_mode(agent)
    else:
        queries = args.queries or ["Hello", "Where is my order ORD-001?"]
        batch_mode(agent, queries)


if __name__ == "__main__":
    main()
