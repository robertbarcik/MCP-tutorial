"""
Terminal chat over all five help-desk servers.

Starts each server as a subprocess (stdio), collects their tools into one
toolbox, and lets the model answer your questions with them.

    export OPENAI_API_KEY="sk-..."
    python client/interactive_client.py

Type "exit" to quit.
"""

import asyncio
import logging
import os
import sys
from contextlib import AsyncExitStack
from getpass import getpass
from pathlib import Path

from mcp import Client, StdioServerParameters
from openai import OpenAI

sys.path.insert(0, str(Path(__file__).parent))
from agent_loop import DEVELOPER_PROMPT, MODEL, Toolbox, run_with_tools

ROOT = Path(__file__).resolve().parent.parent
SERVERS = ["ticket", "customer", "billing", "kb", "asset"]

EXAMPLES = [
    "What are all the critical priority tickets?",
    "Show me customer CUST-001's SLA terms and contacts.",
    "Which assets have warranties expiring in the next 30 days?",
    "Which customers have both open tickets and overdue invoices?",
    "Find similar tickets to TKT-1001 and a knowledge base article that could help.",
]


async def main():
    logging.getLogger("httpx").setLevel(logging.WARNING)   # the OpenAI client logs every request otherwise
    api_key = os.environ.get("OPENAI_API_KEY") or getpass("OpenAI API key: ")
    llm = OpenAI(api_key=api_key)

    print(f"Starting {len(SERVERS)} MCP servers ...")
    async with AsyncExitStack() as stack:         # one with-block that keeps five with-blocks open
        toolbox = Toolbox()
        for name in SERVERS:
            params = StdioServerParameters(command=sys.executable, args=[str(ROOT / "servers" / f"{name}_server.py")])
            client = await stack.enter_async_context(Client(params))
            count = await toolbox.add(client)
            print(f"  ok  {client.server_info.name:15s} {count} tools")
        print(f"\n{len(toolbox.tools)} tools available. Model: {MODEL}. Try for example:")
        for example in EXAMPLES:
            print(f"  - {example}")
        print("Type 'exit' to quit.\n")

        conversation = [{"role": "developer", "content": DEVELOPER_PROMPT}]
        while True:
            try:
                question = (await asyncio.to_thread(input, "You: ")).strip()
            except EOFError:
                break
            if question.lower() in {"exit", "quit", "q"}:
                break
            if not question:
                continue
            answer = await run_with_tools(llm, toolbox, question, conversation)
            print(f"\nAssistant: {answer}\n")
    print("Servers stopped. Bye.")


if __name__ == "__main__":
    asyncio.run(main())
