"""
Interactive MCP Client with OpenAI Integration
Allows you to chat with gpt-5-nano using all MCP server tools
"""

import os
import sys
from mcp_client import MCPOrchestrator


def main():
    """Run interactive chat session"""
    print("\n" + "="*70)
    print("  MCP Orchestrator - Interactive IT Support Assistant")
    print("="*70)

    # Get OpenAI API key from environment or prompt
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("\n⚠️  No OPENAI_API_KEY found in environment.")
        api_key = input("Please enter your OpenAI API key: ").strip()

        if not api_key:
            print("❌ API key required. Exiting.")
            return

    # Create and initialize orchestrator
    orchestrator = MCPOrchestrator()

    try:
        # Start all MCP servers
        print("\n🚀 Initializing system...\n")
        orchestrator.start_servers()  # Not async - uses _run_async internally

        # Get available tools
        orchestrator.get_available_tools()  # Not async - uses _run_async internally

        # Run interactive mode
        orchestrator.interactive_mode(api_key)  # Not async - uses _run_async internally

    except KeyboardInterrupt:
        print("\n\nShutting down...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        orchestrator.stop_servers()  # Not async - uses _run_async internally


if __name__ == "__main__":
    """
    Interactive MCP client with OpenAI gpt-5-nano integration.

    Set your OpenAI API key:
        export OPENAI_API_KEY="sk-..."

    Or the script will prompt you for it.

    Example questions to try:
    - "What are all the critical priority tickets?"
    - "Show me customer CUST-001's information and SLA terms"
    - "What's the outstanding balance for TechCorp Industries?"
    - "Find KB articles about Windows BSOD issues"
    - "Check warranty status for asset AST-SRV-001"
    - "Show me all tickets for customer CUST-002 and their invoices"
    """
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
