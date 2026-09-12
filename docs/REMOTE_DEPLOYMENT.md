# Remote Deployment (Cloud Run, Render, etc.)

The VCE MCP server can be deployed as a standard HTTP application serving MCP over Streamable HTTP. It exposes a `/mcp` endpoint and a `/health` endpoint.

## Architecture

```
AI Client (ChatGPT, etc.)
   |
   | MCP Streamable HTTP
   v
https://YOUR-DOMAIN/mcp
   |
   v
VCE MCP Server
   |
   +---- SQLite
   +---- ChromaDB
   +---- VCE indexed content
```

## Docker Deployment

Build the container:
```bash
docker build -t vce-mcp .
```

Run it locally to test:
```bash
docker run -p 8000:8000 -e PORT=8000 vce-mcp
```

## Initial Setup (Populating the Index)

The Docker image contains the code, but intentionally DOES NOT include the crawled `.db` and `vector` data. To initialize the institutional knowledge base in your cloud environment, you must run the setup command once. 

If your deployment environment supports executing commands (e.g., Cloud Run Jobs or Render Shell):
```bash
vce-mcp setup
```

*Note*: Ensure that your cloud environment has a persistent volume mounted to the `data/` directory. Otherwise, the indexed database will be lost when the container is recreated.

## Environment Variables

*   `PORT`: Controls which port the HTTP server binds to (default: `8000`).
*   `VCE_MCP_ALLOWED_HOSTS`: Comma-separated list of allowed hostnames (e.g., `vce-mcp.example.com`). Required for DNS rebinding protection in production!
*   `MAX_CRAWL_DEPTH` / `MAX_CRAWL_PAGES`: Configures the crawler limits.
