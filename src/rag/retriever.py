"""Retriever for RAG-based answers - Day 05-06 implementation"""
import logging
from typing import List, Dict, Any, Tuple
import chromadb
from chromadb.config import Settings as ChromaSettings

logger = logging.getLogger(__name__)


class RAGRetriever:
    """Retrieves relevant context from ChromaDB knowledge base"""

    def __init__(self):
        """Initialize ChromaDB client and collection"""
        self.client = None
        self.collection = None
        self.initialize()

    def initialize(self) -> None:
        """Initialize ChromaDB client and collection"""
        try:
            self.client = chromadb.PersistentClient(
                path="./chroma_data",
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            
            self.collection = self.client.get_or_create_collection(
                name="ecombot_kb",
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("RAG retriever initialized")
        except Exception as e:
            logger.error(f"Failed to initialize retriever: {e}")
            raise

    def retrieve(self, query: str, n_results: int = 3) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Retrieve relevant chunks for a query.
        
        Args:
            query: User query
            n_results: Number of results to return
            
        Returns:
            Tuple of (documents, metadata)
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
            )
            
            if not results["documents"] or not results["documents"][0]:
                logger.warning(f"No results found for query: {query}")
                return [], []
            
            documents = results["documents"][0]
            metadatas = results["metadatas"][0]
            
            logger.info(f"Retrieved {len(documents)} documents for query: {query}")
            return documents, metadatas
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            return [], []

    def retrieve_with_scores(
        self, query: str, n_results: int = 3
    ) -> List[Tuple[str, Dict[str, Any], float]]:
        """
        Retrieve relevant chunks with similarity scores.
        
        Args:
            query: User query
            n_results: Number of results to return
            
        Returns:
            List of (document, metadata, score) tuples
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["documents", "metadatas", "distances"],
            )
            
            if not results["documents"] or not results["documents"][0]:
                return []
            
            # Convert distances to similarity scores (1 - distance for cosine)
            scored_results = []
            for doc, metadata, distance in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            ):
                score = 1 - distance  # Convert distance to similarity
                scored_results.append((doc, metadata, score))
            
            return scored_results
        except Exception as e:
            logger.error(f"Retrieval with scores failed: {e}")
            return []

    def is_strong_match(self, score: float, threshold: float = 0.5) -> bool:
        """Check if a score is above the match threshold"""
        return score >= threshold


# Global retriever instance
retriever_instance: RAGRetriever = None


def get_retriever() -> RAGRetriever:
    """Get or create the retriever instance"""
    global retriever_instance
    if retriever_instance is None:
        retriever_instance = RAGRetriever()
    return retriever_instance
