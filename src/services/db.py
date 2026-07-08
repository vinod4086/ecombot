"""Database service for PostgreSQL integration - Day 04 implementation"""
import logging
from typing import Optional, List, Dict, Any
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from src.config.settings import settings

logger = logging.getLogger(__name__)


class Database:
    """PostgreSQL database service for eComBot"""

    def __init__(self):
        """Initialize database connection pool"""
        self.pool: Optional[SimpleConnectionPool] = None
        self.initialize()

    def initialize(self) -> None:
        """Initialize connection pool"""
        try:
            self.pool = SimpleConnectionPool(
                1,
                20,
                database=settings.postgres_db,
                user=settings.postgres_user,
                password=settings.postgres_password,
                host=settings.postgres_host,
                port=settings.postgres_port,
            )
            logger.info("Database connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def get_connection(self):
        """Get a connection from the pool"""
        if self.pool is None:
            self.initialize()
        return self.pool.getconn()

    def return_connection(self, conn):
        """Return a connection to the pool"""
        if self.pool:
            self.pool.putconn(conn)

    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results.
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            List of result rows as dictionaries
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            # Get column names
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            
            # Fetch results
            results = cursor.fetchall()
            cursor.close()
            
            # Convert to list of dictionaries
            return [dict(zip(columns, row)) for row in results]
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            raise
        finally:
            if conn:
                self.return_connection(conn)

    def execute_update(self, query: str, params: tuple = None) -> int:
        """
        Execute an INSERT, UPDATE, or DELETE query.
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            Number of affected rows
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            affected_rows = cursor.rowcount
            conn.commit()
            cursor.close()
            return affected_rows
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Update execution error: {e}")
            raise
        finally:
            if conn:
                self.return_connection(conn)

    def close(self) -> None:
        """Close all connections in the pool"""
        if self.pool:
            self.pool.closeall()
            logger.info("Database connection pool closed")


# Global database instance
db_instance: Optional[Database] = None


def get_database() -> Database:
    """Get or create the global database instance"""
    global db_instance
    if db_instance is None:
        db_instance = Database()
    return db_instance
