import argparse
import asyncio
import sys
import logging
from .database.database import init_db, SessionLocal
from .crawler.crawler import VCECrawler
from .database.models import Chunk
from .retrieval.embeddings import EmbeddingService
from .retrieval.vector_store import VectorStore
from .server import mcp

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_crawler():
    logger.info("Initializing Database...")
    init_db()
    
    db = SessionLocal()
    try:
        crawler = VCECrawler(db)
        logger.info("Starting Crawl...")
        asyncio.run(crawler.run())
        logger.info("Crawl completed.")
    finally:
        db.close()

def run_indexer():
    logger.info("Starting Vector Indexing...")
    db = SessionLocal()
    try:
        # Get all chunks
        chunks = db.query(Chunk).all()
        logger.info(f"Found {len(chunks)} chunks to index.")
        
        if not chunks:
            logger.info("No chunks to index.")
            return

        embedding_service = EmbeddingService()
        vector_store = VectorStore()
        
        # Format chunks for vector store
        chunks_data = []
        texts_to_embed = []
        for c in chunks:
            chunks_data.append({
                'id': str(c.id),
                'document_id': c.document_id,
                'url': c.document.url,
                'title': c.title or c.document.title,
                'section': c.section,
                'category': c.document.source_category,
                'page_number': c.page_number,
                'content': c.content
            })
            texts_to_embed.append(c.content)
            
        logger.info("Generating embeddings...")
        embeddings = embedding_service.generate_embeddings(texts_to_embed)
        
        logger.info("Storing in ChromaDB...")
        vector_store.add_chunks(chunks_data, embeddings)
        logger.info("Indexing completed successfully.")
        
    finally:
        db.close()

def setup_all():
    run_crawler()
    run_indexer()

def run_server():
    mcp.run()

def main():
    parser = argparse.ArgumentParser(description="VCE MCP CLI")
    parser.add_argument("command", choices=["crawl", "index", "setup", "refresh", "server"])
    
    args = parser.parse_args()
    
    if args.command == "crawl":
        run_crawler()
    elif args.command == "index":
        run_indexer()
    elif args.command == "setup" or args.command == "refresh":
        setup_all()
    elif args.command == "server":
        run_server()

if __name__ == "__main__":
    main()
