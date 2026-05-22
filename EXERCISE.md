# Exercise: Build Your Own MCP Server

In the past 3 notebooks you've explored MCP through 5 IT support servers. Now it's your turn to build a sixth one in a fresh domain, using everything you've seen plus an LLM as your coding companion.

**Time: about 30 minutes.**

## What you'll do

Build a new MCP server with:

- **3 tools** that answer real questions someone might ask in your domain
- **Mock data** as a Python dict (no database, no external files)
- **At least one structured error payload** with `suggested_actions` and `follow_up_tools`

When you're done, you should be able to import your server in a Python shell or notebook and call any of its tools directly.

## Pick a domain

Pick whichever feels most interesting, or invent your own domain entirely. The table below is just for inspiration:

| Domain | What it handles | Example tools |
|--------|-----------------|---------------|
| **Recruitment** | candidates, interviews, open positions | `search_candidates_by_skill`, `get_interview_schedule`, `list_open_positions` |
| **Project management** | projects, tasks, deadlines | `list_projects`, `find_overdue_tasks`, `get_team_workload` |
| **Procurement** | vendors, purchase orders, contracts | `lookup_vendor`, `get_purchase_order`, `check_contract_expiry` |
| **Travel & expenses** | trips, expenses, approvals | `get_pending_approvals`, `summarize_trip_costs`, `lookup_expense` |

Both the domain and the tool names are up to you. The table is just a starting point if nothing else comes to mind.

## How to start

### 1. Copy an existing server as your scaffold

`ticket_server.py` is the simplest one to start from. Save a copy as `<your_domain>_server.py`, for example `recruitment_server.py`.

### 2. Strip out the ticket logic

Keep the imports, the `app = Server(...)` line, the `@app.list_tools()` skeleton, the `@app.call_tool()` dispatch, and the `make_error()` helper. Delete the ticket data and the ticket-specific functions.

### 3. Ask an LLM for help

Give your favorite LLM (ChatGPT, Claude, whatever you use) a prompt like:

> I'm building a `<domain>` MCP server. Here is a template I want to follow: [paste the contents of `ticket_server.py`]. Help me adapt it for `<domain>` with these 3 tools: [list your tools]. The mock data should be a Python dict with 5 to 8 realistic records.

Ask it to generate the mock data, the 3 plain Python functions, the `Tool()` definitions, and at least one structured error response for a "not found" case.

### 4. Verify it imports cleanly

```bash
python3 -c "from your_domain_server import *; print('OK')"
```

If you get an error, paste it back to the LLM and ask it to fix.

## When you're done (checklist)

- Server file imports with no errors
- At least 3 tools are registered in `list_tools()`
- Each tool has a clear name, description, and `inputSchema`
- Mock data has 5 to 8 realistic records
- One function returns a structured error with `suggested_actions` and `follow_up_tools` when given an invalid ID
- You can call at least one tool directly from a Python shell

## Quick test

In a Python shell or notebook:

```python
from your_domain_server import your_main_tool

# Happy path
print(your_main_tool(valid_argument))

# Error path
print(your_main_tool(invalid_argument))
```

The error path should return something like:

```json
{
  "error": "Candidate CAN-999 not found",
  "reason": "No candidate with that ID exists in the database.",
  "suggested_actions": [
    "Call search_candidates_by_skill to find existing candidates."
  ],
  "follow_up_tools": ["search_candidates_by_skill"],
  "retryable": true
}
```

## Stretch goals

If you finish early and want to keep going:

- **Run MCP Inspector** against your new server and call your tools from the GUI:
  ```bash
  npx @modelcontextprotocol/inspector python3 your_domain_server.py
  ```
- **Wire your server into the orchestrator** by adding it to `server_configs` in `mcp_client.py`, then ask gpt-5-nano a question that uses your new tools through `interactive_client.py`
- **Cross-domain tool** that links to an existing server, for example a recruitment tool that references `customer_id` from `customer_server.py`

## Tips

- **Don't over-engineer.** Mock data as a Python dict is fine. No SQLite, no type checking, no fancy abstractions.
- **Use the LLM for the boring parts.** Generating realistic mock data and repetitive `Tool()` definitions is exactly what it's good at. Save your thinking for the design decisions.
- **Stuck?** Open `ticket_server.py` next to your file. It is intentionally the simplest example.
- **Read your error payloads out loud.** If they don't tell the AI exactly what to try next, rewrite them.
