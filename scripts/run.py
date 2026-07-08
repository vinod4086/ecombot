"""Main runner script for eComBot"""
import logging
import argparse
from src.agents.support_agent import create_support_agent

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
            print(f"Agent: {response}\n")
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
        logger.info(f"Response: {response}\n")


def main():
    parser = argparse.ArgumentParser(description="eComBot Interactive Agent")
    parser.add_argument(
        "--mode",
        choices=["interactive", "batch"],
        default="interactive",
        help="Execution mode"
    )
    parser.add_argument(
        "--instruction-file",
        help="Path to instruction file"
    )
    parser.add_argument(
        "--queries",
        nargs="+",
        help="Queries for batch mode"
    )
    parser.add_argument(
        "--route-hint",
        choices=["fast-faq", "deep-support"],
        default="fast-faq",
        help="Routing hint for LLM gateway (Day 07)"
    )

    args = parser.parse_args()

    # Create agent
    agent = create_support_agent(
        instruction_file=args.instruction_file,
        route_hint=args.route_hint
    )

    if args.mode == "interactive":
        interactive_mode(agent)
    else:
        queries = args.queries or ["Hello", "Where is my order ORD-001?"]
        batch_mode(agent, queries)


if __name__ == "__main__":
    main()
