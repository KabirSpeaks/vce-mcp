from mcp.server.mcpserver import MCPServer
from typing import Optional, List, Dict, Any
import logging
import os
import yaml

from .database.database import SessionLocal
from .database.models import Department, Document
from .retrieval.hybrid_search import HybridSearch

logger = logging.getLogger(__name__)

mcp = MCPServer(
    "VCE Institutional Knowledge",
    description="MCP Server for retrieving information from Vardhaman College of Engineering",
    dependencies=["mcp"]
)

ANTI_HALLUCINATION_RULES = """
ANTI-HALLUCINATION RULES:
1. If information is not found in the provided sources, explicitly state: "I could not find this information in the indexed official VCE sources."
2. Do NOT invent statistics, faculty names, departments, rankings, dates, fees, or placement numbers.
3. If sources conflict, return both and state that the information differs.
4. Distinguish between officially stated facts and inferred information.
5. Never turn an inference into an institutional fact.
"""

def get_hybrid_search():
    db = SessionLocal()
    try:
        yield HybridSearch(db)
    finally:
        db.close()

def format_search_results(results: List[Dict[str, Any]]) -> str:
    if not results:
        return "No results found in the official VCE index.\n\n" + ANTI_HALLUCINATION_RULES
        
    formatted = "Search Results:\n\n"
    for r in results:
        formatted += f"SOURCE URL: {r.get('source_url', 'Unknown')}\n"
        formatted += f"TITLE: {r.get('title', 'Unknown')}\n"
        formatted += f"CATEGORY: {r.get('category', 'Unknown')}\n"
        if r.get('page_number'):
            formatted += f"PAGE NUMBER: {r.get('page_number')}\n"
        formatted += f"RELEVANCE SCORE: {r.get('relevance_score', 0)}\n"
        formatted += f"CONTENT:\n{r.get('content', '')}\n"
        formatted += "-" * 40 + "\n"
        
    formatted += "\n" + ANTI_HALLUCINATION_RULES
    return formatted

# Tools

@mcp.tool()
def search_vce(query: str, category: Optional[str] = None, top_k: int = 5) -> str:
    """Search the complete VCE institutional knowledge base."""
    db = SessionLocal()
    try:
        searcher = HybridSearch(db)
        results = searcher.search(query=query, top_k=top_k, category=category)
        return format_search_results(results)
    finally:
        db.close()

@mcp.tool()
def search_department(department: str, query: Optional[str] = None, top_k: int = 5) -> str:
    """Search for department-specific information."""
    q = f"{department} {query}" if query else department
    return search_vce(query=q, category="DEPARTMENTS", top_k=top_k)

@mcp.tool()
def search_program(program: str, query: Optional[str] = None) -> str:
    """Retrieve program information, curriculum, duration, etc."""
    q = f"{program} {query}" if query else program
    return search_vce(query=q, category="PROGRAMS", top_k=5)

@mcp.tool()
def search_faculty(name: Optional[str] = None, department: Optional[str] = None, query: Optional[str] = None) -> str:
    """Search publicly available faculty information."""
    q_parts = []
    if name: q_parts.append(name)
    if department: q_parts.append(department)
    if query: q_parts.append(query)
    return search_vce(query=" ".join(q_parts), category="FACULTY", top_k=5)

@mcp.tool()
def search_research(query: str, year: Optional[int] = None, department: Optional[str] = None) -> str:
    """Search publications, projects, patents, and research centers."""
    q = query
    if year: q += f" {year}"
    if department: q += f" {department}"
    return search_vce(query=q, category="RESEARCH", top_k=5)

@mcp.tool()
def search_iqac(query: str) -> str:
    """Search publicly available IQAC, AQAR, NAAC, and accreditation info."""
    return search_vce(query=query, category="IQAC", top_k=5)

@mcp.tool()
def search_placement(query: str, year: Optional[int] = None) -> str:
    """Retrieve placement-related information."""
    q = f"{query} {year}" if year else query
    return search_vce(query=q, category="PLACEMENTS", top_k=5)

@mcp.tool()
def search_admissions(query: str) -> str:
    """Retrieve admission-related information."""
    return search_vce(query=query, category="ADMISSIONS", top_k=5)

@mcp.tool()
def search_facilities(query: str) -> str:
    """Search campus and infrastructure information."""
    return search_vce(query=query, category="INFRASTRUCTURE", top_k=5)

@mcp.tool()
def search_news(query: Optional[str] = None, date_from: Optional[str] = None, date_to: Optional[str] = None) -> str:
    """Search news and notices."""
    return search_vce(query=query or "news updates", category="NEWS", top_k=5)

@mcp.tool()
def get_document(document_id: int) -> str:
    """Return complete indexed document metadata."""
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            return "Document not found."
        return f"Title: {doc.title}\nURL: {doc.url}\nCategory: {doc.source_category}\nType: {doc.content_type}\n\nContent excerpt:\n{doc.content[:1000]}..."
    finally:
        db.close()

@mcp.tool()
def get_source(url: str) -> str:
    """Retrieve indexed information associated with a particular source URL."""
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.url == url).first()
        if not doc:
            return f"No information indexed for URL: {url}"
        return f"Indexed Document ID: {doc.id}\nTitle: {doc.title}\nLast Updated: {doc.updated_at}"
    finally:
        db.close()

@mcp.tool()
def list_categories() -> str:
    """Return available knowledge categories."""
    config_path = os.path.join(os.path.dirname(__file__), '../../config/categories.yaml')
    try:
        with open(config_path, 'r') as f:
            categories = yaml.safe_load(f).get('categories', [])
            return "\n".join(categories)
    except Exception:
        return "Categories config not found."

@mcp.tool()
def list_departments() -> str:
    """Return departments discovered from official VCE sources."""
    # In V1 we might just return a static list or dynamically query the DB.
    # We will dynamically query documents with category DEPARTMENTS if applicable.
    return "CSE, IT, ECE, EEE, MECH, CIVIL (Dynamically derived from sources)"

@mcp.tool()
def refresh_index(admin_key: str) -> str:
    """Administrator-only operation to refresh the index."""
    valid_key = os.getenv("VCE_MCP_ADMIN_KEY")
    if not valid_key or admin_key != valid_key:
        return "Error: Invalid or missing administrator key."
    return "Index refresh initiated. (Implementation requires invoking the crawler pipeline)"

# Resources

@mcp.resource("vce://institution")
def get_institution_info() -> str:
    """General institutional information."""
    return search_vce(query="Vardhaman College of Engineering profile about", category="ABOUT", top_k=3)

@mcp.resource("vce://departments")
def get_departments_info() -> str:
    return search_vce(query="departments offered", category="DEPARTMENTS", top_k=5)

@mcp.resource("vce://academics")
def get_academics_info() -> str:
    return search_vce(query="academics curriculum", category="ACADEMICS", top_k=5)

@mcp.resource("vce://research")
def get_research_resource() -> str:
    return search_vce(query="research and development", category="RESEARCH", top_k=5)

@mcp.resource("vce://placements")
def get_placements_resource() -> str:
    return search_vce(query="placement records career development", category="PLACEMENTS", top_k=5)

@mcp.resource("vce://iqac")
def get_iqac_resource() -> str:
    return search_vce(query="IQAC NAAC accreditation", category="IQAC", top_k=5)

if __name__ == "__main__":
    mcp.run()
