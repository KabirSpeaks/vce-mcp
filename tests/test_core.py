import pytest
from bs4 import BeautifulSoup
from vce_mcp.crawler.parser import parse_html
from vce_mcp.crawler.robots import RobotsChecker
from vce_mcp.database.database import Base, engine, SessionLocal
from vce_mcp.database.repository import VCERepository
from vce_mcp.retrieval.embeddings import EmbeddingService
from vce_mcp.retrieval.vector_store import VectorStore
import os

@pytest.fixture(scope="session")
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_html_parser():
    html = """
    <html>
        <head><title>Test VCE Page</title></head>
        <body>
            <h1>Main Heading</h1>
            <p>This is paragraph 1.</p>
            <h2>Sub Heading</h2>
            <p>This is paragraph 2.</p>
            <nav><a href="/link1">Link 1</a></nav>
        </body>
    </html>
    """
    title, text, links, chunks = parse_html(html, "https://vardhaman.org/test")
    
    assert title == "Test VCE Page"
    assert len(chunks) == 2
    assert chunks[0]['section'] == "Main Heading"
    assert chunks[0]['content'] == "This is paragraph 1."
    assert chunks[1]['section'] == "Sub Heading"
    assert chunks[1]['content'] == "This is paragraph 2."

def test_robots_checker():
    # Mocking robots checker is better, but we can just test initialization
    checker = RobotsChecker()
    assert checker.user_agent == "VCEMCPBot/1.0"

def test_repository(setup_db):
    db = SessionLocal()
    repo = VCERepository(db)
    
    doc = repo.create_or_update_document(
        url="https://vardhaman.org/test",
        title="Test",
        content="Testing",
        content_type="html",
        source_domain="vardhaman.org",
        content_hash="hash123",
        category="ABOUT"
    )
    
    assert doc.id is not None
    assert doc.url == "https://vardhaman.org/test"
    db.close()

def test_vector_store():
    # Test with an in-memory or temp directory
    store = VectorStore(persist_directory="data/test_vector")
    assert store.collection_name == "vce_chunks"
    # Basic cleanup
    if os.path.exists("data/test_vector"):
        import shutil
        shutil.rmtree("data/test_vector")
