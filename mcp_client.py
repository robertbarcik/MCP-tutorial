"""
MCP Orchestrator Client
Coordinates multiple MCP servers and integrates with OpenAI's gpt-5-nano for function calling
Works seamlessly in both regular Python and Jupyter notebooks
"""

import asyncio
import json
import sys
from typing import List, Dict, Any, Optional
from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# Jupyter/IPython detection and event loop handling
def _is_jupyter():
    """Detect if we're running in a Jupyter notebook"""
    try:
        from IPython import get_ipython
        if get_ipython() is not None:
            return True
    except ImportError:
        pass
    return False


def _ensure_event_loop():
    """Ensure we have an event loop, handling Jupyter vs regular Python"""
    try:
        loop = asyncio.get_running_loop()
        # We're in Jupyter with a running loop
        return loop, True
    except RuntimeError:
        # No running loop, we're in regular Python
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            return loop, False
        except:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop, False


def _run_async(coro):
    """
    Run an async coroutine, handling both Jupyter and regular Python environments
    """
    loop, is_running = _ensure_event_loop()

    if is_running:
        # In Jupyter, use nest_asyncio to allow nested event loops
        try:
            import nest_asyncio
            nest_asyncio.apply()
        except ImportError:
            print("⚠️  Installing nest_asyncio for Jupyter compatibility...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "nest_asyncio"])
            import nest_asyncio
            nest_asyncio.apply()

        # Now we can use asyncio.run even in Jupyter
        return asyncio.run(coro)
    else:
        # Regular Python environment
        return loop.run_until_complete(coro)


def _make_error_payload(message: str, *, reason: Optional[str] = None, hints: Optional[List[str]] = None,
                        retryable: bool = False, follow_up_tools: Optional[List[str]] = None,
                        context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create a structured error payload suitable for JSON serialization."""
    payload: Dict[str, Any] = {"error": message, "retryable": retryable}
    if reason:
        payload["reason"] = reason
    if hints:
        payload["suggested_actions"] = hints
    if follow_up_tools:
        payload["follow_up_tools"] = follow_up_tools
    if context:
        payload["context"] = context
    return payload


def _make_error_json(*, message: str, reason: Optional[str] = None, hints: Optional[List[str]] = None,
                     retryable: bool = False, follow_up_tools: Optional[List[str]] = None,
                     context: Optional[Dict[str, Any]] = None) -> str:
    """Serialize a structured error payload as JSON for OpenAI tool responses."""
    payload = _make_error_payload(
        message,
        reason=reason,
        hints=hints,
        retryable=retryable,
        follow_up_tools=follow_up_tools,
        context=context
    )
    return json.dumps(payload)


class MCPOrchestrator:
    """
    Orchestrates multiple MCP servers and provides OpenAI gpt-5-nano integration
    with function calling capabilities.

    Works seamlessly in both Jupyter notebooks and regular Python scripts.
    """

    def __init__(self):
        """Initialize the orchestrator"""
        self.server_processes = {}
        self.server_sessions = {}
        self.available_tools = []
        self.tool_to_server_map = {}
        self._initialized = False

        # Define server configurations
        self.server_configs = {
            "ticket": {
                "command": "python3" if sys.platform != "win32" else "python",
                "args": ["ticket_server.py"],
                "description": "Ticket management server"
            },
            "customer": {
                "command": "python3" if sys.platform != "win32" else "python",
                "args": ["customer_server.py"],
                "description": "Customer database server"
            },
            "billing": {
                "command": "python3" if sys.platform != "win32" else "python",
                "args": ["billing_server.py"],
                "description": "Billing server"
            },
            "kb": {
                "command": "python3" if sys.platform != "win32" else "python",
                "args": ["kb_server.py"],
                "description": "Knowledge base server"
            },
            "asset": {
                "command": "python3" if sys.platform != "win32" else "python",
                "args": ["asset_server.py"],
                "description": "Asset management server"
            }
        }

    def start_servers(self):
        """
        Start all MCP server processes and establish connections.

        Works in both Jupyter notebooks and regular Python.
        Each server runs as a separate subprocess using stdio transport.
        """
        return _run_async(self._async_start_servers())

    async def _async_start_servers(self):
        """Internal async implementation of start_servers"""
        # Check if we're in Jupyter/Colab
        if _is_jupyter():
            print("⚠️  WARNING: MCP orchestrator with subprocesses doesn't work in Jupyter/Colab")
            print("    Jupyter notebooks don't support stdin/stdout file descriptors for subprocesses.")
            print()
            print("    💡 SOLUTION: Use direct function calls instead!")
            print("    Example:")
            print("        from ticket_server import search_tickets")
            print("        tickets = search_tickets(priority='critical')")
            print()
            print("    See JUPYTER_GUIDE.md for more information.")
            print()
            raise RuntimeError(
                "MCP orchestrator cannot start servers in Jupyter/Colab. "
                "Use direct function calls instead. See JUPYTER_GUIDE.md for details."
            )

        print("Starting MCP servers...")

        for server_name, config in self.server_configs.items():
            try:
                print(f"  - Starting {server_name} server ({config['description']})...")

                # Create server parameters for stdio transport
                server_params = StdioServerParameters(
                    command=config["command"],
                    args=config["args"],
                    env=None
                )

                # Create stdio client connection
                stdio_transport = stdio_client(server_params)
                stdio, write = await stdio_transport.__aenter__()

                # Create and initialize client session
                session = ClientSession(stdio, write)
                await session.__aenter__()

                # Initialize the session
                await session.initialize()

                # Store the session
                self.server_sessions[server_name] = {
                    "session": session,
                    "transport": stdio_transport
                }

                print(f"    ✓ {server_name} server started successfully")

                # Small delay to ensure server is ready
                await asyncio.sleep(0.5)

            except Exception as e:
                print(f"    ✗ Failed to start {server_name} server: {e}")
                raise

        self._initialized = True
        print("All servers started successfully!\n")

    def stop_servers(self):
        """
        Stop all running MCP server processes and close connections.

        Works in both Jupyter notebooks and regular Python.
        """
        return _run_async(self._async_stop_servers())

    async def _async_stop_servers(self):
        """Internal async implementation of stop_servers"""
        print("Stopping MCP servers...")

        for server_name, server_info in self.server_sessions.items():
            try:
                print(f"  - Stopping {server_name} server...")

                # Close the session
                session = server_info["session"]
                await session.__aexit__(None, None, None)

                # Close the transport
                transport = server_info["transport"]
                await transport.__aexit__(None, None, None)

                print(f"    ✓ {server_name} server stopped")

            except Exception as e:
                print(f"    ✗ Error stopping {server_name} server: {e}")

        self.server_sessions.clear()
        self._initialized = False
        print("All servers stopped.\n")

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        Collect all available tools from all connected MCP servers.

        Works in both Jupyter notebooks and regular Python.

        Returns:
            List of tool definitions from all servers
        """
        return _run_async(self._async_get_available_tools())

    async def _async_get_available_tools(self) -> List[Dict[str, Any]]:
        """Internal async implementation of get_available_tools"""
        all_tools = []
        self.tool_to_server_map.clear()

        print("Collecting available tools from servers...")

        for server_name, server_info in self.server_sessions.items():
            try:
                session = server_info["session"]

                # List tools from this server
                tools_response = await session.list_tools()

                # Add tools and map them to their server
                for tool in tools_response.tools:
                    all_tools.append(tool)
                    self.tool_to_server_map[tool.name] = server_name
                    print(f"  - {tool.name} ({server_name})")

            except Exception as e:
                print(f"  ✗ Error getting tools from {server_name}: {e}")

        self.available_tools = all_tools
        print(f"\nTotal tools available: {len(all_tools)}\n")
        return all_tools

    def convert_mcp_tools_to_openai_format(self) -> List[Dict[str, Any]]:
        """
        Convert MCP tool definitions to OpenAI function calling format.

        OpenAI expects tools in this format:
        {
            "type": "function",
            "function": {
                "name": "tool_name",
                "description": "What the tool does",
                "parameters": {
                    "type": "object",
                    "properties": {...},
                    "required": [...]
                }
            }
        }

        Returns:
            List of tools in OpenAI format
        """
        openai_tools = []

        for tool in self.available_tools:
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            }
            openai_tools.append(openai_tool)

        return openai_tools

    def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Execute a tool call on the appropriate MCP server.

        Works in both Jupyter notebooks and regular Python.

        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool

        Returns:
            Tool execution result as a string
        """
        return _run_async(self._async_call_mcp_tool(tool_name, arguments))

    async def _async_call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Internal async implementation of call_mcp_tool"""
        # Find which server has this tool
        server_name = self.tool_to_server_map.get(tool_name)

        if not server_name:
            available_tools = sorted(self.tool_to_server_map.keys())
            return _make_error_json(
                message=f"Tool {tool_name} not found",
                reason="The requested tool name is not registered with the active MCP servers.",
                hints=[
                    "Call get_available_tools to refresh the tool list.",
                    "Select one of the tool names provided in the available tools list."
                ],
                retryable=True,
                follow_up_tools=available_tools[:5],
                context={"available_tools": available_tools}
            )

        # Get the server session
        server_info = self.server_sessions.get(server_name)
        if not server_info:
            return _make_error_json(
                message=f"Server {server_name} not connected",
                reason="The orchestrator does not have an active session with the server that hosts this tool.",
                hints=[
                    "Call start_servers before invoking tools.",
                    "If servers were stopped, run stop_servers then start_servers to refresh connections."
                ],
                retryable=True,
                context={"server_name": server_name}
            )

        try:
            session = server_info["session"]

            # Call the tool
            result = await session.call_tool(tool_name, arguments)

            # Extract text content from result
            if result.content and len(result.content) > 0:
                return result.content[0].text
            else:
                return json.dumps({"result": "Tool executed successfully but returned no content"})

        except Exception as e:
            return _make_error_json(
                message=f"Error calling tool {tool_name}",
                reason=str(e),
                hints=[
                    "Validate the arguments against the tool schema.",
                    "If the issue persists, inspect server logs for stack traces."
                ],
                retryable=True,
                context={"tool_name": tool_name}
            )

    def query(self, prompt: str, api_key: str, max_iterations: int = 10) -> str:
        """
        Process a user query using OpenAI gpt-5-nano with function calling.

        Works in both Jupyter notebooks and regular Python.

        This implements a multi-turn conversation loop:
        1. Send user prompt + available tools to gpt-5-nano
        2. If gpt-5-nano wants to call tools, execute them on MCP servers
        3. Send tool results back to gpt-5-nano
        4. Repeat until gpt-5-nano gives a final answer

        Args:
            prompt: User's question or request
            api_key: OpenAI API key
            max_iterations: Maximum number of tool calling rounds (safety limit)

        Returns:
            Final text response from gpt-5-nano
        """
        return _run_async(self._async_query(prompt, api_key, max_iterations))

    async def _async_query(self, prompt: str, api_key: str, max_iterations: int = 10) -> str:
        """Internal async implementation of query"""
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)

        # Get tools in OpenAI format
        openai_tools = self.convert_mcp_tools_to_openai_format()

        # Initialize conversation with user prompt
        messages = [
            {
                "role": "system",
                "content": "You are a helpful IT support assistant. You have access to various tools to help answer questions about tickets, customers, billing, knowledge base articles, and assets. Use the tools to gather information needed to answer the user's questions accurately."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        # Multi-turn conversation loop
        for iteration in range(max_iterations):
            try:
                print(f"\n{'='*60}")
                print(f"Iteration {iteration + 1}")
                print(f"{'='*60}")

                # Call OpenAI API with tools
                response = client.chat.completions.create(
                    model="gpt-5-nano",
                    messages=messages,
                    tools=openai_tools,
                    tool_choice="auto"  # Let the model decide when to use tools
                )

                response_message = response.choices[0].message

                # Check if the model wants to call tools
                if response_message.tool_calls:
                    print(f"\n🔧 Model wants to call {len(response_message.tool_calls)} tool(s):")

                    # Add assistant's response to messages
                    messages.append(response_message)

                    # Execute each tool call
                    for tool_call in response_message.tool_calls:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)

                        print(f"  - Calling: {function_name}")
                        print(f"    Arguments: {json.dumps(function_args, indent=6)}")

                        # Execute the tool on the appropriate MCP server
                        tool_result = await self._async_call_mcp_tool(function_name, function_args)

                        print(f"    Result preview: {tool_result[:200]}...")

                        # Add tool result to messages
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": function_name,
                            "content": tool_result
                        })

                    # Continue loop to get next response
                    continue

                else:
                    # No more tool calls - this is the final answer
                    final_answer = response_message.content
                    print(f"\n✅ Final answer received")
                    return final_answer

            except Exception as e:
                error_msg = f"Error during query processing: {str(e)}"
                print(f"\n❌ {error_msg}")
                return f"I encountered an error: {error_msg}"

        # If we hit max iterations, return what we have
        return "I've reached the maximum number of tool calls. Please try rephrasing your question or breaking it into smaller parts."

    def interactive_mode(self, api_key: str):
        """
        Run an interactive chat session where users can ask questions.

        Works in both Jupyter notebooks and regular Python.

        Args:
            api_key: OpenAI API key
        """
        return _run_async(self._async_interactive_mode(api_key))

    async def _async_interactive_mode(self, api_key: str):
        """Internal async implementation of interactive_mode"""
        print("\n" + "="*60)
        print("MCP Orchestrator - Interactive Mode")
        print("="*60)
        print("\nType your questions below. Type 'exit' or 'quit' to stop.\n")

        while True:
            try:
                # Get user input
                user_input = input("\n🤔 You: ").strip()

                # Check for exit commands
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("\nGoodbye! 👋")
                    break

                # Skip empty input
                if not user_input:
                    continue

                # Process the query
                print("\n🤖 Assistant: ", end="", flush=True)
                response = await self._async_query(user_input, api_key)
                print(f"\n{response}\n")

            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")


def run_orchestrator_example():
    """
    Main function demonstrating orchestrator usage.
    Works in both Jupyter notebooks and regular Python.
    """
    # Create orchestrator instance
    orchestrator = MCPOrchestrator()

    try:
        # Start all MCP servers
        orchestrator.start_servers()

        # Get available tools
        orchestrator.get_available_tools()

        print("✅ All systems ready!\n")

        # Example: Test with a simple query (requires OpenAI API key)
        # Uncomment the following to test with OpenAI:
        """
        api_key = "your-openai-api-key-here"
        response = orchestrator.query(
            "What are the critical priority tickets currently open?",
            api_key
        )
        print(f"\nResponse: {response}\n")
        """

        # For now, just verify servers can start and stop
        print("Test complete - servers are running.")
        print("Stopping servers...")

        return orchestrator

    except KeyboardInterrupt:
        print("\n\nShutting down...")
        orchestrator.stop_servers()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        orchestrator.stop_servers()


if __name__ == "__main__":
    """
    Entry point for the MCP Orchestrator.

    Usage:
        python mcp_client.py

    This will:
    1. Start all 5 MCP servers (ticket, customer, billing, kb, asset)
    2. Connect to each server via stdio transport
    3. Collect all available tools
    4. Stop servers

    To use with OpenAI, uncomment the example code in run_orchestrator_example() and add your API key.
    """
    orchestrator = run_orchestrator_example()
    if orchestrator:
        orchestrator.stop_servers()
