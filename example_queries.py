"""
Example queries demonstrating MCP Orchestrator capabilities
Shows how to use the orchestrator for various IT support scenarios
"""

import asyncio
import os
from mcp_client import MCPOrchestrator


async def run_example_queries():
    """Run a series of example queries to demonstrate capabilities"""

    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Please set OPENAI_API_KEY environment variable")
        return

    # Initialize orchestrator
    orchestrator = MCPOrchestrator()

    try:
        # Start servers
        await orchestrator.start_servers()
        await orchestrator.get_available_tools()

        print("\n" + "="*70)
        print("  Running Example Queries")
        print("="*70)

        # Example 1: Ticket Analysis
        print("\n" + "-"*70)
        print("Example 1: Find Critical Tickets")
        print("-"*70)
        response = await orchestrator.query(
            "What are all the critical priority tickets? List them with their IDs, subjects, and status.",
            api_key
        )
        print(f"\n📋 Response:\n{response}")

        # Example 2: Customer Information
        print("\n" + "-"*70)
        print("Example 2: Customer SLA Information")
        print("-"*70)
        response = await orchestrator.query(
            "Tell me about customer CUST-001. What are their SLA terms and who are their contacts?",
            api_key
        )
        print(f"\n📋 Response:\n{response}")

        # Example 3: Billing Analysis
        print("\n" + "-"*70)
        print("Example 3: Outstanding Invoices")
        print("-"*70)
        response = await orchestrator.query(
            "Show me all overdue invoices and which customers have outstanding balances.",
            api_key
        )
        print(f"\n📋 Response:\n{response}")

        # Example 4: Knowledge Base Search
        print("\n" + "-"*70)
        print("Example 4: KB Article Search")
        print("-"*70)
        response = await orchestrator.query(
            "Find knowledge base articles about Windows BSOD issues. What are the recommended solutions?",
            api_key
        )
        print(f"\n📋 Response:\n{response}")

        # Example 5: Asset Management
        print("\n" + "-"*70)
        print("Example 5: Warranty Expiration Check")
        print("-"*70)
        response = await orchestrator.query(
            "Which assets have warranties expiring in the next 30 days or have already expired?",
            api_key
        )
        print(f"\n📋 Response:\n{response}")

        # Example 6: Cross-Server Query
        print("\n" + "-"*70)
        print("Example 6: Complete Customer Analysis")
        print("-"*70)
        response = await orchestrator.query(
            "For customer CUST-002 (DataFlow Solutions), show me their current tickets, outstanding invoices, and assets. Is there anything that needs immediate attention?",
            api_key
        )
        print(f"\n📋 Response:\n{response}")

        # Example 7: Troubleshooting Help
        print("\n" + "-"*70)
        print("Example 7: Find Similar Issues")
        print("-"*70)
        response = await orchestrator.query(
            "Find similar tickets to TKT-1001 and check if there's a knowledge base article that could help resolve it.",
            api_key
        )
        print(f"\n📋 Response:\n{response}")

        print("\n" + "="*70)
        print("  All examples completed!")
        print("="*70)

    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        await orchestrator.stop_servers()


if __name__ == "__main__":
    """
    Run example queries to demonstrate MCP Orchestrator capabilities.

    This script shows:
    - Single-server queries (tickets, customers, billing, KB, assets)
    - Multi-server queries (combining data from multiple sources)
    - Complex analysis requiring multiple tool calls

    Prerequisites:
        export OPENAI_API_KEY="sk-..."

    Run:
        python example_queries.py
    """
    asyncio.run(run_example_queries())
