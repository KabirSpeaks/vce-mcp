import pytest
from starlette.testclient import TestClient
from vce_mcp.http_server import app

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "vce-mcp"
    assert "version" in data

def test_mcp_endpoints_exist(client):
    # MCP requires POST for messages/initialization via streamable http
    # Test that /mcp at least accepts POST or GET and doesn't 404.
    response = client.get("/mcp")
    assert response.status_code != 404
