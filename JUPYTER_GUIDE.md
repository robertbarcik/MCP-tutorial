# Jupyter Notebook Guide

## Overview

The MCP tutorial now works seamlessly in both **regular Python** and **Jupyter notebooks/Google Colab**!

## Two Ways to Use the System

### 1. Direct Function Calls (Required for Jupyter/Colab)

All server functions are exposed as regular Python functions that can be imported and called directly:

```python
# Import and use ticket functions
from ticket_server import search_tickets, get_ticket_details

# Call directly - no async, no MCP protocol needed
tickets = search_tickets(priority="critical")
print(f"Found {tickets['total_count']} critical tickets")
```

**Benefits:**
- ✅ No async/await complexity
- ✅ Works in any Python environment including Jupyter/Colab
- ✅ Perfect for testing and debugging
- ✅ Fast and simple
- ✅ Direct access to sample data

### 2. Full MCP Orchestrator with OpenAI (Regular Python Only)

⚠️ **IMPORTANT:** The MCP orchestrator does NOT work in Jupyter/Colab due to subprocess limitations.

Use the orchestrator for natural language queries with GPT-4 in regular Python scripts:

```python
# Run this in regular Python (NOT Jupyter/Colab)
from mcp_client import MCPOrchestrator

orchestrator = MCPOrchestrator()
orchestrator.start_servers()  # Only works in regular Python
orchestrator.get_available_tools()

# Ask questions in natural language
response = orchestrator.query(
    "What are the critical tickets?",
    api_key="sk-..."
)
```

**Benefits:**
- ✅ Natural language queries
- ✅ Automatic tool selection
- ✅ Multi-server coordination
- ❌ Does NOT work in Jupyter/Colab (use interactive_client.py instead)

## How It Works

### Jupyter Limitations

**The MCP orchestrator cannot run in Jupyter/Colab** because:
- MCP servers communicate via stdio (stdin/stdout)
- Jupyter notebooks don't provide real file descriptors for stdin/stdout
- Attempting to start servers in Jupyter will raise a RuntimeError with a helpful message

The system detects Jupyter environments and prevents server startup:

```python
def _is_jupyter():
    """Detect if we're running in a Jupyter notebook"""
    try:
        from IPython import get_ipython
        if get_ipython() is not None:
            return True
    except ImportError:
        pass
    return False

async def _async_start_servers(self):
    if _is_jupyter():
        raise RuntimeError(
            "MCP orchestrator cannot start servers in Jupyter/Colab. "
            "Use direct function calls instead."
        )
```

### Direct Function Access (Works Everywhere)

All server business logic is extracted into regular Python functions that work in any environment.

Each server file has two sections:

```python
# ============================================================================
# REGULAR PYTHON FUNCTIONS - Can be called directly without MCP
# ============================================================================

def search_tickets(priority=None, status=None, ...):
    """Regular Python function - no async needed"""
    results = TICKETS.copy()
    # ... filtering logic ...
    return {"tickets": results, "total_count": len(results)}


# ============================================================================
# MCP SERVER SETUP - Wraps the above functions for MCP protocol
# ============================================================================

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    """Delegates to regular functions"""
    if name == "search_tickets":
        result = search_tickets(**arguments)
        return [TextContent(type="text", text=json.dumps(result))]
```

## Available Functions

### Ticket Server (`ticket_server.py`)
- `search_tickets(ticket_id, customer_id, status, priority, category, os, query, start_date, end_date)`
- `get_ticket_details(ticket_id)`
- `get_ticket_metrics(time_period)`
- `find_similar_tickets_to(ticket_id, limit)`

### Customer Server (`customer_server.py`)
- `lookup_customer(customer_id, email, company_name)`
- `check_customer_status(customer_id)`
- `get_sla_terms(customer_id)`
- `list_customer_contacts(customer_id)`

### Billing Server (`billing_server.py`)
- `get_invoice(invoice_id, customer_id)`
- `check_payment_status(invoice_id, customer_id)`
- `get_billing_history(customer_id, start_date, end_date)`
- `calculate_outstanding_balance(customer_id)`

### Knowledge Base Server (`kb_server.py`)
- `search_solutions(query, category, limit)`
- `get_article(article_id)`
- `find_related_articles(article_id, topic, limit)`
- `get_common_fixes(product, issue_type)`

### Asset Server (`asset_server.py`)
- `lookup_asset(asset_id, serial_number, hostname, customer_id)`
- `check_warranty(asset_id)`
- `get_software_licenses(asset_id, customer_id)`
- `get_asset_history(asset_id)`

## Quick Start in Jupyter

### Option 1: Direct Function Calls

```python
# Install requirements
!pip install -r requirements.txt

# Import and use functions
from ticket_server import search_tickets
from customer_server import lookup_customer
from billing_server import calculate_outstanding_balance

# Use them directly
tickets = search_tickets(priority="critical")
customer = lookup_customer(customer_id="CUST-001")
balance = calculate_outstanding_balance("CUST-001")
```

### Option 2: Full MCP Orchestrator (Regular Python Only)

⚠️ **This does NOT work in Jupyter/Colab!** Run from command line instead:

```bash
# In terminal (not Jupyter)
python interactive_client.py
```

Or create your own script:

```python
# my_script.py - Run with: python my_script.py (NOT in Jupyter)
import os
from mcp_client import MCPOrchestrator

os.environ['OPENAI_API_KEY'] = 'sk-...'

orch = MCPOrchestrator()
orch.start_servers()  # Only works in regular Python
orch.get_available_tools()

# Natural language query
response = orch.query(
    "What are the critical tickets and their customers?",
    os.getenv('OPENAI_API_KEY')
)
print(response)

# Clean up
orch.stop_servers()
```

## Example Notebook

See `MCP_Demo.ipynb` for a complete interactive example with:
- Direct function call examples for all 5 servers
- Works perfectly in Jupyter/Colab
- Shows all available functions and sample data

For MCP orchestrator with OpenAI GPT-4, see `interactive_client.py` (must be run in regular Python, not Jupyter).

## Troubleshooting

### "UnsupportedOperation: fileno" or subprocess errors in Jupyter

This is expected! The MCP orchestrator cannot run in Jupyter/Colab because:
- Jupyter doesn't provide real file descriptors for stdin/stdout
- MCP servers use subprocess communication via stdio

**Solution:** Use direct function calls in Jupyter, or run the orchestrator in regular Python via `interactive_client.py`.

### "Cannot import server functions"

Make sure you're in the correct directory:

```python
import os
print(os.getcwd())  # Should show mcp_tutorial directory
```

### "MCP orchestrator cannot start servers" error

This is expected in Jupyter/Colab. The system detects the Jupyter environment and prevents server startup with a helpful error message. Use direct function calls instead.

## Google Colab

Direct function calls work perfectly in Colab!

1. Upload all files to Colab or clone the repo
2. Install requirements: `!pip install -r requirements.txt`
3. Use direct function calls (orchestrator will NOT work)

```python
# In Colab
!git clone <your-repo>
%cd mcp_tutorial
!pip install -r requirements.txt

# Use direct function calls
from ticket_server import search_tickets
tickets = search_tickets(priority="critical")
```

## Performance Notes

**Direct Function Calls:**
- Instant (no server startup)
- No network overhead
- Perfect for data exploration

**MCP Orchestrator** (regular Python only):
- ~2-3 seconds startup (launches 5 servers)
- OpenAI API latency (1-5 seconds per query)
- Best for natural language queries
- Must be run from command line, not Jupyter

## Best Practices

1. **For Data Exploration**: Use direct function calls
   ```python
   from ticket_server import TICKETS, search_tickets
   # Quick access to raw data and functions
   ```

2. **For AI Integration**: Use the orchestrator in regular Python (not Jupyter)
   ```bash
   python interactive_client.py
   ```

3. **For Testing**: Direct functions are much faster
   ```python
   def test_search():
       result = search_tickets(priority="high")
       assert result['total_count'] > 0
   ```

4. **Clean Up**: Always stop servers when done (regular Python only)
   ```python
   orchestrator.stop_servers()  # Only needed if you used orchestrator
   ```

## What Changed

1. **mcp_client.py**:
   - Added Jupyter detection (`_is_jupyter()`)
   - Prevents server startup in Jupyter with helpful error message
   - Directs users to use direct function calls instead

2. **All Server Files** (ticket, customer, billing, kb, asset):
   - Exposed regular Python functions that can be called directly
   - MCP handlers delegate to these functions
   - Functions can be imported and used in any Python environment

3. **ticket_server.py**:
   - Added missing helper functions (`calculate_metrics`, `matches_text_search`, etc.)
   - Fixed NameError bugs

4. **New Files**:
   - `MCP_Demo.ipynb` - Interactive Jupyter demo (direct functions only)
   - `JUPYTER_GUIDE.md` - This guide
