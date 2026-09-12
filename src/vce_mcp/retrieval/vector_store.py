import os
import os
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, persist_directory: str = None):
        if persist_directory is None:
            persist_directory = os.getenv("VECTOR_STORE_PATH", "data/vector")
        
        # Ensure path exists
        os.makedirs(persist_directory, exist_ok=True)
        
        import chromadb
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection_name = "vce_chunks"
        
        # We don't rely on chromadb's default embedding function to keep explicit control
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, chunks_data: List[Dict[str, Any]], embeddings: List[List[float]]):
        if not chunks_data:
            return
            
        ids = [str(chunk['id']) for chunk in chunks_data]
        documents = [chunk['content'] for chunk in chunks_data]
        
        metadatas = []
        for chunk in chunks_data:
            meta = {
                'document_id': chunk['document_id'],
                'url': chunk['url'],
                'title': chunk.get('title', ''),
                'section': chunk.get('section', ''),
                'category': chunk.get('category', ''),
                'page_number': chunk.get('page_number') or -1
            }
            metadatas.append(meta)
            
        try:
            self.collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
        except Exception as e:
            logger.error(f"Error adding chunks to ChromaDB: {e}")

    def search(self, query_embedding: List[float], top_k: int = 5, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        try:
            where_clause = None
            if filters:
                # Basic exact match filtering for chromadb
                where_clause = {k: v for k, v in filters.items() if v is not None}
                if not where_clause:
                    where_clause = None
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_clause
            )
            
            formatted_results = []
            if results and results['ids'] and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    formatted_results.append({
                        'id': results['ids'][0][i],
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'score': results['distances'][0][i] if 'distances' in results and results['distances'] else 0.0
                    })
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching ChromaDB: {e}")
            return []
