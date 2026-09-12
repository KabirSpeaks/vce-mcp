# VCE Institutional Knowledge MCP Server

This is an independent/open-source Model Context Protocol (MCP) implementation designed to retrieve publicly available information from the Vardhaman College of Engineering (VCE) website (https://vardhaman.org/).

**Disclaimer:** This project is not officially endorsed by Vardhaman College of Engineering. It serves as a read-only AI knowledge layer based on publicly accessible data.

## Features

- **Web Crawler:** Configurable crawler to index VCE's official website and subdomains, respecting `robots.txt`.
- **Intelligent Chunking:** Extracts text from HTML and PDFs, splitting them logically for search.
- **Hybrid Retrieval:** Local semantic search via ChromaDB and Sentence-Transformers.
- **Source Attribution:** Every retrieved fact contains metadata (Source URL, page number, date).
- **Read-Only:** Strictly designed to read public data. No database writes or unsafe code execution exposed to the AI.
- **15+ MCP Tools:** Tools for searching departments, admissions, placements, faculty, IQAC info, and more.

## Architecture

```mermaid
flowchart TD
    A[MCP Client] --> B[VCE MCP Server]
    B --> C[Retrieval Engine]
    C --> D[Local Index (SQLite + ChromaDB)]
    D --> E[VCE Official Website]
```

## Installation

You need Python 3.12+ installed.

1. **Clone the repo**
```bash
git clone https://github.com/KabirSpeaks/vce-mcp.git
cd vce-mcp
uv pip install -e .
```

## Remote MCP Deployment (Cloud)

The server supports remote deployment via the official MCP Streamable HTTP transport, which can be connected to ChatGPT and other clients.

### Docker
```bash
docker build -t vce-mcp .
docker run -p 8000:8000 -e PORT=8000 vce-mcp
```

### Endpoints
- **MCP Endpoint**: `https://YOUR-DOMAIN/mcp`
- **Health Endpoint**: `https://YOUR-DOMAIN/health`

### Architecture
```text
AI Client (ChatGPT)
   |
   | MCP Streamable HTTP
   v
https://DOMAIN/mcp
   |
   v
VCE MCP Server
   |
   +---- SQLite & ChromaDB
```

> **Important**: ChatGPT connects to the remotely deployed MCP endpoint (e.g., `https://YOUR-DOMAIN/mcp`). The GitHub repository itself is the source code and cannot be directly linked to ChatGPT.

Please refer to:
- [Remote Deployment Guide](docs/REMOTE_DEPLOYMENT.md)
- [ChatGPT Connection Guide](docs/CHATGPT_CONNECTION.md)
- [Marketplace Deployment Guide](docs/MARKETPLACE_DEPLOYMENT.md)

## Usage (Local Stdio)

Run the local stdio MCP server:
```bash
vce-mcp server
```
Edit `.env` if necessary (e.g., to change crawl depth).

## Initial Setup (Indexing)

This repository does not contain pre-crawled institutional data. You must generate your own local index:

```bash
# Crawl the website and index documents
vce-mcp setup
```
*(Alternatively, you can run `vce-mcp crawl` followed by `vce-mcp index`)*

## Running the Server

To start the MCP server using standard input/output (for Claude Desktop or Antigravity):

```bash
vce-mcp server
```

## MCP Client Configuration

### Claude Desktop
Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "vce-mcp": {
      "command": "path/to/vce-mcp/.venv/bin/vce-mcp",
      "args": ["server"]
    }
  }
}
```

### Antigravity
You can load this server in Antigravity by pointing to the executable in the virtual environment.

## Updating

To refresh the index and pull new/changed pages:
```bash
vce-mcp refresh
```

## Limitations

- Information strictly depends on the official VCE website.
- The local index may become outdated if not refreshed.
- Private institutional data (ERP, student portals) is explicitly excluded.
- Always verify important institutional claims against the official source URL provided by the AI.
