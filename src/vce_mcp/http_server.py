import os
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route, Mount
from mcp.server.transport_security import TransportSecuritySettings

from vce_mcp.server import mcp

def health_check(request):
    return JSONResponse({
        "status": "ok",
        "service": "vce-mcp",
        "version": "1.1.0"
    })

def create_app() -> Starlette:
    # 1. Parse allowed hosts from environment for Transport Security
    allowed_hosts_env = os.environ.get("VCE_MCP_ALLOWED_HOSTS", "")
    if allowed_hosts_env:
        allowed_hosts = [h.strip() for h in allowed_hosts_env.split(",") if h.strip()]
        security_settings = TransportSecuritySettings(allowed_hosts=allowed_hosts)
    else:
        # If None, mcp.streamable_http_app will automatically enable safe defaults 
        # for localhost ("127.0.0.1:*", "localhost:*")
        security_settings = None

    # 2. Retrieve the MCP Streamable HTTP app
    # We use streamable_http_path='/mcp' as specified.
    mcp_app = mcp.streamable_http_app(
        streamable_http_path="/mcp",
        transport_security=security_settings
    )

    # 3. Add /health route directly to the mcp_app to preserve its native lifespan
    mcp_app.router.routes.append(Route("/health", endpoint=health_check, methods=["GET"]))
    
    return mcp_app

app = create_app()
