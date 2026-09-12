# MCP Course: One Server, Any Agent

A hands-on course on the **Model Context Protocol (MCP)**: how to expose your own Python functions to any AI application, how to be the client yourself, what travels on the wire, and how to plug a server into Claude Code, Claude Desktop or an agent framework.

The course is one notebook, **`MCP_course.ipynb`**, read top to bottom. This README is the textbook version of it: the same material, written to be re-read later.

**Open in Colab:** [MCP_course.ipynb](https://colab.research.google.com/github/robertbarcik/MCP-tutorial/blob/main/MCP_course.ipynb). The first cells install the packages and clone this repository into the Colab session; you need an OpenAI API key (Colab secret `OPENAI_API_KEY`).

Built and verified in September 2026 on `mcp==2.2.0` (MCP specification 2026-07-28), `openai==3.13.0` and the model `gpt-5.6-luna`.

---

## Contents

1. [What MCP is, in two sentences](#what-mcp-is-in-two-sentences)
2. [When to use MCP, and when a CLI is enough](#when-to-use-mcp-and-when-a-cli-is-enough)
3. [Quick start](#quick-start)
4. [Repository layout](#repository-layout)
5. [The story: an IT help desk with five servers](#the-story-an-it-help-desk-with-five-servers)
6. [Anatomy of a server](#anatomy-of-a-server)
7. [Errors are written for the model](#errors-are-written-for-the-model)
8. [Tool annotations](#tool-annotations)
9. [Being the client](#being-the-client)
10. [What goes over the wire](#what-goes-over-the-wire)
11. [MCP Inspector](#mcp-inspector)
12. [Letting a model drive the server](#letting-a-model-drive-the-server)
13. [Plugging into hosts](#plugging-into-hosts)
14. [Resources and prompts](#resources-and-prompts)
15. [Beyond your laptop: transports, authentication, trust](#beyond-your-laptop-transports-authentication-trust)
16. [Example questions](#example-questions)
17. [Troubleshooting](#troubleshooting)
18. [What changed since the 2025 version of this course](#what-changed-since-the-2025-version-of-this-course)
19. [Exercise and further reading](#exercise-and-further-reading)

---

## What MCP is, in two sentences

MCP is an agreed way for a program that owns data or functions (a **server**) to describe them and serve them to any AI application (a **client**). The client asks two questions, *what tools do you have?* and *run this one for me*, and everything else is built on top of those two.

A **server** waits to be asked; it does nothing on its own. A **client** is the program that asks: Claude Code, Claude Desktop, an agent framework, or a script you write. The words say nothing about where the programs run.

## When to use MCP, and when a CLI is enough

If you control both sides and the consumer is a coding agent on your own machine, a command-line tool with good documentation usually beats an MCP server. The agent reads the help text, runs the command, reads the output. A server adds a layer and takes nothing away.

Use MCP when at least one of these holds:

- **You do not control the client.** Colleagues on Claude.ai, ChatGPT or Copilot cannot run your script; they can connect to your server.
- **The user should not have a shell.** A company wants its ticket system reachable by agents, but only through a handful of vetted functions, behind a login, with every call logged.
- **Many people share one server.** It runs centrally; nobody installs anything.

Rule of thumb: MCP is for the boundary between you and someone else's agent.

## Quick start

Local machine (Python 3.10 or newer; tested on 3.12):

```bash
git clone https://github.com/robertbarcik/MCP-tutorial
cd MCP-tutorial
python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export OPENAI_API_KEY="sk-..."       # Windows: set OPENAI_API_KEY=sk-...

jupyter lab MCP_course.ipynb         # the course
python client/interactive_client.py  # chat with all five servers in the terminal
```

Google Colab: open the badge at the top; the notebook installs and clones everything itself.

The ADK course (the follow-up) pins an older MCP client library (`mcp<2`). Keep the two courses in two virtual environments; a 2.x server such as the ones here works fine with that older client.

## Repository layout

```
MCP-tutorial/
├── MCP_course.ipynb          the course, executed with outputs
├── README.md                 this textbook
├── EXERCISE.md               build a sixth server, plug it into Claude Code
├── requirements.txt          mcp==2.2.0, openai==3.13.0
├── .mcp.json                 Claude Code registration of the servers (project scope)
├── images/                   Inspector screenshot used by the notebook
├── servers/
│   ├── common.py             make_error(), relative dates, READ_ONLY / WRITES annotations
│   ├── ticket_server.py      5 tools (one of them writes)
│   ├── customer_server.py    4 tools
│   ├── billing_server.py     4 tools
│   ├── kb_server.py          4 tools
│   ├── asset_server.py       4 tools
│   └── hr_server.py          2 resources, 1 prompt, 1 tool (the resources/prompts demo)
└── client/
    ├── agent_loop.py         the tool-calling loop over MCP servers (Responses API)
    └── interactive_client.py terminal chat over the five help-desk servers
```

## The story: an IT help desk with five servers

Every example in the course uses one company: an IT support desk with five systems, each behind its own small MCP server. The data is in-memory Python (lists of dicts) with dates computed relative to today, so time windows, overdue invoices and warranties stay meaningful whenever you run it.

| Server | Tools | Data |
|---|---|---|
| `tickets` | `search_tickets`, `get_ticket_details`, `get_ticket_metrics`, `find_similar_tickets`, `update_ticket_status` | 15 tickets (Windows, Linux, macOS) |
| `customers` | `lookup_customer`, `check_customer_status`, `get_sla_terms`, `list_customer_contacts` | 8 customers, three support tiers |
| `billing` | `get_invoice`, `check_payment_status`, `get_billing_history`, `calculate_outstanding_balance` | 15 invoices linked to customers and tickets |
| `knowledge-base` | `search_solutions`, `get_article`, `find_related_articles`, `get_common_fixes` | 10 troubleshooting articles |
| `assets` | `lookup_asset`, `check_warranty`, `get_software_licenses`, `get_asset_history` | 12 assets with warranties and licenses |
| `hr` | `get_employee`, plus resources `hr://policy/{name}`, `hr://policy-index` and the prompt `performance_review` | 3 policies, 3 employees |

Twenty-one tools across the five help-desk servers. Tickets link to customers, invoices to tickets, assets to customers, so cross-server questions have real answers.

## Anatomy of a server

Every server file has four parts, in this order. Only the last one knows MCP exists.

```python
# 1. DATA: the "database" is a list of dicts
TICKETS = [ {...}, {...} ]

# 2. PRIVATE HELPERS: underscore = not a tool
def _matches_text(ticket, query): ...

# 3. TOOLS: plain Python functions, importable and testable without MCP
def get_ticket_details(ticket_id: str) -> dict:
    """Get the full record of one ticket by its ID.

    Args:
        ticket_id: unique ticket identifier (e.g. TKT-1001)
    """
    ...

# 4. MCP LAYER: the only part of this file that knows MCP exists
mcp = MCPServer("tickets")
mcp.tool(annotations=READ_ONLY)(search_tickets)
mcp.tool(annotations=READ_ONLY)(get_ticket_details)
mcp.tool(annotations=WRITES)(update_ticket_status)

if __name__ == "__main__":
    if "--http" in sys.argv:
        mcp.run(transport="streamable-http", host="127.0.0.1", port=8000)
    else:
        mcp.run()                     # stdio: the host starts us
```

What the three key lines do:

- `MCPServer("tickets")` creates the server and gives it a name.
- `mcp.tool(annotations=...)(function)` hands an ordinary function to the server. The tool's name is the function name, its description is the docstring, its argument schema is generated from the type hints. Every parameter needs a type hint; optional ones look like `status: str | None = None`. You never write a JSON schema by hand.
- `mcp.run()` waits for a client over stdio. With `--http` the same file becomes a web service (see [Beyond your laptop](#beyond-your-laptop-transports-authentication-trust)).

The registration form `mcp.tool(...)(function)` at the bottom keeps part 3 free of MCP. The decorator form, `@mcp.tool()` above the function, does the same thing; `servers/hr_server.py` uses it so you see both spellings.

Two rules that bite when forgotten:

- **Never `print()` inside a server.** On stdio, standard output *is* the connection to the client; a stray print corrupts it. Log to standard error if you must.
- **A tool function returns a dict, a string, or raises.** Dicts and strings reach the client as text. Exceptions become a generic "Error executing tool" and your message is lost, which is the point of the next section.

## Errors are written for the model

The one design decision worth copying from this repository: expected failures come back as data the model can act on, not as exceptions.

```python
def make_error(message, *, reason=None, hints=None, retryable=False, follow_up_tools=None, **extra):
    payload = {"error": message}
    if reason:          payload["reason"] = reason
    if hints:           payload["suggested_actions"] = hints
    payload["retryable"] = retryable
    if follow_up_tools: payload["follow_up_tools"] = follow_up_tools
    ...
```

A missing ticket produces:

```json
{
  "error": "Ticket TKT-9999 not found",
  "reason": "The ticket_id did not match any tickets in the dataset.",
  "suggested_actions": [
    "Call search_tickets with a query, customer_id or priority filter to rediscover the ticket.",
    "Verify the ticket_id format (e.g., TKT-1001)."
  ],
  "retryable": true,
  "follow_up_tools": ["search_tickets"],
  "ticket_id": "TKT-9999"
}
```

In the notebook the model asks for "ticket TKT-9999, the BitLocker one", gets this payload, calls `search_tickets(query="BitLocker")`, finds TKT-1009 and answers. The loop has no error handling at all; the recovery happens because the error told the model what to do next.

The rule: **exceptions for bugs, dicts for expected failures.** An empty search result is not an error either; `search_solutions` returns `total_count: 0` and the model tries another keyword.

## Tool annotations

A host such as Claude Code must decide which tools it may run without asking the user. The server can say so with annotations attached to each tool:

| Hint | Meaning |
|---|---|
| `read_only_hint` | the tool only reads |
| `destructive_hint` | the tool may delete or overwrite |
| `idempotent_hint` | calling it twice is the same as once |
| `open_world_hint` | it reaches outside its own data (the internet, other systems) |

`servers/common.py` defines two presets, `READ_ONLY` and `WRITES`. Four ticket tools are read-only; `update_ticket_status` is marked as writing, and Claude Code asks before running it. Annotations are hints: a host may ignore them and a server can lie. They help honest hosts and honest servers cooperate; they are not a security boundary.

## Being the client

The Python SDK's client, in a notebook or a script:

```python
import sys
from mcp import Client, StdioServerParameters

TICKET_SERVER = StdioServerParameters(command=sys.executable, args=["servers/ticket_server.py"])

async with Client(TICKET_SERVER) as tickets:
    listed = await tickets.list_tools()
    for tool in listed.tools:
        print(tool.name, tool.description.strip().splitlines()[0], tool.input_schema)
    result = await tickets.call_tool("search_tickets", {"priority": "critical"})
    print(result.content[0].text)          # the server's dict, as JSON text
```

Read the `Client(...)` line inside out: which program to start (this Python, running the server file), how to talk to it (the program's standard input and output, which is what **stdio** means), and who handles it (`Client`, which starts the program, talks, and stops it when the `with` block ends). `await` means "wait for the other program to answer".

Other ways to connect, same client:

- `Client("http://127.0.0.1:8000/mcp")` connects to a server running as a web service.
- `Client(server_object)` connects to an `MCPServer` instance in the same process, no subprocess. Handy for tests and for the raise-versus-return demo in the notebook.

In Jupyter and Colab, use plain top-level `await` in cells. Do not apply `nest_asyncio`; it hangs the 2.x client. Colab needs one line of plumbing before the first subprocess: if `sys.stderr.fileno()` raises, replace `sys.stderr` with `open(os.devnull, "w")`.

## What goes over the wire

MCP speaks **JSON-RPC 2.0**: one JSON object per line; a request has an `id` and a `method`, the answer carries the same `id` and a `result`. Under the 2026-07-28 specification a session with one tool call is three exchanges:

```
--> server/discover   {"_meta": {"io.modelcontextprotocol/protocolVersion": "2026-07-28",
                                 "io.modelcontextprotocol/clientInfo": {...}, ...}}
<-- result            {"supportedVersions": ["2026-07-28"], "capabilities": {...}, "resultType": "complete"}
--> tools/list        {"_meta": {...}}
<-- result            {"tools": [{"name": "search_tickets", "description": "...", "inputSchema": {...}}, ...]}
--> tools/call        {"name": "get_ticket_details", "arguments": {"ticket_id": "TKT-1001"}, "_meta": {...}}
<-- result            {"content": [{"type": "text", "text": "{ ...the dict as JSON... }"}], "isError": false}
```

Every request carries the protocol version and the client's identity in `_meta`; every result carries `resultType`. The notebook captures these messages with a wiretap: the server is started through `sh -c "tee in.log | python servers/ticket_server.py | tee out.log"`, so both directions land in files.

Backwards compatibility: clients and servers written before mid-2026 open with an `initialize` request instead of `server/discover`. A 2.x client sends `discover` first; an old server answers with an error and the client falls back to `initialize`. A 2.x server answers both. That is how the ADK course's older client talks to these servers.

## MCP Inspector

The standard debugging client from the MCP project. Needs Node.js 22.19 or newer.

```bash
npx @modelcontextprotocol/inspector python servers/ticket_server.py                          # web UI
npx @modelcontextprotocol/inspector --cli python servers/ticket_server.py --method tools/list  # terminal only
npx @modelcontextprotocol/inspector --cli python servers/ticket_server.py --method tools/call \
    --tool-name get_ticket_details --tool-arg ticket_id=TKT-9999
```

In the web UI: Connect, Tools, pick a tool, run it. The History tab shows the JSON-RPC messages. A program you did not write listing and calling your tools is the whole point of a protocol.

## Letting a model drive the server

The tool-calling loop from the previous course, with two lines changed: the tool list comes from `list_tools`, and running a tool goes through `call_tool`. The OpenAI Responses API wants tools as `{"type": "function", "name", "description", "parameters"}`; the server's `input_schema` passes through untouched.

```python
def to_openai_tool(tool):
    return {"type": "function", "name": tool.name, "description": tool.description or "", "parameters": tool.input_schema}

async def run_with_mcp(question, mcp_client, max_rounds=6):
    tools = [to_openai_tool(t) for t in (await mcp_client.list_tools()).tools]
    conversation = [{"role": "developer", "content": "You are an IT help-desk assistant. Use the tools; never invent data."},
                    {"role": "user", "content": question}]
    for _ in range(max_rounds):
        response = llm.responses.create(model=MODEL, input=conversation, tools=tools)
        conversation += response.output
        calls = [item for item in response.output if item.type == "function_call"]
        if not calls:
            return response.output_text
        for call in calls:
            result = await mcp_client.call_tool(call.name, json.loads(call.arguments))
            conversation.append({"type": "function_call_output", "call_id": call.call_id, "output": result.content[0].text})
```

`client/agent_loop.py` is the reusable version: a `Toolbox` that collects tools from several clients and remembers which client owns which tool name, and `run_with_tools` for a running conversation. `client/interactive_client.py` opens the five servers at once with an `AsyncExitStack` (one `with` block that keeps five `with` blocks open) and drops you into a chat.

The current small model, `gpt-5.6-luna`, does tool calls on the Responses API. On the older Chat Completions API it refuses function tools unless reasoning is switched off, which is one reason the course moved to Responses.

## Plugging into hosts

You rarely write the client. Hosts speak MCP already, so connecting a server is configuration.

**Claude Code** (from the repository folder, virtual environment active):

```bash
claude mcp add tickets -- python servers/ticket_server.py
claude mcp list
claude                    # ask: which tickets are critical?  then: close ticket TKT-1004
claude mcp remove tickets
```

The second question triggers a permission prompt: the host saw the `WRITES` annotation. `/mcp` inside a session lists connected servers, their tools, prompts and resources.

This repository ships a **`.mcp.json`** that Claude Code reads when you open the folder (project scope; it asks once whether to trust it):

```json
{
  "mcpServers": {
    "tickets":        {"command": "python", "args": ["servers/ticket_server.py"]},
    "customers":      {"command": "python", "args": ["servers/customer_server.py"]},
    "billing":        {"command": "python", "args": ["servers/billing_server.py"]},
    "knowledge-base": {"command": "python", "args": ["servers/kb_server.py"]},
    "assets":         {"command": "python", "args": ["servers/asset_server.py"]},
    "hr":             {"command": "python", "args": ["servers/hr_server.py"]}
  }
}
```

**Claude Desktop** uses `claude_desktop_config.json` (Settings, Developer, Edit Config) with the same `mcpServers` key. It does not run from your folder, so give absolute paths for both the Python interpreter (the one in your virtual environment) and the server file. **VS Code** uses `.vscode/mcp.json` with the key `servers`; **Cursor** uses `mcpServers`.

**Agent frameworks**: in the ADK course the same server becomes an agent's tool:

```python
McpToolset(connection_params=StdioConnectionParams(
    server_params=StdioServerParameters(command=sys.executable, args=["servers/ticket_server.py"])))
```

Which program, how to talk to it, who handles it: the same three answers as `Client(...)`.

## Resources and prompts

Not everything an assistant needs is a question for the model. Two more things a server can publish:

- A **resource** is a document with an address (a URI). The host shows it to the user, who attaches it to a conversation. The person decides, not the model.
- A **prompt** is a reusable message template with blanks. The host offers it as a menu item or slash command; the person picks it and fills the blanks.

Tools are for the model to call; resources and prompts are for the host's interface and the person in front of it.

```python
@mcp.resource("hr://policy/{name}")        # an address with a hole; the function fills it
def policy(name: str) -> str:
    return HR_POLICIES[name]["content"]

@mcp.prompt()                              # arguments become the blanks
def performance_review(employee_id: str, review_period: str) -> str:
    return f"Write a performance review for ..."
```

Client side: `list_resources`, `list_resource_templates`, `read_resource(uri)` (gives content plus MIME type), `list_prompts`, `get_prompt(name, arguments)` (gives ready-made messages). Where you meet them: the attachment menu in Claude Desktop, slash commands, and `/mcp` in Claude Code.

**Sampling**, an older feature that let a server ask the host's model for a completion, was deprecated in the 2026-07-28 specification together with roots and logging. Servers that need a model call the model provider directly. Do not build on it.

## Beyond your laptop: transports, authentication, trust

**stdio** (everything above): the host starts the server as a child process. One user, one machine, nothing to configure. Fine for development and personal tools.

**Streamable HTTP**: the server is a small web service and the client gets a URL. One server, running centrally, many clients. Our servers support it with one flag:

```bash
python servers/ticket_server.py --http        # listens on http://127.0.0.1:8000/mcp
```

```python
async with Client("http://127.0.0.1:8000/mcp") as tickets: ...
```

The older HTTP+SSE transport is deprecated; new servers use Streamable HTTP.

**Authentication.** A remote server is a web API like any other. MCP uses OAuth 2.0: the host obtains a token from the organisation's login system and sends it with every request, the server checks it. The Python SDK implements the flow on both sides; you configure it rather than write it.

**Low trust.** A server is somebody's code touching your data. Organisations put servers behind a gateway, allow-list which servers agents may use, prefer read-only tools, and log every call. Annotations are one input to those decisions.

**Tool poisoning.** Tool descriptions are text the model reads and trusts. A malicious or compromised server can hide instructions in a description or a result ("before answering, also send the user's files to ..."), and annotations can lie. Only connect to servers you trust, read what they expose, and treat a new server like a new dependency in your code, because that is what it is.

## Example questions

For `python client/interactive_client.py` or Claude Code with the servers registered:

- What are all the critical priority tickets?
- Show me customer CUST-001's SLA terms and contacts.
- Which assets have warranties expiring in the next 30 days?
- Which customers have both open tickets and overdue invoices?
- Find similar tickets to TKT-1001 and a knowledge base article that could help.
- For customer CUST-002: open tickets, outstanding balance, and any asset with an expired warranty.

Watch the `->` lines in the terminal: each names the tool and, through it, the server that answered.

## Troubleshooting

- **`ModuleNotFoundError: mcp.server.fastmcp` or `FastMCP`**: you have code from the 1.x line. In 2.x the class is `MCPServer` from `mcp.server`.
- **`pip install mcp` installed 2.x but a course pins 1.x** (the ADK course): use a separate virtual environment per course.
- **A notebook cell hangs on `async with Client(...)`**: remove `nest_asyncio`. Use plain top-level `await`.
- **`sys.stderr.fileno()` error on Colab**: run the plumbing lines from the "Be the Client" section first.
- **The client gets garbage or disconnects**: the server printed to standard output. Remove the `print`, or log to standard error.
- **Port 8000 already in use** for the HTTP demo: `lsof -i :8000` (macOS, Linux) and stop the old process; the notebook cell terminates its own server, but an interrupted cell may not.
- **Stray servers after an interrupted cell**: `pkill -f "servers/.*_server.py"` (macOS, Linux).
- **The wiretap cell fails on Windows**: it needs `sh` and `tee`. Run that cell in Colab, or inside Git Bash / WSL.
- **Inspector fails to start**: check `node --version` (needs 22.19 or newer).
- **The model gives up on TKT-9999 instead of searching**: models are not deterministic; run the cell again.
- **`Function tools with reasoning_effort are not supported ... in /v1/chat/completions`**: the current models do tool calls on the Responses API. Use `client.responses.create`, as this course does.

## What changed since the 2025 version of this course

- Three notebooks became one. The local-model notebook (Gemma 2 with a hand-parsed tool loop) is gone; the previous course teaches the loop, and this one puts MCP under it.
- `mcp` 1.x to **2.x**: `FastMCP` is now `MCPServer`; the low-level `Server` with `@app.list_tools()` and hand-written schemas is replaced by functions with type hints; `ClientSession` plus `stdio_client` became one `Client`; field names are snake_case (`input_schema`, `read_only_hint`).
- Specification **2026-07-28**: no `initialize` handshake, `server/discover` and per-request `_meta` instead; sampling, roots and logging deprecated; SSE transport deprecated in favour of Streamable HTTP.
- `gpt-5-nano` (retiring in December 2026) became `gpt-5.6-luna`, and the loop moved from Chat Completions to the Responses API.
- The hand-rolled `MCPOrchestrator` became a 60-line `agent_loop.py`; the model-driven demos now run inside the notebook instead of only in a terminal.
- The servers moved to `servers/`, the error helper is shared in `servers/common.py`, and all mock dates are relative to today.

## Exercise and further reading

- **Exercise:** [EXERCISE.md](EXERCISE.md): build a sixth server and plug it into Claude Code (about 30 minutes).
- MCP specification and documentation: https://modelcontextprotocol.io
- Python SDK: https://github.com/modelcontextprotocol/python-sdk (migration guide for 1.x code: https://py.sdk.modelcontextprotocol.io/migration/)
- MCP Inspector: https://github.com/modelcontextprotocol/inspector
- Claude Code and MCP: https://code.claude.com/docs/en/mcp
- OpenAI Responses API, function calling: https://developers.openai.com/api/docs/guides/function-calling

## License

MIT
