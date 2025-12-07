import chromadb
from typing import List, Dict, Any

class Memory:
    def __init__(self, persist_directory: str = "data/memory"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection("user_facts")

    def add(self, text: str, metadata: Dict[str, Any] = None):
        """
        Adds a single text memory to the backend.
        
        Args:
            text: The text content to memorize.
            metadata: Optional dictionary of metadata.
        """
        import uuid
        self.collection.add(
            documents=[text],
            metadatas=[metadata or {}],
            ids=[str(uuid.uuid4())]
        )

    def search(self, query: str, n_results: int = 3) -> List[str]:
        """
        Semantic search for memories relevant to the query.
        
        Args:
            query: The search query.
            n_results: Number of top results to return.
            
        Returns:
            List of document strings.
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        # Chroma returns list of lists (one per query). We only have 1 query.
        return results["documents"][0] if results["documents"] else []

