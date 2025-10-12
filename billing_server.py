"""
Billing MCP Server
Provides tools for accessing billing and payment information
"""

import asyncio
import json
from datetime import datetime, timedelta
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


def make_error(message, *, reason=None, hints=None, retryable=False, follow_up_tools=None, **extra):
    """Standardised error payload for LLM-friendly responses."""
    payload = {"error": message}
    if reason:
        payload["reason"] = reason
    if hints:
        payload["suggested_actions"] = hints
    payload["retryable"] = retryable
    if follow_up_tools:
        payload["follow_up_tools"] = follow_up_tools
    for key, value in extra.items():
        if value is not None:
            payload[key] = value
    return payload


# Sample invoice data
INVOICES = [
    {
        "invoice_id": "INV-2025-001",
        "customer_id": "CUST-001",
        "ticket_id": "TKT-1001",
        "amount": 450.00,
        "currency": "USD",
        "status": "paid",
        "issue_date": "2025-09-15",
        "due_date": "2025-10-15",
        "paid_date": "2025-09-20",
        "description": "Premium support - Windows BSOD investigation and resolution",
        "line_items": [
            {"description": "Senior engineer hours (3h)", "amount": 450.00}
        ]
    },
    {
        "invoice_id": "INV-2025-002",
        "customer_id": "CUST-002",
        "ticket_id": "TKT-1002",
        "amount": 850.00,
        "currency": "USD",
        "status": "pending",
        "issue_date": "2025-10-01",
        "due_date": "2025-10-31",
        "paid_date": None,
        "description": "Critical incident - Linux server disk space emergency response",
        "line_items": [
            {"description": "Emergency response fee", "amount": 250.00},
            {"description": "Engineer hours (4h)", "amount": 600.00}
        ]
    },
    {
        "invoice_id": "INV-2025-003",
        "customer_id": "CUST-003",
        "ticket_id": "TKT-1003",
        "amount": 300.00,
        "currency": "USD",
        "status": "paid",
        "issue_date": "2025-09-28",
        "due_date": "2025-10-28",
        "paid_date": "2025-10-02",
        "description": "macOS kernel panic diagnosis and fix",
        "line_items": [
            {"description": "Standard support hours (2h)", "amount": 300.00}
        ]
    },
    {
        "invoice_id": "INV-2025-004",
        "customer_id": "CUST-001",
        "ticket_id": "TKT-1004",
        "amount": 600.00,
        "currency": "USD",
        "status": "pending",
        "issue_date": "2025-10-03",
        "due_date": "2025-11-02",
        "paid_date": None,
        "description": "Network performance troubleshooting - Windows Server",
        "line_items": [
            {"description": "Network analysis (4h)", "amount": 600.00}
        ]
    },
    {
        "invoice_id": "INV-2025-005",
        "customer_id": "CUST-004",
        "ticket_id": "TKT-1005",
        "amount": 200.00,
        "currency": "USD",
        "status": "paid",
        "issue_date": "2025-09-30",
        "due_date": "2025-10-30",
        "paid_date": "2025-10-01",
        "description": "Ubuntu repository configuration fix",
        "line_items": [
            {"description": "Standard support (1.5h)", "amount": 200.00}
        ]
    },
    {
        "invoice_id": "INV-2025-006",
        "customer_id": "CUST-005",
        "ticket_id": "TKT-1006",
        "amount": 500.00,
        "currency": "USD",
        "status": "pending",
        "issue_date": "2025-10-04",
        "due_date": "2025-11-03",
        "paid_date": None,
        "description": "Windows filesystem troubleshooting - ongoing",
        "line_items": [
            {"description": "Investigation and diagnostics (3h)", "amount": 500.00}
        ]
    },
    {
        "invoice_id": "INV-2025-007",
        "customer_id": "CUST-002",
        "ticket_id": "TKT-1007",
        "amount": 350.00,
        "currency": "USD",
        "status": "overdue",
        "issue_date": "2025-09-05",
        "due_date": "2025-10-05",
        "paid_date": None,
        "description": "SSH performance optimization - Debian server",
        "line_items": [
            {"description": "Performance tuning (2.5h)", "amount": 350.00}
        ]
    },
    {
        "invoice_id": "INV-2025-008",
        "customer_id": "CUST-006",
        "ticket_id": "TKT-1008",
        "amount": 150.00,
        "currency": "USD",
        "status": "pending",
        "issue_date": "2025-10-01",
        "due_date": "2025-10-31",
        "paid_date": None,
        "description": "macOS Time Machine backup troubleshooting",
        "line_items": [
            {"description": "Basic support (1h)", "amount": 150.00}
        ]
    },
    {
        "invoice_id": "INV-2025-009",
        "customer_id": "CUST-007",
        "ticket_id": "TKT-1009",
        "amount": 750.00,
        "currency": "USD",
        "status": "pending",
        "issue_date": "2025-10-02",
        "due_date": "2025-11-01",
        "paid_date": None,
        "description": "Critical BitLocker recovery - Windows 11",
        "line_items": [
            {"description": "Emergency support", "amount": 200.00},
            {"description": "Senior engineer (3.5h)", "amount": 550.00}
        ]
    },
    {
        "invoice_id": "INV-2025-010",
        "customer_id": "CUST-003",
        "ticket_id": "TKT-1010",
        "amount": 1500.00,
        "currency": "USD",
        "status": "pending",
        "issue_date": "2025-09-25",
        "due_date": "2025-10-25",
        "paid_date": None,
        "description": "CentOS migration planning and consultation",
        "line_items": [
            {"description": "Migration assessment", "amount": 500.00},
            {"description": "Planning consultation (6h)", "amount": 1000.00}
        ]
    },
    {
        "invoice_id": "INV-2025-011",
        "customer_id": "CUST-008",
        "ticket_id": "TKT-1011",
        "amount": 900.00,
        "currency": "USD",
        "status": "paid",
        "issue_date": "2025-09-29",
        "due_date": "2025-10-29",
        "paid_date": "2025-09-30",
        "description": "Active Directory replication fix - critical",
        "line_items": [
            {"description": "Emergency AD repair (5h)", "amount": 900.00}
        ]
    },
    {
        "invoice_id": "INV-2025-012",
        "customer_id": "CUST-004",
        "ticket_id": "TKT-1012",
        "amount": 400.00,
        "currency": "USD",
        "status": "pending",
        "issue_date": "2025-10-04",
        "due_date": "2025-11-03",
        "paid_date": None,
        "description": "Ubuntu high CPU investigation - ongoing",
        "line_items": [
            {"description": "System analysis (2.5h)", "amount": 400.00}
        ]
    },
    {
        "invoice_id": "INV-2024-088",
        "customer_id": "CUST-005",
        "ticket_id": None,
        "amount": 2500.00,
        "currency": "USD",
        "status": "paid",
        "issue_date": "2024-12-01",
        "due_date": "2024-12-31",
        "paid_date": "2024-12-15",
        "description": "Monthly premium support retainer - December 2024",
        "line_items": [
            {"description": "Premium support package", "amount": 2500.00}
        ]
    },
    {
        "invoice_id": "INV-2024-075",
        "customer_id": "CUST-002",
        "ticket_id": None,
        "amount": 1800.00,
        "currency": "USD",
        "status": "overdue",
        "issue_date": "2024-11-15",
        "due_date": "2024-12-15",
        "paid_date": None,
        "description": "Quarterly infrastructure review - Q4 2024",
        "line_items": [
            {"description": "Infrastructure audit", "amount": 1800.00}
        ]
    },
    {
        "invoice_id": "INV-2025-013",
        "customer_id": "CUST-006",
        "ticket_id": "TKT-1014",
        "amount": 275.00,
        "currency": "USD",
        "status": "pending",
        "issue_date": "2025-10-05",
        "due_date": "2025-11-04",
        "paid_date": None,
        "description": "Windows 11 taskbar troubleshooting",
        "line_items": [
            {"description": "Support hours (2h)", "amount": 275.00}
        ]
    }
]




# ============================================================================
# REGULAR PYTHON FUNCTIONS - Can be called directly without MCP
# ============================================================================

def get_invoice(invoice_id=None, customer_id=None):
    """Get invoice(s) by ID or customer ID. Can be called directly."""
    if invoice_id:
        invoice = next((inv for inv in INVOICES if inv["invoice_id"] == invoice_id), None)
        if not invoice:
            return make_error(
                f"Invoice {invoice_id} not found",
                reason="The provided invoice_id does not exist in the billing dataset.",
                hints=[
                    "Call calculate_outstanding_balance to review invoices by customer.",
                    "Use get_invoice with customer_id to browse available invoices."
                ],
                retryable=True,
                follow_up_tools=["calculate_outstanding_balance", "get_invoice"],
                invoice_id=invoice_id
            )
        result = invoice.copy()
        result["is_overdue"] = is_overdue(invoice)
        result["days_overdue"] = calculate_days_overdue(invoice)
        return result
    elif customer_id:
        customer_invoices = [inv for inv in INVOICES if inv["customer_id"] == customer_id]
        return {"customer_id": customer_id, "invoices": customer_invoices, "total_invoices": len(customer_invoices)}
    else:
        return make_error(
            "Missing invoice lookup criteria",
            reason="Neither invoice_id nor customer_id was supplied.",
            hints=[
                "Provide invoice_id to retrieve a single invoice.",
                "Provide customer_id to list all invoices for that customer."
            ],
            retryable=True,
            follow_up_tools=["get_invoice"],
            expected_arguments=["invoice_id", "customer_id"]
        )


def check_payment_status(invoice_id=None, customer_id=None):
    """Check payment status of invoice(s). Can be called directly."""
    if invoice_id:
        invoice = next((inv for inv in INVOICES if inv["invoice_id"] == invoice_id), None)
        if not invoice:
            return make_error(
                f"Invoice {invoice_id} not found",
                reason="Payment details require a valid invoice_id.",
                hints=[
                    "List invoices by passing customer_id to get_invoice.",
                    "Double-check the invoice_id spelling (e.g., INV-2025-001)."
                ],
                retryable=True,
                follow_up_tools=["get_invoice"],
                invoice_id=invoice_id
            )
        return {
            "invoice_id": invoice["invoice_id"], "customer_id": invoice["customer_id"],
            "payment_status": invoice["status"], "amount": invoice["amount"], "currency": invoice["currency"],
            "issue_date": invoice["issue_date"], "due_date": invoice["due_date"], "paid_date": invoice["paid_date"],
            "is_overdue": is_overdue(invoice), "days_overdue": calculate_days_overdue(invoice)
        }
    elif customer_id:
        customer_invoices = [inv for inv in INVOICES if inv["customer_id"] == customer_id]
        pending = [inv for inv in customer_invoices if inv["status"] == "pending"]
        overdue = [inv for inv in customer_invoices if inv["status"] == "overdue" or is_overdue(inv)]
        paid = [inv for inv in customer_invoices if inv["status"] == "paid"]
        return {
            "customer_id": customer_id,
            "summary": {"total_invoices": len(customer_invoices), "paid": len(paid), "pending": len(pending), "overdue": len(overdue)},
            "overdue_invoices": [{"invoice_id": inv["invoice_id"], "amount": inv["amount"], "due_date": inv["due_date"], "days_overdue": calculate_days_overdue(inv)} for inv in overdue]
        }
    else:
        return make_error(
            "Missing payment status lookup criteria",
            reason="No invoice_id or customer_id was provided to scope the request.",
            hints=[
                "Use invoice_id for a specific invoice payment status.",
                "Use customer_id to summarise billing status across invoices."
            ],
            retryable=True,
            follow_up_tools=["check_payment_status"],
            expected_arguments=["invoice_id", "customer_id"]
        )


def get_billing_history(customer_id, start_date=None, end_date=None):
    """Get billing history for a customer. Can be called directly."""
    customer_invoices = [inv for inv in INVOICES if inv["customer_id"] == customer_id]
    if start_date or end_date:
        filtered = []
        for inv in customer_invoices:
            inv_date = parse_date(inv["issue_date"])
            if not inv_date:
                continue
            if start_date and inv_date < parse_date(start_date):
                continue
            if end_date and inv_date > parse_date(end_date):
                continue
            filtered.append(inv)
        customer_invoices = filtered
    total_billed = sum(inv["amount"] for inv in customer_invoices)
    total_paid = sum(inv["amount"] for inv in customer_invoices if inv["status"] == "paid")
    total_pending = sum(inv["amount"] for inv in customer_invoices if inv["status"] in ["pending", "overdue"])
    return {
        "customer_id": customer_id, "start_date": start_date, "end_date": end_date,
        "invoices": customer_invoices,
        "summary": {"total_invoices": len(customer_invoices), "total_billed": total_billed, "total_paid": total_paid, "total_pending": total_pending, "currency": "USD"}
    }


def calculate_outstanding_balance(customer_id):
    """Calculate outstanding balance for a customer. Can be called directly."""
    customer_invoices = [inv for inv in INVOICES if inv["customer_id"] == customer_id]
    unpaid = [inv for inv in customer_invoices if inv["status"] != "paid"]
    overdue = [inv for inv in unpaid if is_overdue(inv)]
    outstanding_balance = sum(inv["amount"] for inv in unpaid)
    overdue_amount = sum(inv["amount"] for inv in overdue)
    return {
        "customer_id": customer_id, "outstanding_balance": outstanding_balance, "currency": "USD",
        "overdue_amount": overdue_amount, "number_of_unpaid_invoices": len(unpaid), "number_of_overdue_invoices": len(overdue),
        "unpaid_invoices": [{"invoice_id": inv["invoice_id"], "amount": inv["amount"], "status": inv["status"], "due_date": inv["due_date"], "is_overdue": is_overdue(inv), "days_overdue": calculate_days_overdue(inv)} for inv in unpaid]
    }


# ============================================================================
# MCP SERVER SETUP
# ============================================================================

# Initialize the MCP server
app = Server("billing-server")


# Helper functions
def parse_date(date_str):
    """Parse date string to datetime object"""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except (ValueError, TypeError):
        return None


def is_overdue(invoice):
    """Check if invoice is overdue"""
    if invoice["status"] == "paid":
        return False
    due_date = parse_date(invoice["due_date"])
    if due_date:
        return datetime.now() > due_date
    return False


def calculate_days_overdue(invoice):
    """Calculate how many days an invoice is overdue"""
    if invoice["status"] == "paid":
        return 0
    due_date = parse_date(invoice["due_date"])
    if due_date:
        delta = datetime.now() - due_date
        return max(0, delta.days)
    return 0


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available billing tools"""
    return [
        Tool(
            name="get_invoice",
            description="Retrieve invoice details by invoice ID or search by customer ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "invoice_id": {"type": "string", "description": "Unique invoice identifier"},
                    "customer_id": {"type": "string", "description": "Get all invoices for a customer"}
                }
            }
        ),
        Tool(
            name="check_payment_status",
            description="Check the payment status of an invoice or customer account",
            inputSchema={
                "type": "object",
                "properties": {
                    "invoice_id": {"type": "string", "description": "Invoice identifier"},
                    "customer_id": {"type": "string", "description": "Customer identifier"}
                }
            }
        ),
        Tool(
            name="get_billing_history",
            description="Retrieve billing history for a customer over a specified time period",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string", "description": "Unique customer identifier"},
                    "start_date": {"type": "string", "description": "Start date for history (YYYY-MM-DD)"},
                    "end_date": {"type": "string", "description": "End date for history (YYYY-MM-DD)"}
                },
                "required": ["customer_id"]
            }
        ),
        Tool(
            name="calculate_outstanding_balance",
            description="Calculate the total outstanding balance for a customer account",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string", "description": "Unique customer identifier"}
                },
                "required": ["customer_id"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls - delegates to regular Python functions"""
    if name == "get_invoice":
        result = get_invoice(**arguments)
    elif name == "check_payment_status":
        result = check_payment_status(**arguments)
    elif name == "get_billing_history":
        result = get_billing_history(**arguments)
    elif name == "calculate_outstanding_balance":
        result = calculate_outstanding_balance(arguments.get("customer_id"))
    else:
        raise ValueError(f"Unknown tool: {name}")
    return [TextContent(type="text", text=json.dumps(result, indent=2))]



async def main():
    """Run the billing server using stdio transport"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
