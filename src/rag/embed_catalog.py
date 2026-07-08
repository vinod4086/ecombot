"""Embedding script for ChromaDB knowledge base - Day 05-06 implementation"""
import json
import logging
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings as ChromaSettings

logger = logging.getLogger(__name__)


class KnowledgeBaseEmbedder:
    """Embeds product and FAQ data into ChromaDB"""

    def __init__(self):
        """Initialize ChromaDB client"""
        self.client = None
        self.collection = None
        self.initialize()

    def initialize(self) -> None:
        """Initialize ChromaDB client and collection"""
        try:
            # Use the modern persistent client API.
            self.client = chromadb.PersistentClient(
                path="./chroma_data",
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            
            # Create or get collection
            self.collection = self.client.get_or_create_collection(
                name="ecombot_kb",
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("ChromaDB collection initialized")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise

    def load_knowledge_base(self) -> List[Dict[str, Any]]:
        """Load product and FAQ data"""
        documents = []
        
        # Load products
        try:
            with open("data/products.json", "r") as f:
                products = json.load(f)
                for product in products:
                    doc = {
                        "id": f"product_{product['id']}",
                        "content": self._format_product(product),
                        "metadata": {
                            "type": "product",
                            "product_id": product["id"],
                            "category": product.get("category", ""),
                        }
                    }
                    documents.append(doc)
            logger.info(f"Loaded {len(products)} products")
        except FileNotFoundError:
            logger.warning("products.json not found")
        
        # Load FAQs
        try:
            with open("data/faq.json", "r") as f:
                faqs = json.load(f)
                for idx, faq in enumerate(faqs):
                    doc = {
                        "id": f"faq_{idx}",
                        "content": f"Q: {faq['question']}\nA: {faq['answer']}",
                        "metadata": {
                            "type": "faq",
                            "category": faq.get("category", ""),
                        }
                    }
                    documents.append(doc)
            logger.info(f"Loaded {len(faqs)} FAQs")
        except FileNotFoundError:
            logger.warning("faq.json not found")
        
        return documents

    def _format_product(self, product: Dict[str, Any]) -> str:
        """Format product data as text for embedding"""
        return f"""
Product: {product['name']}
Category: {product.get('category', 'N/A')}
Price: {product.get('price', 'N/A')}
Description: {product.get('description', '')}
Features: {', '.join(product.get('features', []))}
Warranty: {product.get('warranty', 'N/A')}
Shipping: {product.get('shipping', 'N/A')}
"""

    def embed_and_store(self) -> None:
        """Embed and store documents in ChromaDB"""
        documents = self.load_knowledge_base()
        
        if not documents:
            logger.warning("No documents to embed")
            return
        
        # Prepare data for ChromaDB
        ids = []
        contents = []
        metadatas = []
        
        for doc in documents:
            ids.append(doc["id"])
            contents.append(doc["content"])
            metadatas.append(doc["metadata"])
        
        try:
            self.collection.add(
                ids=ids,
                documents=contents,
                metadatas=metadatas,
            )
            logger.info(f"Embedded {len(documents)} documents in ChromaDB")
        except Exception as e:
            logger.error(f"Failed to embed documents: {e}")
            raise

    def clear_collection(self) -> None:
        """Clear the collection"""
        try:
            # Delete and recreate collection
            self.client.delete_collection(name="ecombot_kb")
            self.collection = self.client.get_or_create_collection(
                name="ecombot_kb",
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("Collection cleared")
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")


def main():
    """Main function to run embedding"""
    embedder = KnowledgeBaseEmbedder()
    embedder.clear_collection()
    embedder.embed_and_store()
    print("Knowledge base embedded successfully!")


if __name__ == "__main__":
    main()
