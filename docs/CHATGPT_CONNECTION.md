# ChatGPT Connection Guide

ChatGPT Desktop app supports connecting to remote MCP servers. 

> **Important**: This requires a ChatGPT plan or workspace configuration that explicitly allows custom MCP integrations (developer mode). It does not automatically work for all ChatGPT accounts unless configured in the app.

## Connection Steps

1. **Deploy the Server**: First, deploy the VCE MCP Server to a public HTTPS endpoint (e.g., `https://vce-mcp.example.com`). See `REMOTE_DEPLOYMENT.md`.
2. **Obtain Endpoint**: The correct MCP endpoint is the base URL plus `/mcp` (e.g., `https://vce-mcp.example.com/mcp`).
3. **Open ChatGPT**: Open your ChatGPT Desktop app.
4. **Developer Mode**: Navigate to settings and open the MCP / Developer configuration.
5. **Add Server**: Add a new remote Server-Sent Events / HTTP MCP server.
6. **Enter URL**: Provide your `https://YOUR-DOMAIN/mcp` URL.
7. **Verify**: ChatGPT will automatically perform a handshake, negotiate the protocol, and fetch the 15 VCE tools.
8. **Test**: Ask a question like *"What undergraduate programs are offered at Vardhaman College of Engineering?"* ChatGPT will use the `search_vce` tool, hitting your remote backend and returning sourced answers.

*Note: The GitHub repository is just the source code; ChatGPT connects to the remotely deployed endpoint, not the repository.*
