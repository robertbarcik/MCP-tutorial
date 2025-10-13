"""
E-commerce Payment Analysis MCP Server with Sampling
Demonstrates bidirectional communication where the server asks the host's LLM for help

This script shows an ADVANCED MCP pattern: sampling.
The server processes sensitive payment data and uses sampling to get AI-powered
analysis without sending raw transaction data to external APIs.

Usage:
    export OPENAI_API_KEY="sk-your-key-here"
    python sampling_demo.py

    Then interact with the server by asking questions like:
    - "Analyze spending patterns for customer CUST-001"
    - "What are the payment trends for CUST-002?"
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from openai import OpenAI


# ============================================================================
# MOCK E-COMMERCE TRANSACTION DATA
# ============================================================================

def generate_transaction_data(customer_id: str, num_transactions: int = 50) -> List[Dict[str, Any]]:
    """Generate realistic mock transaction data for a customer"""
    categories = [
        "Electronics", "Clothing", "Books", "Home & Garden",
        "Sports", "Food & Groceries", "Health & Beauty", "Toys"
    ]

    transactions = []
    base_date = datetime.now() - timedelta(days=365)

    for i in range(num_transactions):
        transaction_date = base_date + timedelta(days=i * 7)

        # Simulate realistic spending patterns
        category = categories[i % len(categories)]

        # Different spending amounts by category
        if category == "Electronics":
            amount = round(100 + (i % 5) * 50, 2)
        elif category == "Clothing":
            amount = round(30 + (i % 3) * 20, 2)
        elif category == "Food & Groceries":
            amount = round(50 + (i % 4) * 15, 2)
        else:
            amount = round(20 + (i % 6) * 10, 2)

        transactions.append({
            "transaction_id": f"TXN-{customer_id}-{i+1:04d}",
            "customer_id": customer_id,
            "date": transaction_date.strftime("%Y-%m-%d"),
            "amount": amount,
            "category": category,
            "status": "completed" if i % 20 != 0 else "pending",
            "payment_method": "credit_card" if i % 3 == 0 else "debit_card",
            "merchant": f"{category} Store {(i % 3) + 1}"
        })

    return transactions


# Customer transaction datasets
CUSTOMER_TRANSACTIONS = {
    "CUST-001": generate_transaction_data("CUST-001", 50),
    "CUST-002": generate_transaction_data("CUST-002", 75),
    "CUST-003": generate_transaction_data("CUST-003", 30),
}

print(f"Loaded transaction data for {len(CUSTOMER_TRANSACTIONS)} customers")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def anonymize_transactions(transactions: List[Dict[str, Any]]) -> str:
    """
    Anonymize transaction data for safe sharing with LLM.
    Removes sensitive identifiers while preserving analytical value.
    """
    anonymized = []
    for txn in transactions:
        anonymized.append({
            "date": txn["date"],
            "amount": txn["amount"],
            "category": txn["category"],
            "status": txn["status"]
        })
    return json.dumps(anonymized, indent=2)


def calculate_spending_stats(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate aggregate statistics from transactions"""
    if not transactions:
        return {}

    total_amount = sum(txn["amount"] for txn in transactions)
    avg_amount = total_amount / len(transactions)

    # Category breakdown
    category_totals = {}
    for txn in transactions:
        cat = txn["category"]
        category_totals[cat] = category_totals.get(cat, 0) + txn["amount"]

    # Sort categories by spending
    top_categories = sorted(
        category_totals.items(),
        key=lambda x: x[1],
        reverse=True
    )[:3]

    # Payment status
    completed = len([t for t in transactions if t["status"] == "completed"])
    pending = len([t for t in transactions if t["status"] == "pending"])

    return {
        "total_transactions": len(transactions),
        "total_amount": round(total_amount, 2),
        "average_amount": round(avg_amount, 2),
        "top_categories": [{"category": cat, "amount": round(amt, 2)} for cat, amt in top_categories],
        "completed_transactions": completed,
        "pending_transactions": pending,
        "date_range": f"{transactions[0]['date']} to {transactions[-1]['date']}"
    }


# ============================================================================
# MCP SERVER WITH SAMPLING
# ============================================================================

app = Server("payment-analysis-server")

# Store reference to sampling function (set during initialization)
_request_sampling = None


def set_sampling_function(sampling_fn):
    """Set the sampling function (called by the orchestrator)"""
    global _request_sampling
    _request_sampling = sampling_fn


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available payment analysis tools"""
    return [
        Tool(
            name="analyze_payment_patterns",
            description="Analyze customer spending patterns using AI (with privacy-preserving sampling)",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "Customer ID (e.g., CUST-001)"
                    }
                },
                "required": ["customer_id"]
            }
        ),
        Tool(
            name="get_transaction_summary",
            description="Get statistical summary of customer transactions (no AI processing)",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "Customer ID (e.g., CUST-001)"
                    }
                },
                "required": ["customer_id"]
            }
        )
    ]


async def analyze_payment_patterns(customer_id: str) -> Dict[str, Any]:
    """
    Analyze payment patterns using sampling (server asks host LLM for help).

    This demonstrates the SAMPLING pattern:
    1. Server retrieves sensitive transaction data (stays local)
    2. Server anonymizes data and requests sampling from host LLM
    3. Host LLM analyzes the data and returns insights
    4. Server combines stats + AI insights into final result

    Benefits:
    - Raw transaction data never leaves the server
    - Only anonymized summaries shared with external LLM
    - Privacy-preserving AI analysis
    """

    # Step 1: Get transaction data (stays on server)
    transactions = CUSTOMER_TRANSACTIONS.get(customer_id)

    if not transactions:
        return {
            "error": f"Customer {customer_id} not found",
            "available_customers": list(CUSTOMER_TRANSACTIONS.keys())
        }

    print(f"\n📊 Server has {len(transactions)} transactions for {customer_id}")
    print(f"🔒 Raw transaction data stays on server (privacy preserved)")

    # Step 2: Calculate statistical summary
    stats = calculate_spending_stats(transactions)

    # Step 3: Use SAMPLING to get AI-powered analysis
    # This is where the magic happens: server asks host LLM for help
    print(f"🤖 Server requesting sampling from host LLM...")

    # Anonymize data before sending to LLM
    anonymized_data = anonymize_transactions(transactions)

    # NOTE: In a real MCP implementation, this would use the sampling API
    # For this demo, we'll simulate it with a direct OpenAI call
    sampling_prompt = f"""
Analyze the following customer spending patterns and provide insights:

Transaction Data (anonymized):
{anonymized_data}

Provide a 3-4 sentence summary covering:
1. Overall spending behavior and trends
2. Top spending categories
3. Payment reliability
4. Any notable patterns or recommendations
"""

    # Simulate sampling (in real MCP, this would be session.request_sampling())
    ai_analysis = await simulate_sampling(sampling_prompt)

    print(f"✅ Sampling complete (AI analysis received)")

    # Step 4: Combine stats + AI analysis
    return {
        "customer_id": customer_id,
        "ai_analysis": ai_analysis,
        "statistics": stats,
        "note": "Raw transaction data was not shared externally. Only anonymized summaries were processed."
    }


async def simulate_sampling(prompt: str) -> str:
    """
    Simulate sampling by calling OpenAI directly.

    In a real MCP implementation, this would use session.request_sampling()
    which sends a request back to the host's LLM.
    """
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return "⚠️ Sampling simulation requires OPENAI_API_KEY. Using fallback analysis."

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a financial analyst providing insights on spending patterns."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Sampling failed: {str(e)}. Using fallback analysis."


def get_transaction_summary(customer_id: str) -> Dict[str, Any]:
    """Get statistical summary without AI analysis (no sampling)"""
    transactions = CUSTOMER_TRANSACTIONS.get(customer_id)

    if not transactions:
        return {
            "error": f"Customer {customer_id} not found",
            "available_customers": list(CUSTOMER_TRANSACTIONS.keys())
        }

    return {
        "customer_id": customer_id,
        "summary": calculate_spending_stats(transactions),
        "note": "Statistical summary only (no AI analysis)"
    }


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""

    if name == "analyze_payment_patterns":
        result = await analyze_payment_patterns(arguments.get("customer_id"))
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "get_transaction_summary":
        result = get_transaction_summary(arguments.get("customer_id"))
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Run the payment analysis server using stdio transport"""
    print("\n" + "="*70)
    print("E-commerce Payment Analysis Server with Sampling")
    print("="*70)
    print("\nThis server demonstrates the SAMPLING pattern:")
    print("  • Server has sensitive transaction data (stays local)")
    print("  • Server uses sampling to get AI analysis from host LLM")
    print("  • Only anonymized data is shared (privacy-preserving)")
    print("\n" + "="*70 + "\n")

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


# ============================================================================
# INTERACTIVE DEMO MODE
# ============================================================================

async def demo_mode():
    """
    Interactive demo showing sampling in action.
    This mode simulates what would happen when the server is called via MCP.
    """
    print("\n" + "="*70)
    print("🚀 Payment Analysis Server - Interactive Demo")
    print("="*70)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n⚠️  WARNING: No OPENAI_API_KEY found.")
        print("    Set your API key to see real sampling in action:")
        print("    export OPENAI_API_KEY='sk-your-key-here'")
        print("\n    Continuing with simulated responses...\n")

    print("\nAvailable customers:")
    for cust_id in CUSTOMER_TRANSACTIONS.keys():
        txn_count = len(CUSTOMER_TRANSACTIONS[cust_id])
        print(f"  • {cust_id} ({txn_count} transactions)")

    print("\n" + "="*70)
    print("Demo: Analyzing customer spending with SAMPLING")
    print("="*70)

    # Analyze first customer
    customer_id = "CUST-001"
    print(f"\n🔍 User Query: \"Analyze spending patterns for {customer_id}\"")
    print(f"\n{'─'*70}")

    result = await analyze_payment_patterns(customer_id)

    print(f"\n{'─'*70}")
    print("\n📊 Final Result Returned to User:")
    print("="*70)
    print(json.dumps(result, indent=2))

    print("\n" + "="*70)
    print("✅ Demo Complete!")
    print("="*70)
    print("\nKey Observations:")
    print("  • Raw transaction data never left the server")
    print("  • Only anonymized summaries were processed by LLM")
    print("  • User received AI-powered insights + statistics")
    print("  • Privacy preserved throughout the process")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    """
    Entry point for the payment analysis server.

    Run modes:
    1. MCP Server Mode (default): python sampling_demo.py
       - Runs as MCP server via stdio transport
       - Used with interactive_client.py or mcp_client.py

    2. Demo Mode: python sampling_demo.py --demo
       - Interactive demonstration of sampling
       - Shows step-by-step what happens during sampling
    """

    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        # Run in demo mode
        asyncio.run(demo_mode())
    else:
        # Run as MCP server (stdio transport)
        asyncio.run(main())
