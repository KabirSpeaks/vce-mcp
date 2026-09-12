from typing import List, Dict, Any
from .embeddings import EmbeddingService
from .vector_store import VectorStore
from ..database.repository import VCERepository
from ..database.models import Document, Chunk
import logging
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class HybridSearch:
    def __init__(self, db: Session):
        self.db = db
        self.repo = VCERepository(db)
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()
        
    def search(self, query: str, top_k: int = 5, category: str = None) -> List[Dict[str, Any]]:
        logger.info(f"Performing search for: '{query}'")
        
        # 1. Generate Query Embedding
        query_embedding = self.embedding_service.generate_embedding(query)
        if not query_embedding:
            return []
            
        # 2. Setup filters
        filters = {}
        if category:
            filters['category'] = category
            
        # 3. Vector Search
        vector_results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            filters=filters
        )
        
        # 4. Format Results
        results = []
        for res in vector_results:
            meta = res['metadata']
            
            results.append({
                'source_url': meta.get('url', ''),
                'title': meta.get('title', ''),
                'section': meta.get('section', ''),
                'content': res['content'],
                'category': meta.get('category', ''),
                'relevance_score': round(1.0 - res.get('score', 0.0), 4), # Convert distance to rough similarity
                'page_number': meta.get('page_number') if meta.get('page_number') != -1 else None
            })
            
        return results
