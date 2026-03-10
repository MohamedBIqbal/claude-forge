
---

## MCP Server Patterns

### Server Structure
```python
server = Server("server-name")

@server.list_tools()
async def list_tools():
    return [Tool(name="...", description="...", inputSchema={...})]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    # Implementation
```

### Tool Design
- Clear, descriptive tool names
- Comprehensive inputSchema with required/optional fields
- Return structured TextContent or ImageContent

### Error Handling
- Return error messages as TextContent
- Use appropriate HTTP-style error codes in messages
- Log errors server-side for debugging

### Testing
- Test tools independently before integration
- Use stdio transport for local development
- Test with Claude Code before production deployment
