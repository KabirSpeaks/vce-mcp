from sentence_transformers import SentenceTransformer
import logging
import os

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        provider = os.getenv("EMBEDDING_PROVIDER", "local")
        self.provider = provider
        
        if provider == "local":
            logger.info(f"Loading local embedding model: {model_name}")
            self.model = SentenceTransformer(model_name)
        else:
            logger.warning(f"Unsupported provider {provider}, falling back to local {model_name}")
            self.model = SentenceTransformer(model_name)
            
    def generate_embedding(self, text: str) -> list[float]:
        try:
            return self.model.encode(text).tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return []
            
    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        try:
            return self.model.encode(texts).tolist()
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return [[] for _ in texts]
