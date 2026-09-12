"""
The tool-calling loop, with MCP servers as the source of tools.

It is the same loop you wrote in the previous course (ask the model, run the
function it asks for, hand the result back, repeat), with two changes:

  1. The tool list comes from the servers:   await client.list_tools()
  2. Running a tool goes through the server:  await client.call_tool(name, args)

The model never sees Python. It sees tool names, descriptions and schemas, and
it gets back the text the server returned.

Used by the course notebook and by client/interactive_client.py.
"""

import json

MODEL = "gpt-5.6-luna"

DEVELOPER_PROMPT = (
    "You are an IT help-desk assistant. Use the tools to look things up; never invent "
    "ticket, customer, invoice, article or asset data. When a tool returns an error with "
    "suggested_actions, follow them. Answer briefly."
)


def to_openai_tool(tool):
    """Translate one MCP tool description into the shape the OpenAI Responses API expects."""
    return {
        "type": "function",
        "name": tool.name,
        "description": tool.description or "",
        "parameters": tool.input_schema,   # the JSON schema the server generated; passed through untouched
    }


class Toolbox:
    """Tools from one or several MCP clients, looked up by tool name."""

    def __init__(self):
        self.tools = []        # OpenAI-format tool descriptions, all servers together
        self._owner = {}       # tool name -> the MCP client that serves it
        self.calls = []        # every (name, args) the model asked for; handy for tests

    async def add(self, mcp_client) -> int:
        """Register every tool of one connected MCP client. Returns how many were added."""
        listed = await mcp_client.list_tools()
        for tool in listed.tools:
            self.tools.append(to_openai_tool(tool))
            self._owner[tool.name] = mcp_client
        return len(listed.tools)

    async def call(self, name: str, args: dict) -> str:
        """Run one tool on whichever server owns it; return the text the server sent back."""
        self.calls.append((name, args))
        if name not in self._owner:
            return json.dumps({"error": f"Unknown tool {name}", "known_tools": list(self._owner)})
        result = await self._owner[name].call_tool(name, args)
        return "".join(part.text for part in result.content if getattr(part, "text", None))


async def run_with_tools(llm, toolbox: Toolbox, question: str, conversation: list | None = None,
                         model: str = MODEL, max_rounds: int = 8, verbose: bool = True) -> str:
    """
    Ask the model a question and let it call MCP tools until it answers in text.

    `conversation` is the running list of messages; pass the same list again to
    continue a chat, or leave it None for a fresh one.
    """
    if conversation is None:
        conversation = [{"role": "developer", "content": DEVELOPER_PROMPT}]
    conversation.append({"role": "user", "content": question})

    for round_number in range(1, max_rounds + 1):
        # llm.responses.create is a normal (blocking) call; fine for a course, one question at a time.
        response = llm.responses.create(model=model, input=conversation, tools=toolbox.tools)
        conversation += response.output
        calls = [item for item in response.output if item.type == "function_call"]
        if not calls:                                   # no tool call: the model answered in text
            return response.output_text
        if verbose:
            print(f"round {round_number}: the model asked for {len(calls)} call(s)")
        for call in calls:
            args = json.loads(call.arguments)
            output = await toolbox.call(call.name, args)
            if verbose:
                shown = {k: v for k, v in args.items() if v not in (None, "")}   # the model sends every optional argument, most as null
                print(f"  -> {call.name}({shown}) -> {output[:120].replace(chr(10), ' ')}")
            conversation.append({"type": "function_call_output", "call_id": call.call_id, "output": output})
    return "Stopped after too many rounds."
