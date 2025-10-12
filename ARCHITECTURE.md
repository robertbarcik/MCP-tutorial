# MCP Tutorial - System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                         USER INTERFACE                          │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │  interactive_    │  │  example_        │  │   Custom     │ │
│  │  client.py       │  │  queries.py      │  │   Scripts    │ │
│  └──────────────────┘  └──────────────────┘  └──────────────┘ │
│           │                      │                    │         │
└───────────┼──────────────────────┼────────────────────┼─────────┘
            │                      │                    │
            └──────────────────────┴────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                     MCP ORCHESTRATOR                            │
│                     (mcp_client.py)                             │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  MCPOrchestrator Class                                  │  │
│  │                                                          │  │
│  │  • start_servers()      - Launch all MCP servers        │  │
│  │  • stop_servers()       - Clean shutdown               │  │
│  │  • get_available_tools() - Discover server tools       │  │
│  │  • query()              - Process user queries          │  │
│  │  • call_mcp_tool()      - Execute tool on server       │  │
│  │  • convert_to_openai()  - Format tools for OpenAI      │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   Server     │  │     Tool     │  │    OpenAI    │        │
│  │  Process     │  │   Mapping    │  │  Integration │        │
│  │  Manager     │  │              │  │   (GPT-4)    │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
            │              │              │              │
            │              │              │              │
     ┌──────┘              │              │              └──────┐
     │                     │              │                     │
     ▼                     ▼              ▼                     ▼
┌─────────┐         ┌──────────┐   ┌──────────┐         ┌──────────┐
│ Ticket  │         │ Customer │   │ Billing  │         │    KB    │
│ Server  │         │  Server  │   │  Server  │         │  Server  │
│         │         │          │   │          │         │          │
│  stdio  │         │  stdio   │   │  stdio   │         │  stdio   │
│transport│         │transport │   │transport │         │transport │
└─────────┘         └──────────┘   └──────────┘         └──────────┘
     │
     ▼
┌──────────┐
│  Asset   │
│  Server  │
│          │
│  stdio   │
│transport │
└──────────┘
```

## Component Details

### 1. MCP Servers (5 Independent Processes)

Each server is a standalone Python process running the MCP SDK:

```python
# Example: ticket_server.py
from mcp.server import Server
from mcp.server.stdio import stdio_server

app = Server("ticket-management-server")

@app.list_tools()
async def list_tools():
    return [Tool(...), Tool(...)]

@app.call_tool()
async def call_tool(name, arguments):
    # Execute tool logic
    return result
```

**Communication**: stdio (stdin/stdout pipes)
**Transport**: MCP stdio transport protocol
**State**: Each server maintains its own sample data

### 2. MCP Orchestrator (Central Coordinator)

The orchestrator manages all servers and coordinates requests:

```python
class MCPOrchestrator:
    def __init__(self):
        self.server_processes = {}      # Process handles
        self.server_sessions = {}       # MCP client sessions
        self.available_tools = []       # All discovered tools
        self.tool_to_server_map = {}    # Tool → Server mapping
```

**Key Responsibilities**:
- Launch server processes via subprocess
- Establish MCP client connections (stdio transport)
- Discover and catalog all available tools
- Route tool calls to correct server
- Integrate with OpenAI GPT-4

### 3. OpenAI Integration

The orchestrator converts MCP tools to OpenAI's function calling format:

```
MCP Tool Format:
{
  "name": "search_tickets",
  "description": "Search for tickets...",
  "inputSchema": {
    "type": "object",
    "properties": {...}
  }
}

              ↓ Conversion ↓

OpenAI Tool Format:
{
  "type": "function",
  "function": {
    "name": "search_tickets",
    "description": "Search for tickets...",
    "parameters": {
      "type": "object",
      "properties": {...}
    }
  }
}
```

## Query Processing Flow

```
┌──────────────────────────────────────────────────────────────┐
│ 1. USER QUERY                                                │
└──────────────────────────────────────────────────────────────┘
   "What are the critical tickets for customer CUST-001?"
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ 2. ORCHESTRATOR PREPARATION                                  │
│    • Collect all tools from servers                          │
│    • Convert to OpenAI format                                │
│    • Prepare conversation context                            │
└──────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ 3. OPENAI API CALL                                           │
│    POST /v1/chat/completions                                 │
│    {                                                          │
│      "model": "gpt-4",                                        │
│      "messages": [...],                                       │
│      "tools": [20 tools from all servers]                    │
│    }                                                          │
└──────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ 4. GPT-4 DECISION                                            │
│    Model analyzes query and decides to call:                 │
│    • search_tickets(customer_id="CUST-001", priority="critical")│
└──────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ 5. ORCHESTRATOR ROUTING                                      │
│    • Looks up tool_to_server_map                             │
│    • search_tickets → ticket_server                          │
│    • Gets server session                                     │
└──────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ 6. MCP TOOL CALL                                             │
│    ticket_server.call_tool(                                  │
│      "search_tickets",                                       │
│      {"customer_id": "CUST-001", "priority": "critical"}     │
│    )                                                          │
└──────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ 7. SERVER EXECUTION                                          │
│    • Filters TICKETS array                                   │
│    • Returns matching tickets as JSON                        │
└──────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ 8. RESULT TO GPT-4                                           │
│    Orchestrator sends tool result back to OpenAI            │
└──────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ 9. MULTI-TURN CONTINUATION                                   │
│    GPT-4 may call more tools or provide final answer         │
│    • If more tools needed: Go to step 5                      │
│    • If done: Return final answer                            │
└──────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ 10. FINAL RESPONSE                                           │
│     "Customer CUST-001 has 2 critical priority tickets:      │
│      TKT-1001 (Windows BSOD) and TKT-1004 (Network issues)"  │
└──────────────────────────────────────────────────────────────┘
```

## Data Flow

### Server ↔ Orchestrator Communication

```
Orchestrator                           Server
    │                                     │
    │  Initialize Connection (stdio)     │
    ├────────────────────────────────────>│
    │                                     │
    │  list_tools()                      │
    ├────────────────────────────────────>│
    │                                     │
    │  <── Tools List                    │
    │<────────────────────────────────────┤
    │                                     │
    │  call_tool(name, args)             │
    ├────────────────────────────────────>│
    │                                     │
    │                    Execute Tool ──┐ │
    │                                   │ │
    │                    Query Data ────┤ │
    │                                   │ │
    │                    Format Result ─┘ │
    │                                     │
    │  <── Result (JSON)                 │
    │<────────────────────────────────────┤
    │                                     │
```

### Orchestrator ↔ OpenAI Communication

```
Orchestrator                           OpenAI API
    │                                     │
    │  POST /chat/completions            │
    │  {                                  │
    │    messages: [...],                 │
    │    tools: [...]                     │
    │  }                                  │
    ├────────────────────────────────────>│
    │                                     │
    │                      Analyze ───┐   │
    │                                 │   │
    │                      Decide ────┤   │
    │                      Tool Call ─┘   │
    │                                     │
    │  <── Response with tool_calls      │
    │<────────────────────────────────────┤
    │                                     │
    │  [Execute tools on MCP servers]    │
    │                                     │
    │  POST /chat/completions            │
    │  {                                  │
    │    messages: [...],                 │
    │    tool_results: [...]              │
    │  }                                  │
    ├────────────────────────────────────>│
    │                                     │
    │  <── Final Answer                  │
    │<────────────────────────────────────┤
```

## Process Lifecycle

### Startup Sequence

```
1. User runs: python mcp_client.py
              │
              ▼
2. Create MCPOrchestrator instance
              │
              ▼
3. Call start_servers()
              │
              ├──> Launch ticket_server.py subprocess
              ├──> Launch customer_server.py subprocess
              ├──> Launch billing_server.py subprocess
              ├──> Launch kb_server.py subprocess
              └──> Launch asset_server.py subprocess
              │
              ▼
4. Establish stdio connections to each server
              │
              ▼
5. Initialize MCP client sessions
              │
              ▼
6. Call get_available_tools()
              │
              ├──> ticket_server: 4 tools
              ├──> customer_server: 4 tools
              ├──> billing_server: 4 tools
              ├──> kb_server: 4 tools
              └──> asset_server: 4 tools
              │
              ▼
7. Build tool_to_server_map
              │
              ▼
8. Ready to process queries
```

### Shutdown Sequence

```
1. User presses Ctrl+C or calls stop_servers()
              │
              ▼
2. Close each MCP client session
              │
              ▼
3. Close stdio transports
              │
              ▼
4. Server processes automatically terminate
              │
              ▼
5. Clean up resources
```

## Tool Distribution

```
┌──────────────────────────────────────────────────────┐
│                   All 20 Tools                       │
├──────────────────────────────────────────────────────┤
│                                                      │
│  Ticket Server (4)              Customer Server (4)  │
│  • search_tickets               • lookup_customer    │
│  • get_ticket_details           • check_customer_status │
│  • get_ticket_metrics           • get_sla_terms      │
│  • find_similar_tickets         • list_customer_contacts │
│                                                      │
│  Billing Server (4)             KB Server (4)        │
│  • get_invoice                  • search_solutions   │
│  • check_payment_status         • get_article        │
│  • get_billing_history          • find_related_articles │
│  • calculate_outstanding_balance • get_common_fixes  │
│                                                      │
│  Asset Server (4)                                    │
│  • lookup_asset                                      │
│  • check_warranty                                    │
│  • get_software_licenses                             │
│  • get_asset_history                                 │
│                                                      │
└──────────────────────────────────────────────────────┘
```

## Error Handling

```
┌─────────────────────────────────────────┐
│  Error Types & Handling Strategy        │
├─────────────────────────────────────────┤
│                                         │
│  1. Server Startup Failure              │
│     • Log error                         │
│     • Stop other servers                │
│     • Exit with error code              │
│                                         │
│  2. Tool Call Failure                   │
│     • Return error JSON to GPT-4        │
│     • Let GPT-4 handle gracefully       │
│     • Continue processing               │
│                                         │
│  3. OpenAI API Error                    │
│     • Log error                         │
│     • Return error message to user      │
│     • Maintain server connections       │
│                                         │
│  4. Network/Transport Error             │
│     • Retry once                        │
│     • If fails, mark server unavailable │
│     • Continue with remaining servers   │
│                                         │
│  5. Keyboard Interrupt (Ctrl+C)         │
│     • Graceful shutdown                 │
│     • Close all connections             │
│     • Terminate server processes        │
│                                         │
└─────────────────────────────────────────┘
```

All MCP servers emit a shared error envelope:
- `error`: short problem statement
- `reason`: human-readable diagnosis
- `suggested_actions`: concrete follow-up ideas
- `retryable`: whether the caller should try again with new parameters
- Optional `follow_up_tools` and `context` fields that point GPT toward useful next steps

The orchestrator returns the same structure when tools are missing or sessions fail, so the agent loop receives consistent guidance regardless of where the failure occurs.

## Security Considerations

1. **API Key Management**
   - Never hardcode API keys
   - Use environment variables
   - Validate before use

2. **Process Isolation**
   - Each server runs in separate process
   - Limited inter-process communication
   - stdio transport only

3. **Input Validation**
   - Server-side parameter validation
   - Type checking via JSON schemas
   - Bounds checking for arrays

4. **Resource Limits**
   - Max iterations for query loop (10)
   - Timeout for tool calls
   - Memory limits per server process

## Performance Characteristics

- **Startup Time**: ~2-3 seconds (all servers)
- **Tool Discovery**: <1 second
- **Single Tool Call**: 50-200ms
- **OpenAI API Call**: 1-5 seconds (network dependent)
- **Complex Query**: 5-15 seconds (multiple tool calls)

## Scalability Notes

Current implementation is designed for:
- **Concurrent Users**: 1 (single process)
- **Data Volume**: Small (in-memory datasets)
- **Tool Count**: 20 total

For production scaling:
- Use message queue for multi-user support
- Replace in-memory data with databases
- Implement connection pooling
- Add caching layer
- Deploy servers as microservices
