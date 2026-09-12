# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2026-09-12

### Added
- **Remote Streamable HTTP Transport**: Added `vce-mcp serve-http` to run the MCP server over HTTP for remote ChatGPT/Claude connectivity.
- **Docker Support**: Added `Dockerfile` and `.dockerignore` for seamless cloud deployment.
- **Health Endpoint**: Added `GET /health` endpoint for uptime monitoring and container orchestration.
- **Transport Security**: Added automatic DNS rebinding protection via `VCE_MCP_ALLOWED_HOSTS`.
- **Remote MCP Integration Tests**: Validates the HTTP handshake and MCP protocol locally.

### Changed
- Preserved existing local stdio mode (`vce-mcp server`).
- Preserved existing SQLite, ChromaDB, and all 15 institutional knowledge tools.

## [1.0.0] - 2026-09-12
- Initial Release with Local Stdio MCP Transport, SQLite, ChromaDB, and Web Crawler.
