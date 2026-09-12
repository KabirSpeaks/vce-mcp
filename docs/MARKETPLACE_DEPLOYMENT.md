# Marketplace Deployment Contract

To deploy this MCP server via an MCP Marketplace or automated deployment pipeline, ensure your system respects the following contract:

1. **Build Environment**: Docker compatible.
2. **Build Command**: `docker build -t vce-mcp .`
3. **Startup Command**: `vce-mcp serve-http --host 0.0.0.0` (or allow the Docker `CMD` to execute natively).
4. **Port Binding**: The application listens on the port specified by the `PORT` environment variable. Ensure this is injected.
5. **Endpoints**:
    - **Health Check**: `GET /health` (Returns HTTP 200 JSON on success).
    - **MCP Endpoint**: `POST /mcp` and `GET /mcp` (Streamable HTTP).
6. **Required Environment Variables**:
    - `PORT`: (e.g., 8000)
    - `VCE_MCP_ALLOWED_HOSTS`: The public domain where the service is hosted (e.g., `mcp.example.com`). This is required for security (DNS rebinding protection).
7. **Persistent Storage**:
    - The server requires persistent storage at `/app/data/` for `vce.db` and `/app/data/vector/`. Without persistent storage, the index must be rebuilt (`vce-mcp setup`) every time the container restarts.
