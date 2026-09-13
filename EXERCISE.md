# Exercise: Build Your Own MCP Server

The course used five help-desk servers. Now build a sixth one, in a domain you choose, and plug it into a real host.

**Time: about 30 minutes.** Use an LLM as your coding companion for the boring parts.

## Starter variant: add one tool to an existing server (about 20 minutes)

If you are not a developer, or short on time, do this one instead. The skill it trains is the one that matters most in MCP: writing a description and an error that a model can act on.

1. Open `servers/hr_server.py` and find `get_employee` near the bottom.
2. Below it, add `list_department(department: str) -> dict`. It returns the employees of one department (name and role are enough). When no employee matches, return `make_error(...)` with a hint that lists the known departments.
3. Write the docstring for the model: one line saying what the tool does, an `Args:` section, an example value (`Engineering`).
4. Register it with the same line as its neighbour: `@mcp.tool(annotations=READ_ONLY)`.
5. Check it in Inspector: `npx @modelcontextprotocol/inspector python servers/hr_server.py`. Does the tool appear? Call it with a department that does not exist and read your own error hint. Would a model know what to do next?

An LLM can write the Python for you; the description and the error are yours.

## What you will build

A server file `servers/<your_domain>_server.py` with:

- **3 tools**: plain Python functions that answer questions someone in your domain would actually ask
- **Mock data** as a Python list or dict, 5 to 8 realistic records, no database
- **At least one structured error** built with `make_error(...)`, with `suggested_actions` and `follow_up_tools`
- **An annotation on every tool** (`READ_ONLY` or `WRITES`)

## Pick a domain

Anything you like. Some starting points:

| Domain | What it handles | Example tools |
|---|---|---|
| Recruitment | candidates, interviews, open positions | `search_candidates`, `get_interview_schedule`, `list_open_positions` |
| Project management | projects, tasks, deadlines | `list_projects`, `find_overdue_tasks`, `get_team_workload` |
| Procurement | vendors, purchase orders, contracts | `lookup_vendor`, `get_purchase_order`, `check_contract_expiry` |
| Travel and expenses | trips, expenses, approvals | `get_pending_approvals`, `summarize_trip_costs`, `lookup_expense` |

## How to start

1. **Copy the scaffold.** `servers/ticket_server.py` is the template. Copy it to `servers/<your_domain>_server.py` and keep the four-part order: data, private helpers, tools, MCP layer. Keep the two lines at the top that import from `common`.

2. **Replace the data and the tools.** Delete the ticket data and functions. Write your own with **type hints on every parameter** (`str`, `int`, `str | None = None` for optional ones) and a docstring whose first line says what the tool does and whose `Args:` section explains each parameter. The docstring is what the model reads.

3. **Ask an LLM for help.** A prompt that works:

   > I am building an MCP server for `<domain>` with the Python `mcp` 2.x SDK. Here is the template I follow: [paste `servers/ticket_server.py`]. Adapt it for `<domain>` with these three tools: [list them]. Keep the four-part structure, keep type hints and docstrings, use `make_error` for a "not found" case, and register the tools at the bottom with `mcp.tool(annotations=READ_ONLY)(function)`. Mock data: 5 to 8 realistic records.

4. **Register the tools** at the bottom, one line per tool, and give the server a name:

   ```python
   mcp = MCPServer("recruitment")
   mcp.tool(annotations=READ_ONLY)(search_candidates)
   mcp.tool(annotations=READ_ONLY)(get_interview_schedule)
   mcp.tool(annotations=WRITES)(schedule_interview)
   ```

5. **Check it imports and runs** from the repository folder:

   ```bash
   python -c "from servers.recruitment_server import search_candidates; print(search_candidates(skill='python'))"
   npx @modelcontextprotocol/inspector --cli python servers/recruitment_server.py --method tools/list
   ```

## Checklist

- The file imports with no errors and never prints to standard output
- Three tools appear in `tools/list` with the descriptions you wrote
- Every parameter has a type hint; optional ones have a default
- One tool returns a `make_error(...)` dict for an unknown ID, with `suggested_actions` and `follow_up_tools`
- Every tool carries an annotation
- Inspector can call at least one tool

The error path should look like this:

```json
{
  "error": "Candidate CAN-999 not found",
  "reason": "No candidate with that ID exists.",
  "suggested_actions": ["Call search_candidates with a skill to find existing candidates."],
  "retryable": true,
  "follow_up_tools": ["search_candidates"]
}
```

## Plug it in

- **Terminal chat:** add `"recruitment"` (the part before `_server.py`) to the `SERVERS` list in `client/interactive_client.py` and ask a question that needs your server.
- **Claude Code:** add an entry to `.mcp.json`, or run `claude mcp add recruitment -- python servers/recruitment_server.py`, then ask Claude Code about your domain. Try a question that needs your writing tool and watch the permission prompt.

## Stretch goals

- **A resource and a prompt.** Add `@mcp.resource("recruitment://job/{id}")` that returns a job description as text, and `@mcp.prompt()` `interview_plan(candidate_id: str, role: str)` that returns a structured brief. Check them with `--method resources/list` and `--method prompts/list` in Inspector, and look for them under `/mcp` in Claude Code. Sketch:

  ```python
  @mcp.resource("recruitment://job/{job_id}")
  def job_description(job_id: str) -> str:
      return JOBS[job_id]["description"]

  @mcp.prompt()
  def interview_plan(candidate_id: str, role: str) -> str:
      c = CANDIDATES[candidate_id]
      return f"Plan a 45-minute interview of {c['name']} for the {role} role. Cover: ..."
  ```

- **Cross-server link.** Reference an ID from another server (a `customer_id` from `customer_server.py`) and ask a question that makes the model use both.
- **Over HTTP.** Start your server with `--http` and connect with `Client("http://127.0.0.1:8000/mcp")`.

## Tips

- Do not over-engineer. A list of dicts is a fine database.
- Read your error payloads out loud. If they do not tell the model exactly what to try next, rewrite them.
- If a tool needs to fail on purpose, return a dict. Raising an exception hides your message from the client.
