import os
import uuid
import chromadb
from typing import List, Dict, Any
from ..core.logging import logger

class MemoryManager:
    """
    Manages persistent memory using ChromaDB.
    Memories are vectorized using Chroma's default sentence-transformers model.
    """
    def __init__(self, db_path: str = "chroma_db"):
        self.db_path = db_path
        os.makedirs(self.db_path, exist_ok=True)
        
        # Initialize persistent client
        self.client = chromadb.PersistentClient(path=self.db_path)
        
        # Get or create collections for different memory types
        self.long_term = self.client.get_or_create_collection(name="long_term_memory")
        self.project_context = self.client.get_or_create_collection(name="project_memory")
        
        logger.info(f"Memory System initialized at {self.db_path}")

    def save_memory(self, text: str, importance: int = 5, tags: List[str] = None):
        """Saves a conversational memory to the long-term DB."""
        if not text.strip():
            return
            
        mem_id = f"mem_{uuid.uuid4().hex[:12]}"
        metadata = {"importance": importance}
        if tags:
            metadata["tags"] = ",".join(tags)
            
        try:
            self.long_term.add(
                documents=[text],
                metadatas=[metadata],
                ids=[mem_id]
            )
            logger.debug(f"Saved memory {mem_id}")
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")

    def recall_memories(self, query: str, n_results: int = 3, threshold: float = 1.5) -> List[str]:
        """
        Retrieves the most semantically relevant memories to the given query.
        Returns a list of text strings.
        """
        try:
            results = self.long_term.query(
                query_texts=[query],
                n_results=n_results
            )
            
            memories = []
            if results and results.get("documents"):
                docs = results["documents"][0]
                distances = results["distances"][0] if "distances" in results else []
                
                for i, doc in enumerate(docs):
                    # Lower distance = closer match. Only include if it's somewhat relevant.
                    if i < len(distances) and distances[i] > threshold:
                        continue
                    memories.append(doc)
                    
            return memories
        except Exception as e:
            logger.error(f"Failed to recall memories: {e}")
            return []

    def clean_unimportant_memories(self, importance_threshold: int = 3):
        """Deletes memories that have a low importance score to keep DB fast."""
        try:
            # ChromaDB supports where filtering on metadata
            self.long_term.delete(where={"importance": {"$lt": importance_threshold}})
            logger.info("Cleaned unimportant memories.")
        except Exception as e:
            logger.error(f"Failed to clean memories: {e}")

    def get_stats(self) -> Dict[str, int]:
        """Returns the number of documents in each collection."""
        try:
            return {
                "long_term": self.long_term.count(),
                "project": self.project_context.count()
            }
        except Exception:
            return {"long_term": 0, "project": 0}

# Singleton instance
memory_manager = MemoryManager()
