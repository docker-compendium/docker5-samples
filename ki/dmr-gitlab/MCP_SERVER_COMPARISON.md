# MCP vs. GitLab Proxy Options

> The default stack now ships with a lightweight GitLab proxy (`gitlab-proxy/`)
> that exposes the endpoints the chatbot needs. This document explores what
> would change if we swapped that proxy for a true MCP server implementation.

## Current Implementation (Custom HTTP-based)

**Pros:**

- ✅ Simple HTTP REST API that your FastAPI app can call directly
- ✅ Works perfectly with Docker Compose networking
- ✅ Easy to debug (standard HTTP requests/responses)
- ✅ Already working and tested
- ✅ Minimal dependencies

**Cons:**

- ❌ Not using standard MCP protocol
- ❌ Custom implementation to maintain

## Standard MCP Servers (stdio/SSE transport)

**Pros:**

- ✅ Uses official MCP protocol
- ✅ Potentially more features from community implementations
- ✅ Standardized interface

**Cons:**

- ❌ Requires MCP client library in your Python app (e.g., `mcp` package)
- ❌ More complex integration (stdio requires subprocess management)
- ❌ Need to refactor `app/main.py` to use MCP client instead of HTTP
- ❌ May need HTTP-to-MCP adapter/wrapper

## Recommendation

**Keep your current custom HTTP server** because:

1. It's working well for your use case
2. Your app is designed for HTTP communication
3. Switching would require significant refactoring
4. The HTTP approach is actually simpler for containerized services

## If You Still Want to Use a Standard MCP Server

You would need to:

1. **Install MCP client library:**
   ```bash
   pip install mcp
   ```

2. **Refactor `app/main.py`** to use MCP client instead of HTTP:
   ```python
   from mcp import ClientSession, StdioServerParameters
   from mcp.client.stdio import stdio_client

   # Instead of HTTP calls, use:
   async with stdio_client(server_params) as (read, write):
       async with ClientSession(read, write) as session:
           tools = await session.list_tools()
           result = await session.call_tool("list_open_issues", {})
   ```

3. **Update Docker Compose** to run MCP server as subprocess or use SSE
   transport

4. **Handle stdio/SSE communication** instead of simple HTTP requests

This is significantly more complex than your current HTTP approach.

## Alternative: HTTP Wrapper for Standard MCP Server

You could create a thin HTTP wrapper that:

- Accepts HTTP requests (like your current server)
- Internally uses an MCP client to communicate with a standard MCP server
- Returns HTTP responses

But this adds complexity without much benefit for your use case.
