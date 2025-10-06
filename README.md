# MCP Tutorial - Multi-Server IT Support System

A demonstration of the Model Context Protocol (MCP) with 5 specialized servers orchestrated by an OpenAI GPT-4 client.

## Overview

This project implements a complete IT support system using MCP servers:

- **Ticket Management Server** - Search and manage support tickets
- **Customer Database Server** - Customer information and SLA terms
- **Billing Server** - Invoices, payments, and billing history
- **Knowledge Base Server** - IT troubleshooting articles and solutions
- **Asset Management Server** - Hardware/software asset tracking and warranties

All servers are coordinated by an MCP orchestrator that integrates with OpenAI's GPT-4 for natural language queries.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User / Interactive Client                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              MCP Orchestrator (mcp_client.py)               │
│  - Manages server processes                                 │
│  - Coordinates tool calls                                   │
│  - Integrates with OpenAI GPT-4                            │
└─────────────────────────────────────────────────────────────┘
          │          │          │          │          │
          ▼          ▼          ▼          ▼          ▼
    ┌─────────┐┌─────────┐┌─────────┐┌─────────┐┌─────────┐
    │ Ticket  ││Customer ││ Billing ││   KB    ││  Asset  │
    │ Server  ││ Server  ││ Server  ││ Server  ││ Server  │
    └─────────┘└─────────┘└─────────┘└─────────┘└─────────┘
```

## Files

### MCP Servers
- `ticket_server.py` - Ticket management (15 sample tickets)
- `customer_server.py` - Customer database (8 customers with SLA terms)
- `billing_server.py` - Billing system (15 invoices)
- `kb_server.py` - Knowledge base (10 detailed technical articles)
- `asset_server.py` - Asset tracking (12 hardware/software assets)

### Client/Orchestrator
- `mcp_client.py` - Main orchestrator class (MCPOrchestrator)
- `interactive_client.py` - Interactive chat interface
- `example_queries.py` - Demonstration script with example queries

## Setup

### Prerequisites

1. **Python 3.10+**
2. **Install dependencies:**

```bash
pip install openai mcp anthropic-mcp-client
```

3. **OpenAI API Key:**

```bash
export OPENAI_API_KEY="sk-..."
```

## Usage

### 1. Test Server Startup

Verify all servers can start and stop:

```bash
python mcp_client.py
```

Press Ctrl+C to stop.

### 2. Interactive Mode

Chat with the AI assistant using natural language:

```bash
python interactive_client.py
```

Example questions:
- "What are all the critical priority tickets?"
- "Show me customer CUST-001's information and SLA terms"
- "What's the outstanding balance for TechCorp Industries?"
- "Find KB articles about Windows BSOD issues"
- "Check warranty status for asset AST-SRV-001"
- "Show me all tickets for customer CUST-002 and their invoices"

### 3. Run Example Queries

Execute a series of demonstration queries:

```bash
python example_queries.py
```

This runs 7 example queries showing:
- Single-server queries
- Multi-server data correlation
- Complex analysis requiring multiple tool calls

## How It Works

### MCP Orchestrator Flow

1. **Server Startup**
   - Launches all 5 server processes via subprocess
   - Establishes stdio transport connections to each server
   - Initializes MCP client sessions

2. **Tool Discovery**
   - Queries each server for available tools
   - Collects all tool definitions (20 tools total)
   - Maps tools to their respective servers

3. **Query Processing**
   - User asks a question in natural language
   - Orchestrator converts MCP tools to OpenAI function calling format
   - Sends query + tools to GPT-4

4. **Multi-Turn Conversation**
   - GPT-4 decides which tools to call
   - Orchestrator executes tools on appropriate MCP servers
   - Results sent back to GPT-4
   - Process repeats until GPT-4 has enough information
   - Final answer returned to user

### Example Query Flow

```
User: "What are the critical tickets and who are the customers?"

  ├─> GPT-4: Calls search_tickets(priority="critical")
  │   └─> ticket_server.py executes search
  │       └─> Returns 3 critical tickets
  │
  ├─> GPT-4: Calls lookup_customer(customer_id="CUST-002")
  │   └─> customer_server.py executes lookup
  │       └─> Returns customer details
  │
  ├─> GPT-4: Calls lookup_customer(customer_id="CUST-007")
  │   └─> customer_server.py executes lookup
  │       └─> Returns customer details
  │
  └─> GPT-4: Synthesizes final answer with all information
```

## Available Tools (20 total)

### Ticket Server (4 tools)
- `search_tickets` - Search tickets by status, priority, OS, date, etc.
- `get_ticket_details` - Get full details of a specific ticket
- `get_ticket_metrics` - Calculate ticket statistics
- `find_similar_tickets` - Find similar tickets based on tags/category

### Customer Server (4 tools)
- `lookup_customer` - Find customer by ID, email, or company name
- `check_customer_status` - Check account status
- `get_sla_terms` - Get SLA details
- `list_customer_contacts` - Get all contacts for a customer

### Billing Server (4 tools)
- `get_invoice` - Get invoice by ID or all invoices for a customer
- `check_payment_status` - Check payment status
- `get_billing_history` - Get billing history for date range
- `calculate_outstanding_balance` - Calculate unpaid amounts

### Knowledge Base Server (4 tools)
- `search_solutions` - Search KB articles by keywords
- `get_article` - Get full article content by ID
- `find_related_articles` - Find related articles
- `get_common_fixes` - Get common fixes for a product/issue

### Asset Server (4 tools)
- `lookup_asset` - Find asset by ID, serial, hostname, or customer
- `check_warranty` - Check warranty status and expiration
- `get_software_licenses` - Get license information
- `get_asset_history` - Get complete asset history

## Sample Data

The servers contain realistic, interconnected sample data:

- **15 tickets** covering Windows, Linux, macOS issues (BSOD, disk space, kernel panic, etc.)
- **8 customers** with different tiers (basic, standard, premium) and SLA levels
- **15 invoices** (paid, pending, overdue) linked to customers and tickets
- **10 KB articles** with detailed technical solutions
- **12 assets** (servers, workstations, laptops) with warranty and license tracking

All data uses 2024-2025 dates and valid cross-references.

## Key Features

### OpenAI Function Calling Integration
- Automatic tool discovery from MCP servers
- Conversion of MCP tool schemas to OpenAI format
- Multi-turn conversation support
- Parallel tool calling when needed

### Error Handling
- Server startup validation
- Timeout protection
- Graceful shutdown of all processes
- OpenAI API error handling

### Extensibility
- Easy to add new MCP servers
- Modular server architecture
- Clear separation of concerns

## Customization

### Adding a New Server

1. Create `new_server.py` with MCP server implementation
2. Add to `server_configs` in `mcp_client.py`:

```python
"new_server": {
    "command": "python",
    "args": ["new_server.py"],
    "description": "Description of new server"
}
```

3. Restart the orchestrator - tools will be auto-discovered

### Modifying Sample Data

Edit the data arrays at the top of each server file:
- `TICKETS` in `ticket_server.py`
- `CUSTOMERS` in `customer_server.py`
- `INVOICES` in `billing_server.py`
- `KB_ARTICLES` in `kb_server.py`
- `ASSETS` in `asset_server.py`

## Troubleshooting

### Servers won't start
- Check Python is in PATH: `python --version`
- Verify all server files are in the same directory
- Check for port conflicts (stdio uses pipes, not ports)

### OpenAI API errors
- Verify API key is set: `echo $OPENAI_API_KEY`
- Check API key has credits
- Ensure network connectivity

### Tool calls failing
- Check server logs for errors
- Verify tool arguments match schema
- Test individual servers: `python ticket_server.py`

## License

MIT

## Credits

Built with:
- [Model Context Protocol (MCP)](https://github.com/anthropics/mcp)
- [OpenAI API](https://platform.openai.com/)
