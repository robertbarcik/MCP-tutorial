# MCP Tutorial - Multi-Server IT Support System

A hands-on demonstration of the **Model Context Protocol (MCP)** with 5 specialized servers orchestrated by OpenAI gpt-5-nano.

Welcome to the Model Context Protocol (MCP) tutorial! This guide will teach you how to build a multi-server AI system using MCP, demonstrating real-world patterns for creating intelligent IT support applications.

## What You'll Learn

- How to build multi-server AI systems using MCP
- OpenAI function calling integration
- Server orchestration and tool discovery
- Natural language queries across multiple data sources

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set OpenAI API Key

```bash
export OPENAI_API_KEY="sk-your-key-here"
```

### 3. Try It Out

**Interactive Chat (Recommended):**
```bash
python interactive_client.py
```

Ask questions like:
- "What are all the critical priority tickets?"
- "Show me customer CUST-001's information and SLA terms"
- "Which assets have expired warranties?"

**Jupyter Notebook:**
```bash
jupyter notebook MCP_Demo.ipynb
```

**Test Server Startup:**
```bash
python mcp_client.py
```

---

## Table of Contents

1. [What is MCP?](#what-is-mcp)
2. [System Architecture](#system-architecture)
3. [Repository Structure](#repository-structure)
4. [Getting Started](#getting-started)
5. [Learning Paths](#learning-paths)
6. [Testing Tool Selection](#testing-tool-selection)
7. [Example Queries](#example-queries)
8. [Technical Deep Dive](#technical-deep-dive)
9. [Exercises](#exercises)

---

## What is MCP?

**Model Context Protocol (MCP)** is a protocol for connecting AI models with external tools and data sources. Think of it as a standardized way for AI systems to:

- Discover available tools from multiple services
- Call those tools with properly formatted parameters
- Receive structured responses
- Chain multiple tool calls together to solve complex tasks

### Why MCP?

Traditional approaches to AI tool calling often require:
- Custom integration code for each service
- Manual tool definition management
- Complex routing logic
- Inconsistent error handling

MCP solves these problems by providing:
- **Standardized protocol** for tool discovery and execution
- **Server isolation** - each service runs independently
- **Automatic tool discovery** - AI models learn what's available
- **Type-safe schemas** - tools define their input/output contracts

### Key Concepts

```
┌─────────────────────────────────────────────────────────────┐
│                       LLM (gpt-5-nano)                       │
│              "What are the critical tickets?"                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     MCP Orchestrator                         │
│  • Discovers tools from all servers                         │
│  • Converts tools to LLM-compatible format                  │
│  • Routes tool calls to correct server                      │
│  • Returns results back to LLM                              │
└─────────────────────────────────────────────────────────────┘
           │              │              │              │
           ▼              ▼              ▼              ▼
    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
    │ Ticket  │    │Customer │    │ Billing │    │   KB    │
    │ Server  │    │ Server  │    │ Server  │    │ Server  │
    └─────────┘    └─────────┘    └─────────┘    └─────────┘
```

---

## System Architecture

This tutorial implements a complete **IT Support System** with 5 specialized MCP servers:

### The Five Servers

#### 1. Ticket Management Server
- **Purpose:** Track and manage support tickets
- **Tools:** `search_tickets`, `get_ticket_details`, `get_ticket_metrics`, `find_similar_tickets`
- **Data:** 15 sample tickets (Windows, Linux, macOS issues)

#### 2. Customer Database Server
- **Purpose:** Store customer information and SLA terms
- **Tools:** `lookup_customer`, `check_customer_status`, `get_sla_terms`, `list_customer_contacts`
- **Data:** 8 customers with different support tiers

#### 3. Billing Server
- **Purpose:** Manage invoices and payment tracking
- **Tools:** `get_invoice`, `check_payment_status`, `get_billing_history`, `calculate_outstanding_balance`
- **Data:** 15 invoices linked to customers and tickets

#### 4. Knowledge Base Server
- **Purpose:** Provide technical articles and solutions
- **Tools:** `search_solutions`, `get_article`, `find_related_articles`, `get_common_fixes`
- **Data:** 10 detailed troubleshooting articles

#### 5. Asset Management Server
- **Purpose:** Track hardware/software assets and warranties
- **Tools:** `lookup_asset`, `check_warranty`, `get_software_licenses`, `get_asset_history`
- **Data:** 12 assets with warranty and license information

### How MCP Servers Work

Each MCP server is a standalone Python process that:

1. **Defines tools** using MCP's Tool schema
2. **Implements handlers** for those tools
3. **Communicates** via stdio (stdin/stdout) transport
4. **Returns structured data** as JSON

Example tool definition:
```python
from mcp.server import Server
from mcp.types import Tool

app = Server("ticket-management-server")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_tickets",
            description="Search for tickets by various criteria",
            inputSchema={
                "type": "object",
                "properties": {
                    "priority": {"type": "string"},
                    "status": {"type": "string"}
                }
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "search_tickets":
        # Execute search logic
        return results
```

### The Orchestrator

The **MCP Orchestrator** (`mcp_client.py`) is the central coordinator:

```python
class MCPOrchestrator:
    def start_servers(self):
        # Launch all 5 server processes via subprocess
        # Establish stdio connections
        # Initialize MCP sessions

    def get_available_tools(self):
        # Query each server for its tools
        # Build a mapping of tool_name → server

    def query(self, prompt: str, api_key: str):
        # Convert MCP tools to OpenAI function format
        # Send prompt + tools to gpt-5-nano
        # Execute tool calls on appropriate servers
        # Multi-turn conversation until final answer
```

### Multi-Turn Conversation Flow

```
User: "What are the critical tickets for customer CUST-001?"
         │
         ▼
    ┌─────────────────────────────────────────┐
    │ Orchestrator sends to gpt-5-nano:       │
    │ - User question                          │
    │ - All 20 available tools                │
    └─────────────────────────────────────────┘
         │
         ▼
    ┌─────────────────────────────────────────┐
    │ gpt-5-nano decides to call:             │
    │ search_tickets(customer_id="CUST-001",  │
    │                priority="critical")      │
    └─────────────────────────────────────────┘
         │
         ▼
    ┌─────────────────────────────────────────┐
    │ Orchestrator routes to ticket_server    │
    │ Executes tool, returns results          │
    └─────────────────────────────────────────┘
         │
         ▼
    ┌─────────────────────────────────────────┐
    │ gpt-5-nano receives results             │
    │ Synthesizes final answer                │
    │ "Customer CUST-001 has 2 critical..."   │
    └─────────────────────────────────────────┘
```

---

## Repository Structure

```
MCP-tutorial/
├── README.md                    # This file - complete learning guide
├── requirements.txt             # Python dependencies
│
├── servers/                     # MCP server implementations
│   ├── ticket_server.py         # Ticket management (4 tools)
│   ├── customer_server.py       # Customer database (4 tools)
│   ├── billing_server.py        # Billing system (4 tools)
│   ├── kb_server.py             # Knowledge base (4 tools)
│   └── asset_server.py          # Asset tracking (4 tools)
│
├── mcp_client.py                # Orchestrator (coordinates all servers)
├── interactive_client.py        # CLI chat interface
├── MCP_Demo.ipynb               # Jupyter notebook demo
└── test_intents.py              # Intent mapping test framework
```

### The Five Servers

1. **Ticket Server** - Manage support tickets (search, metrics, similar tickets)
2. **Customer Server** - Customer info and SLA terms
3. **Billing Server** - Invoices and payment tracking
4. **Knowledge Base Server** - Technical articles and solutions
5. **Asset Server** - Hardware/software asset and warranty tracking

**Total: 20 tools** across 5 servers, all discoverable and callable via natural language.

---

## Getting Started

### Prerequisites

- **Python 3.10+**
- **OpenAI API Key** (for gpt-5-nano integration)

### Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

Required packages:
- `mcp>=1.0.0` - MCP SDK
- `openai>=1.0.0` - OpenAI API client
- `nest_asyncio>=1.5.0` - Jupyter compatibility

2. **Set up OpenAI API key:**
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

### Verification

Test that servers can start:
```bash
python mcp_client.py
```

You should see:
```
Starting MCP servers...
  - Starting ticket server (Ticket management server)...
    ✓ ticket server started successfully
  - Starting customer server (Customer database server)...
    ✓ customer server started successfully
  ...
All servers started successfully!
```

---

## Learning Paths

This tutorial offers multiple ways to learn, depending on your goals:

### Path 1: Interactive Chat (Recommended for Beginners)

**Best for:** Understanding how MCP works end-to-end with natural language

```bash
python interactive_client.py
```

Ask questions in plain English:
- "What are all the critical priority tickets?"
- "Show me customer CUST-001's information and SLA terms"
- "Which assets have expired warranties?"

**What you'll learn:**
- How gpt-5-nano decides which tools to call
- Multi-turn conversation patterns
- Tool call chaining and data correlation

### Path 2: Jupyter Notebook (Best for Experimentation)

**Best for:** Testing individual functions and exploring data

```bash
jupyter notebook MCP_Demo.ipynb
```

The notebook shows **direct function calls**:
```python
from ticket_server import search_tickets

# Call functions directly without MCP protocol
tickets = search_tickets(priority="critical")
print(tickets)
```

**What you'll learn:**
- How each server function works independently
- Data structures and schemas
- Function parameters and return values

**Note:** The full MCP orchestrator with subprocesses doesn't work in Jupyter due to stdin/stdout limitations. Use direct function calls instead.

### Path 3: Code Deep Dive (For Advanced Learners)

**Best for:** Understanding implementation details

1. **Start with a single server:** Read `ticket_server.py`
   - How tools are defined with `@app.list_tools()`
   - How handlers work with `@app.call_tool()`
   - Error handling patterns

2. **Understand the orchestrator:** Read `mcp_client.py`
   - Server process management
   - Tool discovery mechanism
   - OpenAI integration
   - Multi-turn conversation loop

3. **Explore cross-server queries:**
   - How data from multiple servers combines
   - Tool selection strategies
   - Error recovery patterns

---

## Testing Tool Selection

The repository includes `test_intents.py`, a comprehensive test framework that validates whether gpt-5-nano correctly selects the appropriate tools for different types of user queries.

### What is Intent Mapping?

**Intent mapping** is the process of understanding a user's natural language query and selecting the correct tool(s) to fulfill that request. This is a critical aspect of MCP systems because:

- The same intent can be expressed in many different ways
- gpt-5-nano must choose from 20 available tools
- Multi-server queries require calling multiple tools in the right order
- Poor tool selection leads to incorrect or incomplete answers

### Why Test Intent Mapping?

Testing ensures that:
1. **Query variations are handled** - "What are critical tickets?" vs "Show me tickets marked as critical"
2. **Correct tools are selected** - Search queries use search tools, not detail lookups
3. **Multi-tool coordination works** - Complex queries call all necessary tools
4. **Edge cases are covered** - Missing data, invalid IDs, ambiguous requests

### Running the Tests

**Basic usage:**
```bash
export OPENAI_API_KEY="sk-your-key-here"
python test_intents.py
```

**What it tests:**

The framework includes 8 intent categories with 5 query variations each (40 total test cases):

1. **Search Critical Tickets** - Tests priority-based ticket searches
2. **Customer with Tickets** - Tests cross-server queries (customer + tickets)
3. **Billing Status** - Tests financial queries (invoices, payments)
4. **Knowledge Base Search** - Tests KB article lookups
5. **Asset Warranty Check** - Tests asset and warranty queries
6. **Multi-Server Analysis** - Tests comprehensive customer overviews
7. **Ticket Metrics** - Tests statistical queries
8. **Similar Tickets** - Tests similarity matching

### Understanding Test Results

**Output format:**
```
Test Case: search_critical_tickets
Description: User wants to find critical priority tickets
Expected Tools: search_tickets
============================================================

  Testing: 'What are the critical tickets?'
    ✅ PASS: All validations passed
    Tools: search_tickets

  Testing: 'Show me all critical priority tickets'
    ✅ PASS: All validations passed
    Tools: search_tickets

  📊 Success Rate: 5/5 (100.0%)
```

**Success criteria:**
- ✅ **Pass:** Correct tools were called with expected parameters
- ❌ **Fail:** Wrong tools called, missing tools, or incorrect parameters

**Overall summary:**
```
Total Test Variations: 40
Passed: 38
Failed: 2
Overall Success Rate: 95.0%

Per-Intent Breakdown:
✅ search_critical_tickets      5/5 (100.0%)
✅ customer_with_tickets         5/5 (100.0%)
⚠️ billing_status               4/5 (80.0%)
```

### How It Works

The test framework:

1. **Starts all MCP servers** - Initializes the full orchestrator
2. **Captures tool calls** - Intercepts which tools gpt-5-nano selects
3. **Validates selections** - Checks if correct tools were called
4. **Generates report** - Shows pass/fail for each query variation

**Example test case:**
```python
{
    "intent": "search_critical_tickets",
    "description": "User wants to find critical priority tickets",
    "variations": [
        "What are the critical tickets?",
        "Show me all critical priority tickets",
        "List tickets with critical priority",
    ],
    "expected_tools": ["search_tickets"],
    "expected_args_contain": {"priority": "critical"},
}
```

### Teaching Use Cases

Use `test_intents.py` to demonstrate:

1. **Natural language variations** - Show students how many ways users express the same intent
2. **Tool selection strategies** - Discuss why gpt-5-nano chose specific tools
3. **Debugging failures** - Analyze why certain queries fail and how to improve them
4. **Adding new intents** - Have students add test cases for new query types
5. **Model comparison** - Test different models to compare tool selection accuracy

### Extending the Tests

Students can add their own test cases:

```python
{
    "intent": "your_custom_intent",
    "description": "What the user wants to accomplish",
    "variations": [
        "Query variation 1",
        "Query variation 2",
        "Query variation 3",
    ],
    "expected_tools": ["tool1", "tool2"],
    "min_tool_calls": 2,  # At least 2 tools should be called
}
```

### Common Failure Patterns

**Too few tool calls:**
- gpt-5-nano didn't gather enough information
- May need more context in the query

**Wrong tools selected:**
- Query might be ambiguous
- Tool descriptions might need clarification

**Missing parameters:**
- Expected arguments not provided
- gpt-5-nano might need better examples

---

## Example Queries

Here are example queries you can try with `interactive_client.py`. They demonstrate different capabilities:

### Single-Server Queries

#### Example 1: Find Critical Tickets
```
Query: "What are all the critical priority tickets? List them with their IDs, subjects, and status."

What happens:
- gpt-5-nano calls: search_tickets(priority="critical")
- Returns: List of critical tickets from ticket server
```

#### Example 2: Customer SLA Information
```
Query: "Tell me about customer CUST-001. What are their SLA terms and who are their contacts?"

What happens:
- gpt-5-nano calls: lookup_customer(customer_id="CUST-001")
- gpt-5-nano calls: get_sla_terms(customer_id="CUST-001")
- gpt-5-nano calls: list_customer_contacts(customer_id="CUST-001")
- Returns: Comprehensive customer information
```

#### Example 3: Outstanding Invoices
```
Query: "Show me all overdue invoices and which customers have outstanding balances."

What happens:
- gpt-5-nano calls: get_billing_history() or check_payment_status()
- May call: lookup_customer() for each customer with overdue invoices
- Returns: Financial summary with customer details
```

#### Example 4: KB Article Search
```
Query: "Find knowledge base articles about Windows BSOD issues. What are the recommended solutions?"

What happens:
- gpt-5-nano calls: search_solutions(query="BSOD")
- May call: get_article() for specific articles
- Returns: Relevant articles with solutions
```

#### Example 5: Warranty Expiration Check
```
Query: "Which assets have warranties expiring in the next 30 days or have already expired?"

What happens:
- gpt-5-nano calls: check_warranty() for multiple assets
- Or: lookup_asset() with filtering
- Returns: List of assets needing attention
```

### Multi-Server Queries

#### Example 6: Complete Customer Analysis
```
Query: "For customer CUST-002 (DataFlow Solutions), show me their current tickets, outstanding invoices, and assets. Is there anything that needs immediate attention?"

What happens:
- gpt-5-nano calls: lookup_customer(customer_id="CUST-002")
- gpt-5-nano calls: search_tickets(customer_id="CUST-002")
- gpt-5-nano calls: calculate_outstanding_balance(customer_id="CUST-002")
- gpt-5-nano calls: lookup_asset(customer_id="CUST-002")
- Returns: Comprehensive analysis across all systems
```

#### Example 7: Troubleshooting Help
```
Query: "Find similar tickets to TKT-1001 and check if there's a knowledge base article that could help resolve it."

What happens:
- gpt-5-nano calls: get_ticket_details(ticket_id="TKT-1001")
- gpt-5-nano calls: find_similar_tickets(ticket_id="TKT-1001")
- gpt-5-nano calls: search_solutions() based on ticket tags/category
- Returns: Related tickets and relevant KB articles
```

### Complex Analysis Queries

Try these to see advanced multi-tool coordination:

```
"Which customers have both critical tickets AND overdue invoices?"

"Show me all Linux-related tickets and relevant KB articles for each."

"Are there any assets assigned to customers who have expired warranties and open tickets?"

"Calculate the total outstanding balance for all customers with premium SLA terms."
```

---

## Technical Deep Dive

### Error Handling: LLM-Friendly Responses

One key innovation in this tutorial is **structured error messages** that help gpt-5-nano recover gracefully:

```python
def make_error(message, *, reason=None, hints=None, retryable=False,
               follow_up_tools=None, context=None):
    """Create LLM-friendly error payload"""
    return {
        "error": message,                    # Short problem statement
        "reason": reason,                    # Human-readable diagnosis
        "suggested_actions": hints,          # What to do next
        "retryable": retryable,              # Should the LLM retry?
        "follow_up_tools": follow_up_tools,  # Recommended next tools
        "context": context                   # Additional context
    }
```

Example error response:
```json
{
  "error": "Ticket TKT-9999 not found",
  "reason": "The ticket_id did not match any tickets in the dataset.",
  "suggested_actions": [
    "Call search_tickets with customer_id or priority filters to rediscover the ticket.",
    "Verify the ticket_id format (e.g., TKT-1001)."
  ],
  "retryable": true,
  "follow_up_tools": ["search_tickets"],
  "context": {"ticket_id": "TKT-9999"}
}
```

This helps gpt-5-nano:
1. Understand what went wrong
2. Know whether to retry with different parameters
3. Choose the next best tool to call
4. Provide helpful feedback to the user

### Dual-Mode Functions

Each server implements functions that work in **two modes**:

1. **As regular Python functions** (for direct import)
2. **As MCP tools** (for protocol-based calls)

Example:
```python
# Regular Python function
def search_tickets(priority=None, status=None):
    """Can be called directly"""
    results = [t for t in TICKETS if matches(t, priority, status)]
    return {"tickets": results, "total_count": len(results)}

# MCP wrapper
@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "search_tickets":
        result = search_tickets(**arguments)
        return [TextContent(type="text", text=json.dumps(result))]
```

Benefits:
- **Testing:** Call functions directly without MCP setup
- **Jupyter:** Works in notebooks without subprocess issues
- **Debugging:** Easier to trace function execution
- **Flexibility:** Use with or without OpenAI integration

### Jupyter Compatibility

The orchestrator detects Jupyter environments and handles event loops properly:

```python
def _is_jupyter():
    """Detect if we're running in a Jupyter notebook"""
    try:
        from IPython import get_ipython
        return get_ipython() is not None
    except ImportError:
        return False

def _run_async(coro):
    """Run async code in both Jupyter and regular Python"""
    loop, is_running = _ensure_event_loop()

    if is_running:
        # Jupyter: Use nest_asyncio for nested loops
        import nest_asyncio
        nest_asyncio.apply()
        return asyncio.run(coro)
    else:
        # Regular Python
        return loop.run_until_complete(coro)
```

### OpenAI Integration

The orchestrator converts MCP tools to OpenAI's function calling format:

```python
# MCP Tool Format
{
  "name": "search_tickets",
  "description": "Search for tickets...",
  "inputSchema": {
    "type": "object",
    "properties": {"priority": {"type": "string"}}
  }
}

# ↓ Conversion ↓

# OpenAI Function Format
{
  "type": "function",
  "function": {
    "name": "search_tickets",
    "description": "Search for tickets...",
    "parameters": {
      "type": "object",
      "properties": {"priority": {"type": "string"}}
    }
  }
}
```

---

## Exercises

### Exercise 1: Add a New Tool

**Goal:** Add a tool to count tickets by priority

**Steps:**
1. Open `servers/ticket_server.py`
2. Add a new function:
```python
def count_tickets_by_priority():
    """Count tickets grouped by priority"""
    counts = {}
    for ticket in TICKETS:
        priority = ticket.get("priority", "unknown")
        counts[priority] = counts.get(priority, 0) + 1
    return {"priority_counts": counts}
```

3. Register it as an MCP tool in `list_tools()`
4. Add handler in `call_tool()`
5. Test with interactive client

### Exercise 2: Create a Cross-Server Query

**Goal:** Find customers with high-priority tickets and overdue invoices

**Think about:**
- Which tools would gpt-5-nano need to call?
- In what order?
- How would results be correlated?

**Try asking:**
```
"Which customers have both high-priority or critical tickets AND overdue invoices?
Show me their names, ticket counts, and total overdue amounts."
```

### Exercise 3: Improve Error Messages

**Goal:** Add better error guidance when a customer is not found

**Steps:**
1. Open `servers/customer_server.py`
2. Find the `lookup_customer()` function
3. Enhance the error response with:
   - More specific hints
   - List of valid customer IDs
   - Suggestion to search by company name

### Exercise 4: Build Your Own Server

**Goal:** Create a new MCP server (e.g., "scheduling server" for maintenance windows)

**Requirements:**
1. Define 3-4 tools
2. Use in-memory sample data
3. Implement proper error handling
4. Add it to the orchestrator's server configs
5. Test with natural language queries

---

## Additional Resources

### Sample Data Overview

All servers contain realistic, interconnected data:

- **15 tickets** - Windows, Linux, macOS issues with realistic problems
- **8 customers** - Different tiers (basic, standard, premium)
- **15 invoices** - Mix of paid, pending, and overdue
- **10 KB articles** - Detailed technical solutions
- **12 assets** - Servers, workstations, laptops with warranty tracking

Data is cross-referenced: tickets link to customers, invoices link to tickets, assets link to customers.

### Key Files Reference

| File | Purpose |
|------|---------|
| `mcp_client.py` | Orchestrator - coordinates all servers |
| `interactive_client.py` | CLI interface for natural language queries |
| `servers/ticket_server.py` | Ticket management MCP server |
| `servers/customer_server.py` | Customer database MCP server |
| `servers/billing_server.py` | Billing system MCP server |
| `servers/kb_server.py` | Knowledge base MCP server |
| `servers/asset_server.py` | Asset tracking MCP server |
| `MCP_Demo.ipynb` | Jupyter notebook with direct function calls |

### Performance Characteristics

- **Startup time:** ~2-3 seconds (all 5 servers)
- **Tool discovery:** <1 second
- **Single tool call:** 50-200ms
- **OpenAI API call:** 1-5 seconds (network dependent)
- **Complex multi-tool query:** 5-15 seconds

### Troubleshooting

**Servers won't start:**
- Check Python version: `python --version` (need 3.10+)
- Verify all server files exist
- Try running a single server: `python servers/ticket_server.py`

**OpenAI API errors:**
- Verify API key: `echo $OPENAI_API_KEY`
- Check API quota/credits
- Ensure network connectivity

**Tool calls failing:**
- Check argument types match schema
- Look for error messages in terminal
- Test function directly in Python

**Jupyter issues:**
- Don't try to use MCP orchestrator with subprocesses in Jupyter
- Use direct function imports instead
- See `MCP_Demo.ipynb` for examples

---

## Next Steps

After completing this tutorial, you can:

1. **Extend the system** - Add more servers (e.g., monitoring, scheduling)
2. **Enhance tools** - Add more sophisticated search and filtering
3. **Production deployment** - Replace in-memory data with real databases
4. **Scale up** - Implement connection pooling, caching, queuing
5. **Advanced patterns** - Implement tool chaining, conditional logic, error recovery

### Learn More About MCP

- [MCP Official Documentation](https://github.com/anthropics/mcp)
- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)

---

**Happy Learning! 🚀**

For questions or issues, check the repository's issue tracker or reach out to your instructor.

## License

MIT

## Credits

Built with:
- [Model Context Protocol (MCP)](https://github.com/anthropics/mcp)
- [OpenAI API](https://platform.openai.com/)
