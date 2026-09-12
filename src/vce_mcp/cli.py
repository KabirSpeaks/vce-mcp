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

def run_serve_http(host: str = None, port: int = None):
    import uvicorn
    import os
    
    final_host = host or os.environ.get("VCE_MCP_HOST", "0.0.0.0")
    
    if port is not None:
        final_port = port
    else:
        env_port = os.environ.get("PORT") or os.environ.get("VCE_MCP_PORT")
        final_port = int(env_port) if env_port else 8000
        
    logger.info(f"Starting Streamable HTTP server on {final_host}:{final_port}")
    uvicorn.run("vce_mcp.http_server:app", host=final_host, port=final_port)

def main():
    parser = argparse.ArgumentParser(description="VCE MCP CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    subparsers.add_parser("crawl", help="Crawl the VCE website")
    subparsers.add_parser("index", help="Index the crawled data into ChromaDB")
    subparsers.add_parser("setup", help="Crawl and index")
    subparsers.add_parser("refresh", help="Alias for setup")
    subparsers.add_parser("server", help="Run the local stdio MCP server")
    
    http_parser = subparsers.add_parser("serve-http", help="Run the remote Streamable HTTP server")
    http_parser.add_argument("--host", type=str, help="Host to bind to")
    http_parser.add_argument("--port", type=int, help="Port to bind to")
    
    args = parser.parse_args()
    
    if args.command == "crawl":
        run_crawler()
    elif args.command == "index":
        run_indexer()
    elif args.command in ("setup", "refresh"):
        setup_all()
    elif args.command == "server":
        run_server()
    elif args.command == "serve-http":
        run_serve_http(args.host, args.port)

if __name__ == "__main__":
    main()
