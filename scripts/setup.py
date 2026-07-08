"""Setup and initialization script for eComBot"""
import os
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_environment():
    """Setup environment and configuration"""
    logger.info("Setting up eComBot environment...")

    # Check for .env file
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            logger.info("Creating .env from .env.example")
            with open(".env.example", "r") as f_in:
                with open(".env", "w") as f_out:
                    f_out.write(f_in.read())
        else:
            logger.warning(".env.example not found")

    logger.info("Environment setup complete")


def setup_database():
    """Initialize database"""
    logger.info("Setting up database...")
    logger.info("Run: docker-compose up -d postgres")
    logger.info("Database will be automatically initialized from scripts/init_db.sql")


def setup_redis():
    """Initialize Redis"""
    logger.info("Setting up Redis...")
    logger.info("Run: docker-compose up -d redis")
    logger.info("Redis will start with password protection")


def setup_rag():
    """Initialize RAG components"""
    logger.info("Setting up RAG...")
    logger.info("Run: python -m src.rag.embed_catalog")
    logger.info("This will index products and FAQs into ChromaDB")


def main():
    """Run setup"""
    logger.info("=" * 60)
    logger.info("eComBot Setup Script")
    logger.info("=" * 60)

    try:
        setup_environment()
        
        logger.info("\nTo complete setup, run:")
        logger.info("1. docker-compose up -d  (start all services)")
        logger.info("2. python -m src.rag.embed_catalog  (setup RAG)")
        logger.info("3. python scripts/test_agent.py  (run tests)")
        logger.info("4. python scripts/run.py  (interactive mode)")

        logger.info("\nFor MCP server, run:")
        logger.info("python -m src.services.mcp_server")

        logger.info("\n" + "=" * 60)
        logger.info("Setup complete!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Setup failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
