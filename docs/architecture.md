# Architecture

The VCE MCP Server is built to index public information from Vardhaman College of Engineering and expose it securely to an AI assistant via the Model Context Protocol (MCP).

## Components

1. **Crawler (`vce_mcp/crawler`)**
   - Respects `robots.txt`
   - Downloads HTML and PDFs
   - Cleans HTML and chunks by headings
   - Extracts page-level PDF text

2. **Database (`vce_mcp/database`)**
   - SQLite for persistence of URLs, document metadata, and text chunks.
   - Preserves source attribution and timestamps.

3. **Retrieval Engine (`vce_mcp/retrieval`)**
   - ChromaDB local vector store.
   - Generates embeddings using `sentence-transformers/all-MiniLM-L6-v2`.
   - Hybrid search combines exact metadata filtering with semantic similarity.

4. **MCP Server (`vce_mcp/server.py`)**
   - Uses `mcp.server.mcpserver` SDK (v2).
   - Read-only tools exposing categories like Admissions, Placements, Faculty.
