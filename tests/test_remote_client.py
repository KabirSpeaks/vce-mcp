import asyncio
import os
import uvicorn
from multiprocessing import Process
import time

def run_server():
    # Remove explicit VCE_MCP_ALLOWED_HOSTS so it falls back to default localhost:*
    if "VCE_MCP_ALLOWED_HOSTS" in os.environ:
        del os.environ["VCE_MCP_ALLOWED_HOSTS"]
    uvicorn.run("vce_mcp.http_server:app", host="127.0.0.1", port=8001)

async def test_mcp_client():
    from mcp import ClientSession
    from mcp.client.streamable_http import streamable_http_client
    
    server_url = "http://127.0.0.1:8001/mcp"
    
    print(f"Connecting to {server_url}...")
    try:
        async with streamable_http_client(server_url) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                
                tools = await session.list_tools()
                print("TOOLS FOUND:", [t.name for t in tools.tools])
                assert len(tools.tools) == 15, f"Expected 15 tools, found {len(tools.tools)}"
                
                print("Calling search_vce...")
                result = await session.call_tool("search_vce", {"query": "What undergraduate programs does Vardhaman College of Engineering offer?"})
                print("Search result:", result.content)
                assert len(result.content) > 0, "Expected non-empty result"
                
                print("Calling a test query...")
                res = await session.call_tool("search_vce", {"query": "Vardhaman College campus"})
                assert len(res.content) > 0, "Query failed!"
                
                print("ALL REMOTE HTTP TESTS PASSED!")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("Test failed:", e)

if __name__ == "__main__":
    import requests
    p = Process(target=run_server)
    p.start()
    
    # Wait for server to start
    for _ in range(30):
        try:
            if requests.get("http://127.0.0.1:8001/health").status_code == 200:
                break
        except:
            time.sleep(0.5)
    else:
        print("Server failed to start!")
        p.terminate()
        exit(1)
        
    try:
        asyncio.run(test_mcp_client())
    finally:
        p.terminate()
        p.join()
